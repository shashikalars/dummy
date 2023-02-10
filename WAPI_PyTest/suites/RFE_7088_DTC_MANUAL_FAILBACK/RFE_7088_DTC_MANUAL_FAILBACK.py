import re
import sys
import config
import pytest
import unittest
import logging
import ast
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

Server1=config.Server1
global Server1
Server2=config.Server2
global Server2
Server3=config.Server3
global Server3
Server4=config.Server4
global Server4
global failback_output
global reference
global Server_data
global Pool_data
global Lbdn_data
global enable_output
global state_output

def print_and_log(arg=""):
        print(arg)
        logging.info(arg)

def Getting_DTC_Object_Reference(object_type,object_name):
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:"+object_type+"?name="+object_name, grid_vip=config.grid_vip)
        res = json.loads(ref)
        reference = json.loads(ref)[0]['_ref']
        print_and_log(reference)
        global reference

def DTC_Object_Fail_back_Manual_Disable(data):
	response = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data),params="?_function=dtc_object_disable")
        failback_output = str(response)
        failback_output=failback_output.replace('\n','').replace('{','').replace('}','').replace(']','').replace('[','').replace('\\','').replace("'",'')
        global failback_output
        print_and_log("Object Failback completed")

def DTC_Object_Fail_back_Manual_Enable(data):
        response = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data),params="?_function=dtc_object_enable")
        enable_output = str(response)
        global enable_output
        print_and_log("Object Enable completed")

def DTC_Object_Fail_back_GET_State(object_type,object_name):
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:"+object_type+"?name="+object_name, grid_vip=config.grid_vip)
        res = json.loads(ref)
        reference = json.loads(ref)[0]['_ref']
        print_and_log(reference)
        data={"dtc_object":str(reference)}
        response = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data),params="?_function=dtc_get_object_grid_state")
        state_output=json.loads(response)
        state_output=eval(json.dumps(state_output))
        global state_output
        print_and_log("Object Enable completed")


def Validate_Server_Fail_back_Status(object_name):
        print_and_log("Validate Server Fail Back Status")
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name="+object_name+"&_return_fields%2B=health", grid_vip=config.grid_vip)
        Server_data = ref
        global Server_data

def Validate_Pool_Fail_back_Status(object_name):
        print_and_log("Validate Pool Fail Back Status")
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?name="+object_name+"&_return_fields%2B=health,servers", grid_vip=config.grid_vip)
        Pool_data = ref
        global Pool_data

def Validate_Lbdn_Fail_back_Status(object_name):
        print_and_log("Validate Lbdn Fail Back Status")
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?name="+object_name+"&_return_fields%2B=health,pools", grid_vip=config.grid_vip)
        Lbdn_data = ref
        global Lbdn_data

def Getting_DTC_Object_Reference_GMC(object_type,object_name):
        print_and_log("Server Fail Back started")
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:"+object_type+"?name="+object_name, grid_vip=config.grid_member2_vip)
        res = json.loads(ref)
        reference = json.loads(ref)[0]['_ref']
        print_and_log(reference)
        global reference

def DTC_Object_Fail_back_Manual_Disable_GMC(data):
        response = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data),params="?_function=dtc_object_disable",grid_vip=config.grid_member2_vip)
        failback_output = str(response)
        failback_output=failback_output.replace('\n','').replace('{','').replace('}','').replace(']','').replace('[','').replace('\\','').replace("'",'')
        global failback_output
        print_and_log("Object Failback completed")

def DTC_Object_Fail_back_Manual_Enable_GMC(data):
        response = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data),params="?_function=dtc_object_enable",grid_vip=config.grid_member2_vip)
        enable_output = str(response)
        global enable_output
        print_and_log("Object Enable completed")

def DTC_Object_Fail_back_GET_State_GMC(object_type,object_name):
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:"+object_type+"?name="+object_name, grid_vip=config.grid_member2_vip)
        res = json.loads(ref)
        reference = json.loads(ref)[0]['_ref']
        print_and_log(reference)
        data={"dtc_object":str(reference)}
        response = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data),params="?_function=dtc_get_object_grid_state",grid_vip=config.grid_member2_vip)
        state_output=json.loads(response)
        state_output=eval(json.dumps(state_output))
        global state_output
        print_and_log("Object Enable completed")

def Validate_Server_Fail_back_Status_GMC(object_name):
        print_and_log("Validate Server Fail Back Status")
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name="+object_name+"&_return_fields%2B=health", grid_vip=config.grid_member2_vip)
        Server_data = ref
        global Server_data

def Validate_Pool_Fail_back_Status_GMC(object_name):
        print_and_log("Validate Pool Fail Back Status")
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?name="+object_name+"&_return_fields%2B=health,servers", grid_vip=config.grid_member2_vip)
        Pool_data = ref
        global Pool_data

def Validate_Lbdn_Fail_back_Status_GMC(object_name):
        print_and_log("Validate Lbdn Fail Back Status")
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?name="+object_name+"&_return_fields%2B=health,pools", grid_vip=config.grid_member2_vip)
        Lbdn_data = ref
        global Lbdn_data
def restart_services():
        print_and_log("Service restart start")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)
        print_and_log("Service restart Done")

def restart_services_IF_NEEDED():
        print_and_log("Service restart start")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"RESTART_IF_NEEDED","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(40)
        print_and_log("Service restart Done")

def validate_sigsegv_sigquit_and_sigabrt_core_files(grid_vip):
        print("************ Validate Sigsegv Sigquit and Sigabrt Core files ************")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(grid_vip, username='root', pkey = mykey)
        stdin, stdout, stderr = client.exec_command('ls -lrt /storage/cores')
        count_sigsegv=0
        count_sigabrt=0
        count_sigquit=0
        for i in stdout.readlines():
            print(i)
            if re.search(r'core.isc-worker0000.SIGSEGV', i):
                count_sigsegv=count_sigsegv+1
            elif re.search(r'core.idns_healthd.SIGABRT', i):
                count_sigabrt=count_sigabrt+1
            elif re.search(r'core.named.SIGQUIT', i):
                count_sigquit=count_sigquit+1
        print(str(count_sigsegv)+" core.isc-worker0000.SIGSEGV files are seen")
        print(str(count_sigabrt)+" core.idns_healthd.SIGABRT files are seen")
        print(str(count_sigquit)+" core.named.SIGQUIT files are seen")
        if count_sigsegv == 0 and count_sigabrt == 0 and count_sigquit == 0:
            print("No core files are seen")
            assert True
        else:
            print("Core files are seen")
            assert False

class RFE_7088_DTC_MANUAL_FAILBACK(unittest.TestCase):
        
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
        def test_003_create_New_AuthZone(self):
                logging.info("Create A new Zone")
                data = {"fqdn": "dtc.com","grid_primary": [{"name": config.grid_member_fqdn,"stealth":False}, {"name": config.grid_member1_fqdn,"stealth":False},{"name": config.grid_member2_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Restart DNS Services") 
                restart_services()
                sleep(20)
                logging.info("Test Case 3 Execution Completed")

        @pytest.mark.run(order=4)
        def test_004_Validate_Created_Zone(self):
                logging.info("Validate Created Zone")
                response =  ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=dtc.com", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                assert re.search(r'"dtc.com"',response)
                sleep(5)
                print("Test Case 4 Execution Completed")

        @pytest.mark.run(order=5)
        def test_005_add_a_DTC_Server1(self):
                logging.info("Create A DTC first Server")
                data = {"name":"Server1","host":config.Server1}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 5 Execution Completed")

        @pytest.mark.run(order=6)
        def test_006_Validate_Created_Server1(self):
                logging.info("Validate Created Server1")
                Getting_DTC_Object_Reference("server","Server1")
                assert re.search(r'Server1',reference)
                sleep(5)
                print("Test Case 6 Execution Completed")
        
	@pytest.mark.run(order=7)
        def test_007_Disable_server1_with_None_state_to_validate_Internal_Error_NIOS_84909(self):
		logging.info("Disable_server1_with_None_state_to_validate Internal_Error")
                Getting_DTC_Object_Reference("server","Server1")
		data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}	              #print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                print(failback_output)
                failback_output1=failback_output.replace(",","")
                assert re.search(r'"text": "The DTC object Server1 cannot be enabled/disabled since there are no associated enabled LBDNs"',failback_output1)
 
        @pytest.mark.run(order=8)
        def test_008_add_a_DTC_pool(self):
                logging.info("Create A DTC Pool")
                data= {"name": "Pool1","lb_preferred_method": "ROUND_ROBIN","servers": [{"ratio": 1,"server": "dtc:server/ZG5zLmlkbnNfc2VydmVyJFNlcnZlcjE:Server1"}],"monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:pool", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 9 Execution Completed")

        
        @pytest.mark.run(order=9)
        def test_009_Validate_Created_Pool(self):
                logging.info("Validate Created Pool")
                Getting_DTC_Object_Reference("pool","Pool1")
                assert re.search(r'Pool1',reference)
                sleep(5)
                print("Test Case 09 Execution Completed")

        @pytest.mark.run(order=10)
        def test_010_add_a_DTC_lbdn(self):
                logging.info("Create A DTC LBDN")
                data = {"name":"Lbdn","lb_method":"ROUND_ROBIN","patterns": ["a1.dtc.com"], "pools": [{"pool":"dtc:pool/ZG5zLmlkbnNfcG9vbCRQb29sMQ:Pool1","ratio": 1}], "auth_zones":["zone_auth/ZG5zLnpvbmUkLl9kZWZhdWx0LmNvbS5kdGM:dtc.com/default"],"types":["A","AAAA","CNAME","NAPTR","SRV"]}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:lbdn", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Restart DNS Services")
                restart_services()
                sleep(30)
                logging.info("Test Case 10 Execution Completed")

        @pytest.mark.run(order=11)
        def test_011_Validate_Created_LBDN(self):
                logging.info("Validate Created LBDN")
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                assert re.search(r'Lbdn',reference)
                sleep(5)
                print("Test Case 11 Execution Completed")

        @pytest.mark.run(order=12)
        def test_012_Validate_Single_server_Failback_Limitation(self):
                logging.info("Validate_Single_server_Failback_Limitation")
                Getting_DTC_Object_Reference("server","Server1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                print(failback_output)
                assert re.search(r'"text": "Cannot disable all the servers in a pool. At least one server must be enabled."',failback_output)
                print("Test Case 12 Execution Completed")

        @pytest.mark.run(order=13)
        def test_013_Validate_Single_pool_Failback_Limitation(self):
                logging.info("Validate_Single_pool_Failback_Limitation")
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                print(failback_output)
                assert re.search(r'"text": "Cannot disable all the pools in an LBDN. At least one pool must be enabled."',failback_output)
                print("Test Case 13 Execution Completed")

        @pytest.mark.run(order=14)
        def test_014_add_a_DTC_Server2(self):
                logging.info("Create A DTC Second Server")
                data = {"name":"Server2","host":config.Server2}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 14 Execution Completed")

        @pytest.mark.run(order=15)
        def test_015_Validate_Created_Server2(self):
                logging.info("Validate Created Server2")
                Getting_DTC_Object_Reference("server","Server2")
                assert re.search(r'Server2',reference)
                sleep(5)
                print("Test Case 15 Execution Completed")

        @pytest.mark.run(order=16)
        def test_016_Update_DTC_pool_with_Server2(self):
                logging.info("Update DTC_pool with Server2")
                data= {"servers": [{"ratio": 1,"server": "dtc:server/ZG5zLmlkbnNfc2VydmVyJFNlcnZlcjE:Server1"},{"ratio": 1,"server": "dtc:server/ZG5zLmlkbnNfc2VydmVyJFNlcnZlcjI:Server2"}]}
                Getting_DTC_Object_Reference("pool","Pool1")
                response = ib_NIOS.wapi_request('PUT', object_type=reference, fields=json.dumps(data))
                print response
                restart_services()
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                sleep(20)
                logging.info("Test Case 16 Execution Completed")

        @pytest.mark.run(order=17)
        def test_017_Validate_updated_Pool(self):
                logging.info("Validate updated Pool")
                Validate_Pool_Fail_back_Status("Pool1")
                assert re.search(r'Server2',Pool_data)
                sleep(5)
                print("Test Case 17 Execution Completed")
        
        @pytest.mark.run(order=18)
        def test_018_Validate_Default_Status_Of_DTC_Objects_Before_Disable(self):
                logging.info("Validate_Default_Status_Of_DTC_Objects_Before_Disable")
                Validate_Server_Fail_back_Status("Server1")
                print(Server_data)
                server1=Server_data
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                server2=Server_data
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "GREEN"' in server1) and ('"availability": "GREEN"' in server2) and ('"availability": "GREEN"' in Pool_data) and ('"availability": "GREEN"' in Lbdn_data)):
                    assert True
                else:
                    assert False
                print("Test Case 18 Execution Completed")
	
        @pytest.mark.run(order=19)
        def test_019_Perform_server1_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_server1_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 19 Execution Completed")

        @pytest.mark.run(order=20)
        def test_020_Validate_Server1_Failback_Status_of_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Server1_Failback_Status of UNTIL_MANUAL_ENABLING")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server1 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server1 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server1")
                print(Server_data)
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Master=child.before
                child.close()
                sleep(2)
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member1=child.before
                sleep(2)
                child.close()
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member2=child.before
                child.close()
                sleep(2)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and ("'health' : 'WHITE'" in Health_Master) and ("'health' : 'WHITE'" in Health_Member1) and ("'health' : 'WHITE'" not in Health_Member2) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 20 Execution Completed")

        @pytest.mark.run(order=21)
        def test_021_Validate_Server1_Failback_Status_On_Each_node(self):
                logging.info("Validate_Server1_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("server","Server1") 
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in disabled) and (config.grid_member1_fqdn in disabled) and (config.grid_member2_fqdn in enabled)):
                    assert True
                else:
                    assert False
                print("Test Case 21 Execution Completed")

        @pytest.mark.run(order=22)
        def test_022_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
                if ((Server2 in dig_result_1) and (Server1 not in dig_result_2) and (Server2 in dig_result_3) and (Server1 not in dig_result_4) and (Server1 in dig_result_5) and (Server2 in dig_result_6) ):
                    assert True
                else:
                    assert False
                print("Test Case 22 Execution Completed")

        @pytest.mark.run(order=23)
        def test_023_Perform_server1_Failback_with_UNTIL_MANUAL_ENABLING_Negative(self):
                logging.info("Perform_server1_Failback_with_UNTIL_MANUAL_ENABLING_Negative")
                Getting_DTC_Object_Reference("server","Server1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                print(failback_output)
                assert re.search(r'"text": "The DTC object Server1 is already disabled"',failback_output)
                sleep(5)
                print("Test Case 23 Execution Completed")
       
        @pytest.mark.run(order=24)
        def test_024_Perform_server1_Failback_Enable_On_Master(self):
                logging.info("Perform_server1_Failback_Enable On_Master")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server1")
                data={"enable_on":[config.grid_member_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                print(enable_output)
                assert re.search(r'"failback_status": "SUCCESS"',enable_output)
                sleep(10)
                print("Test Case 24 Execution Completed")

        @pytest.mark.run(order=25)
        def test_025_Validate_Server1_Failback_Status_On_Master(self):
                logging.info("Validate_Server1_Failback_Status On_Master")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server1")
                print(Server_data)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 25 Execution Completed")

        @pytest.mark.run(order=26)
        def test_026_Validate_Server1_Failback_Status_On_Each_node(self):
                logging.info("Validate_Server1_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("server","Server1")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in enabled) and (config.grid_member1_fqdn in disabled) and (config.grid_member2_fqdn in enabled)):
                    assert True
                else:
                    assert False
                print("Test Case 26 Execution Completed")

        @pytest.mark.run(order=27)
        def test_027_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
                if ((Server1 in dig_result_1) and (Server2 in dig_result_2) and (Server2 in dig_result_3) and (Server1 not in dig_result_4) and (Server1 in dig_result_5) and (Server2 in dig_result_6) ):
                    assert True
                else:
                    assert False
                print("Test Case 27 Execution Completed")

        @pytest.mark.run(order=28)
        def test_028_Perform_server1_Failback_Enable_On_Member1(self):
                logging.info("Perform_server1_Failback_Enable on Member1")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server1")
                data={"enable_on":[config.grid_member1_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                print(enable_output)
                assert re.search(r'"failback_status": "SUCCESS"',enable_output)
                sleep(25)
                print("Test Case 28 Execution Completed")

        @pytest.mark.run(order=29)
        def test_029_Validate_Server1_Failback_Status_On_Member1(self):
                logging.info("Validate_Server1_Failback_Status On_Member1")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))

                Validate_Server_Fail_back_Status("Server1")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and (int(check_master)==0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 29 Execution Completed") 

        @pytest.mark.run(order=30)
        def test_030_Validate_Server1_Failback_Status_On_Each_node(self):
                logging.info("Validate_Server1_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("server","Server1")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in enabled) and (config.grid_member1_fqdn in enabled) and (config.grid_member2_fqdn in enabled)):
                    assert True
                else:
                    assert False
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_member1_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.active_ip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.passive_ip)
                print("Test Case 30 Execution Completed")

        @pytest.mark.run(order=31)
        def test_031_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
                if ((Server1 in dig_result_1) and (Server2 in dig_result_2) and (Server1 in dig_result_3) and (Server2 in dig_result_4) and (Server1 in dig_result_5) and (Server2 in dig_result_6) ):
                    assert True
                else:
                    assert False
                print("Test Case 31 Execution Completed")

        @pytest.mark.run(order=32)
        def test_032_Perform_server1_Failback_with_UNTIL_DNS_RESTART(self):
                logging.info("Perform_server1_Failback_with_UNTIL_DNS_RESTART")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_DNS_RESTART","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(30)
                print("Test Case 32 Execution Completed")

        @pytest.mark.run(order=33)
        def test_033_Validate_Server1_Failback_Status_for_UNTIL_DNS_RESTART(self):
                logging.info("Validate_Server1_Failback_Status for UNTIL_DNS_RESTART")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server1 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server1 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server1")
                print(Server_data)
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Master=child.before
                sleep(2)
                child.close()
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member1=child.before
                sleep(2)
                child.close()
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member2=child.before
                sleep(2)
                child.close()
                if (('"availability": "DARKGRAY"' in Server_data) and ('"description": "Temporarily Disabled"' in Server_data) and ("'health' : 'DARKGRAY'" in Health_Master) and ("'health' : 'DARKGRAY'" not in Health_Member1) and ("'health' : 'DARKGRAY'" in Health_Member2) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 33 Execution Completed")

        @pytest.mark.run(order=34)
        def test_034_Validate_Server1_Failback_Status_On_Each_node(self):
                logging.info("Validate_Server1_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("server","Server1")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in disabled) and (config.grid_member1_fqdn in enabled) and (config.grid_member2_fqdn in disabled)):
                    assert True
                else:
                    assert False
                print("Test Case 34 Execution Completed")

        @pytest.mark.run(order=35)
        def test_035_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
                if ((Server2 in dig_result_1) and (Server1 not in dig_result_2) and (Server1 in dig_result_3) and (Server2 in dig_result_4) and (Server2 in dig_result_5) and (Server1 not in dig_result_6) ):
                    assert True
                else:
                    assert False
                print("Test Case 35 Execution Completed")


        @pytest.mark.run(order=36)
        def test_036_Perform_server1_Failback_Enable_with_IFNEEDED_Restart(self):        
                logging.info("Perform_server1_Failback_Enable_with_IFNEEDED_Restart")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                restart_services_IF_NEEDED()
                sleep(15)
                print("Test Case 36 Execution Completed")

        @pytest.mark.run(order=37)
        def test_037_Validate_Server1_Failback_Status_For_IFNEEDED_Restart(self):
                logging.info("Validate_Server1_Failback_Status for IFNEEDED_Restart")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))

                Validate_Server_Fail_back_Status("Server1")
                print(Server_data)
                if (('"availability": "DARKGRAY"' in Server_data) and ('"description": "Temporarily Disabled"' in Server_data) and (int(check_master)==0) and (int(check_member_1)==0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 37 Execution Completed")

        @pytest.mark.run(order=38)
        def test_038_Perform_server1_Failback_Enable_with_FORCE_Restart(self):
                logging.info("Perform_server1_Failback_Enable_with_FORCE_Restart")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                restart_services()
                sleep(25)
                print("Test Case 38 Execution Completed")

        @pytest.mark.run(order=39)
        def test_039_Validate_Server1_Failback_Status_For_FORCE_Restart(self):
                logging.info("Validate_Server1_Failback_Status for FORCE_Restart")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))

                Validate_Server_Fail_back_Status("Server1")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 39 Execution Completed")

        @pytest.mark.run(order=40)
        def test_040_Validate_Server1_Failback_Status_On_Each_node(self):
                logging.info("Validate_Server1_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("server","Server1")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in enabled) and (config.grid_member1_fqdn in enabled) and (config.grid_member2_fqdn in enabled)):
                    assert True
                else:
                    assert False
                print("Test Case 40 Execution Completed")

        @pytest.mark.run(order=41)
        def test_041_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
                if ((Server1 in dig_result_1) and (Server2 in dig_result_2) and (Server1 in dig_result_3) and (Server2 in dig_result_4) and (Server1 in dig_result_5) and (Server2 in dig_result_6) ):
                    assert True
                else:
                    assert False
                print("Test Case 41 Execution Completed")

        @pytest.mark.run(order=42)
        def test_042_Perform_server1_Failback_with_UNTIL_DNS_RESTART_For_Manual_Enable(self):
                logging.info("Perform_server1_Failback_with_UNTIL_DNS_RESTART For_Manual_Enable")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_DNS_RESTART","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(30)
                print("Test Case 42 Execution Completed")

        @pytest.mark.run(order=43)
        def test_043_Validate_Server1_Failback_Status_with_UNTIL_DNS_RESTART_For_Manual_Enable(self):
                logging.info("Validate_Server1_Failback_Status with_UNTIL_DNS_RESTART For_Manual_Enable")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server1 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server1 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))

                Validate_Server_Fail_back_Status("Server1")
                print(Server_data)
                if (('"availability": "DARKGRAY"' in Server_data) and ('"description": "Temporarily Disabled"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 43 Execution Completed")

        @pytest.mark.run(order=44)
        def test_044_Validate_Server1_Failback_Status_On_Each_node(self):
                logging.info("Validate_Server1_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("server","Server1")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in disabled) and (config.grid_member1_fqdn in disabled) and (config.grid_member2_fqdn in disabled)):
                    assert True
                else:
                    assert False
                print("Test Case 44 Execution Completed")

        @pytest.mark.run(order=45)
        def test_045_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
                if ((Server2 in dig_result_1) and (Server1 not in dig_result_2) and (Server2 in dig_result_3) and (Server1 not in dig_result_4) and (Server2 in dig_result_5) and (Server1 not in dig_result_6) ):
                    assert True
                else:
                    assert False
                print("Test Case 45 Execution Completed")

        @pytest.mark.run(order=46)
        def test_046_Perform_server1_Failback_with_UNTIL_DNS_RESTART_Negative(self):
                logging.info("Perform_server1_Failback_with_UNTIL_DNS_RESTART_Negative")
                Getting_DTC_Object_Reference("server","Server1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member1_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                print(failback_output)
                assert re.search(r'"text": "The DTC object Server1 is already disabled"',failback_output)
                sleep(5)
                print("Test Case 46 Execution Completed")
        
        @pytest.mark.run(order=47)
        def test_047_Perform_server1_Failback_Enable_On_master(self):
                logging.info("Perform_server1_Failback_Enable on master")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server1")
                data={"enable_on":[config.grid_member_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                print(enable_output)
                assert re.search(r'"failback_status": "SUCCESS"',enable_output)
                sleep(30)
                print("Test Case 47 Execution Completed") 

        @pytest.mark.run(order=48)
        def test_048_Validate_Server1_Failback_Status(self):
                logging.info("Validate_Server1_Failback_Status")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))

                Validate_Server_Fail_back_Status("Server1")
                print(Server_data)
                if (('"availability": "DARKGRAY"' in Server_data) and ('"description": "Temporarily Disabled"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 48 Execution Completed")

        @pytest.mark.run(order=49)
        def test_049_Validate_Server1_Failback_Status_On_Each_node(self):
                logging.info("Validate_Server1_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("server","Server1")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in enabled) and (config.grid_member1_fqdn in disabled) and (config.grid_member2_fqdn in disabled)):
                    assert True
                else:
                    assert False
                print("Test Case 49 Execution Completed")

        @pytest.mark.run(order=50)
        def test_050_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
                if ((Server1 in dig_result_1) and (Server2 in dig_result_2) and (Server2 in dig_result_3) and (Server1 not in dig_result_4) and (Server2 in dig_result_5) and (Server1 not in dig_result_6) ):
                    assert True
                else:
                    assert False
                print("Test Case 50 Execution Completed")

        @pytest.mark.run(order=51)
        def test_051_Perform_server1_Failback_Enable_On_Members(self):
                logging.info("Perform_server1_Failback_Enable on members")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server1")
                data={"enable_on":[config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                print(enable_output)
                assert re.search(r'"failback_status": "SUCCESS"',enable_output)
                sleep(30)
                print("Test Case 51 Execution Completed")

        @pytest.mark.run(order=52)
        def test_052_Validate_Server1_Failback_Status(self):
                logging.info("Validate_Server1_Failback_Status")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))

                Validate_Server_Fail_back_Status("Server1")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and (int(check_master)==0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 52 Execution Completed")

        @pytest.mark.run(order=53)
        def test_053_Validate_Server1_Failback_Status_On_Each_node(self):
                logging.info("Validate_Server1_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("server","Server1")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in enabled) and (config.grid_member1_fqdn in enabled) and (config.grid_member2_fqdn in enabled)):
                    assert True
                else:
                    assert False
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_member1_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.active_ip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.passive_ip)
                print("Test Case 53 Execution Completed")

        @pytest.mark.run(order=54)
        def test_054_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
                if ((Server1 in dig_result_1) and (Server2 in dig_result_2) and (Server1 in dig_result_3) and (Server2 in dig_result_4) and (Server1 in dig_result_5) and (Server2 in dig_result_6) ):
                    assert True
                else:
                    assert False
                print("Test Case 54 Execution Completed")
        
        @pytest.mark.run(order=55)
        def test_055_Perform_server1_Failback_with_SPECIFIED_TIME(self):
                logging.info("Perform_server1_Failback_with_SPECIFIED_TIME")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object":str(reference),"specific_time_disable":140}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(30)
                print("Test Case 55 Execution Completed")

        @pytest.mark.run(order=56)
        def test_056_Validate_Server1_Failback_Status_for_SPECIFIED_TIME(self):
                logging.info("Validate_Server1_Failback_Status for SPECIFIED_TIME")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server1 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server1 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server1")
                print(Server_data)
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Master=child.before
                sleep(2)
                child.close()
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member1=child.before
                sleep(2)
                child.close()
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member2=child.before
                sleep(2)
                child.close()
                if (('"availability": "DARKGRAY"' in Server_data) and ('"description": "Temporarily Disabled"' in Server_data) and ("'health' : 'DARKGRAY'" in Health_Master) and ("'health' : 'DARKGRAY'" in Health_Member1) and ("'health' : 'DARKGRAY'" in Health_Member2) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 56 Execution Completed")

        @pytest.mark.run(order=57)
        def test_057_Validate_Server1_Failback_Status_On_Each_node(self):
                logging.info("Validate_Server1_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("server","Server1")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in disabled) and (config.grid_member1_fqdn in disabled) and (config.grid_member2_fqdn in disabled)):
                    assert True
                else:
                    assert False
                print("Test Case 57 Execution Completed")

        @pytest.mark.run(order=58)
        def test_058_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
                if ((Server2 in dig_result_1) and (Server1 not in dig_result_2) and (Server2 in dig_result_3) and (Server1 not in dig_result_4) and (Server2 in dig_result_5) and (Server1 not in dig_result_6)):
                    assert True
                else:
                    assert False
                print("Test Case 58 Execution Completed")

        @pytest.mark.run(order=59)
        def test_059_Perform_server1_Failback_Enable_with_FORCE_Restart_Negative(self):
                logging.info("Perform_server1_Failback_Enable_with_FORCE_Restart Negative")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                restart_services()
                sleep(2)
                print("Test Case 59 Execution Completed")

        @pytest.mark.run(order=60)
        def test_060_Validate_Server1_Failback_Status_After_FORCE_Restart(self):
                logging.info("Validate_Server1_Failback_Status After FORCE_Restart")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))

                Validate_Server_Fail_back_Status("Server1")
                print(Server_data)
                if (('"availability": "DARKGRAY"' in Server_data) and ('"description": "Temporarily Disabled"' in Server_data) and (int(check_master)==0) and (int(check_member_1)==0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 60 Execution Completed")

        @pytest.mark.run(order=61)
        def test_061_Validate_Server1_Failback_Status_On_Each_node(self):
                logging.info("Validate_Server1_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("server","Server1")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in disabled) and (config.grid_member1_fqdn in disabled) and (config.grid_member2_fqdn in disabled)):
                    assert True
                else:
                    assert False
                print("Test Case 61 Execution Completed")

        @pytest.mark.run(order=62)
        def test_062_Validate_server1_Failback_After_Specified_Time_Expires(self):
                logging.info("Validate_server1_Failback After Specified_Time_Expires")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                sleep(100)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))

                Validate_Server_Fail_back_Status("Server1")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 62 Execution Completed")
        
        @pytest.mark.run(order=63)
        def test_063_Validate_Server1_Failback_Status_On_Each_node(self):
                logging.info("Validate_Server1_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("server","Server1")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in enabled) and (config.grid_member1_fqdn in enabled) and (config.grid_member2_fqdn in enabled)):
                    assert True
                else:
                    assert False
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_member1_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.active_ip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.passive_ip)
                print("Test Case 63 Execution Completed")

        @pytest.mark.run(order=64)
        def test_064_Perform_server1_Failback_with_SPECIFIED_TIME_NIOS_84919(self):
                logging.info("Perform_server1_Failback_with_SPECIFIED_TIME NIOS_84919")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object":str(reference),"specific_time_disable":140}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(25)
                print("Test Case 64 Execution Completed")

        @pytest.mark.run(order=65)
        def test_065_Validate_Server1_Failback_Status_for_SPECIFIED_TIME_NIOS_84919(self):
                logging.info("Validate_Server1_Failback_Status for SPECIFIED_TIME NIOS_84919")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server1 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server1 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))

                Validate_Server_Fail_back_Status("Server1")
                print(Server_data)
                if (('"availability": "DARKGRAY"' in Server_data) and ('"description": "Temporarily Disabled"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 65 Execution Completed")

        @pytest.mark.run(order=66)
        def test_066_Validate_Server1_Failback_Status_On_Each_node_NIOS_84919(self):
                logging.info("Validate_Server1_Failback_Status_On_Each_node NIOS_84919")
                DTC_Object_Fail_back_GET_State("server","Server1")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in disabled) and (config.grid_member1_fqdn in disabled) and (config.grid_member2_fqdn in disabled)):
                    assert True
                else:
                    assert False
                print("Test Case 66 Execution Completed")

        @pytest.mark.run(order=67)
        def test_067_Perform_server1_Failback_Enable_On_All_Nodes_NIOS_84919(self):
                logging.info("Perform_server1_Failback_Enable All Nodes NIOS_84919")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server1")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                print(enable_output)
                assert re.search(r'"failback_status": "SUCCESS"',enable_output)
                sleep(30)
                print("Test Case 67 Execution Completed")

        @pytest.mark.run(order=68)
        def test_068_Validate_Server1_Failback_Status_On_All_Nodes_NIOS_84919(self):
                logging.info("Validate_Server1_Failback_Status On All_Nodes NIOS_84919")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server1")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 68 Execution Completed") 

        @pytest.mark.run(order=69)
        def test_069_Validate_Server1_Failback_Status_On_Each_node_NIOS_84919(self):
                logging.info("Validate_Server1_Failback_Status_On_Each_node NIOS_84919")
                DTC_Object_Fail_back_GET_State("server","Server1")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in enabled) and (config.grid_member1_fqdn in enabled) and (config.grid_member2_fqdn in enabled)):
                    assert True
                else:
                    assert False
                print("Test Case 69 Execution Completed")

        @pytest.mark.run(order=70)
        def test_070_Perform_server1_Failback_with_UNTIL_MANUAL_ENABLING_NIOS_84919(self):
                logging.info("Perform_server1_Failback_with_UNTIL_MANUAL_ENABLING NIOS_84919")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 70 Execution Completed")

        @pytest.mark.run(order=71)
        def test_071_Validate_Server1_Failback_Status_of_UNTIL_MANUAL_ENABLING_NIOS_84919(self):
                logging.info("Validate_Server1_Failback_Status of UNTIL_MANUAL_ENABLING NIOS_84919")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server1 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server1 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server1")
                print(Server_data)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 71 Execution Completed")

        @pytest.mark.run(order=72)
        def test_072_Validate_Server1_Failback_Status_On_Each_node_NIOS_84919(self):
                logging.info("Validate_Server1_Failback_Status_On_Each_node NIOS_84919")
                DTC_Object_Fail_back_GET_State("server","Server1")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in disabled) and (config.grid_member1_fqdn in disabled) and (config.grid_member2_fqdn in disabled)):
                    assert True
                else:
                    assert False
                print("Test Case 72 Execution Completed")
	
        @pytest.mark.run(order=73)
        def test_073_Validate_server1_Failback_For_UNTIL_MANUAL_ENABLING_After_Specified_Time_Expires_NIOS_85582(self):
                logging.info("Validate_server1_Failback UNTIL_MANUAL_ENABLING After Specified_Time_Expires NIOS_85582")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                sleep(80)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))

                Validate_Server_Fail_back_Status("Server1")
                print(Server_data)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)==0) and (int(check_member_1)==0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_member1_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.active_ip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.passive_ip)
                print("Test Case 73 Execution Completed")
       		 
#Server With Disable After option
        @pytest.mark.run(order=74)
        def test_074_Perform_server2_Failback_with_UNTIL_MANUAL_ENABLING_With_Disable_After(self):
                logging.info("Perform_server2_Failback_with_UNTIL_MANUAL_ENABLING With_Disable_After")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server2")
                data={"disable_health_monitoring":True,"delayed_disable":True,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 74 Execution Completed")

        @pytest.mark.run(order=75)
        def test_075_Validate_Server2_Failback_Status_of_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Server2_Failback_Status of UNTIL_MANUAL_ENABLING")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*name (Server2) action disable after 40 seconds.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*name (Server2) action disable after 40 seconds.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*name (Server2) action disable after 40 seconds.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))

                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 75 Execution Completed")

        @pytest.mark.run(order=76)
        def test_076_Validate_server2_Failback_For_UNTIL_MANUAL_ENABLING_After_Specified_Time_Expires(self):
                logging.info("Validate_server2_Failback UNTIL_MANUAL_ENABLING After Specified_Time_Expires")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                sleep(40)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 76 Execution Completed")

        @pytest.mark.run(order=77)
        def test_077_Enable_server2_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_server2_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference("server","Server2")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member_fqdn,config.grid_member1_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(30)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 77 Execution Completed")
       		 
        @pytest.mark.run(order=78)
        def test_078_Perform_server2_Failback_with_UNTIL_DNS_RESTART_With_Disable_After(self):
                logging.info("Perform_server2_Failback_with_UNTIL_DNS_RESTART With_Disable_After")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server2")
                data={"disable_health_monitoring":True,"delayed_disable":True,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"UNTIL_DNS_RESTART","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 78 Execution Completed") 

        @pytest.mark.run(order=79)
        def test_079_Validate_Server2_Failback_Status_of_UNTIL_DNS_RESTART(self):
                logging.info("Validate_Server2_Failback_Status of UNTIL_DNS_RESTART")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*name (Server2) action disable after 40 seconds.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*name (Server2) action disable after 40 seconds.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*name (Server2) action disable after 40 seconds.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))

                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 79 Execution Completed")

        @pytest.mark.run(order=80)
        def test_080_Validate_server2_Failback_For_UNTIL_DNS_RESTART_After_Specified_Time_Expires(self):
                logging.info("Validate_server2_Failback UNTIL_DNS_RESTART After Specified_Time_Expires")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                sleep(40)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))

                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "DARKGRAY"' in Server_data) and ('"description": "Temporarily Disabled"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 80 Execution Completed")

        @pytest.mark.run(order=81)
        def test_081_Enable_server2_Failback_For_UNTIL_DNS_RESTART(self):
                logging.info("Validate_server2_Failback UNTIL_DNS_RESTART")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                data={"enable_on":[config.grid_member_fqdn,config.grid_member_fqdn,config.grid_member1_fqdn],"dtc_object":str(reference)}
                restart_services()
                sleep(30)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 81 Execution Completed")
        
        @pytest.mark.run(order=82)
        def test_082_Perform_server2_Failback_FOR_SPECIFIED_TIME_With_Disable_After(self):
                logging.info("Perform_server2_Failback FOR_SPECIFIED_TIME With_Disable_After")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server2")
                data={"disable_health_monitoring":True,"delayed_disable":True,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object":str(reference),"specific_time_disable":70}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(10)
                print("Test Case 82 Execution Completed")

        @pytest.mark.run(order=83)
        def test_083_Validate_Server2_Failback_Status_of_FOR_SPECIFIED_TIME(self):
                logging.info("Validate_Server2_Failback_Status of FOR_SPECIFIED_TIME")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*name (Server2) action disable after 40 seconds.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*name (Server2) action disable after 40 seconds.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*name (Server2) action disable after 40 seconds.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 83 Execution Completed")

        @pytest.mark.run(order=84)
        def test_084_Validate_server2_Failback_FOR_SPECIFIED_TIME_After_Specified_Time_Expires(self):
                logging.info("Validate_server2_Failback FOR_SPECIFIED_TIME After Specified_Time_Expires")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                sleep(40)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))

                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "DARKGRAY"' in Server_data) and ('"description": "Temporarily Disabled"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 84 Execution Completed")

        @pytest.mark.run(order=85)
        def test_085_Enable_server1_Failback_FOR_SPECIFIED_TIME_After_Specified_Time_Expires(self):
                logging.info("Validate_server2_Failback FOR_SPECIFIED_TIME After Specified_Time_Expires")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server2")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member_fqdn,config.grid_member1_fqdn],"dtc_object":str(reference)}
                sleep(100)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_member1_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.active_ip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.passive_ip)
                print("Test Case 85 Execution Completed")
		
        @pytest.mark.run(order=86)
        def test_086_add_a_DTC_Server3(self):
                logging.info("Create DTC Server")
                data = {"name":"Server3","host":config.Server3}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 86 Execution Completed")

        @pytest.mark.run(order=87)
        def test_087_Validate_Created_Server3(self):
                logging.info("Validate Created Server3")
                Getting_DTC_Object_Reference("server","Server3")
                assert re.search(r'Server3',reference)
                sleep(5)
                print("Test Case 87 Execution Completed")

        @pytest.mark.run(order=88)
        def test_088_add_a_DTC_Server4(self):
                logging.info("Create DTC Server4")
                data = {"name":"Server4","host":config.Server4}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 88 Execution Completed")

        @pytest.mark.run(order=89)
        def test_089_Validate_Created_Server4(self):
                logging.info("Validate Created Server4")
                Getting_DTC_Object_Reference("server","Server4")
                assert re.search(r'Server4',reference)
                sleep(5)
                print("Test Case 89 Execution Completed")

        @pytest.mark.run(order=90)
        def test_090_add_DTC_pool2(self):
                logging.info("Create DTC Pool2")
                data= {"name": "Pool2","lb_preferred_method": "ROUND_ROBIN","servers": [{"ratio": 1,"server": "dtc:server/ZG5zLmlkbnNfc2VydmVyJFNlcnZlcjM:Server3"},{"ratio": 1,"server": "dtc:server/ZG5zLmlkbnNfc2VydmVyJFNlcnZlcjQ:Server4"}],"monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:pool", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 90 Execution Completed")

        @pytest.mark.run(order=91)
        def test_091_Validate_Created_Pool(self):
                logging.info("Validate Created Pool")
                Getting_DTC_Object_Reference("pool","Pool2")
                assert re.search(r'Pool2',reference)
                sleep(5)
                print("Test Case 91 Execution Completed") 

        @pytest.mark.run(order=92)
        def test_092_Update_DTC_lbdn_with_Pool2(self):
                logging.info("Update_DTC_lbdn_with_Pool2")
                data = {"pools": [{"pool":"dtc:pool/ZG5zLmlkbnNfcG9vbCRQb29sMQ:Pool1","ratio": 1},{"pool":"dtc:pool/ZG5zLmlkbnNfcG9vbCRQb29sMg:Pool2","ratio": 1}]}
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                response = ib_NIOS.wapi_request('PUT', object_type=reference, fields=json.dumps(data))
                restart_services()
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                sleep(20)
                logging.info("Test Case 92 Execution Completed")
        
        @pytest.mark.run(order=93)
        def test_093_Validate_updated_Lbdn(self):
                logging.info("Validate updated Lbdn")
                Validate_Lbdn_Fail_back_Status("Lbdn")
                assert re.search(r'Pool2',Lbdn_data)
                sleep(5)
                print("Test Case 93 Execution Completed")
         
#Disabling Pool
        @pytest.mark.run(order=94)
        def test_094_Perform_Pool1_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_Pool1_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 94 Execution Completed")

        @pytest.mark.run(order=95)
        def test_095_Validate_Pool1_Failback_Status_of_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Pool1_Failback_Status of UNTIL_MANUAL_ENABLING")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))

                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "WHITE"' in Pool_data) and ('"description": "Requires Manual enabling"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 95 Execution Completed")

        @pytest.mark.run(order=96)
        def test_096_Validate_Pool1_Failback_Status_On_Each_node(self):
                logging.info("Validate_Pool1_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("pool","Pool1")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in disabled) and (config.grid_member1_fqdn in disabled) and (config.grid_member2_fqdn in enabled)):
                    assert True
                else:
                    assert False
                print("Test Case 96 Execution Completed")

        @pytest.mark.run(order=97)
        def test_097_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
                if ((Server3 in dig_result_1) and (Server4 in dig_result_2) and (Server3 in dig_result_3) and (Server4 in dig_result_4) and (Server1 in dig_result_5) and (Server3 in dig_result_6) ):
                    assert True
                else:
                    assert False
                print("Test Case 97 Execution Completed")

        @pytest.mark.run(order=98)
        def test_098_Perform_Pool1_Failback_with_UNTIL_MANUAL_ENABLING_Negative(self):
                logging.info("Perform_Pool1_Failback_with_UNTIL_MANUAL_ENABLING_Negative")
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                print(failback_output)
                assert re.search(r'"text": "The DTC object Pool1 is already disabled"',failback_output)
                sleep(5)
                print("Test Case 98 Execution Completed")

        @pytest.mark.run(order=99)
        def test_099_Perform_Pool1_Failback_Enable_On_Master(self):
                logging.info("Perform_Pool1_Failback_Enable On_Master")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"enable_on":[config.grid_member_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                print(enable_output)
                assert re.search(r'"failback_status": "SUCCESS"',enable_output)
                sleep(10)
                print("Test Case 99 Execution Completed")

        @pytest.mark.run(order=100)
        def test_100_Perform_pool1_Failback_Enable_On_Master(self):
                logging.info("Perform_pool1_Failback_Enable On_Master")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"enable_on":[config.grid_member_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                print(enable_output)
                assert re.search(r'"failback_status": "SUCCESS"',enable_output)
                sleep(10)
                print("Test Case 100 Execution Completed")

        @pytest.mark.run(order=101)
        def test_101_Validate_Pool1_Failback_Status_On_Master(self):
                logging.info("Validate_Pool1_Failback_Status On_Master")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "WHITE"' in Pool_data) and ('"description": "Requires Manual enabling"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 101 Execution Completed")

        @pytest.mark.run(order=102)
        def test_102_Validate_Pool1_Failback_Status_On_Each_node(self):
                logging.info("Validate_Pool1_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("pool","Pool1")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in enabled) and (config.grid_member1_fqdn in disabled) and (config.grid_member2_fqdn in enabled)):
                    assert True
                else:
                    assert False
                print("Test Case 102 Execution Completed")

        @pytest.mark.run(order=103)
        def test_103_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
                if ((Server1 in dig_result_1) and (Server3 in dig_result_2) and (Server3 in dig_result_3) and (Server4 in dig_result_4) and (Server2 in dig_result_5) and (Server4 in dig_result_6) ):
                    assert True
                else:
                    assert False
                print("Test Case 103 Execution Completed")
		
        @pytest.mark.run(order=104)
        def test_104_Perform_Pool1_Failback_Enable_On_Member1(self):
                logging.info("Perform_Pool1_Failback_Enable on Member1")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"enable_on":[config.grid_member1_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                print(enable_output)
                assert re.search(r'"failback_status": "SUCCESS"',enable_output)
                sleep(15)
                print("Test Case 104 Execution Completed")

        @pytest.mark.run(order=105)
        def test_105_Validate_Pool1_Failback_Status_On_Member1(self):
                logging.info("Validate_Pool1_Failback_Status On_Member1")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))

                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data) and (int(check_master)==0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 105 Execution Completed")

        @pytest.mark.run(order=106)
        def test_106_Validate_Pool1_Failback_Status_On_Each_node(self):
                logging.info("Validate_Pool1_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("pool","Pool1")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in enabled) and (config.grid_member1_fqdn in enabled) and (config.grid_member2_fqdn in enabled)):
                    assert True
                else:
                    assert False
		validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_member1_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.active_ip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.passive_ip)
                print("Test Case 106 Execution Completed")

        @pytest.mark.run(order=107)
        def test_107_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
                if ((Server2 in dig_result_1) and (Server4 in dig_result_2) and (Server1 in dig_result_3) and (Server3 in dig_result_4) and (Server1 in dig_result_5) and (Server3 in dig_result_6) ):
                    assert True
                else:
                    assert False
                print("Test Case 107 Execution Completed")
        
        @pytest.mark.run(order=108)
        def test_108_Perform_Pool1_Failback_with_UNTIL_DNS_RESTART(self):
                logging.info("Perform_Pool1_Failback_with_UNTIL_DNS_RESTART")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_DNS_RESTART","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(15)
                print("Test Case 108 Execution Completed")

        @pytest.mark.run(order=109)
        def test_109_Validate_Pool1_Failback_Status_for_UNTIL_DNS_RESTART(self):
                logging.info("Validate_Pool1_Failback_Status for UNTIL_DNS_RESTART")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "DARKGRAY"' in Pool_data) and ('"description": "Temporarily Disabled"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 109 Execution Completed")

        @pytest.mark.run(order=110)
        def test_110_Validate_Pool1_Failback_Status_On_Each_node(self):
                logging.info("Validate_Pool1_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("pool","Pool1")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in disabled) and (config.grid_member1_fqdn in enabled) and (config.grid_member2_fqdn in disabled)):
                    assert True
                else:
                    assert False
                print("Test Case 110 Execution Completed")

        @pytest.mark.run(order=111)
        def test_111_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
                if ((Server3 in dig_result_1) and (Server4 in dig_result_2) and (Server2 in dig_result_3) and (Server4 in dig_result_4) and (Server4 in dig_result_5) and (Server3 in dig_result_6) ):
                    assert True
                else:
                    assert False
                print("Test Case 111 Execution Completed")
                
                
        @pytest.mark.run(order=112)
        def test_112_Perform_Pool1_Failback_Enable_with_IFNEEDED_Restart(self):
                logging.info("Perform_Pool1_Failback_Enable_with_IFNEEDED_Restart")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                restart_services_IF_NEEDED()
                sleep(15)
                print("Test Case 112 Execution Completed")

        @pytest.mark.run(order=113)
        def test_113_Validate_Pool1_Failback_Status_For_IFNEEDED_Restart(self):
                logging.info("Validate_Pool1_Failback_Status for IFNEEDED_Restart")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))

                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "DARKGRAY"' in Pool_data) and ('"description": "Temporarily Disabled"' in Pool_data) and (int(check_master)==0) and (int(check_member_1)==0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 113 Execution Completed")
                
        @pytest.mark.run(order=114)
        def test_114_Perform_Pool1_Failback_Enable_with_FORCE_Restart(self):
                logging.info("Perform_Pool1_Failback_Enable_with_FORCE_Restart")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                restart_services()
                sleep(25)
                print("Test Case 114 Execution Completed")

        @pytest.mark.run(order=115)
        def test_115_Validate_Pool1_Failback_Status_For_FORCE_Restart(self):
                logging.info("Validate_Pool1_Failback_Status for FORCE_Restart")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))

                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 115 Execution Completed")
                
        @pytest.mark.run(order=116)
        def test_116_Validate_Pool1_Failback_Status_On_Each_node(self):
                logging.info("Validate_Pool1_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("pool","Pool1")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in enabled) and (config.grid_member1_fqdn in enabled) and (config.grid_member2_fqdn in enabled)):
                    assert True
                else:
                    assert False
                print("Test Case 116 Execution Completed")

        @pytest.mark.run(order=117)
        def test_117_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
                if ((Server1 in dig_result_1) and (Server3 in dig_result_2) and (Server1 in dig_result_3) and (Server3 in dig_result_4) and (Server1 in dig_result_5) and (Server3 in dig_result_6) ):
                    assert True
                else:
                    assert False
                print("Test Case 117 Execution Completed")
                 
        @pytest.mark.run(order=118)
        def test_118_Perform_Pool1_Failback_with_UNTIL_DNS_RESTART_For_Manual_Enable(self):
                logging.info("Perform_Pool1_Failback_with_UNTIL_DNS_RESTART For_Manual_Enable")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_DNS_RESTART","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(15)
                print("Test Case 118 Execution Completed")

        @pytest.mark.run(order=119)
        def test_119_Validate_Pool1_Failback_Status_For_Manual_Enable(self):
                logging.info("Validate_Pool1_Failback_Status For_Manual_Enable")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))

                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "DARKGRAY"' in Pool_data) and ('"description": "Temporarily Disabled"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 119 Execution Completed")
                
        @pytest.mark.run(order=120)
        def test_120_Validate_Pool1_Failback_Status_On_Each_node(self):
                logging.info("Validate_Pool1_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("pool","Pool1")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in disabled) and (config.grid_member1_fqdn in disabled) and (config.grid_member2_fqdn in disabled)):
                    assert True
                else:
                    assert False
                print("Test Case 120 Execution Completed")
		
        @pytest.mark.run(order=121)
        def test_121_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
                if (((Server1 and Server2) not in dig_result_1) and ((Server3 or Server4) in dig_result_2) and ((Server1 and Server2) not in dig_result_3) and ((Server3 or Server4) in dig_result_4) and ((Server1 and Server2) not in dig_result_5) and ((Server3 or Server4) in dig_result_6) ):
                    assert True
                else:
                    assert False
                print("Test Case 121 Execution Completed")
                
        @pytest.mark.run(order=122)
        def test_122_Perform_Pool1_Failback_with_UNTIL_DNS_RESTART_Negative(self):
                logging.info("Perform_Pool1_Failback_with_UNTIL_DNS_RESTART_Negative")
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member1_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                print(failback_output)
                assert re.search(r'"text": "The DTC object Pool1 is already disabled"',failback_output)
                sleep(5)
                print("Test Case 122 Execution Completed")

        @pytest.mark.run(order=123)
        def test_123_Perform_Pool1_Failback_Enable_On_master(self):
                logging.info("Perform_Pool1_Failback_Enable on master")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"enable_on":[config.grid_member_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                print(enable_output)
                assert re.search(r'"failback_status": "SUCCESS"',enable_output)
                sleep(15)
                print("Test Case 123 Execution Completed")
                
        @pytest.mark.run(order=124)
        def test_124_Validate_Pool1_Failback_Status(self):
                logging.info("Validate_Pool1_Failback_Status")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))

                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "DARKGRAY"' in Pool_data) and ('"description": "Temporarily Disabled"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 124 Execution Completed")
	
        @pytest.mark.run(order=125)
        def test_125_Validate_Pool1_Failback_Status_On_Each_node(self):
                logging.info("Validate_Pool1_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("pool","Pool1")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in enabled) and (config.grid_member1_fqdn in disabled) and (config.grid_member2_fqdn in disabled)):
                    assert True
                else:
                    assert False
                print("Test Case 125 Execution Completed")
                
        @pytest.mark.run(order=126)
        def test_126_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
		dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
                if (((Server1 in dig_result_1) or (Server2 in dig_result_1)) and ((Server3 in dig_result_2) or (Server4 in dig_result_2)) and ((Server1 or Server2) not in dig_result_3) and ((Server3 or Server4) in dig_result_4) and ((Server1 or Server2) not in dig_result_5) and ((Server3 or Server4) in dig_result_6)):
                    assert True
                else:
                    assert False
                print("Test Case 126 Execution Completed")

        @pytest.mark.run(order=127)
        def test_127_Perform_Pool1_Failback_Enable_On_Members(self):
                logging.info("Perform_Pool1_Failback_Enable on members")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"enable_on":[config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                print(enable_output)
                assert re.search(r'"failback_status": "SUCCESS"',enable_output)
                sleep(30)
                print("Test Case 127 Execution Completed")
                
        @pytest.mark.run(order=128)
        def test_128_Validate_Pool1_Failback_Status(self):
                logging.info("Validate_Pool1_Failback_Status")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))

                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data) and (int(check_master)==0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 128 Execution Completed")

        @pytest.mark.run(order=129)
        def test_129_Validate_Pool1_Failback_Status_On_Each_node(self):
                logging.info("Validate_Pool1_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("pool","Pool1")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in enabled) and (config.grid_member1_fqdn in enabled) and (config.grid_member2_fqdn in enabled)):
                    assert True
                else:
                    assert False
		validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_member1_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.active_ip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.passive_ip)
                print("Test Case 129 Execution Completed")
                
        @pytest.mark.run(order=130)
        def test_130_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
		if(((Server1 in dig_result_1) or (Server2 in dig_result_1)) and ((Server3 in dig_result_2) or (Server4 in dig_result_2)) and ((Server1 in dig_result_3) or (Server2 in dig_result_3)) and ((Server3 in dig_result_4) or (Server4 in dig_result_4)) and ((Server1 in dig_result_5) or (Server2 in dig_result_5)) and ((Server3 in dig_result_6) or (Server4 in dig_result_6))):
                    assert True
                else:
                    assert False
                print("Test Case 130 Execution Completed")

        @pytest.mark.run(order=131)
        def test_131_Perform_Pool1_Failback_with_SPECIFIED_TIME(self):
                logging.info("Perform_Pool1_Failback_with_SPECIFIED_TIME")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object":str(reference),"specific_time_disable":140}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(15)
                print("Test Case 131 Execution Completed")
                
        @pytest.mark.run(order=132)
        def test_132_Validate_Pool1_Failback_Status_for_SPECIFIED_TIME(self):
                logging.info("Validate_Pool1_Failback_Status for SPECIFIED_TIME")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "DARKGRAY"' in Pool_data) and ('"description": "Temporarily Disabled"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 132 Execution Completed")

        @pytest.mark.run(order=133)
        def test_133_Validate_Pool1_Failback_Status_On_Each_node(self):
                logging.info("Validate_Pool1_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("pool","Pool1")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in disabled) and (config.grid_member1_fqdn in disabled) and (config.grid_member2_fqdn in disabled)):
                    assert True
                else:
                    assert False
                print("Test Case 133 Execution Completed")
                
        @pytest.mark.run(order=134)
        def test_134_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
		L=[dig_result_1,dig_result_2,dig_result_3,dig_result_4,dig_result_5,dig_result_6]
		for i in L:
			if((Server1 not in i) and (Server2 not in i)):
                   		assert True
                	else:
                    		assert False
                print("Test Case 134 Execution Completed")

        @pytest.mark.run(order=135)
        def test_135_Perform_Pool1_Failback_Enable_with_FORCE_Restart_Negative(self):
                logging.info("Perform_Pool1_Failback_Enable_with_FORCE_Restart Negative")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                restart_services()
                sleep(2)
                print("Test Case 135 Execution Completed")
                
        @pytest.mark.run(order=136)
        def test_136_Validate_Pool1_Failback_Status_After_FORCE_Restart(self):
                logging.info("Validate_Pool1_Failback_Status After FORCE_Restart")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "DARKGRAY"' in Pool_data) and ('"description": "Temporarily Disabled"' in Pool_data) and (int(check_master)==0) and (int(check_member_1)==0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 136 Execution Completed")

        @pytest.mark.run(order=137)
        def test_137_Validate_Pool1_Failback_Status_On_Each_node(self):
                logging.info("Validate_Pool1_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("pool","Pool1")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in disabled) and (config.grid_member1_fqdn in disabled) and (config.grid_member2_fqdn in disabled)):
                    assert True
                else:
                    assert False
                print("Test Case 137 Execution Completed")
        
        @pytest.mark.run(order=138)
        def test_138_Validate_Pool1_Failback_After_Specified_Time_Expires(self):
                logging.info("Validate_Pool1_Failback After Specified_Time_Expires")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                sleep(120)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 138 Execution Completed")

        @pytest.mark.run(order=139)
        def test_139_Validate_Pool1_Failback_Status_On_Each_node(self):
                logging.info("Validate_Pool1_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("pool","Pool1")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in enabled) and (config.grid_member1_fqdn in enabled) and (config.grid_member2_fqdn in enabled)):
                    assert True
                else:
                    assert False
		validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_member1_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.active_ip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.passive_ip)
                print("Test Case 139 Execution Completed")
		
#Pool with Disable after option       
        
        @pytest.mark.run(order=140)
        def test_140_Perform_Pool2_Failback_with_UNTIL_MANUAL_ENABLING_With_Disable_After(self):
                logging.info("Perform_Pool2_Failback_with_UNTIL_MANUAL_ENABLING With_Disable_After")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool2")
                data={"disable_health_monitoring":True,"delayed_disable":True,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(25)
                print("Test Case 140 Execution Completed")

        @pytest.mark.run(order=141)
        def test_141_Validate_Pool2_Failback_Status_of_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Pool2_Failback_Status of UNTIL_MANUAL_ENABLING")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*name (Pool2) action disable after 40 seconds.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*name (Pool2) action disable after 40 seconds.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*name (Pool2) action disable after 40 seconds.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))

                Validate_Pool_Fail_back_Status("Pool2")
                print(Pool_data)
                if (('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 141 Execution Completed")

        @pytest.mark.run(order=142)
        def test_142_Validate_Pool2_Failback_For_UNTIL_MANUAL_ENABLING_After_Specified_Time_Expires(self):
                logging.info("Validate_Pool2_Failback UNTIL_MANUAL_ENABLING After Specified_Time_Expires")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                sleep(40)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool2")
                print(Pool_data)
                if (('"availability": "WHITE"' in Pool_data) and ('"description": "Requires Manual enabling"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 142 Execution Completed")
	
        @pytest.mark.run(order=143)
        def test_143_Enable_Pool2_Failback_For_UNTIL_MANUAL_ENABLING_After_Specified_Time_Expires(self):
                logging.info("Validate_Pool2_Failback UNTIL_MANUAL_ENABLING After Specified_Time_Expires")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference("pool","Pool2")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member_fqdn,config.grid_member1_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(30)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool2 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool2 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool2 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool2")
                print(Pool_data)
                if (('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 143 Execution Completed")
	
        @pytest.mark.run(order=144)
        def test_144_Perform_Pool2_Failback_with_UNTIL_DNS_RESTART_With_Disable_After(self):
                logging.info("Perform_Pool2_Failback_with_UNTIL_DNS_RESTART With_Disable_After")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool2")
                data={"disable_health_monitoring":True,"delayed_disable":True,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"UNTIL_DNS_RESTART","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 144 Execution Completed")

        @pytest.mark.run(order=145)
        def test_145_Validate_Pool2_Failback_Status_of_UNTIL_DNS_RESTART(self):
                logging.info("Validate_Pool2_Failback_Status of UNTIL_DNS_RESTART")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*name (Pool2) action disable after 40 seconds.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*name (Pool2) action disable after 40 seconds.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*name (Pool2) action disable after 40 seconds.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool2")
                print(Pool_data)
                if (('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 145 Execution Completed")

        @pytest.mark.run(order=146)
        def test_146_Validate_Pool2_Failback_For_UNTIL_DNS_RESTART_After_Specified_Time_Expires(self):
                logging.info("Validate_Pool2_Failback UNTIL_DNS_RESTART After Specified_Time_Expires")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                sleep(30)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool2")
                print(Pool_data)
                if (('"availability": "DARKGRAY"' in Pool_data) and ('"description": "Temporarily Disabled"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 146 Execution Completed")

        @pytest.mark.run(order=147)
        def test_147_Enable_Pool2_Failback_For_UNTIL_DNS_RESTART_After_Specified_Time_Expires(self):
                logging.info("Validate_Pool2_Failback UNTIL_DNS_RESTART After Specified_Time_Expires")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                data={"enable_on":[config.grid_member_fqdn,config.grid_member_fqdn,config.grid_member1_fqdn],"dtc_object":str(reference)}
                restart_services()
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool2 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool2 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool2 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool2")
                print(Pool_data)
                if (('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 147 Execution Completed")

        @pytest.mark.run(order=148)
        def test_148_Perform_Pool2_Failback_FOR_SPECIFIED_TIME_With_Disable_After(self):
                logging.info("Perform_Pool2_Failback FOR_SPECIFIED_TIME With_Disable_After")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool2")
                data={"disable_health_monitoring":True,"delayed_disable":True,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object":str(reference),"specific_time_disable":40}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 148 Execution Completed")

        @pytest.mark.run(order=149)
        def test_149_Validate_Pool2_Failback_Status_of_FOR_SPECIFIED_TIME(self):
                logging.info("Validate_Pool2_Failback_Status of FOR_SPECIFIED_TIME")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*name (Pool2) action disable after 40 seconds.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*name (Pool2) action disable after 40 seconds.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*name (Pool2) action disable after 40 seconds.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool2")
                print(Pool_data)
                if (('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 149 Execution Completed")

        @pytest.mark.run(order=150)
        def test_150_Validate_Pool2_Failback_FOR_SPECIFIED_TIME_After_Specified_Time_Expires(self):
                logging.info("Validate_Pool2_Failback FOR_SPECIFIED_TIME After Specified_Time_Expires")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                sleep(40)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool2")
                print(Pool_data)
                if (('"availability": "DARKGRAY"' in Pool_data) and ('"description": "Temporarily Disabled"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 150 Execution Completed")

        @pytest.mark.run(order=151)
        def test_151_Enable_Pool2_Failback_FOR_SPECIFIED_TIME_After_Specified_Time_Expires(self):
                logging.info("Validate_Pool2_Failback FOR_SPECIFIED_TIME After Specified_Time_Expires")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool2")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member_fqdn,config.grid_member1_fqdn],"dtc_object":str(reference)}
                sleep(50)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool2 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool2 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool2 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool2")
                print(Pool_data)
                if (('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_member1_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.active_ip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.passive_ip)
                print("Test Case 151 Execution Completed")
        	 
        @pytest.mark.run(order=152)
        def test_152_Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 152 Execution Completed")

        @pytest.mark.run(order=153)
        def test_153_Validate_Lbdn_Failback_Status_of_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Lbdn_Failback_Status of UNTIL_MANUAL_ENABLING")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "WHITE"' in Lbdn_data) and ('"description": "Requires Manual enabling"' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 153 Execution Completed")

        @pytest.mark.run(order=154)
        def test_154_Validate_Lbdn_Failback_Status_On_Each_node(self):
                logging.info("Validate_Lbdn_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("lbdn","Lbdn")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in disabled) and (config.grid_member1_fqdn in disabled) and (config.grid_member2_fqdn in enabled)):
                    assert True
                else:
                    assert False
                print("Test Case 154 Execution Completed")

        @pytest.mark.run(order=155)
        def test_155_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
                if ((config.grid_member_fqdn in dig_result_1) and (config.grid_member_fqdn in dig_result_2) and (config.grid_member1_fqdn in dig_result_3) and (config.grid_member1_fqdn in dig_result_4) and (config.grid_member2_fqdn not in dig_result_5) and (config.grid_member2_fqdn not in dig_result_6) ):
                    assert True
                else:
                    assert False
                print("Test Case 155 Execution Completed")

        @pytest.mark.run(order=156)
        def test_156_Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING_Negative(self):
                logging.info("Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING_Negative")
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                print(failback_output)
                assert re.search(r'"text": "The DTC object Lbdn is already disabled"',failback_output)
                sleep(5)
                print("Test Case 156 Execution Completed")

        @pytest.mark.run(order=157)
        def test_157_Perform_Lbdn_Failback_Enable_On_Master(self):
                logging.info("Perform_Lbdn_Failback_Enable On_Master")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"enable_on":[config.grid_member_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                print(enable_output)
                assert re.search(r'"failback_status": "SUCCESS"',enable_output)
                sleep(10)
                print("Test Case 157 Execution Completed")

        @pytest.mark.run(order=158)
        def test_158_Validate_Lbdn_Failback_Status_On_Master(self):
                logging.info("Validate_Lbdn_Failback_Status On_Master")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "WHITE"' in Lbdn_data) and ('"description": "Requires Manual enabling"' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 158 Execution Completed")

        @pytest.mark.run(order=159)
        def test_159_Validate_Lbdn_Failback_Status_On_Each_node(self):
                logging.info("Validate_Lbdn_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("lbdn","Lbdn")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in enabled) and (config.grid_member1_fqdn in disabled) and (config.grid_member2_fqdn in enabled)):
                    assert True
                else:
                    assert False
                print("Test Case 159 Execution Completed")

        @pytest.mark.run(order=160)
        def test_160_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
                if ((config.grid_member_fqdn not in dig_result_1) and (config.grid_member_fqdn not in dig_result_2) and (config.grid_member1_fqdn in dig_result_3) and (config.grid_member1_fqdn in dig_result_4) and (config.grid_member2_fqdn not in dig_result_5) and (config.grid_member2_fqdn not in dig_result_6) ):
                    assert True
                else:
                    assert False
                print("Test Case 160 Execution Completed")

        @pytest.mark.run(order=161)
        def test_161_Perform_Lbdn_Failback_Enable_On_Member1(self):
                logging.info("Perform_Lbdn_Failback_Enable on Member1")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"enable_on":[config.grid_member1_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                print(enable_output)
                assert re.search(r'"failback_status": "SUCCESS"',enable_output)
                sleep(15)
                print("Test Case 161 Execution Completed")

        @pytest.mark.run(order=162)
        def test_162_Validate_Lbdn_Failback_Status_On_Member1(self):
                logging.info("Validate_Lbdn_Failback_Status On_Member1")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)==0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 162 Execution Completed")

        @pytest.mark.run(order=163)
        def test_163_Validate_Lbdn_Failback_Status_On_Each_node(self):
                logging.info("Validate_Lbdn_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("lbdn","Lbdn")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in enabled) and (config.grid_member1_fqdn in enabled) and (config.grid_member2_fqdn in enabled)):
                    assert True
                else:
                    assert False
		validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_member1_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.active_ip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.passive_ip)
                print("Test Case 163 Execution Completed")
	
        @pytest.mark.run(order=164)
        def test_164_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
		L=[dig_result_1,dig_result_2,dig_result_3,dig_result_4,dig_result_5,dig_result_6]
                for i in L:
                        if((Server1 in i) or (Server2 in i) or (Server3 in i) or (Server4 in i)):
                	    assert True
                	else:
                    	    assert False
                print("Test Case 164 Execution Completed")

        @pytest.mark.run(order=165)
        def test_165_Perform_Lbdn_Failback_with_UNTIL_DNS_RESTART(self):
                logging.info("Perform_Lbdn_Failback_with_UNTIL_DNS_RESTART")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_DNS_RESTART","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(15)
                print("Test Case 165 Execution Completed")

        @pytest.mark.run(order=166)
        def test_166_Validate_Lbdn_Failback_Status_for_UNTIL_DNS_RESTART(self):
                logging.info("Validate_Lbdn_Failback_Status for UNTIL_DNS_RESTART")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))

                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "DARKGRAY"' in Lbdn_data) and ('"description": "Temporarily Disabled"' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 166 Execution Completed")

        @pytest.mark.run(order=167)
        def test_167_Validate_Lbdn_Failback_Status_On_Each_node(self):
                logging.info("Validate_Lbdn_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("lbdn","Lbdn")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in disabled) and (config.grid_member1_fqdn in enabled) and (config.grid_member2_fqdn in disabled)):
                    assert True
                else:
                    assert False
                print("Test Case 167 Execution Completed")

        @pytest.mark.run(order=168)
        def test_168_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
                if ((config.grid_member_fqdn in dig_result_1) and (config.grid_member_fqdn in dig_result_2) and (config.grid_member1_fqdn not in dig_result_3) and (config.grid_member1_fqdn not in dig_result_4) and (config.grid_member2_fqdn in dig_result_5) and (config.grid_member2_fqdn  in dig_result_6) ):
                    assert True
                else:
                    assert False
                print("Test Case 168 Execution Completed")


        @pytest.mark.run(order=169)
        def test_169_Perform_Lbdn_Failback_Enable_with_IFNEEDED_Restart(self):
                logging.info("Perform_Lbdn_Failback_Enable_with_IFNEEDED_Restart")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                restart_services_IF_NEEDED()
                sleep(15)
                print("Test Case 169 Execution Completed")

        @pytest.mark.run(order=170)
        def test_170_Validate_Lbdn_Failback_Status_For_IFNEEDED_Restart(self):
                logging.info("Validate_Lbdn_Failback_Status for IFNEEDED_Restart")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "DARKGRAY"' in Lbdn_data) and ('"description": "Temporarily Disabled"' in Lbdn_data) and (int(check_master)==0) and (int(check_member_1)==0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 170 Execution Completed")

        @pytest.mark.run(order=171)
        def test_171_Perform_Lbdn_Failback_Enable_with_FORCE_Restart(self):
                logging.info("Perform_Lbdn_Failback_Enable_with_FORCE_Restart")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                restart_services()
                sleep(10)
                print("Test Case 171 Execution Completed")

        @pytest.mark.run(order=172)
        def test_172_Validate_Lbdn_Failback_Status_For_FORCE_Restart(self):
                logging.info("Validate_Lbdn_Failback_Status for FORCE_Restart")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 172 Execution Completed")

        @pytest.mark.run(order=173)
        def test_173_Validate_Lbdn_Failback_Status_On_Each_node(self):
                logging.info("Validate_Lbdn_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("lbdn","Lbdn")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in enabled) and (config.grid_member1_fqdn in enabled) and (config.grid_member2_fqdn in enabled)):
                    assert True
                else:
                    assert False
                print("Test Case 173 Execution Completed")

        @pytest.mark.run(order=174)
        def test_174_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
                if (((Server1 or Server2) in dig_result_1) and ((Server3 or Server4) in dig_result_2) and ((Server1 or Server2) in dig_result_3) and ((Server3 or Server4) in dig_result_4) and ((Server1 or Server2) in dig_result_5) and ((Server3 or Server4) in dig_result_6)):
                    assert True
                else:
                    assert False
                print("Test Case 174 Execution Completed")

        @pytest.mark.run(order=175)
        def test_175_Perform_Lbdn_Failback_with_UNTIL_DNS_RESTART_For_Manual_Enable(self):
                logging.info("Perform_Lbdn_Failback_with_UNTIL_DNS_RESTART For_Manual_Enable")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_DNS_RESTART","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(15)
                print("Test Case 175 Execution Completed")

        @pytest.mark.run(order=176)
        def test_176_Validate_Lbdn_Failback_Status_For_Manual_Enable(self):
                logging.info("Validate_Lbdn_Failback_Status For_Manual_Enable")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "DARKGRAY"' in Lbdn_data) and ('"description": "Temporarily Disabled"' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 176 Execution Completed")

        @pytest.mark.run(order=177)
        def test_177_Validate_Lbdn_Failback_Status_On_Each_node(self):
                logging.info("Validate_Lbdn_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("lbdn","Lbdn")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in disabled) and (config.grid_member1_fqdn in disabled) and (config.grid_member2_fqdn in disabled)):
                    assert True
                else:
                    assert False
                print("Test Case 177 Execution Completed")

        @pytest.mark.run(order=178)
        def test_178_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
                if ((config.grid_member_fqdn in dig_result_1) and (config.grid_member_fqdn in dig_result_2) and (config.grid_member1_fqdn in dig_result_3) and (config.grid_member1_fqdn in dig_result_4) and (config.grid_member2_fqdn in dig_result_5) and (config.grid_member2_fqdn in dig_result_6) ):
                    assert True
                else:
                    assert False
                print("Test Case 178 Execution Completed")

        @pytest.mark.run(order=179)
        def test_179_Perform_Lbdn_Failback_with_UNTIL_DNS_RESTART_Negative(self):
                logging.info("Perform_Lbdn_Failback_with_UNTIL_DNS_RESTART_Negative")
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member1_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                print(failback_output)
                assert re.search(r'"text": "The DTC object Lbdn is already disabled"',failback_output)
                sleep(5)
                print("Test Case 179 Execution Completed")

        @pytest.mark.run(order=180)
        def test_180_Perform_Lbdn_Failback_Enable_On_master(self):
                logging.info("Perform_Lbdn_Failback_Enable on master")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"enable_on":[config.grid_member_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                print(enable_output)
                assert re.search(r'"failback_status": "SUCCESS"',enable_output)
                sleep(15)
                print("Test Case 180 Execution Completed")

        @pytest.mark.run(order=181)
        def test_181_Validate_Lbdn_Failback_Status(self):
                logging.info("Validate_Lbdn_Failback_Status")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "DARKGRAY"' in Lbdn_data) and ('"description": "Temporarily Disabled"' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 181 Execution Completed")

        @pytest.mark.run(order=182)
        def test_182_Validate_Lbdn_Failback_Status_On_Each_node(self):
                logging.info("Validate_Lbdn_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("lbdn","Lbdn")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in enabled) and (config.grid_member1_fqdn in disabled) and (config.grid_member2_fqdn in disabled)):
                    assert True
                else:
                    assert False
                print("Test Case 182 Execution Completed")

        @pytest.mark.run(order=183)
        def test_183_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
                if ((config.grid_member_fqdn not in dig_result_1) and (config.grid_member_fqdn not in dig_result_2) and (config.grid_member1_fqdn in dig_result_3) and (config.grid_member1_fqdn in dig_result_4) and (config.grid_member2_fqdn in dig_result_5) and (config.grid_member2_fqdn in dig_result_6) ):
                    assert True
                else:
                    assert False
                print("Test Case 183 Execution Completed")

        @pytest.mark.run(order=184)
        def test_184_Perform_Lbdn_Failback_Enable_On_Members(self):
                logging.info("Perform_Lbdn_Failback_Enable on members")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"enable_on":[config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                print(enable_output)
                assert re.search(r'"failback_status": "SUCCESS"',enable_output)
                sleep(15)
                print("Test Case 184 Execution Completed")

        @pytest.mark.run(order=185)
        def test_185_Validate_Lbdn_Failback_Status(self):
                logging.info("Validate_Lbdn_Failback_Status")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)==0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 185 Execution Completed")

        @pytest.mark.run(order=186)
        def test_186_Validate_Lbdn_Failback_Status_On_Each_node(self):
                logging.info("Validate_Lbdn_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("lbdn","Lbdn")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in enabled) and (config.grid_member1_fqdn in enabled) and (config.grid_member2_fqdn in enabled)):
                    assert True
                else:
                    assert False
		validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_member1_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.active_ip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.passive_ip)
                print("Test Case 186 Execution Completed")
	
        @pytest.mark.run(order=187)
        def test_187_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
		L=[dig_result_1,dig_result_2,dig_result_3,dig_result_4,dig_result_5,dig_result_6]
		for i in L:
                        if((Server1 in i) or (Server2 in i) or (Server3 in i) or (Server4 in i)):
                    	    assert True
                	else:
                            assert False
                print("Test Case 187 Execution Completed")

        @pytest.mark.run(order=188)
        def test_188_Perform_Lbdn_Failback_with_SPECIFIED_TIME(self):
                logging.info("Perform_Lbdn_Failback_with_SPECIFIED_TIME")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(15)
                print("Test Case 188 Execution Completed")

        @pytest.mark.run(order=189)
        def test_189_Validate_Lbdn_Failback_Status_for_SPECIFIED_TIME(self):
                logging.info("Validate_Lbdn_Failback_Status for SPECIFIED_TIME")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "DARKGRAY"' in Lbdn_data) and ('"description": "Temporarily Disabled"' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 189 Execution Completed")

        @pytest.mark.run(order=190)
        def test_190_Validate_Lbdn_Failback_Status_On_Each_node(self):
                logging.info("Validate_Lbdn_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("lbdn","Lbdn")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in disabled) and (config.grid_member1_fqdn in disabled) and (config.grid_member2_fqdn in disabled)):
                    assert True
                else:
                    assert False
                print("Test Case 190 Execution Completed")

        @pytest.mark.run(order=191)
        def test_191_perform_query_for_DTC_record_for_Master_Member(self):
                logging.info("Executing Dig queries")
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_1 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_1
                dig_cmd = 'dig @'+str(config.grid_vip)+' a1.dtc.com IN a'
                dig_result_2 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_2
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_3 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_3
                dig_cmd = 'dig @'+str(config.grid_member1_vip)+' a1.dtc.com IN a'
                dig_result_4 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_4
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_5 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_5
                dig_cmd = 'dig @'+str(config.grid_member2_vip)+' a1.dtc.com IN a'
                dig_result_6 = subprocess.check_output(dig_cmd, shell=True)
                print dig_result_6
                if ((config.grid_member_fqdn in dig_result_1) and (config.grid_member_fqdn in dig_result_2) and (config.grid_member1_fqdn in dig_result_3) and (config.grid_member1_fqdn in dig_result_4) and (config.grid_member2_fqdn in dig_result_5) and (config.grid_member2_fqdn in dig_result_6)):
                    assert True
                else:
                    assert False
                print("Test Case 191 Execution Completed")

        @pytest.mark.run(order=192)
        def test_192_Perform_Lbdn_Failback_Enable_with_FORCE_Restart_Negative(self):
                logging.info("Perform_Lbdn_Failback_Enable_with_FORCE_Restart Negative")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                restart_services()
                sleep(2)
                print("Test Case 192 Execution Completed")

        @pytest.mark.run(order=193)
        def test_193_Validate_Lbdn_Failback_Status_After_FORCE_Restart(self):
                logging.info("Validate_Lbdn_Failback_Status After FORCE_Restart")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "DARKGRAY"' in Lbdn_data) and ('"description": "Temporarily Disabled"' in Lbdn_data) and (int(check_master)==0) and (int(check_member_1)==0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 193 Execution Completed")

        @pytest.mark.run(order=194)
        def test_194_Validate_Lbdn_Failback_Status_On_Each_node(self):
                logging.info("Validate_Lbdn_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("lbdn","Lbdn")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in disabled) and (config.grid_member1_fqdn in disabled) and (config.grid_member2_fqdn in disabled)):
                    assert True
                else:
                    assert False
                print("Test Case 194 Execution Completed")

        @pytest.mark.run(order=195)
        def test_195_Validate_Lbdn_Failback_After_Specified_Time_Expires(self):
                logging.info("Validate_Lbdn_Failback After Specified_Time_Expires")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                sleep(80)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 195 Execution Completed")

        @pytest.mark.run(order=196)
        def test_196_Validate_Lbdn_Failback_Status_On_Each_node(self):
                logging.info("Validate_Lbdn_Failback_Status_On_Each_node")
                DTC_Object_Fail_back_GET_State("lbdn","Lbdn")
                print(state_output)
                print(type(state_output))
                disabled=state_output.get('disabled_on')
                enabled=state_output.get('enabled_on')
                print(enabled,disabled)
                if ((config.grid_member_fqdn in enabled) and (config.grid_member1_fqdn in enabled) and (config.grid_member2_fqdn in enabled)):
                    assert True
                else:
                    assert False
		validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_member1_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.active_ip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.passive_ip)
                print("Test Case 196 Execution Completed")
		
#lbdn With Disable After option
        @pytest.mark.run(order=197)
        def test_197_Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING_With_Disable_After(self):
                logging.info("Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING With_Disable_After")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":True,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 197 Execution Completed")

        @pytest.mark.run(order=198)
        def test_198_Validate_Lbdn_Failback_Status_of_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Lbdn_Failback_Status of UNTIL_MANUAL_ENABLING")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*name (Lbdn) action disable after 40 seconds.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*name (Lbdn) action disable after 40 seconds.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*name (Lbdn) action disable after 40 seconds.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 198 Execution Completed")

        @pytest.mark.run(order=199)
        def test_199_Validate_Lbdn_Failback_For_UNTIL_MANUAL_ENABLING_After_Specified_Time_Expires(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING After Specified_Time_Expires")
		log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                sleep(40)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "WHITE"' in Lbdn_data) and ('"description": "Requires Manual enabling"' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 199 Execution Completed")

        @pytest.mark.run(order=200)
        def test_200_Enable_Lbdn_Failback_For_UNTIL_MANUAL_ENABLING_After_Specified_Time_Expires(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING After Specified_Time_Expires")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                data={"enable_on":[config.grid_member_fqdn,config.grid_member_fqdn,config.grid_member1_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 200 Execution Completed")

        @pytest.mark.run(order=201)
        def test_201_Perform_Lbdn_Failback_with_UNTIL_DNS_RESTART_With_Disable_After(self):
                logging.info("Perform_Lbdn_Failback_with_UNTIL_DNS_RESTART With_Disable_After")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":True,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"UNTIL_DNS_RESTART","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 201 Execution Completed")

        @pytest.mark.run(order=202)
        def test_202_Validate_Lbdn_Failback_Status_of_UNTIL_DNS_RESTART(self):
                logging.info("Validate_Lbdn_Failback_Status of UNTIL_DNS_RESTART")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*name (Lbdn) action disable after 40 seconds.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*name (Lbdn) action disable after 40 seconds.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*name (Lbdn) action disable after 40 seconds.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 202 Execution Completed")

        @pytest.mark.run(order=203)
        def test_203_Validate_Lbdn_Failback_For_UNTIL_DNS_RESTART_After_Specified_Time_Expires(self):
                logging.info("Validate_Lbdn_Failback UNTIL_DNS_RESTART After Specified_Time_Expires")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                sleep(30)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "DARKGRAY"' in Lbdn_data) and ('"description": "Temporarily Disabled"' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 203 Execution Completed")

        @pytest.mark.run(order=204)
        def test_204_Enable_Lbdn_Failback_For_UNTIL_DNS_RESTART_After_Specified_Time_Expires(self):
                logging.info("Validate_Lbdn_Failback UNTIL_DNS_RESTART After Specified_Time_Expires")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                data={"enable_on":[config.grid_member_fqdn,config.grid_member_fqdn,config.grid_member1_fqdn],"dtc_object":str(reference)}
                restart_services()
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 204 Execution Completed")

        @pytest.mark.run(order=205)
        def test_205_Perform_Lbdn_Failback_FOR_SPECIFIED_TIME_With_Disable_After(self):
                logging.info("Perform_Lbdn_Failback FOR_SPECIFIED_TIME With_Disable_After")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":True,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object":str(reference),"specific_time_disable":30}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 205 Execution Completed")

        @pytest.mark.run(order=206)
        def test_206_Validate_Lbdn_Failback_Status_of_FOR_SPECIFIED_TIME(self):
                logging.info("Validate_Lbdn_Failback_Status of FOR_SPECIFIED_TIME")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*name (Lbdn) action disable after 40 seconds.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*name (Lbdn) action disable after 40 seconds.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*name (Lbdn) action disable after 40 seconds.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 206 Execution Completed")

        @pytest.mark.run(order=207)
        def test_207_Validate_Lbdn_Failback_FOR_SPECIFIED_TIME_After_Specified_Time_Expires(self):
                logging.info("Validate_Lbdn_Failback FOR_SPECIFIED_TIME After Specified_Time_Expires")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                sleep(30)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "DARKGRAY"' in Lbdn_data) and ('"description": "Temporarily Disabled"' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 207 Execution Completed")

        @pytest.mark.run(order=208)
        def test_208_Enable_Lbdn_Failback_FOR_SPECIFIED_TIME_After_Specified_Time_Expires(self):
                logging.info("Validate_Lbdn_Failback FOR_SPECIFIED_TIME After Specified_Time_Expires")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                sleep(30)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_member1_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.active_ip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.passive_ip)
                print("Test Case 208 Execution Completed") 
						
#Combinations       
        @pytest.mark.run(order=209)
        def test_209_Perform_server2_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_server2_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server2")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 209 Execution Completed")

        @pytest.mark.run(order=210)
        def test_210_Validate_server2_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_server2_Failback UNTIL_MANUAL_ENABLING")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 210 Execution Completed")
        @pytest.mark.run(order=211)
        def test_211_Perform_Pool1_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_Pool1_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 211 Execution Completed")

        pytest.mark.run(order=212)
        def test_212_Validate_Pool1_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Pool1_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "WHITE"' in Pool_data) and ('"description": "Requires Manual enabling"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 212 Execution Completed")
                
        @pytest.mark.run(order=213)
        def test_213_Enable_server2_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_server2_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference("server","Server2")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 213 Execution Completed")
                
        @pytest.mark.run(order=214)
        def test_214_Enable_Pool1_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Pool1_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference("pool","Pool1")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(30)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 214 Execution Completed")

        @pytest.mark.run(order=215)
        def test_215_Validate_Server2_Health_status(self):
                logging.info("Validate_Server2_Health_status")
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data)):
                    assert True
                else:
                    assert False
                print("Test Case 215 Execution Completed")
               
        @pytest.mark.run(order=216)
        def test_216_Perform_server2_Failback_with_UNTIL_DNS_RESTART(self):
                logging.info("Perform_server2_Failback_with UNTIL_DNS_RESTART")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server2")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_DNS_RESTART","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 216 Execution Completed")

        @pytest.mark.run(order=217)
        def test_217_Validate_server2_Failback_For_UNTIL_DNS_RESTART(self):
                logging.info("Validate_server2_Failback UNTIL_DNS_RESTART")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "DARKGRAY"' in Server_data) and ('"description": "Temporarily Disabled"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 217 Execution Completed")
                
        @pytest.mark.run(order=218)
        def test_218_Perform_Pool1_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_Pool1_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 218 Execution Completed")

        pytest.mark.run(order=219)
        def test_219_Validate_Pool1_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Pool1_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                sleep(40)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "WHITE"' in Pool_data) and ('"description": "Requires Manual enabling"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 219 Execution Completed")
                
        @pytest.mark.run(order=220)
        def test_220_Enable_server2_Failback_For_UNTIL_DNS_RESTART(self):
                logging.info("Validate_server2_Failback UNTIL_DNS_RESTART")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference("server","Server2")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                restart_services()
                sleep(30)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 220 Execution Completed")
                
        @pytest.mark.run(order=221)
        def test_221_Enable_Pool1_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Pool1_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference("pool","Pool1")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(30)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 221 Execution Completed")

        @pytest.mark.run(order=222)
        def test_222_Validate_Server2_Health_status(self):
                logging.info("Validate_Server2_Health_status")
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data)):
                    assert True
                else:
                    assert False
                print("Test Case 222 Execution Completed")
                
        @pytest.mark.run(order=223)
        def test_223_Perform_server2_Failback_with_FOR_SPECIFIED_TIME(self):
                logging.info("Perform_server2_Failback_with FOR_SPECIFIED_TIME")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server2")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 223 Execution Completed")

        @pytest.mark.run(order=224)
        def test_224_Validate_server2_Failback_For_FOR_SPECIFIED_TIME(self):
                logging.info("Validate_server2_Failback FOR_SPECIFIED_TIME")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "DARKGRAY"' in Server_data) and ('"description": "Temporarily Disabled"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 224 Execution Completed")
                
        @pytest.mark.run(order=225)
        def test_225_Perform_Pool1_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_Pool1_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 225 Execution Completed")

        pytest.mark.run(order=226)
        def test_226_Validate_Pool1_Failback_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Pool1_Failback UNTIL_MANUAL_ENABLING")
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "WHITE"' in Pool_data) and ('"description": "Requires Manual enabling"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 226 Execution Completed")
                
        @pytest.mark.run(order=227)
        def test_227_Enable_server2_Failback_For_FOR_SPECIFIED_TIME(self):
                logging.info("Validate_server2_Failback FOR_SPECIFIED_TIME")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference("server","Server2")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                sleep(40)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "DARKGRAY"' in Server_data) and ('"description": "Temporarily Disabled"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 227 Execution Completed")
                
        @pytest.mark.run(order=228)
        def test_228_Enable_Pool1_Failback_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Pool1_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference("pool","Pool1")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(30)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 228 Execution Completed")

        @pytest.mark.run(order=229)
        def test_229_Validate_Server2_Health_status(self):
                logging.info("Validate_Server2_Health_status")
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data)):
                    assert True
                else:
                    assert False
                print("Test Case 229 Execution Completed")
               
        @pytest.mark.run(order=230)
        def test_230_Perform_server2_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_server2_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server2")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 230 Execution Completed")

        @pytest.mark.run(order=231)
        def test_231_Validate_server2_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_server2_Failback UNTIL_MANUAL_ENABLING")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 231 Execution Completed")
        @pytest.mark.run(order=232)
        def test_232_Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 232 Execution Completed")

        pytest.mark.run(order=233)
        def test_233_Validate_Lbdn_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING")
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "WHITE"' in Lbdn_data) and ('"description": "Requires Manual enabling"' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 233 Execution Completed")
                
        @pytest.mark.run(order=234)
        def test_234_Enable_server2_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_server2_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference("server","Server2")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 234 Execution Completed")
                 
        @pytest.mark.run(order=235)
        def test_235_Enable_Lbdn_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(30)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 235 Execution Completed")
	
        @pytest.mark.run(order=236)
        def test_236_Validate_Server2_Health_status(self):
                logging.info("Validate_Server2_Health_status")
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data)):
                    assert True
                else:
                    assert False
                print("Test Case 236 Execution Completed")
                 
        @pytest.mark.run(order=237)
        def test_237_Perform_server2_Failback_with_UNTIL_DNS_RESTART(self):
                logging.info("Perform_server2_Failback_with UNTIL_DNS_RESTART")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server2")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_DNS_RESTART","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 237 Execution Completed")

        @pytest.mark.run(order=238)
        def test_238_Validate_server2_Failback_For_UNTIL_DNS_RESTART(self):
                logging.info("Validate_server2_Failback UNTIL_DNS_RESTART")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "DARKGRAY"' in Server_data) and ('"description": "Temporarily Disabled"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 238 Execution Completed")
                
        @pytest.mark.run(order=239)
        def test_239_Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 239 Execution Completed")

        pytest.mark.run(order=240)
        def test_240_Validate_Lbdn_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING")
                sleep(40)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "WHITE"' in Lbdn_data) and ('"description": "Requires Manual enabling"' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 240 Execution Completed")
                
        @pytest.mark.run(order=241)
        def test_241_Enable_server2_Failback_For_UNTIL_DNS_RESTART(self):
                logging.info("Validate_server2_Failback UNTIL_DNS_RESTART")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference("server","Server2")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                restart_services()
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 241 Execution Completed")
                
        @pytest.mark.run(order=242)
        def test_242_Enable_Lbdn_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 242 Execution Completed")

        @pytest.mark.run(order=243)
        def test_243_Validate_Server2_Health_status(self):
                logging.info("Validate_Server2_Health_status")
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data)):
                    assert True
                else:
                    assert False
                print("Test Case 243 Execution Completed")
                
        @pytest.mark.run(order=244)
        def test_244_Perform_server2_Failback_with_FOR_SPECIFIED_TIME(self):
                logging.info("Perform_server2_Failback_with FOR_SPECIFIED_TIME")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server2")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 244 Execution Completed")

        @pytest.mark.run(order=245)
        def test_245_Validate_server2_Failback_For_FOR_SPECIFIED_TIME(self):
                logging.info("Validate_server2_Failback FOR_SPECIFIED_TIME")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "DARKGRAY"' in Server_data) and ('"description": "Temporarily Disabled"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 245 Execution Completed")
                
        @pytest.mark.run(order=246)
        def test_246_Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 246 Execution Completed")

        pytest.mark.run(order=247)
        def test_247_Validate_Lbdn_Failback_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "WHITE"' in Lbdn_data) and ('"description": "Requires Manual enabling"' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 247 Execution Completed")
                
        @pytest.mark.run(order=248)
        def test_248_Enable_server2_Failback_For_FOR_SPECIFIED_TIME(self):
                logging.info("Validate_server2_Failback FOR_SPECIFIED_TIME")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference("server","Server2")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                sleep(40)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "DARKGRAY"' in Server_data) and ('"description": "Temporarily Disabled"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 248 Execution Completed")
                
        @pytest.mark.run(order=249)
        def test_249_Enable_Lbdn_Failback_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(30)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 249 Execution Completed")

        @pytest.mark.run(order=250)
        def test_250_Validate_Server2_Health_status(self):
                logging.info("Validate_Server2_Health_status")
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data)):
                    assert True
                else:
                    assert False
                print("Test Case 250 Execution Completed")

        @pytest.mark.run(order=251)
        def test_251_Perform_Pool2_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_Pool2_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool2")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(30)
                print("Test Case 251 Execution Completed")

        @pytest.mark.run(order=252)
        def test_252_Validate_Pool2_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Pool2_Failback UNTIL_MANUAL_ENABLING")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool2")
                print(Pool_data)
                if (('"availability": "WHITE"' in Pool_data) and ('"description": "Requires Manual enabling"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 252 Execution Completed")
        @pytest.mark.run(order=253)
        def test_253_Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 253 Execution Completed")

        pytest.mark.run(order=254)
        def test_254_Validate_Lbdn_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING")
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "WHITE"' in Lbdn_data) and ('"description": "Requires Manual enabling"' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 254 Execution Completed")
                
        @pytest.mark.run(order=255)
        def test_255_Enable_Pool2_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Pool2_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference("pool","Pool2")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool2 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool2 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool2 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool2")
                print(Pool_data)
                if (('"availability": "WHITE"' in Pool_data) and ('"description": "Requires Manual enabling"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 255 Execution Completed")
                
        @pytest.mark.run(order=256)
        def test_256_Enable_Lbdn_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(30)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 256 Execution Completed")

        @pytest.mark.run(order=257)
        def test_257_Validate_Pool2_Health_status(self):
                logging.info("Validate_Pool2_Health_status")
                Validate_Pool_Fail_back_Status("Pool2")
                print(Pool_data)
                if (('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data)):
                    assert True
                else:
                    assert False
                print("Test Case 257 Execution Completed")
                
        @pytest.mark.run(order=258)
        def test_258_Perform_Pool2_Failback_with_UNTIL_DNS_RESTART(self):
                logging.info("Perform_Pool2_Failback_with UNTIL_DNS_RESTART")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool2")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_DNS_RESTART","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 258 Execution Completed")

        @pytest.mark.run(order=259)
        def test_259_Validate_Pool2_Failback_For_UNTIL_DNS_RESTART(self):
                logging.info("Validate_Pool2_Failback UNTIL_DNS_RESTART")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool2")
                print(Pool_data)
                if (('"availability": "DARKGRAY"' in Pool_data) and ('"description": "Temporarily Disabled"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 259 Execution Completed")
                
        @pytest.mark.run(order=260)
        def test_260_Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 260 Execution Completed")

        pytest.mark.run(order=261)
        def test_261_Validate_Lbdn_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING")
                sleep(40)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "WHITE"' in Lbdn_data) and ('"description": "Requires Manual enabling"' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 261 Execution Completed")
                
        @pytest.mark.run(order=262)
        def test_262_Enable_Pool2_Failback_For_UNTIL_DNS_RESTART(self):
                logging.info("Validate_Pool2_Failback UNTIL_DNS_RESTART")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference("pool","Pool2")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                restart_services()
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool2 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool2 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool2 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool2")
                print(Pool_data)
                if (('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 262 Execution Completed")
                
        @pytest.mark.run(order=263)
        def test_263_Enable_Lbdn_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 263 Execution Completed")

        @pytest.mark.run(order=264)
        def test_264_Validate_Pool2_Health_status(self):
                logging.info("Validate_Pool2_Health_status")
                Validate_Pool_Fail_back_Status("Pool2")
                print(Pool_data)
                if (('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data)):
                    assert True
                else:
                    assert False
                print("Test Case 264 Execution Completed")
                
        @pytest.mark.run(order=265)
        def test_265_Perform_Pool2_Failback_with_FOR_SPECIFIED_TIME(self):
                logging.info("Perform_Pool2_Failback_with FOR_SPECIFIED_TIME")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool2")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 265 Execution Completed")

        @pytest.mark.run(order=266)
        def test_266_Validate_Pool2_Failback_For_FOR_SPECIFIED_TIME(self):
                logging.info("Validate_Pool2_Failback FOR_SPECIFIED_TIME")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool2")
                print(Pool_data)
                if (('"availability": "DARKGRAY"' in Pool_data) and ('"description": "Temporarily Disabled"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 266 Execution Completed")
                
        @pytest.mark.run(order=267)
        def test_267_Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 267 Execution Completed")

        pytest.mark.run(order=268)
        def test_268_Validate_Lbdn_Failback_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "WHITE"' in Lbdn_data) and ('"description": "Requires Manual enabling"' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 268 Execution Completed")
                
        @pytest.mark.run(order=269)
        def test_269_Enable_Pool2_Failback_For_FOR_SPECIFIED_TIME(self):
                logging.info("Validate_Pool2_Failback FOR_SPECIFIED_TIME")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference("pool","Pool2")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                sleep(40)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool2 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool2 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool2 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool2")
                print(Pool_data)
                if (('"availability": "DARKGRAY"' in Pool_data) and ('"description": "Temporarily Disabled"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 269 Execution Completed")
                
        @pytest.mark.run(order=270)
        def test_270_Enable_Lbdn_Failback_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(30)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 270 Execution Completed")

        @pytest.mark.run(order=271)
        def test_271_Validate_Pool2_Health_status(self):
                logging.info("Validate_Pool2_Health_status")
                Validate_Pool_Fail_back_Status("Pool2")
                print(Pool_data)
                if (('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data)):
                    assert True
                else:
                    assert False
                print("Test Case 271 Execution Completed")

        @pytest.mark.run(order=272)
        def test_272_Perform_server2_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_server2_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server2")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 272 Execution Completed")

        @pytest.mark.run(order=273)
        def test_273_Validate_server2_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_server2_Failback UNTIL_MANUAL_ENABLING")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 273 Execution Completed")
        
        @pytest.mark.run(order=274)
        def test_274_Perform_Pool1_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_Pool1_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 274 Execution Completed")

        pytest.mark.run(order=275)
        def test_275_Validate_Pool1_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Pool1_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "WHITE"' in Pool_data) and ('"description": "Requires Manual enabling"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 275 Execution Completed")
                
        @pytest.mark.run(order=276)
        def test_276_Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 276 Execution Completed")

        pytest.mark.run(order=277)
        def test_277_Validate_Lbdn_Failback_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "WHITE"' in Lbdn_data) and ('"description": "Requires Manual enabling"' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 277 Execution Completed")
                
        @pytest.mark.run(order=278)
        def test_278_Enable_server2_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_server2_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference("server","Server2")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 278 Execution Completed")
                
        @pytest.mark.run(order=279)
        def test_279_Enable_Pool1_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Pool1_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference("pool","Pool1")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and ('"availability": "WHITE"' in Pool_data) and ('"description": "Requires Manual enabling"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 279 Execution Completed")
                
        
        @pytest.mark.run(order=280)
        def test_280_Enable_Lbdn_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(30)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and ('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data) and ('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 280 Execution Completed")
		
	@pytest.mark.run(order=281)
        def test_281_Perform_server2_Failback_with_UNTIL_DNS_RESTART_on_Member1(self):
                logging.info("Perform_server2_Failback_with_UNTIL_DNS_RESTART on_Member1")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server2")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member1_fqdn],"disable_timeframe":"UNTIL_DNS_RESTART","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 281 Execution Completed")
				
	@pytest.mark.run(order=282)
        def test_282_Validate_server2_Failback_For_UNTIL_DNS_RESTART_on_Member1(self):
                logging.info("Validate_server2_Failback UNTIL_DNS_RESTART on_Member1")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                sleep(40)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "DARKGRAY"' in Server_data) and ('"description": "Temporarily Disabled"' in Server_data) and (int(check_master)==0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 282 Execution Completed")
				
	@pytest.mark.run(order=283)
        def test_283_Perform_server2_Failback_with_UNTIL_MANUAL_ENABLING_on_Member2(self):
                logging.info("Perform_server2_Failback_with_UNTIL_MANUAL_ENABLING on_Member2")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server2")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 283 Execution Completed")
				
	@pytest.mark.run(order=284)
        def test_284_Validate_server2_Failback_For_UNTIL_MANUAL_ENABLING_on_Member2(self):
                logging.info("Validate_server2_Failback UNTIL_MANUAL_ENABLING on_Member2")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                sleep(40)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)==0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 284 Execution Completed")
				
	@pytest.mark.run(order=285)
        def test_285_Perform_server2_Failback_FOR_SPECIFIED_TIME_on_Master(self):
                logging.info("Perform_server2_Failback_FOR_SPECIFIED_TIME on_Master")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server2")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object":str(reference),"specific_time_disable":50}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 285 Execution Completed")
				
	@pytest.mark.run(order=286)
        def test_286_Validate_server2_Failback_FOR_SPECIFIED_TIME(self):
                logging.info("Validate_server2_Failback FOR_SPECIFIED_TIME")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                sleep(40)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 286 Execution Completed")
	
	@pytest.mark.run(order=287)
        def test_287_Perform_Pool1_Failback_with_UNTIL_DNS_RESTART_on_Member1(self):
                logging.info("Perform_Pool1_Failback_with_UNTIL_DNS_RESTART on_Member1")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member1_fqdn],"disable_timeframe":"UNTIL_DNS_RESTART","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 287 Execution Completed")
				
	@pytest.mark.run(order=288)
        def test_288_Validate_Pool1_Failback_For_UNTIL_DNS_RESTART_on_Member1(self):
                logging.info("Validate_Pool1_Failback UNTIL_DNS_RESTART on_Member1")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                sleep(40)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "DARKGRAY"' in Pool_data) and ('"description": "Temporarily Disabled"' in Pool_data) and (int(check_master)==0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 288 Execution Completed")
				
	@pytest.mark.run(order=289)
        def test_289_Perform_Pool1_Failback_with_UNTIL_MANUAL_ENABLING_on_Member2(self):
                logging.info("Perform_Pool1_Failback_with_UNTIL_MANUAL_ENABLING on_Member2")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 289 Execution Completed")
				
	@pytest.mark.run(order=290)
        def test_290_Validate_Pool1_Failback_For_UNTIL_MANUAL_ENABLING_on_Member2(self):
                logging.info("Validate_Pool1_Failback UNTIL_MANUAL_ENABLING on_Member2")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                sleep(40)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "WHITE"' in Pool_data) and ('"description": "Requires Manual enabling"' in Pool_data) and (int(check_master)==0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 290 Execution Completed")
				
	@pytest.mark.run(order=291)
        def test_291_Perform_Pool1_Failback_FOR_SPECIFIED_TIME_on_Master(self):
                logging.info("Perform_Pool1_Failback_FOR_SPECIFIED_TIME on_Master")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object":str(reference),"specific_time_disable":50}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 291 Execution Completed")
				
	@pytest.mark.run(order=292)
        def test_292_Validate_Pool1_Failback_FOR_SPECIFIED_TIME(self):
                logging.info("Validate_Pool1_Failback FOR_SPECIFIED_TIME")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                sleep(40)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "WHITE"' in Pool_data) and ('"description": "Requires Manual enabling"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 292 Execution Completed")
	
	@pytest.mark.run(order=293)
        def test_293_Perform_Lbdn_Failback_with_UNTIL_DNS_RESTART_on_Member1(self):
                logging.info("Perform_Lbdn_Failback_with_UNTIL_DNS_RESTART on_Member1")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member1_fqdn],"disable_timeframe":"UNTIL_DNS_RESTART","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 293 Execution Completed")
				
	@pytest.mark.run(order=294)
        def test_294_Validate_Lbdn_Failback_For_UNTIL_DNS_RESTART_on_Member1(self):
                logging.info("Validate_Lbdn_Failback UNTIL_DNS_RESTART on_Member1")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                sleep(40)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "DARKGRAY"' in Lbdn_data) and ('"description": "Temporarily Disabled"' in Lbdn_data) and (int(check_master)==0) and (int(check_member_1)!=0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 294 Execution Completed")
				
	@pytest.mark.run(order=295)
        def test_295_Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING_on_Member2(self):
                logging.info("Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING on_Member2")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 295 Execution Completed")
				
	@pytest.mark.run(order=296)
        def test_296_Validate_Lbdn_Failback_For_UNTIL_MANUAL_ENABLING_on_Member2(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING on_Member2")
                sleep(40)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "WHITE"' in Lbdn_data) and ('"description": "Requires Manual enabling"' in Lbdn_data) and (int(check_master)==0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 296 Execution Completed")
				
	@pytest.mark.run(order=297)
        def test_297_Perform_Lbdn_Failback_FOR_SPECIFIED_TIME_on_Master(self):
                logging.info("Perform_Lbdn_Failback_FOR_SPECIFIED_TIME on_Master")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object":str(reference),"specific_time_disable":50}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 297 Execution Completed")
				
	@pytest.mark.run(order=298)
        def test_298_Validate_Lbdn_Failback_FOR_SPECIFIED_TIME(self):
                logging.info("Validate_Lbdn_Failback FOR_SPECIFIED_TIME")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                sleep(40)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "WHITE"' in Lbdn_data) and ('"description": "Requires Manual enabling"' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 298 Execution Completed")

	@pytest.mark.run(order=299)
        def test_299_Enable_server2_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_server2_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server2")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)==0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 299 Execution Completed")
				
	@pytest.mark.run(order=300)
        def test_300_Enable_Pool1_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Pool1_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and ('"availability": "WHITE"' in Pool_data) and ('"description": "Requires Manual enabling"' in Pool_data) and (int(check_master)==0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 300 Execution Completed")
				
	@pytest.mark.run(order=301)
        def test_301_Enable_Lbdn_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(30)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and ('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data) and ('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)==0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
		validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_member1_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.active_ip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.passive_ip)
                print("Test Case 301 Execution Completed")
					
#Disable_Health_Monitoring
	@pytest.mark.run(order=302)
        def test_302_Enabling_debug_healthd_To_Capture_Health_Monitoring_Logs_in_Master(self):
                logging.info("Enabling debug_healthd to Health_Monitoring_Logs Logs")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                sleep(10)
                child.expect('#')
		child.sendline('touch /infoblox/var/debug')
		child.expect('#')
		child.sendline('touch /infoblox/var/debug_nice')
		child.expect('#')
                child.sendline('touch /infoblox/var/debug_healthd')
                child.expect('#')
                child.sendline('/infoblox/rc restart')
                sleep(200)
                child.expect('#')
                child.close()
                print("Test Case 302 Execution Completed")
			
	@pytest.mark.run(order=303)
        def test_303_Enabling_debug_healthd_To_Capture_Health_Monitoring_Logs_In_Member2(self):
                logging.info("Enabling debug_healthd to Capture Health_Monitoring_Logs ")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                sleep(10)
                child.expect('#')
		child.sendline('touch /infoblox/var/debug')
                child.expect('#')
                child.sendline('touch /infoblox/var/debug_nice')
                child.expect('#')
                child.sendline('touch /infoblox/var/debug_healthd')
                child.expect('#')
                child.sendline('/infoblox/rc restart')
                sleep(200)
                child.expect('#')
                child.close()
                print("Test Case 303 Execution Completed")
		
	@pytest.mark.run(order=304)
        def test_304_Perform_server1_Failback_with_UNTIL_MANUAL_ENABLING_disable_health_monitoring_False(self):
                logging.info("Perform_server1_Failback_with_UNTIL_MANUAL_ENABLING disable_health_monitoring_False")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server1")
                data={"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 304 Execution Completed")
				
	@pytest.mark.run(order=305)
        def test_305_Validate_Server1_Failback_Status_of_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Server1_Failback_Status of UNTIL_MANUAL_ENABLING")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*stop_health_monitoring=FALSE.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*stop_health_monitoring=FALSE.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*stop_health_monitoring=FALSE.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server1")
		child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Master=child.before
                sleep(2)
                child.close()
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member1=child.before
                sleep(2)
                child.close()
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member2=child.before
                sleep(2)
                child.close()
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and ("'health' : 'WHITE'" in Health_Master) and ("'health' : 'WHITE'" not in Health_Member1) and ("'health' : 'WHITE'" in Health_Member2) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 305 Execution Completed")	

	@pytest.mark.run(order=306)
        def test_306_Check_health_status_txt_file_for_timestamp(self):
                try:
                        client = paramiko.SSHClient()
                        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
                        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
                        client.connect(config.grid_vip, username='root', pkey = mykey)
                        data ='cat /infoblox/var/idns_conf/health_status.txt'
                        stdin, stdout, stderr = client.exec_command(data)
                        file_output = stdout.read()
                        print(file_output)
                        file_output = ast.literal_eval(file_output)
                        for i in file_output['server_monitor']:
                                if i['health'] == 'WHITE':
                                        T1_Master=i['timestamp']
                                        continue
                except paramiko.AuthenticationException:
                        print("Authentication failed, please verify your credentials")
                except paramiko.SSHException as sshException:
                        print("Unable to establish SSH connection: %s" %sshException)
                except paramiko.BadHostKeyException as badHostKeyException:
                        print("Unable to verify server's host key: %s" %badHostKeyException)
                finally:
                        client.close()
                        logging.info("Test Case 306 Execution Completed")
                print(T1_Master)
                sleep(100)
                try:
                        client = paramiko.SSHClient()
                        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
                        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
                        client.connect(config.grid_vip, username='root', pkey = mykey)
                        data ='cat /infoblox/var/idns_conf/health_status.txt'
                        stdin, stdout, stderr = client.exec_command(data)
                        file_output = stdout.read()
                        print(file_output)
                        file_output = ast.literal_eval(file_output)
                        for i in file_output['server_monitor']:
                                if i['health'] == 'WHITE':
                                        T2_Master=i['timestamp']
                                        continue
                except paramiko.AuthenticationException:
                        print("Authentication failed, please verify your credentials")
                except paramiko.SSHException as sshException:
                        print("Unable to establish SSH connection: %s" %sshException)
                except paramiko.BadHostKeyException as badHostKeyException:
                        print("Unable to verify server's host key: %s" %badHostKeyException)
                finally:
                        client.close()
                        logging.info("Test Case 306 Execution Completed")
                print(T2_Master)
				
		try:
                        client = paramiko.SSHClient()
                        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
                        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
                        client.connect(config.grid_vip, username='root', pkey = mykey)
                        data ='cat /infoblox/var/idns_conf/health_status.txt'
                        stdin, stdout, stderr = client.exec_command(data)
                        file_output = stdout.read()
                        print(file_output)
                        file_output = ast.literal_eval(file_output)
                        for i in file_output['server_monitor']:
                                if i['health'] == 'WHITE':
                                        T1_Member=i['timestamp']
                                        continue
                except paramiko.AuthenticationException:
                        print("Authentication failed, please verify your credentials")
                except paramiko.SSHException as sshException:
                        print("Unable to establish SSH connection: %s" %sshException)
                except paramiko.BadHostKeyException as badHostKeyException:
                        print("Unable to verify server's host key: %s" %badHostKeyException)
                finally:
                        client.close()
                        logging.info("Test Case 306 Execution Completed")
                print(T1_Member)
                sleep(100)
                try:
                        client = paramiko.SSHClient()
                        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
                        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
                        client.connect(config.grid_vip, username='root', pkey = mykey)
                        data ='cat /infoblox/var/idns_conf/health_status.txt'
                        stdin, stdout, stderr = client.exec_command(data)
                        file_output = stdout.read()
                        print(file_output)
                        file_output = ast.literal_eval(file_output)
                        for i in file_output['server_monitor']:
                                if i['health'] == 'WHITE':
                                        T2_Member=i['timestamp']
                                        continue
                except paramiko.AuthenticationException:
                        print("Authentication failed, please verify your credentials")
                except paramiko.SSHException as sshException:
                        print("Unable to establish SSH connection: %s" %sshException)
                except paramiko.BadHostKeyException as badHostKeyException:
                        print("Unable to verify server's host key: %s" %badHostKeyException)
                finally:
                        client.close()
                        logging.info("Test Case 306 Execution Completed")
                print(T2_Member)
                if ((T1_Master!=T2_Master) and (T1_Member!=T2_Member)):
                        assert True
                else:
                        assert False

	@pytest.mark.run(order=307)
        def test_307_Perform_server1_Failback_Enable(self):
                logging.info("Perform_server1_Failback_Enable")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server1")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                print(enable_output)
                assert re.search(r'"failback_status": "SUCCESS"',enable_output)
                sleep(25)
                print("Test Case 307 Execution Completed")

        @pytest.mark.run(order=308)
        def test_308_Validate_Server1_Failback_Status(self):
                logging.info("Validate_Server1_Failback_Status")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server1")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 308 Execution Completed")
	
	@pytest.mark.run(order=309)
        def test_309_Perform_server1_Failback_with_UNTIL_MANUAL_ENABLING_disable_health_monitoring_False_True(self):
                logging.info("Perform_server1_Failback_with_UNTIL_MANUAL_ENABLING disable_health_monitoring_False_True")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 309 Execution Completed")

        @pytest.mark.run(order=310)
        def test_310_Validate_Server1_Failback_Status_of_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Server1_Failback_Status of UNTIL_MANUAL_ENABLING")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*stop_health_monitoring=TRUE.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*stop_health_monitoring=TRUE.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*stop_health_monitoring=TRUE.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server1")
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 310 Execution Completed")

        @pytest.mark.run(order=311)
        def test_311_Check_health_status_txt_file_for_timestamp(self):
                try:
                        client = paramiko.SSHClient()
                        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
                        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
                        client.connect(config.grid_vip, username='root', pkey = mykey)
                        data ='cat /infoblox/var/idns_conf/health_status.txt'
                        stdin, stdout, stderr = client.exec_command(data)
                        file_output = stdout.read()
                        print(file_output)
                        file_output = ast.literal_eval(file_output)
                        for i in file_output['server_monitor']:
                                if i['health'] == 'WHITE':
                                        T1_Master=i['timestamp']
                                        continue
                except paramiko.AuthenticationException:
                        print("Authentication failed, please verify your credentials")
                except paramiko.SSHException as sshException:
                        print("Unable to establish SSH connection: %s" %sshException)
                except paramiko.BadHostKeyException as badHostKeyException:
                        print("Unable to verify server's host key: %s" %badHostKeyException)
                finally:
                        client.close()
                print(T1_Master)
                sleep(100)
                try:
                        client = paramiko.SSHClient()
                        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
                        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
                        client.connect(config.grid_vip, username='root', pkey = mykey)
                        data ='cat /infoblox/var/idns_conf/health_status.txt'
                        stdin, stdout, stderr = client.exec_command(data)
                        file_output = stdout.read()
                        print(file_output)
                        file_output = ast.literal_eval(file_output)
                        for i in file_output['server_monitor']:
                                if i['health'] == 'WHITE':
                                        T2_Master=i['timestamp']
                                        continue
                except paramiko.AuthenticationException:
                        print("Authentication failed, please verify your credentials")
                except paramiko.SSHException as sshException:
                        print("Unable to establish SSH connection: %s" %sshException)
                except paramiko.BadHostKeyException as badHostKeyException:
                        print("Unable to verify server's host key: %s" %badHostKeyException)
                finally:
                        client.close()
                print(T2_Master)
				
		try:
                        client = paramiko.SSHClient()
                        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
                        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
                        client.connect(config.grid_vip, username='root', pkey = mykey)
                        data ='cat /infoblox/var/idns_conf/health_status.txt'
                        stdin, stdout, stderr = client.exec_command(data)
                        file_output = stdout.read()
                        print(file_output)
                        file_output = ast.literal_eval(file_output)
                        for i in file_output['server_monitor']:
                                if i['health'] == 'WHITE':
                                        T1_Member=i['timestamp']
                                        continue
                except paramiko.AuthenticationException:
                        print("Authentication failed, please verify your credentials")
                except paramiko.SSHException as sshException:
                        print("Unable to establish SSH connection: %s" %sshException)
                except paramiko.BadHostKeyException as badHostKeyException:
                        print("Unable to verify server's host key: %s" %badHostKeyException)
                finally:
                        client.close()
                print(T1_Member)
                sleep(100)
                try:
                        client = paramiko.SSHClient()
                        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
                        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
                        client.connect(config.grid_vip, username='root', pkey = mykey)
                        data ='cat /infoblox/var/idns_conf/health_status.txt'
                        stdin, stdout, stderr = client.exec_command(data)
                        file_output = stdout.read()
                        print(file_output)
                        file_output = ast.literal_eval(file_output)
                        for i in file_output['server_monitor']:
                                if i['health'] == 'WHITE':
                                        T2_Member=i['timestamp']
                                        continue
                except paramiko.AuthenticationException:
                        print("Authentication failed, please verify your credentials")
                except paramiko.SSHException as sshException:
                        print("Unable to establish SSH connection: %s" %sshException)
                except paramiko.BadHostKeyException as badHostKeyException:
                        print("Unable to verify server's host key: %s" %badHostKeyException)
                finally:
                        client.close()
                print(T2_Member)
                if ((T1_Master!=T2_Master) and (T1_Member!=T2_Member)):
                        assert True
                else:
                        assert False
		logging.info("Test Case 311 Execution Completed")		
	
        @pytest.mark.run(order=312)
        def test_312_Perform_server1_Failback_Enable(self):
                logging.info("Perform_server1_Failback_Enable")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server1")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                print(enable_output)
                assert re.search(r'"failback_status": "SUCCESS"',enable_output)
                sleep(25)
                print("Test Case 312 Execution Completed")

        @pytest.mark.run(order=313)
        def test_313_Validate_Server1_Failback_Status(self):
                logging.info("Validate_Server1_Failback_Status")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server1")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 313 Execution Completed")
	
	@pytest.mark.run(order=314)
        def test_314_Perform_Pool1_Failback_with_UNTIL_DNS_RESTART_disable_health_monitoring_False(self):
                logging.info("Perform_Pool1_Failback_with_UNTIL_DNS_RESTART disable_health_monitoring_False")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_DNS_RESTART","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 314 Execution Completed")

        @pytest.mark.run(order=315)
        def test_315_Validate_Pool1_Failback_Status_of_UNTIL_DNS_RESTART(self):
                logging.info("Validate_Pool1_Failback_Status of UNTIL_DNS_RESTART")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*stop_health_monitoring=FALSE.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*stop_health_monitoring=FALSE.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*stop_health_monitoring=FALSE.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Master=child.before
                sleep(2)
                child.close()
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member1=child.before
                sleep(2)
                child.close()
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member2=child.before
                sleep(2)
                child.close()
                if (('"availability": "DARKGRAY"' in Pool_data) and ('"description": "Temporarily Disabled"' in Pool_data) and ("'health' : 'DARKGRAY'" in Health_Master) and ("'health' : 'DARKGRAY'" not in Health_Member1) and ("'health' : 'DARKGRAY'" in Health_Member2) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 315 Execution Completed")

        @pytest.mark.run(order=316)
        def test_316_Perform_Pool1_Failback_Enable(self):
                logging.info("Perform_Pool1_Failback_Enable")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                print(enable_output)
                assert re.search(r'"failback_status": "SUCCESS"',enable_output)
                sleep(25)
                print("Test Case 316 Execution Completed")

        @pytest.mark.run(order=317)
        def test_317_Validate_Pool1_Failback_Status(self):
                logging.info("Validate_Pool1_Failback_Status")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 317 Execution Completed")

	@pytest.mark.run(order=318)
        def test_318_Perform_Pool1_Failback_with_UNTIL_DNS_RESTART_disable_health_monitoring_True(self):
                logging.info("Perform_Pool1_Failback_with_UNTIL_DNS_RESTART disable_health_monitoring True")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_DNS_RESTART","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 318 Execution Completed")

        @pytest.mark.run(order=319)
        def test_319_Validate_Pool1_Failback_Status_of_UNTIL_DNS_RESTART(self):
                logging.info("Validate_Pool1_Failback_Status of UNTIL_DNS_RESTART")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*stop_health_monitoring=TRUE.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*stop_health_monitoring=TRUE.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*stop_health_monitoring=TRUE.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                if (('"availability": "DARKGRAY"' in Pool_data) and ('"description": "Temporarily Disabled"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 319 Execution Completed")		

        @pytest.mark.run(order=320)
        def test_320_Perform_Pool1_Failback_Enable(self):
                logging.info("Perform_Pool1_Failback_Enable")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                print(enable_output)
                assert re.search(r'"failback_status": "SUCCESS"',enable_output)
                sleep(25)
                print("Test Case 320 Execution Completed")

        @pytest.mark.run(order=321)
        def test_321_Validate_Pool1_Failback_Status(self):
                logging.info("Validate_Pool1_Failback_Status")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 321 Execution Completed")
	
	@pytest.mark.run(order=322)
        def test_322_Perform_Lbdn_Failback_with_FOR_SPECIFIED_TIME_disable_health_monitoring_False(self):
                logging.info("Perform_Lbdn_Failback_with_FOR_SPECIFIED_TIME disable_health_monitoring_False")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member2_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object":str(reference),"specific_time_disable":50}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 322 Execution Completed")

        @pytest.mark.run(order=323)
        def test_323_Validate_Lbdn_Failback_Status_of_FOR_SPECIFIED_TIME(self):
                logging.info("Validate_Lbdn_Failback_Status of FOR_SPECIFIED_TIME")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*stop_health_monitoring=FALSE.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*stop_health_monitoring=FALSE.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*stop_health_monitoring=FALSE.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
		if (('"availability": "DARKGRAY"' in Lbdn_data) and ('"description": "Temporarily Disabled"' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 323 Execution Completed")

        @pytest.mark.run(order=324)
        def test_324_Validate_Lbdn_Failback_Status(self):
                logging.info("Validate_Lbdn_Failback_Status")
		log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
		sleep(50)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 324 Execution Completed")
	@pytest.mark.run(order=325)
        def test_325_Perform_Lbdn_Failback_with_FOR_SPECIFIED_TIME_disable_health_monitoring_True(self):
                logging.info("Perform_Lbdn_Failback_with_FOR_SPECIFIED_TIME disable_health_monitoring_True")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member2_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object":str(reference),"specific_time_disable":50}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 325 Execution Completed")

        @pytest.mark.run(order=326)
        def test_326_Validate_Lbdn_Failback_Status_of_FOR_SPECIFIED_TIME(self):
                logging.info("Validate_Lbdn_Failback_Status of FOR_SPECIFIED_TIME")
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*stop_health_monitoring=TRUE.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*stop_health_monitoring=TRUE.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*stop_health_monitoring=TRUE.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                if (('"availability": "DARKGRAY"' in Lbdn_data) and ('"description": "Temporarily Disabled"' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 326 Execution Completed")		

        @pytest.mark.run(order=327)
        def test_327_Validate_Lbdn_Failback_Status(self):
                logging.info("Validate_Lbdn_Failback_Status")
		log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
		sleep(50)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
                log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
		validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_member1_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.active_ip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.passive_ip)
                print("Test Case 327 Execution Completed")
                	
#GMC Promotion
	@pytest.mark.run(order=328)
        def test_328_Perform_server2_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_server2_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server2")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 328 Execution Completed")

        @pytest.mark.run(order=329)
        def test_329_Validate_server2_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_server2_Failback UNTIL_MANUAL_ENABLING")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 329 Execution Completed")

        @pytest.mark.run(order=330)
        def test_330_Perform_Pool1_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_Pool1_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 330 Execution Completed")

        @pytest.mark.run(order=331)
        def test_331_Validate_Pool1_Failback_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Pool1_Failback UNTIL_MANUAL_ENABLING")
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "WHITE"' in Pool_data) and ('"description": "Requires Manual enabling"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 331 Execution Completed")

        @pytest.mark.run(order=332)
        def test_332_Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 332 Execution Completed")

        @pytest.mark.run(order=333)
        def test_333_Validate_Lbdn_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING")
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "WHITE"' in Lbdn_data) and ('"description": "Requires Manual enabling"' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 333 Execution Completed")

        @pytest.mark.run(order=334)
        def test_334_Enable_Master_Candidate_For_SA_member(self):
                logging.info("Enable Master_Candidate For SA-member")
                response =  ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                res = json.loads(response)
                ref1 = json.loads(response)[2]['_ref']
                print ref1
                data = {"master_candidate":True}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(400)
                print("Test Case 334 Execution Completed")

        @pytest.mark.run(order=335)
        def test_335_Validate_Enabled_Master_Candidate_For_SA_member(self):
                logging.info("Enabled Master_Candidate For SA-member")
                response =  ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                res = json.loads(response)
                ref1 = json.loads(response)[2]['_ref']
                print ref1
                response = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=master_candidate")
                print(response)
                if('"master_candidate": true' in response):
                        assert True
                else:
                        assert False
                print("Test Case 335 Execution Completed")
		
	@pytest.mark.run(order=336)
        def test_336_Validate_DTC_Objects_Health_status_After_Enabling_GMC(self):
                logging.info("Validate_DTC_Objects_Health_status_After_Enabling_GMC")
		Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "WHITE"' in Server_data) and ('"availability": "WHITE"' in Pool_data) and ('"availability": "WHITE"' in Lbdn_data)):
                    assert True
                else:
                    assert False
                print("Test Case 336 Execution Completed")
				
	@pytest.mark.run(order=337)
        def test_337_Promoting_SA_Member_as_Master(self):
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('set promote_master')
                child.expect(':')
                child.sendline('y')
                child.expect(':')
                child.sendline('10')
                child.expect(':')
                child.sendline('y')
                child.expect(':')
                child.sendline('y')
                time.sleep(300)
                child.expect('closed.')
                print("Test Case 337 Execution Completed")

        @pytest.mark.run(order=338)
        def test_338_Validate_SA_Member_as_Master(self):
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show network')
                child.expect('Infoblox >')
                response=child.before
                child.close()
                print(response)
                assert re.search(r'Master of Infoblox Grid',response)
		time.sleep(100)
                print("Test Case 338 Execution Completed")

	@pytest.mark.run(order=339)
        def test_339_Validate_Status_Of_DTC_Objects_After_GMC_Promotion(self):
                logging.info("Validate_Status_Of_DTC_Objects_After_GMC_Promotion")
                Validate_Server_Fail_back_Status_GMC("Server2")
                print(Server_data)
                Validate_Pool_Fail_back_Status_GMC("Pool1")
                print(Pool_data)
                Validate_Lbdn_Fail_back_Status_GMC("Lbdn")
                print(Lbdn_data)
                if (('"availability": "WHITE"' in Server_data) and ('"availability": "WHITE"' in Pool_data) and ('"availability": "WHITE"' in Lbdn_data)):
                    assert True
                else:
                    assert False
                print("Test Case 339 Execution Completed")
	
	@pytest.mark.run(order=340)
        def test_340_Enable_server2_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_server2_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference_GMC("server","Server2")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable_GMC(data)
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status_GMC("Server2")
                print(Server_data)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 340 Execution Completed")
		
	@pytest.mark.run(order=341)
        def test_341_Enable_Pool1_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Pool1_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference_GMC("pool","Pool1")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable_GMC(data)
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status_GMC("Pool1")
                print(Pool_data)
                Validate_Server_Fail_back_Status_GMC("Server2")
                print(Server_data)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and ('"availability": "WHITE"' in Pool_data) and ('"description": "Requires Manual enabling"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 341 Execution Completed")				
						
	@pytest.mark.run(order=342)
        def test_342_Enable_Lbdn_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		Getting_DTC_Object_Reference_GMC("lbdn","Lbdn")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable_GMC(data)
                sleep(30)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status_GMC("Lbdn")
                print(Lbdn_data)
                Validate_Pool_Fail_back_Status_GMC("Pool1")
                print(Pool_data)
                Validate_Server_Fail_back_Status_GMC("Server2")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and ('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data) and ('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 342 Execution Completed")
	
	@pytest.mark.run(order=343)
        def test_343_Perform_server2_Failback_with_UNTIL_DNS_RESTART(self):
                logging.info("Perform_server2_Failback_with UNTIL_DNS_RESTART")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference_GMC("server","Server2")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_DNS_RESTART","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable_GMC(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 343 Execution Completed")

        @pytest.mark.run(order=344)
        def test_344_Validate_server2_Failback_For_UNTIL_DNS_RESTART(self):
                logging.info("Validate_server2_Failback UNTIL_DNS_RESTART")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status_GMC("Server2")
                print(Server_data)
                if (('"availability": "DARKGRAY"' in Server_data) and ('"description": "Temporarily Disabled"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 344 Execution Completed")
				
	@pytest.mark.run(order=345)
        def test_345_Perform_Pool2_Failback_with_UNTIL_DNS_RESTART(self):
                logging.info("Perform_Pool2_Failback_with UNTIL_DNS_RESTART")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference_GMC("pool","Pool2")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_DNS_RESTART","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable_GMC(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 345 Execution Completed")

        @pytest.mark.run(order=346)
        def test_346_Validate_Pool2_Failback_For_UNTIL_DNS_RESTART(self):
                logging.info("Validate_Pool2_Failback UNTIL_DNS_RESTART")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status_GMC("Pool2")
                print(Pool_data)
                if (('"availability": "DARKGRAY"' in Pool_data) and ('"description": "Temporarily Disabled"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 346 Execution Completed")
				
	@pytest.mark.run(order=347)
        def test_347_Perform_Lbdn_Failback_with_UNTIL_DNS_RESTART(self):
                logging.info("Perform_Lbdn_Failback_with_UNTIL_DNS_RESTART")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference_GMC("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_DNS_RESTART","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable_GMC(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 347 Execution Completed")
		
	@pytest.mark.run(order=348)
        def test_348_Validate_Lbdn_Failback_For_UNTIL_DNS_RESTART(self):
                logging.info("Validate_Lbdn_Failback UNTIL_DNS_RESTART")
                sleep(30)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status_GMC("Lbdn")
                print(Lbdn_data)
                if (('"availability": "DARKGRAY"' in Lbdn_data) and ('"description": "Temporarily Disabled"' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 348 Execution Completed")

	@pytest.mark.run(order=349)
        def test_349_Enable_DTC_Objects_Failback_For_UNTIL_DNS_RESTART(self):
                logging.info("Validate_DTC_Objects_Failback UNTIL_DNS_RESTART")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
		grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_member2_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_member2_vip)
		sleep(30)
		print_and_log("Service restart Done")
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool2 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status_GMC("Lbdn")
                print(Lbdn_data)
                Validate_Pool_Fail_back_Status_GMC("Pool2")
                print(Pool_data)
                Validate_Server_Fail_back_Status_GMC("Server2")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and ('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data) and ('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 349 Execution Completed")
	
	@pytest.mark.run(order=350)
        def test_350_Perform_server2_Failback_with_FOR_SPECIFIED_TIME(self):
                logging.info("Perform_server2_Failback_with FOR_SPECIFIED_TIME")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference_GMC("server","Server2")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object":str(reference),"specific_time_disable":1200}
                print(data)
                DTC_Object_Fail_back_Manual_Disable_GMC(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 350 Execution Completed")

        @pytest.mark.run(order=351)
        def test_351_Validate_server2_Failback_For_FOR_SPECIFIED_TIME(self):
                logging.info("Validate_server2_Failback FOR_SPECIFIED_TIME")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status_GMC("Server2")
                print(Server_data)
                if (('"availability": "DARKGRAY"' in Server_data) and ('"description": "Temporarily Disabled"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 351 Execution Completed")
				
	@pytest.mark.run(order=352)
        def test_352_Perform_Pool1_Failback_with_FOR_SPECIFIED_TIME(self):
                logging.info("Perform_Pool1_Failback_with FOR_SPECIFIED_TIME")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference_GMC("pool","Pool1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object":str(reference),"specific_time_disable":1200}
                print(data)
                DTC_Object_Fail_back_Manual_Disable_GMC(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 352 Execution Completed")

        @pytest.mark.run(order=353)
        def test_353_Validate_Pool1_Failback_For_FOR_SPECIFIED_TIME(self):
                logging.info("Validate_Pool1_Failback FOR_SPECIFIED_TIME")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status_GMC("Pool1")
                print(Pool_data)
                if (('"availability": "DARKGRAY"' in Pool_data) and ('"description": "Temporarily Disabled"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 353 Execution Completed")

	@pytest.mark.run(order=354)
        def test_354_Perform_Lbdn_Failback_with_FOR_SPECIFIED_TIME(self):
                logging.info("Perform_Lbdn_Failback_with FOR_SPECIFIED_TIME")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference_GMC("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object":str(reference),"specific_time_disable":1200}
                print(data)
                DTC_Object_Fail_back_Manual_Disable_GMC(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 354 Execution Completed")

        @pytest.mark.run(order=355)
        def test_355_Validate_Lbdn_Failback_For_FOR_SPECIFIED_TIME(self):
                logging.info("Validate_Lbdn_Failback FOR_SPECIFIED_TIME")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status_GMC("Lbdn")
                print(Lbdn_data)
                if (('"availability": "DARKGRAY"' in Lbdn_data) and ('"description": "Temporarily Disabled"' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 355 Execution Completed")

	@pytest.mark.run(order=356)
        def test_356_Promoting_GMC_as_Master(self):
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('set promote_master')
                child.expect(':')
                child.sendline('y')
                child.expect(':')
                child.sendline('10')
                child.expect(':')
                child.sendline('y')
                child.expect(':')
                child.sendline('y')
                time.sleep(300)
                child.expect('closed.')
                print("Test Case 356 Execution Completed")
	
        @pytest.mark.run(order=357)
        def test_357_Validate_GMC_as_Master(self):
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show network')
                child.expect('Infoblox >')
                response=child.before
                child.close()
                print(response)
                assert re.search(r'Master of Infoblox Grid',response)
		time.sleep(100)
                print("Test Case 357 Execution Completed")
		
	@pytest.mark.run(order=358)
        def test_358_Validate_Disable_Status_Of_DTC_Objects(self):
                logging.info("Validate_Disable_Status_Of_DTC_Objects")
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "DARKGRAY"' in Server_data) and ('"availability": "DARKGRAY"' in Pool_data) and ('"availability": "DARKGRAY"' in Lbdn_data)):
                    assert True
                else:
                    assert False
		validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_member1_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.active_ip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.passive_ip)
                print("Test Case 358 Execution Completed")

	@pytest.mark.run(order=359)
        def test_359_Taking_DTC_Backup_Config_File(self):
                logging.info("Taking DTC Backup config file")
                data = {"type": "BACKUP_DTC"}
                response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=getgriddata",grid_vip=config.grid_vip)
                response = json.loads(response)
                global token_of_GM
                global token_of_URL
                token_of_GM = response['token']
                token_of_URL = response['url']
                print(token_of_GM)
                print(token_of_URL)
                print("Test Case 359 Execution Completed")

        @pytest.mark.run(order=360)
        def test_360_Restore_DTC_Config_File(self):
                log("start","/infoblox/var/infoblox.log", config.grid_vip)
                data = {"forced": False, "token": token_of_GM}
                response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=restoredtcconfig",grid_vip=config.grid_vip)
                sleep(30)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
		check_master=commands.getoutput(" grep -cw \".*DTC restore: done.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print("Restart DNS Services")
                restart_services()
                sleep(60)
		if (int(check_master)!=0):
		    assert True
                else:
                    assert False
                logging.info("Test Case 360 Execution Completed")
					
	@pytest.mark.run(order=361)
        def test_361_Validate_Disable_Status_Of_DTC_Objects_After_DTC_Restore(self):
                logging.info("Validate_Disable_Status_Of_DTC_Objects After_DTC_Restore")
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
		child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Master=child.before
                sleep(2)
                child.close()
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member1=child.before
                sleep(2)
                child.close()
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member2=child.before
                sleep(2)
                child.close()
                if (('"availability": "GREEN"' in Server_data) and ('"availability": "GREEN"' in Pool_data) and ('"availability": "GREEN"' in Lbdn_data) and ("'health' : 'DARKGRAY'" not in Health_Master) and ("'health' : 'DARKGRAY'" not in Health_Member1) and ("'health' : 'DARKGRAY'" not in Health_Member2)):
                    assert True
                else:
                    assert False
                print("Test Case 361 Execution Completed")

	@pytest.mark.run(order=362)
        def test_362_Perform_server2_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_server2_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server2")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 362 Execution Completed")

        @pytest.mark.run(order=363)
        def test_363_Validate_server2_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_server2_Failback UNTIL_MANUAL_ENABLING")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 363 Execution Completed")
				
	@pytest.mark.run(order=364)
        def test_364_Perform_Pool1_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_Pool1_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 364 Execution Completed")

        @pytest.mark.run(order=365)
        def test_365_Validate_Pool1_Failback_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Pool1_Failback UNTIL_MANUAL_ENABLING")
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "WHITE"' in Pool_data) and ('"description": "Requires Manual enabling"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 365 Execution Completed")
				
	@pytest.mark.run(order=366)
        def test_366_Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 366 Execution Completed")

        @pytest.mark.run(order=367)
        def test_367_Validate_Lbdn_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING")
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "WHITE"' in Lbdn_data) and ('"description": "Requires Manual enabling"' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 367 Execution Completed")
	
	@pytest.mark.run(order=368)
        def test_368_Validate_Disable_Status_Of_DTC_Objects_Before_Restore(self):
                logging.info("Validate_Disable_Status_Of_DTC_Objects Before Restore")
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Master=child.before
                sleep(2)
                child.close()
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member1=child.before
                sleep(2)
                child.close()
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member2=child.before
                sleep(2)
                child.close()
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and ('"availability": "WHITE"' in Pool_data) and ('"description": "Requires Manual enabling"' in Pool_data) and ('"availability": "WHITE"' in Lbdn_data) and ('"description": "Requires Manual enabling"' in Lbdn_data) and ("'health' : 'WHITE'" in Health_Master) and ("'health' : 'WHITE'" in Health_Member1) and ("'health' : 'WHITE'" in Health_Member2)):
                    assert True
                else:
                    assert False
                print("Test Case 368 Execution Completed")
						
	@pytest.mark.run(order=369)
        def test_369_Taking_Grid_Backup_File(self):
                logging.info("Taking Grid Backup file")
                data = {"type": "BACKUP"}
                response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=getgriddata",grid_vip=config.grid_vip)
                response = json.loads(response)
                token_of_GM = response['token']
                token_of_URL = response['url']
		curl_download='curl -k -u admin:infoblox -H  "content-type: application/force-download" '+token_of_URL+' -o "database.bak"'
		os.system(curl_download)
                print(token_of_GM)
                print(token_of_URL)
                print("Test Case 369 Execution Completed")

        @pytest.mark.run(order=370)
        def test_370_Restore_Grid_Backup_File(self):
		logging.info("Restore_Grid_Backup_File")
                log("start","/infoblox/var/infoblox.log", config.grid_vip)
		response = ib_NIOS.wapi_request('POST', object_type="fileop",params="?_function=uploadinit",grid_vip=config.grid_vip)
		response = json.loads(response)
		print(response)
                token_of_GM = response['token']
                token_of_URL = response['url']
		curl_upload='curl -k -u admin:infoblox -H "content-typemultipart-formdata" '+token_of_URL+' -F file=@database.bak'
		os.system(curl_upload)
		print(curl_upload) 
                data = {"mode": "FORCED", "token": token_of_GM}
                response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=restoredatabase",grid_vip=config.grid_vip)
                sleep(60)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
		check_master=commands.getoutput(" grep -cw \".*restore_node complete.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                if (int(check_master)!=0):
                    assert True
                else:
                    assert False

                sleep(60)
	        logging.info("Test Case 370 Execution Completed")
		
	@pytest.mark.run(order=371)
        def test_371_Validate_Disable_Status_Of_DTC_Objects_After_Restore_NIOS_85557(self):
                logging.info("Validate_Disable_Status_Of_DTC_Objects After Restore NIOS_85557")
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Master=child.before
                sleep(2)
                child.close()
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member1=child.before
                sleep(2)
                child.close()
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                child.expect('#')
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member2=child.before
                sleep(2)
                child.close()
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and ('"availability": "WHITE"' in Pool_data) and ('"description": "Requires Manual enabling"' in Pool_data) and ('"availability": "WHITE"'  in Lbdn_data) and ('"description": "Requires Manual enabling"' in Lbdn_data) and ("'health' : 'WHITE'" in Health_Master) and ("'health' : 'WHITE'" in Health_Member1) and ("'health' : 'WHITE'" in Health_Member2)):
                    assert True
                else:
                    assert False
                print("Test Case 371 Execution Completed")
	                	
	@pytest.mark.run(order=372)
        def test_372_Delete_the_DTC_LBDN(self):
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                response1 = ib_NIOS.wapi_request('DELETE', object_type=str(reference), grid_vip=config.grid_vip)
                print("Restart DNS Services")
		restart_services()
                sleep(30)
                print("Test Case 372 Execution Completed")
			
	@pytest.mark.run(order=373)
        def test_373_add_a_DTC_lbdn(self):
                logging.info("Create A DTC LBDN")
		Getting_DTC_Object_Reference("pool","Pool1")
		Pool1_ref=reference
		Getting_DTC_Object_Reference("pool","Pool2")
		Pool2_ref=reference				
                data = {"name":"Lbdn","lb_method":"ROUND_ROBIN","patterns": ["a1.dtc.com"], "pools": [{"pool":str(Pool1_ref),"ratio": 1},{"pool":str(Pool2_ref),"ratio": 1}], "auth_zones":["zone_auth/ZG5zLnpvbmUkLl9kZWZhdWx0LmNvbS5kdGM:dtc.com/default"],"types":["A","AAAA","CNAME","NAPTR","SRV"]}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:lbdn", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Restart DNS Services")
                restart_services()
                sleep(30)
                logging.info("Test Case 373 Execution Completed")

        @pytest.mark.run(order=374)
        def test_374_Validate_Created_LBDN(self):
                logging.info("Validate Created LBDN")
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                assert re.search(r'Lbdn',reference)
                sleep(5)
                print("Test Case 374 Execution Completed")
	
	@pytest.mark.run(order=375)
        def test_375_Validate_Default_Status_Of_DTC_Objects_After_adding_Lbdn(self):
                logging.info("Validate_Default_Status_Of_DTC_Objects After_adding_Lbdn")
                Validate_Server_Fail_back_Status("Server1")
                print(Server_data)
                server1=Server_data
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                server2=Server_data
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "GREEN"' in server1) and ('"availability": "GREEN"' in server2) and ('"availability": "GREEN"' in Pool_data) and ('"availability": "GREEN"' in Lbdn_data)):
                    assert True
                else:
                    assert False
                print("Test Case 375 Execution Completed")
		
	@pytest.mark.run(order=376)
        def test_376_Perform_server2_Failback_with_UNTIL_MANUAL_ENABLING_On_Member2(self):
                logging.info("Perform_server2_Failback_with_UNTIL_MANUAL_ENABLING On_Member2")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server2")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 376 Execution Completed")

        @pytest.mark.run(order=377)
        def test_377_Validate_server2_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_server2_Failback UNTIL_MANUAL_ENABLING")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)==0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 377 Execution Completed")
				
	@pytest.mark.run(order=378)
        def test_378_Perform_Pool1_Failback_with_UNTIL_MANUAL_ENABLING_On_Member2(self):
                logging.info("Perform_Pool1_Failback_with_UNTIL_MANUAL_ENABLING On_Member2")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 378 Execution Completed")

        @pytest.mark.run(order=379)
        def test_379_Validate_Pool1_Failback_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Pool1_Failback UNTIL_MANUAL_ENABLING")
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "WHITE"' in Pool_data) and ('"description": "Requires Manual enabling"' in Pool_data) and (int(check_master)==0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 379 Execution Completed")
				
	@pytest.mark.run(order=380)
        def test_380_Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING_On_Member2(self):
                logging.info("Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING On_Member2")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 380 Execution Completed")

        @pytest.mark.run(order=381)
        def test_381_Validate_Lbdn_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING")
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "WHITE"' in Lbdn_data) and ('"description": "Requires Manual enabling"' in Lbdn_data) and (int(check_master)==0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 381 Execution Completed")

	@pytest.mark.run(order=382)
        def test_382_Disable_DNS_service_on_the_grid_member(self):
            	logging.info("Disable DNS service on the grid member")
            	get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
            	res = json.loads(get_ref)
            	for i in res:
                	data = {"enable_dns": False}
                	if i["host_name"] == config.grid_member2_fqdn:
                    		response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                    		print_and_log(response)
                    		read  = re.search(r'200',response)
                    		if read == None:
                        		print("DNS disabled on member2")
                        		assert True
                    		else:
                        		print("DNS disable failed on member2")
                        		assert False
		sleep(20)
	    	print("Test Case 382 Execution Completed")
							
	@pytest.mark.run(order=383)
        def test_383_Validate_Disable_Status_Of_DTC_Objects_In_Member(self):
                logging.info("Validate_Disable_Status_Of_DTC_Objects In_Member")
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                sleep(2)
                child.expect('#')
                sleep(2)
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Master=child.before
                sleep(2)
                child.close()
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                child.logfile=sys.stdout
                sleep(2)
                child.expect('#')
                sleep(2)
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member1=child.before
                sleep(2)
                child.close()
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                sleep(2)
                child.expect('#')
                sleep(2)
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member2=child.before
                sleep(2)
                child.close()
                if (('"availability": "GREEN"' in Server_data) and ('"availability": "GREEN"' in Pool_data) and ('"availability": "GREEN"' in Lbdn_data) and ("'health' : 'WHITE'" not in Health_Master) and ("'health' : 'WHITE'" not in Health_Member1) and ("'health' : 'WHITE'" in Health_Member2)):
                    assert True
                else:
                    assert False
                print("Test Case 383 Execution Completed")

	@pytest.mark.run(order=384)
        def test_384_Enable_server2_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_server2_Failback UNTIL_MANUAL_ENABLING")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server2")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(20)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*DNS service is not running in the node .*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": "1 monitor(s) with an Disabled, Requires manual enabling status: icmp (ICMP)"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 384 Execution Completed")
				
	@pytest.mark.run(order=385)
        def test_385_Enable_Pool1_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Pool1_Failback UNTIL_MANUAL_ENABLING")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(20)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*DNS service is not running in the node .*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and ('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 385 Execution Completed")
				
	@pytest.mark.run(order=386)
        def test_386_Enable_Lbdn_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING")
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(20)
                log("stop","/infoblox/var/infoblox.log",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*DNS service is not running in the node .*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and ('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data) and ('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)==0) and (int(check_member_2)==0)):
                    assert True
                else:
                    assert False
                print("Test Case 386 Execution Completed")
				
	@pytest.mark.run(order=387)
        def test_387_Enable_DNS_service_on_the_grid_member(self):
            	logging.info("Enable DNS service on the grid member")
            	get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
            	res = json.loads(get_ref)
            	for i in res:
                	data = {"enable_dns": True}
                	if i["host_name"] == config.grid_member2_fqdn:
                    		response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                    		print_and_log(response)
                    		read  = re.search(r'200',response)
                    		if read == None:
                        		print("DNS enabled on member2")
                        		sleep(20)
                        		assert True
                    		else:
                        		print("DNS enable failed on member2")
                        		assert False
		sleep(20)
		print("Test Case 387 Execution Completed")
						
						
	@pytest.mark.run(order=388)
        def test_388_Validate_Disable_Status_Of_DTC_Objects_After_Restore(self):
                logging.info("Validate_Disable_Status_Of_DTC_Objects After Restore")
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                sleep(2)
                child.expect('#')
                sleep(2)
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Master=child.before
                sleep(2)
                child.close()
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                child.logfile=sys.stdout
                sleep(2)
                child.expect('#')
                sleep(2)
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member1=child.before
                sleep(2)
                child.close()
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                sleep(2)
                child.expect('#')
                sleep(2)
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member2=child.before
                sleep(2)
                child.close()            
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and ('"availability": "WHITE"' in Pool_data) and ('"description": "Requires Manual enabling"' in Pool_data) and ('"availability": "WHITE"' in Lbdn_data) and ('"description": "Requires Manual enabling"' in Lbdn_data) and ("'health' : 'WHITE'" not in Health_Master) and ("'health' : 'WHITE'" not in Health_Member1) and ("'health' : 'WHITE'" in Health_Member2)):
                    assert True
                else:
                    assert False
                print("Test Case 388 Execution Completed")

						
	@pytest.mark.run(order=389)
        def test_389_Enable_server2_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_server2_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server2")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)==0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 389 Execution Completed")
				
	@pytest.mark.run(order=390)
        def test_390_Enable_Pool1_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Pool1_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and ('"availability": "WHITE"' in Pool_data) and ('"description": "Requires Manual enabling"' in Pool_data) and (int(check_master)==0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 390 Execution Completed")
				
	@pytest.mark.run(order=391)
        def test_391_Enable_Lbdn_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and ('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data) and ('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)==0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 391 Execution Completed")
	
	@pytest.mark.run(order=392)
        def test_392_Perform_server2_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_server2_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server2")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 392 Execution Completed")

        @pytest.mark.run(order=393)
        def test_393_Validate_server2_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_server2_Failback UNTIL_MANUAL_ENABLING")
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 393 Execution Completed")
				
	@pytest.mark.run(order=394)
        def test_394_Perform_Pool1_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_Pool1_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 394 Execution Completed")

        @pytest.mark.run(order=395)
        def test_395_Validate_Pool1_Failback_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Pool1_Failback UNTIL_MANUAL_ENABLING")
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                if (('"availability": "WHITE"' in Pool_data) and ('"description": "Requires Manual enabling"' in Pool_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 395 Execution Completed")
				
	@pytest.mark.run(order=396)
        def test_396_Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING(self):
                logging.info("Perform_Lbdn_Failback_with_UNTIL_MANUAL_ENABLING")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":40,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
                print(data)
                DTC_Object_Fail_back_Manual_Disable(data)
                assert re.search(r'"failback_status": "SUCCESS"',failback_output)
                sleep(20)
                print("Test Case 396 Execution Completed")

        @pytest.mark.run(order=397)
        def test_397_Validate_Lbdn_Failback_For_UNTIL_MANUAL_ENABLING(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING")
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                if (('"availability": "WHITE"' in Lbdn_data) and ('"description": "Requires Manual enabling"' in Lbdn_data) and (int(check_master)!=0) and (int(check_member_1)!=0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 397 Execution Completed")
				
	@pytest.mark.run(order=398)
        def test_398_Validate_Disable_Status_Of_DTC_Objects_with_Master_Candidate_Enabled(self):
                logging.info("Validate_Disable_Status_Of_DTC_Objects with_Master_Candidate_Enabled")
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                sleep(2)
                child.expect('#')
                sleep(2)
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Master=child.before
                sleep(2)
                child.close()
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                child.logfile=sys.stdout
                sleep(2)
                child.expect('#')
                sleep(2)
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member1=child.before
                sleep(2)
                child.close()
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                sleep(2)
                child.expect('#')
                sleep(2)
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member2=child.before
                sleep(2)
                child.close()
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and ('"availability": "WHITE"' in Pool_data) and ('"description": "Requires Manual enabling"' in Pool_data) and ('"availability": "WHITE"' in Lbdn_data) and ('"description": "Requires Manual enabling"' in Lbdn_data) and ("'health' : 'WHITE'" in Health_Master) and ("'health' : 'WHITE'" in Health_Member1) and ("'health' : 'WHITE'" in Health_Member2)):
                    assert True
                else:
                    assert False
                print("Test Case 398 Execution Completed")
				
	@pytest.mark.run(order=399)
        def test_399_Disable_Master_Candidate_For_SA_member(self):
                logging.info("Disable Master_Candidate For SA-member")
                response =  ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                res = json.loads(response)
                ref1 = json.loads(response)[2]['_ref']
                print ref1
                data = {"master_candidate":False}
                response = ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
                print(response)
                sleep(400)
                print("Test Case 399 Execution Completed")

        @pytest.mark.run(order=400)
        def test_400_Validate_Disable_Master_Candidate_For_SA_member(self):
                logging.info("Disable Master_Candidate For SA-member")
                response =  ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
                print response
                logging.info(response)
                res = json.loads(response)
                ref1 = json.loads(response)[2]['_ref']
                print ref1
                response = ib_NIOS.wapi_request('GET', object_type=ref1+"?_return_fields=master_candidate")
                print(response)
                if('"master_candidate": false' in response):
                        assert True
                else:
                        assert False
		validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_member1_vip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.active_ip)
                validate_sigsegv_sigquit_and_sigabrt_core_files(config.passive_ip)
                print("Test Case 400 Execution Completed")
				
	@pytest.mark.run(order=401)
        def test_401_Validate_Disable_Status_Of_DTC_Objects_with_Master_Candidate_Disabled_NIOS_85557(self):
                logging.info("Validate_Disable_Status_Of_DTC_Objects with_Master_Candidate Disable NIOS_85557")
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                sleep(2)
                child.expect('#')
                sleep(2)
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Master=child.before
                sleep(2)
                child.close()
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                child.logfile=sys.stdout
                sleep(2)
                child.expect('#')
                sleep(2)
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member1=child.before
                sleep(2)
                child.close()
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                sleep(2)
                child.expect('#')
                sleep(2)
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member2=child.before
                sleep(2)
                child.close()
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and ('"availability": "WHITE"' in Pool_data) and ('"description": "Requires Manual enabling"' in Pool_data) and ('"availability": "WHITE"' in Lbdn_data) and ('"description": "Requires Manual enabling"' in Lbdn_data) and ("'health' : 'WHITE'" in Health_Master) and ("'health' : 'WHITE'" in Health_Member1) and ("'health' : 'WHITE'" in Health_Member2)):
                    assert True
                else:
                    assert False
                print("Test Case 401 Execution Completed")

	@pytest.mark.run(order=402)
        def test_402_Enable_server2_Failback_For_UNTIL_MANUAL_ENABLING_NIOS_85557(self):
                logging.info("Validate_server2_Failback UNTIL_MANUAL_ENABLING NIOS_85557")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("server","Server2")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)==0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 402 Execution Completed")
				
	@pytest.mark.run(order=403)
        def test_403_Enable_Pool1_Failback_For_UNTIL_MANUAL_ENABLING_NIOS_85557(self):
                logging.info("Validate_Pool1_Failback UNTIL_MANUAL_ENABLING NIOS_85557")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*Pool Pool1 is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and ('"availability": "WHITE"' in Pool_data) and ('"description": "Requires Manual enabling"' in Pool_data) and (int(check_master)==0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 403 Execution Completed")
				
	@pytest.mark.run(order=404)
        def test_404_Enable_Lbdn_Failback_For_UNTIL_MANUAL_ENABLING_NIOS_85557(self):
                logging.info("Validate_Lbdn_Failback UNTIL_MANUAL_ENABLING NIOS_85557")
                log("start","/var/log/syslog",config.grid_vip)
                log("start","/var/log/syslog",config.grid_member1_vip)
                log("start","/var/log/syslog",config.grid_member2_vip)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                data={"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn],"dtc_object":str(reference)}
                DTC_Object_Fail_back_Manual_Enable(data)
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                log("stop","/var/log/syslog",config.grid_member1_vip)
                log("stop","/var/log/syslog",config.grid_member2_vip)
                check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messages*")
                print(int(check_master))
                check_member_1=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member1_vip)+"_var_log_messages*")
                print(int(check_member_1))
                check_member_2=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_member2_vip)+"_var_log_messages*")
                print(int(check_member_2))
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and ('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data) and ('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)==0) and (int(check_member_1)==0) and (int(check_member_2)!=0)):
                    assert True
                else:
                    assert False
                print("Test Case 404 Execution Completed")

	@pytest.mark.run(order=405)
        def test_405_Validate_Enable_Status_Of_DTC_Objects_with_Master_Candidate_Disabled_NIOS_85557(self):
                logging.info("Validate_Enable_Status_Of_DTC_Objects with_Master_Candidate Disable NIOS_85557")
                Validate_Server_Fail_back_Status("Server2")
                print(Server_data)
                Validate_Pool_Fail_back_Status("Pool1")
                print(Pool_data)
                Validate_Lbdn_Fail_back_Status("Lbdn")
                print(Lbdn_data)
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                sleep(2)
                child.expect('#')
                sleep(2)
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Master=child.before
                sleep(2)
                child.close()
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
                child.logfile=sys.stdout
                sleep(2)
                child.expect('#')
                sleep(2)
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member1=child.before
                sleep(2)
                child.close()
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member2_vip)
                child.logfile=sys.stdout
                sleep(2)
                child.expect('#')
                sleep(2)
                child.sendline('cat /infoblox/var/idns_conf/health_status.txt')
                child.expect('#')
                Health_Member2=child.before
                sleep(2)
                child.close()
                if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and ('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data) and ('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and ("'health' : 'WHITE'" not in Health_Master) and ("'health' : 'WHITE'" not in Health_Member1) and ("'health' : 'WHITE'" not in Health_Member2)):
                    assert True
                else:
                    assert False
                print("Test Case 405 Execution Completed")
	 		

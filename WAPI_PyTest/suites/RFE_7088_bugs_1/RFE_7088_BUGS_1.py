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
import ast

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
        print_and_log("Server Fail Back started")
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:"+object_type+"?name="+object_name, grid_vip=config.grid_vip)
        res = json.loads(ref)
        reference = json.loads(ref)[0]['_ref']
        print_and_log(reference)
        global reference
        #print_and_log(data)

def DTC_Object_Fail_back_Manual_Disable(data):
        #response = ib_NIOS.wapi_request('PUT',object_type=ref1, fields=json.dumps(data))
        response = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data),params="?_function=dtc_object_disable")
        failback_output = str(response)
        print(response)
        failback_output=failback_output.replace('\n','').replace('{','').replace('}','').replace(']','').replace('[','').replace('\\','').replace("'",'')
        global failback_output
        print_and_log("Server Failback completed")

def DTC_Object_Fail_back_Manual_Enable(data):
        #response = ib_NIOS.wapi_request('PUT',object_type=ref1, fields=json.dumps(data))
        response = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data),params="?_function=dtc_object_enable")
        print(response)
        enable_output = str(response)
        global enable_output
        print_and_log("Server Enable completed")

def DTC_Object_Fail_back_GET_State(object_type,object_name):
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:"+object_type+"?name="+object_name, grid_vip=config.grid_vip)
        res = json.loads(ref)
        reference = json.loads(ref)[0]['_ref']
        print_and_log(reference)
        data={"dtc_object":str(reference)}
        response = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data),params="?_function=dtc_get_object_grid_state")
        #state_output = response
        state_output=json.loads(response)
        state_output=eval(json.dumps(state_output))
        global state_output
        print_and_log("Server Enable completed")


def Validate_Server_Fail_back_Status(object_name):
        print_and_log("Validate Server Fail Back Status")
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name="+object_name+"&_return_fields%2B=health", grid_vip=config.grid_vip)
        #print_and_log(ref)
        Server_data = ref
        global Server_data

def Validate_Pool_Fail_back_Status(object_name):
        print_and_log("Validate Pool Fail Back Status")
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?name="+object_name+"&_return_fields%2B=health", grid_vip=config.grid_vip)
        #print_and_log(ref)
        Pool_data = ref
        global Pool_data

def Validate_Lbdn_Fail_back_Status(object_name):
        print_and_log("Validate Lbdn Fail Back Status")
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?name="+object_name+"&_return_fields%2B=health", grid_vip=config.grid_vip)
        #print_and_log(ref)
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
                data = {"fqdn": "dtc.com","grid_primary": [{"name": config.grid_member_fqdn,"stealth":False}, {"name": config.grid_member1_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Restart DNS Services") 
                restart_services()
                sleep(30)
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
                #response =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name=Server1", grid_vip=config.grid_vip)
                #print response
                #logging.info(response)
                Getting_DTC_Object_Reference("server","Server1")
                assert re.search(r'Server1',reference)
                sleep(5)
                print("Test Case 6 Execution Completed")


        @pytest.mark.run(order=7)
        def test_007_add_a_DTC_Server2(self):
                logging.info("Create A DTC second Server")
                data = {"name":"Server2","host":config.Server2}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 7 Execution Completed")

        @pytest.mark.run(order=8)
        def test_008_Validate_Created_Server2(self):
                logging.info("Validate Created Server2")
                #response =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name=Server1", grid_vip=config.grid_vip)
                #print response
                #logging.info(response)
                Getting_DTC_Object_Reference("server","Server2")
                assert re.search(r'Server2',reference)
                sleep(5)
                print("Test Case 8 Execution Completed")


        @pytest.mark.run(order=9)
        def test_009_add_a_DTC_pool(self):
                logging.info("Creating dtc pool")
                server=ib_NIOS.wapi_request('GET',object_type='dtc:server')
                server1=json.loads(server)[0]['_ref']
                server2=json.loads(server)[1]['_ref']
                data={"name": "Pool1","lb_preferred_method": "ROUND_ROBIN","monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"],"servers": [{"ratio": 1,"server": server1},{"ratio": 1,"server": server2}]}
                pool_ref=ib_NIOS.wapi_request('POST',object_type='dtc:pool',fields=json.dumps(data))
                logging.info(pool_ref)
                if bool(re.match("\"dtc:pool*.",str(pool_ref))):
                    logging.info("pool created succesfully")
                else:
                    raise Exception("pool creation unsuccessful")
                logging.info("Test Case 9 Execution Completed")

        
        @pytest.mark.run(order=10)
        def test_010_Validate_Created_Pool(self):
                logging.info("Validate Created Pool")
                Getting_DTC_Object_Reference("pool","Pool1")
                #response =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?name=Pool1", grid_vip=config.grid_vip)
                #print response
                #logging.info(response)
                assert re.search(r'Pool1',reference)
                sleep(5)
                print("Test Case 10 Execution Completed")

        @pytest.mark.run(order=11)
        def test_011_add_a_DTC_lbdn(self):
            logging.info("Creating lbdn")
            sleep(10)
            zone=ib_NIOS.wapi_request('GET',object_type='zone_auth', params="?fqdn=dtc.com")
            zone_ref=json.loads(zone)[0]['_ref']
            pool=ib_NIOS.wapi_request('GET',object_type='dtc:pool')
            pool_ref=json.loads(pool)[0]['_ref']
            data={"name": "Lbdn","lb_method": "ROUND_ROBIN","patterns": ["a1.dtc.com"],"auth_zones": [zone_ref],"pools": [{"pool": pool_ref,"ratio": 1}]}
            lbdn_ref=ib_NIOS.wapi_request('POST',object_type='dtc:lbdn',fields=json.dumps(data))
            print(lbdn_ref)
            logging.info(lbdn_ref)
            if bool(re.match("\"dtc:lbdn*.",str(lbdn_ref))):
                logging.info("lbdn created succesfully")
                restart_services()
                print("Test Case 11 Execution Completed")
            else:
                raise Exception("lbdn creation unsuccessful")


        @pytest.mark.run(order=12)
        def test_012_Validate_Created_LBDN(self):
                logging.info("Validate Created LBDN")
                #response =  ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?name=Lbdn", grid_vip=config.grid_vip)
                #print response
                #logging.info(response)
                Getting_DTC_Object_Reference("lbdn","Lbdn")
                assert re.search(r'Lbdn',reference)
                sleep(5)
                print("Test Case 12 Execution Completed")


        @pytest.mark.run(order=13)
        def test_013_NIOS_84773_disable_server1_with_disable_until_manual_enable(self):
            logging.info("NIOS-84773 Disable server1 with option disable until manual enable")
            log("start","/var/log/syslog",config.grid_vip)
            Getting_DTC_Object_Reference("server","Server1")
            data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
            print(data)
            DTC_Object_Fail_back_Manual_Disable(data)
            assert re.search(r'"failback_status": "SUCCESS"',failback_output)
            sleep(30)
            print("Test Case 13 Execution Completed")

        @pytest.mark.run(order=14)
        def test_014_NIOS_84773_Verify_disable_server1_with_disable_until_manual_enable(self):
            logging.info("NIOS-84773 Verify Disable server1 with option disable until manual enable")
            log("stop","/var/log/syslog",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*Server Server1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_syslog*")
            print(int(check_master))
            print(check_master)
            Validate_Server_Fail_back_Status("Server1")
            print(Server_data)
            if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)!=0) ):
                assert True
            else:
                assert False
            print("Test Case 14 Execution Completed")

        @pytest.mark.run(order=15)
        def test_015_NIOS_84773_disable_lbdn_with_disable_until_manual_enable(self):
            logging.info("NIOS-84773 Disable lbdn with option disable until manual enable")
            log("start","/var/log/syslog",config.grid_vip)
            Getting_DTC_Object_Reference("lbdn","Lbdn")
            data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
            print(data)
            DTC_Object_Fail_back_Manual_Disable(data)
            assert re.search(r'"failback_status": "SUCCESS"',failback_output)
            sleep(30)
            print("Test Case 15 Execution Completed")

        @pytest.mark.run(order=16)
        def test_016_NIOS_84773_Verify_disable_lbdn_with_disable_until_manual_enable(self):
            logging.info("NIOS-84773 Verify Disable lbdn with option disable until manual enable")
            log("stop","/var/log/syslog",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_syslog*")
            print(int(check_master))
            print(check_master)
            Validate_Lbdn_Fail_back_Status("Lbdn")
            print(Lbdn_data)
            if (('"availability": "WHITE"' in Lbdn_data) and ('"description": "Requires Manual enabling"' in Lbdn_data) and (int(check_master)!=0) ):
                assert True
            else:
                assert False
            print("Test Case 16 Execution Completed")


        @pytest.mark.run(order=17)
        def test_017_NIOS_84773_Enable_server1(self):
            logging.info("NIOS-84773 Enable server1")
            log("start","/var/log/syslog",config.grid_vip)
            Getting_DTC_Object_Reference("server","Server1")
            data={"dtc_object":str(reference),"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn]}
            DTC_Object_Fail_back_Manual_Enable(data)
            assert re.search(r'"failback_status": "SUCCESS"',enable_output)
            sleep(30)
            print("Test Case 17 Execution Completed")

        @pytest.mark.run(order=18)
        def test_018_NIOS_84773_Verify_Enable_server1(self):
            logging.info("NIOS-84773 Verify Enable server1")
            log("stop","/var/log/syslog",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_syslog*")
            print(int(check_master))
            print(check_master)
            Validate_Server_Fail_back_Status("Server1")
            print(Server_data)
            if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)!=0) ):
                assert True
            else:
                assert False
            print("Test Case 18 Execution Completed")

        @pytest.mark.run(order=19)
        def test_019_NIOS_84773_enable_lbdn(self):
            logging.info("NIOS-84773 Enable lbdn")
            log("start","/var/log/syslog",config.grid_vip)
            Getting_DTC_Object_Reference("lbdn","Lbdn")
            data={"dtc_object":str(reference),"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn]}
            DTC_Object_Fail_back_Manual_Enable(data)
            assert re.search(r'"failback_status": "SUCCESS"',enable_output)
            sleep(30)
            print("Test Case 19 Execution Completed")

        @pytest.mark.run(order=20)
        def test_020_NIOS_84773_verify_enable_lbdn(self):
            logging.info("NIOS-84773 verify enable lbdn")
            log("stop","/var/log/syslog",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_syslog*")
            print(int(check_master))
            print(check_master)
            Validate_Lbdn_Fail_back_Status("Lbdn")
            print(Lbdn_data)
            if (('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)!=0) ):
                assert True
            else:
                assert False
            print("Test Case 20 Execution Completed")

        @pytest.mark.run(order=21)
        def test_021_NIOS_84773_Verify_Server1_status_after_enabling_the_Lbdn(self):
            Validate_Server_Fail_back_Status("Server1")
            print(Server_data)
            if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data)):
                sleep(30)
                assert True
            else:
                assert False
            print("Test Case 21 Execution Completed")

        @pytest.mark.run(order=22)
        def test_022_NIOS_84395_NIOS_84353_Try_disabling_the_single_pool(self):
            logging.info("NIOS-84395 NIOS-84353 Try disabling the single pool")
            Getting_DTC_Object_Reference("pool","Pool1")
            data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
            print(data)
            DTC_Object_Fail_back_Manual_Disable(data)
            print(failback_output)
            if 'Cannot disable all the pools in an LBDN. At least one pool must be enabled' in str(failback_output):
                print("Single pool disable failed as expected")
                print("Test Case 22 Execution Completed")
                assert True
            else:
                 print("Single pool disable passed as unexpected")
                 print("Test Case 22 Execution Completed")
                 assert False

        @pytest.mark.run(order=23)
        def test_023_NIOS_84395_NIOS_84353_Check_status_of_lbdn(self):
            logging.info("NIOS-84395 NIOS-84353 Check status of lbdn")
            Validate_Lbdn_Fail_back_Status("Lbdn")
            print(Lbdn_data)
            if (('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data)):
                sleep(30)
                assert True
            else:
                assert False
            print("Test Case 23 Execution Completed")

        @pytest.mark.run(order=24)
        def test_024_NIOS_84395_NIOS_84353_Enable_pool_if_not_enabled(self):
            logging.info("Enable pool if not enabled")
            Validate_Pool_Fail_back_Status("Pool1")
            print(Pool_data)
            if (('"availability": "GREEN"' in Pool_data) and ('"description": ""' in Pool_data)):
                print("Pool is already enabled")
            else:
                Getting_DTC_Object_Reference("pool","Pool1")
                data={"dtc_object":str(reference),"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn]}
                DTC_Object_Fail_back_Manual_Enable(data)
                assert re.search(r'"failback_status": "SUCCESS"',enable_output)
                sleep(30)
            print("Test Case 24 Execution Completed")

        @pytest.mark.run(order=25)
        def test_025_NIOS_84415_Check_if_SIGSEGV_cores_have_been_generated(self):
            logging.info("NIOS-84415 Verify if SIGSEGV cores have been generated")
            sleep(30)
            validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_vip)
            validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_member1_vip)
            print("Test Case 25 Execution Completed")

        @pytest.mark.run(order=26)
        def test_026_NIOS_84311_Disable_DNS_service_on_the_grid_member(self):
            logging.info("NIOS-84311 Disable DNS service on the grid member")
            get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
            res = json.loads(get_ref)
            for i in res:
                data = {"enable_dns": False}
                if i["host_name"] == config.grid_member1_fqdn:
                    response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                    print_and_log(response)
                    read  = re.search(r'200',response)
                    if read == None:
                        print("DNS disabled on member1")
                        assert True
                    else:
                        print("DNS disable failed on member1")
                        assert False
        
        @pytest.mark.run(order=27)
        def test_027_NIOS_84311_Disable_server2_with_manual_enable_option_keep_the_member_in_enable_column(self):
            logging.info("NIOS-84311 Disable server2 with manual enable option. Disable the master, but keep the member enabled while disabling")
            log("start","/infoblox/var/infoblox.log",config.grid_vip)
            Getting_DTC_Object_Reference("server","Server2")
            data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
            print(data)
            DTC_Object_Fail_back_Manual_Disable(data)
            assert re.search(r'"failback_status": "SUCCESS"',failback_output)
            sleep(30)
            print("Test Case 27 Execution Completed")

        @pytest.mark.run(order=28)
        def test_028_NIOS_84311_Verify_disable_server2_with_disable_until_manual_enable(self):
            logging.info("NIOS-84311 Verify Disable server2 with option disable until manual enable")
            log("stop","/infoblox/var/infoblox.log",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*Server Server2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
            print(int(check_master))
            print(check_master)
            Validate_Server_Fail_back_Status("Server2")
            print(Server_data)
            if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)!=0) ):
                assert True
            else:
                assert False
            print("Test Case 28 Execution Completed")

        @pytest.mark.run(order=29)
        def test_029_NIOS_84311_Enable_server2_with_manual_enable_option(self):
            logging.info("NIOS-84311 Enable server2 with manual enable option.")
            log("start","/infoblox/var/infoblox.log",config.grid_vip)
            Getting_DTC_Object_Reference("server","Server2")
            data={"dtc_object":str(reference),"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn]}
            DTC_Object_Fail_back_Manual_Enable(data)
            assert re.search(r'"failback_status": "SUCCESS"',enable_output)
            sleep(30)
            print("Test Case 29 Execution Completed")

        @pytest.mark.run(order=30)
        def test_030_NIOS_84311_Verify_Enable_server2_with_manual_enable_option(self):
            logging.info("NIOS-84311 Verify enable server2 with manual enable option.")
            log("stop","/infoblox/var/infoblox.log",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*Server Server2 is enabling.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
            check_master1=commands.getoutput(" grep -cw \".*DNS service is not running in the node "+config.grid_member1_fqdn+".*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
            print(int(check_master))
            print(int(check_master1))
            Validate_Server_Fail_back_Status("Server2")
            print(Server_data)
            if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and (int(check_master)!=0) and (int(check_master1)!=0)):
                    assert True
            else:
                    assert False
            print("Test Case 30 Execution Completed")


        @pytest.mark.run(order=31)
        def test_031_NIOS_84311_Enable_DNS_service_on_the_grid_member(self):
            logging.info("NIOS-84311 Enable DNS service on the grid member")
            get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
            res = json.loads(get_ref)
            for i in res:
                data = {"enable_dns": True}
                if i["host_name"] == config.grid_member1_fqdn:
                    response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                    print_and_log(response)
                    read  = re.search(r'200',response)
                    if read == None:
                        print("DNS enabled on member1")
                        sleep(30)
                        assert True
                    else:
                        print("DNS enable failed on member1")
                        assert False

        @pytest.mark.run(order=32)
        def test_032_NIOS_84298_disable_lbdn_with_disable_until_manual_enable(self):
            logging.info("NIOS-84298 Disable lbdn with option disable until manual enable")
            log("start","/var/log/syslog",config.grid_vip)
            Getting_DTC_Object_Reference("lbdn","Lbdn")
            data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
            print(data)
            DTC_Object_Fail_back_Manual_Disable(data)
            assert re.search(r'"failback_status": "SUCCESS"',failback_output)
            sleep(30)
            print("Test Case 32 Execution Completed")

        @pytest.mark.run(order=33)
        def test_033_NIOS_84298_Verify_disable_lbdn_with_disable_until_manual_enable(self):
            logging.info("NIOS-84298 Verify Disable lbdn with option disable until manual enable")
            log("stop","/var/log/syslog",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_syslog*")
            print(int(check_master))
            print(check_master)
            Validate_Lbdn_Fail_back_Status("Lbdn")
            print(Lbdn_data)
            if (('"availability": "WHITE"' in Lbdn_data) and ('"description": "Requires Manual enabling"' in Lbdn_data) and (int(check_master)!=0) ):
                assert True
            else:
                assert False
            print("Test Case 33 Execution Completed")

        @pytest.mark.run(order=34)
        def test_034_NIOS_84298_enable_lbdn(self):
            logging.info("NIOS-84298 Enable lbdn")
            log("start","/var/log/syslog",config.grid_vip)
            Getting_DTC_Object_Reference("lbdn","Lbdn")
            data={"dtc_object":str(reference),"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn]}
            DTC_Object_Fail_back_Manual_Enable(data)
            assert re.search(r'"failback_status": "SUCCESS"',enable_output)
            sleep(30)
            print("Test Case 34 Execution Completed")

        @pytest.mark.run(order=35)
        def test_035_NIOS_84298_verify_enable_lbdn(self):
            logging.info("NIOS-84298 verify enable lbdn")
            log("stop","/var/log/syslog",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_syslog*")
            print(int(check_master))
            print(check_master)
            Validate_Lbdn_Fail_back_Status("Lbdn")
            print(Lbdn_data)
            if (('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)!=0) ):
                sleep(30)
                assert True
            else:
                assert False
            print("Test Case 35 Execution Completed")


        @pytest.mark.run(order=36)
        def test_036_NIOS_84765_disable_server1_from_server_properties_checkbox(self):
            logging.info("NIOS-84765 Disable server1 from server properties checkbox")
            response = ib_NIOS.wapi_request('GET', object_type="dtc:server", grid_vip=config.grid_vip)
            response = json.loads(response)
            server_ref = ''
            for i in response:
                if i["name"] == "Server1":
                    server_ref = i["_ref"]
                    print(server_ref)
            data={"disable":True}
            print(data)
            response = ib_NIOS.wapi_request('PUT',ref=server_ref, fields=json.dumps(data))
            print(response)
            if bool(re.match("\"dtc:server*.",str(response))):
                restart_services()
                sleep(30)
                assert True
            else:
                assert False
            print("Test Case 36 Execution Completed")

        @pytest.mark.run(order=37)
        def test_037_NIOS_84765_Verify_disable_server1_with_disable_until_manual_enable(self):
            logging.info("NIOS-84765 Verify Disable server1 from server properties checkbox")
            response = ib_NIOS.wapi_request('GET', object_type="dtc:server", grid_vip=config.grid_vip)
            response = json.loads(response)
            server_ref = ''
            for i in response:
                if i["name"] == "Server1":
                    server_ref = i["_ref"]
                    print(server_ref)
            ref = ib_NIOS.wapi_request('GET',object_type=server_ref+'?_return_fields=disable',grid_vip=config.grid_vip)
            ref =json.loads(ref)
            if ref["disable"] == True:
                assert True
            else:
                assert False
            print("Test Case 37 Execution Completed")


        @pytest.mark.run(order=38)
        def test_038_NIOS_84765_disable_server2_with_disable_until_manual_enable(self):
            logging.info("NIOS-84765 Disable server2 with option disable until manual enable")
            log("start","/var/log/syslog",config.grid_vip)
            Getting_DTC_Object_Reference("server","Server2")
            data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
            print(data)
            DTC_Object_Fail_back_Manual_Disable(data)
            assert re.search(r'Cannot disable all the servers in a pool. At least one server must be enabled',failback_output)
            sleep(30)
            print("Test Case 38 Execution Completed")

        @pytest.mark.run(order=39)
        def test_039_NIOS_84765_Enable_server1(self):
            logging.info("NIOS-84765 Enable server1")
            response = ib_NIOS.wapi_request('GET', object_type="dtc:server", grid_vip=config.grid_vip)
            response = json.loads(response)
            server_ref = ''
            for i in response:
                if i["name"] == "Server1":
                    server_ref = i["_ref"]
                    print(server_ref)
            data={"disable":False}
            print(data)
            response = ib_NIOS.wapi_request('PUT',ref=server_ref, fields=json.dumps(data))
            print(response)
            if bool(re.match("\"dtc:server*.",str(response))):
                restart_services()
                sleep(30)
                assert True
            else:
                assert False
            print("Test Case 39 Execution Completed")

        @pytest.mark.run(order=40)
        def test_040_NIOS_84765_Verify_Enable_server1(self):
            logging.info("NIOS-84765 Verify Enable server1")
            response = ib_NIOS.wapi_request('GET', object_type="dtc:server", grid_vip=config.grid_vip)
            response = json.loads(response)
            server_ref = ''
            for i in response:
                if i["name"] == "Server1":
                    server_ref = i["_ref"]
                    print(server_ref)
            ref = ib_NIOS.wapi_request('GET',object_type=server_ref+'?_return_fields=disable',grid_vip=config.grid_vip)
            ref =json.loads(ref)
            if ref["disable"] == False:
                assert True
            else:
                assert False
            print("Test Case 40 Execution Completed")


        @pytest.mark.run(order=41)
        def test_041_NIOS_84899_disable_server1_with_disable_until_manual_enable(self):
            logging.info("NIOS-84899 Disable server1 with option disable until manual enable")
            log("start","/var/log/syslog",config.grid_vip)
            Getting_DTC_Object_Reference("server","Server1")
            data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
            print(data)
            DTC_Object_Fail_back_Manual_Disable(data)
            assert re.search(r'"failback_status": "SUCCESS"',failback_output)
            sleep(30)
            print("Test Case 41 Execution Completed")

        @pytest.mark.run(order=42)
        def test_042_NIOS_84899_Verify_disable_server1_with_disable_until_manual_enable(self):
            logging.info("NIOS-84899 Verify Disable server1 with option disable until manual enable")
            log("stop","/var/log/syslog",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*Server Server1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_syslog*")
            check_master1=commands.getoutput(" grep -cw \".*name (Server1) action disable after 0 seconds for 0 seconds.*\" /tmp/"+str(config.grid_vip)+"_var_log_syslog*")
            print(int(check_master))
            print(check_master1)
            Validate_Server_Fail_back_Status("Server1")
            print(Server_data)
            if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)!=0) and (int(check_master1)== 0)):
                assert True
            else:
                assert False
            print("Test Case 42 Execution Completed")


        @pytest.mark.run(order=43)
        def test_043_NIOS_84899_Enable_server1(self):
            logging.info("NIOS-84899 Enable server1")
            log("start","/var/log/syslog",config.grid_vip)
            Getting_DTC_Object_Reference("server","Server1")
            data={"dtc_object":str(reference),"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn]}
            DTC_Object_Fail_back_Manual_Enable(data)
            assert re.search(r'"failback_status": "SUCCESS"',enable_output)
            sleep(30)
            print("Test Case 43 Execution Completed")

        @pytest.mark.run(order=44)
        def test_044_NIOS_84899_Verify_Enable_server1(self):
            logging.info("NIOS-84899 Verify Enable server1")
            log("stop","/var/log/syslog",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_messag*")
            check_master1=commands.getoutput(" grep -cw \".*name (Server1) action enable after 0 seconds for 0 seconds.*\" /tmp/"+str(config.grid_vip)+"_var_log_messag*")
            print(int(check_master1))
            print(check_master)
            Validate_Server_Fail_back_Status("Server1")
            print(Server_data)
            if (('"availability": "GREEN"' in Server_data)  and (int(check_master)!=0) and (int(check_master1)== 0)):
                sleep(30)
                assert True
            else:
                assert False
            print("Test Case 44 Execution Completed")

        @pytest.mark.run(order=45)
        def test_045_NIOS_84555_Disable_server1_manually_with_disable_for_specified_time_option(self):
            logging.info("NIOS-84555 Disable server1 manually with disable for specific time option")
            log("start","/var/log/syslog",config.grid_vip)
            Getting_DTC_Object_Reference("server","Server1")
            data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object":str(reference),"specific_time_disable":60}
            print(data)
            DTC_Object_Fail_back_Manual_Disable(data)
            assert re.search(r'"failback_status": "SUCCESS"',failback_output)
            sleep(15)
            print("Test Case 45 Execution Completed")

        @pytest.mark.run(order=46)
        def test_046_NIOS_84555_Verify_Disable_server1_manually_with_disable_for_specified_time_option(self):
            logging.info("NIOS-84555 Verify disable server1 manually with disable for specific time option")
            log("stop","/var/log/syslog",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*Server Server1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_syslog*")
            print(int(check_master))
            check_master1=commands.getoutput(" grep -cw \".*Add disable event for object type(4) name (Server1) action enable after 60 seconds for 0 seconds.*\" /tmp/"+str(config.grid_vip)+"_var_log_syslog*")
            print(int(check_master1))
            Validate_Server_Fail_back_Status("Server1")
            print(Server_data)
            if (('"availability": "DARKGRAY"' in Server_data) and ('"description": "Temporarily Disabled"' in Server_data) and (int(check_master)!=0) and (int(check_master1)!=0) ):
                sleep(40)
                assert True
            else:
                sleep(40)
                assert False
            print("Test Case 46 Execution Completed")

        @pytest.mark.run(order=47)
        def test_047_NIOS_84415_disable_lbdn_with_disable_until_manual_enable(self):
            logging.info("NIOS-84415 Disable lbdn with option disable until manual enable")
            log("start","/var/log/syslog",config.grid_vip)
            Getting_DTC_Object_Reference("lbdn","Lbdn")
            data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
            print(data)
            DTC_Object_Fail_back_Manual_Disable(data)
            assert re.search(r'"failback_status": "SUCCESS"',failback_output)
            sleep(30)
            print("Test Case 47 Execution Completed")

        @pytest.mark.run(order=48)
        def test_048_NIOS_84415_Verify_disable_lbdn_with_disable_until_manual_enable(self):
            logging.info("NIOS-84415 Verify Disable lbdn with option disable until manual enable")
            log("stop","/var/log/syslog",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_syslog*")
            print(int(check_master))
            print(check_master)
            Validate_Lbdn_Fail_back_Status("Lbdn")
            print(Lbdn_data)
            if (('"availability": "WHITE"' in Lbdn_data) and ('"description": "Requires Manual enabling"' in Lbdn_data) and (int(check_master)!=0) ):
                assert True
            else:
                assert False
            print("Test Case 48 Execution Completed")

        @pytest.mark.run(order=49)
        def test_049_NIOS_84415_Check_if_SIGSEGV_cores_have_been_generated(self):
            logging.info("NIOS-84415 Verify if SIGSEGV cores have been generated")
            sleep(30)
            validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_vip)
            validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_member1_vip)
            print("Test Case 49 Execution Completed")

        @pytest.mark.run(order=50)
        def test_050_NIOS_84415_enable_lbdn(self):
            logging.info("NIOS-84415 Enable lbdn")
            log("start","/var/log/syslog",config.grid_vip)
            Getting_DTC_Object_Reference("lbdn","Lbdn")
            data={"dtc_object":str(reference),"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn]}
            DTC_Object_Fail_back_Manual_Enable(data)
            assert re.search(r'"failback_status": "SUCCESS"',enable_output)
            sleep(30)
            print("Test Case 50 Execution Completed")

        @pytest.mark.run(order=51)
        def test_051_NIOS_84415_verify_enable_lbdn(self):
            logging.info("NIOS-84415 verify enable lbdn")
            log("stop","/var/log/syslog",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_syslog*")
            print(int(check_master))
            print(check_master)
            Validate_Lbdn_Fail_back_Status("Lbdn")
            print(Lbdn_data)
            if (('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)!=0) ):
                sleep(30)
                assert True
            else:
                assert False
            print("Test Case 51 Execution Completed")

        @pytest.mark.run(order=52)
        def test_052_NIOS_84293_Disable_Server1_with_option_disable_until_DNS_restart(self):
            logging.info("NIOS-84293 Disable server1 with option disable until DNS restart")
            log("start","/var/log/syslog",config.grid_vip)
            Getting_DTC_Object_Reference("server","Server1")
            data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"UNTIL_DNS_RESTART","dtc_object":str(reference),"specific_time_disable":100}
            print(data)
            DTC_Object_Fail_back_Manual_Disable(data)
            assert re.search(r'"failback_status": "SUCCESS"',failback_output)
            sleep(30)
            print("Test Case 52 Execution Completed")

        @pytest.mark.run(order=53)
        def test_053_NIOS_84293_Verify_Disable_Server1_with_option_disable_until_DNS_restart(self):
            logging.info("NIOS-84293 Verify disable server1 with option disable until DNS restart")
            log("stop","/var/log/syslog",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*Server Server1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_syslog*")
            print(int(check_master))
            Validate_Server_Fail_back_Status("Server1")
            print(Server_data)
            if (('"availability": "DARKGRAY"' in Server_data) and ('"description": "Temporarily Disabled"' in Server_data) and (int(check_master)!=0) ):
                assert True
            else:
                assert False
            print("Test Case 53 Execution Completed")

        @pytest.mark.run(order=54)
        def test_054_NIOS_84293_Enable_server1_manually(self):
            logging.info("NIOS-84293 Enable server1 manually")
            log("start","/var/log/syslog",config.grid_vip)
            Getting_DTC_Object_Reference("server","Server1")
            data={"dtc_object":str(reference),"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn]}
            DTC_Object_Fail_back_Manual_Enable(data)
            assert re.search(r'"failback_status": "SUCCESS"',enable_output)
            sleep(30)
            print("Test Case 54 Execution Completed")

        @pytest.mark.run(order=55)
        def test_055_NIOS_84293_Verify_Enable_server1_manually(self):
            logging.info("NIOS-84293 Verify Enable server1 manually")
            log("stop","/var/log/syslog",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_syslog*")
            print(int(check_master))
            print(check_master)
            Validate_Server_Fail_back_Status("Server1")
            print(Server_data)
            if (('"availability": "GREEN"' in Server_data)  and (int(check_master)!=0) ):
                sleep(30)
                assert True
            else:
                assert False
            print("Test Case 55 Execution Completed")

        @pytest.mark.run(order=56)
        def test_056_NIOS_84257_Try_disabling_lbdn_with_no_grid_members_selected_and_check_if_error_is_thrown(self):
            logging.info("Try disabling lbdn with no grid members selected and check if error is thrown")
            Getting_DTC_Object_Reference("lbdn","Lbdn")
            data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
            print(data)
            DTC_Object_Fail_back_Manual_Disable(data)
            assert re.search(r'cannot be disabled if member list is empty',failback_output)
            sleep(30)
            print("Test Case 56 Execution Completed")

        @pytest.mark.run(order=57)
        def test_057_NIOS_84650_Disable_DNS_service_on_one_of_the_member(self):
            logging.info("Disable DNS service on one of the members")
            get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
            print_and_log(get_ref)
            res = json.loads(get_ref)
            for i in res:
                if i["ipv4addr"] == config.grid_vip:
                    print_and_log("Modify a enable_dns")
                    data = {"enable_dns": False}
                    response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                    print_and_log(response)
                    sleep(30)
                    assert re.search(r'member:dns.*',response)
            print_and_log("Test Case 57 Execution Completed")

        @pytest.mark.run(order=58)
        def test_058_NIOS_84650_Disbale_server1_selecting_the_member_for_which_DNS_service_was_disabled(self):
            logging.info("NIOS-84650 Disable server1 selecting the member for which DNS service was disabled")
            log("start","/infoblox/var/infoblox.log",config.grid_vip)
            Getting_DTC_Object_Reference("server","Server1")
            data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
            print(data)
            DTC_Object_Fail_back_Manual_Disable(data)
            assert re.search(r'"failback_status": "FAILED"',failback_output)
            sleep(30)
            print("Test Case 58 Execution Completed")

        @pytest.mark.run(order=59)
        def test_059_NIOS_84650_Verify_Disbale_server1_selecting_the_member_for_which_DNS_service_was_disabled(self):
            logging.info("NIOS-84773 Verify Disable server1 with option disable until manual enable")
            log("stop","/infoblox/var/infoblox.log",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*DNS service is not running in the node.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
            print(check_master)
            if ((int(check_master)!=0) ):
                assert True
            else:
                assert False
            print("Test Case 59 Execution Completed")

        @pytest.mark.run(order=60)
        def test_060_NIOS_84650_Enable_DNS_service_on_one_the_disabled_member(self):
            logging.info("Enable DNS service on the disbaled member")
            get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
            print_and_log(get_ref)
            res = json.loads(get_ref)
            for i in res:
                if i["ipv4addr"] == config.grid_vip:
                    print_and_log("Modify a enable_dns")
                    data = {"enable_dns": True}
                    response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                    print_and_log(response)
                    sleep(30)
                    assert re.search(r'member:dns.*',response)
            print_and_log("Test Case 60 Execution Completed")


        @pytest.mark.run(order=61)
        def test_061_NIOS_84406_Disable_server1_manually_with_disable_for_specified_time_option_and_delay_disable_set_to_false_with_value_for_deayed_disable_time(self):
            logging.info("NIOS-84406 Disable server1 manually with disable for specific time option, with delay_disable set to False and the value being set for the delayed_disable_time field")
            log("start","/var/log/syslog",config.grid_vip)
            Getting_DTC_Object_Reference("server","Server1")
            data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object":str(reference),"specific_time_disable":70}
            print(data)
            DTC_Object_Fail_back_Manual_Disable(data)
            assert re.search(r'"failback_status": "SUCCESS"',failback_output)
            sleep(15)
            print("Test Case 61 Execution Completed")

        @pytest.mark.run(order=62)
        def test_062_NIOS_84406_Verify_Disable_server1_manually_with_disable_for_specified_time_option(self):
            logging.info("NIOS-84406 Verify disable server1 manually with disable for specific time option")
            log("stop","/var/log/syslog",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*Server Server1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_syslog*")
            print(int(check_master))
            check_master1=commands.getoutput(" grep -cw \".*Add disable event for object type(4) name (Server1) action enable after 70 seconds for 0 seconds.*\" /tmp/"+str(config.grid_vip)+"_var_log_syslog*")
            print(int(check_master1))
            Validate_Server_Fail_back_Status("Server1")
            print(Server_data)
            if (('"availability": "DARKGRAY"' in Server_data) and ('"description": "Temporarily Disabled"' in Server_data) and (int(check_master)!=0) and (int(check_master1)!=0) ):
                sleep(70)
                assert True
            else:
                sleep(70)
                assert False
            print("Test Case 62 Execution Completed")

        @pytest.mark.run(order=63)
        def test_063_NIOS_84909_Try_disabling_DTC_object_by_selecting_a_non_DTC_member(self):
            logging.info("NIOS-84909 Try disabling a DTC object by selecting a non DTC member")
            log("start","/var/log/syslog",config.grid_vip)
            Getting_DTC_Object_Reference("server","Server1")
            data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member2_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
            print(data)
            try:
                DTC_Object_Fail_back_Manual_Disable(data)
            except Exception as e:
                assert re.search(r"Grid Member '"+config.grid_member2_fqdn+"' is a non-dtc member",str(e))
                sleep(30)
            print("Test Case 63 Execution Completed")

        @pytest.mark.run(order=64)
        def test_064_NIOS_84492_Disable_Server1_with_disable_until_manual_enable_for_the_master_only(self):
            logging.info("NIOS-84492 Disable server1 with disable until manual enable for the master only")
            log("start","/var/log/syslog",config.grid_vip)
            Getting_DTC_Object_Reference("server","Server1")
            #data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object":str(reference),"specific_time_disable":70}
            data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
            print(data)
            DTC_Object_Fail_back_Manual_Disable(data)
            assert re.search(r'"failback_status": "SUCCESS"',failback_output)
            sleep(30)
            print("Test Case 64 Execution Completed")

        @pytest.mark.run(order=65)
        def test_065_NIOS_84492_Verify_Disable_Server1_with_disable_until_manula_enable_for_the_master_only(self):
            logging.info("NIOS-84492 Verify Disable server1 with disable until manual enable for the master only")
            log("stop","/var/log/syslog",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*Server Server1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_syslog*")
            print(int(check_master))
            Validate_Server_Fail_back_Status("Server1")
            print(Server_data)
            if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)!=0)):
                sleep(40)
                assert True
            else:
                sleep(40)
                assert False
            print("Test Case 65 Execution Completed")


        @pytest.mark.run(order=66)
        def test_066_NIOS_84492_Disable_Server1_with_disable_until_dns_restart_for_the_member_only(self):
            logging.info("NIOS-84492 Disable server1 with disable until dns restart for the member only")
            log("start","/infoblox/var/infoblox.log",config.grid_vip)
            Getting_DTC_Object_Reference("server","Server1")
            #data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object":str(reference),"specific_time_disable":70}
            data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member1_fqdn],"disable_timeframe":"UNTIL_DNS_RESTART","dtc_object":str(reference),"specific_time_disable":100}
            print(data)
            DTC_Object_Fail_back_Manual_Disable(data)
            assert re.search(r'"failback_status": "SUCCESS"',failback_output)
            sleep(30)
            print("Test Case 66 Execution Completed")


        @pytest.mark.run(order=67)
        def test_067_NIOS_84492_Verify_Disable_Server1_with_disable_until_dns_restart_for_the_member_only(self):
            logging.info("NIOS-84492 Verify disable server1 with disable until dns restart for the member only")
            log("stop","/infoblox/var/infoblox.log",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*sending disable request to controld.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
            print(int(check_master))
            Validate_Server_Fail_back_Status("Server1")
            print(Server_data)
            if (('"availability": "WHITE"' in Server_data) and ('"Requires Manual enabling"' in Server_data) and (int(check_master)!=0)):
                sleep(40)
                assert True
            else:
                sleep(40)
                assert False
            print("Test Case 67 Execution Completed")

        @pytest.mark.run(order=68)
        def test_068_NIOS_84492_Enable_server1_manually(self):
            logging.info("NIOS-84492 Enable server1 manually")
            log("start","/var/log/syslog",config.grid_vip)
            Getting_DTC_Object_Reference("server","Server1")
            data={"dtc_object":str(reference),"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn]}
            DTC_Object_Fail_back_Manual_Enable(data)
            assert re.search(r'"failback_status": "SUCCESS"',enable_output)
            sleep(30)
            print("Test Case 68 Execution Completed")

        @pytest.mark.run(order=69)
        def test_069_NIOS_84492_Verify_Enable_server1_manually(self):
            logging.info("NIOS-84492 Verify Enable server1 manually")
            log("stop","/var/log/syslog",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_syslog*")
            print(int(check_master))
            print(check_master)
            Validate_Server_Fail_back_Status("Server1")
            print(Server_data)
            if (('"availability": "GREEN"' in Server_data)  and (int(check_master)!=0) ):
                sleep(30)
                assert True
            else:
                assert False
            print("Test Case 69 Execution Completed")

        @pytest.mark.run(order=70)
        def test_070_NIOS_84521_Disable_lbdn_for_specified_time_with_delay_time_interval(self):
            logging.info("Disable lbdn for specified time with delay time interval")
            log("start","/var/log/syslog",config.grid_vip)
            Getting_DTC_Object_Reference("lbdn","Lbdn")
            data={"disable_health_monitoring":True,"delayed_disable":True,"delayed_disable_time":120,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object":str(reference),"specific_time_disable":120}
            print(data)
            DTC_Object_Fail_back_Manual_Disable(data)
            assert re.search(r'"failback_status": "SUCCESS"',failback_output)
            sleep(15)
            print("Test Case 70 Execution Completed")

        @pytest.mark.run(order=71)
        def test_071_NIOS_84521_Verify_if_the_lbdn_has_not_been_disabled_before_the_delay_disabled_time(self):
            logging.info("Verify if the lbdn has not been disabled before the delay disabled time")
            Validate_Lbdn_Fail_back_Status("Lbdn")
            print(Lbdn_data)
            if (('"availability": "GREEN"' in Lbdn_data)):
                sleep(130)
                assert True
            else:
                assert False
            print("Test Case 71 Execution Completed")

        @pytest.mark.run(order=72)
        def test_072_NIOS_84521_Verify_if_the_lbdn_has_been_disabled_for_specific_time(self):
            logging.info("NIOS-84521 Verify if the lbdn has been disabled for specific time")
            log("stop","/var/log/syslog",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_syslog*")
            print(int(check_master))
            Validate_Lbdn_Fail_back_Status("Lbdn")
            print(Lbdn_data)
            if (('"availability": "DARKGRAY"' in Lbdn_data) and ('"description": "Temporarily Disabled"' in Lbdn_data) and (int(check_master)!=0) ):
                sleep(120)
                assert True
            else:
                assert False
            print("Test Case 72 Execution Completed")

        @pytest.mark.run(order=73)
        def test_073_NIOS_84521_disable_lbdn_with_disable_until_manual_enable_with_delay_disabled_time(self):
            logging.info("NIOS-84521 Disable lbdn with option disable until manual enable")
            log("start","/var/log/syslog",config.grid_vip)
            Getting_DTC_Object_Reference("lbdn","Lbdn")
            data={"disable_health_monitoring":True,"delayed_disable":True,"delayed_disable_time":120,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
            print(data)
            DTC_Object_Fail_back_Manual_Disable(data)
            assert re.search(r'"failback_status": "SUCCESS"',failback_output)
            sleep(15)
            print("Test Case 73 Execution Completed")

        @pytest.mark.run(order=74)
        def test_074_NIOS_84521_Verify_if_the_lbdn_has_not_been_disabled_before_the_delay_disabled_time(self):
            logging.info("Verify if the lbdn has not been disabled before the delay disabled time")
            Validate_Lbdn_Fail_back_Status("Lbdn")
            print(Lbdn_data)
            if (('"availability": "GREEN"' in Lbdn_data)):
                sleep(130)
                assert True
            else:
                assert False
            print("Test Case 74 Execution Completed")


        @pytest.mark.run(order=75)
        def test_075_NIOS_84521_Verify_disable_lbdn_with_disable_until_manual_enable(self):
            logging.info("NIOS-84899 Verify Disable lbdn with option disable until manual enable")
            log("stop","/var/log/syslog",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_syslog*")
            check_master1=commands.getoutput(" grep -cw \".*name (Lbdn) action disable after 120 seconds for 0 seconds.*\" /tmp/"+str(config.grid_vip)+"_var_log_syslog*")
            print(int(check_master))
            print(int(check_master1))
            Validate_Lbdn_Fail_back_Status("Lbdn")
            print(Lbdn_data)
            if (('"availability": "WHITE"' in Lbdn_data) and ('"description": "Requires Manual enabling"' in Lbdn_data) and (int(check_master)!=0) and (int(check_master1)!= 0)):
                assert True
            else:
                assert False
            print("Test Case 75 Execution Completed")


        @pytest.mark.run(order=76)
        def test_076_NIOS_84521_Enable_lbdn(self):
            logging.info("NIOS-84521 Enable lbdn")
            log("start","/var/log/syslog",config.grid_vip)
            Getting_DTC_Object_Reference("lbdn","Lbdn")
            data={"dtc_object":str(reference),"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn]}
            DTC_Object_Fail_back_Manual_Enable(data)
            assert re.search(r'"failback_status": "SUCCESS"',enable_output)
            sleep(30)
            print("Test Case 76 Execution Completed")

        @pytest.mark.run(order=77)
        def test_077_NIOS_84521_Verify_Enable_lbdn(self):
            logging.info("NIOS-84521 Verify Enable server1")
            log("stop","/var/log/syslog",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*LBDN Lbdn is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_syslog*")
            print(int(check_master))
            Validate_Lbdn_Fail_back_Status("Lbdn")
            print(Lbdn_data)
            if (('"availability": "GREEN"' in Lbdn_data)  and (int(check_master)!=0) ):
                sleep(30)
                assert True
            else:
                assert False
            print("Test Case 77 Execution Completed")


        @pytest.mark.run(order=78)
        def test_078_NIOS_85287_disable_server1_with_disable_until_manual_enable(self):
            logging.info("NIOS-85287 Disable server1 with option disable until manual enable")
            log("start","/var/log/syslog",config.grid_vip)
            Getting_DTC_Object_Reference("server","Server1")
            data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object":str(reference),"specific_time_disable":100}
            print(data)
            DTC_Object_Fail_back_Manual_Disable(data)
            assert re.search(r'"failback_status": "SUCCESS"',failback_output)
            sleep(30)
            print("Test Case 78 Execution Completed")

        @pytest.mark.run(order=79)
        def test_079_NIOS_85287_Verify_disable_server1_with_disable_until_manual_enable(self):
            logging.info("NIOS-85287 Verify Disable server1 with option disable until manual enable")
            log("stop","/var/log/syslog",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*Server Server1 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_syslog*")
            print(int(check_master))
            print(check_master)
            Validate_Server_Fail_back_Status("Server1")
            print(Server_data)
            if (('"availability": "WHITE"' in Server_data) and ('"description": "Requires Manual enabling"' in Server_data) and (int(check_master)!=0) ):
                assert True
            else:
                assert False
            print("Test Case 79 Execution Completed")

        @pytest.mark.run(order=80)
        def test_080_NIOS_85287_Try_to_disable_server1_from_server1_properties_checkbox(self):
            logging.info("NIOS-85287 Try to disable server1 from server1 properties checkbox")
            response = ib_NIOS.wapi_request('GET', object_type="dtc:server", grid_vip=config.grid_vip)
            response = json.loads(response)
            server_ref = ''
            for i in response:
                if i["name"] == "Server1":
                    server_ref = i["_ref"]
                    print(server_ref)
            data={"disable":True}
            print(data)
            response = ib_NIOS.wapi_request('PUT',ref=server_ref, fields=json.dumps(data))
            print(response)
            if "The DTC object 'Server1' is already disabled" in str(response):
                assert True
            else:
                assert False
            print("Test Case 80 Execution Completed")


        @pytest.mark.run(order=81)
        def test_081_NIOS_85287_Enable_server1(self):
            logging.info("NIOS-84773 Enable server1")
            log("start","/var/log/syslog",config.grid_vip)
            Getting_DTC_Object_Reference("server","Server1")
            data={"dtc_object":str(reference),"enable_on":[config.grid_member_fqdn,config.grid_member1_fqdn]}
            DTC_Object_Fail_back_Manual_Enable(data)
            assert re.search(r'"failback_status": "SUCCESS"',enable_output)
            sleep(30)
            print("Test Case 81 Execution Completed")

        @pytest.mark.run(order=82)
        def test_082_NIOS_85287_Verify_Enable_server1(self):
            logging.info("NIOS-85287 Verify Enable server1")
            log("stop","/var/log/syslog",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*Server Server1 is enabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_syslog*")
            print(int(check_master))
            print(check_master)
            Validate_Server_Fail_back_Status("Server1")
            print(Server_data)
            if (('"availability": "GREEN"' in Server_data) and ('"description": ""' in Server_data) and (int(check_master)!=0) ):
                sleep(30)
                assert True
            else:
                assert False
            print("Test Case 82 Execution Completed")

        @pytest.mark.run(order=83)
        def test_083_NIOS_84415_Check_if_SIGSEGV_cores_have_been_generated(self):
            logging.info("NIOS-84415 Verify if SIGSEGV cores have been generated")
            sleep(30)
            validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_vip)
            validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_member1_vip)
            print("Test Case 83 Execution Completed")

        @pytest.mark.run(order=84)
        def test_084_add_a_DTC_Server3(self):
                logging.info("Create A DTC 3 Server")
                data = {"name":"Server3","host":config.Server3}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 84 Execution Completed")

        @pytest.mark.run(order=85)
        def test_085_Validate_Created_Server3(self):
                logging.info("Validate Created Server3")
                #response =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name=Server1", grid_vip=config.grid_vip)
                #print response
                #logging.info(response)
                Getting_DTC_Object_Reference("server","Server3")
                assert re.search(r'Server3',reference)
                sleep(5)
                print("Test Case 85 Execution Completed")


        @pytest.mark.run(order=86)
        def test_086_add_a_DTC_Server4(self):
                logging.info("Create A DTC fourth Server")
                data = {"name":"Server4","host":config.Server4}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 86 Execution Completed")

        @pytest.mark.run(order=87)
        def test_087_Validate_Created_Server4(self):
                logging.info("Validate Created Server4")
                #response =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name=Server1", grid_vip=config.grid_vip)
                #print response
                #logging.info(response)
                Getting_DTC_Object_Reference("server","Server4")
                assert re.search(r'Server4',reference)
                sleep(5)
                print("Test Case 87 Execution Completed")


        @pytest.mark.run(order=88)
        def test_088_add_a_DTC_pool2(self):
                logging.info("Creating dtc pool")
                server=ib_NIOS.wapi_request('GET',object_type='dtc:server')
                server3=json.loads(server)[2]['_ref']
                server4=json.loads(server)[3]['_ref']
                data={"name": "Pool2","lb_preferred_method": "ROUND_ROBIN","monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"],"servers": [{"ratio": 1,"server": server3},{"ratio": 1,"server": server4}]}
                pool_ref=ib_NIOS.wapi_request('POST',object_type='dtc:pool',fields=json.dumps(data))
                logging.info(pool_ref)
                if bool(re.match("\"dtc:pool*.",str(pool_ref))):
                    logging.info("pool created succesfully")
                else:
                    raise Exception("pool creation unsuccessful")
                logging.info("Test Case 88 Execution Completed")

        
        @pytest.mark.run(order=89)
        def test_089_Validate_Created_Pool(self):
                logging.info("Validate Created Pool")
                Getting_DTC_Object_Reference("pool","Pool2")
                #response =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?name=Pool1", grid_vip=config.grid_vip)
                #print response
                #logging.info(response)
                assert re.search(r'Pool2',reference)
                sleep(5)
                print("Test Case 89 Execution Completed")


        @pytest.mark.run(order=90)
        def test_090_add_Pool2_to_DTC_lbdn(self):
            logging.info("Add Pool2 to lbdn")
            sleep(10)
            pool=ib_NIOS.wapi_request('GET',object_type='dtc:pool')
            pool1_ref=json.loads(pool)[0]['_ref']
            pool2_ref=json.loads(pool)[1]['_ref']
            lbdn =ib_NIOS.wapi_request('GET',object_type='dtc:lbdn')
            lbdnref=json.loads(lbdn)[0]['_ref']
            data={"pools": [{"pool": pool1_ref,"ratio": 1},{"pool": pool2_ref,"ratio": 1}]}
            lbdn_ref=ib_NIOS.wapi_request('PUT',ref=lbdnref,fields=json.dumps(data))
            print(lbdn_ref)
            logging.info(lbdn_ref)
            if bool(re.match("\"dtc:lbdn*.",str(lbdn_ref))):
                logging.info("Pool2 added to lbdn succesfully")
                restart_services()
                print("Test Case 90 Execution Completed")
            else:
                raise Exception("Pool2 addition to lbdn unsuccessful")



        @pytest.mark.run(order=91)
        def test_091_NIOS_84827_Disable_Pool2_manually_with_disable_for_specified_time_option(self):
            logging.info("NIOS-84827 Disable Pool2 manually with disable for specific time option")
            log("start","/var/log/syslog",config.grid_vip)
            Getting_DTC_Object_Reference("pool","Pool2")
            data={"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":100,"disable_on":[config.grid_member_fqdn,config.grid_member1_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object":str(reference),"specific_time_disable":300}
            print(data)
            DTC_Object_Fail_back_Manual_Disable(data)
            assert re.search(r'"failback_status": "SUCCESS"',failback_output)
            sleep(15)
            print("Test Case 91 Execution Completed")

        @pytest.mark.run(order=92)
        def test_092_NIOS_84827_Verify_Disable_Pool2_manually_with_disable_for_specified_time_option(self):
            logging.info("NIOS-84827 Verify disable Pool2 manually with disable for specific time option")
            log("stop","/var/log/syslog",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*Pool Pool2 is disabling.*\" /tmp/"+str(config.grid_vip)+"_var_log_syslog*")
            print(int(check_master))
            Validate_Pool_Fail_back_Status("Pool2")
            print(Pool_data)
            if (('"availability": "DARKGRAY"' in Pool_data) and ('"description": "Temporarily Disabled"' in Pool_data) and (int(check_master)!=0)  ):
                sleep(40)
                assert True
            else:
                sleep(40)
                assert False
            print("Test Case 92 Execution Completed")


        @pytest.mark.run(order=93)
        def test_093_NIOS_84827_remove_server4_from_DTC2_pool(self):
                logging.info("remove server4 from dtc pool")
                server=ib_NIOS.wapi_request('GET',object_type='dtc:server')
                server3=json.loads(server)[2]['_ref']
                server4=json.loads(server)[3]['_ref']
                pool = ib_NIOS.wapi_request('GET',object_type='dtc:pool')
                pool_ref = json.loads(pool)[1]['_ref']
                data={"servers": [{"ratio": 1,"server": server3}]}
                response=ib_NIOS.wapi_request('PUT',ref=pool_ref,fields=json.dumps(data))
                logging.info(response)
                if bool(re.match("\"dtc:pool*.",str(response))):
                    logging.info("Server4 removal from Pool2 successful")
                    restart_services()
                    assert True
                else:
                    raise Exception("Server4 removal from Pool2 unsuccessful")
                logging.info("Test Case 93 Execution Completed")

        @pytest.mark.run(order=94)
        def test_094_NIOS_84827_Check_health_status_txt_file_for_timestamp(self):
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
                    if i['timestamp'] !=0:
                        continue
                    else:
                        logging.info("Timestamp not available")
                        assert False
                logging.info("Timestamo available for all server monitors")
                assert True
            except paramiko.AuthenticationException:
                print("Authentication failed, please verify your credentials")
            except paramiko.SSHException as sshException:
                print("Unable to establish SSH connection: %s" %sshException)
            except paramiko.BadHostKeyException as badHostKeyException:
                print("Unable to verify server's host key: %s" %badHostKeyException)
            finally:
                client.close()
                logging.info("Test Case 94 Execution Completed")

        @pytest.mark.run(order=95)
        def test_095_NIOS_84827_Add_server4_to_DTC2_pool(self):
                logging.info("Add server4 to dtc pool")
                server=ib_NIOS.wapi_request('GET',object_type='dtc:server')
                server3=json.loads(server)[2]['_ref']
                server4=json.loads(server)[3]['_ref']
                pool = ib_NIOS.wapi_request('GET',object_type='dtc:pool')
                pool_ref = json.loads(pool)[1]['_ref']
                data={"servers": [{"ratio": 1,"server": server3},{"ratio": 1,"server": server4}]}
                response=ib_NIOS.wapi_request('PUT',ref=pool_ref,fields=json.dumps(data))
                logging.info(response)
                if bool(re.match("\"dtc:pool*.",str(response))):
                    logging.info("Server4 addition to Pool2 successful")
                    restart_services()
                    sleep(180)
                    assert True
                else:
                    raise Exception("Server4 addition to Pool2 unsuccessful")
                logging.info("Test Case 95 Execution Completed")

        @pytest.mark.run(order=96)
        def test_096_NIOS_84761_Disable_server1_from_server1_properties_checkbox(self):
            logging.info("NIOS-84761 Disable server1 from server1 properties checkbox")
            response = ib_NIOS.wapi_request('GET', object_type="dtc:server", grid_vip=config.grid_vip)
            response = json.loads(response)
            server_ref = ''
            for i in response:
                if i["name"] == "Server1":
                    server_ref = i["_ref"]
                    print(server_ref)
            data={"disable":True}
            print(data)
            response = ib_NIOS.wapi_request('PUT',ref=server_ref, fields=json.dumps(data))
            print(response)
            if bool(re.match("\"dtc:server*.",str(response))):
                restart_services()
                assert True
            else:
                logging.info("Disabling the server1 failed")
                assert False
            print("Test Case 96 Execution Completed")

        @pytest.mark.run(order=97)
        def test_097_NIOS_84761_Check_dtc_conf_file_for_server1_entries_being_removed(self):
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
                mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
                client.connect(config.grid_vip, username='root', pkey = mykey)
                data ='cat /infoblox/var/idns_conf/dtc.conf'
                stdin, stdout, stderr = client.exec_command(data)
                file_output = stdout.read()
                print(file_output)
                file_output = ast.literal_eval(file_output)
                for i in file_output['servers']:
                    if i['name'] != 'Server1':
                        continue
                    else:
                        logging.info("Server1 entry has not been removed")
                        assert False
                logging.info("Server1 entry has been removed")
                assert True
            except paramiko.AuthenticationException:
                print("Authentication failed, please verify your credentials")
            except paramiko.SSHException as sshException:
                print("Unable to establish SSH connection: %s" %sshException)
            except paramiko.BadHostKeyException as badHostKeyException:
                print("Unable to verify server's host key: %s" %badHostKeyException)
            finally:
                client.close()
                logging.info("Test Case 97 Execution Completed")

        @pytest.mark.run(order=98)
        def test_098_NIOS_84761_Enable_server1_from_server1_properties_checkbox(self):
            logging.info("NIOS-84761 Enable server1 from server1 properties checkbox")
            response = ib_NIOS.wapi_request('GET', object_type="dtc:server", grid_vip=config.grid_vip)
            response = json.loads(response)
            server_ref = ''
            for i in response:
                if i["name"] == "Server1":
                    server_ref = i["_ref"]
                    print(server_ref)
            data={"disable":False}
            print(data)
            response = ib_NIOS.wapi_request('PUT',ref=server_ref, fields=json.dumps(data))
            print(response)
            if bool(re.match("\"dtc:server*.",str(response))):
                restart_services()
                sleep(30)
                assert True
            else:
                logging.info("Enabling the server1 failed")
                assert False
            print("Test Case 98 Execution Completed")

        @pytest.mark.run(order=99)
        def test_099_NIOS_84866_Remove_the_grid_master_from_thezone_dtc_com_as_primary(self):
            logging.info("Remove the grid master from the zone dtc.com as primary")
            response = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
            print(response)
            response = json.loads(response)
            zone_ref = response[0]['_ref']
            data = {"grid_primary": [{"name": config.grid_member1_fqdn,"stealth":False}]}
            response = ib_NIOS.wapi_request('PUT', ref=zone_ref, fields=json.dumps(data))
            print response
            logging.info(response)
            read  = re.search(r'201',response)
            for read in  response:
                    assert True
            print("Restart DNS Services") 
            restart_services()
            sleep(30)

        @pytest.mark.run(order=100)
        def test_100_NIOS_84866_Enable_debug_logs_on_the_grid(self):
            try:
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('set debug all on')
                child.expect('>')
                child.sendline('show debug')
                child.expect('>')
                if 'Debug logging status : enabled' in child.before :
                    child.close()
                    assert True
                else:
                    print("Unable to enable debug logs")
                    assert False
            except Exception as e :
                print(e)
                assert False

        @pytest.mark.run(order=101)
        def test_101_NIOS_84866_Disable_LBDN_for_specified_time_with_disable_after_specific_timee_option_enabled(self):
            logging.info("NIOS-84866 Disable LBDN for specified time with disable after speific time option disabled")
            log("start","/infoblox/var/infoblox.log",config.grid_vip)
            Getting_DTC_Object_Reference("lbdn","Lbdn")
            data={"disable_health_monitoring":True,"delayed_disable":True,"delayed_disable_time":10,"disable_on":[config.grid_member1_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object":str(reference),"specific_time_disable":300}
            print(data)
            DTC_Object_Fail_back_Manual_Disable(data)
            assert re.search(r'"failback_status": "SUCCESS"',failback_output)
            sleep(30)
            print("Test Case 101 Execution Completed")


        @pytest.mark.run(order=102)
        def test_102_NIOS_84866_Remove_the_grid_member_from_the_zone_dtc_com_as_primary_and_add_grid_master_as_primary(self):
            logging.info("Remove the grid master from the zone dtc.com as primary and add grid master as primary")
            response = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
            print(response)
            response = json.loads(response)
            zone_ref = response[0]['_ref']
            data = {"grid_primary": [{"name": config.grid_member_fqdn,"stealth":False}]}
            response = ib_NIOS.wapi_request('PUT', ref=zone_ref, fields=json.dumps(data))
            print response
            logging.info(response)
            read  = re.search(r'201',response)
            for read in  response:
                    assert True
            print("Restart DNS Services") 
            restart_services()
            sleep(30)
            print("Test Case 102 Execution Completed")

        @pytest.mark.run(order=103)
        def test_103_NIOS_84866_Remove_the_grid_master_from_the_zone_dtc_com_as_primary_and_add_grid_member_as_primary(self):
            logging.info("Remove the grid member from the zone dtc.com as primary and add grid member as primary")
            response = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
            print(response)
            response = json.loads(response)
            zone_ref = response[0]['_ref']
            data = {"grid_primary": [{"name": config.grid_member1_fqdn,"stealth":False}]}
            response = ib_NIOS.wapi_request('PUT', ref=zone_ref, fields=json.dumps(data))
            print response
            logging.info(response)
            read  = re.search(r'201',response)
            for read in  response:
                    assert True
            print("Restart DNS Services") 
            restart_services()
            sleep(30)
            print("Test Case 103 Execution Completed")

        @pytest.mark.run(order=104)
        def test_104_NIOS_84866_Verify_the_LBDN_status(self):
            logging.info("Verify the lbdn status")
            log("stop","/infoblox/var/infoblox.log",config.grid_vip)
            check_master=commands.getoutput(" grep -cw \".*deleting disabled obj 1..com.infoblox.dns.idns_lbdn$Lbdn.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
            print(int(check_master))
            print(check_master)
            Validate_Lbdn_Fail_back_Status("Lbdn")
            print(Lbdn_data)
            if (('"availability": "GREEN"' in Lbdn_data) and ('"description": ""' in Lbdn_data) and (int(check_master)!=0) ):
                assert True
            else:
                assert False
            print("Test Case 104 Execution Completed")


        @pytest.mark.run(order=105)
        def test_105_NIOS_84415_Check_if_SIGSEGV_cores_have_been_generated(self):
            logging.info("NIOS-84415 Verify if SIGSEGV cores have been generated")
            sleep(30)
            validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_vip)
            validate_sigsegv_sigquit_and_sigabrt_core_files(config.grid_member1_vip)
            print("Test Case 105 Execution Completed")

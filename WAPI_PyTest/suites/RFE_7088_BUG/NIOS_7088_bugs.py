__author__ = "Shivasai B"
__email__  = "sbandaru@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master + Member                                                             #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415),DTC                                  #
########################################################################################

import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
import commands
import json, ast
import time
import getpass
import sys
import pexpect
import paramiko
from paramiko import client
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv



logging.basicConfig(filename='nios-7088-bugs.log', filemode='w', level=logging.DEBUG)
global Server1
global Server2
global Pool
global Lbdn
global zone
global failback_output


def restart_services():
    print("Service restart start")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
    ref = json.loads(grid)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
    sleep(30)
    print("Service restart Done")

def restart_services_IF_NEEDED():
    print("Service restart start")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
    ref = json.loads(grid)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"RESTART_IF_NEEDED","service_option": "ALL"}
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
    sleep(40)
    print("Service restart Done")


def DTC_Object_Fail_back_Manual_Disable(data):
    response = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data),params="?_function=dtc_object_disable")
    failback_output = str(response)
    failback_output=failback_output.replace('\n','').replace('{','').replace('}','').replace(']','').replace('[','').replace('\\','').replace("'",'')
    return failback_output
    print("Server Failback completed")



def DTC_Object_Fail_back_Manual_Enable(data):
    response = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data),params="?_function=dtc_object_enable")
    enable_output = str(response)
    return enable_output
    print("Server Enable completed")


def DTC_Object_Fail_back_GET_State(object_type,object_name):
    ref =  ib_NIOS.wapi_request('GET', object_type="dtc:"+object_type+"?name="+object_name, grid_vip=config.grid_vip)
    res = json.loads(ref)
    reference = json.loads(ref)[0]['_ref']
    print(reference)
    data={"dtc_object":str(reference)}
    response = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data),params="?_function=dtc_get_object_grid_state")
    state_output=json.loads(response)
    state_output=eval(json.dumps(state_output))
    return state_output




class RFE_7088(unittest.TestCase):

    @pytest.mark.order(order=1)
    def test_001_create_zone_NIOS_84908(self):
        """
        Create zone dtcbug.com
        """
        global zone
        data = {"fqdn": "dtcbug.com",
                "view":"default",
                "grid_primary": [
                    {
                        "name": config.grid_fqdn,
                        "stealth": False
                    },
                    {
                        "name": config.grid_member1_fqdn, 
                        "stealth": False
                    }
                    ]
                }
        zone = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        zone=json.loads(zone)
        print(zone)
        restart_services()
        if type(zone)  == tuple:
            if zone[0] == 400 or zone[0] == 401:
                assert False
        else:
            assert True
            
    
    @pytest.mark.order(order=2)
    def test_002_create_servers_NIOS_84908(self):
        """
        Create Server1 and Server2
        """
        global Server1
        global Server2
        data={"host": config.Server1,"name": "server1ss"}
        server1_ref=ib_NIOS.wapi_request('POST',object_type='dtc:server',fields=json.dumps(data))
        print(server1_ref)
        data={"host": config.Server2,"name": "server2ss"}
        server2_ref=ib_NIOS.wapi_request('POST',object_type='dtc:server',fields=json.dumps(data))
        print(server2_ref)
        
        Server1 = json.loads(server1_ref)
        Server2 = json.loads(server2_ref)
        if type(server1_ref) == tuple:
            if server1_ref[0]==400 or server1_ref[0]==401:
                assert False
        
        if type(server2_ref) == tuple:
            if server2_ref[0]==400 or server2_ref[0]==401:
                assert False
            else:
                assert True
                print("server1 and server2 are created successfully")
    
    
    @pytest.mark.order(order=3)
    def test_003_create_POOL_LBDN_NIOS_84908(self):
        """
        Create Pool and LBDN
        """
        global Server1
        global Server2
        global zone
        global Pool
        global Lbdn
        print(Server1,Server2)
        data={"name": "pool","lb_preferred_method": "ROUND_ROBIN","servers": [{"ratio": 1,"server": Server1},{"ratio": 1,"server": Server2}],"monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
        pool_ref=ib_NIOS.wapi_request('POST',object_type='dtc:pool',fields=json.dumps(data))
        print(pool_ref)
        Pool = json.loads(pool_ref)
        data={"name": "lbdn","lb_method": "ROUND_ROBIN","patterns": ["*.dtcbug.com"],"auth_zones": [zone],"pools": [{"pool": Pool,"ratio": 1}]}
        lbdn_ref=ib_NIOS.wapi_request('POST',object_type='dtc:lbdn',fields=json.dumps(data))
        sleep(10)
        restart_services()
        Lbdn = json.loads(lbdn_ref)
        print(Lbdn)
        if type(pool_ref) == tuple:
            if pool_ref[0]==400 or pool_ref[0]==401:
                assert False
        
        if type(lbdn_ref) == tuple:
            if lbdn_ref[0]==400 or lbdn_ref[0]==401:
                assert False
            else:
                assert True
                print("server1 and server2 are created successfully")

        
    @pytest.mark.order(order=4)
    def test_004_Disable_server2_for_4294967295seconds_NIOS_84908(self):
        """
        Disable server 2 for 4294967295 seconds
        """
        global Server2
        pool = "dtc:pool/ZG5zLmlkbnNfcG9vbCRwb29s:pool"
        Server1 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjFzcw:server1ss"
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        data = {"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":4294967295,"disable_on":[config.grid_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object": Server2,"specific_time_disable":4}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        if "Delayed disable time value must be between 1 and 31536000 seconds" not in output:
            assert False
        else:
            print("Seeing proper error message", output)
        data = {"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":4,"disable_on":[config.grid_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object": Server2,"specific_time_disable":4294967295}
        output1 = DTC_Object_Fail_back_Manual_Disable(data)
        sleep(45)
        print(output1)
        if "Specific time disable value must be between 1 and 31536000 seconds" in output1:
            assert True
            print("\n Seeing proper error message 'Delayed disable time value must be between 1 and 31536000 seconds'")
        else:
            assert False            
        
        
    @pytest.mark.order(order=5)
    def test_005_Disable_server2_delete_server1_from_pool_NIOS_84751(self):
        """
        Disable server2 and delete server1 from pool should through error
        """
        global Server1
        global Server2
        global Pool
        Pool = "dtc:pool/ZG5zLmlkbnNfcG9vbCRwb29s:pool"
        Server1 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjFzcw:server1ss"
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        data = {"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":4,"disable_on":[config.grid_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object": Server2,"specific_time_disable":4}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        if "SUCCESS" not in output:
            assert False
            
        sleep(15)
        data={"name": "pool","lb_preferred_method": "ROUND_ROBIN","servers": [{"ratio": 1,"server": Server2}],"monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
        pool_ref=ib_NIOS.wapi_request('PUT',object_type=Pool,fields=json.dumps(data))
        print(pool_ref)
        
        if """Cannot remove server \'server1ss\' from pool \'pool\' because it is used by LBDN \'lbdn\' and no enabled server remains in the pool""" in pool_ref[1]:
            assert True
            print("Seeing proper error when we try to have only disabled servers in pool")
        else:
            assert False
        
    @pytest.mark.order(order=6)
    def test_006_revert_NIOS_84751_changes(self):
        """
        Enable server2 
        pool = "dtc:pool/ZG5zLmlkbnNfcG9vbCRwb29s:pool"
        Server1 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjFzcw:server1ss"
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        """ 
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        global Server2
        data = {"dtc_object": Server2,"enable_on":[config.grid_fqdn]}
        output = DTC_Object_Fail_back_Manual_Enable(data)
        print(output)
        if "SUCCESS" not in output:
            assert False
        else:
            assert True
            print("Reverted NIOS-84751 changes")
            
    @pytest.mark.order(order=7)
    def test_007_Specific_time_disable_with_value_as_0_NIOS_84433(self):
        """
        Disable server 2 with specific_time_disable value as 0, should fail
        """
        global Server2
        data = {"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":4,"disable_on":[config.grid_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object": Server2,"specific_time_disable":0}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        if "Specific time disable value must be between 1 and 31536000 seconds" in output:
            assert True
            print("Specific_time_disable is not accepting 0")
        
        else:
            assert False
            
    @pytest.mark.order(order=8)
    def test_008_Disable_server_and_check_wapi_output_and_get_status_NIOS_84367_and_NIOS_84425(self):
        """
        Disable server 2 and check WAPI output
        """
        global Server2
        data = {"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":4,"disable_on":[config.grid_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object": Server2,"specific_time_disable":120}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        if "SUCCESS" not in output:
            assert False
            
        state_output = DTC_Object_Fail_back_GET_State("server","server2ss")
        print(state_output)
        disabled=state_output.get('disabled_on')
        enabled=state_output.get('enabled_on')
        print(enabled,disabled)
        if ((config.grid_fqdn in disabled) and (config.grid_member1_fqdn in enabled)):
            assert True
            print("getting proper status with wapi")
        else:
            assert False
    
 
    @pytest.mark.order(order=10)
    def test_009_revert_changes_NIOS_84367(self):
        """
        Enable server 2 and check WAPI output
        """   
        global Server2
        data = {"dtc_object": Server2,"enable_on":[config.grid_fqdn]}
        output = DTC_Object_Fail_back_Manual_Enable(data)
        sleep(30)
        print(output)
        if "SUCCESS" not in output:
            assert False
        else:
            assert True
            print("Reverted NIOS-84751 changes")
            
    
    
    @pytest.mark.order(order=10)
    def test_010_Disable_server_on_master_NIOS_84314(self):
        """
        Disable server_on_master
        """
        global Server2
        log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
        data = {"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":4,"disable_on":[config.grid_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object": Server2,"specific_time_disable":120}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        if "SUCCESS" not in output:
            assert False 
        
        else:
            assert True
            
    @pytest.mark.order(order=11)
    def test_011_enable_server_on_master_and_check_logs_on_member1NIOS_84314(self):
        """
        Enable server on master and check for logs in meber
        """
        global Server2
        data = {"dtc_object": Server2,"enable_on":[config.grid_fqdn]}
        output = DTC_Object_Fail_back_Manual_Enable(data)
        print(output)
        if "SUCCESS" not in output:
            assert False
        
        sleep(10)
        log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
        
        LookFor="sending enable request to controld"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_member1_vip)
        print(logs)
        
        if logs == None:
            assert True
        else:
            assert False
            print("Error : server is enabling on member1 even it is already enabled")
            
    @pytest.mark.order(order=12)
    def test_012_delayed_disable_should_not_accept_0_NIOS_84797(self):
        """
        "delayed_disable_time" wapi object should not accept value "0"
        """
        global Server2
        data = {"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":0,"disable_on":[config.grid_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object": Server2,"specific_time_disable":120}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        if "Delayed disable time value must be between 1 and 31536000 seconds" not in output:
            assert False 
        else:
            assert True
            print("delayed_disable_time wapi object not accepting value as 0")
            
            
    @pytest.mark.order(order=13)
    def test_013_disable_server2_NIOS_84258(self):
        """
        disable server2 with until manual enabling
        """
        global Server2
        data = {"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":10,"disable_on":[config.grid_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object": Server2,"specific_time_disable":120}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        sleep(15)
        if "SUCCESS" not in output:
            assert False
        else:
            assert True
            print("Successfully disabled server2")
        
            
    @pytest.mark.order(order=14)
    def test_014_Force_restart_grid_and_check_logs_NIOS_84258(self):
        """
        "Post DNS restart adding failback events" logs should be seen After Force restart performed on grid
        """
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        restart_services()
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        LookFor="Post DNS restart adding failback events"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        print(logs)
        
        if logs == None:
            assert False
            print("Post DNS restart adding failback events log not seen After Force restart performed on grid")
        
        else:
            assert True
            print("Post DNS restart adding failback events logs seen After Force restart performed on grid")
    
    
    @pytest.mark.order(order=15)
    def test_015_disable_pool_NIOS_84260(self):
        """
        disable pool and disable should be failed
        """
        global Pool
        #Pool = "dtc:pool/ZG5zLmlkbnNfcG9vbCRwb29s:pool"
        data = {"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":10,"disable_on":[config.grid_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object": Pool,"specific_time_disable":120}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        sleep(15)
        if "Cannot disable all the pools in an LBDN" in output:
            assert True
            print("Won't be able to disable all the Servers/Pool")
        else:
            assert False
            
    
    
    @pytest.mark.order(order=16)
    def test_016_revert_changes_NIOS_84260(self):
        """
        Enable server2
        """   
        global Server2
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        data = {"dtc_object": Server2,"enable_on":[config.grid_fqdn]}
        output = DTC_Object_Fail_back_Manual_Enable(data)
        print(output)
        sleep(15)
        if "SUCCESS" not in output:
            assert False
        else:
            assert True
            print("Reverted NIOS-84260 changes" ) 
            
    
    
    
    @pytest.mark.order(order=17)
    def test_017_remove_server1_from_pool_NIOS_84953(self):
        """
        Remove server1 from pool
        """
        global Pool
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        Pool = "dtc:pool/ZG5zLmlkbnNfcG9vbCRwb29s:pool"
        sleep(15)
        data={"name": "pool","lb_preferred_method": "ROUND_ROBIN","servers": [{"ratio": 1,"server": Server2}],"monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
        pool_ref=ib_NIOS.wapi_request('PUT',object_type=Pool,fields=json.dumps(data))
        print(pool_ref)       
        
        restart_services()
        if type(pool_ref)  == tuple:
            if pool_ref[0] == 400 or pool_ref[0] == 401:
                assert False
        else:
            assert True
    
    @pytest.mark.order(order=18)
    def test_018_add_server1_to_pool_NIOS_84953(self):
        """
        Add server1 to pool and dont perform restart service
        Pool = "dtc:pool/ZG5zLmlkbnNfcG9vbCRwb29s:pool"
        Server1 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjFzcw:server1ss"
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        """
        global Server1
        global Server2
        global Pool
        Server1 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjFzcw:server1ss"
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        Pool = "dtc:pool/ZG5zLmlkbnNfcG9vbCRwb29s:pool"
        
        data={"name": "pool","lb_preferred_method": "ROUND_ROBIN","servers": [{"ratio": 1,"server": Server1},{"ratio": 1,"server": Server2}],"monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"]}
        pool_ref=ib_NIOS.wapi_request('PUT',object_type=Pool,fields=json.dumps(data))
        print(pool_ref)  
        
        sleep(10)
        
    @pytest.mark.order(order=19)
    def test_019_disable_server1_NIOS_84953(self):
        """
        disable server1 with until manual enabling and we should get 'Failure while communicating the message with the grid member OID '0': general failure'
        """
        global Server1
        Server1 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjFzcw:server1ss"
        data = {"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":10,"disable_on":[config.grid_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object": Server1,"specific_time_disable":120}
        try:
            output = DTC_Object_Fail_back_Manual_Disable(data)
            if "SUCCESS" in output:
                assert False
        except Exception as error:
            error = str(error)
            print(error)
            if "Failure while communicating the message with the grid member OID" in error:
                assert True
                print("Seeing proper error message when we try to disbale server in unknown state")
                
                
    
    @pytest.mark.order(order=20)
    def test_020_revert_changes_NIOS_84953(self):
        """
        Restart service and server1 should be in running state
        """       
        restart_services()
        sleep(125)
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name=server1ss&_return_fields%2B=health", grid_vip=config.grid_vip)
        ref = json.loads(ref)
        print(ref[0]["health"]["availability"])
        if ref[0]["health"]["availability"] == "GREEN":
            assert True
        else:
            assert False
        

    @pytest.mark.order(order=21)
    def test_021_disable_server2_NIOS_83858(self):
        """
        disable server2 with until manual enabling
        """
        global Server2
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        data = {"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":10,"disable_on":[config.grid_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object": Server2,"specific_time_disable":120}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        sleep(15)
        if "SUCCESS" not in output:
            assert False
        else:
            assert True
            print("Successfully disabled server2")

    @pytest.mark.order(order=22)
    def test_022_health_status_should_not_have_special_character_NIOS_83858(self):
        """
        check status of server2, should not have "!"
        """       
        
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name=server2ss&_return_fields%2B=health", grid_vip=config.grid_vip)
        ref = json.loads(ref)
        print(ref[0]["health"]["availability"])
        if "!" in ref[0]["health"]["availability"]:      
            assert False
            print("! mark is shown in health status")
        else:
            assert True
            print("! mark is not shown in health status")
    
    
    @pytest.mark.order(order=23)
    def test_023_revert_changes_NIOS_83858(self):
        """
        Enable server2
        """   
        global Server2
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        data = {"dtc_object": Server2,"enable_on":[config.grid_fqdn]}
        output = DTC_Object_Fail_back_Manual_Enable(data)
        print(output)
        sleep(20)
        if "SUCCESS" not in output:
            assert False
        else:
            assert True
            print("Reverted NIOS-83858 changes" )  
            
    
    
    @pytest.mark.order(order=24)
    def test_024_disable_server2_NIOS_84558(self):
        """
        disable server2 with until manual enabling
        """
        global Server2
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        data = {"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":10,"disable_on":[config.grid_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object": Server2,"specific_time_disable":120}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        sleep(15)
        if "SUCCESS" not in output:
            assert False
        else:
            assert True
            print("Successfully disabled server2")
    
    
    @pytest.mark.order(order=25)
    def test_025_check_logs_during_restart_service_NIOS_84558(self):
        """
        should not see "DTC initialization: out of memory" in logs
        """
        log("start","/var/log/syslog",config.grid_vip)
        restart_services()
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor="DTC initialization: out of memory"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(logs)
        
        if logs == None:
            assert True
        else:
            assert False
            
            
            
    @pytest.mark.order(order=26)
    def test_026_revert_changes_NIOS_84558(self):
        """
        Enable server2
        """   
        global Server2
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        data = {"dtc_object": Server2,"enable_on":[config.grid_fqdn]}
        output = DTC_Object_Fail_back_Manual_Enable(data)
        print(output)
        sleep(20)
        if "SUCCESS" not in output:
            assert False
        else:
            assert True
            print("Reverted NIOS-84558 changes" )
            
            
    @pytest.mark.order(order=27)
    def test_027_disable_server2_NIOS_84294(self):
        """
        disable server2 with until manual enabling
        """
        global Server2
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        data = {"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":10,"disable_on":[config.grid_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object": Server2,"specific_time_disable":60}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        sleep(15)
        if "SUCCESS" not in output:
            assert False
        else:
            assert True
            print("Successfully disabled server2")       
    
    @pytest.mark.order(order=28)
    def test_028_check_health_status_NIOS_84294(self):
        """
        check status of server2 after force restart
        """       
        
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name=server2ss&_return_fields%2B=health", grid_vip=config.grid_vip)
        ref = json.loads(ref)
        print(ref[0]["health"]["availability"])
        if ref[0]["health"]["availability"] != "DARKGRAY":
            assert False
            print("incorrect health status")
        print("perform force restart")
        restart_services()
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name=server2ss&_return_fields%2B=health", grid_vip=config.grid_vip)
        ref = json.loads(ref)
        print(ref[0]["health"]["availability"])
        if ref[0]["health"]["availability"] != "DARKGRAY":
            assert False
            print("health status changed after force restart")
        else:
            assert True
            print("health status didnt changed after force restart")
        
            
    @pytest.mark.order(order=29)
    def test_029_revert_changes_NIOS_84294(self):
        """
        wait for sometime to get server2 enables
        """   
        global Server2
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"        
        
        sleep(60)
        
        print("wait for server to come up")
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name=server2ss&_return_fields%2B=health", grid_vip=config.grid_vip)
        ref = json.loads(ref)
        print(ref[0]["health"]["availability"])
        if ref[0]["health"]["availability"] == "GREEN":
            assert True
            print("health status changed after wait disabled for time finishes")
        else:
            assert False
            
    @pytest.mark.order(order=30)
    def test_030_disable_server2_NIOS_84928(self):
        """
        disable server2 with until manual enabling
        """
        global Server2
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        data = {"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":10,"disable_on":[config.grid_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object": Server2,"specific_time_disable":60}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        sleep(15)
        if "SUCCESS" not in output:
            assert False
        else:
            assert True
            print("Successfully disabled server2")       
    
    @pytest.mark.order(order=31)
    def test_031_disable_server2_again_NIOS_84928(self):
        """
        disable server2 with until manual enabling
        """
        global Server2
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        data = {"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":10,"disable_on":[config.grid_member1_fqdn,config.grid_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object": Server2,"specific_time_disable":70}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        output = str(output)
        sleep(15)
        if "The DTC object server2ss is already disabled" in output:
            assert True
            print("Cannot disable already disabled server")
        else:
            assert False
            
    @pytest.mark.order(order=32)
    def test_032_revert_changes_NIOS_84928(self):
        """
        wait for sometime to get server2 enables
        """   
        global Server2
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"        
        restart_services()
        sleep(90)
        
        print("wait for server to come up")
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name=server2ss&_return_fields%2B=health", grid_vip=config.grid_vip)
        ref = json.loads(ref)
        print(ref[0]["health"]["availability"])
        if ref[0]["health"]["availability"] == "GREEN":
            assert True
            print("health status changed after wait disabled for time finishes")
        else:
            assert False        
    
    
    @pytest.mark.order(order=33)
    def test_033_enable_ibap_logs_NIOS_84843(self):
        """
        enable ibap logs
        """
        global Server2
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"logging_categories":{"log_dtc_health": True,"log_dtc_gslb": True,}}
        response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
        print(response)
        sleep(20)
        if type(response)  == tuple:
            if response[0] == 400 or response[0] == 401:
                assert False
        
        else:
            assert True
    
    @pytest.mark.order(order=34)
    def test_034_start_logs_NIOS_84843(self):
        """
        check ibap logs when disable time exceeds limit
        """
        global Server2
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        log("start","/infoblox/var/ibap-active.log",config.grid_vip)
        sleep(10)
        data = {"disable_health_monitoring":False,"delayed_disable":True,"delayed_disable_time":4294967295,"disable_on":[config.grid_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object": Server2,"specific_time_disable":10}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        output = str(output)
        sleep(15)
        log("stop","/infoblox/var/ibap-active.log",config.grid_vip)
        LookFor="SystemError: Error in parsing parameterss"
        logs=logv(LookFor,"/infoblox/var/ibap-active.log",config.grid_vip)
        print(logs)
        
        if logs == None:
            assert True
            print("No ibap error logs seen")
        else:
            assert False
            print("Seeing ibap erros")
            
            
    @pytest.mark.order(order=35)
    def test_035_disable_server2_on_master_NIOS_84902(self):
        """
        disable server2 with until manual enabling
        """
        global Server2
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        data = {"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":10,"disable_on":[config.grid_fqdn],"disable_timeframe":"UNTIL_MANUAL_ENABLING","dtc_object": Server2,"specific_time_disable":60}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        sleep(15)
        if "SUCCESS" not in output:
            assert False
        else:
            assert True
            print("Successfully disabled server2") 
            
            
            
    @pytest.mark.order(order=36)
    def test_036_disable_server2_again_using_for_specified_time__on_member1_NIOS_84902(self):
        """
        disable server2 again with specific_time_disable on member1
        """
        global Server2
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        data = {"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":10,"disable_on":[config.grid_member1_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object": Server2,"specific_time_disable":60}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        output = str(output)
        sleep(15)
        
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name=server2ss&_return_fields%2B=health", grid_vip=config.grid_vip)
        ref = json.loads(ref)
        print(ref[0]["health"]["availability"])
        if ref[0]["health"]["availability"] == "WHITE":
            assert True
        else:
            assert False
    
    
    @pytest.mark.order(order=37)
    def test_037_disable_server2_again_using_until_dns_restarts_NIOS_84902(self):
        """
        disable server2 again with until_dns_restarts
        """
        global Server2
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        data = {"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":10,"disable_on":[config.grid_fqdn],"disable_timeframe":"UNTIL_DNS_RESTART","dtc_object": Server2,"specific_time_disable":60}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        output = str(output)
        sleep(15)
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name=server2ss&_return_fields%2B=health", grid_vip=config.grid_vip)
        ref = json.loads(ref)
        print(ref[0]["health"]["availability"])
        if ref[0]["health"]["availability"] == "WHITE":
            assert True
        else:
            assert False
    
    
    @pytest.mark.order(order=38)
    def test_038_revert_changes_NIOS_84902(self):
        """
        Enable server2
        """   
        global Server2
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        data = {"dtc_object": Server2,"enable_on":[config.grid_fqdn]}
        output = DTC_Object_Fail_back_Manual_Enable(data)
        print(output)
        sleep(20)
        if "SUCCESS" not in output:
            assert False
        else:
            assert True
            print("Reverted NIOS-84902 changes" )
            
    
    
            
    @pytest.mark.order(order=39)
    def test_039_disable_server2_NIOS_84396(self):
        """
        disable server2 with FOR_SPECIFIED_TIME
        """
        global Server2
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        data = {"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":10,"disable_on":[config.grid_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object": Server2,"specific_time_disable":100}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        sleep(15)
        if "SUCCESS" not in output:
            assert False
        else:
            assert True
            print("Successfully disabled server2")      
            
            
    
    @pytest.mark.order(order=40)
    def test_040_enable_server_NIOS_84396(self):
        """
        Enable server2
        """   
        global Server2
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        data = {"dtc_object": Server2,"enable_on":[config.grid_fqdn]}
        output = DTC_Object_Fail_back_Manual_Enable(data)
        print(output)
        sleep(20)
        if "SUCCESS" not in output:
            assert False
        else:
            assert True
            print("Reverted NIOS-84902 changes" )
            
    
    @pytest.mark.order(order=41)
    def test_041_enable_server_NIOS_84396(self):
        """
        check logs if we are seeing server enabling messages again
        """   
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        print("waiting to see if we see enable logs again")
        sleep(90)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        
        LookFor="sending enable request to controld"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        print(logs)
        
        if logs == None:
            assert True
            print("server enabling messages are not seen again")
        else:
            assert False
            print("sserver enabling messages are seen again")
            
    
    @pytest.mark.order(order=42)
    def test_042_disable_server2_NIOS_84271(self):
        """
        disable server2 with FOR_SPECIFIED_TIME
        """
        global Server2
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        data = {"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":10,"disable_on":[config.grid_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object": Server2,"specific_time_disable":100}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        sleep(15)
        if "SUCCESS" not in output:
            assert False
        else:
            assert True
            print("Successfully disabled server2")

    @pytest.mark.order(order=43)
    def test_043_disable_server2_again_with_another_valueNIOS_84271(self):
        """
        disable server2 with FOR_SPECIFIED_TIME with different value
        """
        global Server2
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        data = {"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":10,"disable_on":[config.grid_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object": Server2,"specific_time_disable":70}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        output = str(output)
        sleep(5)
        if "The DTC object server2ss is already disabled" in output:
            assert True
            print("Cannot modify already disabled server")
        else:
            assert False
    
    @pytest.mark.order(order=44)
    def test_044_enable_server_NIOS_84271(self):
        """
        Enable server2
        """   
        global Server2
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        data = {"dtc_object": Server2,"enable_on":[config.grid_fqdn]}
        output = DTC_Object_Fail_back_Manual_Enable(data)
        print(output)
        sleep(20)
        if "SUCCESS" not in output:
            assert False
        else:
            assert True
            print("Reverted NIOS-84271 changes" )
    
    
    @pytest.mark.order(order=45)
    def test_045_disable_lbdn_NIOS_84732(self):
        """
        disable lbdn from lndb object
        """
        global Lbdn
        Lbdn = "dtc:lbdn/ZG5zLmlkbnNfbGJkbiRsYmRu:lbdn"
        data = {"disable": True}
        lbdn_ref=ib_NIOS.wapi_request('PUT',object_type=Lbdn,fields=json.dumps(data))
        print(lbdn_ref)
        sleep(15)
        if type(lbdn_ref)  == tuple:
            if lbdn_ref[0] == 400 or lbdn_ref[0] == 401:
                assert False
        else:
            assert True
            
    

    @pytest.mark.order(order=46)
    def test_046_check_server_status_when_lbdn_is_disabled_NIOS_84732(self):
        """
        server status should be NONE when lbdn is disabled
        """       
        restart_services()
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name=server1ss&_return_fields%2B=health", grid_vip=config.grid_vip)
        ref = json.loads(ref)
        print(ref[0]["health"]["availability"])
        if ref[0]["health"]["availability"] == "NONE":
            assert True
        else:
            assert False    
            
    @pytest.mark.order(order=47)
    def test_047_disable_server2_when_lbdn_is_disabled_NIOS_84732(self):
        """
        disable server2 when lbdn is already disabled
        """
        global Server2
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        data = {"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":10,"disable_on":[config.grid_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object": Server2,"specific_time_disable":50}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        output = str(output)
        sleep(15)
        if "cannot be enabled/disabled since there are no associated enabled LBDN" in output:
            assert True
            print("Cannot modify server when it is in NONE state")
        else:
            assert False
            
    
    @pytest.mark.order(order=48)
    def test_048_revert_NIOS_84732_changes(self):
        """
        Enable LBDN 
        pool = "dtc:pool/ZG5zLmlkbnNfcG9vbCRwb29s:pool"
        Server1 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjFzcw:server1ss"
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        """ 
        global Lbdn
        Lbdn = "dtc:lbdn/ZG5zLmlkbnNfbGJkbiRsYmRu:lbdn"
        data = {"disable": False}
        lbdn_ref=ib_NIOS.wapi_request('PUT',object_type=Lbdn,fields=json.dumps(data))
        print(lbdn_ref)
        sleep(15)
        if type(lbdn_ref)  == tuple:
            if lbdn_ref[0] == 400 or lbdn_ref[0] == 401:
                assert False
        else:
            assert True
            
            
    @pytest.mark.order(order=49)
    def test_049_check_server_status_when_lbdn_is_enabled_NIOS_84732(self):
        """
        server status should be NONE when lbdn is enabled
        """       
        restart_services()
        sleep(30)
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name=server1ss&_return_fields%2B=health", grid_vip=config.grid_vip)
        ref = json.loads(ref)
        print(ref[0]["health"]["availability"])
        if ref[0]["health"]["availability"] == "GREEN":
            assert True
        else:
            assert False      
    
    @pytest.mark.order(order=50)
    def test_050_disable_server2_NIOS_84811(self):
        """
        start logs disable server2 with FOR_SPECIFIED_TIME
        """
        global Server2
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        
        log("start","/var/log/syslog",config.grid_vip)
        data = {"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":10,"disable_on":[config.grid_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object": Server2,"specific_time_disable":100}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        sleep(15)
        log("stop","/var/log/syslog",config.grid_vip)
        LookFor="will be enabled after 100 seconds with time delay of 0 Seconds"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        print(logs)
        
        if logs == None:
            print("bug is still open")
            assert False
            
        else:
            assert True
            
            
    
    @pytest.mark.order(order=51)
    def test_051_disable_lbdn_NIOS_84320(self):
        """
        disable pool and disable should be failed
        """
        global Lbdn
        Lbdn = "dtc:lbdn/ZG5zLmlkbnNfbGJkbiRsYmRu:lbdn"
        data = {"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":10,"disable_on":[config.grid_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object": Lbdn,"specific_time_disable":120}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        sleep(15)
        if "SUCCESS" not in output:
            assert False
        else:
            assert True
            print("Successfully disabled Lbdn")  
            
    
    
    
    @pytest.mark.order(order=52)
    def test_052_create_servers3_NIOS_84320(self):
        """
        Create Server3 when lbdn is in disabled
        """
        data={"host": config.Server3,"name": "server3ss"}
        server3_ref=ib_NIOS.wapi_request('POST',object_type='dtc:server',fields=json.dumps(data))
        print(server3_ref)
        restart_services()
        if type(server3_ref) == tuple:
            assert False
        else:
            assert True
            print("server3 was created successfully")
            
    @pytest.mark.run(order=53)
    def test_053_check_cores_when_lbdn_is_down_NIOS_84320(self):
        """
        Create for cores when LBDN is down and we add new server 
        """
        sleep(30)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(config.grid_vip, username='root')
        stdin, stdout, stderr = ssh.exec_command("ls /storage/cores/ | wc -l")
        response=stdout.readlines()
        print(response[0])
        if int(response[0]) == 0:
            assert True
            print("No cores found")
            ssh.close()
        else:
            stdin, stdout, stderr = ssh.exec_command("ls -ltr /storage/cores/")
            response=stdout.readlines()
            print(response)
            ssh.close()
            assert False
    
    @pytest.mark.order(order=54)
    def test_054_perform_if_needed_restart_during_lbdn_down_NIOS_84602(self):
        """
        perform if_needed restart and check status
        """       
        restart_services_IF_NEEDED()
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name=server1ss&_return_fields%2B=health", grid_vip=config.grid_vip)
        ref = json.loads(ref)
        print(ref[0]["health"]["availability"])
        if ref[0]["health"]["availability"] == "UNKNOWN":
            assert False
        else:
            assert True
   
    @pytest.mark.order(order=55)
    def test_055_revert_changes_NIOS_84320(self):
        """
        wait for lbdn to come up
        """
        sleep(70)
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:server?name=server1ss&_return_fields%2B=health", grid_vip=config.grid_vip)
        ref = json.loads(ref)
        print(ref[0]["health"]["availability"])
        if ref[0]["health"]["availability"] == "GREEN":
            assert True
        else:
            assert False
            
            
    
    @pytest.mark.order(order=56)
    def test_056_disable_server2_NIOS_83854(self):
        """
        disable server2 with for specific_time_disable
        """
        global Server2
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        data = {"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":10,"disable_on":[config.grid_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object": Server2,"specific_time_disable":60}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        sleep(15)
        if "SUCCESS" not in output:
            assert False
        else:
            assert True
            print("Successfully disabled server2")
    
    
    
    @pytest.mark.order(order=57)
    def test_057_create_servers4_NIOS_83854(self):
        """
        Create Server4 and perform if needed restart
        """
        data={"host": config.Server4,"name": "server4ss"}
        server4_ref=ib_NIOS.wapi_request('POST',object_type='dtc:server',fields=json.dumps(data))
        print(server4_ref)
        restart_services_IF_NEEDED()
        if type(server4_ref) == tuple:
            assert False
        else:
            assert True
            print("server4 was created successfully")
           
            
    @pytest.mark.run(order=58)
    def test_058_check_timestamp_in_healthstatus_file_NIOS_84320(self):
        """
        Create timestamp when healthstatus file 
        """
        sleep(60)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(config.grid_vip, username='root')
        stdin, stdout, stderr = ssh.exec_command("cat /infoblox/var/idns_conf/health_status.txt |grep timestamp")
        response=stdout.readlines()
        response0 = (response[0])
        response0 = response0.split(":")
        response0 = str(response0[1])
        response0 = response0[1:-2]
        response1 = (response[1])
        response1 = response[1].split(":")  
        response1 = str(response0)
        response1 = response1[1:-2]
        print(response0,response1) 
        if response1 =="0" or response0 == '0':
            assert False
            ssh.close()
        else:
            assert True
            print("timestamp value is not 0")
            ssh.close()

    

    @pytest.mark.order(order=59)
    def test_059_disable_server2_with_wrong_reference_NIOS_84910(self):
        """
        disable server2 with until manual enabling
        """
        Server_wrong__ref = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzee:server2ss"
        data = {"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":10,"disable_on":[config.grid_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object": Server_wrong__ref,"specific_time_disable":60}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        sleep(15)
        if "The selected object could not be found" in output:
            assert True
            print("getting proper error when we use wrong reference")
        else:
            assert False
            
            

    @pytest.mark.order(order=60)
    def test_060_power_off_member1_NIOS_84910(self):
        """
        power off member1 for sometime
        """
        os.system("/import/tools/lab/bin/reboot_system -H " + config.vmid1 + " -a poweroff")
        sleep(15)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(config.grid_vip, username='root')
        stdin, stdout, stderr = ssh.exec_command("ping "+config.grid_member1_vip+" -c 2 \n" )
        response=stdout.readlines()
        response = str(response)
        print(response)
        if "100% packet loss" in response:
            assert True
            print("member1 is offline")
            ssh.close()
        else:
            assert False
            ssh.close()
            

    @pytest.mark.order(order=61)
    def test_061_disable_server2_when_member1_is_offline_NIOS_84910(self):
        """
        disable server2 for member1 when member is offline
        """
        sleep(60)
        global Server2
        Server2 = "dtc:server/ZG5zLmlkbnNfc2VydmVyJHNlcnZlcjJzcw:server2ss"
        data = {"disable_health_monitoring":True,"delayed_disable":False,"delayed_disable_time":10,"disable_on":[config.grid_member1_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object": Server2,"specific_time_disable":60}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        sleep(15)
        output = output.split('text": ')[1]
        final_output = output.split('n)')[0].strip('"')
        print(final_output)
        expected_output = "A DTC object cannot be enabled or disabled on an offline grid member "+config.grid_member1_fqdn
        if expected_output == final_output:
            assert True
            print("cannot disable server2 for member1 when it is offline")
        else:
            assert False
            
    
    
    @pytest.mark.order(order=62)
    def test_062_power_on_member1_NIOS_84910(self):
        """
        power off member1 for sometime
        """
        os.system("/import/tools/lab/bin/reboot_system -H " + config.vmid1 + " -a poweron")
        sleep(255)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(config.grid_vip, username='root')
        stdin, stdout, stderr = ssh.exec_command("ping "+config.grid_member1_vip+" -c 2 \n" )
        response=stdout.readlines()
        response = str(response)
        print(response)
        if "100% packet loss" in response:
            assert False
            print("member1 is still offline")
            sleep(90)
        else:
            assert True
            print("member1 is up")
    
    @pytest.mark.order(order=63)
    def test_063_disable_lbdn_NIOS_84821(self):
        """
        disable lbdn and disable should not fail
        """
        global Lbdn
        Lbdn = "dtc:lbdn/ZG5zLmlkbnNfbGJkbiRsYmRu:lbdn"
        data = {"disable_health_monitoring":False,"delayed_disable":False,"delayed_disable_time":10,"disable_on":[config.grid_fqdn],"disable_timeframe":"FOR_SPECIFIED_TIME","dtc_object": Lbdn,"specific_time_disable":180}
        output = DTC_Object_Fail_back_Manual_Disable(data)
        print(output)
        sleep(15)
        if "SUCCESS" not in output:
            assert False
        else:
            assert True
            print("Successfully disabled Lbdn")
    
            
            
    @pytest.mark.order(order=64)
    def test_064_modify_pool_to_have_https_healthmonitors_NIOS_84821(self):
        """
        modify health monitor to https from icmp
        """
        Pool = "dtc:pool/ZG5zLmlkbnNfcG9vbCRwb29s:pool"
        global Pool
        global Server1
        global Server2
        print(Server1,Server2)
        data={"name": "pool","lb_preferred_method": "ROUND_ROBIN","servers": [{"ratio": 1,"server": Server2}],"monitors": ["dtc:monitor:http/ZG5zLmlkbnNfbW9uaXRvcl9odHRwJGh0dHBz:https"]}
        pool_ref=ib_NIOS.wapi_request('PUT',object_type=Pool,fields=json.dumps(data))
        print(pool_ref)
        pool_ref = json.loads(pool_ref)
        restart_services()
        sleep(60)
        if type(pool_ref)  == tuple:
            if pool_ref[0] == 400 or pool_ref[0] == 401:
                assert False
        else:
            assert True
            
    
    @pytest.mark.order(order=65)
    def test_065_check_pool_health_status_NIOS_84821(self):
        """
        check pool health status
        """       
        ref =  ib_NIOS.wapi_request('GET', object_type="dtc:pool?name=pool&_return_fields%2B=health", grid_vip=config.grid_vip)
        ref = json.loads(ref)
        print(ref[0]["health"]["availability"])
        if ref[0]["health"]["availability"] == "GREEN":
            assert False
        else:
            assert True
            print("Health status updated properly")
            
        
        
            
    @pytest.mark.order(order=66)
    def test_066_Force_restart_grid_and_check_logs_NIOS_84258(self):
        """
        "Post DNS restart adding failback events" logs should be seen After Force restart performed on grid
        """
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        restart_services()
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        LookFor="Post DNS restart adding failback events"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        print(logs)
        
        if logs == None:
            assert False
            print("Post DNS restart adding failback events log not seen After Force restart performed on grid")
        
        else:
            assert True
            print("Post DNS restart adding failback events logs seen After Force restart performed on grid")
    
    

    

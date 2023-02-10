import dns.message
import base64
import re
import config                                    
import pytest                                    
import unittest                                  
import logging
import os
import pexpect
import sys
import os.path
from os.path import join
import subprocess
import commands
import json
import random
import commands
import string
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv

#  -----------------------------------------------------------

# Grid Configuration :-

# Grid Master (IB-FLEX) with MGMT enabled having 8 CPU and 22 GB Memory
# Grid Member1 (IB-FLEX) with MGMT enabled having 8 CPU and 32 GB Memory
# Grid Member2 (IB-v1415) with MGMT enabled. ( APD license )

#-------------------------------------------------------------

# Making DoH Query
def doh_query(ip,domain='infoblox.com',rr='A',edns=True):
    endpoint = "https://"+ip+"/dns-query"
    message = dns.message.make_query(domain, rr, use_edns=edns)
    dns_req = base64.urlsafe_b64encode(message.to_wire()).decode("UTF8").rstrip('=')
    query = "curl -H 'content-type: application/dns-message' "+endpoint+"?dns="+dns_req+" -o - -s -k1 --http2 > doh_http2.txt"
    try:
        op = os.popen(query)
        h = op.read()
        fi = open("doh_http2.txt", "rb").read()
        response = dns.message.from_wire(fi)
        response = response.to_text().encode("utf-8")
        os.remove("doh_http2.txt")
    except:
        print("\nThere is some problem with the DOH server...!!")
        response = "NIL"
    return response
   
#Getting the Grid Reference sting

def grid_ref_string():
    response = ib_NIOS.wapi_request('GET', object_type="grid:dns",grid_vip=config.grid_vip)
    logging.info(response)
    print(response)
    if type(response)!=tuple:
        ref1 = json.loads(response)
        for key in ref1:
            grid_ref = key.get('_ref')
    else:
        print("Failed to get grid DNS ref string")
        grid_ref = "NIL"
    return grid_ref


#Getting the member DNS Reference sting

def mem_ref_string(hostname):
    response = ib_NIOS.wapi_request('GET', object_type="member:dns",grid_vip=config.grid_vip)
    logging.info(response)
    print(response)
    if type(response)!=tuple:
        ref1 = json.loads(response)
        for key in ref1:
            if key.get('host_name') == hostname:
                mem_ref = key.get('_ref')
                break
    else:
        print("Failed to get member DNS ref string")
        mem_ref = "NIL"
    
    return mem_ref

#Getting the member Reference sting

def mem_ref(hostname):
    response = ib_NIOS.wapi_request('GET', object_type="member",grid_vip=config.grid_vip)
    logging.info(response)
    print(response)
    if type(response)!=tuple:
        ref1 = json.loads(response)
        for key in ref1:
            if key.get('host_name') == hostname:
                mem_ref = key.get('_ref')
                break
    else:
        print("Failed to get member DNS ref string")
        mem_ref = "NIL"
    
    return mem_ref


#Perform DNS Restart

def dns_restart(hostname):
    ref = mem_ref(hostname)
    data= {"restart_option":"FORCE_RESTART","service_option": "DNS"}
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
    sleep(60)
    print("DNS Restart Successfull")

# Perform product reboot

def prod_reboot(ip):
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+ip)
    child.logfile=sys.stdout
    child.expect('password:')
    child.sendline('infoblox')
    child.expect('Infoblox >')
    child.sendline('reboot')
    child.expect('REBOOT THE SYSTEM?')
    child.sendline('y')
    child.expect(pexpect.EOF)
    sleep(120)
    for i in range(1,20):
        sleep(60)
        status = os.system("ping -c5 "+ip)
        print(status)
        if status == 0:
            print("System is up")
            break
        else:
            print("System is still down..!!")
    sleep(10)
    print("Product Reboot successfull ..!!!")
                    
#syslog and infoblox.log start and stop funtions

def syslog_log_start(ip):
    log("start","/var/log/syslog",ip)
                
def syslog_log_stop(ip):
    log("stop","/var/log/syslog",ip)

def infoblox_log_start(ip):                
    log("start","/infoblox/var/infoblox.log",ip)
                
def infoblox_log_stop(ip):
    log("stop","/infoblox/var/infoblox.log",ip)


class RFE_9826(unittest.TestCase):

        
        # Configuring the Forwarder and recursion on Grid level

        @pytest.mark.run(order=1)
        def test_001_configuring_forwarder_and_recursion_grid_wide(self):
            logging.info("Configuring forwarder and recursion grid wide")
            mgmt_fqdn = "ib-"+config.grid_vip.replace('.','-')+".infoblox.com"
            lan_fqdn = "ib-"+config.master1_ip.replace('.','-')+".infoblox.com"
            data = {"host_name": mgmt_fqdn}
            grid_ref = mem_ref(lan_fqdn)
            response = ib_NIOS.wapi_request('PUT', object_type=grid_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
            sleep(60)
            if type(response)!=tuple:
                print("Hostname changed successfully")
            else:
                print("Failed to change the hostname")
            data = {"forward_only":True, "forwarders": [config.forwarder],"allow_recursive_query":True}
            grid_ref = grid_ref_string()
            response = ib_NIOS.wapi_request('PUT', object_type=grid_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
            if type(response)!=tuple:
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "DNS"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(120)
                print("Forwarder and Recursion enabled")
                assert True
            else:
                print("Failed to enable forwarder and recursion")
                assert False

        # Validating recursiona and forwarder setting on the first member

        @pytest.mark.run(order=2)
        def test_002_validating_forwarder_and_recursion(self):
                logging.info("Validating forwarder and recursion")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.member1_mgmt)
                child.logfile=sys.stdout
                child.expect('-bash-5.0#')
                child.sendline('cat /infoblox/var/named_conf/named.conf')
                try:
                    child.expect('recursion yes')
                    forward = "forwarders { "+config.forwarder+"; };"
                    child.expect(forward)
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(20)
                    print("Test case Successfull")
                    assert True
                except:
                    child.expect('-bash-5.0#')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(20)
                    print("Test case Failed")
                    assert False

        # Configuring DoH/DOT in the Master which dont have enough memory as per the specification to configure DoH

        @pytest.mark.run(order=3)
        def test_003_enable_DoH_and_dot_on_standalone_member_not_enough_memory(self):
                logging.info("Enable DoH and DoT in member1 not having enough memory")
                data = {"doh_service": True, "doh_https_session_duration": 40, "dns_over_tls_service": True, "tls_session_duration": 40}
                mem_ref = mem_ref_string(config.grid_member_fqdn)
                print(mem_ref)
                status, response = ib_NIOS.wapi_request('PUT', object_type=mem_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(20)
                if status == 400:
                    ref1 = json.loads(response)
                    print("Failed to enabled DoH on the Member level because " + ref1['text'] )
                    print("Test case successfully executed")
                    assert True
                else:
                    print("Test case Failed and does not get 400 error")
                    print("Error code received " + status)
                    assert False
                
        # Enable DCA on the member1

        @pytest.mark.run(order=4)
        def test_004_enable_DCA_on_standalone_member(self):
                logging.info("Enable DCA on the standalone member1")
                data = {"enable_dns": True, "enable_dns_cache_acceleration": True}
                grid_ref = mem_ref_string(config.grid_member1_fqdn)
                print(grid_ref)
                response = ib_NIOS.wapi_request('PUT', object_type=grid_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                for i in range(1,20):
                    sleep(60)
                    status = os.system("ping -c1 -w2 "+config.member1_mgmt)
                    print(status)
                    if status == 0:
                        print("System is up")
                        break
                    else:
                        print("System is still down..!!")
                sleep(10)
                print("Product Reboot successfull ..!!!")
                if type(response)!=tuple:
                    print("DCA Enabled successfully")
                    assert True
                else:
                    print("Failed to enable DCA on the Member1")
                    assert False
        
        # verification for the above test case:

        @pytest.mark.run(order=5)
        def test_005_validate_debug(self):
                logging.info("Validate DCA on member1")
                sleep(300)
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.member1_mgmt)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show dns-accel')
                try:
                    child.expect('Cache:                           Enabled')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(120)
                    print("Test case Successfull")
                    assert True
                except:
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(120)
                    print("Test case Failed")
                    assert False

        # Configuring DoH and DoT on the member1 having MGMT and fastpath configured

        @pytest.mark.run(order=7)
        def test_007_enable_DoH_and_dot_on_standalone_member(self):
                logging.info("Enable DoH/DoT in member1")
                data = {"doh_service": True, "doh_https_session_duration": 40, "dns_over_tls_service": True, "tls_session_duration": 40}
                grid_ref = mem_ref_string(config.grid_member1_fqdn)
                print(grid_ref)
                response = ib_NIOS.wapi_request('PUT', object_type=grid_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(60)
                print(response)
                if type(response)!=tuple:
                    prod_reboot(config.member1_mgmt)
                    sleep(120)
                    print("DoH/DoT has been enabled on the member Level")
                    assert True
                else:
                    print("Failed to enable DoH/DoT on the member Level")
                    assert False

        # Debug log verification for the above test case:

        @pytest.mark.run(order=8)
        def test_008_validate_debug_logs_for_enabling_doh_dot_feature(self):
                logging.info("Validating debug logs for enabling DoH/DoT feature")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.member1_mgmt)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show doh-status')
                try:
                    child.expect('DoH is enabled')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(120)
                    print("Test case Successfull")
                    assert True
                except:
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(120)
                    print("Test case Failed")
                    assert False

        # check the memory footprints allowcated to fastpath (with DoH and dot) on member1

        @pytest.mark.run(order=9)
        def test_009_check_memory_size_allocated_fastpath_with_DoH_and_DoT(self):
                logging.info("Check memory allocated to fatpath for IB_FLEX small with DoH and dot")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.member1_mgmt)
                f = open(config.backup_path + "/mylogdca.txt", "wb")
                path = config.backup_path + "/mylogdca.txt"
                child.logfile=open(path,'wb')
                child.expect('-bash-5.0#')
                child.sendline('ps ax | grep fp-rte')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(120)
                fi = open(path, "rb").read()
                for i in fi.splitlines():
                    if "--socket-mem" in i:
                        res = i
                val = res.split()[int(res.split().index("--socket-mem")) + 1]
                if val == config.fast_mem:
                    print("Test case Successfull")
                    os.remove(path)
                    assert True
                else:
                    print("Test case Failed")
                    os.remove(path)
                    assert False
        
        # This case test the listen on port 8443 details in the DoH/DoT enabled member1

        @pytest.mark.run(order=10)
        def test_010_check_listen_on_port_details_for_DOH_in_Standalone_member1(self):
                logging.info("Check listen-on port details for DoH in standalone member 1")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.member1_mgmt)
                child.logfile=sys.stdout
                child.expect('-bash-5.0#')
                child.sendline('cat /infoblox/var/named_conf/named.conf')
                try:
                    child.expect('listen-on port 8443')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(20)
                    print("Test case Successfull")
                    assert True
                except:
                    child.expect('-bash-5.0#')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(20)
                    print("Test case Failed")
                    assert False

        # This case test the listen on port 8853 details in the DoH/DoT enabled member1

        @pytest.mark.run(order=11)
        def test_011_check_listen_on_port_details_for_dot_in_Standalone_member1(self):
                logging.info("Check listen-on port details for dot in standalone member 1")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.member1_mgmt)
                child.logfile=sys.stdout
                child.expect('-bash-5.0#')
                child.sendline('cat /infoblox/var/named_conf/named.conf')
                try:
                    child.expect('listen-on port 8853')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(20)
                    print("Test case Successfull")
                    assert True
                except:
                    child.expect('-bash-5.0#')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(20)
                    print("Test case Failed")
                    assert False
        
        # This case test the DCA json file to check the DOH details in the DoH/DoT enabled member1

        @pytest.mark.run(order=12)
        def test_012_check_dca_json_details_for_DOH_in_Standalone_member1(self):
                logging.info("Check dca json details for DOH in standalone member 1")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.member1_mgmt)
                child.logfile=sys.stdout
                child.expect('-bash-5.0#')
                child.sendline('cat /infoblox/var/named_conf/dns_cache_acceleration.json | grep "dns_over_https" -a4 ')
                try:
                    child.expect('"doh_https_session_duration": "40"')
                    child.expect('"enabled": true')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(20)
                    print("Test case Successfull")
                    assert True
                except:
                    child.expect('-bash-5.0#')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(20)
                    print("Test case Failed")
                    assert False

        # This case test the DCA json (DoT Details) file details in the DoH/DoT enabled member1

        @pytest.mark.run(order=13)
        def test_013_check_dca_json_details_for_dot_in_Standalone_member1(self):
                logging.info("Check dca json details for dot in standalone member 1")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.member1_mgmt)
                child.logfile=sys.stdout
                child.expect('-bash-5.0#')
                child.sendline('cat /infoblox/var/named_conf/dns_cache_acceleration.json | grep "dns_over_tls" -a4 ')
                try:
                    child.expect('"enabled": true')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(20)
                    print("Test case Successfull")
                    assert True
                except:
                    child.expect('-bash-5.0#')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(20)
                    print("Test case Failed")
                    assert False

        # This case to check the DoH Status is populated in the DoH enabled member1 or not
    
        @pytest.mark.run(order=14)
        def test_014_check_doh_status_in_standalone_member1(self):
                logging.info("Check DOH status details in standalone member1")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.member1_mgmt)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show doh-status')
                try:
                    child.expect('DoH is enabled')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(120)
                    print("Test case Successfull")
                    assert True
                except:
                    child.expect('Infoblox >')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(120)
                    print("Test case Failed")
                    assert False

        # This case to check the DoH Config is populated in the DoH enabled member1 or not

        @pytest.mark.run(order=15)
        def test_015_check_doh_config_in_standalone_member1(self):
                logging.info("Check DOH config details in standalone member1")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.member1_mgmt)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show doh-config')
                try:
                    child.expect('DoH listen on port: 443')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(120)
                    print("Test case Successfull")
                    assert True
                except:
                    child.expect('Infoblox >')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(120)
                    print("Test case Failed")
                    assert False

        # This case to check the DoT Stats is populated in the DoH enabled member1 or not

        @pytest.mark.run(order=16)
        def test_016_check_dot_stats_in_standalone_member1(self):
                logging.info("Check DOT stats details in standalone member1")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.member1_mgmt)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show dns-over-tls-stats')
                try:
                    child.expect('rx_packets:')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(120)
                    print("Test case Successfull")
                    assert True
                except:
                    child.expect('Infoblox >')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(120)
                    print("Test case Failed")
                    assert False

        # This case to check the DoT Status is populated in the DoH enabled member1 or not
    
        @pytest.mark.run(order=17)
        def test_017_check_dot_status_in_standalone_member1(self):
                logging.info("Check DOT status details in standalone member1")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.member1_mgmt)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show dns-over-tls-status')
                try:
                    child.expect('DoT is enabled')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(120)
                    print("Test case Successfull")
                    assert True
                except:
                    child.expect('Infoblox >')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(120)
                    print("Test case Failed")
                    assert False

        # This case to check the DoT Config is populated in the DoH enabled member1 or not

        @pytest.mark.run(order=18)
        def test_018_check_dot_config_in_standalone_member1(self):
                logging.info("Check DOT config details in standalone member1")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.member1_mgmt)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show dns-over-tls-config')
                try:
                    child.expect('DoT listen on port: 853')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(120)
                    print("Test case Successfull")
                    assert True
                except:
                    child.expect('Infoblox >')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(120)
                    print("Test case Failed")
                    assert False

        # This case to check the DoT Stats is populated in the DoH enabled member1 or not

        @pytest.mark.run(order=19)
        def test_019_check_dot_config_in_standalone_member1(self):
                logging.info("Check DOT stats details in standalone member1")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.member1_mgmt)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show dns-over-tls-stats')
                try:
                    child.expect('rx_packets:')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(120)
                    print("Test case Successfull")
                    assert True
                except:
                    child.expect('Infoblox >')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(120)
                    print("Test case Failed")
                    assert False
                    
    
        # Perfrom a EDNS DoH query on member1 and check the response 
        
        @pytest.mark.run(order=20)
        def test_020_check_response_details_of_DoH_query_with_edns(self):
            logging.info("Check DoH response details by making a query with EDNS padding")
            response = doh_query(config.grid_member1_vip)
            if response == "NIL":
                print("Failed to execute the test case")
                assert False
            else:
                if "rcode NOERROR" in response:
                    print("The response of the query is" + response)
                    print("Successfully executed the test case !!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    assert False
        

        
        
        # Perfrom some non - EDNS continuous DoH queries on member1 and check if the responses are from DCA cache or not
        
        @pytest.mark.run(order=22)
        def test_022_check_dca_output_details_of_DoH_query(self):
            logging.info("Check dca chache response details of a DoH query")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.member1_mgmt)
            path = config.backup_path + "/mylog.txt"
            child.logfile=open(path,'wb')
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('show dns-accel')
            child.sendline('exit')
            child.expect(pexpect.EOF)
            sleep(120)
            fi = open(path, "rb").read()
            for i in fi.splitlines():
                if "Cache hit count" in i:
                    res1 = i.split()[-1]
            print("Initial Cache count :" + res1)
            f = open(path, "r+") 
            f.seek(0)
            f.truncate()
            for i in range(1,10):
                res = doh_query(config.grid_member1_vip, "sony.com", "A", False)
                sleep(1)
            sleep(10)
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.member1_mgmt)
            child.logfile=open(path,'wb')
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('show dns-accel')
            child.sendline('exit')
            child.expect(pexpect.EOF)
            sleep(120)
            fi = open(path, "rb").read()
            for i in fi.splitlines():
                if "Cache hit count" in i:
                    res2 = i.split()[-1]
            print("Cache count after 10 same query: " + res2)
            count = int(res2) - int(res1)
            print(count)
            if count == 8:
                print("Success !!") 
                os.remove(path)
                assert True
            else:
                print("Failed")
                os.remove(path)
                assert False


        # Test case to check the RX, TX values, Open sessions and close sessions for DoH

        @pytest.mark.run(order=23)
        def test_023_check_rx_tx_open_close_sessions_DoH_query(self):
            logging.info("Check rx, tx, open, close sessions for DoH queries")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.member1_mgmt)
            path = config.backup_path + "/mylog.txt"
            child.logfile=open(path,'wb')
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('show doh-stats')
            child.sendline('exit')
            child.expect(pexpect.EOF)
            sleep(120)
            fi = open(path, "rb").read()
            for i in fi.splitlines():
                if "rx_packets:" in i:
                    rx = i.split()[-1]
                if "tx_packets:" in i:
                    tx = i.split()[-1]
                if "opened_sessions:" in i:
                    open_session = i.split()[-1]
                if "closed_sessions:" in i:
                    close_session = i.split()[-1]
            print("RX :" + rx)
            print("TX :" + tx)
            print("Open Sessions :" + open_session)
            print("close Sessions :" + close_session)
            if rx == tx and open_session == close_session:
                print("Test successfull")
                os.remove(path)
                assert True
            else:
                print("Test Failed")
                os.remove(path)
                assert False

        # Perfrom a EDNS query on the mgmt interface of member1 and check the response 
        
        @pytest.mark.run(order=24)
        def test_024_check_response_details_of_DoH_query_on_mgmt_interface_with_edns(self):
            logging.info("Check DoH response details by making a query with EDNS padding in mgmt interface")
            response = doh_query(config.member1_mgmt)
            if response == "NIL":
                print("Successfully executed the test case !!")
                assert True
            else:
                print("Failed to execute the test case")
                assert False

        # Perfrom a DoT queries and check the response 
        
        @pytest.mark.run(order=25)
        def test_025_check_response_details_of_DoT_query_with_edns(self):
            logging.info("Check DoT response details by making a DoT query")
            query = "kdig @"+config.grid_member1_vip+" discovery.com +tls"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    assert False    
            except:
                print("Failed to execute the test case")
                assert False

        # Test case to check the RX, TX values, Open sessions and close sessions for DoT

        @pytest.mark.run(order=26)
        def test_026_check_rx_tx_open_close_sessions_DoT_query(self):
            logging.info("Check rx, tx, open, close sessions for DoT queries")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.member1_mgmt)
            path = config.backup_path + "/mylog.txt"
            child.logfile=open(path,'wb')
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('show dns-over-tls-stats')
            child.sendline('exit')
            child.expect(pexpect.EOF)
            sleep(120)
            fi = open(path, "rb").read()
            for i in fi.splitlines():
                if "rx_packets:" in i:
                    rx = i.split()[-1]
                if "tx_packets:" in i:
                    tx = i.split()[-1]
                if "opened_sessions:" in i:
                    open_session = i.split()[-1]
                if "closed_sessions:" in i:
                    close_session = i.split()[-1]
            print("RX :" + rx)
            print("TX :" + tx)
            print("Open Sessions :" + open_session)
            print("close Sessions :" + close_session)
            if rx == tx and open_session == close_session:
                print("Test successfull")
                os.remove(path)
                assert True
            else:
                print("Test Failed")
                os.remove(path)
                assert False
            
        # Perfrom some continuous DoT queries on member1 and check if the responses are from DCA cache or not
        
        @pytest.mark.run(order=27)
        def test_027_check_dca_output_details_of_DoT_query(self):
            logging.info("Check dca chache response details of a DoT query")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.member1_mgmt)
            path = config.backup_path + "/mylog.txt"
            child.logfile=open(path,'wb')
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('show dns-accel')
            child.sendline('exit')
            child.expect(pexpect.EOF)
            sleep(120)
            fi = open(path, "rb").read()
            for i in fi.splitlines():
                if "Cache hit count" in i:
                    res1 = i.split()[-1]
            print("Initial Cache count :" + res1)
            f = open(path, "r+") 
            f.seek(0)
            f.truncate()
            query = "kdig @"+config.grid_member1_vip+" dell.com +tls"
            for i in range(1,10):
                op = os.popen(query)
                h = op.read()
                sleep(1)
            sleep(10)
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.member1_mgmt)
            child.logfile=open(path,'wb')
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('show dns-accel')
            child.sendline('exit')
            child.expect(pexpect.EOF)
            sleep(120)
            fi = open(path, "rb").read()
            for i in fi.splitlines():
                if "Cache hit count" in i:
                    res2 = i.split()[-1]
            print("Cache count after 10 same query: " + res2)
            count = int(res2) - int(res1)
            print(count)
            if count == 8:
                print("Success !!") 
                os.remove(path)
                assert True
            else:
                print("Failed")
                os.remove(path)
                assert False      
        
        # Disable DCA on the member1 having DoH/DOH Enabled

        @pytest.mark.run(order=28)
        def test_028_disabl_DCA_on_standalone_member1_level_doh_dot_enable(self):
                logging.info("Disable DCA on the standalone member1 having DoH/dot enabled")
                data = {"enable_dns": True, "enable_dns_cache_acceleration": False}
                grid_ref = mem_ref_string(config.grid_member1_fqdn)
                print(grid_ref)
                status, response = ib_NIOS.wapi_request('PUT', object_type=grid_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(60)
                if status == 400:
                    ref1 = json.loads(response)
                    print("Failed to enabled DoH on the Member level because " + ref1['text'] )
                    print("Test case successfully executed")
                    assert True
                else:
                    print("Test case Failed and does not get 400 error")
                    print("Error code received " + status)
                    assert False
        
        # Enable ADP on the member1

        @pytest.mark.run(order=29)
        def test_029_enable_ADP_on_standalone_member1_level(self):
                logging.info("Enable ADP on the standalone member1")
                data = {"enable_service": True}
                response = ib_NIOS.wapi_request('GET', object_type="member:threatprotection",grid_vip=config.grid_vip)
                logging.info(response)
                print(response)
                if type(response)!=tuple:
                    ref1 = json.loads(response)
                    for key in ref1:
                        if config.grid_member1_fqdn in key.get('_ref'):
                            mem_ref = key.get('_ref')
                            print(mem_ref)
                            break
                response = ib_NIOS.wapi_request('PUT', object_type=mem_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                for i in range(1,20):
                    sleep(60)
                    status = os.system("ping -c1 -w2 "+config.member1_mgmt)
                    print(status)
                    if status == 0:
                        print("System is up")
                        break
                    else:
                        print("System is still down..!!")
                sleep(10)
                print("Product Reboot successfull ..!!!")
                if type(response)!=tuple:
                    print("ADP Enabled successfully")
                    assert True
                else:
                    print("Failed to enable ADP on the Member1")
                    assert False
        
        # Debug log verification for the above test case:

        @pytest.mark.run(order=30)
        def test_030_validate_debug_for_adp_configuration(self):
                logging.info("Validating debug logs for ADP configuration")
                sleep(300)
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.member1_mgmt)+' " tail -2000 /infoblox/var/infoblox.log"'
                out1 = commands.getoutput(sys_log_validation)
                logging.info (out1)
                res = re.search(r'suricata already running',out1)
                if res == None:
                    logging.info("Test Case Execution Completed")
                    assert False
                else:
                    logging.info("Test Case Execution Completed")
                    assert True

        # Perfrom a EDNS query on member1 and check the response 
        
        @pytest.mark.run(order=31)
        def test_031_check_response_details_of_DoH_query_with_edns(self):
            logging.info("Check DoH response details by making a query with EDNS padding")
            sleep(30)
            response = doh_query(config.grid_member1_vip)
            if response == "NIL":
                print("Failed to execute the test case")
                assert False
            else:
                if "rcode NOERROR" in response:
                    print("The response of the query is" + response)
                    print("Successfully executed the test case !!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    assert False
        
        # Perfrom a non - EDNS query on member1 and check the response 
        
        @pytest.mark.run(order=32)
        def test_032_check_response_details_of_DoH_query_with_non_edns(self):
            logging.info("Check DoH response details by making a query with EDNS padding")
            sleep(30)
            response = doh_query(config.grid_member1_vip, "test.com", "A", False)
            if response == "NIL":
                print("Failed to execute the test case")
                assert False
            else:
                if "rcode NOERROR" in response:
                    print("The response of the query is" + response)
                    print("Successfully executed the test case !!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    assert False

        # Perfrom a DoT queries and check the response 
        
        @pytest.mark.run(order=33)
        def test_033_check_response_details_of_DoT_query_with_edns(self):
            logging.info("Check DoT response details by making a DoT query")
            sleep(30)
            query = "kdig @"+config.grid_member1_vip+" discovery.com +tls"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    assert False    
            except:
                print("Failed to execute the test case")
                assert False
        
        # This case test Enable DoH Trace from the root of member1

        @pytest.mark.run(order=34)
        def test_034_enable_doh_trace_on_Standalone_member1_from_root(self):
                logging.info("Enable DoH trace from root in standalone member 1")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.member1_mgmt)
                child.logfile=sys.stdout
                child.expect('-bash-5.0#')
                child.sendline('fp-cli fp ib_dca set doh_trace 1')
                try:
                    child.expect('DOH trace is set to on')
                    child.expect('-bash-5.0#')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(20)
                    print("Test case 2 Successfull")
                    assert True
                except:
                    child.expect('-bash-5.0#')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(20)
                    print("Test case 2 Failed")
                    assert False


        # This case validate the DoH trace details from the CLI of the appliance (member1)
        
        @pytest.mark.run(order=35)
        def test_035_check_doh_trace_details_from_CLI(self):
            logging.info("Check doh trace details from the CLI of the appliance")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.member1_mgmt)
            path = config.backup_path + "/mylog.txt"
            child.logfile=open(path,'wb')
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('show doh-status')
            try:
                child.expect('DoH trace is on')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(60)
                print("Test case 2 Successfull")
                assert True
            except:
                child.expect('-bash-5.0#')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(60)
                print("Test case 2 Failed")
                assert False

            
        # This case test the DoH key logging enable from the CLI of member1
        
        @pytest.mark.run(order=36)
        def test_036_configure_doh_key_loggin_from_CLI(self):
            logging.info("configure DoH key logging from the CLI of the appliance")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.member1_mgmt)
            path = config.backup_path + "/mylog.txt"
            child.logfile=open(path,'wb')
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
            syslog_log_start(config.member1_mgmt)         
            child.sendline('set enable-doh-key-logging on')
            sleep(20)
            syslog_log_stop(config.member1_mgmt)
            try:
                child.expect('DOH key logging is enabled')
                child.expect('Maintenance Mode >')
                child.sendline('show doh-status')
                child.expect('DoH key logging is on')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(60)
                print("Test case Successfull")
                assert True
            except:
                child.expect('Maintenance Mode >')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(60)
                print("Test case Failed")
                assert False
        
        # Syslog log verification for the above test case:

        @pytest.mark.run(order=38)
        def test_038_validate_syslog_for_doh_key_logging(self):
                logging.info("Validating syslog logs for doh key logging")
                sleep(20)
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.member1_mgmt)+' " tail -20 /var/log/syslog"'
                out1 = commands.getoutput(sys_log_validation)
                logging.info (out1)
                res = re.search(r'DOH\'s key logging is enabled',out1)
                if res == None:
                    logging.info("Test Case Execution Completed")
                    assert False
                else:
                    logging.info("Test Case Execution Completed")
                    assert True
        
        # Changing the resolver from BIND to unbound of a DoH enabled member1

        @pytest.mark.run(order=39)
        def test_039_changing_resolver_from_bind_to_unbound(self):
                logging.info("Changing resolver from bind to unbound of a DoH enabled member")
                data = {"recursive_resolver": "UNBOUND"}
                ref = mem_ref_string(config.grid_member1_fqdn)
                response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data),grid_vip=config.grid_vip)
                if type(response)!=tuple:
                    dns_restart(config.grid_member1_fqdn)
                    print("Resolver changed successfully")
                    assert True
                else:
                    print("Failed to change the Resolver")
                    assert False
        
       # Debug log verification for the above test case:

        @pytest.mark.run(order=40)
        def test_040_validate_debug_log_for_resolver_changes(self):
                logging.info("Validating debug logs for resolver changes")
                sleep(20)
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.member1_mgmt)+' " tail -100 /infoblox/var/infoblox.log"'
                out1 = commands.getoutput(sys_log_validation)
                logging.info (out1)
                res = re.search(r'starting unbound',out1)
                if res == None:
                    logging.info("Test Case Execution Completed")
                    assert False
                else:
                    logging.info("Test Case Execution Completed")
                    assert True
       
       
        # Syslog log verification for the above test case:

        @pytest.mark.run(order=41)
        def test_041_validate_syslog_for_resolver_changes(self):
                logging.info("Validating syslog logs for resolver changes")
                sleep(60)
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.member1_mgmt)+' " tail -100 /var/log/syslog"'
                out1 = commands.getoutput(sys_log_validation)
                logging.info (out1)
                res = re.search(r'start of service \(unbound',out1)
                if res == None:
                    logging.info("Test Case Execution Completed")
                    assert False
                else:
                    logging.info("Test Case Execution Completed")
                    assert True       
       
       
       # This case to check the DoH Status is populated in the DoH enabled member1 having unbound resolver type
    
        @pytest.mark.run(order=42)
        def test_042_check_doh_status_in_standalone_member1_in_unbound_resolver(self):
                logging.info("Check DOH status details in standalone member1 in resolver type unbound")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.member1_mgmt)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show doh-status')
                try:
                    child.expect('DoH is enabled')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(120)
                    print("Test case 3 Failed")
                    assert False
                except:
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(120)
                    print("Test case 3 Successfull")
                    assert True

        # This case to check the DoT Status is populated in the DoH enabled member1 having unbound resolver type
    
        @pytest.mark.run(order=43)
        def test_043_check_dot_status_in_standalone_member1_having_unbound_resolver(self):
                logging.info("Check DOT status details in standalone member1 having unbound resolver")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.member1_mgmt)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show dns-over-tls-status')
                try:
                    child.expect('DoT is enabled')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(120)
                    print("Test case 3 Failed")
                    assert False
                except:
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(120)
                    print("Test case 3 Successfull")
                    assert True 

# The following test cases are to check on Member 2 which is IB-v1415

        # Enable ADP on the member2

        @pytest.mark.run(order=44)
        def test_044_enable_ADP_on_standalone_member2_level(self):
                logging.info("Enable ADP on the standalone member2")
                data = {"enable_service": True}
                response = ib_NIOS.wapi_request('GET', object_type="member:threatprotection",grid_vip=config.grid_vip)
                logging.info(response)
                print(response)
                if type(response)!=tuple:
                    ref1 = json.loads(response)
                    for key in ref1:
                        if config.grid_member2_fqdn in key.get('_ref'):
                            mem_ref = key.get('_ref')
                            print(mem_ref)
                            break
                response = ib_NIOS.wapi_request('PUT', object_type=mem_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                for i in range(1,20):
                    sleep(60)
                    status = os.system("ping -c1 -w2 "+config.member2_mgmt)
                    print(status)
                    if status == 0:
                        print("System is up")
                        break
                    else:
                        print("System is still down..!!")
                sleep(10)
                print("Product Reboot successfull ..!!!")
                if type(response)!=tuple:
                    print("ADP Enabled successfully")
                    assert True
                else:
                    print("Failed to enable ADP on the Member1")
                    assert False
        
        # Debug log verification for the above test case:

        @pytest.mark.run(order=45)
        def test_045_validate_debug(self):
                logging.info("Validating debug logs")
                sleep(120)
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.member2_mgmt)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show adp')
                try:
                    child.expect('Threat Protection:               Enabled')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(120)
                    print("Test case Successfull")
                    assert True
                except:
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(120)
                    print("Test case Failed")
                    assert False
        
        # Configuring DoH and DoT on the member2 having MGMT and fastpath configured

        @pytest.mark.run(order=46)
        def test_046_enable_DoH_and_dot_on_standalone_member2(self):
                logging.info("Enable DoH/DoT in member2")
                data = {"doh_service": True, "doh_https_session_duration": 40, "dns_over_tls_service": True, "tls_session_duration": 40}
                grid_ref = mem_ref_string(config.grid_member2_fqdn)
                print(grid_ref)
                response = ib_NIOS.wapi_request('PUT', object_type=grid_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(60)
                print(response)
                if type(response)!=tuple:
                    prod_reboot(config.member2_mgmt)
                    sleep(120)
                    print("DoH/DoT has been enabled on the member Level")
                    assert True
                else:
                    print("Failed to enable DoH/DoT on the member Level")
                    assert False
        
        # Debug log verification for the above test case:

        @pytest.mark.run(order=47)
        def test_047_validate_debug_logs_for_enabling_doh_dot_feature(self):
                logging.info("Validating debug logs for enabling DoH/DoT feature")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.member2_mgmt)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show doh-status')
                try:
                    child.expect('DoH is enabled')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(120)
                    print("Test case Successfull")
                    assert True
                except:
                    child.expect('Infoblox >')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(120)
                    print("Test case Failed")
                    assert False

        # check the memory footprints allowcated to fastpath (with DoH and dot) on member2

        @pytest.mark.run(order=48)
        def test_048_check_memory_size_allocated_fastpath_with_DoH_and_DoT(self):
                logging.info("Check memory allocated to fatpath for IB_FLEX small with DoH and dot on member2")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.member2_mgmt)
                path = config.backup_path + "/mylogdca.txt"
                child.logfile=open(path,'wb')
                child.expect('-bash-5.0#')
                child.sendline('ps ax | grep fp-rte')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(120)
                fi = open(path, "rb").read()
                for i in fi.splitlines():
                    if "--socket-mem" in i:
                        res = i
                val = res.split()[int(res.split().index("--socket-mem")) + 1]
                if val == config.fast_mem2:
                    print("Test case Successfull")
                    os.remove(path)
                    assert True
                else:
                    print("Test case Failed")
                    os.remove(path)
                    assert False
        
        # This case test the listen on port 8443 details in the DoH/DoT enabled member2

        @pytest.mark.run(order=49)
        def test_049_check_listen_on_port_details_for_DOH_in_Standalone_member2(self):
                logging.info("Check listen-on port details for DoH in standalone member 2")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.member2_mgmt)
                child.logfile=sys.stdout
                child.expect('-bash-5.0#')
                child.sendline('cat /infoblox/var/named_conf/named.conf')
                try:
                    child.expect('listen-on port 8443')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(20)
                    print("Test case Successfull")
                    assert True
                except:
                    child.expect('-bash-5.0#')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(20)
                    print("Test case Failed")
                    assert False

        # This case test the listen on port 8853 details in the DoH/DoT enabled member2

        @pytest.mark.run(order=50)
        def test_050_check_listen_on_port_details_for_dot_in_Standalone_member2(self):
                logging.info("Check listen-on port details for dot in standalone member 2")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.member2_mgmt)
                child.logfile=sys.stdout
                child.expect('-bash-5.0#')
                child.sendline('cat /infoblox/var/named_conf/named.conf')
                try:
                    child.expect('listen-on port 8853')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(20)
                    print("Test case Successfull")
                    assert True
                except:
                    child.expect('-bash-5.0#')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(20)
                    print("Test case Failed")
                    assert False
        
        # This case test the DCA json file to check the DOH details in the DoH/DoT enabled member2

        @pytest.mark.run(order=51)
        def test_051_check_dca_json_details_for_DOH_in_Standalone_member2(self):
                logging.info("Check dca json details for DOH in standalone member 1")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.member2_mgmt)
                child.logfile=sys.stdout
                child.expect('-bash-5.0#')
                child.sendline('cat /infoblox/var/named_conf/dns_cache_acceleration.json | grep "dns_over_https" -a4 ')
                try:
                    child.expect('"doh_https_session_duration": "40"')
                    child.expect('"enabled": true')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(20)
                    print("Test case Successfull")
                    assert True
                except:
                    child.expect('-bash-5.0#')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(20)
                    print("Test case Failed")
                    assert False

        # This case test the DCA json (DoT Details) file details in the DoH/DoT enabled member1

        @pytest.mark.run(order=52)
        def test_052_check_dca_json_details_for_dot_in_Standalone_member2(self):
                logging.info("Check dca json details for dot in standalone member 2")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.member2_mgmt)
                child.logfile=sys.stdout
                child.expect('-bash-5.0#')
                child.sendline('cat /infoblox/var/named_conf/dns_cache_acceleration.json | grep "dns_over_tls" -a4 ')
                try:
                    child.expect('"enabled": true')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(20)
                    print("Test case Successfull")
                    assert True
                except:
                    child.expect('-bash-5.0#')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(20)
                    print("Test case Failed")
                    assert False

        # Perfrom a EDNS DoH query on member2 and check the response 
        
        @pytest.mark.run(order=53)
        def test_053_check_response_details_of_DoH_query_with_edns(self):
            logging.info("Check DoH response details by making a query with EDNS padding")
            response = doh_query(config.grid_member2_vip)
            if response == "NIL":
                print("Failed to execute the test case")
                assert False
            else:
                if "rcode NOERROR" in response:
                    print("The response of the query is" + response)
                    print("Successfully executed the test case !!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    assert False
        
        # Perfrom a non - EDNS query on member1 and check the response 
        
        @pytest.mark.run(order=54)
        def test_054_check_response_details_of_DoH_query_with_non_edns(self):
            logging.info("Check DoH response details by making a query with EDNS padding")
            response = doh_query(config.grid_member2_vip, "test.com", "A", False)
            if response == "NIL":
                print("Failed to execute the test case")
                assert False
            else:
                if "rcode NOERROR" in response:
                    print("The response of the query is" + response)
                    print("Successfully executed the test case !!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    assert False

        # Perfrom a DoT queries and check the response 
        
        @pytest.mark.run(order=55)
        def test_055_check_response_details_of_DoT_query_with_edns(self):
            logging.info("Check DoT response details by making a DoT query")
            query = "kdig @"+config.grid_member2_vip+" discovery.com +tls"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    assert False    
            except:
                print("Failed to execute the test case")
                assert False

        # Test case to check the RX, TX values, Open sessions and close sessions for DoH

        @pytest.mark.run(order=56)
        def test_056_check_rx_tx_open_close_sessions_DoH_query(self):
            logging.info("Check rx, tx, open, close sessions for DoH queries")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.member2_mgmt)
            path = config.backup_path + "/mylog.txt"
            child.logfile=open(path,'wb')
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('show doh-stats')
            child.sendline('exit')
            child.expect(pexpect.EOF)
            sleep(120)
            fi = open(path, "rb").read()
            for i in fi.splitlines():
                if "rx_packets:" in i:
                    rx = i.split()[-1]
                if "tx_packets:" in i:
                    tx = i.split()[-1]
                if "opened_sessions:" in i:
                    open_session = i.split()[-1]
                if "closed_sessions:" in i:
                    close_session = i.split()[-1]
            print("RX :" + rx)
            print("TX :" + tx)
            print("Open Sessions :" + open_session)
            print("close Sessions :" + close_session)
            if rx == tx and open_session == close_session:
                print("Test successfull")
                os.remove(path)
                assert True
            else:
                print("Test Failed")
                os.remove(path)
                assert False

        # Test case to check the RX, TX values, Open sessions and close sessions for DoT

        @pytest.mark.run(order=57)
        def test_057_check_rx_tx_open_close_sessions_DoT_query(self):
            logging.info("Check rx, tx, open, close sessions for DoT queries")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.member2_mgmt)
            path = config.backup_path + "/mylog.txt"
            child.logfile=open(path,'wb')
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('show dns-over-tls-stats')
            child.sendline('exit')
            child.expect(pexpect.EOF)
            sleep(120)
            fi = open(path, "rb").read()
            for i in fi.splitlines():
                if "rx_packets:" in i:
                    rx = i.split()[-1]
                if "tx_packets:" in i:
                    tx = i.split()[-1]
                if "opened_sessions:" in i:
                    open_session = i.split()[-1]
                if "closed_sessions:" in i:
                    close_session = i.split()[-1]
            print("RX :" + rx)
            print("TX :" + tx)
            print("Open Sessions :" + open_session)
            print("close Sessions :" + close_session)
            if rx == tx and open_session == close_session:
                print("Test successfull")
                os.remove(path)
                assert True
            else:
                print("Test Failed")
                os.remove(path)
                assert False
        
        # Changing the hostname of the DoH enabled member2

        @pytest.mark.run(order=58)
        def test_058_changing_hostname_member_doh_enable(self):
                logging.info("Changing hostname of the DoH member")
                data = {"host_name": "name_change.com"}
                grid_ref = mem_ref(config.grid_member2_fqdn)
                infoblox_log_start(config.member2_mgmt)
                response = ib_NIOS.wapi_request('PUT', object_type=grid_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(60)
                infoblox_log_stop(config.member2_mgmt)
                if type(response)!=tuple:
                    print("Hostname changed successfully")
                    assert True
                else:
                    print("Failed to change the hostname")
                    assert False
                
        # Debug log verification for the above test case and checking if DoH restarted to sync with the certificate:

        @pytest.mark.run(order=59)
        def test_059_validate_debug(self):
                logging.info("Validating debug logs")
                sleep(120)
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.member2_mgmt)+' " tail -100 /infoblox/var/infoblox.log"'
                out1 = commands.getoutput(sys_log_validation)
                logging.info (out1)
                res = re.search(r'Restarting DOH service to reload certificate',out1)
                res1 = re.search(r'Restarting DOT service to reload certificate',out1)
                if res == None and res1 == None:
                    logging.info("Test Case Execution Completed")
                    assert False
                else:
                    logging.info("Test Case Execution Completed")
                    assert True

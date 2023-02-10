__author__ = "Arunkumar CM"
__email__  = "acm@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master                                                                      #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415),RPZ                                  #
########################################################################################
import datetime
from ib_utils.common_utilities import generate_token_from_file
import config
import re
import paramiko
import socket
import pexpect
import pytest
import unittest
import logging
from paramiko import client
import subprocess
import os
import json
import config
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
import commands
import json, ast
import requests
import time
import getpass
import sys
import pexpect
from paramiko import client
import ib_utils.ib_NIOS as ib_NIOS
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv

def restart_the_grid():
    logging.info("Restaring the grid")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data))
    sleep(30)
    print("Restrting the grid")

def add_rpz_rule(rule,zone):
    data={"name":rule+"."+zone,"rp_zone":zone,"canonical":rule}
    reference3=ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
    if type(reference3)!=tuple:
        return reference3
    else:
        return None

class Network(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_001_Start_DNS_Service(self):
        logging.info("Start DNS Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        print get_ref
        logging.info(get_ref)
        res = json.loads(get_ref)
        for i in res:
            ref=i["_ref"]
            logging.info("Modify a enable_dns")
            data = {"enable_dns": True}
            response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
            sleep(20)
            logging.info(response)
            read  = re.search(r'200',response)
            for read in  response:
                assert True
        logging.info("Test Case 1 Execution Completed")

    @pytest.mark.run(order=2)
    def test_002_Validate_DNS_service_Enabled(self):
        logging.info("Validate DNs Service is enabled")
        get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
        logging.info(get_tacacsplus)
        res = json.loads(get_tacacsplus)
        logging.info(res)
        for i in res:
            logging.info("found")
            assert i["enable_dns"] == True
        logging.info("Test Case 2 Execution Completed")
        logging.info("============================")
    
    @pytest.mark.run(order=3)
    def test_003_modify_grid_dns_properties_to_configure_threat_analytics(self):
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:dns")
        get_ref1=json.loads(get_ref)[0]['_ref']
        logging.info(get_ref1)
        data={"allow_recursive_query":True,"allow_query":[{"_struct": "addressac","address":"Any","permission":"ALLOW"}],"forwarders":[config.forwarder_ip],"logging_categories":{"log_rpz":True,"log_queries":True,"log_responses":True}}
        put_ref=ib_NIOS.wapi_request('PUT', object_type=get_ref1,fields=json.dumps(data))
        logging.info(put_ref)
        read  = re.search(r'200',put_ref)
        for read in put_ref:
            assert True
        logging.info("Test Case 3 Execution Completed")
        sleep(20)

    @pytest.mark.run(order=4)
    def test_004_modify_grid_settings(self):
        response = ib_NIOS.wapi_request('GET', object_type="grid")
        response = json.loads(response)
        response=response[0]["_ref"]
        data={"dns_resolver_setting": {"resolvers": ["127.0.0.1",config.resolver_ip]}}
        res = ib_NIOS.wapi_request('PUT', object_type=response,fields=json.dumps(data))
        logging.info(res)
        logging.info("Test Case 4 Execution Completed")
    
    @pytest.mark.run(order=7)
    def test_005_Enable_Parental_Control_with_Proxy_Settings(self):
        logging.info("Enabling parental control with proxy settings")
        response = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber")
        response = json.loads(response)
        response=response[0]["_ref"]
        logging.info(response)
        data={"interim_accounting_interval":2,"enable_parental_control": True,"cat_acctname":"infoblox_sdk", "cat_password":"LinWmRRDX0q","category_url":"https://dl.zvelo.com/","pc_zone_name":"pc.com","cat_update_frequency":1,"proxy_url":config.zvelo_proxy,"proxy_username":config.zvelo_username,"proxy_password":config.zvelo_password}
        res = ib_NIOS.wapi_request('PUT', object_type=response,fields=json.dumps(data))
        logging.info(res)
        restart_the_grid()
        sleep(20)
        print res
        if type(res)==tuple:
            if res[0]==400 or res[0]==401:
                logging.info("Test case Execution failed")
                assert False
            else:
                logging.info("Test Case Execution passed")
        else:
            logging.info("Test Case Execution passed")
            assert True

    @pytest.mark.run(order=6)
    def  test_006_add_subscriber_site(self):
        data={"blocking_ipv4_vip1": "1.1.1.1","msps":[{"ip_address":config.proxy_server1}],"spms": [{"ip_address": "10.12.11.11"}],"name":"site3","maximum_subscribers":100000,"members":[{"name":config.grid_fqdn}],"nas_gateways":[{"ip_address":"2.2.2.2","name":"nas1","shared_secret":"test123"}]}
        get_ref=ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data))
        logging.info(get_ref)
        print get_ref
        if type(get_ref)!=tuple:
            reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
            reference=json.loads(reference)
            if reference[0]["name"]==data["name"]:
                logging.info("Test case 6 execution passed")
                assert True
            else:
                logging.info("Test case 6 execution Failed")
                assert False
        else:
            logging.info(get_ref)
            logging.info("Test case 6 execution failed")
            assert False
    
    @pytest.mark.run(order=7)
    def test_007_start_subscriber_collection_services_for_added_site(self):
        get_ref=ib_NIOS.wapi_request('GET', object_type="member:parentalcontrol")
        get_ref=json.loads(get_ref)
        logging.info(get_ref)
        for ref in get_ref:
            ref=ref["_ref"]
            data={"enable_service":True}
            reference=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
            logging.info(reference)
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            time.sleep(1)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        get_ref=ib_NIOS.wapi_request('GET', object_type="member:parentalcontrol")
        get_ref=json.loads(get_ref)
        for ref in get_ref:
            if get_ref[0]["enable_service"]==True:
                time.sleep(60)
                logging.info("Test Case 7 Execution Completed")
                assert True
            else:
                logging.info("Test Case 7 Execution Completed")
                assert False

    @pytest.mark.run(order=8)
    def test_008_start_category_log_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/storage/zvelo/log/category_download.log",config.grid_vip)
        logging.info("Test case 8 execution failed")
        time.sleep(2000)

    @pytest.mark.run(order=9)
    def test_009_stop_category_log_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("stop","/storage/zvelo/log/category_download.log",config.grid_vip)
        logging.info("Test case 9 execution failed")

    @pytest.mark.run(order=10)
    def test_010_validate_for_zvelo_data(self):
        #time.sleep(40)
        logging.info("Validating Sylog Messages Logs")
        LookFor="zvelodb download completed"
        logs=logv(LookFor,"/storage/zvelo/log/category_download.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 10 Execution Completed")
            assert True
        else:
            logging.info("Test Case 10 Execution Failed")
            assert False

    @pytest.mark.run(order=405)
    def test_011_add_32_rpz_zone(self):
        logging.info("Adding 32 RPZ zones")
        for i in range(31,-1,-1):
            data={"fqdn": "rpz"+str(i)+".com","grid_primary":[{"name": config.grid_fqdn,"stealth":False}]}
            reference1=ib_NIOS.wapi_request('POST', object_type="zone_rp",fields=json.dumps(data))
            print(reference1)
            logging.info("adding RPZ zone ")
            data={"name":"pass"+str(i)+".rpz"+str(i)+".com","rp_zone":"rpz"+str(i)+".com","canonical":"pass"+str(i)}
            reference2=ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
            print(reference2)
            data={"name":"nxd"+str(i)+".rpz"+str(i)+".com","rp_zone":"rpz"+str(i)+".com","canonical":""}
            reference3=ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
            print(reference3)
            if type(reference1)!=tuple or type(reference2)!=tuple or type(reference3)!=tuple:
                logging.info("Test case execution passed")
                assert True
            else:
                logging.info("Test case execution failed")
                assert False

    @pytest.mark.run(order=12)
    def test_012_add_subscriber_record_to_the_added_site(self):
        host_name = socket.gethostname()
        host_ip=socket.gethostbyname(host_name)
        data={"ans0":"User-Name=JOHN","ip_addr":host_ip, "prefix":32,"localid":"N/A","ipsd":"N/A","subscriber_secure_policy":"FF","parental_control_policy":"00000000000000000000000000020040","unknown_category_policy":False,"dynamic_category_policy":False,"subscriber_id":"IMSI=12345","accounting_session_id":"Acct-Session-Id=9999732d-34590346","bwflag":True,"black_list":"a.com,a.com","site":"site3","flags":"SB","nas_contextual":"NAS-PORT=1813"}
        print data
        get_ref=ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscriberrecord",fields=json.dumps(data))
        print get_ref
        data1={"site":"site3"}
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriberrecord",fields=json.dumps(data1))
        get_ref=json.loads(get_ref)[0]
        if get_ref["prefix"]==data["prefix"] and get_ref["ip_addr"]==data["ip_addr"] and get_ref["ipsd"]==data["ipsd"] and get_ref["localid"]==data["localid"]:
            print("Test case Execution Passed")
            assert True
        else:
            print("Test case execution Failed")
            assert False
    
    @pytest.mark.run(order=13)
    def test_013_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("Test case 31 execution failed")

    @pytest.mark.run(order=19)
    def test_014_check_SSPC_functionality(self):
        host_name = socket.gethostname()
        host_ip=socket.gethostbyname(host_name)
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(host_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+host_ip+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site3-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        logging.info("Test case execution Completed")
    
    @pytest.mark.run(order=15)
    def test_015_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        print("Test Case 33 Execution Completed")

    @pytest.mark.run(order=124)
    def test_016_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_times_com(self):
        logging.info("Validate Named CEF Log for playboy.com  when get response from Bind")
        LookFor=".*named.*info CEF.*playboy.com.*CAT=0x00000000000000000000000000020000.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=17)
    def test_017_add_subscriber_record_to_the_added_site_for_SSPC(self):
        host_name = socket.gethostname()
        host_ip=socket.gethostbyname(host_name)
        data={"ans0":"User-Name=JOHN","ip_addr":host_ip, "prefix":32,"localid":"N/A","ipsd":"N/A","subscriber_secure_policy":"FF","parental_control_policy":"00000000000000000000000000000001","subscriber_id":"Calling-Station-Id=110361221","accounting_session_id":"Acct-Session-Id=9999732d-34590346","site":"site3","nas_contextual":"NAS-PORT=1813"}
        print data
        get_ref=ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscriberrecord",fields=json.dumps(data))
        print get_ref
        data1={"site":"site3"}
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriberrecord",fields=json.dumps(data1))
        get_ref=json.loads(get_ref)[0]
        if get_ref["prefix"]==data["prefix"] and get_ref["ip_addr"]==data["ip_addr"] and get_ref["ipsd"]==data["ipsd"] and get_ref["localid"]==data["localid"]:
            print("Test case Execution Passed")
            assert True
        else:
            print("Test case execution Failed")
            assert False

    @pytest.mark.run(order=13)
    def test_018_add_rpz_rule_in_rpz0(self):
        logging.info("add rpz rule")
        ref1=add_rpz_rule("playboy.com","rpz0.com")
        if ref1!=None:
            logging.info("Test case executed successfully")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
        sleep(30)

    @pytest.mark.run(order=18)
    def test_019_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("Test case 31 execution failed")

    @pytest.mark.run(order=15)
    def test_020_Query_playboy_com(self):
        host_name = socket.gethostname()
        host_ip=socket.gethostbyname(host_name)
        logging.info("Query")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(host_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+host_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")
        sleep(40)
    
    @pytest.mark.run(order=20)
    def test_021_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        print("Test Case 33 Execution Completed")

    @pytest.mark.run(order=12)
    def test_022_Validate_RPZ_hit_with_CEF_Log_RPZ_QNAME_PASSTHRU(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        #LookFor=".*RPZ-QNAME.*PASSTHRU.*rpz QNAME PASSTHRU rewrite playboy.com.*via playboy.com.rpz0.com.*Parental-Control-Policy=00000000000000000000000000000001.*CAT=RPZ.*"
        LookFor=".*CAT=RPZ.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False

    @pytest.mark.run(order=405)
    def test_023_delete_32_rpz_zone(self):
        logging.info("delete 32 RPZ zones")
        reference1=ib_NIOS.wapi_request('GET', object_type="zone_rp")
        reference1=json.loads(reference1)
        for ref in reference1:
            reference=ref["_ref"]
            reference1=ib_NIOS.wapi_request('DELETE', object_type=reference)
            if type(reference1)!=tuple:
                logging.info("Test case execution passed")
                assert True
            else:
                logging.info("Test case execution failed")
                assert False

    @pytest.mark.run(order=405)
    def test_024_validate_32_rpz_zone_deleted(self):
        restart_the_grid()
        logging.info("validate 32 RPZ zones deleted")
        reference1=ib_NIOS.wapi_request('GET', object_type="zone_rp")
        if reference1=="[]":
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

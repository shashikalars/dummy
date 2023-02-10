import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
import commands
import json, ast
import requests
from time import sleep as sleep
import pexpect
import paramiko
import time
import sys
from paramiko import client
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

def start_subscriber_collection_services_for_added_site(member):
    get_ref=ib_NIOS.wapi_request('GET', object_type='member:parentalcontrol?name='+member)
    get_ref=json.loads(get_ref)
    ref=get_ref[0]["_ref"]
    logging.info(ref)
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
    time.sleep(20)
    get_ref=ib_NIOS.wapi_request('GET', object_type='member:parentalcontrol?name='+member)
    get_ref=json.loads(get_ref)
    if get_ref[0]["enable_service"]==True:
        logging.info ("Test case passed")
        time.sleep(40)
        return get_ref[0]["enable_service"]
        logging.info ("subscriber service is started")
    else:
        logging.info("Not able to start subscriber service")
        return None

def stop_subscriber_collection_services_for_added_site(member):#config.grid_fqdn
    get_ref=ib_NIOS.wapi_request('GET', object_type='member:parentalcontrol?name='+member)
    get_ref=json.loads(get_ref)
    ref=get_ref[0]["_ref"]
    logging.info(ref)
    data={"enable_service":False}
    reference=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
    logging.info(reference)
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    publish={"member_order":"SIMULTANEOUSLY"}
    request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
    time.sleep(1)
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    get_ref=ib_NIOS.wapi_request('GET', object_type='member:parentalcontrol?name='+member)
    get_ref=json.loads(get_ref)
    if get_ref[0]["enable_service"]==False:
        logging.info ("Test case passed")
        time.sleep(40)
        logging.info ("subscriber service is stopped")
        return get_ref[0]["enable_service"]
    else:
        logging.info("Not able to stop subscriber service")
        return None


class Network(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_001_start_DCA_service(self):
        logging.info("starting DCA service in the Grid member...\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        logging.info(get_ref)
        logging.info(get_ref)
        res = json.loads(get_ref)
        logging.info(res)
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"enable_dns": True,"enable_dns_cache_acceleration": True}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        logging.info(response)
        sleep(300)
        logging.info (response)
        logging.info("DCA service started in the Grid member")
        logging.info("Test Case 1 Execution Completed")
    
    @pytest.mark.run(order=3)
    def test_002_Validate_DCA_service_running(self):
        logging.info("Validate_DCA_service_running")
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -2000 /infoblox/var/infoblox.log"'
        out1 = commands.getoutput(sys_log_validation)
        logging.info (out1)
        logging.info(out1)
        assert re.search(r'DNS cache acceleration is now started',out1)
        logging.info("Test Case 3 Execution Completed") 
    
    @pytest.mark.run(order=5)
    def test_003_Start_DNS_Service(self):
        logging.info("Start DNS Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        logging.info(get_ref)
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
        logging.info("Test Case 5 Execution Completed")
    
    @pytest.mark.run(order=6)
    def test_004_Validate_DNS_service_Enabled(self):
        logging.info("Validate DNs Service is enabled")
        get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
        logging.info(get_tacacsplus)
        res = json.loads(get_tacacsplus)
        logging.info(res)
        for i in res:
            logging.info("found")
            assert i["enable_dns"] == True
        logging.info("Test Case 6 Execution Completed")
        logging.info("============================")

    @pytest.mark.run(order=7)
    def test_005_modify_grid_dns_properties(self):
        logging.info("Mofifying GRID dns properties")
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:dns")
        get_ref1=json.loads(get_ref)[0]['_ref']
        logging.info(get_ref1)
        data={"allow_recursive_query":True,"allow_query":[{"_struct": "addressac","address":"Any","permission":"ALLOW"}],"forwarders":[config.forwarder_ip],"logging_categories":{"log_rpz":True,"log_queries":True,"log_responses":True}}
        put_ref=ib_NIOS.wapi_request('PUT', object_type=get_ref1,fields=json.dumps(data))
        logging.info(put_ref)
        if type(put_ref)!=tuple:
            logging.info("Test Case 8 Execution Passed")
            assert True
        else:
            logging.info("Test Case 8 Execution Failed")
            assert False

    @pytest.mark.run(order=8)
    def test_006_validate_grid_dns_properties(self):
        logging.info("Validating GRID dns properties")
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:dns?_return_fields=allow_recursive_query,forwarders")
        get_ref1=json.loads(get_ref)
        if get_ref1[0]["allow_recursive_query"]==True and get_ref1[0]["forwarders"]==[config.forwarder_ip]:
            logging.info("Test Case 8 Execution Passed")
            assert True
        else:
            logging.info("Test Case 8 Execution Failed")
            assert False

    @pytest.mark.run(order=9)
    def test_007_modify_grid_settings(self):
        logging.info("Mofifying GRID properties")
        response = ib_NIOS.wapi_request('GET', object_type="grid")
        response = json.loads(response)
        response=response[0]["_ref"]
        data={"dns_resolver_setting": {"resolvers": ["127.0.0.1"]}}
        res = ib_NIOS.wapi_request('PUT', object_type=response,fields=json.dumps(data))
        logging.info(res)
        if type(res)!=tuple:
            logging.info("Test Case 9 Execution Passed")
            assert True
        else:
            logging.info("Test Case 9 Execution Failed")
            assert False
    
    @pytest.mark.run(order=10)
    def test_008_validate_grid_settings(self):
        logging.info("Validating GRID properties")
        response = ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=dns_resolver_setting")
        response = json.loads(response)
        response=response[0]["dns_resolver_setting"]["resolvers"]
        if response==["127.0.0.1"]:
            logging.info("Test Case 10 Execution Passed")
            assert True
        else:
            logging.info("Test Case 10 Execution Failed")
            assert False
    
    @pytest.mark.run(order=11)
    def test_009_enable_parental_control(self):
        logging.info("enabling parental control")
        response = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber")
        response = json.loads(response)
        response=response[0]["_ref"]
        logging.info(response)
        data={"enable_parental_control": True,"cat_acctname":"infoblox_sdk", "cat_password":"LinWmRRDX0q","category_url":"https://dl.zvelo.com/","proxy_url":"http://"+config.zvelo_proxy+":8001", "proxy_username":config.zvelo_username, "proxy_password":config.zvelo_password,"pc_zone_name":"parental_control", "cat_update_frequency":24}
        res = ib_NIOS.wapi_request('PUT', object_type=response,fields=json.dumps(data))
        logging.info(res)
        if type(res)==tuple:
            if res[0]==400 or res[0]==401:
                logging.info("Test case 11 execution failed")
                assert False
            else:
                logging.info("Test Case 11 execution passed")
        else:
            logging.info("Test Case 11 execution passed")
            assert True
   
    @pytest.mark.run(order=12)
    def test_010_validate_parental_control_enabled(self):
        logging.info("validating parental control is enabled")
        response = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber?_return_fields=enable_parental_control")
        print response
        response = json.loads(response)
        response=response[0]["enable_parental_control"]
        if response==True:
            logging.info("Test Case 12 execution passed")
            assert True
        else:
            logging.info("Test Case 12 execution failed")
            assert False

    @pytest.mark.run(order=13)
    def  test_011_add_subscriber_site(self):
        logging.info("Adding subscriber site site3")
        data={"blocking_ipv4_vip1": "2.4.5.6","msps":[{"ip_address": config.proxy_server1}],"spms": [{"ip_address": "10.12.11.11"}],"name":"site3","maximum_subscribers":100000,"members":[{"name":config.grid_fqdn}],"nas_gateways":[{"ip_address":"2.2.2.2","name":"nas1","shared_secret":"test123"}]}
        get_ref=ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data))
        logging.info(get_ref)
        print(get_ref)
        if type(get_ref)!=tuple:
            reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
            reference=json.loads(reference)
            if reference[0]["name"]==data["name"]:
                logging.info("Test case 10 execution passed")
                assert True
            else:
                logging.info("Test case 13 execution Failed")
                assert False
        else:
            logging.info(get_ref)
            logging.info("Test case 13 execution failed")
            assert False

    @pytest.mark.run(order=14)
    def  test_012_validate_for_subscriber_site(self):
        logging.info("validating subscriber site site3 added")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        reference=json.loads(reference)
        if reference[0]["name"]=="site3":
            logging.info("Test case 14 execution passed")
            assert True
        else:
            logging.info("Test case 14 execution failed")
            assert False

    @pytest.mark.run(order=15)
    def test_013_start_subscriber_collection_services_for_added_site(self):
        logging.info("Starting subscriber collection services")
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
                logging.info("Test Case 15 Execution Passed")
                assert True
            else:
                logging.info("Test Case 15 Execution Failed")
                assert False
    
    @pytest.mark.run(order=16)
    def test_014_Validate_subscriber_service_is_running(self):
        logging.info("Validating subscriber collection services started")
        get_ref=ib_NIOS.wapi_request('GET', object_type="member:parentalcontrol")
        get_ref=json.loads(get_ref)
        for ref in get_ref:
            if get_ref[0]["enable_service"]==True:
                time.sleep(60)
                logging.info("Test Case 16 Execution Passed")
                assert True
            else:
                logging.info("Test Case 16 Execution Failed")
                assert False

    @pytest.mark.run(order=17)
    def test_015_start_category_download_Messages_logs(self):
        logging.info("Starting category_download Messages")
        log("start","/storage/zvelo/log/category_download.log",config.grid_vip)
        logging.info("Test case 17 execution passed")
        time.sleep(2300)

    @pytest.mark.run(order=18)
    def test_016_stop_category_download_Messages_logs(self):
        logging.info("Stopping category_download Messages")
        log("stop","/storage/zvelo/log/category_download.log",config.grid_vip)
        logging.info("Test case 18 execution passed")
    
    @pytest.mark.run(order=19)
    def test_017_validate_for_ufcclient_data(self):
        time.sleep(40)
        logging.info("Validating Sylog Messages Logs")
        LookFor="zvelodb download completed"
        logs=logv(LookFor,"/storage/zvelo/log/category_download.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 19 Execution passed")
            assert True
        else:
            logging.info("Test Case 19 Execution failed")
            assert False
    
    @pytest.mark.run(order=20)
    def test_018_add_32_rpz_zone(self):
        logging.info("Adding 32 RPZ zones")
        for i in range(31,-1,-1):
            print str(i)
            #data={"fqdn": "rpz"+str(i)+".com","grid_primary":[{"name": config.grid_fqdn,"stealth":False},{"name": config.grid_fqdn1,"stealth":False},{"name": config.grid_fqdn2,"stealth":False}]}
            data={"fqdn": "rpz"+str(i)+".com","grid_primary":[{"name": config.grid_fqdn,"stealth":False}]}
            reference1=ib_NIOS.wapi_request('POST', object_type="zone_rp",fields=json.dumps(data))
            logging.info(reference1)
            print reference1
            logging.info("adding RPZ zone ")
            data={"name":"pass"+str(i)+".rpz"+str(i)+".com","rp_zone":"rpz"+str(i)+".com","canonical":"pass"+str(i)}
            reference2=ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
            logging.info(reference2)
            print reference2
            data={"name":"nxd"+str(i)+".rpz"+str(i)+".com","rp_zone":"rpz"+str(i)+".com","canonical":""}
            reference3=ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
            logging.info(reference3)
            print reference3
            if type(reference1)!=tuple or type(reference2)!=tuple or type(reference3)!=tuple:
                logging.info("Test Case 20 Execution passed")
                assert True
            else:
                logging.info("Test Case 20 Execution failed")
                assert False
    
    @pytest.mark.run(order=21)
    def test_019_restart_the_grid(self):
        logging.info("Restaring the grid")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(60)
        logging.info("Test Case 21 Execution passed")
    
    @pytest.mark.run(order=22)
    def test_020_validate_32_rpz_zone_added(self):
        logging.info("validate 32 rpz zone added")
        reference1=ib_NIOS.wapi_request('GET', object_type="zone_rp")
        #reference1=json.loads(reference1)
        for i in range(32):
            if "rpz"+str(i)+".com" in reference1:
                logging.info("Test case 22 execution passed")
                assert True
            else:
                logging.info("Test case 22 execution failed")
                assert False
    
    @pytest.mark.run(order=27)
    def test_021_disable_subscriber_service(self):
        logging.info("Disabling subscriber service")
        res=stop_subscriber_collection_services_for_added_site(config.grid_fqdn)
        if res!=None:
            logging.info("Test case 27 execution passed")
            assert True
        else:
            logging.info("Test case 27 execution failed")
            assert False

    @pytest.mark.run(order=28)
    def test_022_validate_subscriber_service_is_disabled(self):
        logging.info("validating subscriber site is disabled")
        get_ref=ib_NIOS.wapi_request('GET', object_type='member:parentalcontrol?name='+config.grid_fqdn)
        get_ref=json.loads(get_ref)
        ref=get_ref[0]["enable_service"]
        if ref==False:
            logging.info("Test case 28 execution passed")
            assert True
        else:
            logging.info("Test case 28 execution failed")
            assert False

    @pytest.mark.run(order=29)
    def test_023_disable_proxy_rpz_passthru(self):
        logging.info("disable_proxy_rpz_passthru")
        ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=proxy_rpz_passthru")
        ref=json.loads(ref)
        ref1=ref[0]["_ref"]
        data={"proxy_rpz_passthru":False}
        ref=ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
        if type(ref)!=tuple:
            logging.info(ref)
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            time.sleep(1)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            time.sleep(20)
            logging.info("test case 87 Execution passed")
            assert True
        else:
            logging.info("test case 87 Execution failed")
            assert False

    @pytest.mark.run(order=30)
    def test_024_validate_proxy_rpz_passthru_is_disabled(self):
        restart_the_grid()
        logging.info("Disabling proxy rpz passthru")
        ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=proxy_rpz_passthru")
        ref=json.loads(ref)
        data=ref[0]["proxy_rpz_passthru"]
        if data==False:
            logging.info("Test case 30 execution passed")
            assert True
        else:
            logging.info("Test case 30 execution failed")
            assert False

    @pytest.mark.run(order=31)
    def test_025_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 31 passed")

    @pytest.mark.run(order=32)
    def test_026_Query_all_32_RPZ_Passthru_when_Subscriber_Service_and_Proxy_RPZ_Passthru_are_disabled(self):
        try:
            logging.info("Query PCP and WPCP domain 'playboy.com'")
            for i in range(32):
                dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@10.36.0.151 "dig @'+str(config.grid_vip)+' pass'+str(i)+' +noedns -b 10.36.0.151"'
                dig_cmd1 = os.system(dig_cmd)
            logging.info("Test case 33 execution passed")
            assert True
        except:
            logging.info("Test case 33 execution failed")
            assert False
        sleep(30)

    @pytest.mark.run(order=33)
    def test_027_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 33 Execution Completed")

    @pytest.mark.run(order=34)
    def test_028_Validate_all_these_32_RPZ_Passthru_returns_Public_IPs_in_response(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(32):
            LookFor="response.*NOERROR.*pass"+str(i)+".*IN.*A"
            logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
            logging.info(logs)
            if logs!=None:
                logging.info(logs)
                logging.info("Test Case 34 Execution Passed")
                assert True
            else:
                logging.info("Test Case 34 Execution Failed")
                assert False
    
    @pytest.mark.run(order=35)
    def test_029_Validate_CEF_Log_for_PASSTHRU_in_syslog_for_first_5_zones(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(5):
            LookFor="pass"+str(i)+".rpz"+str(i)+".com.*CAT=RPZ"
            logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
            LookFor2="PASSTHRU"
            logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
            logging.info(logs2)
            if logs!=None and logs2!=None:
                logging.info(logs)
                logging.info("Test Case 35 Execution Passed")
                assert True
            else:
                logging.info("Test Case 35 Execution Failed")
                assert False
    
    @pytest.mark.run(order=47)
    def test_030_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel-cache')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache is empty.*',c)
        logging.info("Test case 47 execution Completed")


    @pytest.mark.run(order=36)
    def test_036_Validate_all_these_32_RPZ_Passthru_rules_did_not_cache_in_dca(self):
        logging.info("Validate all these 32 RPZ Passthru rules did not cache in dca")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test Case 36 Execution Completed")

    @pytest.mark.run(order=37)
    def test_037_Enable_subscriber_service(self):
        logging.info("Enabling subscriber service")
        res=start_subscriber_collection_services_for_added_site(config.grid_fqdn)
        if res!=None:
            logging.info("Test Case 37 Execution Passed")
            assert True
        else:
            logging.info("Test Case 37 Execution Failed")
            assert False

    @pytest.mark.run(order=38)
    def test_038_validate_subscriber_service_is_enabled(self):
        logging.info("validate subscriber service is enabled")
        get_ref=ib_NIOS.wapi_request('GET', object_type='member:parentalcontrol?name='+config.grid_fqdn)
        get_ref=json.loads(get_ref)
        ref=get_ref[0]["enable_service"]
        if ref==True:
            logging.info("Test case 38 execution passed")
            assert True
        else:
            logging.info("Test case 38 execution failed")
            assert False 

    @pytest.mark.run(order=39)
    def test_039_Add_Subscriber_Record_with_SSP_set_to_0(self):
        try:
            logging.info("Add Subscriber Record with SSP bit set to 0")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip+' 32 N/A N/A "ACS:Acct-Session-Id=9999732d-34590346;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=00;PCC:PC-Category-Policy=00000000000000000000000000000001;SUB:Calling-Station-Id=110361221;BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;IPA:IP6=2620:10a:6000:2500:230:48ff:fed5:d928;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+'"')
            child.expect('Record successfully added')
            logging.info("Test Case 39 Execution Passed")
            assert True
        except:
            logging.info("Test Case 39 Execution Failed")
            assert False
    
    @pytest.mark.run(order=40)
    def test_040_Validate_Subscriber_Record_with_SSP_set_to_0(self):
        logging.info("ValidatingSubscriber record SSP set to 0")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*10.36.0.151/32|LID:N/A|IPS:N/A.*',c)
        logging.info("Test case 40 execution completed")

    @pytest.mark.run(order=41)
    def test_041_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 41 passed")

    @pytest.mark.run(order=42)
    def test_042_Query_First_5_RPZ_Passthru_rules_when_subscriber_service_is_enabled(self):
        try:
            logging.info("Query PCP and WPCP domain 'playboy.com'")
            for i in range(5):
                dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@10.36.0.151 "dig @'+str(config.grid_vip)+' pass'+str(i)+' +noedns -b 10.36.0.151"'
                dig_cmd1 = os.system(dig_cmd)
            logging.info("Test Case 42 Execution Passed")
            assert True
        except:
            logging.info("Test Case 42 Execution failed")
            assert False
        sleep(30)

    @pytest.mark.run(order=43)
    def test_043_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 43 Execution Completed")

    @pytest.mark.run(order=44)
    def test_044_Validate_all_these_5_RPZ_Passthru_returns_Public_IPs_in_response(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(5):
            LookFor="response.*NOERROR.*pass"+str(i)+".*IN.*A"
            logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
            logging.info(logs)
            if logs!=None:
                logging.info(logs)
                logging.info("Test Case 44 Execution passed")
                assert True
            else:
                logging.info("Test Case 44 Execution Failed")
                assert False

    @pytest.mark.run(order=45)
    def test_045_Validate_CEF_Log_for_PASSTHRU_in_syslog(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(5):
            LookFor="PASSTHRU rewrite pass"+str(i)+".* via pass"+str(i)+".rpz"+str(i)+".com"
            logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
            logging.info(logs)
            LookFor2="CAT=RPZ"
            logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
            logging.info(logs2)
            if logs!=None and logs2!=None:
                logging.info(logs)
                logging.info("Test Case 45 Execution Passed")
                assert True
            else:
                logging.info("Test Case 45 Execution Failed")
                assert False

    @pytest.mark.run(order=46)
    def test_046_Validate_all_these_5_RPZ_Passthru_rules_did_not_cache_in_dca(self):
        logging.info("Validating 5 RPZ passthru rules did not cache in DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test case 46 execution Passed")

    @pytest.mark.run(order=47)
    def test_047_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel-cache')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache is empty.*',c)
        logging.info("Test case 47 execution Completed")
    
    @pytest.mark.run(order=48)
    def test_048_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 48 passed")

    @pytest.mark.run(order=49)
    def test_049_Query_Next_6_to_30_RPZ_Passthru_rules_when_subscriber_service_is_enabled(self):
        try:
            logging.info("Query PCP and WPCP domain 'playboy.com'")
            for i in range(5,31):
                dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@10.36.0.151 "dig @'+str(config.grid_vip)+' pass'+str(i)+' +noedns -b 10.36.0.151"'
                dig_cmd1 = os.system(dig_cmd)
            logging.info("test case 49 execution passed")
            assert True
        except:
            logging.info("test case 49 execution failed")
            assert False
        sleep(30)

    @pytest.mark.run(order=50)
    def test_050_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 50 Execution Completed")

    @pytest.mark.run(order=51)
    def test_051_Validate_next_6_to_30_RPZ_Passthru_returns_Public_IPs_in_response(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(5,31):
            LookFor="response.*NOERROR.*pass"+str(i)+".*IN.*A"
            logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
            logging.info(logs)
            if logs!=None:
                logging.info(logs)
                logging.info("Test Case 51 Execution Passed")
                assert True
            else:
                logging.info("Test Case 51 Execution Failed")
                assert False

    @pytest.mark.run(order=52)
    def test_052_Validate_CEF_Log_for_PASSTHRU_in_syslog_negative_case(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="PASSTHRU"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        if logs==None:
            logging.info(logs)
            logging.info("Test Case 52 Execution Passed")
            assert True
        else:
            logging.info("Test Case 52 Execution Failed")
            assert False

    @pytest.mark.run(order=53)
    def test_053_Validate_all_these_5_RPZ_Passthru_rules_did_not_cache_in_dca(self):
        logging.info("Validating 5 RPZ passthru rules did not cache in DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test case 53 execution Completed")

    @pytest.mark.run(order=54)
    def test_054_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel-cache')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache is empty.*',c)
        logging.info("Test case 54 execution Completed")

    @pytest.mark.run(order=55)
    def test_055_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 55 Execution passed")

    @pytest.mark.run(order=56)
    def test_056_Query_Last_RPZ_Passthru_rule_31_when_subscriber_service_is_enabled(self):
        try:
            logging.info("Query PCP and WPCP domain 'playboy.com'")
            for i in range(31,32):
                dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@10.36.0.151 "dig @'+str(config.grid_vip)+' pass'+str(i)+' +noedns -b 10.36.0.151"'
                dig_cmd1 = os.system(dig_cmd)
            logging.info("test case 56 Execution passed")
            assert True
        except:
            logging.info("test case 56 Execution failed")
            assert False
        sleep(30)

    @pytest.mark.run(order=57)
    def test_057_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 57 Execution Completed")

    @pytest.mark.run(order=58)
    def test_058_Validate_Last_RPZ_Passthru_31_returns_Public_IPs_in_response(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(31,32):
            LookFor="response.*NOERROR.*pass"+str(i)+".*IN.*A"
            logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
            logging.info(logs)
            if logs!=None:
                logging.info(logs)
                logging.info("Test Case 58 Execution Passed")
                assert True
            else:
                logging.info("Test Case 58 Execution Failed")
                assert False

    @pytest.mark.run(order=59)
    def test_059_Validate_CEF_Log_for_PASSTHRU_in_syslog_negative_case(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="PASSTHRU"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        if logs==None:
            logging.info(logs)
            logging.info("Test Case 59 Execution Passed")
            assert True
        else:
            logging.info("Test Case 59 Execution Failed")
            assert False

    @pytest.mark.run(order=60)
    def test_060_Validate_last_RPZ_Passthru_rules_cache_in_dca(self):
        logging.info("Validating last RPZ passthru rules are cached in DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test case 60 execution Completed")

    @pytest.mark.run(order=61)
    def test_061_Validate_DCA_Cache_content_shows_pass31(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel-cache')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*pass31.*',c)
        logging.info("Test case 61 execution Completed")

    @pytest.mark.run(order=62)
    def test_062_enable_proxy_rpz_passthru(self):
        ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        print ref
        ref=json.loads(ref)
        print ref
        ref1=ref[0]["_ref"]
        data={"proxy_rpz_passthru":True}
        ref=ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
        if type(ref)!=tuple:
            logging.info(ref)
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            time.sleep(1)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            time.sleep(20)
            logging.info("test case 62 Execution passed")
            assert True
        else:
            logging.info("test case 62 Execution failed")
            assert False

    @pytest.mark.run(order=63)
    def test_063_validate_proxy_rpz_passthru_is_enabled(self):
         logging.info("Validating Proxy RPZ passthru is enabled")
         ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=proxy_rpz_passthru")
         ref=json.loads(ref)
         data=ref[0]["proxy_rpz_passthru"]
         if data==True:
             logging.info("test case 63 Execution passed")
             assert True
         else:
            logging.info("test case 63 execution failed")
            assert False

    @pytest.mark.run(order=64)
    def test_064_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 64 passed")

    @pytest.mark.run(order=65)
    def test_065_Query_First_5_RPZ_Passthru_rules_when_subscriber_service_is_enabled(self):
        try:
            logging.info("Query PCP and WPCP domain 'playboy.com'")
            for i in range(5):
                dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@10.36.0.151 "dig @'+str(config.grid_vip)+' pass'+str(i)+' +noedns -b 10.36.0.151"'
                dig_cmd1 = os.system(dig_cmd)
            logging.info("test case 65 Execution passed")
            assert True
            
        except:
            logging.info("test case 65 Execution failed")
            assert False
        sleep(30)

    @pytest.mark.run(order=66)
    def test_066_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 66 Execution Completed")

    @pytest.mark.run(order=67)
    def test_067_Validate_all_these_5_RPZ_Passthru_returns_Public_IPs_in_response(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(5):
            LookFor="response.*NOERROR.*pass"+str(i)+".*IN.*A.*10.*196.*"
            logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
            logging.info(logs)
            print logs
            if logs!=None:
                logging.info(logs)
                logging.info("Test Case 67 Execution Passed")
                assert True
            else:
                logging.info("Test Case 67 Execution Failed")
                assert False

    @pytest.mark.run(order=68)
    def test_068_Validate_CEF_Log_for_PASSTHRU_in_syslog(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(5):
            LookFor="PASSTHRU rewrite pass"+str(i)+".* via pass"+str(i)+".rpz"+str(i)+".com"
            logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
            logging.info (logs)
            LookFor2="PASSTHRU"
            logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
            logging.info (logs2)
            if logs!=None and logs2!=None:
                logging.info(logs)
                logging.info("Test Case 68 Execution Passed")
                assert True
            else:
                logging.info("Test Case 68 Execution Failed")
                assert False

    @pytest.mark.run(order=69)
    def test_069_Validate_all_these_5_RPZ_Passthru_rules_did_not_cache_in_dca(self):
        logging.info("Validating 5 RPZ passthru rules did not cache in DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test case 69 execution Completed")

    @pytest.mark.run(order=70)
    def test_070_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel-cache')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache is empty.*',c)
        logging.info("Test case 70 execution Completed")

    @pytest.mark.run(order=71)
    def test_071_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 71 passed")

    @pytest.mark.run(order=72)
    def test_072_Query_Next_6_to_30_RPZ_Passthru_rules_when_subscriber_service_is_enabled(self):
        try:
            logging.info("Query PCP and WPCP domain 'playboy.com'")
            for i in range(5,31):
                dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@10.36.0.151 "dig @'+str(config.grid_vip)+' pass'+str(i)+' +noedns -b 10.36.0.151"'
                dig_cmd1 = os.system(dig_cmd)
            logging.info("test case 72 Execution passed")
            assert True
        except:
            logging.info("test case 72 Execution failed")
            assert False
        sleep(30)

    @pytest.mark.run(order=73)
    def test_073_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 73 Execution Completed")

    @pytest.mark.run(order=74)
    def test_074_Validate_next_6_to_30_RPZ_Passthru_returns_Public_IPs_in_response(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(5,31):
            LookFor="response.*NOERROR.*pass"+str(i)+".*IN.*A"
            logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
            logging.info(logs)
            if logs!=None:
                logging.info(logs)
                logging.info("Test Case 74 Execution Passed")
                assert True
            else:
                logging.info("Test Case 74 Execution Failed")
                assert False

    @pytest.mark.run(order=75)
    def test_075_Validate_CEF_Log_for_PASSTHRU_in_syslog(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="PASSTHRU"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        if logs==None:
            logging.info(logs)
            logging.info("Test Case 75 Execution Passed")
            assert True
        else:
            logging.info("Test Case 75 Execution Failed")
            assert False

    @pytest.mark.run(order=76)
    def test_076_Validate_all_these_5_RPZ_Passthru_rules_did_not_cache_in_dca(self):
        logging.info("Validate_all_these_32_RPZ_Passthru_rules_did_not_cache_in_dca")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test case 76 execution Completed")

    @pytest.mark.run(order=77)
    def test_077_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel-cache')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache is empty.*',c)
        logging.info("Test case 77 execution Completed")
    
    @pytest.mark.run(order=78)
    def test_078_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 78 passed")

    @pytest.mark.run(order=79)
    def test_079_Query_Last_RPZ_Passthru_rule_31_when_subscriber_service_is_enabled(self):
        try:
            logging.info("Query PCP and WPCP domain 'playboy.com'")
            for i in range(31,32):
                dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@10.36.0.151 "dig @'+str(config.grid_vip)+' pass'+str(i)+' +noedns -b 10.36.0.151"'
                dig_cmd1 = os.system(dig_cmd)
            logging.info("test case 79 Execution passed")
            assert True
        except:
            logging.info("test case 79 Execution failed")
            assert False
        sleep(30)

    @pytest.mark.run(order=80)
    def test_080_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 80 Execution Completed")

    @pytest.mark.run(order=81)
    def test_081_Validate_Last_RPZ_Passthru_31_returns_Public_IPs_in_response(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(31,32):
            LookFor="response.*NOERROR.*pass"+str(i)+".*IN.*A"
            #LookFor="imc_open_data_repo_connection(): connected"
            logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
            logging.info(logs)
            if logs!=None:
                logging.info(logs)
                logging.info("Test Case 81 Execution Passed")
                assert True
            else:
                logging.info("Test Case 81 Execution Failed")
                assert False
    
    @pytest.mark.run(order=82)
    def test_082_Validate_CEF_Log_for_PASSTHRU_in_syslog(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="PASSTHRU"
        #LookFor="imc_open_data_repo_connection(): connected"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        if logs==None:
            logging.info(logs)
            logging.info("Test Case 82 Execution Passed")
            assert True
        else:
            logging.info("Test Case 82 Execution Failed")
            assert False

    @pytest.mark.run(order=83)
    def test_083_Validate_last_RPZ_Passthru_rules_cache_in_dca(self):
        logging.info("Validate_all_these_32_RPZ_Passthru_rules_did_not_cache_in_dca")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test case 83 execution Completed")

    @pytest.mark.run(order=84)
    def test_084_Validate_DCA_Cache_content_shows_pass31(self):
        logging.info("Validate passthru queries cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel-cache')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*pass31.*',c)
        logging.info("Test case 84 execution Completed")

    @pytest.mark.run(order=85)
    def test_085_Add_Subscriber_Record_with_SSP_ff(self):
        logging.info("Add Subscriber Record with Proxy-All=1, Dynamic=0, Unknown=0 and with specific 128 bits for PCP and WPCP")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data add '+config.client_ip+' 32 N/A N/A "ACS:Acct-Session-Id=9999732d-34590346;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000000001;SUB:Calling-Station-Id=110361221;BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;IPA:IP6=2620:10a:6000:2500:230:48ff:fed5:d928;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+'"')
        child.expect('Record successfully added')
        logging.info("test case 85 Completed")
   
    @pytest.mark.run(order=86)
    def test_086_Validate_Subscriber_Record_with_SSP_set_to_ff(self):
        logging.info("Validate_Subscriber_Record_with_SSP_set_to_ff")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*10.36.0.151/32|LID:N/A|IPS:N/A.*',c)
        logging.info("Test case 86 execution Completed")

    @pytest.mark.run(order=87)
    def test_087_disable_proxy_rpz_passthru(self):
        logging.info("disable_proxy_rpz_passthru")
        ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=proxy_rpz_passthru")
        ref=json.loads(ref)
        ref1=ref[0]["_ref"]
        data={"proxy_rpz_passthru":False}
        ref=ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
        if type(ref)!=tuple:
            logging.info(ref)
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            time.sleep(1)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            time.sleep(20)
            logging.info("test case 87 Execution passed")
            assert True
        else:
            logging.info("test case 87 Execution failed")
            assert False

    @pytest.mark.run(order=88)
    def test_088_validate_proxy_rpz_passthru_is_disabled(self):
         logging.info("validate_proxy_rpz_passthru_is_disabled")
         ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=proxy_rpz_passthru")
         ref=json.loads(ref)
         data=ref[0]["proxy_rpz_passthru"]
         if data==False:
             logging.info("test case 88 Execution passed")
             assert True
         else:
            logging.info("test case 88 Execution failed")
            assert False

    @pytest.mark.run(order=89)
    def test_089_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 89 Execution Completed")

    @pytest.mark.run(order=90)
    def test_090_Query_First_8_RPZ_Passthru_rules_when_subscriber_service_is_enabled(self):
        try:
            logging.info("Query for first 8 rpz rules")
            for i in range(8):
                dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@10.36.0.151 "dig @'+str(config.grid_vip)+' pass'+str(i)+' +noedns -b 10.36.0.151"'
                dig_cmd1 = os.system(dig_cmd)
            logging.info("test case 90 Execution passed")
            assert True
        except:
            logging.info("test case 90 Execution failed")
            assert False
        sleep(30)

    @pytest.mark.run(order=91)
    def test_091_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 91 Execution Completed")

    @pytest.mark.run(order=92)
    def test_092_Validate_all_these_8_RPZ_Passthru_returns_Public_IPs_in_response(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(8):
            LookFor="response.*NOERROR.*pass"+str(i)+".*IN.*A"
            logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
            logging.info(logs)
            if logs!=None:
                logging.info(logs)
                logging.info("Test Case 92 Execution Passed")
                assert True
            else:
                logging.info("Test Case 92 Execution Failed")
                assert False
    
        
    @pytest.mark.run(order=93)
    def test_093_Validate_CEF_Log_for_PASSTHRU_in_syslog(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(8):
            LookFor="PASSTHRU rewrite pass"+str(i)+".* via pass"+str(i)+".rpz"+str(i)+".com"
            logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
            logging.info (logs)
            LookFor2="PASSTHRU"
            logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
            logging.info (logs2)
            if logs!=None and logs2!=None:
                logging.info(logs)
                logging.info("Test Case 93 Execution Passed")
                assert True
            else:
                logging.info("Test Case 93 Execution Failed")
                assert False

    @pytest.mark.run(order=94)
    def test_094_Validate_all_these_5_RPZ_Passthru_rules_did_not_cache_in_dca(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test case 94 execution Completed")

    @pytest.mark.run(order=95)
    def test_095_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel-cache')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache is empty.*',c)
        logging.info("Test case 95 execution Completed")

    @pytest.mark.run(order=96)
    def test_096_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 96 Execution Completed")

    @pytest.mark.run(order=97)
    def test_097_Query_next_24_RPZ_Passthru_rules(self):
        try:
            logging.info("Query PCP and WPCP domain 'playboy.com'")
            for i in range(9,31):
                dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@10.36.0.151 "dig @'+str(config.grid_vip)+' pass'+str(i)+' +noedns -b 10.36.0.151"'
                dig_cmd1 = os.system(dig_cmd)
            logging.info("test case 97 Execution passed")
            assert True
        except:
            logging.info("test case 97 Execution Failed")
            assert False
        sleep(30)

    @pytest.mark.run(order=98)
    def test_098_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 98 Execution Completed")

    @pytest.mark.run(order=99)
    def test_099_Validate_all_these_24_RPZ_Passthru_returns_Public_IPs_in_response(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(9,31):
            LookFor="response.*NOERROR.*pass"+str(i)+".*IN.*A"
            logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
            logging.info(logs)
            print logs
            if logs!=None:
                logging.info(logs)
                logging.info("Test Case 99 Execution Passed")
                assert True
            else:
                logging.info("Test Case 99 Execution Failed")
                assert False

    @pytest.mark.run(order=100)
    def test_100_Validate_CEF_Log_for_PASSTHRU_in_syslog(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="PASSTHRU"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        if logs==None:
            logging.info(logs)
            logging.info("Test Case 100 Execution Passed")
            assert True
        else:
            logging.info("Test Case 100 Execution Failed")
            assert False

    @pytest.mark.run(order=101)
    def test_101_Validate_all_these_5_RPZ_Passthru_rules_did_not_cache_in_dca(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test case 101 execution Completed")

    @pytest.mark.run(order=102)
    def test_102_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel-cache')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache is empty.*',c)
        logging.info("Test case 102 execution Completed")

    @pytest.mark.run(order=103)
    def test_103_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case103 Execution Completed")

    @pytest.mark.run(order=104)
    def test_104_Query_last_RPZ_Passthru_rule(self):
        try:
            logging.info("Query last RPZ passthru rule")
            for i in range(31,32):
                dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@10.36.0.151 "dig @'+str(config.grid_vip)+' pass'+str(i)+' +noedns -b 10.36.0.151"'
                dig_cmd1 = os.system(dig_cmd)
            logging.info("Test case 104 Execution passed")
            assert True
        except:
            logging.info("Test case 104 Execution failed")
            assert False
        sleep(30)

    @pytest.mark.run(order=105)
    def test_105_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 105 Execution Completed")

    @pytest.mark.run(order=106)
    def test_106_Validate_last_RPZ_Passthru_returns_Public_IPs_in_response(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(31,32):
            LookFor="response.*NOERROR.*pass"+str(i)+".*IN.*A"
            logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
            logging.info(logs)
            if logs!=None:
                logging.info(logs)
                logging.info("Test Case 106 Execution Passed")
                assert True
            else:
                logging.info("Test Case 106 Execution Failed")
                assert False

    @pytest.mark.run(order=107)
    def test_107_Validate_CEF_Log_for_PASSTHRU_in_syslog(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="PASSTHRU"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        print logs
        logging.info(logs)
        if logs==None:
            logging.info(logs)
            logging.info("Test Case 107 Execution Passed")
            assert True
        else:
            logging.info("Test Case 107 Execution Failed")
            assert False

    @pytest.mark.run(order=108)
    def test_108_Validate_all_these_5_RPZ_Passthru_rules_did_not_cache_in_dca(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test case 108 execution Completed")

    @pytest.mark.run(order=109)
    def test_109_Validate_DCA_Cache_content_pass31(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel-cache')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*pass31.*',c)
        logging.info("Test case 109 execution Completed")
    
    @pytest.mark.run(order=110)
    def test_110_enable_proxy_rpz_passthru(self):
        logging.info("enable_proxy_rpz_passthru")
        ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=proxy_rpz_passthru")
        ref=json.loads(ref)
        ref1=ref[0]["_ref"]
        data={"proxy_rpz_passthru":True}
        ref=ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
        if type(ref)!=tuple:
            logging.info(ref)
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            time.sleep(1)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            time.sleep(20)
            logging.info("Test case 110 Execution passed")
            assert True
        else:
            logging.info("Test case 110 Execution failed")
            assert False

    @pytest.mark.run(order=111)
    def test_111_validate_proxy_rpz_passthru_is_enabled(self):
         logging.info("validate_proxy_rpz_passthru_is_enabled")
         ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=proxy_rpz_passthru")
         ref=json.loads(ref)
         data=ref[0]["proxy_rpz_passthru"]
         if data==True:
             logging.info("Test case 111 Execution passed")
             assert True
         else:
            logging.info("Test case 111 Execution failed")
            assert False

    @pytest.mark.run(order=112)
    def test_112_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 112 Execution Completed")

    @pytest.mark.run(order=113)
    def test_113_Query_First_8_RPZ_Passthru_rules(self):
        try:
            logging.info("Query last RPZ passthru rule")
            for i in range(8):
                dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@10.36.0.151 "dig @'+str(config.grid_vip)+' pass'+str(i)+' +noedns -b 10.36.0.151"'
                dig_cmd1 = os.system(dig_cmd)
            logging.info("Test Case 113 Execution Passed")
            assert True
        except:
            logging.info("Test Case 113 Execution Failed")
            assert False
        sleep(30)

    @pytest.mark.run(order=114)
    def test_114_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 114 Execution Completed")

    @pytest.mark.run(order=115)
    def test_115_Validate_First_8_RPZ_Passthru_returns_Proxy_IPs_in_response(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(8):
            LookFor="response.*NOERROR.*pass"+str(i)+".*IN.*A.*10.*196.*"
            logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
            logging.info(logs)
            if logs!=None:
                logging.info(logs)
                logging.info("Test Case 115 Execution Passed")
                assert True
            else:
                logging.info("Test Case 115 Execution Failed")
                assert False
    
    @pytest.mark.run(order=116)
    def test_116_Validate_CEF_Log_for_PASSTHRU_in_syslog(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(8):
            LookFor="PASSTHRU rewrite pass"+str(i)+".* via pass"+str(i)+".rpz"+str(i)+".com"
            logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
            logging.info (logs)
            LookFor2="PASSTHRU"
            logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
            logging.info (logs2)
            if logs!=None and logs2!=None:
                logging.info(logs)
                logging.info("Test Case 116 Execution Passed")
                assert True
            else:
                logging.info("Test Case 116 Execution Failed")
                assert False

    @pytest.mark.run(order=117)
    def test_117_Validate_all_these_8_RPZ_Passthru_rules_did_not_cache_in_dca(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test case 117 execution Completed")

    @pytest.mark.run(order=118)
    def test_118_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel-cache')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache is empty.*',c)
        logging.info("Test case 118 execution Completed")

    @pytest.mark.run(order=119)
    def test_119_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 119 Execution Completed")

    @pytest.mark.run(order=120)
    def test_120_Query_next_24_RPZ_Passthru_rule(self):
        try:
            logging.info("Query last RPZ passthru rule")
            for i in range(8,31):
                dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@10.36.0.151 "dig @'+str(config.grid_vip)+' pass'+str(i)+' +noedns -b 10.36.0.151"'
                dig_cmd1 = os.system(dig_cmd)
            logging.info("test case 120 Execution passed")
            assert True
        except:
            logging.info("test case 120 Execution failed")
            assert False
        sleep(30)

    @pytest.mark.run(order=121)
    def test_121_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 121 Execution Completed")

    @pytest.mark.run(order=122)
    def test_122_Validate_next_24_RPZ_Passthru_returns_Public_IPs_in_response(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(8,31):
            LookFor="response.*NOERROR.*pass"+str(i)+".*IN.*A"
            logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
            logging.info(logs)
            if logs!=None:
                logging.info(logs)
                logging.info("Test Case 122 Execution Passed")
                assert True
            else:
                logging.info("Test Case 122 Execution Failed")
                assert False
    
    @pytest.mark.run(order=123)
    def test_123_Validate_CEF_Log_for_PASSTHRU_in_syslog(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="PASSTHRU"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        if logs==None:
            logging.info(logs)
            logging.info("Test Case 123 Execution Passed")
            assert True
        else:
            logging.info("Test Case 123 Execution Failed")
            assert False

    @pytest.mark.run(order=124)
    def test_124_Validate_all_these_24_RPZ_Passthru_rules_did_not_cache_in_dca(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test case 124 execution Completed")

    @pytest.mark.run(order=125)
    def test_125_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel-cache')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache is empty.*',c)
        logging.info("Test case 125 execution Completed")

    @pytest.mark.run(order=126)
    def test_126_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 126 Execution passed")

    @pytest.mark.run(order=127)
    def test_127_Query_Last_RPZ_Passthru_rule(self):
        try:
            logging.info("Query last RPZ passthru rule")
            for i in range(31,32):
                dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@10.36.0.151 "dig @'+str(config.grid_vip)+' pass'+str(i)+' +noedns -b 10.36.0.151"'
                dig_cmd1 = os.system(dig_cmd)
            logging.info("test case 127 Execution passed")
            assert True
        except:
            logging.info("test case 127 Execution failed")
            assert False
        sleep(30)

    @pytest.mark.run(order=128)
    def test_128_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 128 Execution Completed")

    @pytest.mark.run(order=129)
    def test_129_Validate_last_RPZ_Passthru_returns_Public_IPs_in_response(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(31,32):
            LookFor="response.*NOERROR.*pass"+str(i)+".*IN.*A"
            logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
            logging.info(logs)
            if logs!=None:
                logging.info(logs)
                logging.info("Test Case 129 Execution Passed")
                assert True
            else:
                logging.info("Test Case 129 Execution Failed")
                assert False

    @pytest.mark.run(order=130)
    def test_130_Validate_CEF_Log_for_PASSTHRU_in_syslog(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="PASSTHRU"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        if logs==None:
            logging.info(logs)
            logging.info("Test Case 130 Execution Passed")
            assert True
        else:
            logging.info("Test Case 130 Execution Failed")
            assert False

    @pytest.mark.run(order=131)
    def test_131_Validate_last_RPZ_Passthru_rule_cache_in_dca(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test case 131 execution Completed")

    @pytest.mark.run(order=132)
    def test_132_Validate_DCA_Cache_content_shows_pass31(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel-cache')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*pass31.*',c)
        logging.info("Test case 132 execution Completed")
    
    @pytest.mark.run(order=133)
    def test_133_Add_Subscriber_Record_with_SSP_Bit_set_to_ffffffff(self):
        logging.info("Add Subscriber Record with SSP=ffffffff")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data add '+config.client_ip+' 32 N/A N/A "ACS:Acct-Session-Id=9999732d-34590346;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ffffffff;PCC:PC-Category-Policy=00000000000000000000000000000001;SUB:Calling-Station-Id=110361221;BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;IPA:IP6=2620:10a:6000:2500:230:48ff:fed5:d928;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+'"')
        child.expect('Record successfully added')
        logging.info("test case 133 passed")
    
    @pytest.mark.run(order=134)
    def test_134_Validate_Subscriber_Record_with_SSP_set_to_0(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*10.36.0.151/32|LID:N/A|IPS:N/A.*',c)
        logging.info("Test case 134 execution Completed")

    @pytest.mark.run(order=135)
    def test_135_disable_proxy_rpz_passthru(self):
        logging.info("disable_proxy_rpz_passthru")
        ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=proxy_rpz_passthru")
        ref=json.loads(ref)
        ref1=ref[0]["_ref"]
        data={"proxy_rpz_passthru":False}
        ref=ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
        if type(ref)!=tuple:
            logging.info(ref)
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            time.sleep(1)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            time.sleep(20)
            logging.info("test case 135 Execution passed")
            assert True
        else:
            logging.info("test case 135 Execution failed")
            assert False

    @pytest.mark.run(order=136)
    def test_136_validate_proxy_rpz_passthru_is_disabled(self):
         logging.info("validate_proxy_rpz_passthru_is_disabled")
         ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=proxy_rpz_passthru")
         ref=json.loads(ref)
         data=ref[0]["proxy_rpz_passthru"]
         if data==False:
             logging.info("test case 136 Execution passed")
             assert True
         else:
            logging.info("test case 136 Execution failed")
            assert False

    @pytest.mark.run(order=137)
    def test_137_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 137 Execution passed")

    @pytest.mark.run(order=138)
    def test_138_Query_ALL_32_RPZ_Passthru_rules_from_0_to_32(self):
        try:
            logging.info("Query last RPZ passthru rule")
            for i in range(32):
                dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@10.36.0.151 "dig @'+str(config.grid_vip)+' pass'+str(i)+' +noedns -b 10.36.0.151"'
                dig_cmd1 = os.system(dig_cmd)
            logging.info("test case 138 Execution passed")
            assert True
        except:
            logging.info("test case 138 Execution failed")
            assert False
        sleep(30)

    @pytest.mark.run(order=139)
    def test_139_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 139 Execution Completed")

    @pytest.mark.run(order=140)
    def test_140_Validate_All_32_RPZ_Passthru_returns_Public_IPs_in_response(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(32):
            LookFor="response.*NOERROR.*pass"+str(i)+".*IN.*A"
            logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
            logging.info(logs)
            print logs
            if logs!=None:
                logging.info(logs)
                logging.info("Test Case 140 Execution Passed")
                assert True
            else:
                logging.info("Test Case 140 Execution Failed")
                assert False

    @pytest.mark.run(order=141)
    def test_141_Validate_CEF_Log_for_PASSTHRU_in_syslog(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(31):
            LookFor="PASSTHRU rewrite pass"+str(i)+".* via pass"+str(i)+".rpz"+str(i)+".com"
            logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
            logging.info (logs)

            print logs
            LookFor2="PASSTHRU"
            logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
            logging.info (logs2)
            if logs!=None and logs2!=None:
                logging.info(logs)
                logging.info("Test Case 141 Execution Passed")
                assert True
            else:
                logging.info("Test Case 141 Execution Failed")
                assert False

    @pytest.mark.run(order=142)
    def test_142_Validate_all_these_32_RPZ_Passthru_rules_did_not_cache_in_dca(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test case 142 execution Completed")

    @pytest.mark.run(order=143)
    def test_143_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel-cache')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache is empty.*',c)
        logging.info("Test case 143 execution Completed")

    @pytest.mark.run(order=144)
    def test_144_enable_proxy_rpz_passthru(self):
        logging.info("enable_proxy_rpz_passthru")
        ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=proxy_rpz_passthru")
        ref=json.loads(ref)
        ref1=ref[0]["_ref"]
        data={"proxy_rpz_passthru":True}
        ref=ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
        if type(ref)!=tuple:
            logging.info(ref)
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            time.sleep(1)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            time.sleep(20)
            logging.info("test case 144 Execution passed")
            assert True
        else:
            logging.info("test case 144 Execution failed")
            assert False

    @pytest.mark.run(order=145)
    def test_145_validate_proxy_rpz_passthru_is_enabled(self):
         logging.info("validate_proxy_rpz_passthru_is_enabled")
         ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=proxy_rpz_passthru")
         ref=json.loads(ref)
         data=ref[0]["proxy_rpz_passthru"]
         if data==True:
             logging.info("test case 145 Execution passed")
             assert True
         else:
            logging.info("test case 145 Execution failed")
            assert False

    @pytest.mark.run(order=146)
    def test_146_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 146 Execution  passed")

    @pytest.mark.run(order=147)
    def test_147_Query_31_RPZ_Passthru_rules_from_0_to_31(self):
        try:
            logging.info("Query last RPZ passthru rule")
            for i in range(31):
                dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@10.36.0.151 "dig @'+str(config.grid_vip)+' pass'+str(i)+' +noedns -b 10.36.0.151"'
                dig_cmd1 = os.system(dig_cmd)
            logging.info("test case 147 Execution passed")
            assert True
        except:
            logging.info("test case 147 Execution failed")
            assert False
        sleep(30)

    @pytest.mark.run(order=148)
    def test_148_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 148 Execution Completed") 

    @pytest.mark.run(order=149)
    def test_149_Validate_31_RPZ_Passthru_returns_Proxy_vips_in_response(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(31):
            LookFor="response.*NOERROR.*pass4.*IN.*A*10.*19*."
            logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
            logging.info(logs)
            if logs!=None:
                logging.info(logs)
                logging.info("Test Case 149 Execution Passed")
                assert True
            else:
                logging.info("Test Case 149 Execution Failed")
                assert False

    @pytest.mark.run(order=150)
    def test_150_Validate_CEF_Log_for_PASSTHRU_in_syslog(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(31):
            LookFor="PASSTHRU rewrite pass"+str(i)+".* via pass"+str(i)+".rpz"+str(i)+".com"
            logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
            logging.info (logs)
            LookFor2="PASSTHRU"
            logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
            logging.info (logs2)
            print logs
            print logs2
            if logs!=None and logs2!=None:
                logging.info(logs)
                logging.info("Test Case 150 Execution Passed")
                assert True
            else:
                logging.info("Test Case 150 Execution Failed")
                assert False
    
    @pytest.mark.run(order=151)
    def test_151_Validate_all_these_32_RPZ_Passthru_rules_did_not_cache_in_dca(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test case 151 execution Completed")

    @pytest.mark.run(order=152)
    def test_152_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel-cache')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache is empty.*',c)
        logging.info("Test case 152 execution Completed")


    @pytest.mark.run(order=153)
    def test_153_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 153 Execution Completed")


    @pytest.mark.run(order=154)
    def test_154_Query_Last_RPZ_Passthru_rule_31(self):
        try:
            logging.info("Query last RPZ passthru rule")
            for i in range(31,32):
                dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@10.36.0.151 "dig @'+str(config.grid_vip)+' pass'+str(i)+' +noedns -b 10.36.0.151"'
                dig_cmd1 = os.system(dig_cmd)
            logging.info("test case 154 Execution passed")
            assert True
        except:
            logging.info("test case 154 Execution failed")
            assert False
        sleep(30)

    @pytest.mark.run(order=155)
    def test_155_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 155 Execution Completed")


    @pytest.mark.run(order=156)
    def test_156_Validate_Last_RPZ_Passthru_returns_Public_ip_in_response(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(31,32):
            LookFor="response.*NOERROR.*pass"+str(i)+".*IN.*A"
            logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
            logging.info(logs)
            if logs!=None:
                logging.info(logs)
                logging.info("Test Case 156 Execution Passed")
                assert True
            else:
                logging.info("Test Case 156 Execution Failed")
                assert False

    @pytest.mark.run(order=157)
    def test_157_Validate_CEF_Log_for_PASSTHRU_in_syslog(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(31,32):
            LookFor="PASSTHRU rewrite pass"+str(i)+".* via pass"+str(i)+".rpz"+str(i)+".com"
            logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
            logging.info (logs)
            LookFor2="PASSTHRU"
            logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
            logging.info (logs2)
            if logs==None and logs2==None:
                logging.info(logs)
                logging.info("Test Case 157 Execution Passed")
                assert True
            else:
                logging.info("Test Case 157 Execution Failed")
                assert False

    @pytest.mark.run(order=158)
    def test_158_Validate_last_RPZ_Passthru_rule_not_cached_in_dca(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test case 158 execution Completed")

    @pytest.mark.run(order=159)
    def test_159_Validate_DCA_Cache_content_shows_cache_is_empty(self):
        logging.info("Validate passthru queries are not cached in DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel-cache')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache is empty.*',c)
        logging.info("Test case 159 execution Completed")

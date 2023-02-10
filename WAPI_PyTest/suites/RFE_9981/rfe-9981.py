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
import socket
from paramiko import client
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)

class SSH:
    client=None

    def __init__(self,address):
        logging.info ("Log Validation Script")
        logging.info ("connecting to server \n : ", address)
        self.client=client.SSHClient()
        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        self.client.connect(address, username='root', pkey = mykey)


    def send_command(self,command):
        if(self.client):
            stdin, stdout, stderr = self.client.exec_command(command)
            result=stdout.readlines()
            return result
        else:
            logging.info("Connection not opened.")



def validate_public_suffix_list (IP_address,command,Host_address=config.client_ip):
    try:
        logging.info ("Checking Log Info")
        connection=SSH(str(IP_address))
        result= connection.send_command(command)
        return result
    except grep:
        logging.info ("Pattern not found")

def change_default_route():
    ref=ib_NIOS.wapi_request('GET', object_type="grid")
    ref=json.loads(ref)[0]['_ref']
    data={"dns_resolver_setting": {"resolvers": [config.resolver_ip]}}
    ref1=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
    child.logfile=sys.stdout
    child.expect('-bash-5.0#')
    child.sendline('ip route del default via 10.35.0.1 dev eth1 table main')
    child.expect('-bash-5.0#')
    child.sendline('ip route add default via 10.36.0.1 dev eth0 table main')
    child.sendline('exit')
    child.expect(pexpect.EOF)
    time.sleep(20)

def enable_mgmt_port_for_dns():
    ref=ib_NIOS.wapi_request('GET', object_type="member:dns")
    ref=json.loads(ref)[0]['_ref']
    data={"use_mgmt_port":True}
    ref1=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
    logging.info (ref1)
    time.sleep(120)

def enable_GUI_and_API_access_through_LAN_and_MGMT():
    ref=ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.Master1_MGMT_IP)
    logging.info (ref)
    ref=json.loads(ref)[0]['_ref']
    logging.info(ref)
    data={"enable_gui_api_for_lan_vip":True}
    ref1=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data),grid_vip=config.Master1_MGMT_IP)
    logging.info (ref1)
    time.sleep(120)

def start_subscriber_collection_services_for_added_site(member):
    get_ref=ib_NIOS.wapi_request('GET', object_type='member:parentalcontrol?name='+member)
    get_ref=json.loads(get_ref)
    ref=get_ref[0]["_ref"]
    logging.info(ref)
    data={"enable_service":True}
    reference=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
    logging.info(reference)
    print("DNS Restart Services")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
    ref = json.loads(grid)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
    sleep(120)
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
    print("DNS Restart Services")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
    ref = json.loads(grid)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
    sleep(120)
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
        enable_mgmt_port_for_dns()
        logging.info("starting DCA service in the Grid member...\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        logging.info(res)
        for i in res:
            ref1=i["_ref"]
            logging.info("Modify a enable_dns")
            data = {"enable_dns": True,"enable_dns_cache_acceleration": True}
            response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
            logging.info(response)
        sleep(360)
        logging.info("Test Case 1 Execution Completed")
        assert True

    @pytest.mark.run(order=2)
    def test_002_start_TP_service(self):
        logging.info("start the TP service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        print get_ref
        logging.info(get_ref)
        res = json.loads(get_ref)
        for i in res:
            ref1=i["_ref"]
            logging.info("Modify a enable_ADP")
            data = {"enable_service": True}
            response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
            print response
            logging.info(response)
        sleep(360)
        logging.info("Test Case 2 Execution Completed")
        assert True

    @pytest.mark.run(order=3)
    def test_003_Validate_DCA_service_running(self):
        logging.info("Validate_DCA_service_running")
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -3000 /infoblox/var/infoblox.log"'
        out1 = commands.getoutput(sys_log_validation)
        logging.info (out1)
        logging.info(out1)
        sys_log_validation2='ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member1_vip)+' " tail -3000 /infoblox/var/infoblox.log"'
        out2 = commands.getoutput(sys_log_validation2)
        logging.info (out2)
        sys_log_validation3 = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member2_vip)+' " tail -3000 /infoblox/var/infoblox.log"'
        out3 = commands.getoutput(sys_log_validation3)
        logging.info (out3)
        logging.info(out3)
        res=re.search(r'DNS cache acceleration is now started',out3) and re.search(r'DNS cache acceleration is now started',out2) and re.search(r'DNS cache acceleration is now started',out3)
        if res is not None:
            logging.info("Test Case 3 Execution passed")
            assert True
        else:
            logging.info("Test Case 3 Execution failed")
            assert False

    @pytest.mark.run(order=4)
    def test_004_Validate_ADP_service_running(self):
        logging.info("Validate_ADP_service_running")
        sys_log_validation2='ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member1_vip)+' " tail -2000 /infoblox/var/infoblox.log"'
        out2 = commands.getoutput(sys_log_validation2)
        logging.info (out2)
        sys_log_validation3 = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member2_vip)+' " tail -4000 /infoblox/var/infoblox.log"'
        out3 = commands.getoutput(sys_log_validation3)
        logging.info (out3)
        logging.info(out3)
        res=re.search(r'Threat Protection service is working',out2) and re.search(r'Threat Protection service is working',out3)
        if res is not None:
            logging.info("Test Case 4 Execution passed")
            assert True
        else:
            logging.info("Test Case 4 Execution failed")
            assert False

    @pytest.mark.run(order=5)
    def test_005_Validate_DCA_service_Enabled(self):
        logging.info("Validate DCA Service is enabled")
        get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns_cache_acceleration")
        logging.info(get_tacacsplus)
        res = json.loads(get_tacacsplus)
        logging.info(res)
        for i in res:
            if i["enable_dns_cache_acceleration"] == True:
                logging.info("Test Case 5 Execution Passed")
                assert True
            else:
                logging.info("Test Case 5 Execution Failed")
                assert False
    
    @pytest.mark.run(order=6)
    def test_006_Validate_ADP_service_Enabled(self):
        logging.info("Validate ADP Service is enabled")
        get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:threatprotection",params="?_return_fields=enable_service")
        logging.info(get_tacacsplus)
        res = json.loads(get_tacacsplus)
        logging.info(res)
        for i in res:
            if i["enable_service"] == True:
                logging.info("Test Case 6 Execution Passed")
                assert True
            else:
                logging.info("Test Case 6 Execution Failed")
                assert False

    @pytest.mark.run(order=7)
    def test_007_Start_DNS_Service(self):
        change_default_route()
        logging.info("Start DNS Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        logging.info(get_ref)
        logging.info(get_ref)
        res = json.loads(get_ref)
        for i in res:
            ref=i["_ref"]
            logging.info("Modify a enable_dns")
            data = {"enable_dns": True,"use_mgmt_port":True}
            response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
            sleep(20)
            logging.info(response)
            if type(response)!=tuple:
                logging.info("Test Case 7 Execution Passed")
                assert True
            else:
                logging.info("Test Case 7 Execution failed")
                assert False

    @pytest.mark.run(order=8)
    def test_008_Validate_DNS_service_Enabled(self):
        logging.info("Validate DNS Service is enabled")
        get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
        logging.info(get_tacacsplus)
        res = json.loads(get_tacacsplus)
        logging.info(res)
        for i in res:
            if i["enable_dns"] == True:
                logging.info("Test Case 8 Execution Passed")
                assert True
            else:
                logging.info("Test Case 8 Execution Failed")
                assert False

    @pytest.mark.run(order=9)
    def test_009_Modify_Grid_Dns_Properties_to_enable_rpz_logging_and_add_forwarder(self):
        logging.info("Mofifying GRID dns propertiesi_to_enable_rpz_logging_and_add_forwarder")
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:dns")
        get_ref1=json.loads(get_ref)[0]['_ref']
        logging.info(get_ref1)
        data={"allow_recursive_query":True,"allow_query":[{"_struct": "addressac","address":"Any","permission":"ALLOW"}],"forwarders":[config.forwarder_ip],"logging_categories":{"log_rpz":True,"log_queries":True,"log_responses":True}}
        put_ref=ib_NIOS.wapi_request('PUT', object_type=get_ref1,fields=json.dumps(data))
        logging.info(put_ref)
        if type(put_ref)!=tuple:
	    print("DNS Restart Services")
       	    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
            ref = json.loads(grid)[0]['_ref']
            data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
            sleep(30)
            logging.info("Test Case 9 Execution Passed")
            assert True
        else:
            logging.info("Test Case 9 Execution Failed")
            assert False

    @pytest.mark.run(order=10)
    def test_010_Validate_Grid_Dns_Properties(self):
        logging.info("Validating GRID dns properties")
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:dns?_return_fields=allow_recursive_query,forwarders")
        get_ref1=json.loads(get_ref)
        if get_ref1[0]["allow_recursive_query"]==True and get_ref1[0]["forwarders"]==[config.forwarder_ip]:
            logging.info("Test Case 10 Execution Passed")
            assert True
        else:
            logging.info("Test Case 10 Execution Failed")
            assert False

    @pytest.mark.run(order=11)
    def test_011_Modify_Grid_Settings_to_add_resolvers(self):
        logging.info("Mofifying GRID properties_to_add_resolvers")
        response = ib_NIOS.wapi_request('GET', object_type="grid")
        response = json.loads(response)
        response=response[0]["_ref"]
        data={"dns_resolver_setting": {"resolvers": [config.resolver_ip]}}
        res = ib_NIOS.wapi_request('PUT', object_type=response,fields=json.dumps(data))
        logging.info(res)
        if type(res)!=tuple:
            logging.info("Test Case 11 Execution Passed")
            assert True
        else:
            logging.info("Test Case 11 Execution Failed")
            assert False
    
    @pytest.mark.run(order=12)
    def test_012_Validate_Modified_Grid_Settings(self):
        logging.info("Validating GRID properties")
        response = ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=dns_resolver_setting")
        response = json.loads(response)
        response=response[0]["dns_resolver_setting"]["resolvers"]
        if response==[config.resolver_ip]:
            logging.info("Test Case 12 Execution Passed")
            assert True
        else:
            logging.info("Test Case 12 Execution Failed")
            assert False

    @pytest.mark.run(order=13)
    def test_013_start_infoblox_logs_on_master_and_two_members(self):
        logging.info("Starting Infoblox Messages Logs on master and two members")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
        log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
        logging.info("Test case 13 execution passed")

    @pytest.mark.run(order=14)
    def test_014_Enable_Parental_Control(self):
        logging.info("enabling parental control")
        response = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber")
        response = json.loads(response)
        response=response[0]["_ref"]
        logging.info(response)
        #data={"enable_parental_control": True,"cat_acctname":"InfoBlox", "cat_password":"CSg@vBz!rx7A","category_url":"https://pitchers.rulespace.com/ufsupdate/web.pl","proxy_url":"http://10.196.9.113:8001", "proxy_username":"client", "proxy_password":"infoblox","pc_zone_name":"parental_control", "ident":"pkFu-yhrf-qPOV-s5BU","cat_update_frequency":24}
        data={"enable_parental_control": True,"cat_acctname":"infoblox_sdk", "cat_password":"LinWmRRDX0q","category_url":"https://dl.zvelo.com/","pc_zone_name":"parental_control","cat_update_frequency":24}
        res = ib_NIOS.wapi_request('PUT', object_type=response,fields=json.dumps(data))
        logging.info(res)
        print res
        if type(res)==tuple:
            if res[0]==400 or res[0]==401:
                logging.info("Test case 14 Execution failed")
                assert False
            else:
                logging.info("Test Case 14 Execution passed")
        else:
            logging.info("Test Case 14 Execution passed")
            assert True

    @pytest.mark.run(order=15)
    def test_015_Validate_Parental_Control_is_Enabled(self):
        logging.info("validating parental control is enabled")
        response = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber?_return_fields=enable_parental_control,cat_acctname,category_url,proxy_url,proxy_username")
        logging.info(response)
        response = json.loads(response)
        pc=response[0]["enable_parental_control"]
        act_name=response[0]["cat_acctname"]
        cat_url=response[0]["category_url"]
        #proxy_url=response[0]["proxy_url"]
        #proxy_username=response[0]["proxy_username"]
        if pc==True and act_name=="infoblox_sdk" and cat_url=="https://dl.zvelo.com/":
            logging.info("Test Case 15 execution passed")
            assert True
        else:
            logging.info("Test Case 15 execution Failed")
            assert False

    @pytest.mark.run(order=16)
    def  test_016_Add_Subscriber_Site_s1_With_Two_Members_In_Site(self):
        logging.info("Adding subscriber site s1")
        data={"name":"s1","maximum_subscribers":100000,"members":[{"name":config.grid_fqdn},{"name":config.grid_member1_fqdn}],"nas_gateways":[{"ip_address":"2.2.2.2","name":"nas1","shared_secret":"test123"}]}
        #data={"name":"s1","maximum_subscribers":100000,"members":[{"name":config.grid_fqdn}],"nas_gateways":[{"ip_address":"2.2.2.2","name":"nas1","shared_secret":"test123"}]}
        get_ref=ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data))
        logging.info(get_ref)
        print get_ref
        logging.info(get_ref)
        if type(get_ref)!=tuple:
            reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
            reference=json.loads(reference)
            if reference[0]["name"]==data["name"]:
                logging.info("Test case 16 execution passed")
                assert True
            else:
                logging.info("Test case 16 execution Failed")
                assert False
        else:
            logging.info(get_ref)
            logging.info("Test case 16 execution Failed")
            assert False

    @pytest.mark.run(order=17)
    def  test_017_validate_for_subscriber_site_s1(self):
        logging.info("validating subscriber site s1 added")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=name,maximum_subscribers")
        reference=json.loads(reference)
        site=reference[0]["name"]
        maximum_subscribers=reference[0]["maximum_subscribers"]
        if site=="s1" and maximum_subscribers==100000:
            logging.info("Test case 17 execution passed")
            assert True
        else:
            logging.info("Test case 17 execution failed")
            assert False
    
    @pytest.mark.run(order=18)
    def  test_018_add_subscriber_site_s2(self):
        logging.info("Adding subscriber site s2")
        data={"name":"s2","maximum_subscribers":100000,"members":[{"name":config.grid_member2_fqdn}],"nas_gateways":[{"ip_address":"2.2.2.2","name":"nas1","shared_secret":"test123"}]}
        get_ref=ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data))
        logging.info(get_ref)
        logging.info(get_ref)
        print get_ref
        if type(get_ref)!=tuple:
            reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
            reference=json.loads(reference)
            print reference[1]["name"]
            if reference[1]["name"]==data["name"]:
                logging.info("Test case 18 execution passed")
                assert True
            else:
                logging.info("Test case 18 execution Failed")
                assert False
        else:
            logging.info(get_ref)
            logging.info("Test case 18 execution failed")
            assert False
    
    @pytest.mark.run(order=19)
    def  test_019_validate_for_subscriber_site_s2(self):
        logging.info("validating subscriber site s2 added")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=name,maximum_subscribers")
        reference=json.loads(reference)
        site=reference[1]["name"]
        maximum_subscribers=reference[0]["maximum_subscribers"]
        if site=="s2" and maximum_subscribers==100000:
            logging.info("Test case 19 execution passed")
            assert True
        else:
            logging.info("Test case 19 execution failed")
            assert False

    @pytest.mark.run(order=20)
    def test_020_start_subscriber_collection_services_for_added_sites(self):
        logging.info("Starting subscriber collection services")
        get_ref=ib_NIOS.wapi_request('GET', object_type="member:parentalcontrol")
        get_ref=json.loads(get_ref)
        logging.info(get_ref)
        for ref in get_ref:
            ref=ref["_ref"]
            data={"enable_service":True}
            reference=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
        print("DNS Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)
        get_ref=ib_NIOS.wapi_request('GET', object_type="member:parentalcontrol")
        get_ref=json.loads(get_ref)
        for ref in get_ref:
            if get_ref[0]["enable_service"]==True:
                time.sleep(60)
                logging.info("Test Case 20 Execution Passed")
                assert True
            else:
                logging.info("Test Case 20 Execution Failed")
                assert False
    
    @pytest.mark.run(order=21)
    def test_021_Validate_subscriber_service_is_running(self):
        logging.info("Validating subscriber collection services started")
        get_ref=ib_NIOS.wapi_request('GET', object_type="member:parentalcontrol")
        get_ref=json.loads(get_ref)
        for ref in get_ref:
            if get_ref[0]["enable_service"]==True:
                time.sleep(60)
                logging.info("Test Case 21 Execution Passed")
                assert True
            else:
                logging.info("Test Case 21 Execution Failed")
                assert False

    @pytest.mark.run(order=22)
    def test_022_start_category_download_Messages_logs_on_master(self):
        logging.info("Starting category download Messages Logs on master")
        log("start","/storage/zvelo/log/category_download.log",config.grid_vip)
        logging.info("Test case 22 execution passed")
        time.sleep(3200)

    @pytest.mark.run(order=23)
    def test_023_stop_category_download_Messages_logs_on_master_and_infoblox_logs_on_master_and_two_members(self):
        logging.info("Stop Syslog Messages Logs on master and member")
        logging.info("Stop category download in master")
        log("stop","/storage/zvelo/log/category_download.log",config.grid_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
        logging.info("Test case 23 execution passed")

    @pytest.mark.run(order=24)
    def test_024_Modify_Grid_Settings_to_add_resolvers(self):
        logging.info("Mofifying GRID properties_to_add_resolvers")
        response = ib_NIOS.wapi_request('GET', object_type="grid")
        response = json.loads(response)
        response=response[0]["_ref"]
        data={"dns_resolver_setting": {"resolvers": ["127.0.0.1",config.resolver_ip]}}
        res = ib_NIOS.wapi_request('PUT', object_type=response,fields=json.dumps(data))
        logging.info(res)
        if type(res)!=tuple:
            logging.info("Test Case 24 Execution Passed")
            assert True
        else:
            logging.info("Test Case 24 Execution Failed")
            assert False

    @pytest.mark.run(order=25)
    def test_025_Validate_Modified_Grid_Settings(self):
        logging.info("Validating GRID properties")
        response = ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=dns_resolver_setting")
        response = json.loads(response)
        response=response[0]["dns_resolver_setting"]["resolvers"]
        if response==["127.0.0.1",config.resolver_ip]:
            logging.info("Test Case 25 Execution Passed")
            assert True
        else:
            logging.info("Test Case 25 Execution Failed")
            assert False

    @pytest.mark.run(order=26)
    def test_026_modify_subscriber_site_s1_to_add_blocking_ips(self):
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        reference=json.loads(reference)[0]["_ref"]
        logging.info("Adding blocking ip's to subscriber site s1")
        data={"blocking_ipv4_vip1": "2.4.5.6","msps":[{"ip_address": config.proxy_server1}],"spms": [{"ip_address": "10.12.11.11"}]}
        get_ref=ib_NIOS.wapi_request('PUT', object_type=reference,fields=json.dumps(data))
        logging.info(get_ref)
        print get_ref
        logging.info(get_ref)
        if type(get_ref)!=tuple:
            reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
            reference=json.loads(reference)
            if reference[0]["name"]=="s1":
                print("DNS Restart Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(30)
                logging.info("Test case 26 execution passed")
                assert True
            else:
                logging.info("Test case 26 execution Failed")
                assert False
        else:
            logging.info(get_ref)
            logging.info("Test case 26 execution Failed")
            assert False
    
    @pytest.mark.run(order=27)
    def  test_027_validate_for_subscriber_site_s1(self):
        logging.info("validating subscriber site s1 added")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=name,blocking_ipv4_vip1,msps,spms")
        reference=json.loads(reference)
        site=reference[0]["name"]
        blocking_ip=reference[0]["blocking_ipv4_vip1"]
        msps=reference[0]["msps"]
        spms=reference[0]["spms"]
        if site=="s1" and blocking_ip=="2.4.5.6" and msps==[{"ip_address": config.proxy_server1}] and spms==[{"ip_address": "10.12.11.11"}]:
            logging.info("Test case 27 execution passed")
            assert True
        else:
            logging.info("Test case 27 execution failed")
            assert False
    
    @pytest.mark.run(order=28)
    def test_028_modify_subscriber_site_s2_to_add_blocking_ips(self):
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        reference=json.loads(reference)[1]["_ref"]
        logging.info("Adding blocking ip's to subscriber site s2")
        data={"blocking_ipv4_vip1": "2.4.5.6","msps":[{"ip_address": config.proxy_server1}],"spms": [{"ip_address": "10.12.11.11"}]}
        get_ref=ib_NIOS.wapi_request('PUT', object_type=reference,fields=json.dumps(data))
        logging.info(get_ref)
        print get_ref
        logging.info(get_ref)
        if type(get_ref)!=tuple:
            reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
            reference=json.loads(reference)
            if reference[1]["name"]=="s2":
                print("DNS Restart Services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(30)
                logging.info("Test case 28 execution passed")
                assert True
            else:
                logging.info("Test case 28 execution Failed")
                assert False
        else:
            logging.info(get_ref)
            logging.info("Test case 28 execution Failed")
            assert False

    @pytest.mark.run(order=29)
    def  test_029_validate_for_subscriber_site_s2(self):
        logging.info("validating subscriber site s1 added")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=name,blocking_ipv4_vip1,msps,spms")
        print reference
        reference=json.loads(reference)
        site=reference[1]["name"]
        blocking_ip=reference[1]["blocking_ipv4_vip1"]
        msps=reference[1]["msps"]
        spms=reference[1]["spms"]
        if site=="s2" and blocking_ip=="2.4.5.6":
            logging.info("Test case 29 execution passed")
            assert True
        else:
            logging.info("Test case 29 execution failed")
            assert False


    @pytest.mark.run(order=30)
    def test_030_validate_for_zvelo_download_data_completion(self):
        time.sleep(40)
        logging.info("Validating category download Messages Logs for data completion")
        LookFor="zvelodb download completed"
        logs=logv(LookFor,"/storage/zvelo/log/category_download.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 30 Execution passed")
            assert True
        else:
            logging.info("Test Case 30 Execution failed")
            assert False
    
    @pytest.mark.run(order=31)
    def test_031_validate_for_public_suffix_data_logs_on_master_to_see_Public_Suffix_List_master_copy_downloaded(self):
        logging.info("validate_for_public_suffix_data_logs_on_master_to_see_Public Suffix List master copy downloaded")
        LookFor="Public Suffix List master copy downloaded"
        LookFor1=".*public_suffix_list.dat reloaded.*"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        logs1=logv(LookFor1,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None or logs1!=None :
            logging.info(logs)
            logging.info("Test Case 31 Execution passed")
            assert True
        else:
            logging.info("Test Case 31 Execution failed")
            assert False
    '''
    @pytest.mark.run(order=32)
    def test_032_validate_for_public_suffix_data_logs_on_member1_to_see_Public_Suffix_List_reloaded_on_member1(self):
        logging.info("validate_for_public_suffix_data_logs_on_member1_to_see_Public_Suffix_List_reloaded_on_member1")
        LookFor1=".*public_suffix_list.dat reloaded.*"
        logs1=logv(LookFor1,"/infoblox/var/infoblox.log",config.grid_member1_vip)
        if logs1!=None :
            logging.info(logs1)
            logging.info("Test Case 32 Execution passed")
            assert True
        else:
            logging.info("Test Case 32 Execution failed")
            assert False
    
    @pytest.mark.run(order=33)
    def test_033_validate_for_public_suffix_data_logs_on_member2_to_see_Public_Suffix_List_reloaded_on_member2(self):
        logging.info("validate_for_public_suffix_data_logs_on_member2_to_see_Public_Suffix_List_reloaded_on_member2")
        LookFor1=".*public_suffix_list.dat reloaded.*"
        logs1=logv(LookFor1,"/infoblox/var/infoblox.log",config.grid_member2_vip)
        if logs1!=None :
            logging.info(logs1)
            logging.info("Test Case 33 Execution passed")
            assert True
        else:
            logging.info("Test Case 33 Execution failed")
            assert False
    '''
    @pytest.mark.run(order=34)
    def test_034_validate_public_suffix_list_file_on_master(self):
        logging.info("validate_public_suffix_list_file_on_master")
        public_suffix_list=validate_public_suffix_list(config.grid_vip,"ls /storage/subscriber_services/ | grep -i 'public_suffix_list.dat'")
        #site=validate_public_suffix_list(config.grid_vip,"ls /storage/subscriber_services/ | grep -i 's1'")
        print public_suffix_list
        if public_suffix_list!=[]:
            logging.info("Test case 34 Execution passed")
            assert True
        else:
            logging.info("Test case 34 Execution failed")
            assert False

    @pytest.mark.run(order=35)
    def test_035_validate_public_suffix_list_file_on_member1(self):
        logging.info("validate_public_suffix_list_file_on_member1")
        public_suffix_list=validate_public_suffix_list(config.grid_member1_vip,"ls /storage/subscriber_services/ | grep -i 'public_suffix_list.dat'")
        #site=validate_public_suffix_list(config.grid_member1_vip,"ls /storage/subscriber_services/ | grep -i 's1'")
        if public_suffix_list!=[]:
            logging.info("Test case 35 Execution passed")
            assert True
        else:
            logging.info("Test case 35 Execution failed")
            assert False
    
    @pytest.mark.run(order=36)
    def test_036_validate_public_suffix_list_file_on_member2(self):
        logging.info("validate_public_suffix_list_file_on_member2")
        public_suffix_list=validate_public_suffix_list(config.grid_member2_vip,"ls /storage/subscriber_services/ | grep -i 'public_suffix_list.dat'")
        #site=validate_public_suffix_list(config.grid_member2_vip,"ls /storage/subscriber_services/ | grep -i 's2'")
        if public_suffix_list!=[]:
            logging.info("Test case 36 Execution passed")
            assert True
        else:
            logging.info("Test case 36 Execution failed")
            assert False
    
    @pytest.mark.run(order=37)
    def test_037_Add_Subscriber_Record_with_whitelist_set_to_netflix_and_blacklist_set_to_linkedin(self):
        try:
            logging.info("Add_Subscriber_Record_with_whitelist_set_to_netflix_and_blacklist_set_to_linkedin")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip+' 32 N/A N/A "ACS:Acct-Session-Id=9999732d-34590346;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';SUB:Calling-Station-Id=110361221;BWI:BWFlag=1;BL=linkedin;WL=netflix;"')
            child.expect('Record successfully added')
            logging.info("Test Case 37 Execution Passed")
            assert True
        except:
            logging.info("Test Case 37 Execution Failed")
            assert False

    @pytest.mark.run(order=38)
    def test_038_Validate_Subscriber_Record_with_whitelist_set_to_netflix_and_blacklist_set_to_linkedin(self):
        logging.info("Validate_Subscriber_Record_with_whitelist_set_to_netflix_and_blacklist_set_to_linkedin")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip+'/32|LID:N/A|IPS:N/A.*',c)
        logging.info("Test case 38 execution completed")

    @pytest.mark.run(order=39)
    def test_039_start_Syslog_Messages_logs_on_master(self):
        logging.info("Starting Syslog Messages Logs on master")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 39 passed")

    @pytest.mark.run(order=40)
    def test_040_Query_linkedin_com(self):
        try:
            logging.info("Query for linkedin.com'")
            dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' linkedin.com +noedns -b '+config.client_ip+'"'
            print dig_cmd
            dig_cmd1 = os.system(dig_cmd)
            logging.info("Test Case 40 Execution Passed")
            assert True
        except:
            logging.info("Test Case 40 Execution failed")
            assert False

    @pytest.mark.run(order=41)
    def test_041_stop_Syslog_Messages_Logs_on_master(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 41 Execution Completed")

    @pytest.mark.run(order=42)
    def test_042_Validate_linkedin_com_returns_Blocked_IPs_in_response(self):
        logging.info("Validate_linkedin_com_returns_Blocked_IPs_in_response")
        logging.info("Validating Sylog Messages Logs")
        LookFor="response.*NOERROR.*linkedin.com.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 42 Execution Passed")
            assert True
        else:
            logging.info("Test Case 42 Execution Failed")
            assert False

    @pytest.mark.run(order=43)
    def test_043_Validate_CEF_Log_for_linkedin_in_syslog(self):
        logging.info("Validate_CEF_Log_for_linkedin_in_syslog")
        LookFor="linkedin.com"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        LookFor1="s1-blocking.parental_control. 0 IN A 2.4.5.6"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        LookFor2="CAT=BL"
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
        logging.info(logs2)
        print logs2
        if logs!=None and logs1!=None and logs2!=None:
            logging.info(logs)
            logging.info("Test Case 43 Execution Passed")
            assert True
        else:
            logging.info("Test Case 43 Execution Failed")
            assert False

    @pytest.mark.run(order=44)
    def test_044_Validate_linkedin_com_did_not_cache_in_dca(self):
        logging.info("Validate_linkedin_com_did_not_cache_in_dca")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test Case 44 Execution Completed")

    @pytest.mark.run(order=45)
    def test_045_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
        logging.info("Validate_DCA_Cache_content_shows_Cache_is_empty")
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
        logging.info("Test Case 45 Execution Completed")

    @pytest.mark.run(order=46)
    def test_046_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 46 Execution completed")

    @pytest.mark.run(order=47)
    def test_047_Query_linkedin_co_uk(self):
        try:
            logging.info("Query for linkedin.co.uk'")
            #dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@10.36.0.151 "dig @'+str(config.grid_vip)+' linkedin.co.uk +noedns -b 10.36.0.151"'
            dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' linkedin.co.uk +noedns -b '+config.client_ip+'"'
            print dig_cmd
            dig_cmd1 = os.system(dig_cmd)
            logging.info("Test Case 47 Execution Passed")
            assert True
        except:
            logging.info("Test Case 47 Execution failed")
            assert False

    @pytest.mark.run(order=48)
    def test_048_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 48 Execution Completed")

    @pytest.mark.run(order=49)
    def test_049_Validate_linkedin_co_uk_returns_Public_IPs_in_response(self):
        logging.info("Validate_linkedin_co_uk_returns_Public_IPs_in_response")
        LookFor="response.*NOERROR.*linkedin.co.uk.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 49 Execution Passed")
            assert True
        else:
            logging.info("Test Case 49 Execution Failed")
            assert False

    @pytest.mark.run(order=50)
    def test_050_Validate_CEF_Log_for_linkedin_co_uk_in_syslog(self):
        logging.info("Validate_CEF_Log_for_linkedin_co_uk_in_syslog")
        LookFor="linkedin.co.uk"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        LookFor1="s1-blocking.parental_control. 0 IN A 2.4.5.6"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        LookFor2="CAT=BL"
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
        logging.info(logs2)
        if logs!=None and logs1!=None and logs2!=None:
            logging.info(logs)
            logging.info("Test Case 50 Execution Passed")
            assert True
        else:
            logging.info("Test Case 50 Execution Failed")
            assert False

    @pytest.mark.run(order=51)
    def test_051_Validate_linkedin_com_did_not_cache_in_dca(self):
        logging.info("Validate_linkedin_com_did_not_cache_in_dca")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test Case 51 execution completed")

    @pytest.mark.run(order=52)
    def test_052_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
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
        logging.info("Test Case 52 execution completed")

    @pytest.mark.run(order=53)
    def test_053_start_Syslog_Messages_logs_on_master(self):
        logging.info("Starting Syslog Messages Logs on master")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 53 passed")

    @pytest.mark.run(order=54)
    def test_054_Query_sub1_linkedin_com(self):
        try:
            logging.info("Query for sub1.linkedin.com'")
            #dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@10.36.0.151 "dig @'+str(config.grid_vip)+' sub1.linkedin.com +noedns -b 10.36.0.151"'
            dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' sub1.linkedin.com +noedns -b '+config.client_ip+'"'
            dig_cmd1 = os.system(dig_cmd)
            logging.info("Test Case 54 Execution Passed")
            assert True
        except:
            logging.info("Test Case 54 Execution failed")
            assert False

    @pytest.mark.run(order=55)
    def test_055_stop_Syslog_Messages_Logs_on_master(self):
        logging.info("Stopping Syslog Logs_on_master")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 55 Execution Completed")

    @pytest.mark.run(order=56)
    def test_056_Validate_sub1_linkedin_returns_Blocked_IPs_in_response(self):
        logging.info("Validate_sub1_linkedin_returns_Blocked_IPs_in_response")
        LookFor="response.*NOERROR.*sub1.linkedin.com.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 56 Execution Passed")
            assert True
        else:
            logging.info("Test Case 56 Execution Failed")
            assert False

    @pytest.mark.run(order=57)
    def test_057_Validate_CEF_Log_for_sub1_linkedin_com_in_syslog(self):
        logging.info("Validate_CEF_Log_for_sub1_linkedin_com_in_syslog")
        LookFor="sub1.linkedin.com"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        LookFor1="s1-blocking.parental_control. 0 IN A 2.4.5.6"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        LookFor2="CAT=BL"
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
        logging.info(logs2)
        if logs!=None and logs1!=None and logs2!=None:
            logging.info(logs)
            logging.info("Test Case 57 Execution Failed")
            assert True
        else:
            logging.info("Test Case 57 Execution Failed")
            assert False

    @pytest.mark.run(order=58)
    def test_058_Validate_sub1_linkedin_com_did_not_cache_in_dca(self):
        logging.info("Validate_sub1_linkedin_com_did_not_cache_in_dca")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test Case 58 execution completed")

    @pytest.mark.run(order=59)
    def test_059_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
        logging.info("Validate_DCA_Cache_content_shows_Cache_is_empty")
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
        logging.info("Test Case 59 execution completed")

    @pytest.mark.run(order=60)
    def test_060_start_Syslog_Messages_logs_on_master(self):
        logging.info("Starting Syslog Messages Logs on master")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 60 passed")

    @pytest.mark.run(order=61)
    def test_061_Query_sub2_linkedin_co_uk(self):
        try:
            logging.info("Query for sub2.linkedin.co.uk'")
            #dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@10.36.0.151 "dig @'+str(config.grid_vip)+' sub2.linkedin.co.uk +noedns -b 10.36.0.151"'
            dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' sub2.linkedin.co.uk +noedns -b '+config.client_ip+'"'
            dig_cmd1 = os.system(dig_cmd)
            logging.info("Test Case 61 Execution Passed")
            assert True
        except:
            logging.info("Test Case 61 Execution failed")
            assert False

    @pytest.mark.run(order=62)
    def test_062_stop_Syslog_Messages_Logs_on_master(self):
        logging.info("Stopping Syslog Logs on Master")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 62 Execution Completed")

    @pytest.mark.run(order=63)
    def test_063_Validate_sub2_linkedin_co_uk_returns_Blocked_IPs_in_response(self):
        logging.info("Validate_sub2_linkedin_co_uk_returns_Blocked_IPs_in_response")
        LookFor="response.*NOERROR.*sub2.linkedin.co.uk.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 63 Execution Passed")
            assert True
        else:
            logging.info("Test Case 63 Execution Failed")
            assert False

    @pytest.mark.run(order=64)
    def test_064_Validate_CEF_Log_for_sub2_linkedin_co_uk_in_syslog(self):
        logging.info("Validate_CEF_Log_for_sub2_linkedin_co_uk_in_syslog")
        LookFor="sub2.linkedin.co.uk"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        LookFor1="s1-blocking.parental_control. 0 IN A 2.4.5.6"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        LookFor2="CAT=BL"
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
        logging.info(logs2)
        if logs!=None and logs1!=None and logs2!=None:
            logging.info(logs)
            logging.info("Test Case 64 Execution Passed")
            assert True
        else:
            logging.info("Test Case 64 Execution Failed")
            assert False

    @pytest.mark.run(order=65)
    def test_065_Validate_sub2_linkedin_co_uk_did_not_cache_in_dca(self):
        logging.info("Validate_sub2_linkedin_co_uk_did_not_cache_in_dca")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test Case 65 execution completed")

    @pytest.mark.run(order=66)
    def test_066_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
        logging.info("Validate_DCA_Cache_content_shows_Cache_is_empty")
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
        logging.info("Test Case 66 execution completed")

    @pytest.mark.run(order=67)
    def test_067_start_Syslog_Messages_logs_on_master(self):
        logging.info("Starting Syslog Messages Logs on master")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 67 passed")

    @pytest.mark.run(order=68)
    def test_068_Query_LINKEDIN_COM(self):
        try:
            logging.info("Query for LINKEDIN.COM'")
            #dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@10.36.0.151 "dig @'+str(config.grid_vip)+' LINKEDIN.COM +noedns -b 10.36.0.151"'
            dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' LINKEDIN.COM +noedns -b '+config.client_ip+'"'
            dig_cmd1 = os.system(dig_cmd)
            logging.info("Test Case 68 Execution Passed")
            assert True
        except:
            logging.info("Test Case 68 Execution failed")
            assert False

    @pytest.mark.run(order=69)
    def test_069_stop_Syslog_Messages_Logs_on_master(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 69 Execution Completed")

    @pytest.mark.run(order=70)
    def test_070_Validate_LINKEDIN_COM_returns_Public_IPs_in_response(self):
        logging.info("Validate_LINKEDIN_COM_returns_Public_IPs_in_response")
        LookFor="response.*NOERROR.*LINKEDIN.COM.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 70 Execution Passed")
            assert True
        else:
            logging.info("Test Case 70 Execution Failed")
            assert False

    @pytest.mark.run(order=71)
    def test_071_Validate_CEF_Log_for_LINKEDIN_COM_in_syslog(self):
        logging.info("Validate_CEF_Log_for_LINKEDIN_COM_in_syslog")
        LookFor="LINKEDIN.COM"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        LookFor1="s1-blocking.parental_control. 0 IN A 2.4.5.6"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        LookFor2="CAT=BL"
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
        logging.info(logs2)
        if logs!=None and logs1!=None and logs2!=None:
            logging.info(logs)
            logging.info("Test Case 71  Execution Passed")
            assert True
        else:
            logging.info("Test Case 71 Execution Failed")
            assert False

    @pytest.mark.run(order=72)
    def test_072_Validate_LINKEDIN_COM_did_not_cache_in_dca(self):
        logging.info("Validate_LINKEDIN_COM_did_not_cache_in_dca")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test Case 72 execution completed")

    @pytest.mark.run(order=73)
    def test_073_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
        logging.info("Validate_DCA_Cache_content_shows_Cache_is_empty")
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
        logging.info("Test Case 73 execution completed")

    @pytest.mark.run(order=74)
    def test_074_start_Syslog_Messages_logs_on_master(self):
        logging.info("Starting Syslog Messages Logs on master")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 74 Execution passed")

    @pytest.mark.run(order=75)
    def test_075_Query_LiNkEdIn_CoM(self):
        try:
            logging.info("Query for LiNkEdIn.CoM'")
            #dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@10.36.0.151 "dig @'+str(config.grid_vip)+' LiNkEdIn.CoM +noedns -b 10.36.0.151"'
            dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' LiNkEdIn.CoM +noedns -b '+config.client_ip+'"'
            dig_cmd1 = os.system(dig_cmd)
            logging.info("Test Case 75 Execution Passed")
            assert True
        except:
            logging.info("Test Case 75 Execution failed")
            assert False

    @pytest.mark.run(order=76)
    def test_076_stop_Syslog_Messages_Logs_on_master(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 76 Execution Completed")

    @pytest.mark.run(order=77)
    def test_077_Validate_LiNkEdIn_CoM_returns_Public_IPs_in_response(self):
        logging.info("Validate_LiNkEdIn_CoM_returns_Public_IPs_in_response")
        LookFor="response.*NOERROR.*LiNkEdIn.CoM.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 77 Execution Passed")
            assert True
        else:
            logging.info("Test Case 77 Execution Failed")
            assert False

    @pytest.mark.run(order=78)
    def test_078_Validate_CEF_Log_for_LiNkEdIn_CoM_in_syslog(self):
        logging.info("Validate_CEF_Log_for_LiNkEdIn_CoM_in_syslog")
        LookFor="LiNkEdIn.CoM"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        LookFor1="s1-blocking.parental_control. 0 IN A 2.4.5.6"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        LookFor2="CAT=BL"
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
        logging.info(logs2)
        if logs!=None and logs1!=None and logs2!=None:
            logging.info(logs)
            logging.info("Test Case 78 Execution Passed")
            assert True
        else:
            logging.info("Test Case 78 Execution Failed")
            assert False

    @pytest.mark.run(order=79)
    def test_079_Validate_LiNkEdIn_CoM__did_not_cache_in_dca(self):
        logging.info("Validate_LiNkEdIn_CoM__did_not_cache_in_dca")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test Case 79 execution completed")

    @pytest.mark.run(order=80)
    def test_080_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
        logging.info("Validate_DCA_Cache_content_shows_Cache_is_empty")
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
        logging.info("Test Case 80 execution completed")

    @pytest.mark.run(order=81)
    def test_081_start_Syslog_Messages_logs_on_master(self):
        logging.info("Starting Syslog Messages Logs on master")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 81 passed")

    @pytest.mark.run(order=82)
    def test_082_Query_Netflix_com(self):
        try:
            logging.info("Query for netflix.com")
            #dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@10.36.0.151 "dig @'+str(config.grid_vip)+' netflix.com +noedns -b 10.36.0.151"'
            dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' netflix.com +noedns -b '+config.client_ip+'"'
            dig_cmd1 = os.system(dig_cmd)
            logging.info("Test Case 82 Execution Passed")
            assert True
        except:
            logging.info("Test Case 82 Execution failed")
            assert False

    @pytest.mark.run(order=83)
    def test_083_stop_Syslog_Messages_Logs_on_master(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 83 Execution Completed")

    @pytest.mark.run(order=84)
    def test_084_Validate_netflix_com_returns_Public_IPs_in_response(self):
        logging.info("Validate_netflix_com_returns_Public_IPs_in_response")
        LookFor="response.*NOERROR.*netflix.com.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 84 Execution Passed")
            assert True
        else:
            logging.info("Test Case 84 Execution Failed")
            assert False


    @pytest.mark.run(order=85)
    def test_085_Validate_netflix_com_cache_in_dca(self):
        logging.info("Validate_netflix_com_cache_in_dca")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test Case 85 execution completed")

    @pytest.mark.run(order=86)
    def test_086_Validate_DCA_Cache_content(self):
        logging.info("Validate_DCA_Cache_content")
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
        assert re.search(r'.*netflix.com.*',c)
        logging.info("Test Case 86 execution completed")

    @pytest.mark.run(order=87)
    def test_087_start_Syslog_Messages_logs_on_master(self):
        logging.info("Starting Syslog Messages Logs on master")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 87 passed")

    @pytest.mark.run(order=88)
    def test_088_Query_Netflix_co_uk(self):
        try:
            logging.info("Query for netflix.co.uk")
            #dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@10.36.0.151 "dig @'+str(config.grid_vip)+' netflix.co.uk +noedns -b 10.36.0.151"'
            dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' netflix.co.uk +noedns -b '+config.client_ip+'"'
            dig_cmd1 = os.system(dig_cmd)
            logging.info("Test Case 88 Execution Passed")
            assert True
        except:
            logging.info("Test Case 88 Execution failed")
            assert False

    @pytest.mark.run(order=89)
    def test_089_stop_Syslog_Messages_Logs_on_master(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 89 Execution Completed")

    @pytest.mark.run(order=90)
    def test_090_Validate_netflix_co_uk_returns_Public_IPs_in_response(self):
        logging.info("Validate_netflix_co_uk_returns_Public_IPs_in_response")
        LookFor="response.*NOERROR.*netflix.co.uk.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 90 Execution Passed")
            assert True
        else:
            logging.info("Test Case 90 Execution Failed")
            assert False

    @pytest.mark.run(order=91)
    def test_091_Validate_netflix_co_uk_cache_in_dca(self):
        logging.info("Validate_netflix_co_uk_cache_in_dca")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test Case 91 execution completed")

    @pytest.mark.run(order=92)
    def test_092_Validate_DCA_Cache_content(self):
        logging.info("Validate_DCA_Cache_content")
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
        assert re.search(r'.*netflix.co.uk.*',c)
        logging.info("Test Case 92 execution completed")

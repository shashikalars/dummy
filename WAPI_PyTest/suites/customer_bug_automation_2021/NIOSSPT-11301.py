########################################################################
#
# File: NIOSSPT-11301.py
#
# 
######################################################################################################################
#  Grid Set up required:                                                                                             #
#  1. Grid Master(IB-v1415)                                                                    #
#  2. Licenses : DNS, DHCP,GRID, RPZ						#
######################################################################################################################
#	  			





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
import sys
import pexpect
import ib_utils.log_capture
from paramiko import client
import paramiko
import shlex
import socket
from subprocess import Popen, PIPE
from ib_utils.log_capture import log_action as log
from ib_utils.log_validation import log_validation as logv
from ib_utils.common_utilities import generate_token_from_file
import pdb
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)


class SSH:
    client=None

    def __init__(self,address):
        logging.info ("connecting to server \n : ", address)
        self.client=client.SSHClient()
        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        self.client.connect(address, username='root', pkey = mykey)

    def send_command(self,command):
        if(self.client):
            stdin, stdout, stderr = self.client.exec_command(command)
            result=stdout.read()
            return result

def scp_to_server(ip,filename):
    SSH_OPTIONS="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
    cmd=":/root/"+filename+" ."
    print ("sshpass scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@"+ip+cmd)
    a=os.system("sshpass scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@"+ip+cmd)



def restart_the_grid():
    logging.info("Restaring the grid")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
    ref = json.loads(grid)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
    sleep(60)
    print("Restrting the grid")

def start_subscriber_collection_services_for_added_site(member):
    for mem in member:
        get_ref=ib_NIOS.wapi_request('GET', object_type='member:parentalcontrol?name='+mem)
        get_ref=json.loads(get_ref)
        ref=get_ref[0]["_ref"]
        print ref
        logging.info(ref)
        data={"enable_service":True}
        reference=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
        logging.info(reference)
        print reference
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    publish={"member_order":"SIMULTANEOUSLY"}
    request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
    time.sleep(1)
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    time.sleep(20)
    for mem in member:
        get_ref=ib_NIOS.wapi_request('GET', object_type='member:parentalcontrol?name='+mem)
        get_ref=json.loads(get_ref)
        if get_ref[0]["enable_service"]==True:
            return True
            print("subscriber service is started in "+mem)
        else:
            return None
            print("Not able to start subscriber service "+mem)
    time.sleep(40)


def stop_subscriber_collection_services_for_added_site(member):#config.grid_member1_fqdn
    for mem in member:
        get_ref=ib_NIOS.wapi_request('GET', object_type='member:parentalcontrol?name='+mem)
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
    for mem in member:
        get_ref=ib_NIOS.wapi_request('GET', object_type='member:parentalcontrol?name='+mem)
        get_ref=json.loads(get_ref)
        if get_ref[0]["enable_service"]==False:
            print ("subscriber service is stopped")
            return True
        else:
            print("Not able to stop subscriber service")
            return None

def delete_subscriber_site(site):
    print ("deleting subscriber site ")
    site_ref = ib_NIOS.wapi_request('GET', object_type='parentalcontrol:subscribersite?name='+site)
    if site_ref!="[]":
        site_ref=json.loads(site_ref)
        site_ref=site_ref[0]['_ref']
        delete=ib_NIOS.wapi_request('DELETE', object_type=site_ref)
        site_ref_new =  ib_NIOS.wapi_request('GET', object_type='parentalcontrol:subscribersite?name='+site)
        if (site_ref_new == '[]'):
            print ("Successfully deleted subscriber site : Test case 047 passed")
            return True
        else:
            print ("Unable to delete subscriber site : test case 047 failed")
            return None
    else:
        print "No sites to delete"
        return True

def reboot(vm_id):
        logging.info("reboot the member")
        for vm in vm_id:
            cmd="reboot_system -H "+str(vm)
            result = subprocess.check_output(cmd, shell=True)
            print result
        time.sleep(300)
        logging.info("Test case executed")

def prod_reboot(ip):
    child = pexpect.spawn('ssh admin@'+ip)
    child.logfile=sys.stdout
#    child.expect(':')
#    child.sendline('yes')
    child.expect(':')
    child.sendline('infoblox')
    child.expect('Infoblox >')
    child.sendline('reboot')
    child.expect('REBOOT THE SYSTEM?')
    child.sendline('y')
    child.expect(pexpect.EOF)
    for i in range(1,20):
        sleep(60)
        status = os.system("ping -c1 -w2 "+ip)
        print(status)
        if status == 0:
            print("System is up")
            break
        else:
            print("System is down")
    sleep(10)
    print("Product Reboot done")

def mem_ref_string(hostname):
    response = ib_NIOS.wapi_request('GET', object_type="member:dns")
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

def mem_ref_string_pc(hostname):
    response = ib_NIOS.wapi_request('GET', object_type="member:parentalcontrol")
    logging.info(response)
    #print(response)
    if type(response)!=tuple:
        ref1 = json.loads(response)
        for key in ref1:
            if key.get('name') == hostname:
                mem_ref = key.get('_ref')
                break
    else:
        print("Failed to get member ref string")
        mem_ref = "NIL"

    return mem_ref

def mem_ref(hostname):
    response = ib_NIOS.wapi_request('GET', object_type="member")
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


def restart_services():
    """
    Restart Services
    """
    print("Restart services")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
    ref = json.loads(grid)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data),grid_vip=config.grid_vip)
    sleep(10)


class NIOSSPT_11301(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_001_Start_DNS_Service(self):
        logging.info("Start DNS Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        logging.info(get_ref)
        res = json.loads(get_ref)
        for i in res:
            ref=i["_ref"]
            logging.info("Modify a enable_dns")
            data = {"enable_dns": True}
            response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
            sleep(5)
            logging.info(response)
            read  = re.search(r'200',response)
            for read in  response:
                assert True
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=2)
    def test_002_Validate_DNS_service_is_Enabled(self):
        logging.info("Validate DNS Service is enabled")
        get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
        logging.info(get_tacacsplus)
        res = json.loads(get_tacacsplus)
        logging.info(res)
        for i in res:
            if i["enable_dns"] == True:
                logging.info("Test Case  Execution Passed")
                assert True
            else:
                logging.info("Test Case  Execution Failed")
                assert False

    @pytest.mark.run(order=3)
    def test_003_enable_mgmt_port_for_dns(self):
        ref=ib_NIOS.wapi_request('GET', object_type="member:dns")
        ref=json.loads(ref)[0]['_ref']
        data={"use_mgmt_port":True}
        ref1=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
        logging.info (ref1)
        time.sleep(120)
	
    @pytest.mark.run(order=4)
    def test_004_add_site_under_subscriber_site(self):
        ''' Enable Parental Control'''
        print("Enable Parental Control")
        get_ref = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber",grid_vip=config.grid_vip)
        print(get_ref)
        data={"enable_parental_control": True,
              "cat_acctname":"infoblox_sdk", 
              "cat_password":"LinWmRRDX0q",
              "category_url":"https://dl.zvelo.com/",
              "proxy_url":"http://10.197.38.38:8001", 
              "proxy_username":"client", 
              "proxy_password":"infoblox",
              "pc_zone_name":"niosspt_9967.zone.com", 
              "cat_update_frequency":24}
        print (json.loads(get_ref)[0]["_ref"])
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]["_ref"],fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Enabling parental control")
                assert False
        sleep(30)
        ''' Add Subscriber Site'''
        print("Add Subscriber Site")
        data={"blocking_ipv4_vip1": "1.1.1.1","blocking_ipv4_vip2": "2.2.2.2",
              "nas_gateways":[{"ip_address": "10.36.0.151","name": "nas1", "shared_secret":"testing123"}],
              "maximum_subscribers": 898989,
              "members": [{"name": str(config.grid_fqdn)}],
              "msps":[{"ip_address": "3.3.3.3"}],
              "name": "site11",
              "nas_port": 1813,
              "spms": [{"ip_address": "4.4.4.4"}]}
        subs_site = ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data),grid_vip=config.grid_vip)
        print(subs_site)
        if type(subs_site) == tuple:
            if subs_site[0]==400 or subs_site[0]==401:
                print("Failure: Adding subscriber site")
                assert False
        
	'''Update Interim Accounting Interval'''
        print("Update Interim Accounting Interval to 60min")
        get_ref = ib_NIOS.wapi_request('GET', object_type='parentalcontrol:subscriber',grid_vip=config.grid_vip)
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps({"interim_accounting_interval":2}),grid_vip=config.grid_vip)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Updating Interim Accounting Interval to 60min")
                assert False
        
        restart_services()


    @pytest.mark.run(order=5)
    def test_005_modifying_in_grid_dns_properties(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 3  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        grid_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns",grid_vip=config.grid_vip)
        grid_ref = json.loads(grid_ref)
        grid_dns_ref = grid_ref[0]['_ref']
        fields = grid_dns_ref + "?_return_fields=allow_query,allow_update,forwarders,logging_categories,allow_recursive_query"
        grid_fields_data = ib_NIOS.wapi_request('GET', object_type=fields,grid_vip=config.grid_vip)
        print("before editing grid : dns properties", grid_fields_data)
        data = {"allow_query": [], "allow_recursive_query": True, "allow_update": [], "forwarders": ["10.0.2.35"],
                "logging_categories": {"log_client": False, "log_config": False, "log_database": False,
                                       "log_dnssec": False, "log_dtc_gslb": False, "log_dtc_health": False,
                                       "log_general": False, "log_lame_servers": False, "log_network": False,
                                       "log_notify": False, "log_queries": False, "log_query_rewrite": False,
                                       "log_rate_limit": False, "log_resolver": False, "log_responses": True,
                                       "log_rpz": True, "log_security": False, "log_update": True,
                                       "log_update_security": False, "log_xfer_in": False, "log_xfer_out": False}}
        condition = ib_NIOS.wapi_request('PUT', ref=grid_dns_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
        print(condition)
        grid = ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        publish = {"member_order": "SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=publish_changes",
                                               fields=json.dumps(publish),grid_vip=config.grid_vip)
        time.sleep(1)
        request_restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=requestrestartservicestatus",grid_vip=config.grid_vip)
        restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=restartservices",grid_vip=config.grid_vip)
        time.sleep(1)
        grid_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns",grid_vip=config.grid_vip)
        grid_ref = json.loads(grid_ref)
        grid_dns_ref = grid_ref[0]['_ref']
        new_fields = grid_dns_ref + "?_return_fields=allow_query,allow_update,forwarders,logging_categories,allow_recursive_query"
        new_grid_fields_data = ib_NIOS.wapi_request('GET', object_type=new_fields,grid_vip=config.grid_vip)
        print("data data performed from GET operation after Modifying from GET operation after Modifying",
              new_grid_fields_data)
        print("data obtained from GET operation before Modifying", grid_fields_data)
        if (grid_fields_data != new_grid_fields_data):
            assert True
            print("Successfully Modified GRID DNS Properties ")
        else:
            assert False
            print("unable to Modify GRID_DNS Properties ")


    


   
    @pytest.mark.run(order=6)
    def test_006_start_subscriber_services(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 07  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        print("------------------------enabling subscriber collection services------------------------------")
        subscriber_services = ib_NIOS.wapi_request('GET', object_type="member:parentalcontrol",grid_vip=config.grid_vip)
        subscriber_services = json.loads(subscriber_services)
        print(subscriber_services)
        print("__________________________________")
        subscriber_ref = subscriber_services[0]['_ref']
        data = {"enable_service": True}
        enable_subscriber_ref = ib_NIOS.wapi_request('PUT', ref=subscriber_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
        print(enable_subscriber_ref)
        sleep(10)
        ####################Restarting the services now ################################
        grid = ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        publish = {"member_order": "SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=publish_changes",
                                               fields=json.dumps(publish),grid_vip=config.grid_vip)
        time.sleep(1)
        request_restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=requestrestartservicestatus",grid_vip=config.grid_vip)
        restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=restartservices",grid_vip=config.grid_vip)
        time.sleep(5)
        com = json.loads(enable_subscriber_ref) + "?_return_fields=enable_service"
        print(com)
        new_member_ref = ib_NIOS.wapi_request('GET', object_type=com,grid_vip=config.grid_vip)
        new_member_ref = json.loads(new_member_ref)
        if (new_member_ref["enable_service"] == data["enable_service"]):
            assert True
            print("Subscriber Collection Service Enabled : Test case 07 passed")
        else:
            assert False
            print("errored out while enabling Subscriber Collection service ")



    @pytest.mark.run(order=7)
    def test_007_Modify_Grid_Settings(self):
        logging.info("Mofifying GRID properties")
        response = ib_NIOS.wapi_request('GET', object_type="grid")
        response = json.loads(response)
        response=response[0]["_ref"]
        data={"dns_resolver_setting": {"resolvers": ["127.0.0.1"]}}
        res = ib_NIOS.wapi_request('PUT', object_type=response,fields=json.dumps(data))
        logging.info(res)
        if type(res)!=tuple:
            logging.info("Test Case 5 Execution Passed")
            assert True
        else:
            logging.info("Test Case 5 Execution Failed")
            assert False

    @pytest.mark.run(order=8)
    def test_008_Validate_Modified_Grid_Settings(self):
        logging.info("Validating GRID properties")
        response = ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=dns_resolver_setting")
        response = json.loads(response)
        print(response)
        response=response[0]["dns_resolver_setting"]["resolvers"]
        print(response)
        if response==["127.0.0.1"] :
            logging.info("Test Case 6 Execution Passed")
            assert True
        else:
            logging.info("Test Case 6 Execution Failed")
            assert False

    @pytest.mark.run(order=9)
    def test_009_Modify_Grid_Dns_Properties(self):
        logging.info("Mofifying GRID dns properties")
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:dns")
        get_ref1=json.loads(get_ref)[0]['_ref']
        logging.info(get_ref1)
        data={"allow_recursive_query":True,"allow_query":[{"_struct": "addressac","address":"Any","permission":"ALLOW"}],"forwarders":[config.forwarder_ip],"logging_categories":{"log_rpz":True,"log_queries":True,"log_responses":True}}
        put_ref=ib_NIOS.wapi_request('PUT', object_type=get_ref1,fields=json.dumps(data))
        logging.info(put_ref)
        if type(put_ref)!=tuple:
            logging.info("Test Case 7 Execution Passed")
            assert True
        else:
            logging.info("Test Case 7 Execution Failed")
            assert False

    @pytest.mark.run(order=10)
    def test_010_Validate_Grid_Dns_Properties(self):
        logging.info("Validating GRID dns properties")
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:dns?_return_fields=allow_recursive_query,forwarders")
        get_ref1=json.loads(get_ref)
        if get_ref1[0]["allow_recursive_query"]==True and get_ref1[0]["forwarders"]==[config.forwarder_ip]:
            logging.info("Test Case 8 Execution Passed")
            assert True
        else:
            logging.info("Test Case 8 Execution Failed")
            assert False

    @pytest.mark.run(order=11)
    def test_011_Enable_Parental_Control_with_only_proxy_url(self):
        logging.info("enabling parental control with only proxy url")
        response = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber")
        response = json.loads(response)
        response=response[0]["_ref"]
        logging.info(response)
        data={"enable_parental_control": True,"cat_acctname":"infoblox_sdk", "cat_password":"LinWmRRDX0q","category_url":"https://dl.zvelo.com/","pc_zone_name":"pc.com","cat_update_frequency":1,"proxy_url":"http://10.197.38.38:8001","proxy_username":"client","proxy_password":"infoblox"}
        res = ib_NIOS.wapi_request('PUT', object_type=response,fields=json.dumps(data))
        logging.info(res)
        print res
        if type(res)==tuple:
            if res[0]==400 or res[0]==401:
                logging.info("Test case 9 Execution failed")
                assert False
            else:
                logging.info("Test Case 9 Execution passed")
        else:
            logging.info("Test Case 9 Execution passed")
            assert True

    @pytest.mark.run(order=12)
    def test_012_Validate_Parental_Control_is_Enabled(self):
        logging.info("validating parental control is enabled")
        response = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber?_return_fields=enable_parental_control")
        logging.info(response)
        response = json.loads(response)
        response=response[0]["enable_parental_control"]
        if response==True:
            logging.info("Test Case 10 execution passed")
            assert True
        else:
            logging.info("Test Case 10 execution Failed")
            assert False
	restart_the_grid()
        
    @pytest.mark.run(order=13)
    def test_013_start_category_download_Messages_logs_on_master(self):
        logging.info("Starting category download Messages Logs on master")
        log("start","/storage/zvelo/log/category_download.log",config.grid_vip)
        logging.info("Test case 11 execution passed")
        time.sleep(1500)



    @pytest.mark.run(order=14)
    def test_014_stop_category_download_Messages_logs_on_master(self):
        logging.info("Stop Syslog Messages Logs on master")
        log("stop","/storage/zvelo/log/category_download.log",config.grid_vip)
        logging.info("Test case 12 execution passed")

    @pytest.mark.run(order=15)
    def test_015_validate_for_zvelo_download_data_completion_on_master(self):
        time.sleep(10)
        logging.info("Validating category download Messages Logs for data completion")
        LookFor="zvelodb download completed"
        logs=logv(LookFor,"/storage/zvelo/log/category_download.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 13 Execution passed")
            assert True
        else:
            logging.info("Test Case 13 Execution failed")
            assert False        

    @pytest.mark.run(order=16)
    def test_016_add_subscriber_secure_data(self):
	logging.info("adding subscriber secure data ")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('set subscriber_secure_data add 10.36.199.7 32 N/A N/A "ACS:Acct-Session-Id=9889732d-34590010;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SUB:Calling-Station-Id=04321012134;PXP:PXY_PRI=0ac4065f;PXS:PXY_SEC=0ac4065f"')
	child.expect('Infoblox >')
	output=child.before
	if 'Record successfully added' in output:
            return True
	    print ("Test case 007 Passed ")
	else:
	    return False
	    print("Test case failed")	
	child.sendline('exit')
	restart_services()

    @pytest.mark.run(order=17)
    def test_017_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 17 passed")
        sleep(10)

    @pytest.mark.run(order=18)
    def test_018_query_parental_control_domain_playboy_com_ipv4(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 23  Started Executing                      ####")
        print("###############################################################################")
        print("This test performs dig by logging in to Client IP")
        query_list = ['playboy.com']
	#pdb.set_trace()
	'''
	args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.199.7"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
	#dig_command = 'dig @' + config.grid_vip + " " + str(record) + " +noedns -b 10.36.199.7"
        for record in query_list:
            dig_command = 'dig @' + config.grid_vip + " " + str(record) + " +noedns -b 10.36.199.7"
            child.stdin.write(dig_command + '\n')
            child.stdin.write("exit")
            output = child.communicate()
	flag=False
	
	
	for record in query_list:
	    output=os.system('dig @' + "10.35.143.8" + " " + str(record) + " -b 10.36.199.7")
	print (output)
	'''
	#for line in output:
	 #   print (line)
	
	dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+ ' playboy.com "'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site11-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site11-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case 32 Execution Completed") 
        sleep(20)
        #print(output)
	'''
	if "connection timed out; no servers could be reached" in output:
	    assert False
	if "site1-blocking.pc.com" in output:
	    assert True
	if not flag:
	    assert False
	'''

    @pytest.mark.run(order=19)
    def test_019_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 19 Execution Completed")


    @pytest.mark.run(order=20)
    def test_020_validate_blockedip_logs(self):
	print("\n")
        print("###############################################################################")
	#log("start","/infoblox/var/infoblox.log",config.grid_vip)
	#log("stop","/infoblox/var/infoblox.log",config.grid_vip)
	LookFor="site11-blocking.pc.com. 0 IN A 1.1.1.1;"
	logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
	logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 20 Execution Passed")
            assert True
        else:
            logging.info("Test Case 20 Execution Failed")
            assert False	

    @pytest.mark.run(order=21)
    def test_021_cleanup(self):
	logging.info("delete the sites created")
	get_ref = ib_NIOS.wapi_request('GET', object_type="member:parentalcontrol",grid_vip=config.grid_vip)
        print(get_ref)
	data= {"enable_service": False}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]["_ref"],fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
	site=ib_NIOS.wapi_request('GET',object_type='parentalcontrol:subscribersite',grid_vip= config.grid_vip)
	print(site)
	site=json.loads(site)[0]['_ref']
	response = ib_NIOS.wapi_request('DELETE', site,grid_vip= config.grid_vip)
	restart_services

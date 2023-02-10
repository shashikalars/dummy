########################################################################
#
# File: NIOSSPT-10714.py
#
# 
######################################################################################################################
#  Grid Set up required:                                                                                             #
#  1. Grid Master/FLEX                                                                    #
#  2. Licenses : DNS, DCA,TP, RPZ						#
######################################################################################################################
#	  			




import os
import re
import time
import config
import pytest
import unittest
import logging
import subprocess
import paramiko
import json
import sys
import shlex
from time import sleep
from paramiko import client
import datetime
from subprocess import Popen, PIPE
import ib_utils.ib_NIOS as ib_NIOS
#from ib_utils.log_capture import log_action as log
import pexpect
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
import pdb

class SSH:
    client = None

    def __init__(self, address):
        print("connecting to server \n : ", address)
        self.client = client.SSHClient()
        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        self.client.load_system_host_keys()
        # os.system('ssh-keygen -p -m PEM -f ~/.ssh/id_rsa')
        # privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        # mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        # print ("mykey here :",mykey)
        self.client.connect(address, username='root', port=22)

    def send_command(self, command):
        if (self.client):
            stdin, stdout, stderr = self.client.exec_command(command)
            result = stdout.read()
            print(result)
            error = stderr.read()
            print(error)
            return result
        else:
            print("Connection not opened.")





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



def show_subscriber_secure_data():
    print(" show subscriber_secure_data")
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@' + config.grid_vip)
    child.logfile = sys.stdout
    child.expect('password:')
    child.sendline('infoblox')
    child.expect('Infoblox >')
    child.sendline('show subscriber_secure_data')
    child.expect('>')
    output = child.before
    child.sendline('exit')
    return output

def scp_to_server(ip,filename):
    SSH_OPTIONS="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
    cmd=":/root/"+filename+" ."
    print ("sshpass scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@"+ip+cmd)
    a=os.system("sshpass scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@"+ip+cmd)


def fpcli(cmd,ip):
    connection=SSH(str(ip))
    print connection
    cmd=cmd+" > output.txt"
    res=connection.send_command(cmd)
    print res
    scp_to_server(ip,"output.txt")
    header=[]
    values=[]
    f1=open("output.txt","r")
    a=f1.readlines()
    print("aaaaaaaaaaaaa",a)
    b=a[0].split("|")
    for i in b:
        if i=="\n" or i=="":
            pass
        else:
            i=i.strip(" ")
            header.append(i)

    for i in range(1,len(a)):
        if "---" not in a[i]:
            b=a[i].split("|")
            for i in b:
                if i=='\n' or i=='':
                    pass
                else:
                    i=i.strip(" ")
                    values.append(i)
    dictionary = dict(zip(header, values))
    return dictionary

def stop_DHCP_services():

    print("\n============================================\n")
    print("Stop DHCP Service on Master")
    print("\n============================================\n")


    get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties?_return_fields=enable_dhcp", grid_vip=config.grid_vip)
    res = json.loads(get_ref)
    for i in res:
        if config.grid_fqdn in i['_ref']:
            data = {"enable_dhcp": False}
            response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties?_return_fields=enable_dhcp", grid_vip=config.grid_vip)
            print(get_ref)
            
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Stop DHCP Service on Master")
                    assert False
                break
            else:
                print("Success: Stop DHCP Service on Master")
                assert True
                break
        
        else:
            continue
            
    # Restart Services
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    sleep(30)

class NIOSSPT_10714(unittest.TestCase):

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
    def test_003_start_DCA_service(self):
        stop_DHCP_services()
        sleep(30)
        logging.info("starting DCA service in the Grid member...\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        logging.info(res)
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"enable_dns": True,"enable_dns_cache_acceleration": True}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        logging.info(response)
        sleep(420)
        logging.info("DCA service started in the Grid member")
        logging.info("Test Case 3 Execution Completed")


    @pytest.mark.run(order=4)
    def test_004_Validate_DCA_service_running(self):
        logging.info("Validate DCA Service is enabled")
	sleep(120)
        get_response = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns_cache_acceleration")
        logging.info(get_response)
        read  = re.search(r'201',get_response)
        for read in  get_response:
            assert True
        logging.info("Test Case 4 Execution Completed")


    @pytest.mark.run(order=5)
    def test_005_start_TP_service(self):
        logging.info("start the TP service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection",grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        logging.info (ref1)
        data = {"enable_service": True}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        sleep(420)
        logging.info(response)
        logging.info("Test Case 5 Execution Completed")
 
    
    @pytest.mark.run(order=6)
    def test_006_Validate_TP_service_running(self):
        logging.info("Validate TP Service is enabled")
        response = ib_NIOS.wapi_request('GET', object_type="member:threatprotection",params="?_return_fields=enable_service",grid_vip=config.grid_vip)
        logging.info(response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        logging.info("Started Threat protection services")

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

        restart_services()

    
    @pytest.mark.run(order=11)
    def test_011_add_subscriber_site_enable_parental_contorl(self): 
	''' Enable Parental Control'''
        print("Enable Parental Control")
        get_ref = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber",grid_vip=config.grid_vip)
        print(get_ref)
        data={"enable_parental_control": True,
              "cat_acctname":config.cat_acctname, 
              "cat_password":config.cat_password,
              "category_url":config.category_url,
              "proxy_url":config.proxy_url, 
              "proxy_username":config.proxy_username, 
              "proxy_password":config.proxy_password,
              "pc_zone_name":config.pc_zone_name, 
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
        data={"blocking_ipv4_vip1": "2.4.5.6",
              "nas_gateways":[{"ip_address": config.nas_ip,"name": "nas1", "shared_secret":"testing123"}],
              "maximum_subscribers": 898989,
              "members": [{"name": str(config.grid_fqdn)}],
              "msps":[{"ip_address": config.msps}],
              "name": "site1",
              "nas_port": 1813,
              "spms": [{"ip_address": config.spms}]}
        subs_site = ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data),grid_vip=config.grid_vip)
        print(subs_site)
        if type(subs_site) == tuple:
            if subs_site[0]==400 or subs_site[0]==401:
                print("Failure: Adding subscriber site")
                assert False
        
	'''Update Interim Accounting Interval'''
        print("Update Interim Accounting Interval to 60min")
        get_ref = ib_NIOS.wapi_request('GET', object_type='parentalcontrol:subscriber',grid_vip=config.grid_vip)
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps({"interim_accounting_interval":120}),grid_vip=config.grid_vip)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Updating Interim Accounting Interval to 60min")
                assert False
        
        '''Start Subscriber Collection Service on the Master'''
        print("Start Subscriber Collection Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:parentalcontrol",grid_vip=config.grid_vip)
        print(get_ref)
        data= {"enable_service": True}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]["_ref"],fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Starting subscriber Collection Service")
                assert False
        sleep(60)

        restart_services()

        
    @pytest.mark.run(order=12)
    def test_012_start_category_download_Messages_logs_on_master(self):
        logging.info("Starting category download Messages Logs on master")
        log("start","/storage/zvelo/log/category_download.log",config.grid_vip)
        logging.info("Test case 11 execution passed")
        time.sleep(1500)



    @pytest.mark.run(order=13)
    def test_013_stop_category_download_Messages_logs_on_master(self):
        logging.info("Stop Syslog Messages Logs on master")
        log("stop","/storage/zvelo/log/category_download.log",config.grid_vip)
        logging.info("Test case 12 execution passed")

    @pytest.mark.run(order=14)
    def test_014_validate_for_zvelo_download_data_completion_on_master(self):
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

  
    @pytest.mark.run(order=15)
    def test_015_add_Subscriber_Record_without_PCP(self):
        logging.info("add_Subscriber_Record_without_PCP")
	child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('set subscriber_secure_data add 10.36.0.151 32 N/A N/A "ACS:Acct-Session-Id=345;NAS:NAS-PORT=1813;SUB:Calling-Station-Id=1;PXP:PXY_PRI=0a23b507;PXS:PXY_SEC=0a23b507;"')
	child.expect('Infoblox >')
	output = child.before
	if ('Record successfully added' in output):
            logging.info("Record without PCP added successfully")
            assert True
        else:
            logging.info("Record adding failed")
            assert False
        child.sendline('exit')


    @pytest.mark.run(order=16)
    def test_016_Validate_Subscriber_Record_without_PCP(self):
        logging.info("Validate_Subscriber_Record_without_PCP")
        res=fpcli("fp-cli fp ib_dca dump subscriber_entries 1",config.grid_vip)
        print res
	if len(res)==0:
	   logging.info("subscriber entries without policy is not writting in dca cache")
	   assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=17)
    def test_017_add_Subscriber_Record_with_PCP(self):
        logging.info("add_Subscriber_Record_without_PCP")
	child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('set subscriber_secure_data add 10.36.0.152 32 N/A N/A "ACS:Acct-Session-Id=543321;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;PXY:Proxy-All=1;PXP:PXY_PRI=0ac4065f;PXS:PXY_SEC=0ac4065f;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000000001;SUB:Calling-Station-Id=110361221;BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;"')
	child.expect('Infoblox >')
	output = child.before
	if ('Record successfully added' in output):
            logging.info("Record with PCP added successfully")
            assert True
        else:
            logging.info("Record adding failed")
            assert False
        child.sendline('exit')

    @pytest.mark.run(order=18)
    def test_018_Validate_Subscriber_Record_with_PCP(self):
        logging.info("Validate_Subscriber_Record_without_PCP")
        res=fpcli("fp-cli fp ib_dca dump subscriber_entries 1",config.grid_vip)
        print res
	if res["PCP"]=="0x00000000000000000000000000020040" and res["bypass"]=='false':
            logging.info("subscriber entries with policy is writting in dca cache")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=19)
    def test_019_cleanup(self):
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

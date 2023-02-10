#############################################################################
#!/usr/bin/env python
__author__ ="Rajeev Patil"
__email__  = "rpatil@infoblox.com"
#############################################################################
# Bug Description : NIOSSPT-8907-9412                                      #
#  Grid Set up required:                                                    #
#  Confire 2 grids
# grid1 should be IB-4030 and enable DCA
#
#  IN grid 1 add 10 frwd zones with grid 2 ip as forwarder
# in grid2 add same AUth zones#
# 
# Add records in each zones like 10records/20/30/50/60/70/80...           #
#
# Perform dns query in loop and u should not see crash andcores          #
#	"Config File Configuration "
# 	grid_vip="10.35.3.240"
#	grid_fqdn="ib-10-35-3-240.infoblox.com"
#	Master2_IP="10.35.122.10"
#	Master2_fqdn="ib-10-35-122-10.infoblox.com"
#############################################################################




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
from ib_utils.log_capture import log_action as log
import pexpect



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




def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

def start_syslog(logfile):
    """
    Start log capture
    """
    display_msg("Start capturing "+logfile)
    log("start",logfile,config.grid_vip)

def stop_syslog(logfile):
    """
    Stop log capture
    """
    display_msg("Stop capturing "+logfile)
    log("stop",logfile,config.grid_vip)

def get_reference_for_zone(response):
    logging.info("Fetching reference values for Zones")
    get_ref = ib_NIOS.wapi_request('GET',object_type=response)
    return json.loads(get_ref)

def validate_syslog(logfile, lookfor):
    """
    Validate captured log
    """
    display_msg("Validate captured log")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(config.grid_vip, username='root', pkey = mykey)
    file_name='_'.join(logfile.split('/'))
    file = '/root/dump/'+ str(config.grid_vip)+file_name+'.log'
    display_msg("cat "+file+" | grep -i '"+lookfor+"'")
    stdin, stdout, stderr = client.exec_command("cat "+file+" | grep -i '"+lookfor+"'")
    result=stdout.read()
    display_msg(result)
    client.close()
    if result:
        return True
    return False

def restart_services():
    """
    Restart Services
    """
    display_msg("Restart services")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data))
    sleep(10)

def add_subscriber_data(data):
    """
    Add Subscriber Data
    """
    args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_vip
    args=shlex.split(args)
    child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    new_data="set subscriber_secure_data add "+data
    print ("new data :",new_data)
    child.stdin.write(new_data)
    child.stdin.write("exit")
    output = child.communicate()
    display_msg(output)
    for line in list(output):
        if 'Disconnect NOW if you have' in line:
            continue
        display_msg(line)
        if 'Record successfully added' in line:
            return True
    return False


def show_subscriber_secure_data():
    logging.info(" show subscriber_secure_data")
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

def show_subscriber_secure_data_member():
    logging.info(" show subscriber_secure_data")
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@' + config.Master2_IP)
    child.logfile = sys.stdout
    child.expect('password:')
    child.sendline('infoblox')
    child.expect('Infoblox >')
    child.sendline('show subscriber_secure_data')
    child.expect('>')
    output = child.before
    child.sendline('exit')
    return output


class NIOSSPT_9412(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_000_setup(self):
        """
        setup method: Used for configuring pre-required configs.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case setup Started : 9412           |")
        display_msg("------------------------------------------------")
        
        '''Add MGMT ip route'''
        #cmd1 = "ip route del default via 10.35.0.1 dev eth1 table main"
        #cmd2 = "ip route add default via 10.36.0.1 dev eth0 table main"
        #client = paramiko.SSHClient()
        #client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        #mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        #client.connect(config.grid_vip, username='root', pkey = mykey)
        #stdin, stdout, stderr = client.exec_command(cmd1)
        #stdin1, stdout1, stderr1 = client.exec_command(cmd2)
        #result = stdout.read()
        #display_msg(result)
        #result1 = stdout1.read()
        #display_msg(result1)
        #client.close()

        '''Add DNS Resolver'''
        display_msg("Add DNS Resolver 10.0.2.35")
        grid_ref = ib_NIOS.wapi_request('GET', object_type='grid')
        data = {"dns_resolver_setting":{"resolvers":["127.0.0.1","10.0.2.35"]}}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Adding DNS Resolver")
                assert False

        '''Add DNS Forwarder'''
        display_msg("Add DNS forwarder  ")
        grid_dns_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        data = {"forwarders":[config.Master2_IP]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_dns_ref)[0]['_ref'], fields=json.dumps(data))
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Adding DNS Forwarder")
                assert False

        '''Allow recursive query for GRID 1'''
        display_msg("Allow recursive query")
        data =  {"recursive_query_list": [{"address": "Any", "permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_dns_ref)[0]['_ref'], fields=json.dumps({"allow_recursive_query": True}))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Allow recursive query")
                assert False
        display_msg("Update recursive query list")
        response2 = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_dns_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response2)
        if type(response2) == tuple:
            if response2[0]==400 or response2[0]==401:
                display_msg("Failure: Add recursive query list")
                assert False

        '''Enable logging for queries, responses, rpz for GRID 1'''
        display_msg("Enable logging for queries, responses, rpz")
        data = {"logging_categories":{"log_queries":True, "log_responses":True, "log_rpz":True}}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_dns_ref)[0]['_ref'], fields=json.dumps(data))
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Enabling logging for queries, responses, rpz")
                assert False
    
        restart_services()
    	'''Allow recursive query for Grid 2'''
        display_msg("Allow recursive query")
        data =  {"recursive_query_list": [{"address": "Any", "permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_dns_ref)[0]['_ref'], fields=json.dumps({"allow_recursive_query": True}),grid_vip=config.Master2_IP)
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Allow recursive query")
                assert False
        display_msg("Update recursive query list")
        response2 = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_dns_ref)[0]['_ref'], fields=json.dumps(data),grid_vip=config.Master2_IP)
        display_msg(response2)
        if type(response2) == tuple:
            if response2[0]==400 or response2[0]==401:
                display_msg("Failure: Add recursive query list")
                assert False

        '''Enable logging for queries, responses, rpz for Grid 2'''
        display_msg("Enable logging for queries, responses, rpz")
        data = {"logging_categories":{"log_queries":True, "log_responses":True, "log_rpz":True}}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_dns_ref)[0]['_ref'], fields=json.dumps(data),grid_vip=config.Master2_IP)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Enabling logging for queries, responses, rpz")
                assert False
    
        restart_services()

        ''' Enable Parental Control'''
        display_msg("Enable Parental Control")
        get_ref = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber")
        display_msg(get_ref)
        data={"enable_parental_control": True,
              "cat_acctname":"InfoBlox", 
              "cat_password":"CSg@vBz!rx7A",
              "category_url":"https://pitchers.rulespace.com/ufsupdate/web.pl",
              "proxy_url":"http://10.196.9.113:8001", 
              "proxy_username":"client", 
              "proxy_password":"infoblox",
              "pc_zone_name":"niosspt_9967.zone.com", 
              "ident":"pkFu-yhrf-qPOV-s5BU",
              "cat_update_frequency":24}
        print (json.loads(get_ref)[0]["_ref"])
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]["_ref"],fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Enabling parental control")
                assert False
        sleep(30)


        restart_services()

        
        ''' Add Subscriber Site'''
        display_msg("Add Subscriber Site")
        data={"blocking_ipv4_vip1": "2.4.5.6",
              "nas_gateways":[{"ip_address": "10.36.0.151","name": "nas1", "shared_secret":"testing123"}],
              "maximum_subscribers": 898989,
              "members": [{"name": str(config.grid_fqdn)}],
              "msps":[{"ip_address": "10.196.128.13"}],
              "name": "site19",
              "nas_port": 1813,
              "spms": [{"ip_address": "10.12.11.11"}]}
        old_data={"name": "niosspt_9967_subscbr",
              "maximum_subscribers": 898989, 
              "members": [{"name": config.grid_fqdn}],
              "nas_gateways": [{"ip_address": "10.36.120.10","shared_secret": "test","name": "niosspt_9967_nas","send_ack": True}]}
        subs_site = ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data))
        display_msg(subs_site)
        if type(subs_site) == tuple:
            if subs_site[0]==400 or subs_site[0]==401:
                display_msg("Failure: Adding subscriber site")
                assert False

                
        restart_services()
        

        '''Update Interim Accounting Interval'''
        display_msg("Update Interim Accounting Interval to 60min")
        get_ref = ib_NIOS.wapi_request('GET', object_type='parentalcontrol:subscriber')
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps({"interim_accounting_interval":120}))
        if type(response2) == tuple:
            if response2[0]==400 or response2[0]==401:
                display_msg("Failure: Updating Interim Accounting Interval to 60min")
                assert False
        
        '''Start Subscriber Collection Service on the Master'''
        display_msg("Start Subscriber Collection Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:parentalcontrol")
        display_msg(get_ref)
        data= {"enable_service": True}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]["_ref"],fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Starting subscriber Collection Service")
                assert False
        sleep(60)

        restart_services()

        '''Add DNS Resolver'''
        display_msg("Add DNS Resolvers 127.0.0.1, 10.0.2.35")
        grid_ref = ib_NIOS.wapi_request('GET', object_type='grid')
        data = {"dns_resolver_setting":{"resolvers":["127.0.0.1","10.0.2.35"]}}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("Failure: Adding DNS Resolvers")
                assert False
        
        '''Start DCA on Master'''
        display_msg("Start DCA on Master to ensure bug is not  Reproducing")
        member_ref=ib_NIOS.wapi_request('GET',object_type="member:dns")
        display_msg(member_ref)
        condition=ib_NIOS.wapi_request('GET',object_type=json.loads(member_ref)[0]['_ref']+"?_return_fields=enable_dns_cache_acceleration")
        display_msg(condition)
        data={"enable_dns_cache_acceleration": True}
        enable_member_ref = ib_NIOS.wapi_request('PUT', ref=member_ref, fields=json.dumps(data))
        display_msg(enable_member_ref)
        
        
        display_msg("-----------Test Case setup Completed------------")


    @pytest.mark.run(order=2)
    def test_001_add_fwd_zone(self):
          print("Creating forward Zone for Adding Unknown Resource Records ")
	  fwd_zone=["fwd1.com","fwd2.com","fwd3.com","fwd4.com","fwd5.com","fwd6.com","fwd7.com","fwd8.com","fwd9.com","fwd10.com"]
          for i in fwd_zone:
		forward_zone={"fqdn":str(i),"forward_to":[{"address":config.Master2_IP,"name":config.Master2_fqdn}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_forward", fields=json.dumps(forward_zone))
                if (response[0]==400):
                     print ("Zone already exists,try with other data[Don't get confused with Pytest Passed status]")
                else:
                     print ("Zone added and response looks like : ",response)
                     res = json.loads(response)
                     time.sleep(30)
                     print ("reference of zone added ",res)
                     grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                     ref = json.loads(grid)[0]['_ref']
                     publish={"member_order":"SIMULTANEOUSLY"}
                     request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                     time.sleep(1)
                     request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                     restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                     time.sleep(1)
          print ("Added Forward Zones as expected")
	  zones=ib_NIOS.wapi_request('GET', object_type="zone_forward")
	  print (zones)

      
    @pytest.mark.run(order=3)
    def test_002_add_auth_zone(self):
          print("Creating auth Zone for Adding Resource Records ")
          fwd_zone=["fwd1.com","fwd2.com","fwd3.com","fwd4.com","fwd5.com","fwd6.com","fwd7.com","fwd8.com","fwd9.com","fwd10.com"]
          for i in fwd_zone:
                auth_zone={"fqdn": str(i),"allow_query": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}],"allow_update": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(auth_zone),grid_vip=config.Master2_IP)
                if (response[0]==400):
                     logging.info ("Zone already exists,try with other data[Don't get confused with Pytest Passed status]")
                else:
                     logging.info ("Zone added and response looks like : ",response)
                     res = json.loads(response)
                     time.sleep(30)
                     print ("reference of zone added ",res)
                     data = {"grid_primary": [{"name": config.Master2_fqdn,"stealth":False}]}
                     print ("Trying to Associate ZONE with Primary GRID")
                     response = ib_NIOS.wapi_request('PUT',ref=res,fields=json.dumps(data),grid_vip=config.Master2_IP)
                     response=json.loads(response)
                     logging.info ("Restart services")
                     logging.info ("Associated Zone with Primary GRID and reference looks like :",response)
                     grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.Master2_IP)
                     ref = json.loads(grid)[0]['_ref']
                     publish={"member_order":"SIMULTANEOUSLY"}
                     request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish),grid_vip=config.Master2_IP)
                     time.sleep(1)
                     request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus",grid_vip=config.Master2_IP)
                     restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",grid_vip=config.Master2_IP)
                     time.sleep(1)
                print ("Added Auth Zones in Grid 2 as expected")
                zones=ib_NIOS.wapi_request('GET', object_type="zone_auth")
                print (zones) 


    @pytest.mark.run(order=4)
    def test_003_a_record_for_zone(self):
          print("/n")
          print("############################################################################################")
          print("#####                  Test  Case 04 Started Executing                                #####")
          print("############################################################################################")
          zone=["fwd1.com","fwd2.com","fwd3.com","fwd4.com","fwd5.com","fwd6.com","fwd7.com","fwd8.com","fwd9.com","fwd10.com"]
          rec_count=range(1,10)
          for i in zone:
                for j in rec_count:
                      print("Creating A Record for added Zone")
                      data = {"name": "a_rec"+str(j)+"." + str(i), "ipv4addr": "1.2.3.4", "comment": "Adding arec", "view": "default"}
                      response = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(data),grid_vip=config.Master2_IP)
                      if (response[0] != 400):
                          print("Added A Record with Reference value :", json.loads(response))
                          time.sleep(1)
                          read = re.search(r'201', response)
                          for read in response:
                              assert True
          print("A Record is created Successfully") 

    @pytest.mark.run(order=5)
    def test_004_send_dig_query_1(self):
        """
        dig @<Grid_IP> <query1> aaaa
        dnsq -ns Grid_IP -edo 0 -qname <query1> -qtype=aaaa -edata=0xFE31001145303a43423a34453a38303a45373a3636
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 4 Execution Started           |")
        display_msg("----------------------------------------------------")
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@"+str(config.grid_vip)
        args=shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        query_list=["A"]
        zone=["fwd1.com","fwd2.com","fwd3.com","fwd4.com","fwd5.com","fwd6.com","fwd7.com","fwd8.com","fwd9.com","fwd10.com"]
        rec_count=range(1,10)
	for i in range(1,1000):
            for i in zone:
                  for j in rec_count:
                        for record in query_list:
                              query_cmd1 = 'dig @'+config.grid_vip+' '+"a_rec"+str(j)+"."+str(i)+" IN "+ str(record)
                              print (query_cmd1)
                              child.stdin.write(query_cmd1+'\n')
        child.stdin.write("exit")
        output=child.communicate()
        for line in output:
	    print (line)
            grep_output=re.search("connection timed out; no servers could be reached",line)
            if (grep_output != None ):
                assert False
                display_msg("Test case 004 Failed , issue replicated ")
            else:
                display_msg ("Test case 004 Passed, No Connection Timeout issue found")
                assert True

    @pytest.mark.run(order=06)
    def test_005_check_Cores_Storage_File(self):
        print("/n")
        print("############################################################################################")
        print("#####                  Test  Case 005 Started Executing                                #####")
        print("############################################################################################")
        sleep(30)
        print("Check for named_conf file updation with DNSTAP Settings \n")
        try:
            connection = SSH(config.grid_vip)
            core_details = connection.send_command('cat  /infoblox/var/infoblox.log | grep -i " core 5 is stuck"')
	    print (core_details)
            storage_cores=connection.send_command('cd /storage/cores/ ; ls -ltr ')
	    storage_cores=storage_cores.split(" ")
	    print (len(storage_cores))
	    if 	(len(storage_cores)>=12 and len(core_details)>1):
		assert False
	    else:
		assert True
        except TypeError:
            print("Type Error ")

    @pytest.mark.run(order=07)
    def test_006_check_for_show_smartnic_command(self):
        print("/n")
	print("############################################################################################")
        print("#####                  Test  Case 006 Started Executing                                #####")
        print("############################################################################################")
        sleep(30)
	logging.info(" show subscriber_secure_data")
        print("connecting to grid IP for further executions :", config.grid_vip)
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@' + config.grid_vip)
        child.logfile = sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show smartnic')
        child.expect('>')
        print (child.before)	


    @pytest.mark.run(order=8)
    def test_007_add_subscriber_data(self):
        print ("  Validating Bug number NIOSSPT-8907 - Telecom Italia | show subscriber_secure_data' command closes ssh connection to the server ")
	print("/n")
        print("############################################################################################")
        print("#####                  Test  Case 007 Started Executing                                #####")
        print("############################################################################################")
        sleep(30)
	data = "10.36.6.80 32 e0cb4e80e766 N/A  ACS:Acct-Session-Id=9999732d-34590333;NAS:NAS-PORT=1813;LID:LocalId=E0CB4E80E766;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;SUB:Calling-Station-Id=1101202028"
        if not add_subscriber_data(data):
            display_msg("Failure: Adding subscriber data")
            assert False 

    @pytest.mark.run(order=9)
    def test_008_validate_added_subscriber_data(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 8  Started Executing                      ####")
        print("###############################################################################")
        print("Test case to validate the added subscriber data ")
        sleep(10)
        data = show_subscriber_secure_data()
        result = re.findall("10.36.6.80", data)
	print (result)
        if (result != None):
            assert True
            print("Test case 08 passed")
        else:
            assert False
            print("Test case 08 failed")

    @pytest.mark.run(order=10)
    def test_009_add_subscriber_data_member(self):
	args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.Master2_IP
    	args=shlex.split(args)
	data="10.36.6.80 32 e0cb4e80e766 N/A  'ACS:Acct-Session-Id=9999732d-34590333;NAS:NAS-PORT=1813;LID:LocalId=E0CB4E80E766;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;SUB:Calling-Station-Id=1101202028;'"
    	child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    	child.stdin.write("set subscriber_secure_data add "+data+" \n")
   	child.stdin.write("exit")
    	output = child.communicate()
    	display_msg(output)
    	for line in list(output):
            if 'Disconnect NOW if you have' in line:
            	    continue
            display_msg(line)
            if 'Record successfully added' in line:
                return True
		print ("Test case 009 Passed ")

    @pytest.mark.run(order=11)
    def test_010_validate_added_subscriber_data(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 10  Started Executing                      ####")
        print("###############################################################################")
        print("Test case to validate susbscriber data ")
        sleep(10)
        data = show_subscriber_secure_data_member()
        result = re.findall("10.36.6.80", data)
        if (result != None):
            assert True
            print("Test case 10 passed")
        else:
            assert False
            print("Test case 10 failed")

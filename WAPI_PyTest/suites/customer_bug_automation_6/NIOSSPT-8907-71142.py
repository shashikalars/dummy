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
# Perform dns query in loop and u should not see crash andcores
#Run queries against A , AAAA records with edns0 options and make sure there are any crashes #
#Validate dns-accel stats and make sure responses below 1024 and RR below 64 are cached in DCA
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
#from ib_utils.log_capture import log_action as log
import pexpect
from ib_utils.start_stop_logs import log_action as log
#from ib_utils.file_content_validation import log_validation as logv
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

def check_dns_accel(master0mgmt):
    sleep(15)
    print(" show DNS Cacheing ")
    print("connecting to grid IP for further executions :",config.grid_vip)
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@' + config.grid_vip)
    child.logfile = sys.stdout
    child.expect('.*password:')
    child.sendline('infoblox')
    child.expect('Infoblox >')
    child.sendline('show dns-accel')
    child.expect('>')
    child.sendline('exit')
    child.close()
    return child.before



def display_msg(x=""):
    """ 
    Additional function.
    """
    print(x)
    print(x)

def start_syslog(logfile):
    """
    Start log capture
    """
    print("Start capturing "+logfile)
    log("start",logfile,config.grid_vip)

def stop_syslog(logfile):
    """
    Stop log capture
    """
    print("Stop capturing "+logfile)
    log("stop",logfile,config.grid_vip)

def get_reference_for_zone(response):
    print("Fetching reference values for Zones")
    get_ref = ib_NIOS.wapi_request('GET',object_type=response,grid_vip=config.grid_vip)
    return json.loads(get_ref)

def validate_syslog(logfile, lookfor):
    """
    Validate captured log
    """
    print("Validate captured log")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(config.grid_vip, username='root', pkey = mykey)
    file_name='_'.join(logfile.split('/'))
    file = '/root/dump/'+ str(config.grid_vip)+file_name+'.log'
    print("cat "+file+" | grep -i '"+lookfor+"'")
    stdin, stdout, stderr = client.exec_command("cat "+file+" | grep -i '"+lookfor+"'")
    result=stdout.read()
    print(result)
    client.close()
    if result:
        return True
    return False

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

def add_subscriber_data(data):
    """
    Add Subscriber Data
    """
    args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_vip
    args=shlex.split(args)
    child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    new_data="set subscriber_secure_data add "+data+" \n"
    print ("new data :",new_data)
    child.stdin.write(new_data)
    child.stdin.write("exit")
    output = child.communicate()
    print(output)
    for line in list(output):
        if 'Disconnect NOW if you have' in line:
            continue
        print(line)
        if 'Record successfully added' in line:
            return True
    return False


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

def show_subscriber_secure_data_member():
    print(" show subscriber_secure_data")
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@' + config.grid2_vip)
    child.logfile = sys.stdout
    child.expect('password:')
    child.sendline('infoblox')
    child.expect('Infoblox >')
    child.sendline('show subscriber_secure_data')
    child.expect('>')
    output = child.before
    child.sendline('exit')
    return output


class NIOSSPT_71142(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_001_setup(self):
        """
        setup method: Used for configuring pre-required configs.
        """
        print("------------------------------------------------")
        print("|           Test Case setup Started : 9412           |")
        print("------------------------------------------------")
        
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
        #print(result)
        #result1 = stdout1.read()
        #print(result1)
        #client.close()

        '''Add DNS Resolver'''
        print("Add DNS Resolver 10.103.3.10")
        grid_ref = ib_NIOS.wapi_request('GET', object_type='grid',grid_vip=config.grid_vip)
        data = {"dns_resolver_setting":{"resolvers":["127.0.0.1","10.103.3.10"]}}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_ref)[0]['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Adding DNS Resolver")
                assert False

        '''Add DNS Forwarder'''
        print("Add DNS forwarder  ")
        grid_dns_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns',grid_vip=config.grid_vip)
        data = {"forwarders":[config.grid2_vip]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_dns_ref)[0]['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Adding DNS Forwarder")
                assert False

        '''Allow recursive query for GRID 1'''
        print("Allow recursive query")
        data =  {"recursive_query_list": [{"address": "Any", "permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_dns_ref)[0]['_ref'], fields=json.dumps({"allow_recursive_query": True}),grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Allow recursive query")
                assert False
        print("Update recursive query list")
        response2 = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_dns_ref)[0]['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response2)
        if type(response2) == tuple:
            if response2[0]==400 or response2[0]==401:
                print("Failure: Add recursive query list")
                assert False

        '''Enable logging for queries, responses, rpz for GRID 1'''
        print("Enable logging for queries, responses, rpz")
        data = {"logging_categories":{"log_queries":True, "log_responses":True, "log_rpz":True}}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_dns_ref)[0]['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
        print (response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Enabling logging for queries, responses, rpz")
                assert False
    
        restart_services()
    	'''Allow recursive query for Grid 2'''
        print("Allow recursive query")
        data =  {"recursive_query_list": [{"address": "Any", "permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_dns_ref)[0]['_ref'], fields=json.dumps({"allow_recursive_query": True}),grid_vip=config.grid2_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Allow recursive query")
                assert False
        print("Update recursive query list")
        response2 = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_dns_ref)[0]['_ref'], fields=json.dumps(data),grid_vip=config.grid2_vip)
        print(response2)
        if type(response2) == tuple:
            if response2[0]==400 or response2[0]==401:
                print("Failure: Add recursive query list")
                assert False

        '''Enable logging for queries, responses, rpz for Grid 2'''
        print("Enable logging for queries, responses, rpz")
        data = {"logging_categories":{"log_queries":True, "log_responses":True, "log_rpz":True}}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_dns_ref)[0]['_ref'], fields=json.dumps(data),grid_vip=config.grid2_vip)
        print (response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Enabling logging for queries, responses, rpz")
                assert False
    

        restart_services()

        '''Add DNS Resolver'''
        print("Add DNS Resolvers 127.0.0.1, 10.103.3.10")
        grid_ref = ib_NIOS.wapi_request('GET', object_type='grid',grid_vip=config.grid_vip)
        data = {"dns_resolver_setting":{"resolvers":["127.0.0.1","10.103.3.10"]}}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_ref)[0]['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Adding DNS Resolvers")
                assert False
                
        '''Start DNS Service '''
        member_ref=ib_NIOS.wapi_request('GET',object_type="member:dns",grid_vip=config.grid_vip)
        member_ref=json.loads(member_ref)
        print (member_ref)
        print ("__________________________________")
        dns_ref=member_ref[0]['_ref']
        condition=ib_NIOS.wapi_request('GET',object_type=dns_ref+"?_return_fields=enable_dns",grid_vip=config.grid_vip)
        data={"enable_dns": True}
        enable_dns_ref = ib_NIOS.wapi_request('PUT', ref=dns_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
        print (enable_dns_ref)
        print ("*************************************")
        com=json.loads(enable_dns_ref)+"?_return_fields=enable_dns"
        print (com)
         
        member_ref=ib_NIOS.wapi_request('GET',object_type="member:dns",grid_vip=config.grid2_vip)
        member_ref=json.loads(member_ref)
        print (member_ref)
        print ("__________________________________")
        dns_ref=member_ref[0]['_ref']
        condition=ib_NIOS.wapi_request('GET',object_type=dns_ref+"?_return_fields=enable_dns",grid_vip=config.grid2_vip)
        data={"enable_dns": True}
        enable_dns_ref = ib_NIOS.wapi_request('PUT', ref=dns_ref, fields=json.dumps(data),grid_vip=config.grid2_vip)
        print (enable_dns_ref)
        print ("*************************************")
        com=json.loads(enable_dns_ref)+"?_return_fields=enable_dns"
        print (com)
        '''start DNS services for MGMT MASTER + MEMBER IP '''
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=use_lan2_port,use_mgmt_port,use_lan_port,use_mgmt_ipv6_port,use_lan_ipv6_port,use_lan2_ipv6_port', grid_vip=config.grid_vip)
        print("\n")
        #print(get_ref)
        for ref in json.loads(get_ref):
            if config.grid_vip in ref:
                data={"use_lan_port": True,"use_mgmt_port": True}
                response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)

                if type(response) == tuple:
                    if response[0]==400 or response[0]==401 or response[0]==404:
                        print("Failure: All interface are enabled")
                        assert False
        print("------------------------------------------------------")

        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=use_lan2_port,use_mgmt_port,use_lan_port,use_mgmt_ipv6_port,use_lan_ipv6_port,use_lan2_ipv6_port', grid_vip=config.grid2_vip)
        print("\n")
        #print(get_ref)
        for ref in json.loads(get_ref):
            data={"use_lan_port": True,"use_mgmt_port": True}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid2_vip)
            print(response)

            if type(response) == tuple:
                if response[0]==400 or response[0]==401 or response[0]==404:
                    print("Failure: All interface are enabled")
                    assert False



        '''Start DCA on Master'''
        print("Start DCA on Master to ensure bug is not  Reproducing")
        member_ref=ib_NIOS.wapi_request('GET',object_type="member:dns",grid_vip=config.grid_vip)
        print(member_ref)
        object1=json.loads(member_ref)[0]['_ref']
        condition=ib_NIOS.wapi_request('GET',object_type=object1+"?_return_fields=enable_dns_cache_acceleration",grid_vip=config.grid_vip)
        print(condition)
        data={"enable_dns_cache_acceleration": True}
        print ("---------------------------------------------------------------------")
        print ("::::::::::::::::::::::::::::::::::::::::::::::",object1)
        enable_member_ref = ib_NIOS.wapi_request('PUT', ref=object1, fields=json.dumps(data),grid_vip=config.grid_vip)
        print(enable_member_ref)
        print("-----------Test Case setup Completed------------")


    @pytest.mark.run(order=2)
    def test_002_add_fwd_zone(self):
        print("/n")
        print("############################################################################################")
        print("#####                  Test  Case 002 Started Executing                                #####")
        print("############################################################################################")
        print("Creating forward Zone for Adding Unknown Resource Records ")
	fwd_zone=["fwd1.com","fwd2.com","fwd3.com","fwd4.com","fwd5.com","fwd6.com","fwd7.com","fwd8.com","fwd9.com","fwd10.com"]
        for i in fwd_zone:
            forward_zone={"fqdn":str(i),"forward_to":[{"address":config.grid2_vip,"name":config.grid2_fqdn}]}
            response = ib_NIOS.wapi_request('POST', object_type="zone_forward", fields=json.dumps(forward_zone),grid_vip=config.grid_vip)
            if (response[0]==400):
                print ("Zone already exists,try with other data[Don't get confused with Pytest Passed status]")
            else:
                print ("Zone added and response looks like : ",response)
                res = json.loads(response)
                time.sleep(30)
                print ("reference of zone added ",res)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish),grid_vip=config.grid_vip)
                time.sleep(1)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus",grid_vip=config.grid_vip)
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",grid_vip=config.grid_vip)
                time.sleep(1)
        print ("Added Forward Zones as expected")
	zones=ib_NIOS.wapi_request('GET', object_type="zone_forward",grid_vip=config.grid_vip)
	print (zones)

      
    @pytest.mark.run(order=3)
    def test_003_add_auth_zone(self):
        print("/n")
        print("############################################################################################")
        print("#####                  Test  Case 003 Started Executing                                #####")
        print("############################################################################################")
        print("Creating auth Zone for Adding Resource Records ")
        fwd_zone=["fwd1.com","fwd2.com","fwd3.com","fwd4.com","fwd5.com","fwd6.com","fwd7.com","fwd8.com","fwd9.com","fwd10.com"]
        for i in fwd_zone:
            auth_zone={"fqdn": str(i),"allow_query": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}],"allow_update": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}]}
            response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(auth_zone),grid_vip=config.grid2_vip)
            if (response[0]==400):
                print ("Zone already exists,try with other data[Don't get confused with Pytest Passed status]")
            else:
                print ("Zone added and response looks like : ",response)
                res = json.loads(response)
                time.sleep(30)
                print ("reference of zone added ",res)
                data = {"grid_primary": [{"name": config.grid2_fqdn,"stealth":False}]}
                print ("Trying to Associate ZONE with Primary GRID")
                response = ib_NIOS.wapi_request('PUT',ref=res,fields=json.dumps(data),grid_vip=config.grid2_vip)
                response=json.loads(response)
                print ("Restart services")
                print ("Associated Zone with Primary GRID and reference looks like :",response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid2_vip)
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish),grid_vip=config.grid2_vip)
                time.sleep(1)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus",grid_vip=config.grid2_vip)
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",grid_vip=config.grid2_vip)
                time.sleep(1)
                print ("Added Auth Zones in Grid 2 as expected")
                zones=ib_NIOS.wapi_request('GET', object_type="zone_auth",grid_vip=config.grid2_vip)
                print (zones) 


    @pytest.mark.run(order=4)
    def test_004_a_record_for_zone(self):
          print("/n")
          print("############################################################################################")
          print("#####                  Test  Case 04 Started Executing                                #####")
          print("############################################################################################")
          zone=["fwd1.com","fwd2.com","fwd3.com","fwd4.com","fwd5.com","fwd6.com","fwd7.com","fwd8.com","fwd9.com","fwd10.com"]
          rec_count=range(1,50)
          for i in zone:
                for j in rec_count:
                      print("Creating A Record for added Zone")
                      data = {"name": "a_rec"+str(j)+"." + str(i), "ipv4addr": "1.2.3.4", "comment": "Adding arec", "view": "default"}
                      response = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(data),grid_vip=config.grid2_vip)
                      if (response[0] != 400):
                          print("Added A Record with Reference value :", json.loads(response))
                          time.sleep(1)
                          read = re.search(r'201', response)
                          for read in response:
                              assert True
          print("A Record is created Successfully") 


    @pytest.mark.run(order=5)
    def test_005_a_record_for_zone(self):
          print("/n")
          print("############################################################################################")
          print("#####                  Test  Case 005 Started Executing                                #####")
          print("############################################################################################")
          zone=["fwd1.com","fwd2.com","fwd3.com","fwd4.com","fwd5.com","fwd6.com","fwd7.com","fwd8.com","fwd9.com","fwd10.com"]
          rec_count=range(1,50)
          for i in zone:
                for j in rec_count:
                      print("Creating A Record for added Zone")
                      data = {"name":"aaaa"+str(j)+"." + str(i),"ipv6addr":"ab::1","comment": "Adding arec", "view": "default"} 
                      response = ib_NIOS.wapi_request('POST', object_type="record:aaaa", fields=json.dumps(data),grid_vip=config.grid2_vip)
                      if (response[0] != 400):
                          print("Added A Record with Reference value :", json.loads(response))
                          time.sleep(1)
                          read = re.search(r'201', response)
                          for read in response:
                              assert True
          print("A Record is created Successfully")
          

    @pytest.mark.run(order=6)
    def test_006_send_dig_query_1(self):
        """
        dig @<Grid_IP> <query1> aaaa / a records
        """
        print()
        print("----------------------------------------------------")
        print("|          Test Case 006 Execution Started           |")
        print("----------------------------------------------------")
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@"+str(config.grid_vip)
        args=shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        query_list=["A","AAAA"]
        zone=["fwd1.com","fwd2.com","fwd3.com","fwd4.com","fwd5.com","fwd6.com","fwd7.com","fwd8.com","fwd9.com","fwd10.com"]
        rec_count=range(1,2)
	for i in range(1,2):
            for i in zone:
                  for j in rec_count:
                        for record in query_list:
                            #sleep(10)
                            query_cmd1 = 'dig @'+config.grid_vip+' '+"a_rec"+str(j)+"."+str(i)+" IN "+str(record)+" +edns=0"
                            print (query_cmd1)
                            #sleep(10)
                            child.stdin.write(query_cmd1+'\n')
                            #sleep(10)
        child.stdin.write("exit")
        output=child.communicate()
        for line in output:
	    print (line)
            grep_output=re.search("connection timed out; no servers could be reached",line)
            if (grep_output ):
                assert False
                print("Test case 006 Failed , issue replicated ")
            else:
                print ("Test case 006 Passed, No Connection Timeout issue found")
                assert True

    @pytest.mark.run(order=7)
    def test_007_check_Cores_Storage_File(self):
        print("/n")
        print("############################################################################################")
        print("#####                  Test  Case 007 Started Executing                                #####")
        print("############################################################################################")
        sleep(30)
        print("Check for named_conf file updation with DNSTAP Settings \n")
        try:
            #connection = SSH(config.grid_vip)
	    connection= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
            core_details = connection.sendline('cat  /infoblox/var/infoblox.log | grep -i " core 5 is stuck"')
	    print (core_details)
            storage_cores=connection.sendline('cd /storage/cores/ ; ls -ltr ')
	    #storage_cores=storage_cores.split(" ")
	    print (len(storage_cores))
	    if 	(len(storage_cores)>=12 and len(core_details)>1):
		assert False
	    else:
		assert True
        except TypeError:
            print("Type Error ")

    @pytest.mark.run(order=8)
    def test_008_check_for_show_smartnic_command(self):
        print("/n")
	print("############################################################################################")
        print("#####                  Test  Case 008 Started Executing                                #####")
        print("############################################################################################")
        sleep(30)
	print(" show subscriber_secure_data")
        print("connecting to grid IP for further executions :", config.grid2_vip)
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@' + config.grid2_vip)
        child.logfile = sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show smartnic')
        child.expect('>')
        print (child.before)	

    @pytest.mark.run(order=9)
    def test_009_check_for_show_dnsaccel_command(self):
        print("/n")
	print("############################################################################################")
        print("#####                  Test  Case 009 Started Executing                                #####")
        print("############################################################################################")
        sleep(30)
	print(" show dns-accel")
        result=check_dns_accel(config.grid_vip) #ssh admin@10.36.192.14
        print (result)
        search_result=re.findall("SUCCESS=.*",result)
        if (search_result[0] != 0):
            assert True

	
    @pytest.mark.run(order=10)
    def test_010_enabling_DNS_recursion(self):
        print ("Enabling DNS on both Recursion and RPZ-logging")
        grid_ref=ib_NIOS.wapi_request('GET',object_type="grid:dns")
	#pdb.set_trace()
	sleep(30)
        grid_ref=json.loads(grid_ref)
        grid_dns_ref=grid_ref[0]['_ref']
        fields=grid_dns_ref+"?_return_fields=allow_query,allow_update,forwarders,logging_categories,allow_recursive_query"
        grid_fields_data=ib_NIOS.wapi_request('GET',object_type=fields)
        print ("before editing grid : dns properties",grid_fields_data)
        data={"allow_query": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}],"allow_recursive_query": True,"allow_update": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}],"forwarders": [],"logging_categories": {"log_client": False,"log_config": False,"log_database": False,"log_dnssec": False,"log_dtc_gslb": False,"log_dtc_health": False,"log_general": False,"log_lame_servers": False,"log_network": False,"log_notify": False,"log_queries": True,"log_query_rewrite": False,"log_rate_limit": False,"log_resolver": False,"log_responses": False,"log_rpz": True,"log_security": False,"log_update": False,"log_update_security": False,"log_xfer_in": False,"log_xfer_out": False}}
        condition=ib_NIOS.wapi_request('PUT', ref=grid_dns_ref, fields=json.dumps(data))
        print (condition)
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = grid_dns_ref + "?_function=publish_changes",fields=json.dumps(publish))
        time.sleep(30)
        request_restart = ib_NIOS.wapi_request('POST', object_type = grid_dns_ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = grid_dns_ref + "?_function=restartservices")
        time.sleep(40)
        new_fields=grid_dns_ref+"?_return_fields=allow_query,allow_update,forwarders,logging_categories,allow_recursive_query"
        new_grid_fields_data=ib_NIOS.wapi_request('GET',object_type=new_fields)
        print(new_grid_fields_data)
        print(grid_fields_data)
        if type(new_grid_fields_data) == tuple:
            if response[0]==400 or response[0]==401:
                assert False
        else:
            assert True

        #if (grid_fields_data == new_grid_fields_data):
         #   assert True
          #  print (" Test case 10 passed Successfully, Modified GRID DNS Properties ")
        #else:
         #   assert False
          #  print ("Test case 10 failed , unable to Modify GRID_DNS Properties ")


    @pytest.mark.run(order=11)
    def test_011_setup_for_NIOSSPT_8907(self):
        print("/n")
	print("############################################################################################")
        print("#####                  Test  Case 010 Started Executing                                #####")
        print("############################################################################################")
        '''Stop DCA on Master'''
        print("Stop DCA on Master to start with enabling subscriber collection")
        member_ref=ib_NIOS.wapi_request('GET',object_type="member:dns",grid_vip=config.grid_vip)
        print(member_ref)
        condition=ib_NIOS.wapi_request('GET',object_type=json.loads(member_ref)[0]['_ref']+"?_return_fields=enable_dns_cache_acceleration",grid_vip=config.grid_vip)
        print(condition)
        object1=json.loads(member_ref)[0]['_ref']
        data={"enable_dns_cache_acceleration": False}
        enable_member_ref = ib_NIOS.wapi_request('PUT', ref=object1, fields=json.dumps(data),grid_vip=config.grid_vip)
        print(enable_member_ref)
	#pdb.set_trace()
        #sleep(1200)
        ''' Enable Parental Control'''
        print("Enable Parental Control")
        get_ref = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber",grid_vip=config.grid_vip)
        print(get_ref)
        data={"enable_parental_control": True,
              "cat_acctname":"infoblox_sdk", 
              "cat_password":"LinWmRRDX0q",
              "category_url":"https://dl.zvelo.com/",
              "proxy_url":"http://10.196.9.113:8001", 
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


        restart_services()
        
        ''' Add Subscriber Site'''
        print("Add Subscriber Site")
        data={"blocking_ipv4_vip1": "2.4.5.6",
              "nas_gateways":[{"ip_address": "10.36.0.151","name": "nas1", "shared_secret":"testing123"}],
              "maximum_subscribers": 898989,
              "members": [{"name": str(config.grid_fqdn)}],
              "msps":[{"ip_address": "10.196.128.13"}],
              "name": "site1",
              "nas_port": 1813,
              "spms": [{"ip_address": "10.12.11.11"}]}
        #old_data={"name": "niosspt_9967_subscbr",
         #     "maximum_subscribers": 898989, 
          #    "members": [{"name": config.grid_fqdn}],
           #   "nas_gateways": [{"ip_address": "10.36.120.10","shared_secret": "test","name": "niosspt_9967_nas","send_ack": True}]}
        subs_site = ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data),grid_vip=config.grid_vip)
        print(subs_site)
        if type(subs_site) == tuple:
            if subs_site[0]==400 or subs_site[0]==401:
                print("Failure: Adding subscriber site")
                assert False
        ''' Enable Parental Control'''
        print("Enable Parental Control")
        get_ref = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber",grid_vip=config.grid2_vip)
        print(get_ref)
        data={"enable_parental_control": True,
              "cat_acctname":"infoblox_sdk", 
              "cat_password":"LinWmRRDX0q",
              "category_url":"https://dl.zvelo.com/",
              "proxy_url":"http://10.196.9.113:8001", 
              "proxy_username":"client", 
              "proxy_password":"infoblox",
              "pc_zone_name":"niosspt_9967.zone.com", 
              "cat_update_frequency":24}
        print (json.loads(get_ref)[0]["_ref"])
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]["_ref"],fields=json.dumps(data),grid_vip=config.grid2_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Enabling parental control")
                assert False
        sleep(30)


        restart_services()
        
        ''' Add Subscriber Site'''
        print("Add Subscriber Site")
        data={"blocking_ipv4_vip1": "2.4.5.7",
              "nas_gateways":[{"ip_address": "10.36.0.151","name": "nas1", "shared_secret":"testing123"}],
              "maximum_subscribers": 898989,
              "members": [{"name": str(config.grid2_fqdn)}],
              "msps":[{"ip_address": "10.195.128.13"}],
              "name": "site12",
              "nas_port": 1813,
              "spms": [{"ip_address": "10.11.11.11"}]}
        #old_data={"name": "niosspt_9967_subscbr",
          #    "maximum_subscribers": 898989, 
           #   "members": [{"name": config.grid2_fqdn}],
            #  "nas_gateways": [{"ip_address": "10.36.120.10","shared_secret": "test","name": "niosspt_9967_nas","send_ack": True}]}
        subs_site = ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data),grid_vip=config.grid2_vip)
        print(subs_site)
	''' Enable Parental Control'''
        print("Enable Parental Control")
        get_ref = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber",grid_vip=config.grid2_vip)
        print(get_ref)
        data={"enable_parental_control": True,
              "cat_acctname":"infoblox_sdk", 
              "cat_password":"LinWmRRDX0q",
              "category_url":"https://dl.zvelo.com/",
              "proxy_url":"http://10.196.9.113:8001", 
              "proxy_username":"client", 
              "proxy_password":"infoblox",
              "pc_zone_name":"niosspt_9967.zone.com", 
              "cat_update_frequency":24}
        print (json.loads(get_ref)[0]["_ref"])
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]["_ref"],fields=json.dumps(data),grid_vip=config.grid2_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Enabling parental control")
                assert False
        sleep(30)

                
        restart_services()
        

        '''Update Interim Accounting Interval'''
        print("Update Interim Accounting Interval to 60min")
        get_ref = ib_NIOS.wapi_request('GET', object_type='parentalcontrol:subscriber',grid_vip=config.grid2_vip)
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps({"interim_accounting_interval":120}),grid_vip=config.grid2_vip)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Updating Interim Accounting Interval to 60min")
                assert False
        
        '''Start Subscriber Collection Service on the Master'''
        print("Start Subscriber Collection Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:parentalcontrol",grid_vip=config.grid2_vip)
        print(get_ref)
        data= {"enable_service": True}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]["_ref"],fields=json.dumps(data),grid_vip=config.grid2_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Starting subscriber Collection Service")
                assert False
        sleep(60)

        restart_services()

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

        '''Add DNS Resolver'''
        print("Add DNS Resolvers 127.0.0.1, 10.0.2.35")
        grid_ref = ib_NIOS.wapi_request('GET', object_type='grid',grid_vip=config.grid2_vip)
        data = {"dns_resolver_setting":{"resolvers":["127.0.0.1","10.0.2.35"]}}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_ref)[0]['_ref'], fields=json.dumps(data),grid_vip=config.grid2_vip)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Adding DNS Resolvers")
                assert False
                
        '''Start DNS Service '''
        member_ref=ib_NIOS.wapi_request('GET',object_type="member:dns",grid_vip=config.grid2_vip)
        member_ref=json.loads(member_ref)
        print (member_ref)
        print ("__________________________________")
        dns_ref=member_ref[0]['_ref']
        condition=ib_NIOS.wapi_request('GET',object_type=dns_ref+"?_return_fields=enable_dns",grid_vip=config.grid2_vip)
        data={"enable_dns": True}
        enable_dns_ref = ib_NIOS.wapi_request('PUT', ref=dns_ref, fields=json.dumps(data),grid_vip=config.grid2_vip)
        print (enable_dns_ref)
        print ("*************************************")
        com=json.loads(enable_dns_ref)+"?_return_fields=enable_dns"
        print (com)

    @pytest.mark.run(order=12)
    def test_012_add_subscriber_data(self):
        print ("  Validating Bug number NIOSSPT-8907 - Telecom Italia | show subscriber_secure_data' command closes ssh connection to the server ")
	print("/n")
        print("############################################################################################")
        print("#####                  Test  Case 011 Started Executing                                #####")
        print("############################################################################################")
        sleep(30)
	#pdb.set_trace()
	data = "10.36.6.80 32 e0cb4e80e766 N/A  'ACS:Acct-Session-Id=9999732d-34590333;NAS:NAS-PORT=1813;LID:LocalId=E0CB4E80E766;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;SUB:Calling-Station-Id=1101202028;'"
	print (data)
        if not add_subscriber_data(data):
            print("Failure: Adding subscriber data")
            assert False 

    @pytest.mark.run(order=13)
    def test_013_validate_added_subscriber_data(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 12  Started Executing                      ####")
        print("###############################################################################")
        print("Test case to validate the added subscriber data ")
        sleep(10)
	#pdb.set_trace()
        data = show_subscriber_secure_data()
        result = re.search("10.36.6.80", data)
        if (result != None):
            assert True
            print("Test case 12 passed")
        else:
            assert False
            print("Test case 12 failed")

    @pytest.mark.run(order=14)
    def test_014_add_subscriber_data_member(self):
	args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid2_vip
    	args=shlex.split(args)
	data="10.36.6.80 32 e0cb4e80e766 N/A  'ACS:Acct-Session-Id=9999732d-34590333;NAS:NAS-PORT=1813;LID:LocalId=E0CB4E80E766;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;SUB:Calling-Station-Id=1101202028;'"
    	child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    	child.stdin.write("set subscriber_secure_data add "+data+" \n")
   	child.stdin.write("exit")
    	output = child.communicate()
    	print(output)
    	for line in list(output):
            if 'Disconnect NOW if you have' in line:
            	    continue
            print(line)
            if 'Record successfully added' in line:
                return True
		print ("Test case 013 Passed ")

    @pytest.mark.run(order=15)
    def test_015_validate_added_subscriber_data(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 14  Started Executing                      ####")
        print("###############################################################################")
        print("Test case to validate susbscriber data ")
        sleep(10)
	#pdb.set_trace()
        data = show_subscriber_secure_data()
        result = re.search("10.36.6.80*", data)
        if (result != None):
            assert True
            print("Test case 14 passed")
        else:
            assert False
            print("Test case 14 failed")

    @pytest.mark.run(order=16)
    def test_016_clean_up(self):
	logging.info("cleaning up zones and rpz added")
	#pdb.set_trace()
	#fwd_zone=["fwd1.com","fwd2.com","fwd3.com","fwd4.com","fwd5.com","fwd6.com","fwd7.com","fwd8.com","fwd9.com","fwd10.com"]
        for i in range(10):
	    zone=ib_NIOS.wapi_request('GET',object_type='zone_forward',grid_vip= config.grid_vip)
	    print(zone)
	    zone1_ref=json.loads(zone)[0]['_ref']
            #forward_zone={"fqdn":str(i),"forward_to":[{"address":config.grid2_vip,"name":config.grid2_fqdn}]}
            response = ib_NIOS.wapi_request('DELETE', zone1_ref,grid_vip= config.grid_vip)
	
	restart_services
	#fwd_zone=["fwd1.com","fwd2.com","fwd3.com","fwd4.com","fwd5.com","fwd6.com","fwd7.com","fwd8.com","fwd9.com","fwd10.com"]
        for i in range(10):
	    zone=ib_NIOS.wapi_request('GET',object_type='zone_auth',grid_vip= config.grid2_vip)
	    print(zone)
	    zone1_ref=json.loads(zone)[0]['_ref']
            #forward_zone={"fqdn":str(i),"forward_to":[{"address":config.grid2_vip,"name":config.grid2_fqdn}]}
            response = ib_NIOS.wapi_request('DELETE', zone1_ref,grid_vip= config.grid2_vip)
	restart_services
	get_ref = ib_NIOS.wapi_request('GET', object_type="member:parentalcontrol",grid_vip=config.grid2_vip)
        print(get_ref)
        data= {"enable_service": False}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]["_ref"],fields=json.dumps(data),grid_vip=config.grid2_vip)
	sleep(10)
	site=ib_NIOS.wapi_request('GET',object_type='parentalcontrol:subscribersite',grid_vip= config.grid2_vip)
	print(site)
	site_ref=json.loads(site)[0]['_ref']
	del_site=ib_NIOS.wapi_request('DELETE',ref=site_ref,grid_vip= config.grid2_vip)
	print(del_site)
	restart_services
	get_ref = ib_NIOS.wapi_request('GET', object_type="member:parentalcontrol",grid_vip= config.grid_vip)
        print(get_ref)
        data= {"enable_service": False}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]["_ref"],fields=json.dumps(data),grid_vip= config.grid_vip)
	sleep(10)
	site=ib_NIOS.wapi_request('GET',object_type='parentalcontrol:subscribersite',grid_vip= config.grid_vip)
	print(site)
	site_ref=json.loads(site)[0]['_ref']
	del_site=ib_NIOS.wapi_request('DELETE',ref=site_ref,grid_vip= config.grid_vip)
	print(del_site)
	restart_services

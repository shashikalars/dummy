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

def change_default_route():
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
    child.logfile=sys.stdout
    child.expect('-bash-4.0#')
    child.sendline('ip route del default via 10.35.0.1 dev eth1 table main')
    child.expect('-bash-4.0#')
    child.sendline('ip route add default via 10.36.0.1 dev eth0 table main')
    child.sendline('exit')
    child.expect(pexpect.EOF)
    time.sleep(20)

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

def restart_the_grid():
    logging.info("Restaring the grid")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
    ref = json.loads(grid)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
    sleep(30)
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


def stop_subscriber_collection_services_for_added_site(member):#config.grid_fqdn
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
        print delete
        site_ref_new =  ib_NIOS.wapi_request('GET', object_type='parentalcontrol:subscribersite?name='+site)
        print site_ref_new
        if (site_ref_new == '[]'):
            print ("Successfully deleted subscriber site : Test case 047 passed")
            return True
        else:
            print ("Unable to delete subscriber site : test case 047 failed")
            return None
    else:
        print "No sites to delete"
        return True

def prod_reboot(ip):
    child = pexpect.spawn('ssh admin@'+ip)
    child.logfile=sys.stdout
    child.expect('password:')
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
    

def change_the_memory_of_a_member(vm_id,cpu,memory):
        logging.info("change the memory of a member")
        cmd="reboot_system -H "+str(vm_id)+" -a poweroff"
        result = subprocess.check_output(cmd, shell=True)
        print result
        cmd="vm_specs -H "+vm_id+" -C "+str(cpu)+" -M "+str(memory)
        result = subprocess.check_output(cmd, shell=True)
        print result
        cmd="reboot_system -H "+str(vm_id)+" -a poweron"
        result = subprocess.check_output(cmd, shell=True)
        print result
        assert re.search(r'.*poweron completed for.*',str(result))
        time.sleep(300)
        logging.info("Test case executed")

def remove_rpz_rule(rule,zone):
        reference=ib_NIOS.wapi_request('GET', object_type="record:rpz:cname")
        reference=json.loads(reference)
        for i in reference:
            if rule+"."+zone in i["name"]:
                print i["_ref"]
                ref=i["_ref"]
                reference=ib_NIOS.wapi_request('DELETE', object_type=ref)
                print reference
                if type(reference)!=tuple:
                    return reference
                else:
                    return None
                break

def add_rpz_rule(rule,zone):
    data={"name":rule+"."+zone,"rp_zone":zone,"canonical":rule}
    reference3=ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
    if type(reference3)!=tuple:
        return reference3
    else:
        return None

def delete_the_license(license):
    ref=ib_NIOS.wapi_request('GET', object_type="member:license?type="+license)
    print ref
    ref=json.loads(ref)
    for i in ref:
        reference3=ib_NIOS.wapi_request('DELETE', object_type=i["_ref"])
        print reference3

def add_the_license(member):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+member)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set temp_license')
        child.expect(':')
        child.sendline('11')
        child.expect(':')
        child.sendline('y')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        sleep(300)

class Network(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_001_start_DCA_service(self):

        delete_the_license("DHCP")
        add_the_license(config.grid_member2_vip)
        print("\n")
        print("************************************************")
        print("****      Test cases for INTIAL SETUP      ****")
        print("************************************************")
        logging.info("Enable DCA on the standalone member1")
        data = {"enable_dns": True, "enable_dns_cache_acceleration": True}
        DCA_capable=[config.grid_member1_fqdn,config.grid_member2_fqdn]
        for mem in DCA_capable:
            grid_ref = mem_ref_string(mem)
            print(grid_ref)
            response = ib_NIOS.wapi_request('PUT', object_type=grid_ref, fields=json.dumps(data))
            print(response)
            if type(response)!=tuple:
                print("DCA Enabled successfully")
                assert True
            else:
                print("Failed to enable DCA on the Member1")
                assert False
        sleep(300)

    @pytest.mark.run(order=2)
    def test_002_Validate_DCA_service_running(self):
        logging.info("Validate_DCA_service_running")
        sys_log_member1 = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member1_vip)+' " tail -2000 /infoblox/var/infoblox.log"'
        sys_log_member2='ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member2_vip)+' " tail -2000 /infoblox/var/infoblox.log"'
        out1 = commands.getoutput(sys_log_member1)
        out2 = commands.getoutput(sys_log_member2)
        logging.info (out1,out2)
        res1=re.search(r'DNS cache acceleration is now started',out1)
        res2=re.search(r'DNS cache acceleration is now started',out2)
        if res1!=None and res2!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=3)
    def test_003_Configure_Recurson_Forwarer_RPZ_logging_At_Grid_DNS_Properties(self):
        logging.info("Mofifying and Configure Allow Recursive Query Forwarder and RPZ logging at GRID dns properties")
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:dns")
        get_ref1=json.loads(get_ref)[0]['_ref']
        logging.info(get_ref1)
        data={"allow_recursive_query":True,"allow_query":[{"_struct": "addressac","address":"Any","permission":"ALLOW"}],"forwarders":[config.forwarder_ip],"logging_categories":{"log_rpz":True}}
        put_ref=ib_NIOS.wapi_request('PUT', object_type=get_ref1,fields=json.dumps(data))
        logging.info(put_ref)
        if type(put_ref)!=tuple:
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False

    @pytest.mark.run(order=4)
    def test_004_Validate_Recurson_Forwarer_RPZ_logging_Configured_At_Grid_DNS_Properties(self):
        logging.info("Validating Allow Recursive Query Forwarder and RPZ logging configured at GRID dns properties")
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:dns?_return_fields=allow_recursive_query,forwarders")
        get_ref1=json.loads(get_ref)
        if get_ref1[0]["allow_recursive_query"]==True and get_ref1[0]["forwarders"]==[config.forwarder_ip]:
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False

    @pytest.mark.run(order=5)
    def test_005_Start_DNS_Service(self):
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
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=6)
    def test_006_Validate_DNS_service_is_Enabled(self):
        logging.info("Validate DNS Service is enabled")
        get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
        logging.info(get_tacacsplus)
        res = json.loads(get_tacacsplus)
        logging.info(res)
        for i in res:
            if i["enable_dns"] == True:
                logging.info("Test case execution Passed")
                assert True
            else:
                logging.info("Test case execution Failed")
                assert False

    @pytest.mark.run(order=7)
    def test_007_Modify_Grid_Settings(self):
        logging.info("Mofifying GRID properties")
        response = ib_NIOS.wapi_request('GET', object_type="grid")
        response = json.loads(response)
        response=response[0]["_ref"]
        data={"dns_resolver_setting": {"resolvers": [config.resolver_ip]}}
        res = ib_NIOS.wapi_request('PUT', object_type=response,fields=json.dumps(data))
        logging.info(res)
        print res
        if type(res)!=tuple:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=8)
    def test_008_Validate_Modified_Grid_Settings(self):
        logging.info("Validating GRID properties")
        response = ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=dns_resolver_setting")
        response = json.loads(response)
        response=response[0]["dns_resolver_setting"]["resolvers"]
        if response==[config.resolver_ip]:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=9)
    def test_009_Enable_Parental_Control(self):
        logging.info("enabling parental control")
        response = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber")
        response = json.loads(response)
        response=response[0]["_ref"]
        logging.info(response)
        data={"enable_parental_control": True,"cat_acctname":"InfoBlox", "cat_password":"CSg@vBz!rx7A","category_url":"https://pitchers.rulespace.com/ufsupdate/web.pl","proxy_url":"http://10.196.9.113:8001", "proxy_username":"client", "proxy_password":"infoblox","pc_zone_name":"pc.com","cat_update_frequency":24}
        res = ib_NIOS.wapi_request('PUT', object_type=response,fields=json.dumps(data))
        logging.info(res)
        print res
        if type(res)==tuple:
            if res[0]==400 or res[0]==401:
                logging.info("Test case execution failed")
                assert False
            else:
                logging.info("Test case execution passed")
        else:
            logging.info("Test case execution passed")
            assert True

    @pytest.mark.run(order=10)
    def test_010_Validate_Parental_Control_is_Enabled(self):
        logging.info("validating parental control is enabled")
        response = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber?_return_fields=enable_parental_control")
        logging.info(response)
        response = json.loads(response)
        response=response[0]["enable_parental_control"]
        if response==True:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False
    @pytest.mark.run(order=11)
    def  test_011_Add_Subscriber_site_site2_with_all_DCA_supported_members(self):
        logging.info("Add_Subscriber_site_site2_with_all_the_supported_members")
        logging.info("Adding subscriber site site3")
        data={"name":"site2","maximum_subscribers":100000,"members":[{"name":config.grid_member1_fqdn},{"name":config.grid_member2_fqdn}],"nas_gateways":[{"ip_address":config.rad_client_ip,"name":config.rad_client_name,"shared_secret":config.rad_client_secret}]}
        get_ref=ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data))
        logging.info(get_ref)
        print(get_ref)
        if type(get_ref)!=tuple:
            reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
            reference=json.loads(reference)
            if reference[0]["name"]==data["name"]:
                logging.info("Test case execution passed")
                assert True
            else:
                logging.info("Test case execution Failed")
                assert False
        else:
            logging.info(get_ref)
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=12)
    def  test_012_validate_for_subscriber_site_site2_is_added(self):
        logging.info("validating subscriber site site1 added")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        reference=json.loads(reference)
        if reference[0]["name"]=="site2":
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=13)
    def test_013_Start_the_subscriber_service_on_members(self):
        logging.info("Start the subscriber service on members")
        ref=start_subscriber_collection_services_for_added_site([config.grid_member1_fqdn,config.grid_member1_fqdn])
        if ref!=None:
            logging.info("Test case executed successfully")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
    
    @pytest.mark.run(order=14)
    def test_014_Validate_subscriber_service_is_running(self):
        logging.info("Validating subscriber collection services started")
        members=[config.grid_member1_fqdn,config.grid_member1_fqdn,config.grid_fqdn]
        for mem in members:
            grid_ref = mem_ref_string_pc(mem)
            print grid_ref
            get_ref=ib_NIOS.wapi_request('GET', object_type=grid_ref)
            for ref in get_ref:
                if ref!=tuple:
                    logging.info("Test case execution Passed")
                    assert True
                else:
                    logging.info("Test case execution Failed")
                    assert False

    @pytest.mark.run(order=15)
    def test_015_Check_for_default_value_set_for_Enable_DCA_subscriber_Query_count_logging(self):
        print("\n")
        print("************************************************")
        print("****  Test cases Related to GUI Scenarios  ****")
        print("************************************************")
        logging.info("Check for default value set for Enable DCA subscriber Query count logging")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=dca_sub_query_count")
        get_ref=json.loads(get_ref)[0]["dca_sub_query_count"]
        print get_ref
        if get_ref==False:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=16)
    def test_016_Check_for_default_value_set_for_Enable_DCA_subscriber_Allowed_and_Blocked_list_support(self):
        logging.info("Check for default value set for Enable_DCA subscriber Allowed and Blocked list support")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=dca_sub_bw_list")
        get_ref=json.loads(get_ref)[0]["dca_sub_bw_list"]
        print get_ref
        if get_ref==False:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
    
    @pytest.mark.run(order=17)
    def test_017_start_Syslog_Messages_logs_on_master(self):
        logging.info("Starting Syslog Messages Logs in Master")
        log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
        log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
        logging.info("test case 20 passed")

    @pytest.mark.run(order=18)
    def test_018_Enable_DCA_subscriber_Allowed_and_Blocked_list_support(self):
        logging.info("Enable DCA subscriber Allowed and Blocked list support")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        get_ref=json.loads(get_ref)[0]["_ref"]
        data={"dca_sub_bw_list":True}
        res = ib_NIOS.wapi_request('PUT', object_type=get_ref,fields=json.dumps(data))
        print res
        if type(res)!=tuple:
            logging.info("Test case execution passed")
            time.sleep(30)
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False
    
    @pytest.mark.run(order=19)
    def test_019_stop_syslog_Messages_logs_on_master(self):
        logging.info("Starting Syslog Messages Logs")
        log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
        logging.info("Test case execution passed")
    
    @pytest.mark.run(order=20)
    def test_020_validate_for_infoblox_Log_for_Enabling_DCA_subscriber_Allowed_and_Blocked_list_support(self):
        logging.info("validate for infoblox Log for Enabling DCA subscriber Allowed and Blocked list support")
        LookFor='.*Enable DCA subscriber Allowed & Blocked list.*is enabled on '+config.grid_member1_fqdn+'. A reboot is required'
        logs1=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_member1_vip)
        LookFor='.*Enable DCA subscriber Allowed & Blocked list.*is enabled on '+config.grid_member2_fqdn+'. A reboot is required'
        logs2=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_member2_vip)
        if logs1!=None and logs2!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
     
    @pytest.mark.run(order=21)
    def test_021_start_Syslog_Messages_logs_on_master_and_members(self):
        logging.info("Starting Syslog Messages Logs in Master")
        log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
        log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
        logging.info("test case 20 passed")

    @pytest.mark.run(order=22)
    def test_022_Disable_DCA_subscriber_Allowed_and_Blocked_list_support(self):
        logging.info("Enable DCA subscriber Allowed and Blocked list support")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        get_ref=json.loads(get_ref)[0]["_ref"]
        data={"dca_sub_bw_list":False}
        res = ib_NIOS.wapi_request('PUT', object_type=get_ref,fields=json.dumps(data))
        if type(res)!=tuple:
            logging.info("Test case execution passed")
            time.sleep(30)
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=23)
    def test_023_stop_syslog_Messages_logs_on_master_and_members(self):
        logging.info("Starting Syslog Messages Logs")
        log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
        logging.info("Test case execution passed")
    
    @pytest.mark.run(order=24)
    def test_024_validate_for_infoblox_Log_for_Enabling_DCA_subscriber_Allowed_and_Blocked_list_support(self):
        logging.info("validate for infoblox Log for Enabling DCA subscriber Allowed and Blocked list support")
        LookFor='.*Enable DCA subscriber Allowed & Blocked list.*is disabled on '+config.grid_member1_fqdn+'. A reboot is required'
        logs1=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_member1_vip)
        LookFor='.*Enable DCA subscriber Allowed & Blocked list.*is disabled on '+config.grid_member2_fqdn+'. A reboot is required'
        logs2=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_member2_vip)
        if logs1!=None and logs2!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=25)
    def test_025_stop_the_subscriber_services_on_all_the_members(self):
        logging.info("stop the subscriber services on all the members")
        ref=stop_subscriber_collection_services_for_added_site([config.grid_member1_fqdn,config.grid_member2_fqdn]) 
        if ref!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
        
    @pytest.mark.run(order=26)
    def test_026_delete_the_subscriber_site_site2(self):
        logging.info("delete the subscriber site site2")
        ref=delete_subscriber_site("site2")
        if ref!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=27)
    def test_027_validate_the_subscriber_site_site2_is_deleted(self):
        logging.info("validate the subscriber site site2 is deleted")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        if get_ref=="[]":
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
    
    @pytest.mark.run(order=28)
    def test_028_Add_the_subscriber_site_with_members_which_are_not_DCA_capable(self):
        logging.info("Add the subscriber site with members which are not DCA capable")
        data={"name":"site2","maximum_subscribers":100000,"members":[{"name":config.grid_fqdn}],"nas_gateways":[{"ip_address":"2.2.2.2","name":"nas1","shared_secret":"test123"}]}
        get_ref=ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data))
        logging.info(get_ref)
        print get_ref
        if type(get_ref)!=tuple:
            reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
            reference=json.loads(reference)
            if reference[0]["name"]==data["name"]:
                logging.info("Test case execution passed")
                assert True
            else:
                logging.info("Test case execution Failed")
                assert False
        else:
            logging.info(get_ref)
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=29)
    def  test_029_validate_for_subscriber_site_site2_is_added(self):
        logging.info("validating subscriber site site1 added")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        reference=json.loads(reference)
        if reference[0]["name"]=="site2":
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
    
    @pytest.mark.run(order=30)
    def test_030_Start_the_subscriber_service_on_members_which_are_not_DCA_capable(self):
        logging.info("Start the subscriber service on members which are not DCA capable")
        ref=start_subscriber_collection_services_for_added_site([config.grid_fqdn])
        if ref!=None:
            logging.info("Test case executed successfully")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
        
    @pytest.mark.run(order=31)
    def test_031_Validate_subscriber_service_is_running_on_non_DCA_capable_members(self):
        logging.info("Validating subscriber collection services started on non DCA capable members")
        members=[config.grid_fqdn]
        for mem in members:
            grid_ref = mem_ref_string_pc(mem)
            print grid_ref
            get_ref=ib_NIOS.wapi_request('GET', object_type=grid_ref)
            #get_ref=json.loads(get_ref)
            #print get_ref
            for ref in get_ref:
                if ref!=tuple:
                    logging.info("Test case execution Passed")
                    assert True
                else:
                    logging.info("Test case execution Failed")
                    assert False

    @pytest.mark.run(order=32)
    def test_032_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("test case 35 passed")

    @pytest.mark.run(order=33)
    def test_033_Enable_DCA_subscriber_Query_count_logging_on_site_with_no_members_are_DCA_capable(self):
        logging.info("Enable DCA subscriber Query count logging on site with no members are DCA capable")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        get_ref=json.loads(get_ref)[0]["_ref"]
        data={"dca_sub_query_count":True}
        res = ib_NIOS.wapi_request('PUT', object_type=get_ref,fields=json.dumps(data))
        print res
        if type(res)==tuple:
            if '"Error": "AdmConDataError: None (IBDataConflictError: IB.Data.Conflict:Atleast one member in site \'site2\' should be software DNS-Cache-Acceleration capable, when query count logging is enabled.)", \n  "code": "Client.Ibap.Data.Conflict", \n  "text": "Atleast one member in site \'site2\' should be software DNS-Cache-Acceleration capable, when query count logging is enabled."\n' in res[1]:
                logging.info("Test case execution passed")
                time.sleep(5)
                assert True
            else:
                logging.info("Test case execution Failed")
                assert False
    
    @pytest.mark.run(order=34)
    def test_034_Enable_DCA_subscriber_Allowed_and_Blocked_list_support_on_site_with_no_members_are_DCA_capable(self):
        logging.info("Enable DCA subscriber Allowed and blocked list support on site with no members are DCA capable")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        get_ref=json.loads(get_ref)[0]["_ref"]
        data={"dca_sub_bw_list":True}
        res = ib_NIOS.wapi_request('PUT', object_type=get_ref,fields=json.dumps(data))
        if type(res)==tuple:
            if '"Error": "AdmConDataError: None (IBDataConflictError: IB.Data.Conflict:Atleast one capable site member should be present when Allowed and Blocked list is enabled.)", \n  "code": "Client.Ibap.Data.Conflict", \n  "text": "Atleast one capable site member should be present when Allowed and Blocked list is enabled."\n' in res[1]:
                logging.info("Test case execution passed")
                time.sleep(5)
                assert True
            else:
                logging.info("Test case execution Failed")
                assert False
        else:
            assert False

    @pytest.mark.run(order=35)
    def test_035_stop_the_subscriber_services_on_all_the_members(self):
        logging.info("stop the subscriber services on all the members")
        ref=stop_subscriber_collection_services_for_added_site([config.grid_fqdn])
        if ref!=None:
            logging.info("Test case executed succesfully")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
        
    @pytest.mark.run(order=36)
    def test_036_delete_the_subscriber_site(self):
        logging.info("delete the subscriber site site2")
        ref=delete_subscriber_site("site2")
        print ref
        if ref!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=37)
    def test_037_validate_the_subscriber_site_site2_is_deleted(self):
        logging.info("validate the subscriber site site2 is deleted")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        if get_ref=="[]":
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
    
    @pytest.mark.run(order=38)
    def test_038_change_the_memory_of_member_to_22GB(self):
        logging.info("change the memory of member to 22GB")
        change_the_memory_of_a_member(config.member2_vm_id,8,22)
        
        
    @pytest.mark.run(order=39)
    def test_039_Add_the_subscriber_site_with_members_which_are_DCA_capable_but_with_memory_less_than_35GB(self):
        logging.info("Add the subscriber site_with members which _are not DCA capable but with memory less than 35GB")
        data={"name":"site2","maximum_subscribers":100000,"members":[{"name":config.grid_member2_fqdn}],"nas_gateways":[{"ip_address":"2.2.2.2","name":"nas1","shared_secret":"test123"}]}
        get_ref=ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data))
        logging.info(get_ref)
        print get_ref
        if type(get_ref)!=tuple:
            reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
            reference=json.loads(reference)
            if reference[0]["name"]==data["name"]:
                logging.info("Test case execution passed")
                assert True
            else:
                logging.info("Test case execution Failed")
                assert False
        else:
            logging.info(get_ref)
            logging.info("Test case execution failed")
            assert False
            
    @pytest.mark.run(order=40)
    def  test_040_validate_for_subscriber_site_site2_is_added_with_members_which_are_DCA_capable_but_with_memory_less_than_35GB(self):
        logging.info("validating subscriber site site1 added")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        reference=json.loads(reference)
        if reference[0]["name"]=="site2":
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
    
    @pytest.mark.run(order=41)
    def test_041_Start_the_subscriber_service_on_members_which_are_DCA_capable_but_with_memory_less_than_35GB(self):
        logging.info("Start the subscriber service on members which are not DCA capable but with memory less than 35GB")
        ref=start_subscriber_collection_services_for_added_site([config.grid_member2_fqdn])
        if ref!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
            
    @pytest.mark.run(order=42)
    def test_042_Validate_subscriber_service_is_running_on_members_which_are_DCA_capable_but_with_memory_less_than_35GB(self):
        logging.info("Validating subscriber collection services started on members which are DCA capable but with memory less than35GB")
        members=[config.grid_member2_fqdn]
        for mem in members:
            grid_ref = mem_ref_string_pc(mem)
            print grid_ref
            get_ref=ib_NIOS.wapi_request('GET', object_type=grid_ref)
            #get_ref=json.loads(get_ref)
            #print get_ref
            for ref in get_ref:
                if ref!=tuple:
                    logging.info("Test case execution Passed")
                    assert True
                else:
                    logging.info("Test case execution Failed")
                    assert False
    
    @pytest.mark.run(order=43)
    def test_043_Enable_DCA_subscriber_Allowed_and_Blocked_list_support_on_site_with_members_are_DCA_capable_but_with_memory_less_than_35GB(self):
        logging.info("Enable DCA subscriber Allowed and Blocked list support on_site with no members are DCA capable")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        get_ref=json.loads(get_ref)[0]["_ref"]
        data={"dca_sub_bw_list":True}
        res = ib_NIOS.wapi_request('PUT', object_type=get_ref,fields=json.dumps(data))
        print res
        if type(res)==tuple:
            if ' "Error": "AdmConDataError: None (IBDataConflictError: IB.Data.Conflict:Site member(s) [\''+config.grid_member2_fqdn+'\'] must have at least 35 GB of memory, when Allowed and Blocked list is enabled.)", \n  "code": "Client.Ibap.Data.Conflict", \n  "text": "Site member(s) [\''+config.grid_member2_fqdn+'\'] must have at least 35 GB of memory, when Allowed and Blocked list is enabled."\n}' in res[1]:
                logging.info("Test case execution passed")
                time.sleep(5)
                assert True
            else:
                logging.info("Test case execution Failed")
                assert False
        else:
            assert False

    @pytest.mark.run(order=44)
    def test_044_stop_the_subscriber_services_on_all_the_site_members(self):
        logging.info("stop the subscriber services on all the members")
        ref=stop_subscriber_collection_services_for_added_site([config.grid_member2_fqdn])
        if ref!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
            
    @pytest.mark.run(order=45)
    def test_045_delete_the_subscriber_site(self):
        logging.info("delete the subscriber site site2")
        ref=delete_subscriber_site("site2")
        if ref!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=46)
    def test_046_validate_the_subscriber_site_site2_is_deleted(self):
        logging.info("validate the subscriber site site2 is deleted")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        if get_ref=="[]":
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=47)
    def test_047_change_the_memory_of_member_to_40GB(self):
        logging.info("change the memory of member to 40GB")
        change_the_memory_of_a_member(config.member2_vm_id,8,40)
    
    @pytest.mark.run(order=48)
    def test_048_Add_the_subscriber_site_with_DCA_capable_members(self):
        logging.info("Add the subscriber site with DCA capable member")
        data={"name":"site2","maximum_subscribers":100000,"members":[{"name":config.grid_member1_fqdn},{"name":config.grid_member2_fqdn}],"nas_gateways":[{"ip_address":"2.2.2.2","name":"nas1","shared_secret":"test123"}]}
        get_ref=ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data))
        logging.info(get_ref)
        print get_ref
        if type(get_ref)!=tuple:
            reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
            reference=json.loads(reference)
            if reference[0]["name"]==data["name"]:
                logging.info("Test case execution passed")
                assert True
            else:
                logging.info("Test case execution Failed")
                assert False
        else:
            logging.info(get_ref)
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=49)
    def  test_049_validate_for_subscriber_site_site2_is_added_with_members_which_are_DCA_capable(self):
        logging.info("validating subscriber site site1 added")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        reference=json.loads(reference)
        if reference[0]["name"]=="site2":
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
    
    @pytest.mark.run(order=50)
    def test_050_Start_the_subscriber_service_on_DCA_capable_member(self):
        logging.info("Start the subscriber service on DCA capable member")
        ref=start_subscriber_collection_services_for_added_site([config.grid_member1_fqdn,config.grid_member2_fqdn])
        if ref!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
            
    @pytest.mark.run(order=51)
    def test_051_Validate_subscriber_service_is_running_on_members_which_are_DCA_capable(self):
        logging.info("Validating subscriber collection services started on members which are DCA capable")
        members=[config.grid_member1_fqdn,config.grid_member2_fqdn]
        for mem in members:
            grid_ref = mem_ref_string_pc(mem)
            print grid_ref
            get_ref=ib_NIOS.wapi_request('GET', object_type=grid_ref)
            for ref in get_ref:
                if ref!=tuple:
                    logging.info("Test case execution Passed")
                    assert True
                else:
                    logging.info("Test case execution Failed")
                    assert False
    
    @pytest.mark.run(order=52)
    def test_052_start_syslog_Messages_logs_on_master(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/infoblox/var/infoblox.log",config.grid_member1_vip)
        log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
        logging.info("Test case execution passed")

    @pytest.mark.run(order=53)
    def test_053_Enable_DCA_subscriber_Allowed_and_Blocked_list_support_on_site(self):
        logging.info("Enable DCA subscriber Allowed and Blocked list support on site")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        get_ref=json.loads(get_ref)[0]["_ref"]
        data={"dca_sub_bw_list":True}
        res = ib_NIOS.wapi_request('PUT', object_type=get_ref,fields=json.dumps(data))
        print res
        if type(res)!=tuple:
            logging.info("Test case execution passed")
            time.sleep(30)
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=54)
    def test_054_stop_syslog_Messages_logs_on_master(self):
        logging.info("Starting Syslog Messages Logs")
        log("stop","/infoblox/var/infoblox.log",config.grid_member1_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid_member2_vip)
        logging.info("Test case execution passed")

    @pytest.mark.run(order=55)
    def test_055_validate_for_infoblox_Log_for_Enabling_DCA_subscriber_Allowed_and_Blocked_list_support(self):
        logging.info("validate for infoblox Log for Enabling DCA subscriber Allowed and Blocked list support")
        LookFor='.*Enable DCA subscriber Allowed & Blocked list.*is enabled on '+config.grid_member1_fqdn+'. A reboot is required'
        logs1=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_member1_vip)
        print logs1
        LookFor='.*Enable DCA subscriber Allowed & Blocked list.*is enabled on '+config.grid_member2_fqdn+'. A reboot is required'
        logs2=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_member2_vip)
        print logs2
        if logs2!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=56)
    def test_056_stop_the_subscriber_services_on_all_the_members(self):
        logging.info("stop the subscriber services on all the members")
        ref=stop_subscriber_collection_services_for_added_site([config.grid_member1_fqdn,config.grid_member2_fqdn])
        if ref!=None:
            sleep(40)
            logging.info("Test case execution passed")
            assert True   
        else:
            logging.info("Test case execution failed")
            assert False
        
    @pytest.mark.run(order=57)
    def test_057_remove_a_single_member_from_subscriber_site_when_DCA_subscriber_Allowed_and_Blocked_list_support_is_enabled_on_site(self):
        logging.info("remove a single member from subscriber site when DCA subscriber Allowed and Blocked list support is enabled on site")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        get_ref=json.loads(get_ref)
        ref=get_ref[0]["_ref"]
        #data={"members":[{"name":config.grid_member2_fqdn}]}
        data={"members":[{"name":config.grid_member1_fqdn}]}
        get_ref=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
        logging.info(get_ref)
        print get_ref
        if type(get_ref)!=tuple:
            reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
            reference=json.loads(reference)
            if reference[0]["name"]=="site2":
                logging.info("Test case execution passed")
                assert True
            else:
                logging.info("Test case execution Failed")
                assert False
        else:
            logging.info(get_ref)
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=58)
    def test_058_remove_all_the_members_from_subscriber_site_when_DCA_subscriber_Allowed_and_Blocked_list_support_is_enabled_on_site(self):
        logging.info("remove all the members from subscriber site when DCA subscriber Allowed and Blocked list support is enabled on site")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        get_ref=json.loads(get_ref)
        ref=get_ref[0]["_ref"]
        data={"members":[]}
        get_ref=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
        logging.info(get_ref)
        print get_ref
        if type(get_ref)==tuple:
            if '"Error": "AdmConDataError: None (IBDataConflictError: IB.Data.Conflict:Atleast one capable site member should be present when Allowed and Blocked list is enabled.)", \n  "code": "Client.Ibap.Data.Conflict", \n  "text": "Atleast one capable site member should be present when Allowed and Blocked list is enabled."' in get_ref[1]:
                logging.info("Test case execution passed")
                assert True
            else:
                logging.info("Test case execution Failed")
                assert False
        else:
            logging.info(get_ref)
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=59)
    def test_059_Disable_DCA_subscriber_Allowed_and_Blocked_list_support_on_site(self):
        logging.info("Disable DCA subscriber Allowed and Blocked list support on site")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        get_ref=json.loads(get_ref)[0]["_ref"]
        data={"dca_sub_bw_list":False}
        res = ib_NIOS.wapi_request('PUT', object_type=get_ref,fields=json.dumps(data))
        if type(res)!=tuple:
            logging.info("Test case execution passed")
            time.sleep(5)
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=60)
    def test_060_validate_DCA_subscriber_Allowed_and_Blocked_list_support_is_disabled_on_site(self):
        logging.info("Validate DCA subscriber Query count reporting and Enable DCA subscriber Allowed and Blocked list support are disbled")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=dca_sub_bw_list")
        get_ref=json.loads(get_ref)
        if get_ref[0]["dca_sub_bw_list"]==False:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=61)
    def test_061_Enable_DCA_subscriber_Query_count_logging_on_site_site2(self):
        logging.info("Enable DCA subscriber Query count logging on site site2")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        get_ref=json.loads(get_ref)[0]["_ref"]
        data={"dca_sub_query_count":True}
        res = ib_NIOS.wapi_request('PUT', object_type=get_ref,fields=json.dumps(data))
        if type(res)!=tuple:
            logging.info("Test case execution passed")
            time.sleep(5)
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=62)
    def test_062_validate_Enable_DCA_subscriber_Query_count_logging_on_site(self):
        logging.info("Validate DCA subscriber Query count reporting and Enable DCA subscriber Allowed and Blocked list support are enabled")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=dca_sub_bw_list,dca_sub_query_count")
        get_ref=json.loads(get_ref)
        if get_ref[0]["dca_sub_query_count"]==True:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=63)
    def test_063_remove_all_the_members_from_subscriber_site_when_DCA_subscriber_Query_count_logging_is_enabled_on_site(self):
        logging.info("remove all the members from subscriber site when DCA subscriber Query count logging is enabled on site")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        get_ref=json.loads(get_ref)
        ref=get_ref[0]["_ref"]
        data={"members":[]}
        get_ref=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
        logging.info(get_ref)
        print get_ref
        if type(get_ref)==tuple:
            if '"Atleast one member in site \'site2\' should be software DNS-Cache-Acceleration capable, when query count logging is enabled."' in get_ref[1]:
                logging.info("Test case execution passed")
                assert True
            else:
                logging.info("Test case execution Failed")
                assert False
        else:
            logging.info(get_ref)
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=64)
    def test_064_Enable_DCA_subscriber_Allowed_and_Blocked_list_support_on_site(self):
        logging.info("Eisable DCA subscriber Allowed and Blocked list support on site")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        get_ref=json.loads(get_ref)[0]["_ref"]
        data={"dca_sub_bw_list":True}
        res = ib_NIOS.wapi_request('PUT', object_type=get_ref,fields=json.dumps(data))
        if type(res)!=tuple:
            logging.info("Test case execution passed")
            time.sleep(5)
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=65)
    def test_065_validate_DCA_subscriber_Allowed_and_Blocked_list_support_is_enabled_on_site(self):
        logging.info("Validate DCA subscriber Query count reporting and Enable DCA subscriber Allowed and Blocked list support are enabled")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=dca_sub_bw_list")
        get_ref=json.loads(get_ref)
        if get_ref[0]["dca_sub_bw_list"]==True:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False
    
    @pytest.mark.run(order=66)
    def test_066_Add_non_DCA_capable_member_to_site_when_DCA_subscriber_Allowed_and_Blocked_list_support_is_enabled(self):
        logging.info("Add non DCA capable member to site when DCA subscriber Allowed and Blocked list support is enabled")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        get_ref=json.loads(get_ref)
        ref=get_ref[0]["_ref"]
        data={"members":[{"name":config.grid_fqdn}]}
        get_ref=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
        logging.info(get_ref)
        print get_ref
        if type(get_ref)==tuple:
            if '"Atleast one member in site \'site2\' should be software DNS-Cache-Acceleration capable, when query count logging is enabled."' in get_ref[1]:
                logging.info("Test case execution passed")
                assert True
            else:
                logging.info("Test case execution Failed")
                assert False
        else:
            logging.info(get_ref)
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=67)
    def test_067_stop_the_subscriber_services_on_all_the_members(self):
        logging.info("stop the subscriber services on all the members")
        ref=stop_subscriber_collection_services_for_added_site([config.grid_member2_fqdn])
        if ref!=None:
            assert True
            logging.info("Test case execution passed")
        else:
            assert False
            logging.info("Test case execution failed")
            
    @pytest.mark.run(order=68)
    def test_068_delete_the_subscriber_site_site2(self):
        logging.info("delete the subscriber site site2")
        ref=delete_subscriber_site("site2")
        if ref!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=69)
    def test_069_validate_the_subscriber_site_site2_is_deleted(self):
        logging.info("validate the subscriber site site2 is deleted")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        if get_ref=="[]":
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=70)
    def test_070_Add_the_subscriber_site_with_all_DCA_supported_members(self):
        logging.info("Add the subscriber site with all the DCA supported members")
        data={"name":"site2","maximum_subscribers":100000,"members":[{"name":config.grid_member1_fqdn},{"name":config.grid_member2_fqdn}],"nas_gateways":[{"ip_address":"2.2.2.2","name":"nas1","shared_secret":"test123"}]}
        get_ref=ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data))
        logging.info(get_ref)
        print get_ref
        if type(get_ref)!=tuple:
            reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
            reference=json.loads(reference)
            if reference[0]["name"]==data["name"]:
                logging.info("Test case execution passed")
                assert True
            else:
                logging.info("Test case execution Failed")
                assert False
        else:
            logging.info(get_ref)
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=71)
    def  test_071_validate_for_subscriber_site_site2_is_added_with_all_DCA_supported_members(self):
        logging.info("validating subscriber site site2 is added with all DCA supported members")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        reference=json.loads(reference)
        if reference[0]["name"]=="site2":
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=72)
    def test_072_Start_the_subscriber_service_on_all_DCA_supported_members(self):
        logging.info("Start the subscriber service on all the members")
        ref=start_subscriber_collection_services_for_added_site([config.grid_member1_fqdn,config.grid_member2_fqdn])
        if ref!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
            
    @pytest.mark.run(order=73)
    def test_073_Validate_subscriber_service_is_running_on_members_which_are_DCA_capable(self):
        logging.info("Validating subscriber collection services started on members which are DCA capable")
        members=[config.grid_member1_fqdn,config.grid_member2_fqdn]
        for mem in members:
            grid_ref = mem_ref_string_pc(mem)
            print grid_ref
            get_ref=ib_NIOS.wapi_request('GET', object_type=grid_ref)
            for ref in get_ref:
                if ref!=tuple:
                    logging.info("Test case execution Passed")
                    assert True
                else:
                    logging.info("Test case execution Failed")
                    assert False
    
    @pytest.mark.run(order=74)
    def test_074_Enable_DCA_subscriber_Allowed_and_Blocked_list_support_on_site(self):
        logging.info("Enable DCA subscriber Allowed and Blocked list support on site")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        get_ref=json.loads(get_ref)[0]["_ref"]
        data={"dca_sub_bw_list":True}
        res = ib_NIOS.wapi_request('PUT', object_type=get_ref,fields=json.dumps(data))
        if type(res)!=tuple:
            logging.info("Test case execution passed")
            time.sleep(5)
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=75)
    def test_075_validate_DCA_subscriber_Allowed_and_Blocked_list_support_is_enabled_on_site(self):
        logging.info("Validate DCA subscriber Query count reporting and Enable DCA subscriber Allowed and Blocked list support are enabled")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=dca_sub_bw_list")
        get_ref=json.loads(get_ref)
        if get_ref[0]["dca_sub_bw_list"]==True:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=76)
    def test_076_change_the_memory_of_member_to_22GB(self):
        logging.info("change the memory of member to 22GB")
        change_the_memory_of_a_member(config.member2_vm_id,8,22)

    @pytest.mark.run(order=77)
    def test_077_modify_site_properties_when_the_memory_is_changed_to_less_than_35GB(self):
        logging.info("modify site properties when the memory is changed to less than 35GB")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        get_ref=json.loads(get_ref)
        ref=get_ref[0]["_ref"]
        data={"comment":"Chnging the site property valiues"}
        get_ref=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
        logging.info(get_ref)
        print get_ref
        if type(get_ref)==tuple:
            if '"Site member(s) [\''+config.grid_member2_fqdn+'\'] must have at least 35 GB of memory, when Allowed and Blocked list is enabled."' in get_ref[1] :
                logging.info("Test case execution passed")
                assert True
            else:
                logging.info("Test case execution Failed")
                assert False
        else:
            logging.info(get_ref)
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=78)
    def test_078_check_for_ip_space_descriminator_is_removed(self):
        logging.info("check for ip space descriminator is removed")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:ipspacediscriminator")
        print get_ref
        if '{ "Error": "AdmConProtoError: Unknown object type (parentalcontrol:ipspacediscriminator)", \n  "code": "Client.Ibap.Proto", \n  "text": "Unknown object type (parentalcontrol:ipspacediscriminator)"\n}'  in get_ref[1]: 
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=79)
    def test_079_stop_the_subscriber_services_on_all_the_members(self):
        logging.info("stop the subscriber services on all the members")
        ref=stop_subscriber_collection_services_for_added_site([config.grid_member1_fqdn,config.grid_member2_fqdn])
        if ref!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
            
    @pytest.mark.run(order=80)
    def test_080_delete_the_subscriber_site(self):
        logging.info("delete subscriber site site1")
        ref=delete_subscriber_site("site2")
        if ref!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=81)
    def test_081_validate_the_subscriber_site_site2_is_deleted(self):
        logging.info("validate the subscriber site site2 is deleted")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        if get_ref=="[]":
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=82)
    def test_082_Modify_Grid_Settings_to_download_zvelo_data(self):
        print("\n")
        print("************************************************")
        print("****  Test cases Related to ZVELO DOWNLOAD  ****")
        print("************************************************")
        logging.info("Mofifying GRID properties to add resolver to download ZVELO data")
        response = ib_NIOS.wapi_request('GET', object_type="grid")
        response = json.loads(response)
        response=response[0]["_ref"]
        data={"dns_resolver_setting": {"resolvers": [config.resolver_ip]}}
        res = ib_NIOS.wapi_request('PUT', object_type=response,fields=json.dumps(data))
        logging.info(res)
        if type(res)!=tuple:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=83)
    def test_083_Validate_Modified_Grid_Settings_to_validate_resolver_is_added(self):
        logging.info("Validating GRID properties to validate reolver is added")
        response = ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=dns_resolver_setting")
        response = json.loads(response)
        response=response[0]["dns_resolver_setting"]["resolvers"]
        if response==[config.resolver_ip]:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=84)
    def test_084_Enable_Parental_Control_with_proxy_url(self):
        logging.info("enabling parental control with proxy url")
        response = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber")
        response = json.loads(response)
        response=response[0]["_ref"]
        logging.info(response)
        data={"enable_parental_control": True,"cat_acctname":"infoblox_sdk", "cat_password":"LinWmRRDX0q","category_url":"https://dl.zvelo.com/","pc_zone_name":"pc.com","cat_update_frequency":1,"proxy_url":config.zvelo_proxy,"proxy_username":config.zvelo_username,"proxy_password":config.zvelo_password,"interim_accounting_interval":2}
        res = ib_NIOS.wapi_request('PUT', object_type=response,fields=json.dumps(data))
        logging.info(res)
        print res
        if type(res)==tuple:
            if res[0]==400 or res[0]==401:
                logging.info("Test case execution failed")
                assert False
            else:
                logging.info("Test case execution passed")
        else:
            logging.info("Test case execution passed")
            assert True

    @pytest.mark.run(order=85)
    def test_085_Validate_Parental_Control_is_Enabled(self):
        logging.info("validating parental control is enabled")
        response = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber?_return_fields=enable_parental_control,cat_acctname,category_url,proxy_url,proxy_username,proxy_password")
        logging.info(response)
        response = json.loads(response)
        pc=response[0]["enable_parental_control"]
        act_name=response[0]["cat_acctname"]
        proxy_url=response[0]["proxy_url"]
        proxy_username=response[0]["proxy_username"]
        proxy_password=response[0]["proxy_password"]
        if pc==True and act_name=="infoblox_sdk" and proxy_url==config.zvelo_proxy and proxy_username== config.zvelo_username and proxy_password==config.zvelo_password:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=86)
    def test_086_Add_the_subscriber_site_with_all_members(self):
        logging.info("Add the subscriber site with all members")
        data={"name":"site2","maximum_subscribers":100000,"members":[{"name":config.grid_fqdn},{"name":config.grid_member1_fqdn},{"name":config.grid_member2_fqdn}],"nas_gateways":[{"ip_address":"2.2.2.2","name":"nas1","shared_secret":"test123"}]}
        get_ref=ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data))
        logging.info(get_ref)
        print get_ref
        if type(get_ref)!=tuple:
            reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
            reference=json.loads(reference)
            if reference[0]["name"]==data["name"]:
                logging.info("Test case execution passed")
                assert True
            else:
                logging.info("Test case execution Failed")
                assert False
        else:
            logging.info(get_ref)
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=87)
    def test_087_Start_the_subscriber_service_on_all_the_members(self):
        logging.info("Start the subscriber service on all the members")
        ref=start_subscriber_collection_services_for_added_site([config.grid_member1_fqdn,config.grid_member2_fqdn,config.grid_fqdn])
        if ref!=None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
        
    @pytest.mark.run(order=88)
    def test_088_start_category_download_Messages_logs_on_master_with_only_proxy_url(self):
        logging.info("Starting category download Messages Logs on master")
        log("start","/storage/zvelo/log/category_download.log",config.grid_vip)
        log("start","/storage/zvelo/log/category_download.log",config.grid_member1_vip)
        log("start","/storage/zvelo/log/category_download.log",config.grid_member2_vip)
        logging.info("Test case execution passed")
        sleep(3200)

    @pytest.mark.run(order=89)
    def test_089_stop_category_download_Messages_logs_on_master(self):
        logging.info("Stop Syslog Messages Logs on master and member")
        logging.info("Stop category download in master")
        log("stop","/storage/zvelo/log/category_download.log",config.grid_vip)
        log("stop","/storage/zvelo/log/category_download.log",config.grid_member1_vip)
        log("stop","/storage/zvelo/log/category_download.log",config.grid_member2_vip)
        logging.info("Test case execution passed")

    @pytest.mark.run(order=90)
    def test_090_validate_for_zvelo_download_data_completion_on_master(self):
        logging.info("Validating category download Messages Logs for data completion")
        LookFor=".*zvelodb download completed.*"
        logs=logv(LookFor,"/storage/zvelo/log/category_download.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=91)
    def test_091_validate_for_zvelo_download_data_completion_on_member1(self):
        logging.info("Validating category download Messages Logs for data completion")
        #LookFor="zvelodb download completed | No updates available for database version | No updates available for database version"
        LookFor=".*zvelodb download completed.*"
        logs=logv(LookFor,"/storage/zvelo/log/category_download.log",config.grid_member1_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=92)
    def test_092_validate_for_zvelo_download_data_completion_on_member2(self):
        logging.info("Validating category download Messages Logs for data completion")
        #LookFor=".*zvelodb download completed | No updates available for database version | No updates available for database version"
        LookFor=".*zvelodb download completed.*"
        logs=logv(LookFor,"/storage/zvelo/log/category_download.log",config.grid_member2_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=93)
    def test_093_stop_the_subscriber_services_on_all_the_members(self):
        logging.info("stop the subscriber services on all the members")
        ref=stop_subscriber_collection_services_for_added_site([config.grid_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn])
        logging.info("Test case execution failed")

    @pytest.mark.run(order=94)
    def test_094_delete_the_subscriber_site_site2(self):
        logging.info("delete the subscriber site site2")
        ref=delete_subscriber_site("site2")
        if ref!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=95)
    def test_095_validate_the_subscriber_site_site2_is_deleted(self):
        logging.info("validate the subscriber site site2 is deleted")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        if get_ref=="[]":
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
            
    @pytest.mark.run(order=96)
    def test_096_change_the_memory_of_member_to_40GB(self):
        logging.info("change the memory of member to 40GB")
        change_the_memory_of_a_member(config.member2_vm_id,8,40)

    @pytest.mark.run(order=97)
    def test_097_Configure_DNS_Resolver_At_Grid_Properties(self):
        logging.info("Configure DNS Resolver At GRID properties")
        response = ib_NIOS.wapi_request('GET', object_type="grid")
        response = json.loads(response)
        response=response[0]["_ref"]
        data={"dns_resolver_setting": {"resolvers": ["127.0.0.1"]}}
        res = ib_NIOS.wapi_request('PUT', object_type=response,fields=json.dumps(data))
        print res
        logging.info(res)
        if type(res)!=tuple:
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False

    @pytest.mark.run(order=98)
    def test_098_Validate_DNS_Resolver_At_Grid_Properties(self):
        logging.info("Validate DNS Resolver is configured at  GRID properties")
        response = ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=dns_resolver_setting")
        response = json.loads(response)
        response=response[0]["dns_resolver_setting"]["resolvers"]
        print response
        if response==["127.0.0.1"]:
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False

    @pytest.mark.run(order=99)
    def test_099_Add_the_subscriber_site_with_all_DCA_supported_members(self):
        stop_subscriber_collection_services_for_added_site([config.grid_member2_fqdn])
        sleep(30)
        #get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        #get_ref=json.loads(get_ref)[0]["_ref"]
        logging.info("Add the subscriber site with all the DCA supported members")
        #data={"members":[{"name":config.grid_member2_fqdn}]}
        data={"blocking_ipv4_vip1": "1.1.1.1","blocking_ipv4_vip2": "2.2.2.2","msps":[{"ip_address": config.proxy_server1}],"spms": [{"ip_address": "10.12.11.11"}],"name":"site2","maximum_subscribers":100000,"members":[{"name":config.grid_member2_fqdn}],"nas_gateways":[{"ip_address":config.rad_client_ip,"name":"nas1","shared_secret":"testing123"},{"ip_address":config.rad_client_ip_lan,"name":"nas1","shared_secret":"testing123"}],"dca_sub_query_count":True}
        get_ref=ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data))
        logging.info(get_ref)
        print get_ref
        if type(get_ref)!=tuple:
            reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
            reference=json.loads(reference)
            if reference[0]["name"]=="site2":
                logging.info("Test case  execution passed")
                assert True
            else:
                logging.info("Test case  execution Failed")
                assert False
        else:
            logging.info(get_ref)
            logging.info("Test case  execution failed")
            assert False

    @pytest.mark.run(order=100)
    def  test_100_validate_for_subscriber_site_site2_is_added_with_all_DCA_supported_members(self):
        logging.info("validating subscriber site site2 is added with all DCA supported members")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        reference=json.loads(reference)
        if reference[0]["name"]=="site2":
            logging.info("Test case  execution passed")
            assert True
        else:
            logging.info("Test case  execution failed")
            assert False

    @pytest.mark.run(order=101)
    def test_101_Start_the_subscriber_service_on_all_DCA_supported_members(self):
        logging.info("Start the subscriber service on all the members")
        ref=start_subscriber_collection_services_for_added_site([config.grid_member2_fqdn])
        if ref!=None:
            logging.info("Test Case  Execution passed")
            sleep(150)
            assert True
        else:
            logging.info("Test Case  Execution failed")
            assert False

    @pytest.mark.run(order=102)
    def test_102_Validate_subscriber_service_is_running_on_members_which_are_DCA_capable(self):
        logging.info("Validating subscriber collection services started on members which are DCA capable")
        members=[config.grid_member2_fqdn]
        for mem in members:
            print mem 
            grid_ref = mem_ref_string_pc(mem)
            print grid_ref
            get_ref=ib_NIOS.wapi_request('GET', object_type=grid_ref)
            for ref in get_ref:
                if ref!=tuple:
                    logging.info("Test Case  Execution Passed")
                    assert True
                else:
                    logging.info("Test Case  Execution Failed")
                    assert False
    '''
    @pytest.mark.run(order=106)
    def test_103_Replace_radcient_client_ips_In_Radius_message_files_with_Configuration_file_values(self):
        logging.info("Replace Radclient IPs in radius message files with configuration file values")
        dig_cmd = 'sed -i s/rad_client_ip/'+str(config.rad_client_ip)+'/g RFE_9980_part1_radfiles/*; sed -i s/client_ip/'+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/*;sed -i s/client_ip2/'+str(config.client_ip2)+'/g RFE_9980_part1_radfiles/*;sed -i s/client_ip3/'+str(config.client_ip3)+'/g RFE_9980_part1_radfiles/*;sed -i s/client_ip4/'+str(config.client_ip4)+'/g RFE_9980_part1_radfiles/*; sed -i s/client_network_8/'+str(config.client_network_8)+'/g RFE_9980_part1_radfiles/*;sed -i s/client_network_24/'+str(config.client_network_24)+'/g RFE_9980_part1_radfiles/*; sed -i s/client_network_16/'+str(config.client_network_16)+'/g RFE_9980_part1_radfiles/*; sed -i s/client_network_32/'+str(config.client_network_32)+'/g RFE_9980_part1_radfiles/*'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)
    '''
    @pytest.mark.run(order=103)
    def test_103_Replace_radcient_client_ips_In_Radius_message_files_with_Configuration_file_values(self):
        logging.info("Replace Radclient IPs in radius message files with configuration file values")
        dig_cmd = 'sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_PCP_start_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip2)+'/g RFE_9980_part1_radfiles/RFE_9980_PCP_start_client2.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_PCP_stop_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_PCP_update_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_PCP_zvelo_block_start_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_PCP_zvelo_cat1_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_PCP_zvelo_cat2_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_qc_false_update_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_SSP_start_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_unknown_dynamic_start_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_WPCP_start_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_WPCP_stop_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_WPCP_update_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_CAIC_start_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_non_sub_start_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_only_SSP_start_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_only_unknown_start_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_PCP_set_to_all_FF_start_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip2)+'/g RFE_9980_part1_radfiles/RFE_9980_non_sub_start_client2.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_WPCP_start_client2.txt;'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)

    @pytest.mark.run(order=104)
    def test_104_Copy_Subscriber_Record_radfiles_to_radclient(self):
        logging.info("Copy Subscriber Record radius message files to RAD Client")
        dig_cmd = 'sshpass -p infoblox scp -pr RFE_9980_part1_radfiles root@'+str(config.rad_client_ip)+':/root/'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        print "Copied the files to radclient"
        logging.info("Test Case 34 Execution Completed")
        sleep(5)
        
    @pytest.mark.run(order=105)
    def test_105_Add_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_start_client1.txt -r 1 '+str(config.grid_member2_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(25)

    @pytest.mark.run(order=106)
    def test_106_Validate_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000040000000000000000.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=107)
    def test_107_Add_Subscriber_Record_without_Proxy_all_set_and_Different_PCP_Policy_bit_than_above(self):
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_start_client2.txt -r 1 '+str(config.grid_member2_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(25)

    @pytest.mark.run(order=108)
    def test_108_Validate_Subscriber_Record_without_Proxy_all_set_and_Different_PCP_Policy_bit_than_above(self):
        logging.info("Validate Subscriber Record without Proxy-All set different PCP Policy bit than the above")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=01000000000000010000000000000000.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=109)
    def test_109_start_Syslog_Messages_logs_on_2225_Member(self):
        logging.info("Starting Syslog Messages Logs on 2225 Member")
        log("start","/var/log/syslog",config.grid_member2_vip)
        logging.info("test case 128 passed")
        sleep(10)

    @pytest.mark.run(order=110)
    def test_110_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
        logging.info("Validate_DCA_Cache_content_shows_Cache_is_empty")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
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
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=111)
    def test_111_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_2225_Member_Validate_returns_Blocked_IPs_in_response_from_Bind_As_Not_DCA_Cache(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using 2225 Member and get PCP Blocked IPs response from Bind as times.com not in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member2_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=112)
    def test_112_stop_Syslog_Messages_Logs_on_2225_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_member2_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=113)
    def test_113_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_times_com(self):
        logging.info("Validate Named CEF Log for times.com  when get response from Bind")
        LookFor=".*named.*info CEF.*times.com.*CAT=0x00000000000000040000000000000000.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member2_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=114)
    def test_114_Validate_PCP_Domain_times_com_did_not_cached_to_DCA_When_Send_Query_From_PCP_bit_Matched_Subscriber_client(self):
        logging.info("Validate times.com domain not cached to DCA when send query from the PCP bit matched subscriber client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
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
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=115)
    def test_115_Validate_when_get_response_from_Bind_for_PCP_domain_times_com_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased(self):
        logging.info("Validate when get response from Bind for PCP domain times.com Cache hit count not increased and Miss_cache count count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=116)
    def test_116_start_Syslog_Messages_logs_on_2225_Member(self):
        logging.info("Starting Syslog Messages Logs on 2225 Member")
        log("start","/var/log/syslog",config.grid_member2_vip)
        logging.info("test case 135 passed")

    @pytest.mark.run(order=117)
    def test_117_Send_Query_from_NON_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_2225_Member_Validate_returns_NORMAL_response_cached_DCA_with_PCP_word(self):
        logging.info("Perform Query from NON PCP bit match Subscriber client for PCP Domain times.com using 2225 Member and Validate get NORMAL response times.com domain is cached to DCA with PCP word")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_member2_vip)+' times.com +noedns -b '+config.client_ip2+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=118)
    def test_118_stop_Syslog_Messages_Logs_on_2225_Member(self):
        logging.info("Stopping Syslog Logs on 2225 Member")
        log("stop","/var/log/syslog",config.grid_member2_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=119)
    def test_119_Validate_NO_CEF_Log_Logs_when_get_NORMAL_response_for_PCP_domain_times_com_when_send_query_from_NON_PCP_bit_match_client(self):
        logging.info("Validate NO CEF Log for times.com  when get NORMAL response when send query from NON PCP bit match client")
        LookFor="info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member2_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=120)
    def test_120_Validate_PCP_Domain_times_com_get_cached_to_DCA_When_Send_Query_From_NON_PCP_bit_Matched_Subscriber_client(self):
        logging.info("Validate times.com domain get cached to DCA when send query from the NON PCP bit matched subscriber client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel-cache')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*times.com,A,IN.*AA,A,times.com.*',c)
        assert re.search(r'.*0x00000000000000040000000000000000.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=121)
    def test_121_Validate_when_get_response_from_Bind_for_PCP_domain_times_com_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased(self):
        logging.info("Validate when get response from Bind for PCP domain times.com Cache hit count not increased ansd Miss_cache count count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*2.*',c)
        logging.info("Test case execution Completed")

#COmmented the below cases as fp-rte logs are not seen for subscribers in 2225 system , Test case results are inconsistent
    @pytest.mark.run(order=122)
    def test_122_start_Syslog_Messages_logs_on_2225_Member(self):
        logging.info("Starting Syslog Messages Logs on 2225 Member")
        log("start","/var/log/syslog",config.grid_member2_vip)
        logging.info("test case 141 passed")

    @pytest.mark.run(order=123)
    def test_123_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_2225_Member_Validate_returns_Blocked_IPs_in_response_from_DCA_As_times_com_domain_is_already_DCA_Cache(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using 2225 Member and get PCP Blocked IPs response from DCA as times.com is already in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member2_vip)+' times.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test case execution Completed")
        sleep(20)

    @pytest.mark.run(order=124)
    def test_124_stop_Syslog_Messages_Logs_on_2225_Member(self):
        logging.info("Stopping Syslog Logs on 2225 Member")
        log("stop","/var/log/syslog",config.grid_member2_vip)
        logging.info("Test case execution Completed")
    
    @pytest.mark.run(order=125)
    def test_125_Validate_DCA_CEF_Log_Logs_when_get_response_from_DCA_for_PCP_domain_times_com(self):
        logging.info("Validate DCA CEF Log for times.com  when get response from DCA")
        #LookFor="fp-rte.*info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
        LookFor="fp-rte.*info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member2_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=126)
    def test_126_Validate_when_get_response_from_DCA_for_PCP_domain_times_com_Cache_hit_count_is_increased_and_Miss_cache_count_count_not_increased(self):
        logging.info("Validate when get response from DCA for PCP domain times.com Cache hit count is get increased and Miss cache count not increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        print c
        assert re.search(r'.*Cache hit count.*1.*',c)
        assert re.search(r'.*Cache miss count.*2.*',c)
        logging.info("Test case execution Completed")


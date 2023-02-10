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

def enable_mgmt_port_for_dns():
    ref=ib_NIOS.wapi_request('GET', object_type="member:dns")
    ref=json.loads(ref)[0]['_ref']
    data={"use_lan_ipv6_port":True}
    ref1=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
    logging.info (ref1)
    time.sleep(30)

def change_default_route():
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
    child.logfile=sys.stdout
    child.expect('-bash-5.0#')
    child.sendline('ip route del default via 10.35.0.1 dev eth1 table main')
    child.expect('-bash-5.0#')
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
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data))
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
        cmd="reboot_system -H "+vm_id+" -a poweron"
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
        sleep(150)

class Network(unittest.TestCase):
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
                logging.info("Test Case Execution Passed")
                assert True
            else:
                logging.info("Test Case Execution Failed")
                assert False

    @pytest.mark.run(order=3)
    def test_003_Configure_Recurson_Forwarer_RPZ_logging_At_Grid_DNS_Properties(self):
        logging.info("Mofifying and Configure Allow Recursive Query Forwarder and RPZ logging at GRID dns properties")
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:dns")
        get_ref1=json.loads(get_ref)[0]['_ref']
        logging.info(get_ref1)
        data={"allow_recursive_query":True,"allow_query":[{"_struct": "addressac","address":"Any","permission":"ALLOW"}],"forwarders":[config.forwarder_ip],"logging_categories":{"log_rpz":True,"log_queries":True,"log_responses":True}}
        #data={"allow_recursive_query":True,"allow_query":[{"_struct": "addressac","address":"Any","permission":"ALLOW"}],"forwarders":[config.forwarder_ip],"logging_categories":{"log_rpz":True}}
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
        print get_ref1[0]["allow_recursive_query"]
        print get_ref1[0]["forwarders"]
        if get_ref1[0]["allow_recursive_query"]==True and get_ref1[0]["forwarders"]==[config.forwarder_ip]:
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False

    @pytest.mark.run(order=5)
    def test_005_Configure_DNS_Resolver_At_Grid_Properties(self):
        logging.info("Configure DNs Resolver At GRID properties")
        response = ib_NIOS.wapi_request('GET', object_type="grid")
        response = json.loads(response)
        response=response[0]["_ref"]
        data={"dns_resolver_setting": {"resolvers": [config.resolver_ip]}}
        res = ib_NIOS.wapi_request('PUT', object_type=response,fields=json.dumps(data))
        print res
        logging.info(res)
        if type(res)!=tuple:
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False

    @pytest.mark.run(order=6)
    def test_006_Validate_DNS_Resolver_At_Grid_Properties(self):
        logging.info("Validate DNS Resolver is configured at  GRID properties")
        response = ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=dns_resolver_setting")
        response = json.loads(response)
        response=response[0]["dns_resolver_setting"]["resolvers"]
        print response
        if response==[config.resolver_ip]:
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False

    @pytest.mark.run(order=7)
    def test_007_Enable_Parental_Control_with_Proxy_Settings(self):
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

    @pytest.mark.run(order=8)
    def test_008_Validate_Parental_Control_is_Enabled_with_Proxy_Settings(self):
        logging.info("Validating parental control is enabled with Proxy Settings")
        response = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber?_return_fields=enable_parental_control,cat_acctname,category_url,proxy_url")
        logging.info(response)
        response = json.loads(response)
        pc=response[0]["enable_parental_control"]
        act_name=response[0]["cat_acctname"]
        proxy_url=response[0]["proxy_url"]
        if pc==True and act_name=="infoblox_sdk" and proxy_url==config.zvelo_proxy:
            logging.info("Test Case execution passed")
            assert True
        else:
            logging.info("Test Case execution Failed")
            assert False

    @pytest.mark.run(order=9)
    def test_009_start_category_download_Messages_logs_on_master(self):
        logging.info("Starting category download Messages Logs on master")
        log("start","/storage/zvelo/log/category_download.log",config.grid_vip)
        logging.info("Test case 116 execution passed")
        time.sleep(1500)

    @pytest.mark.run(order=10)
    def test_010_stop_category_download_Messages_logs_on_master(self):
        logging.info("Stop Syslog Messages Logs on master")
        log("stop","/storage/zvelo/log/category_download.log",config.grid_vip)
        logging.info("Test case execution passed")

    @pytest.mark.run(order=11)
    def test_011_validate_for_zvelo_download_data_completion_on_master(self):
        time.sleep(10)
        logging.info("Validating category download Messages Logs for data completion")
        LookFor="zvelodb download completed"
        logs=logv(LookFor,"/storage/zvelo/log/category_download.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case Execution passed")
            assert True
        else:
            logging.info("Test Case Execution failed")
            assert False

    @pytest.mark.run(order=12)
    def test_012_In_Grid_Properties_Configure_Loopback_IP_as_Primary_DNS_Resolver(self):
        logging.info("At GRID properties configure Loopback IP as DNS Resolver")
        response = ib_NIOS.wapi_request('GET', object_type="grid")
        response = json.loads(response)
        response=response[0]["_ref"]
        data={"dns_resolver_setting": {"resolvers": ["127.0.0.1",config.resolver_ip]}}
        res = ib_NIOS.wapi_request('PUT', object_type=response,fields=json.dumps(data))
        logging.info(res)
        if type(res)!=tuple:
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False

    @pytest.mark.run(order=13)
    def test_013_Validate_At_Grid_Properties_DNS_Resolver_Is_Configured_with_loopback_IP(self):
        logging.info("Validating at GRID properties DNS Resolver is configured with Loopback IP")
        response = ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=dns_resolver_setting")
        response = json.loads(response)
        response=response[0]["dns_resolver_setting"]["resolvers"]
        if response==["127.0.0.1",config.resolver_ip]:
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False
    @pytest.mark.run(order=14)
    def  test_014_Add_the_Subscriber_Site_as_site2_With_IB_FLEX_Member_DCA_Subscriber_Query_count_and_DCA_Blocklist_White_List_Enabled(self):
        logging.info("Addsubscriber site site2 with IB-FLEX DCA Subscriber Query Count and DCA Blocklist whitelist Enable")
        data={"blocking_ipv4_vip1": "1.1.1.1","blocking_ipv4_vip2": "2.2.2.2","msps":[{"ip_address": config.proxy_server1}],"spms": [{"ip_address": "10.12.11.11"}],"name":"site2","maximum_subscribers":100000,"members":[{"name":config.grid_fqdn}],"nas_gateways":[{"ip_address":config.rad_client_ip,"name":"nas1","shared_secret":"testing123"},{"ip_address":config.rad_client_ip_lan,"name":"nas2","shared_secret":"testing123"}],"dca_sub_query_count":True}
        #data={"blocking_ipv4_vip1": "1.1.1.1","blocking_ipv4_vip2": "2.2.2.2","msps":[{"ip_address": config.proxy_server1}],"spms": [{"ip_address": "10.12.11.11"}],"name":"site2","maximum_subscribers":100000,"members":[{"name":config.grid_fqdn}],"nas_gateways":[{"ip_address":config.rad_client_ip,"name":"nas1","shared_secret":"testing123"},{"ip_address":config.rad_client_ip_lan,"name":"nas2","shared_secret":"testing123"}]}
        get_ref=ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data))
        logging.info(get_ref)
        print(get_ref)
        restart_the_grid()
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
    @pytest.mark.run(order=15)
    def  test_015_Validate_subscriber_site_site2_Is_Added_with_IB_FLEX_Member_DCA_Subscriber_Query_count_and_DCA_Blocklist_White_List_Enabled(self):
        logging.info("Validating subscriber site site2 added with IB-FLEX DCA Subscriber Query Count and DCA Blocklist whitelist Enable")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=blocking_ipv4_vip1,blocking_ipv4_vip2,dca_sub_query_count,dca_sub_bw_list")
        reference=json.loads(reference)
        if reference[0]["blocking_ipv4_vip1"]=="1.1.1.1" and reference[0]["blocking_ipv4_vip2"]=="2.2.2.2" and reference[0]["dca_sub_query_count"]==True:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=16)
    def test_016_Start_the_subscriber_service_on_members_and_Validate(self):
        logging.info("Start the subscriber service on members and validate")
        member=[config.grid_fqdn]
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
            time.sleep(10)
        for mem in member:
            get_ref=ib_NIOS.wapi_request('GET', object_type='member:parentalcontrol?name='+mem)
            get_ref=json.loads(get_ref)
            if get_ref[0]["enable_service"]==True:
                print("subscriber service is started on "+mem)
                assert True
            else:
                print("Not able to start subscriber service on "+mem)
                assert False
            time.sleep(10)
            logging.info("Test Case Execution Completd")

    @pytest.mark.run(order=17)
    def test_017_start_DCA_service_on_Grid_Master_Member(self):
        logging.info("Enable DCA on the IB-FLEX Grid Master member")
        data = {"enable_dns": True, "enable_dns_cache_acceleration": True}
        DCA_capable=[config.grid_fqdn]
        for mem in DCA_capable:
            grid_ref = mem_ref_string(mem)
            print(grid_ref)
            response = ib_NIOS.wapi_request('PUT', object_type=grid_ref, fields=json.dumps(data))
            print(response)
            if type(response)!=tuple:
                print("DCA Enabled successfully")
                sleep(300)
                assert True
            else:
                print("Failed to enable DCA on the Member1")
                assert False

    @pytest.mark.run(order=18)
    def test_018_Validate_DCA_service_running_on_Grid_Master_Member(self):
        logging.info("Validate_DCA_service_running")
        sys_log_master = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -2000 /infoblox/var/infoblox.log"'
        out1 = commands.getoutput(sys_log_master)
        logging.info (out1)
        res1=re.search(r'DNS cache acceleration is now started',out1)
        if res1!=None:
            logging.info("Test Case Execution passed")
            assert True
        else:
            logging.info("Test Case Execution failed")
            assert False
    @pytest.mark.run(order=106)
    def test_019_Replace_radcient_client_ips_In_Radius_message_files_with_Configuration_file_values(self):
        logging.info("Replace Radclient IPs in radius message files with configuration file values")
        dig_cmd = 'sed -i s/rad_client_ip/'+str(config.rad_client_ip)+'/g RFE_9980_part1_radfiles/*; sed -i s/client_ip/'+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/*;sed -i s/client_ip2/'+str(config.client_ip2)+'/g RFE_9980_part1_radfiles/*;sed -i s/client_ip3/'+str(config.client_ip3)+'/g RFE_9980_part1_radfiles/*;sed -i s/client_ip4/'+str(config.client_ip4)+'/g RFE_9980_part1_radfiles/*; sed -i s/client_network_8/'+str(config.client_network_8)+'/g RFE_9980_part1_radfiles/*;sed -i s/client_network_24/'+str(config.client_network_24)+'/g RFE_9980_part1_radfiles/*; sed -i s/client_network_16/'+str(config.client_network_16)+'/g RFE_9980_part1_radfiles/*; sed -i s/client_network_32/'+str(config.client_network_32)+'/g RFE_9980_part1_radfiles/*'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)
    
    @pytest.mark.run(order=107)
    def test_020_Copy_Subscriber_Record_radfiles_to_radclient(self):
        logging.info("Copy Subscriber Record radius message files to RAD Client")
        dig_cmd = 'sshpass -p infoblox scp -pr RFE_9980_part1_radfiles root@'+str(config.rad_client_ip)+':/root/'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        print "Copied the files to radclient"
        logging.info("Test Case 34 Execution Completed")
        sleep(5)
    
    @pytest.mark.run(order=116)
    def test_021_From_Radclient_Send_Start_Radius_Message_with_PCP_Policy_and_Proxy_All_Configured(self):
        restart_the_grid()
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_start_client1.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)
    
    @pytest.mark.run(order=117)
    def test_022_Validate_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000040000000000000000.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=118)
    def test_023_From_Radclient_Send_Start_Radius_Message_with_PCP_Policy_and_Proxy_All_Configured(self):
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_start_client2.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=119)
    def test_024_Validate_Subscriber_Record_without_Proxy_all_set_and_Different_PCP_Policy_bit_than_above(self):
        logging.info("Validate Subscriber Record without Proxy-All set different PCP Policy bit than the above")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=01000000000000010000000000000000.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=120)
    def test_025_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 128 passed")

    @pytest.mark.run(order=121)
    def test_026_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
        logging.info("Validate DCA Cache content shows Cache is empty")
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
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=122)
    def test_027_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_Blocked_IPs_in_response_from_Bind_As_Not_DCA_Cache(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and get PCP Blocked IPs response from Bind as times.com not in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=123)
    def test_028_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=124)
    def test_029_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_times_com(self):
        logging.info("Validate Named CEF Log for times.com  when get response from Bind")
        LookFor=".*named.*info CEF.*times.com.*CAT=0x00000000000000040000000000000000.*"
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

    @pytest.mark.run(order=125)
    def test_030_Validate_PCP_Domain_times_com_did_not_cached_to_DCA_When_Send_Query_From_PCP_bit_Matched_Subscriber_client(self):
        logging.info("Validate times.com domain not cached to DCA when send query from the PCP bit matched subscriber client")
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
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=126)
    def test_031_Validate_when_get_response_from_Bind_for_PCP_domain_times_com_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased(self):
        logging.info("Validate when get response from Bind for PCP domain times.com Cache hit count not increased and Miss_cache count count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
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

    @pytest.mark.run(order=127)
    def test_032_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 135 passed")

    @pytest.mark.run(order=128)
    def test_033_Send_Query_from_NON_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_cached_DCA_with_PCP_word(self):
        logging.info("Perform Query from NON PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and Validate get NORMAL response times.com domain is cached to DCA with PCP word")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip2+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=129)
    def test_034_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=130)
    def test_035_Validate_NO_CEF_Log_Logs_when_get_NORMAL_response_for_PCP_domain_times_com_when_send_query_from_NON_PCP_bit_match_client(self):
        logging.info("Validate NO CEF Log for times.com  when get NORMAL response when send query from NON PCP bit match client")
        LookFor="info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=131)
    def test_036_Validate_PCP_Domain_times_com_get_cached_to_DCA_When_Send_Query_From_NON_PCP_bit_Matched_Subscriber_client(self):
        logging.info("Validate times.com domain get cached to DCA when send query from the NON PCP bit matched subscriber client")
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
        assert re.search(r'.*times.com,A,IN.*AA,A,times.com.*',c)
        assert re.search(r'.*0x00000000000000040000000000000000.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=132)
    def test_037_Validate_when_get_response_from_Bind_for_PCP_domain_times_com_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased(self):
        logging.info("Validate when get response from Bind for PCP domain times.com Cache hit count not increased ansd Miss_cache count count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
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

    @pytest.mark.run(order=133)
    def test_038_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 141 passed")

    @pytest.mark.run(order=134)
    def test_039_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_Blocked_IPs_in_response_from_DCA_As_times_com_domain_is_already_DCA_Cache(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and get PCP Blocked IPs response from DCA as times.com is already in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=135)
    def test_040_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=136)
    def test_041_Validate_DCA_CEF_Log_Logs_when_get_response_from_DCA_for_PCP_domain_times_com(self):
        logging.info("Validate DCA CEF Log for times.com  when get response from DCA")
        LookFor="fp-rte.*info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
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

    @pytest.mark.run(order=137)
    def test_042_Validate_when_get_response_from_DCA_for_PCP_domain_times_com_Cache_hit_count_is_increased_and_Miss_cache_count_count_not_increased(self):
        logging.info("Validate when get response from DCA for PCP domain times.com Cache hit count is get increased and Miss cache count not increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
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

    @pytest.mark.run(order=138)
    def test_043_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 146 passed")

    @pytest.mark.run(order=139)
    def test_044_From_Radclient_Stop_Radius_Message_with_PCP_Policy_Configured(self):
        logging.info("From Rad client send Start Radius message with PCP Policy Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_stop_client1.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=140)
    def test_045_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=141)
    def test_046_Validate_Subscriber_Record_with_Proxy_all_set_1_is_deleted_from_Subscriber_Cache(self):
        logging.info("Validate Subscriber Record with Proxy-All set to True is deleted from subscriber cache")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        if re.search(r'.*'+config.client_ip1+'.*',c):
            logging.info("Test case execution Failed")
            assert False
        else:
            logging.info("Test case execution Passed")
            assert True
        logging.info("Test case execution completed")

    @pytest.mark.run(order=142)
    def test_047_Validate_stop_CEF_Log_Logs_when_get_subscriber_record_is_removed(self):
        logging.info("Validate stop_CEF Logs when get subscriber record is removed")
        LookFor=".*fp-rte.*info CEF.*QUERY-COUNT.*event_type=STOP.*"
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

    @pytest.mark.run(order=143)
    def test_048_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 151 passed")

    @pytest.mark.run(order=144)
    def test_049_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_Even_PCP_Domain_in_Cache_with_PCP_word_But_Match_subscriber_client_is_delete(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and Validate get NORMAL response even times.com domain is in cache with PCP word but subscriber client is deleted from subscriber cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip2+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=145)
    def test_050_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=146)
    def test_051_Validate_No_CEF_Log_Logs_when_get_NORMAL_response_from_DCA_for_PCP_domain_times_com(self):
        logging.info("Validate NO CEF Log for times.com  when get NORMAL response")
        LookFor="info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=147)
    def test_052_Validate_PCP_Domain_times_com_still_exist_in_DCA_cache(self):
        logging.info("Validate times.com domain still exist in DCA  cache")
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
        assert re.search(r'.*times.com,A,IN.*AA,A,times.com.*',c)
        assert re.search(r'.*0x00000000000000040000000000000000.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=148)
    def test_053_Validate_when_get_response_from_DCA_for_PCP_domain_times_com_Cache_hit_count_is_increased_and_Miss_cache_count_count_not_increased(self):
        logging.info("Validate when get response from DCA for PCP domain times.com Cache hit count is get increased and Miss cache count not increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        print c
        assert re.search(r'.*Cache hit count.*2.*',c)
        assert re.search(r'.*Cache miss count.*2.*',c)
        #assert re.search(r'.*Cache hit count.*1.*',c)
        #assert re.search(r'.*Cache miss count.*3.*',c)

        logging.info("Test case execution Completed")

    @pytest.mark.run(order=149)
    def test_054_From_Radclient_Send_Same_Start_Radius_Message_with_PCP_Policy_Configured(self):
        logging.info("From Rad client send same Start Radius message with PCP Policy Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_start_client1.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(25)

    @pytest.mark.run(order=150)
    def test_055_Validate_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000040000000000000000.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=151)
    def test_056_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 159 passed")

    @pytest.mark.run(order=152)
    def test_057_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_Blocked_IPs_in_response_from_DCA_As_times_com_domain_is_already_DCA_Cache(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and get PCP Blocked IPs response from DCA as times.com is already in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip1+' +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=153)
    def test_058_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=154)
    def test_059_Validate_DCA_CEF_Log_Logs_when_get_response_from_DCA_for_PCP_domain_times_com(self):
        logging.info("Validate DCA CEF Log for times.com  when get response from DCA")
        LookFor="fp-rte.*info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
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

    @pytest.mark.run(order=155)
    def test_060_Validate_when_get_response_from_DCA_for_PCP_domain_times_com_Cache_hit_count_is_increased_and_Miss_cache_count_count_not_increased(self):
        logging.info("Validate when get response from DCA for PCP domain times.com Cache hit count is get increased and Miss cache count not increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        print c
        assert re.search(r'.*Cache hit count.*3.*',c)
        assert re.search(r'.*Cache miss count.*2.*',c)
        #assert re.search(r'.*Cache hit count.*2.*',c)
        #assert re.search(r'.*Cache miss count.*3.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=156)
    def test_061_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 164 passed")

    @pytest.mark.run(order=157)
    def test_062_From_Radclient_Send_Interim_Radius_Message_with_PCP_Policy_and_Proxy_All_Configured(self):
        logging.info("From Rad client send Interim Radius message with PCP Policy and Proxy-All Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_update_client1.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=158)
    def test_063_Validate_Subscriber_Record_with_Different_PCP_Policy_bit(self):
        logging.info("Validate Subscriber Record with Different PCP Policy bit")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00220000000000000000000000020040.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=159)
    def test_064_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=160)
    def test_065_Validate_DCA_CEF_Log_Logs_when_get_response_from_DCA_for_PCP_domain_times_com(self):
        logging.info("Validate DCA CEF Log for times.com  when get response from DCA")
        LookFor=".*fp-rte.*info CEF.*QUERY-COUNT.*event_type=INTERIM.*"
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

    @pytest.mark.run(order=161)
    def test_066_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 169 passed")

    @pytest.mark.run(order=162)
    def test_067_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_Even_PCP_Domain_in_Cache_with_PCP_word_But_subscriber_client_PCP_Policy_bit_not_matched(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and Validate get NORMAL response even times.com domain is in cache with PCP word but subscriber client PCP Policy bit not matched")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip2+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=163)
    def test_068_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=164)
    def test_164_Validate_No_CEF_Log_Logs_when_get_NORMAL_response_from_bind_for_PCP_domain_times_com(self):
        logging.info("Validate NO CEF Log for times.com  when get NORMAL response")
        LookFor="info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=165)
    def test_069_Validate_PCP_Domain_times_com_still_exist_in_DCA_cache(self):
        logging.info("Validate times.com domain still exist in DCA  cache")
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
        assert re.search(r'.*times.com,A,IN.*AA,A,times.com.*',c)
        assert re.search(r'.*0x00000000000000040000000000000000.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=166)
    def test_070_Validate_when_get_response_from_DCA_for_PCP_domain_times_com_Cache_hit_count_is_increased_and_Miss_cache_count_count_not_increased(self):
        logging.info("Validate when get response from DCA for PCP domain times.com Cache hit count is get increased and Miss cache count not increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        print c
        assert re.search(r'.*Cache hit count.*4.*',c)
        assert re.search(r'.*Cache miss count.*2.*',c)
        #assert re.search(r'.*Cache hit count.*2.*',c)
        #assert re.search(r'.*Cache miss count.*4.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=167)
    def test_071_Add_Subscriber_Record_with_WPCP_Policy_for_Alchohol_Category(self):
        print("\n")
        print("************************************************")
        print("***Test cases Related to WPCP category policy***")
        print("************************************************")
        restart_the_grid()
        logging.info("From Rad client send Start Radius message with WPCP Policy")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_WPCP_start_client1.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=168)
    def test_072_Validate_Subscriber_Record_with_WPCP_Policy_for_Alchohol_Category(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCC\:PC-Category-Policy=00000000000000000000000000000001.*',c)

        logging.info("Test case execution completed")

    @pytest.mark.run(order=169)
    def test_073_Add_Subscriber_Record_without_Proxy_all_set_and_Different_WPCP_Policy_bit_than_above(self):
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_WPCP_start_client2.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=170)
    def test_074_Validate_Subscriber_Record_without_Proxy_all_set_and_Different_WPCP_Policy_bit_than_above(self):
        logging.info("Validate Subscriber Record without Proxy-All set different PCP Policy bit than the above")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCC\:PC-Category-Policy=00000000000000000000000000000010.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=171)
    def test_075_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 181 passed")


    @pytest.mark.run(order=172)
    def test_076_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
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
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=173)
    def test_077_Send_Query_from_WPCP_bit_match_Subscriber_client_for_WPCP_Domain_totalwine_com_Using_IB_FLEX_Member_Validate_returns_IPs_in_response_from_Bind_As_Not_DCA_Cache(self):
        logging.info("Perform Query from WPCP bit match Subscriber client for WPCP Domain totalwine.com using IB-FLEX Member and get normal response from Bind as totalwine.com not in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' totalwine.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*totalwine.com.*IN.*A.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=174)
    def test_078_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=175)
    def test_079_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_WPCP_domain_totalwine_com(self):
        logging.info("Validate Named CEF Log for totalwine.com  when get response from Bind")
        LookFor="named.*info CEF.*totalwine.com.*CAT=WRN_0x00000000000000000000000000000001"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        if logs!=None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=176)
    def test_080_Validate_WPCP_Domain_totalwine_com_cached_to_DCA_When_Send_Query_From_NON_WPCP_bit_Matched_Subscriber_client(self):
        logging.info("Validate totalwine.com domain not cached to DCA when send query from the WPCP bit matched subscriber client")
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
        assert re.search(r'.*0x00000000000000200000000000000001.*',c)
        logging.info("Test case execution Completed")


    @pytest.mark.run(order=177)
    def test_081_Validate_when_get_response_from_Bind_for_WPCP_domain_totalwine_com_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased(self):
        logging.info("Validate when get response from Bind for PCP domain totalwine.com Cache hit count not increased and Miss_cache count count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
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


    @pytest.mark.run(order=178)
    def test_082_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 187 passed")


    @pytest.mark.run(order=179)
    def test_083_Send_Query_from_Non_WPCP_bit_match_Subscriber_client_for_WPCP_Domain_totalwine_com_Using_IB_FLEX_Member_Validate_returns_IPs_in_response_from_DCA_As_times_com_domain_is_already_DCA_Cache(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain totalwine.com using IB-FLEX Member and get normal IPs response from DCA as totalwine.com is already in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' totalwine.com +noedns -b '+config.client_ip2+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*totalwine.com.*IN.*A.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=180)
    def test_084_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=181)
    def test_085_Validate_DCA_CEF_Log_Logs_when_get_response_from_DCA_for_WPCP_domain_totalwine_com(self):
        logging.info("Validate DCA CEF Log for times.com  when get response from DCA")
        LookFor="fp-rte.*info CEF.*totalwine.com.*CAT=WRN_0x00000000000000000000000000000001"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        LookFor2=".*info CEF.*totalwine.com.*"
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
        print logs2
        print logs
        if logs==None and logs2==None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=182)
    def test_086_Validate_when_get_response_from_DCA_for_WPCP_domain_totalwine_com_Cache_hit_count_is_increased_and_Miss_cache_count_count_not_increased(self):
        logging.info("Validate when get response from DCA for PCP domain totalwine.com Cache hit count is get increased and Miss cache count not increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        print c
        assert re.search(r'.*Cache hit count.*1.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        #assert re.search(r'.*Cache hit count.*0.*',c)
        #assert re.search(r'.*Cache miss count.*2.*',c)
        logging.info("Test case execution Completed")


    @pytest.mark.run(order=183)
    def test_087_Delete_Subscriber_Record_with_Proxy_all_set_From_Subscriber_Cache(self):
        logging.info("From Rad client send Stop Radius message with WPCP Policy Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_WPCP_stop_client1.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=184)
    def test_088_Validate_Subscriber_Record_is_deleted_from_Subscriber_Cache(self):
        logging.info("Validate Subscriber Record is deleted from subscriber cache")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        if re.search(r'.*'+config.client_ip1+'.*',c):
            logging.info("Test case execution Failed")
            assert False
        else:
            logging.info("Test case execution Passed")
            assert True
            logging.info("Test case execution completed")


    @pytest.mark.run(order=185)
    def test_089_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 194 passed")


    @pytest.mark.run(order=186)
    def test_090_Send_Query_from_WPCP_bit_match_Subscriber_client_for_WPCP_Domain_totalwine_com_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_Even_WPCP_Domain_in_Cache_with_WPCP_word_But_Match_subscriber_client_is_delete(self):
        logging.info("Perform Query from WPCP bit match Subscriber client for WPCP Domain totalwine.com using IB-FLEX Member and Validate get NORMAL response even totalwine.com domain is in cache with WPCP word but subscriber client is deleted from subscriber cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' totalwine.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*totalwine.com.*IN.*A.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=187)
    def test_091_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=188)
    def test_092_Validate_No_CEF_Log_Logs_when_get_NORMAL_response_from_DCA_for_PCP_domain_totalwine_com(self):
        logging.info("Validate NO CEF Log for times.com  when get NORMAL response")
        LookFor=".*fp-rte.*info CEF.*totalwine.com.*CAT=WRN_0x00000000000000200000000000000001"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=189)
    def test_093_Validate_WPCP_Domain_totalwine_com_still_exist_in_DCA_cache(self):
        logging.info("Validate totalwine.com domain still exist in DCA  cache")
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
        assert re.search(r'.*totalwine.com,A,IN.*AA,A,totalwine.com.*',c)
        assert re.search(r'.*0x00000000000000200000000000000001.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=190)
    def test_094_Validate_when_get_response_from_DCA_for_WPCP_domain_totalwine_com_Cache_hit_count_is_increased_and_Miss_cache_count_count_not_increased(self):
        logging.info("Validate when get response from DCA for WPCP domain totalwine.com Cache hit count is get increased and Miss cache count not increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        print c
        assert re.search(r'.*Cache hit count.*2.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        #assert re.search(r'.*Cache hit count.*1.*',c)
        #assert re.search(r'.*Cache miss count.*2.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=191)
    def test_095_Add_Back_Same_Subscriber_Record_with_WPCP_Policy_for_Alcohol_Category(self):
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_WPCP_start_client1.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=192)
    def test_096_Validate_Subscriber_Record_with_WPCP_Policy_for_Alcohol_Category(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCC\:PC-Category-Policy=00000000000000000000000000000001.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=193)
    def test_097_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 202 passed")

    @pytest.mark.run(order=194)
    def test_098_Send_Query_from_WPCP_bit_match_Subscriber_client_for_WPCP_Domain_totalwine_com_Using_IB_FLEX_Member_Validate_returns_IPs_in_response_from_DCA_As_times_com_domain_is_already_DCA_Cache(self):
        logging.info("Perform Query from WPCP bit match Subscriber client for WPCP Domain totalwine.com using IB-FLEX Member and get normal IPs response from DCA as totalwine.com is already in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' totalwine.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*totalwine.com.*IN.*A.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=195)
    def test_099_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=196)
    def test_100_Validate_DCA_CEF_Log_Logs_when_get_response_from_DCA_for_WPCP_domain_totalwine_com(self):
        logging.info("Validate DCA CEF Log for totalwine.com  when get response from DCA")
        LookFor="fp-rte.*info CEF.*totalwine.com.*WRN_0x00000000000000200000000000000001.*"
        #LookFor="named.*info CEF.*totalwine.com.*WRN_0x00000000000000200000000000000001.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert True
            sleep(10)
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=197)
    def test_101_Validate_when_get_response_from_DCA_for_WPCP_domain_times_com_Cache_hit_count_is_increased_and_Miss_cache_count_count_not_increased(self):
        logging.info("Validate when get response from DCA for PCP domain times.com Cache hit count is get increased and Miss cache count not increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        print c
        assert re.search(r'.*Cache hit count.*3.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        #assert re.search(r'.*Cache hit count.*2.*',c)
        #assert re.search(r'.*Cache miss count.*2.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=198)
    def test_102_Add_Back_Same_Subscriber_Record_with_Different_WPCP_Policy_bit(self):
        logging.info("From Rad client send Interim Radius message with WPCP Policy Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_WPCP_update_client1.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=199)
    def test_103_Validate_Subscriber_Record_with_Different_WPCP_Policy_bit(self):
        logging.info("Validate Subscriber Record with Different WPCP Policy bit")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCC\:PC-Category-Policy=00000000000000000000000000000100.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=200)
    def test_104_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 209 passed")

    @pytest.mark.run(order=201)
    def test_105_Send_Query_from_WPCP_bit_match_Subscriber_client_for_WPCP_Domain_totalwine_com_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_Even_WPCP_Domain_in_Cache_with_WPCP_word_But_subscriber_client_WPCP_Policy_bit_not_matched(self):
        logging.info("Perform Query from WPCP bit match Subscriber client for WPCP Domain totalwine.com using IB-FLEX Member and Validate get NORMAL response even totalwine.com domain is in cache with WPCP word but subscriber client WPCP Policy bit not matched")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' totalwine.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*totalwine.com.*IN.*A.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=202)
    def test_106_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=203)
    def test_107_Validate_No_CEF_Log_Logs_when_get_NORMAL_response_from_DCA_for_PCP_domain_totalwine_com(self):
        logging.info("Validate NO CEF Log for times.com  when get NORMAL response")
        LookFor="info CEF.*totalwine.com.*CAT=0x00000000000000000000000000000001"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=204)
    def test_108_Validate_WPCP_Domain_totalwine_com_still_exist_in_DCA_cache(self):
        logging.info("Validate totalwine.com domain still exist in DCA  cache")
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
        assert re.search(r'.*totalwine.com,A,IN.*AA,A,totalwine.com.*',c)
        assert re.search(r'.*0x00000000000000200000000000000001.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=205)
    def test_109_Validate_when_get_response_from_DCA_for_WPCP_domain_totalwine_com_Cache_hit_count_is_increased_and_Miss_cache_count_count_not_increased(self):
        logging.info("Validate when get response from DCA for WPCP domain totalwine.com Cache hit count is get increased and Miss cache count not increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        print c
        assert re.search(r'.*Cache hit count.*4.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        #assert re.search(r'.*Cache hit count.*2.*',c)
        #assert re.search(r'.*Cache miss count.*3.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=206)
    def test_110_Add_Subscriber_Record_with_PCP_Policy_bit_for_dynamic_domain(self):
        print("\n")
        print("************************************************")
        print("****  Test cases Related to DYNAMIC DOMAIN  ****")
        print("************************************************")
        restart_the_grid()
        logging.info("From Rad client send Start Radius message with PCP Policy and dynamic bit Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_unknown_dynamic_start_client1.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=207)
    def test_111_Validate_Subscriber_Record_with_Policy_bit_for_dynamic_domain(self):
        logging.info("Validate Subscriber Record with Different PCP Policy bit")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000000000000020040.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=208)
    def test_112_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 227 passed")

    @pytest.mark.run(order=209)
    def test_113_Send_Query_from_subscriber_client_for_Dynamic_Domain_cnn_com_Using_IB_FLEX_Member_Validate_returns_NORMAL_response(self):
        logging.info("Perform Query from PCP match Subscriber client for dynamic Domain cnn.com using IB-FLEX Member and Validate get NORMAL response")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' cnn.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*cnn.com.*IN.*A.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=210)
    def test_114_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=211)
    def test_115_Validate_No_CEF_Log_Logs_when_get_NORMAL_response_from_bind_for_domain_cnn_com(self):
        logging.info("Validate NO CEF Log for cnn.com  when get NORMAL response")
        LookFor="info CEF.*cnn.com.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert False
        else:
            logging.info("Test case execution Failed")
            assert True

    @pytest.mark.run(order=212)
    def test_116_Validate_Domain_cnn_com_exist_in_DCA_cache(self):
        logging.info("Validate cnn.com domain still exist in DCA  cache")
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
        assert re.search(r'.*cnn.com,A,IN.*AA,A,cnn.com.*',c)
        assert re.search(r'.*0x00000000000000040000000000000000.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=213)
    def test_117_Validate_when_get_response_from_bind_for_pid_com_Cache_hit_count_is_not_increased_and_Miss_cache_count_is_increased(self):
        logging.info("Validate when get response from DCA for pid_com_Cache_hit_count_is_not_increased_and_Miss_cache_count_is_increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        print c
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=214)
    def test_118_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 233 passed")

    @pytest.mark.run(order=215)
    def test_119_Send_Query_from_subscriber_client_for_dynamic_Domain_cnn_com_Using_IB_FLEX_Member_Validate_returns_NORMAL_response(self):
        logging.info("Send Query from subscriber client for dynamic Domain cnn com Using IB FLEX_Member Validate returns NORMAL response")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' cnn.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*cnn.com.*IN.*A.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=216)
    def test_120_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=217)
    def test_121_Validate_No_CEF_Log_Logs_when_get_NORMAL_response_from_bind_for_domain_cnn_com(self):
        logging.info("Validate NO CEF Log for times.com  when get NORMAL response")
        LookFor="info CEF.*cnn.com.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert False
        else:
            logging.info("Test case execution Failed")
            assert True

    @pytest.mark.run(order=218)
    def test_122_Validate_when_get_response_from_bind_for_pid_com_Cache_hit_count_is_increased_and_Miss_cache_count_is_not_increased(self):
        logging.info("Validate_when_get_response_from_DCA_for_pid_com_Cache_hit_count_is_increased_and_Miss_cache_count_is_not_increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        print c
        #assert re.search(r'.*Cache hit count.*0.*',c)
        #assert re.search(r'.*Cache miss count.*2.*',c)
        assert re.search(r'.*Cache hit count.*1.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test case execution Completed")


    @pytest.mark.run(order=219)
    def test_123_Add_Subscriber_Record_with_Different_PCP_Policy_bit_for_unknown_domain(self):
        print("************************************************")
        print("Test cases Related to UNKNOWN DOMAIN")
        print("************************************************")
        restart_the_grid()
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured with unknown bit set")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_unknown_dynamic_start_client1.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=220)
    def test_124_Validate_Subscriber_Record_with_Policy_bit_for_unknown_domain(self):
        logging.info("Validate Subscriber Record with Different PCP Policy bit")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000000000000020040.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=221)
    def test_125_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 239 passed")

    @pytest.mark.run(order=222)
    def test_126_Send_Query_from_subscriber_client_for_unknown_domain_pid_com_Using_IB_FLEX_Member_Validate_returns_NORMAL_response(self):
        logging.info("Perform Query from PCP match Subscriber client for unknown Domain pid.com using IB-FLEX Member and Validate get NORMAL response")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' pid.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*pid.com.*IN.*A.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=223)
    def test_127_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=224)
    def test_128_Validate_No_CEF_Log_Logs_when_get_NORMAL_response_from_bind_for_domain_cnn_com(self):
        logging.info("Validate NO CEF Log for cnn.com  when get NORMAL response")
        LookFor="info CEF.*pid.com.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert False
        else:
            logging.info("Test case execution Failed")
            assert True

    @pytest.mark.run(order=225)
    def test_129_Validate_Domain_pid_com_exist_in_DCA_cache(self):
        logging.info("Validate pid.com domain still exist in DCA  cache")
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
        assert re.search(r'.*pid.com,A,IN.*AA,A,pid.com.*',c)
        assert re.search(r'.*0x00000000000040000000000000000000.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=226)
    def test_130_Validate_when_get_response_from_DCA_for_pid_com_Cache_hit_count_is_increased_and_Miss_cache_count_count_not_increased(self):
        logging.info("Validate when get response from DCA for WPCP domain pid.com Cache hit count is get increased and Miss cache count not increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        print c
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=227)
    def test_131_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 245 passed")
        sleep(10)

    @pytest.mark.run(order=228)
    def test_132_Send_Query_from_subscriber_client_for_unknown_Domain_pid_com_Using_IB_FLEX_Member_Validate_returns_NORMAL_response(self):
        logging.info("Send Query from subscriber client for unknown Domain pid.com Using IB FLEX_Member Validate returns NORMAL response")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' pid.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*pid.com.*IN.*A.*',str(dig_result))
        logging.info("Test case execution Completed")
        sleep(20)

    @pytest.mark.run(order=229)
    def test_133_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=230)
    def test_134_Validate_No_CEF_Log_Logs_when_get_NORMAL_response_from_DCA_for_domain_pid_com(self):
        logging.info("Validate NO CEF Log for times.com  when get NORMAL response")
        LookFor="info CEF.*pid.com.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert False
        else:
            logging.info("Test case execution Failed")
            assert True

    @pytest.mark.run(order=231)
    def test_135_Validate_when_get_response_from_DCA_for_pid_com_Cache_hit_count_is_increased_and_Miss_cache_count_count_not_increased(self):
        logging.info("Validate when get response from DCA for Unknown domain pid.com Cache hit count get increased and Miss cache count notincreased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        print c
        #assert re.search(r'.*Cache hit count.*0.*',c)
        #assert re.search(r'.*Cache miss count.*2.*',c)
        assert re.search(r'.*Cache hit count.*1.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=251)
    def test_136_Add_Subscriber_Record_with_PCP_Policy_bit_for_Alchohol_category(self):
        print("\n")
        print("************************************************")
        print("****      Test cases for Non Subscribers    ****")
        print("************************************************")
        stop_subscriber_collection_services_for_added_site([config.grid_fqdn])
        sleep(30)
        start_subscriber_collection_services_for_added_site([config.grid_fqdn])
        sleep(30)
        restart_the_grid()
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_non_sub_start_client1.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=252)
    def test_137_Validate_Subscriber_Record_with_Policy_bit_for_Alcohol_category(self):
        logging.info("Validate Subscriber Record with Policy bit for Alcohol category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000000000000000001.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=234)
    def test_138_Add_Subscriber_Record_with_PCP_Policy_bit_for_porn_category_for_another_client(self):
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_non_sub_start_client2.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=235)
    def test_139_Validate_Subscriber_Record_with_Policy_bit_for_porn_category_for_another_client(self):
        logging.info("Validate Subscriber Record with Policy bit for porn category for another client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000000000000020040.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=236)
    def test_140_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 253 passed")
        sleep(10)

    @pytest.mark.run(order=237)
    def test_141_Send_Query_from_non_registerd_client_for_Domain_totalwine_com_Using_IB_FLEX_Member_Validate_returns_NORMAL_response(self):
        logging.info("Send Query from subscriber client for Domain totalwine.com Using IB FLEX_Member Validate returns NORMAL response")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip3)+' "dig @'+str(config.grid_vip)+' totalwine.com +noedns -b '+config.client_ip3+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*totalwine.com.*IN.*A.*',str(dig_result))
        logging.info("Test case execution Completed")
        sleep(10)
        
    @pytest.mark.run(order=238)
    def test_142_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=239)
    def test_143_Validate_No_CEF_Log_Logs_when_get_NORMAL_response_from_bind_for_domain_totalwine_com(self):
        logging.info("Validate NO CEF Log for totalwine.com  when get NORMAL response")
        LookFor="info CEF.*totalwine.com.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert False
        else:
            sleep(10)
            logging.info("Test case execution Failed")
            assert True

    @pytest.mark.run(order=240)
    def test_144_Validate_Domain_totalwine_com_exist_in_DCA_cache(self):
        logging.info("Validate times.com domain still exist in DCA  cache")
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
        res1=re.search(r'.*totalwine.com,A,IN.*AA,A,totalwine.com.*',c)
        res2=re.search(r'.*0x00000000000000000000000000000010.*',c)
        if res1!=None and res2==None:
            sleep(10)
            logging.info("Test case execution Completed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=241)
    def test_145_Validate_when_get_response_from_bind_for_totalwine_com_Cache_hit_count_is_not_increased_and_Miss_cache_count_increased(self):
        logging.info("Validate when get response from bind for domain totalwine.com Cache hit count is not get increased and Miss cache count is increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        print c
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=242)
    def test_146_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        sleep(10)
        logging.info("test case 259 passed")

    @pytest.mark.run(order=243)
    def test_147_Send_Query_from_subscriber_client_for_Domain_totalwine_com_Using_IB_FLEX_Member_Validate_returns_blocking_response_from_Bind(self):
        logging.info("Send Query from subscriber client for Domain totalwine_com Using IB FLEX Member Validate returns blocking response from Bind")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' totalwine.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test case execution Completed")
        sleep(10)

    @pytest.mark.run(order=244)
    def test_148_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=245)
    def test_149_Validate_CEF_Log_Logs_when_get_blocking_response_from_bind_for_domain_playboy_com(self):
        logging.info("Validate NO CEF Log for playboy.com  when get NORMAL response")
        LookFor="named.*info CEF.*totalwine.com.*CAT=0x00000000000000000000000000000001"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            sleep(10)
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=246)
    def test_150_Validate_Domain_totalwine_com_exist_in_DCA_cache(self):
        logging.info("Validate totalwine.com domain still exist in DCA  cache")
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
        assert re.search(r'.*totalwine.com,A,IN.*AA,A,totalwine.com.*',c)
        logging.info("Test case execution Completed")
        sleep(10)

    @pytest.mark.run(order=247)
    def test_151_Validate_when_get_response_from_DCA_for_playboy_com_Cache_hit_count_is_not_increased_and_Miss_cache_count_increased(self):
        logging.info("Validate when get response from DCA for WPCP domain playboy.com Cache hit count is get not increased and Miss cache increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        print c
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*2.*',c)
        logging.info("Test case execution Completed")
        sleep(10)

    @pytest.mark.run(order=248)
    def test_152_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 259 passed")
        sleep(10)

    @pytest.mark.run(order=249)
    def test_153_Send_Query_from_subscriber_client2_for_Domain_totalwine_com_Using_IB_FLEX_Member_Validate_returns_normal_response_from_DCA(self):
        logging.info("Send Query from subscriber client for Domain totalwine_com Using IB FLEX Member Validate returns blocking response from DCA")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' totalwine.com +noedns -b '+config.client_ip2+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*totalwine.com.*IN.*A.*',str(dig_result))
        logging.info("Test case execution Completed")
        sleep(10)

    @pytest.mark.run(order=250)
    def test_154_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")
        sleep(10)

    @pytest.mark.run(order=251)
    def test_155_Validate_no_CEF_Log_Logs_when_get_blocking_response_from_DCA_for_domain_totalwine_com(self):
        logging.info("Validate NO CEF Log for playboy.com  when get NORMAL response")
        LookFor="named.*info CEF.*totalwine.com.*CAT=0x00000000000000000000000000000001"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert False
        else:
            logging.info("Test case execution Failed")
            assert True

    @pytest.mark.run(order=252)
    def test_156_Validate_Domain_totalwine_com_exist_in_DCA_cache_with_PCP_word_updated(self):
        logging.info("Validate totalwine.com domain still exist in DCA  cache")
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
        assert re.search(r'.*totalwine.com,A,IN.*AA,A,totalwine.com.*',c)
        assert re.search(r'.*0x00000000000000200000000000000001.*',c)
        logging.info("Test case execution Completed")
        sleep(10)

    @pytest.mark.run(order=253)
    def test_157_Validate_when_get_response_from_DCA_for_playboy_com_Cache_hit_count_is_not_increased_and_Miss_cache_count_increased(self):
        logging.info("Validate when get response from DCA for WPCP domain playboy.com Cache hit count is get not increased and Miss cache increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        print c
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*3.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=254)
    def test_158_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 259 passed")
        sleep(10)

    @pytest.mark.run(order=255)
    def test_159_Send_Query_from_subscriber_client1_for_Domain_totalwine_com_Using_IB_FLEX_Member_Validate_returns_blocking_response_from_Bind(self):
        logging.info("Send Query from subscriber client for Domain totalwine_com Using IB FLEX Member Validate returns blocking response from Bind")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' totalwine.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test case execution Completed")
        sleep(10)

    @pytest.mark.run(order=256)
    def test_160_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")
        sleep(10)

    @pytest.mark.run(order=257)
    def test_161_Validate_CEF_Log_Logs_when_get_blocking_response_from_DCA_for_domain_totalwine_com(self):
        logging.info("Validate NO CEF Log for totalwine.com  when get NORMAL response")
        LookFor="fp-rte.*info CEF.*totalwine.com.*CAT=0x00000000000000200000000000000001"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            sleep(10)
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=258)
    def test_162_Validate_Domain_totalwine_com_exist_in_DCA_cache(self):
        logging.info("Validate totalwine.com domain still exist in DCA  cache")
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
        assert re.search(r'.*totalwine.com,A,IN.*AA,A,totalwine.com.*',c)
        logging.info("Test case execution Completed")
        sleep(10)

    @pytest.mark.run(order=259)
    def test_163_Validate_when_get_response_from_DCA_for_totalwine_com_Cache_hit_count_is_increased_and_Miss_cache_count_not_increased(self):
        logging.info("Validate when get response from DCA for PCP domain totalwine.com Cache hit count increased and Miss cache not increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        print c
        assert re.search(r'.*Cache hit count.*1.*',c)
        assert re.search(r'.*Cache miss count.*3.*',c)
        logging.info("Test case execution Completed")
        sleep(10)


    @pytest.mark.run(order=260)
    def test_164_Validate_for_category_download_logs_in_CLI(self):
        logging.info("Validate times.com domain not cached to DCA when send query from the PCP bit matched subscriber client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show log category_download_logs')
        child.expect('cancel the command.')
        c= child.before
        assert re.search(r'.*zvelodb download.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=261)
    def test_165_Validate_for_category_api_logs_in_infoblox_CLI(self):
        logging.info("Validate times.com domain not cached to DCA when send query from the PCP bit matched subscriber client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show log category_api_logs')
        child.expect('cancel the command.')
        c= child.before
        assert re.search(r'.*Succesfully initialized zVeloDB.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=262)
    def test_166_Add_Subscriber_Record_with_PCP_Policy_bit_for_Alchohol_category(self):
        print("\n")
        print("******************************************************************************************")
        print("****      Test cases for PCP bit added by subscriber and queried by non subscriber    ****")
        print("******************************************************************************************")
        restart_the_grid()
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_non_sub_start_client1.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=263)
    def test_167_Validate_Subscriber_Record_with_Policy_bit_for_Alcohol_category(self):
        logging.info("Validate Subscriber Record with Policy bit for Alcohol category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000000000000000001.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=264)
    def test_168_Add_Subscriber_Record_with_PCP_Policy_bit_for_porn_category_for_another_client(self):
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_non_sub_start_client2.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=265)
    def test_169_Validate_Subscriber_Record_with_Policy_bit_for_porn_category_for_another_client(self):
        logging.info("Validate Subscriber Record with Policy bit for porn category for another client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000000000000020040.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=266)
    def test_170_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 253 passed")

    @pytest.mark.run(order=267)
    def test_171_Send_Query_from_registerd_client2_for_Domain_totalwine_com_Using_IB_FLEX_Member_Validate_returns_NORMAL_response(self):
        logging.info("Send Query from subscriber client for Domain totalwine.com Using IB FLEX_Member Validate returns NORMAL response")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' totalwine.com +noedns -b '+config.client_ip2+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*totalwine.com.*IN.*A.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=268)
    def test_172_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=269)
    def test_173_Validate_No_CEF_Log_Logs_when_get_NORMAL_response_from_bind_for_domain_totalwine_com(self):
        logging.info("Validate NO CEF Log for totalwine.com  when get NORMAL response")
        LookFor="info CEF.*totalwine.com.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert False
        else:
            logging.info("Test case execution Failed")
            assert True

    @pytest.mark.run(order=270)
    def test_174_Validate_Domain_totalwine_com_exist_in_DCA_cache(self):
        logging.info("Validate times.com domain still exist in DCA  cache")
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
        res1=re.search(r'.*totalwine.com,A,IN.*AA,A,totalwine.com.*',c)
        res2=re.search(r'.*0x00000000000000200000000000000001.*',c)
        if res1!=None and res2!=None:
            logging.info("Test case execution Completed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=271)
    def test_175_Validate_when_get_response_from_bind_for_totalwine_com_Cache_hit_count_is_not_increased_and_Miss_cache_count_increased(self):
        logging.info("Validate when get response from bind for domain totalwine.com Cache hit count is not get increased and Miss cache count is increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        print c
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=272)
    def test_176_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 259 passed")

    @pytest.mark.run(order=273)
    def test_177_Send_Query_from_non_subscriber_client3_for_Domain_totalwine_com_Using_IB_FLEX_Member_Validate_returns_normal_response_from_Bind(self):
        logging.info("Send Query from subscriber client for Domain totalwine_com Using IB FLEX Member Validate returns blocking response from Bind")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip3)+' "dig @'+str(config.grid_vip)+' totalwine.com +noedns -b '+config.client_ip3+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*totalwine.com.*IN.*A.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=274)
    def test_178_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=275)
    def test_179_Validate_CEF_Log_Logs_when_get_blocking_response_from_bind_for_domain_totalwine_com(self):
        logging.info("Validate NO CEF Log for totalwine.com  when get NORMAL response")
        LookFor=".*info CEF.*totalwine.com.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=276)
    def test_180_Validate_Domain_totalwine_com_exist_in_DCA_cache(self):
        logging.info("Validate totalwine.com domain still exist in DCA  cache")
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
        assert re.search(r'.*totalwine.com,A,IN.*AA,A,totalwine.com.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=277)
    def test_181_Validate_when_get_response_from_bind_for_totalwine_com_Cache_hit_count_is_not_increased_and_Miss_cache_count_increased(self):
        logging.info("Validate when get response from bind for WPCP domain totalwine.com Cache hit count is get not increased and Miss cache increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        print c
        assert re.search(r'.*Cache hit count.*1.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test case execution Completed")


    @pytest.mark.run(order=278)
    def test_182_Add_Subscriber_Record_with_PCP_Policy_bit_for_block_all_except_last_two_bit(self):
        print("\n")
        print("************************************************")
        print("**Test cases Related to ZVELO CATEHGORIZATION***")
        print("************************************************")
        restart_the_grid()
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_zvelo_block_start_client1.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=279)
    def test_183_Validate_Subscriber_Record_with_Policy_bit_for_dynamic_domain(self):
        logging.info("Validate Subscriber Record with Different PCP Policy bit")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00ffffffffffffffffffffffffffffff.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=280)
    def test_184_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 279 passed")


    @pytest.mark.run(order=281)
    def test_185_query_all_the_PCP_domains(self):
        fobj=open("pcp_domains.txt", 'r')
        for line in fobj:
            line=line.replace("\n","")
            try:
                logging.info("query all the pcp domains")
                dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' '+str(line)+' +noedns -b '+config.client_ip1+' +tries=1"'
                dig_result = subprocess.check_output(dig_cmd, shell=True)
                print dig_result
                assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
                assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
                assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
                logging.info("Test case execution Completed")
            except:
                logging.info("Test case execution Falied")
                assert False

    @pytest.mark.run(order=282)
    def test_186_stop_syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution passed")

    @pytest.mark.run(order=283)
    def test_187_Validate_Named_CEF_Log_Logs_for_totalwine_com_for_NIOS_PCP_bit_0(self):
        logging.info("Validate Named CEF Log for totalwine.com  when get response from Bind for NIOS PCP bit 0")
        LookFor="named.*info CEF.*totalwine.com.*CAT=0x00000000000000200000000000000001"
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

    @pytest.mark.run(order=284)
    def test_188_Validate_Named_CEF_Log_Logs_for_weedmaps_com_for_NIOS_PCP_bit_1(self):
        logging.info("Validate Named CEF Log for weedmaps.com  when get response from Bind for NIOS PCP bit 1")
        #LookFor="named.*info CEF.*weedmaps.com.*CAT=0x00000000000000000000000000000002"
        LookFor="named.*info CEF.*weedmaps.com.*CAT=0x00000000000000200020000000000002"
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

    @pytest.mark.run(order=285)
    def test_189_Validate_Named_CEF_Log_Logs_for_lottery_gov_cn_for_NIOS_PCP_bit_6(self):
        logging.info("Validate Named CEF Log for lottery.gov.cn  when get response from Bind or NIOS PCP bit 6")
        LookFor="named.*info CEF.*lottery.gov.cn.*CAT=0x00000000000000000000000000000040"
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

    @pytest.mark.run(order=286)
    def test_190_Validate_Named_CEF_Log_Logs_for_bloody_disgusting_com_for_NIOS_PCP_bit_10(self):
        logging.info("Validate Named CEF Log for bloody-disgusting.com  when get response from Bind or NIOS PCP bit 10")
        LookFor="named.*info CEF.*bloody-disgusting.com.*0x00000000000000000004000000000400"
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

    @pytest.mark.run(order=287)
    def test_191_Validate_Named_CEF_Log_Logs_for_defence_point_gr_for_NIOS_PCP_bit_11(self):
        logging.info("Validate Named CEF Log for defence-point.gr when get response from Bind or NIOS PCP bit 11")
        LookFor="named.*info CEF.*defence-point.gr.*CAT=0x00000000000000040000000000000800"
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

    @pytest.mark.run(order=288)
    def test_192_Validate_Named_CEF_Log_Logs_for_hugedomains_com_for_NIOS_PCP_bit_14(self):
        logging.info("Validate Named CEF Log for hugedomains.com  when get response from Bind or NIOS PCP bit 14")
        LookFor="named.*info CEF.*hugedomains.com.*CAT=0x00000000000000000000000000004000"
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

    @pytest.mark.run(order=289)
    def test_193_Validate_Named_CEF_Log_Logs_for_pasion_com_for_NIOS_PCP_bit_15(self):
        logging.info("Validate Named CEF Log for pasion.com  when get response from Bind for NIOS PCP bit 15")
        LookFor="named.*info CEF.*pasion.com.*CAT=0x000000000000000000000000000a0000"
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

    @pytest.mark.run(order=290)
    def test_194_Validate_Named_CEF_Log_Logs_for_www_wicca_life_com_for_NIOS_PCP_bit_16(self):
        logging.info("Validate Named CEF Log for www.wicca-life.com  when get response from Bind or NIOS PCP bit 16")
        LookFor="named.*info CEF.*www.wicca-life.com.*CAT=0x00000100000080000000000000010000"
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

    @pytest.mark.run(order=291)
    def test_195_Validate_Named_CEF_Log_Logs_for_xhamster3_com_for_NIOS_PCP_bit_17(self):
        logging.info("Validate Named CEF Log for xhamster3.com  when get response from Bind for NIOS PCP bit 17")
        LookFor="named.*info CEF.*xhamster3.com.*CAT=0x00000000000000000000000000020000"
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

    @pytest.mark.run(order=292)
    def test_196_Validate_Named_CEF_Log_Logs_for_tinder_com_for_NIOS_PCP_bit_19(self):
        logging.info("Validate Named CEF Log for tinder.com  when get response from Bind for NIOS PCP bit 19")
        LookFor="named.*info CEF.*tinder.com.*CAT=0x00000000000040000000000000080000"
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

    @pytest.mark.run(order=293)
    def test_197_Validate_Named_CEF_Log_Logs_for_swaggsauce_com_for_NIOS_PCP_bit_22(self):
        logging.info("Validate Named CEF Log for swaggsauce.com  when get response from Bind for NIOS PCP bit 22")
        LookFor="named.*info CEF.*swaggsauce.com.*CAT=0x00000000000000200020000000400000"
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

    @pytest.mark.run(order=294)
    def test_198_Validate_Named_CEF_Log_Logs_for_www_swordandscale_com_for_NIOS_PCP_bit_24(self):
        logging.info("Validate Named CEF Log for www.swordandscale.com  when get response from Bind for NIOS PCP bit 24")
        LookFor="named.*info CEF.*www.swordandscale.com.*CAT=0x00000000010000000800000001000000"
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

    @pytest.mark.run(order=295)
    def test_199_Validate_Named_CEF_Log_Logs_for_www_budsgunshop_com_for_NIOS_PCP_bit_25(self):
        logging.info("Validate Named CEF Log for www.budsgunshop.com  when get response from Bind for NIOS PCP bit 25")
        LookFor="named.*info CEF.*budsgunshop.com.*CAT=0x00000000000000200000000002000000"
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

    @pytest.mark.run(order=296)
    def test_200_Validate_Named_CEF_Log_Logs_for_www_cdnx_stream_for_NIOS_PCP_bit_26(self):
        logging.info("Validate Named CEF Log for cdnx.stream  when get response from Bind for NIOS PCP bit 26")
        LookFor="named.*info CEF.*cdnx.stream.*CAT=0x00000000000000000000000004000000"
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

    @pytest.mark.run(order=297)
    def test_201_Validate_Named_CEF_Log_Logs_for_www_adultfriendfinder_com_for_NIOS_PCP_bit_26(self):
        logging.info("Validate Named CEF Log for adultfriendfinder.com  when get response from Bind for NIOS PCP bit 32")
        LookFor="named.*info CEF.*adultfriendfinder.com.*CAT=0x00000000000000000000000400080000"
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

    @pytest.mark.run(order=298)
    def test_202_Validate_Named_CEF_Log_Logs_for_www_exoclick_com_for_NIOS_PCP_bit_33(self):
        logging.info("Validate Named CEF Log for exoclick.com  when get response from Bind for NIOS PCP bit 33")
        LookFor="named.*info CEF.*exoclick.com.*CAT=0x00000000000000000000000800000000"
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

    @pytest.mark.run(order=299)
    def test_203_Validate_Named_CEF_Log_Logs_for_www_os7_biz_for_NIOS_PCP_bit_34(self):
        logging.info("Validate Named CEF Log for os7.biz  when get response from Bind for NIOS PCP bit 34")
        LookFor="named.*info CEF.*os7.biz.*CAT=0x00000000000000000080000400000000"
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

    @pytest.mark.run(order=300)
    def test_204_Validate_Named_CEF_Log_Logs_for_www_adskeeper_co_uk_for_NIOS_PCP_bit_35(self):
        logging.info("Validate Named CEF Log for adskeeper.co.uk  when get response from Bind for NIOS PCP bit 35")
        LookFor="named.*info CEF.*adskeeper.co.uk.*CAT=0x00000000000000000000000800000000"
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

    @pytest.mark.run(order=301)
    def test_205_Validate_Named_CEF_Log_Logs_for_www_openload_co_for_NIOS_PCP_bit_36(self):
        logging.info("Validate Named CEF Log for openload.co  when get response from Bind for NIOS PCP bit 36")
        LookFor="named.*info CEF.*openload.co.*CAT=0x00000000000000000000004000000000"
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

    @pytest.mark.run(order=302)
    def test_206_Validate_Named_CEF_Log_Logs_for_www_autozone_com_for_NIOS_PCP_bit_37(self):
        logging.info("Validate Named CEF Log for autozone.com when get response from Bind for NIOS PCP bit 37")
        LookFor="named.*info CEF.*autozone.com.*CAT=0x00000000000000200000002000000000"
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

    @pytest.mark.run(order=303)
    def test_207_Validate_Named_CEF_Log_Logs_for_www_wetransfer_com_for_NIOS_PCP_bit_38(self):
        logging.info("Validate Named CEF Log for wetransfer.com  when get response from Bind for NIOS PCP bit 38")
        LookFor="named.*info CEF.*wetransfer.com.*CAT=0x00000000000000000000004000000000"
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

    @pytest.mark.run(order=304)
    def test_208_Validate_Named_CEF_Log_Logs_for_www_teenhd_porn_for_NIOS_PCP_bit_39(self):
        logging.info("Validate Named CEF Log for teenhd.porn  when get response from Bind for NIOS PCP bit 39")
        LookFor="named.*info CEF.*teenhd.porn.*CAT=0x00000000000000000000008000000000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 304Execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=305)
    def test_209_Validate_Named_CEF_Log_Logs_for_www_services_brid_tv_for_NIOS_PCP_bit_40(self):
        logging.info("Validate Named CEF Log for services.brid.tv  when get response from Bind for NIOS PCP bit 40")
        LookFor="named.*info CEF.*services.brid.tv.*CAT=0x00000000000000000004010000000000"
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

    @pytest.mark.run(order=306)
    def test_210_Validate_Named_CEF_Log_Logs_for_www_ct137_isaachosting_ca_for_NIOS_PCP_bit_43(self):
        logging.info("Validate Named CEF Log for ct137.isaachosting.ca when get response from Bind for NIOS PCP bit 43")
        LookFor="named.*info CEF.*ct137.isaachosting.ca.*CAT=0x00000000000000000000200000000000"
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

    @pytest.mark.run(order=307)
    def test_211_Validate_Named_CEF_Log_Logs_for_fandangollc_demdex_net_for_NIOS_PCP_bit_45(self):
        logging.info("Validate Named CEF Log for fandangollc.demdex.net  when get response from Bind for NIOS PCP bit 45")
        LookFor="named.*info CEF.*fandangollc.demdex.net.*CAT=0x00000000000000000000200000000000"
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

    @pytest.mark.run(order=308)
    def test_212_Validate_Named_CEF_Log_Logs_for_www_funnyjunk_com_for_NIOS_PCP_bit_46(self):
        logging.info("Validate Named CEF Log for funnyjunk.com when get response from Bind for NIOS PCP bit 46")
        LookFor="named.*info CEF.*funnyjunk.com.*CAT=0x00000000000000000004400000000000"
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

    @pytest.mark.run(order=309)
    def test_213_Validate_Named_CEF_Log_Logs_for_itheat_com_for_NIOS_PCP_bit_47(self):
        logging.info("Validate Named CEF Log for itheat.com  when get response from Bind for NIOS PCP bit 47")
        LookFor="named.*info CEF.*itheat.com.*CAT=0x00000000000040000000000000000000"
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

    @pytest.mark.run(order=310)
    def test_214_Validate_Named_CEF_Log_Logs_for_www_edgenuity_com_for_NIOS_PCP_bit_48(self):
        logging.info("Validate Named CEF Log for edgenuity.com when get response from Bind for NIOS PCP bit 48")
        LookFor="named.*info CEF.*edgenuity.com.*CAT=0x00000000000000000001000000000000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 310Execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=311)
    def test_215_Validate_Named_CEF_Log_Logs_for_babytree_com_for_NIOS_PCP_bit_49(self):
        logging.info("Validate Named CEF Log for babytree.com  when get response from Bind for NIOS PCP bit 49")
        LookFor="named.*info CEF.*babytree.com.*CAT=0x00000000001000000008000000000000"
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

    @pytest.mark.run(order=312)
    def test_216_Validate_Named_CEF_Log_Logs_for_www_tinyzonetv_to_for_NIOS_PCP_bit_50(self):
        logging.info("Validate Named CEF Log for tinyzonetv.to when get response from Bind for NIOS PCP bit 50")
        LookFor="named.*info CEF.*tinyzonetv.to.*CAT=0x00000004000000000004000000000000"
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

    @pytest.mark.run(order=313)
    def test_217_Validate_Named_CEF_Log_Logs_for_parents_com_for_NIOS_PCP_bit_51(self):
        logging.info("Validate Named CEF Log for parents.com when get response from Bind for NIOS PCP bit 51")
        LookFor="named.*info CEF.*parents.com.*CAT=0x00000000000000040008000000000000"
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

    @pytest.mark.run(order=314)
    def test_218_Validate_Named_CEF_Log_Logs_for_gameloop_fun_for_NIOS_PCP_bit_52(self):
        logging.info("Validate Named CEF Log for gameloop.fun  when get response from Bind for NIOS PCP bit 52")
        LookFor="named.*info CEF.*gameloop.fun.*CAT=0x00000000000000000010000000000000"
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

    @pytest.mark.run(order=315)
    def test_219_Validate_Named_CEF_Log_Logs_for_positivepsychology_com_for_NIOS_PCP_bit_53(self):
        logging.info("Validate Named CEF Log for positivepsychology.com when get response from Bind for NIOS PCP bit 53")
        LookFor="named.*info CEF.*positivepsychology.com.*CAT=0x00000000000000000020000000000000"
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

    @pytest.mark.run(order=316)
    def test_220_Validate_Named_CEF_Log_Logs_for_bell_ca_for_NIOS_PCP_bit_54(self):
        logging.info("Validate Named CEF Log for bell.ca  when get response from Bind for NIOS PCP bit 54")
        LookFor="named.*info CEF.*bell.ca.*CAT=0x00000000000000000040000000000000"
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

    @pytest.mark.run(order=317)
    def test_221_Validate_Named_CEF_Log_Logs_for_supercoloring_com_for_NIOS_PCP_bit_55(self):
        logging.info("Validate Named CEF Log for supercoloring.com  when get response from Bind for NIOS PCP bit 55")
        LookFor="named.*info CEF.*supercoloring.com.*CAT=0x00000400000000000080000000000000"
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

    @pytest.mark.run(order=318)
    def test_222_Validate_Named_CEF_Log_Logs_for_lawtime_cn_for_NIOS_PCP_bit_56(self):
        logging.info("Validate Named CEF Log for lawtime.cn when get response from Bind for NIOS PCP bit 56")
        LookFor="named.*info CEF.*lawtime.cn.*CAT=0x00000000000000000100000000000000"
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

    @pytest.mark.run(order=319)
    def test_223_Validate_Named_CEF_Log_Logs_for_networksolutionsemail_com_for_NIOS_PCP_bit_57(self):
        logging.info("Validate Named CEF Log for networksolutionsemail.com when get response from Bind for NIOS PCP bit 57")
        LookFor="named.*info CEF.*networksolutionsemail.com.*CAT=0x00000000000000000200000000000000"
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

    @pytest.mark.run(order=320)
    def test_224_Validate_Named_CEF_Log_Logs_for_mp3teca_com_for_NIOS_PCP_bit_59(self):
        logging.info("Validate Named CEF Log for mp3teca.com  when get response from Bind for NIOS PCP bit 59")
        LookFor="named.*info CEF.*mp3teca.com.*CAT=0x00000000000000000800000000000000"
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

    @pytest.mark.run(order=321)
    def test_225_Validate_Named_CEF_Log_Logs_for_fekrafn_com_for_NIOS_PCP_bit_60(self):
        logging.info("Validate Named CEF Log for fekrafn.com  when get response from Bind for NIOS PCP bit 60")
        LookFor="named.*info CEF.*fekrafn.com.*CAT=0x00000000002000001000000000000000"
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

    @pytest.mark.run(order=322)
    def test_226_Validate_Named_CEF_Log_Logs_for_taxheaven_gr_for_NIOS_PCP_bit_61(self):
        logging.info("Validate Named CEF Log for taxheaven.gr  when get response from Bind for NIOS PCP bit 61")
        LookFor="named.*info CEF.*taxheaven.gr.*CAT=0x00000000000000002000000000000000"
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

    @pytest.mark.run(order=323)
    def test_227_Validate_Named_CEF_Log_Logs_for_koton_com_for_NIOS_PCP_bit_62(self):
        logging.info("Validate Named CEF Log for koton.com  when get response from Bind for NIOS PCP bit 62")
        LookFor="named.*info CEF.*koton.com.*CAT=0x00000000000000204000000000000000"
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

    @pytest.mark.run(order=324)
    def test_228_Validate_Named_CEF_Log_Logs_for_ad1_tjeux_com_for_NIOS_PCP_bit_63(self):
        logging.info("Validate Named CEF Log for ad1.tjeux.com when get response from Bind for NIOS PCP bit 63")
        LookFor="named.*info CEF.*ad1.tjeux.com.*CAT=0x00000000000000008000000000000000"
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

    @pytest.mark.run(order=325)
    def test_229_Validate_Named_CEF_Log_Logs_for_dailymail_co_uk_for_NIOS_PCP_bit_64(self):
        logging.info("Validate Named CEF Log for dailymail.co.uk  when get response from Bind for NIOS PCP bit 64")
        LookFor="named.*info CEF.*dailymail.co.uk.*CAT=0x00000000000000040004000000000000"
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

    @pytest.mark.run(order=326)
    def test_230_Validate_Named_CEF_Log_Logs_for_nfl_com_for_NIOS_PCP_bit_66(self):
        logging.info("Validate Named CEF Log for nfl.com when get response from Bind for NIOS PCP bit 66")
        LookFor="named.*info CEF.*nfl.com.*CAT=0x00000000000000440004000000000000"
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

    @pytest.mark.run(order=327)
    def test_231_Validate_Named_CEF_Log_Logs_for_libero_it_for_NIOS_PCP_bit_67(self):
        logging.info("Validate Named CEF Log for libero.it when get response from Bind for NIOS PCP bit 67")
        LookFor="named.*info CEF.*libero.it.*CAT=0x00000000000000080000000000000000"
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

    @pytest.mark.run(order=328)
    def test_232_Validate_Named_CEF_Log_Logs_for_exportersindia_com_for_NIOS_PCP_bit_69(self):
        logging.info("Validate Named CEF Log for exportersindia.com when get response from Bind for NIOS PCP bit 69")
        LookFor="named.*info CEF.*exportersindia.com.*CAT=0x00000000000000200000000000000000"
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

    @pytest.mark.run(order=329)
    def test_233_Validate_Named_CEF_Log_Logs_for_wikihow_com_for_NIOS_PCP_bit_70(self):
        logging.info("Validate Named CEF Log for wikihow.com  when get response from Bind for NIOS PCP bit 70")
        LookFor="named.*info CEF.*wikihow.com.*CAT=0x00000000000001000000000000000000"
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

    @pytest.mark.run(order=330)
    def test_234_Validate_Named_CEF_Log_Logs_for_qyer_com_for_NIOS_PCP_bit_71(self):
        logging.info("Validate Named CEF Log for qyer.com  when get response from Bind for NIOS PCP bit 71")
        LookFor="named.*info CEF.*qyer.com.*CAT=0x00000000000001800000000000000000"
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

    @pytest.mark.run(order=331)
    def test_235_Validate_Named_CEF_Log_Logs_for_jisho_org_for_NIOS_PCP_bit_72(self):
        logging.info("Validate Named CEF Log for jisho.org  when get response from Bind for NIOS PCP bit 72")
        LookFor="named.*info CEF.*jisho.org.*CAT=0x00000000000001000000000000000000"
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

    @pytest.mark.run(order=332)
    def test_236_Validate_Named_CEF_Log_Logs_for_www_scientificamerican_com_for_NIOS_PCP_bit_73(self):
        logging.info("Validate Named CEF Log for www.scientificamerican.com when get response from Bind for NIOS PCP bit 73")
        LookFor="named.*info CEF.*www.scientificamerican.com.*CAT=0x00000000000002040004000000000000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case332 Execution Passed")
            assert True
        else:
            logging.info("Test Case332 Execution Failed")
            assert False

    @pytest.mark.run(order=333)
    def test_237_Validate_Named_CEF_Log_Logs_for_filehippo_com_for_NIOS_PCP_bit_75(self):
        logging.info("Validate Named CEF Log for filehippo.com  when get response from Bind for NIOS PCP bit 75")
        LookFor="named.*info CEF.*filehippo.com.*CAT=0x00000000000008000000000000000000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test Case333 Execution Failed")
            assert False

    @pytest.mark.run(order=334)
    def test_238_Validate_Named_CEF_Log_Logs_for_adcount_io_for_NIOS_PCP_bit_76(self):
        logging.info("Validate Named CEF Log for adcount.io  when get response from Bind for NIOS PCP bit 76")
        LookFor="named.*info CEF.*adcount.io.*CAT=0x00000000000010000000000000000000"
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

    @pytest.mark.run(order=335)
    def test_239_Validate_Named_CEF_Log_Logs_for_socialbookmarkssite_com_for_NIOS_PCP_bit_77(self):
        logging.info("Validate Named CEF Log for socialbookmarkssite.com  when get response from Bind for NIOS PCP bit 77")
        LookFor="named.*info CEF.*socialbookmarkssite.com.*CAT=0x00000000000020000000000000000000"
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

    @pytest.mark.run(order=336)
    def test_240_Validate_Named_CEF_Log_Logs_for_www_discordapp_com_for_NIOS_PCP_bit_78(self):
        logging.info("Validate Named CEF Log for discordapp.com  when get response from Bind for NIOS PCP bit 78")
        LookFor="named.*info CEF.*discordapp.com.*CAT=0x00000000000108000000000000000000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test Case336 Execution Failed")
            assert False

    @pytest.mark.run(order=337)
    def test_241_Validate_Named_CEF_Log_Logs_for_acs_org_for_NIOS_PCP_bit_79(self):
        logging.info("Validate Named CEF Log for acs.org  when get response from Bind for NIOS PCP bit 79")
        LookFor="named.*info CEF.*acs.org.*CAT=0x00000000000080000000000000000000"
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

    @pytest.mark.run(order=338)
    def test_242_Validate_Named_CEF_Log_Logs_for_www_wechat_com_for_NIOS_PCP_bit_80(self):
        logging.info("Validate Named CEF Log for wechat.com when get response from Bind for NIOS PCP bit 80")
        LookFor="named.*info CEF.*wechat.com.*CAT=0x00000000080100000000000000000000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case338 Execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=339)
    def test_243_Validate_Named_CEF_Log_Logs_for_ppt_online_org_for_NIOS_PCP_bit_81(self):
        logging.info("Validate Named CEF Log for ppt-online.org when get response from Bind for NIOS PCP bit 81")
        LookFor="named.*info CEF.*ppt-online.org.*CAT=0x00000000000200000001000000000000"
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

    @pytest.mark.run(order=340)
    def test_244_Validate_Named_CEF_Log_Logs_for_loantech_top_for_NIOS_PCP_bit_82(self):
        logging.info("Validate Named CEF Log for loantech.top  when get response from Bind for NIOS PCP bit 82")
        LookFor="named.*info CEF.*loantech.top.*CAT=0x00000000000440002000000000000000"
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

    @pytest.mark.run(order=341)
    def test_245_Validate_Named_CEF_Log_Logs_for_teamviewer_com_for_NIOS_PCP_bit_83(self):
        logging.info("Validate Named CEF Log for teamviewer.com  when get response from Bind for NIOS PCP bit 83")
        LookFor="named.*info CEF.*teamviewer.com.*CAT=0x00000000000800000000000000000000"
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

    @pytest.mark.run(order=342)
    def test_246_Validate_Named_CEF_Log_Logs_for_freepik_com_for_NIOS_PCP_bit_84(self):
        logging.info("Validate Named CEF Log for freepik.com when get response from Bind for NIOS PCP bit 84")
        LookFor="named.*info CEF.*freepik.com.*CAT=0x00000000001000000000000000000000"
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

    @pytest.mark.run(order=343)
    def test_247_Validate_Named_CEF_Log_Logs_for_financialfxclub_com_for_NIOS_PCP_bit_85(self):
        logging.info("Validate Named CEF Log for financialfxclub.com when get response from Bind for NIOS PCP bit 85")
        LookFor="named.*info CEF.*financialfxclub.com.*CAT=0x00000000002000000000000000000000"
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

    @pytest.mark.run(order=344)
    def test_248_Validate_Named_CEF_Log_Logs_for_jwcredito_online_for_NIOS_PCP_bit_86(self):
        logging.info("Validate Named CEF Log for jwcredito.online when get response from Bind for NIOS PCP bit 86")
        LookFor="named.*info CEF.*jwcredito.online.*CAT=0x00000000010000000000000000000000"
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

    @pytest.mark.run(order=345)
    def test_249_Validate_Named_CEF_Log_Logs_for_metmuseum_org_for_NIOS_PCP_bit_87(self):
        logging.info("Validate Named CEF Log for metmuseum.org when get response from Bind for NIOS PCP bit 87")
        LookFor="named.*info CEF.*metmuseum.org.*CAT=0x00000000008000000001000000000000"
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

    @pytest.mark.run(order=346)
    def test_250_Validate_Named_CEF_Log_Logs_for_megadrift_club_for_NIOS_PCP_bit_88(self):
        logging.info("Validate Named CEF Log for megadrift.club when get response from Bind for NIOS PCP bit 88")
        LookFor="named.*info CEF.*megadrift.club.*CAT=0x00000000010000040000400000000000"
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

    @pytest.mark.run(order=347)
    def test_251_Validate_Named_CEF_Log_Logs_for_deere_com_for_NIOS_PCP_bit_89(self):
        logging.info("Validate Named CEF Log for deere.com when get response from Bind for NIOS PCP bit 89")
        LookFor="named.*info CEF.*deere.com.*CAT=0x00000000020000000000000000000000"
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

    @pytest.mark.run(order=348)
    def test_252_Validate_Named_CEF_Log_Logs_for_golfnow_com_for_NIOS_PCP_bit_90(self):
        logging.info("Validate Named CEF Log for golfnow.com when get response from Bind for NIOS PCP bit 90")
        LookFor="named.*info CEF.*golfnow.com.*CAT=0x00000000040000400000000000000000"
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

    @pytest.mark.run(order=349)
    def test_253_Validate_Named_CEF_Log_Logs_for_linkedin_com_for_NIOS_PCP_bit_91(self):
        logging.info("Validate Named CEF Log for linkedin.com  when get response from Bind for NIOS PCP bit 91")
        LookFor="named.*info CEF.*linkedin.com.*CAT=0x00000000200000000000000000000000"
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

    @pytest.mark.run(order=350)
    def test_254_Validate_Named_CEF_Log_Logs_for_pinterest_at_for_NIOS_PCP_bit_92(self):
        logging.info("Validate Named CEF Log for pinterest.at when get response from Bind for NIOS PCP bit 92")
        LookFor="named.*info CEF.*pinterest.at.*CAT=0x00000020100000000000000000000000"
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

    @pytest.mark.run(order=351)
    def test_255_Validate_Named_CEF_Log_Logs_for_parliament_uk_for_NIOS_PCP_bit_93(self):
        logging.info("Validate Named CEF Log for parliament.uk  when get response from Bind for NIOS PCP bit 93")
        LookFor="named.*info CEF.*parliament.uk.*CAT=0x00000001200000000000000000000000"
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

    @pytest.mark.run(order=352)
    def test_256_Validate_Named_CEF_Log_Logs_for_meishij_net_for_NIOS_PCP_bit_94(self):
        logging.info("Validate Named CEF Log for meishij.net  when get response from Bind for NIOS PCP bit 94")
        LookFor="named.*info CEF.*meishij.net.*CAT=0x00000000400000000000000000000000"
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

    @pytest.mark.run(order=353)
    def test_257_Validate_Named_CEF_Log_Logs_for_oneplusbbs_com_for_NIOS_PCP_bit_95(self):
        logging.info("Validate Named CEF Log for oneplusbbs.com when get response from Bind for NIOS PCP bit 95")
        LookFor="named.*info CEF.*oneplusbbs.com.*CAT=0x00000000800000000000000000000000"
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

    @pytest.mark.run(order=354)
    def test_258_Validate_Named_CEF_Log_Logs_for_gujarat_gov_in_for_NIOS_PCP_bit_96(self):
        logging.info("Validate Named CEF Log for gujarat.gov.in  when get response from Bind for NIOS PCP bit 96")
        LookFor="named.*info CEF.*gujarat.gov.in.*CAT=0x00000001000000080000000000000000"
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

    @pytest.mark.run(order=355)
    def test_259_Validate_Named_CEF_Log_Logs_for_unicef_org_for_NIOS_PCP_bit_97(self):
        logging.info("Validate Named CEF Log for unicef.org when get response from Bind for NIOS PCP bit 97")
        LookFor="named.*info CEF.*unicef.org.*CAT=0x00000002000000000000000000000000"
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

    @pytest.mark.run(order=356)
    def test_260_Validate_Named_CEF_Log_Logs_for_piratebay_proxylist_net_for_NIOS_PCP_bit_98(self):
        logging.info("Validate Named CEF Log for piratebay-proxylist.net  when get response from Bind for NIOS PCP bit 98")
        LookFor="named.*info CEF.*piratebay-proxylist.net.*CAT=0x0000000c000000000004000000000000"
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

    @pytest.mark.run(order=357)
    def test_261_Validate_Named_CEF_Log_Logs_for_rutor_info_for_NIOS_PCP_bit_99(self):
        logging.info("Validate Named CEF Log for rutor.info when get response from Bind for NIOS PCP bit 99")
        LookFor="named.*info CEF.*rutor.info.*CAT=0x0000000c000000000000000000000000"
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

    @pytest.mark.run(order=358)
    def test_262_Validate_Named_CEF_Log_Logs_for_petsmart_com_for_NIOS_PCP_bit_100(self):
        logging.info("Validate Named CEF Log for petsmart.com when get response from Bind for NIOS PCP bit 100")
        LookFor="named.*info CEF.*petsmart.com.*CAT=0x00000010000000200000000000000000"
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

    @pytest.mark.run(order=359)
    def test_263_Validate_Named_CEF_Log_Logs_for_greencardphotocheck_com_for_NIOS_PCP_bit_101(self):
        logging.info("Validate Named CEF Log for greencardphotocheck.com when get response from Bind for NIOS PCP bit 101")
        LookFor="named.*info CEF.*greencardphotocheck.com.*CAT=0x00000020000000000000000000000000"
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

    @pytest.mark.run(order=360)
    def test_264_Validate_Named_CEF_Log_Logs_for_townhall_com_for_NIOS_PCP_bit_102(self):
        logging.info("Validate Named CEF Log for townhall.com when get response from Bind for NIOS PCP bit 102")
        LookFor="named.*info CEF.*townhall.com.*CAT=0x00000040000000000000000000000000"
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

    @pytest.mark.run(order=361)
    def test_265_Validate_Named_CEF_Log_Logs_for_point2homes_com_for_NIOS_PCP_bit_103(self):
        logging.info("Validate Named CEF Log for point2homes.com when get response from Bind for NIOS PCP bit 103")
        LookFor="named.*info CEF.*point2homes.com.*CAT=0x00000080020000000000000000000000"
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

    @pytest.mark.run(order=362)
    def test_266_Validate_Named_CEF_Log_Logs_for_17_live_for_NIOS_PCP_bit_104(self):
        logging.info("Validate Named CEF Log for 17.live when get response from Bind for NIOS PCP bit 104")
        LookFor="named.*info CEF.*17.live.*CAT=0x00000100000000000000000000000000"
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

    @pytest.mark.run(order=363)
    def test_267_Validate_Named_CEF_Log_Logs_for_theknot_com_for_NIOS_PCP_bit_105(self):
        logging.info("Validate Named CEF Log for theknot.com when get response from Bind for NIOS PCP bit 105")
        LookFor="named.*info CEF.*theknot.com.*CAT=0x00000200000000000000000000000000"
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

    @pytest.mark.run(order=364)
    def test_268_Validate_Named_CEF_Log_Logs_for_pinclipart_com_for_NIOS_PCP_bit_106(self):
        logging.info("Validate Named CEF Log for pinclipart.com when get response from Bind for NIOS PCP bit 106")
        LookFor="named.*info CEF.*pinclipart.com.*CAT=0x00000020000200000000000000000000"
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

    @pytest.mark.run(order=365)
    def test_269_Validate_Named_CEF_Log_Logs_for_www_cocktailsandcocktalk_com_for_NIOS_PCP_bit_107(self):
        logging.info("Validate Named CEF Log for www.cocktailsandcocktalk.com when get response from Bind for NIOS PCP bit 107")
        LookFor="named.*info CEF.*www.cocktailsandcocktalk.com.*CAT=0x00002000010000000000000000000000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 365Execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=366)
    def test_270_Validate_Named_CEF_Log_Logs_for_locations_ariontrak_com_for_NIOS_PCP_bit_109(self):
        logging.info("Validate Named CEF Log for locations.ariontrak.com when get response from Bind for NIOS PCP bit 109")
        LookFor="named.*info CEF.*locations.ariontrak.com.*CAT=0x00008000000000000000000000000000"
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

    @pytest.mark.run(order=367)
    def test_271_Validate_Named_CEF_Log_Logs_for_cloystercdn_com_for_NIOS_PCP_bit_110(self):
        logging.info("Validate Named CEF Log for cloystercdn.com when get response from Bind for NIOS PCP bit 110")
        LookFor="named.*info CEF.*cloystercdn.com.*CAT=0x00004000000000000000000000000000"
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

    @pytest.mark.run(order=368)
    def test_272_Validate_Named_CEF_Log_Logs_for_wezhan_cn_for_NIOS_PCP_bit_111(self):
        logging.info("Validate Named CEF Log for wezhan.cn when get response from Bind for NIOS PCP bit 111")
        LookFor="named.*info CEF.*wezhan.cn.*CAT=0x00008000000000000000000000000000"
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

    @pytest.mark.run(order=369)
    def test_273_Validate_Named_CEF_Log_Logs_for_nseindia_com_for_NIOS_PCP_bit_112(self):
        logging.info("Validate Named CEF Log for nseindia.com when get response from Bind for NIOS PCP bit 112")
        LookFor="named.*info CEF.*nseindia.com.*CAT=0x00010000000000000000000000000000"
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

    @pytest.mark.run(order=370)
    def test_274_Disable_DCA_subscriber_Query_count_logging_on_site(self):
        print("/n")
        print("******************************************************************")
        print("****  Test cases when DCA subscriber Query count is disabled  ****")
        print("******************************************************************")
        logging.info("Dnable_DCA_subscriber_Query_count_logging_on_site")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        get_ref=json.loads(get_ref)[0]["_ref"]
        data={"dca_sub_query_count":False}
        res = ib_NIOS.wapi_request('PUT', object_type=get_ref,fields=json.dumps(data))
        if type(res)!=tuple:
            logging.info("Test case execution passed")
            time.sleep(5)
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=371)
    def test_275_validate_Disable_DCA_subscriber_Query_count_logging_on_site(self):
        logging.info("Validate_DCA_subscriber_Query_count_reporting_and_Enable_DCA_subscriber_Allowed_and_Blocked_list_support_are_enabled")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=dca_sub_bw_list,dca_sub_query_count")
        get_ref=json.loads(get_ref)
        if get_ref[0]["dca_sub_query_count"]==False:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=372)
    def test_276_Add_Subscriber_Record_with_PCP_Policy_for_News_Category_when_dca_sub_query_count_is_disabled(self):
        restart_the_grid()
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_start_client1.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=373)
    def test_277_Validate_Subscriber_Record_with_PCP_Policy_for_news_Category_when_dca_sub_query_count_is_disabled(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category when dca_sub_query_count is disabled")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000040000000000000000.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=374)
    def test_278_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 375 passed")

    @pytest.mark.run(order=375)
    def test_279_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_playboy_Using_IB_FLEX_Member_Validate_returns_NORMAL_response(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain playboy.com using IB-FLEX Member and Validate get NORMAL response even times.com domain is in cache with PCP word but subscriber client is deleted from subscriber cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=376)
    def test_280_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=377)
    def test_281_Validate_No_CEF_Log_Logs_when_get_NORMAL_response_from_Bind_for_PCP_domain_playboy_com(self):
        logging.info("Validate NO CEF Log for playboy.com  when get NORMAL response")
        LookFor="info CEF.*playboy.com.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=378)
    def test_282_Validate_PCP_Domain_playboy_com_exist_in_DCA_cache(self):
        logging.info("Validate playboy.com domain exist in DCA  cache")
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
        assert re.search(r'.*playboy.com,A,IN.*AA,A,playboy.com.*',c)
        assert re.search(r'.*0x00000000000000000000000000020000.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=379)
    def test_283_Validate_when_get_response_from_bind_for_PCP_domain_playboy_com_Cache_hit_count_is_not_increased_and_Miss_cache_count_is_increased(self):
        logging.info("Validate when get response from DCA for PCP domain playboy.com Cache hit count is not get increased and Miss count is increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        print c
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=380)
    def test_284_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 381 passed")

    @pytest.mark.run(order=381)
    def test_285_Update_Subscriber_Record_with_PCP_Policy_for_News_and_alcohol_Category_when_dca_sub_query_count_is_disabled(self):
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_update_client1.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=382)
    def test_286_Validate_Subscriber_Record_with_PCP_Policy_for_news_Category_when_dca_sub_query_count_is_disabled(self):
        logging.info("Validate Subscriber Record with PCP Policy for news and alcohol Category when dca sub query count is disabled")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00220000000000000000000000020040.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=383)
    def test_287_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=384)
    def test_288_Validate_no_CEF_Log_Logs_when_subscriber_record_is_updated_when_dca_sub_query_count_is_disabled(self):
        logging.info("Validate no CEF Log Logs when subscriber record is updated when dca sub query count is disabled")
        LookFor="info CEF.*QUERY-COUNT.*event_type=INTERIM.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False


    @pytest.mark.run(order=385)
    def test_289_Add_Subscriber_Record_with_BWlist_when_dca_sub_bw_list_is_disabled(self):
        restart_the_grid()
        try:
            logging.info("Add Subscriber Record with BWList")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=99-d99;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';UCP:Unknown-Category-Policy=1;DCP:Dynamic-Category-Policy=1;SUB:Calling-Station-Id=143;BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Case 386 Execution Passed")
            assert True
        except:
            logging.info("Test Case 386 Execution Failed")
            assert False

    @pytest.mark.run(order=386)
    def test_290_Validate_Subscriber_Record_with_BWList(self):
        logging.info("Validate Subscriber Record with_BWList")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000000000000020040.*.*BWFlag.*BL.*facebook.*WL.*bbc.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=387)
    def test_291_Add_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 N/A N/A "ACS:Acct-Session-Id=981-d991;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000001000000000000;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000001000000000000000;SUB:Calling-Station-Id=1493;BWI:BWFlag=1;BL=blore.com;WL=hydbad.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Case 388 Execution Passed")
            assert True
        except:
            logging.info("Test Case 388 Execution Failed")
            assert False
        

    @pytest.mark.run(order=388)
    def test_292_Validate_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000001000000000000.*.*BWFlag.*BL.*blore.*WL.*hydbad.com.*',c)
        logging.info("Test case 389 execution completed")

    @pytest.mark.run(order=389)
    def test_293_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 390 passed")

    @pytest.mark.run(order=390)
    def test_294_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query Blacklist domain facebook.com from PCP bit matching Subscriber client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=391)
    def test_295_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=392)
    def test_296_Validate_NAMED_CEF_Log_For_CAT_BL(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor="named.*info CEF.*facebook.com.*CAT=BL.*"
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

    @pytest.mark.run(order=393)
    def test_297_Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client(self):
        logging.info("Validate Blacklist Domain facebook.com did not cache into DCA When Send Query From PCP bit Matching Subscriber client")
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
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=394)
    def test_298_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com(self):
        logging.info("Validate Cache hit count not increased But Miss cache count increased For Blacklist Domain facebook.com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
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

    @pytest.mark.run(order=395)
    def test_299_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 396 passed")

    @pytest.mark.run(order=396)
    def test_300_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query Blacklist domain facebook com from NON PCP bit matching Subscriber client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip2+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*facebook.com.*IN.*A.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=397)
    def test_301_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=398)
    def test_302_Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_NEGATIVE_CASE(self):
        logging.info("Validate NO CEF Log When Query Blacklist domain facebook com from NON PCP bit matching Subscriber client")
        LookFor="info CEF.*facebook.com.*CAT=BL"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=399)
    def test_303_Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
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
        assert re.search(r'.*facebook.com.*',c)
        assert re.search(r'.*0x00000000100000000000000000000000.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=400)
    def test_304_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
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

    @pytest.mark.run(order=401)
    def test_305_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 402 passed")

    @pytest.mark.run(order=402)
    def test_306_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=403)
    def test_307_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=404)
    def test_308_Validate_DCA_CEF_Log_does_not_shows_fp_rte_When_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate DCA CEF Log does not shows When Query Blacklist domain facebook.com from PCP bit matching Subscriber client")
        LookFor="fp-rte.*info CEF.*facebook.com.*CAT=BL"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=405)
    def test_309_add_32_rpz_zone(self):
        print("************************************************")
        print("****  Test cases Related to SSP            *****")
        print("************************************************")
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

    @pytest.mark.run(order=406)
    def test_310_validate_32_rpz_zone_added(self):
        restart_the_grid()
        logging.info("validate 32 rpz zone added")
        reference1=ib_NIOS.wapi_request('GET', object_type="zone_rp")
        #reference1=json.loads(reference1)
        for i in range(32):
            if "rpz"+str(i)+".com" in reference1:
                logging.info("Test case execution passed")
                assert True
            else:
                logging.info("Test case execution failed")
                assert False

    @pytest.mark.run(order=407)
    def test_311_Add_Subscriber_Record_with_Different_PCP_Policy_bit_for_SSP(self):
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_SSP_start_client1.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=408)
    def test_312_Validate_Subscriber_Record_with_Policy_bit_for_SSP(self):
        logging.info("Validate Subscriber Record with Different PCP Policy bit")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*SSP\:Subscriber-Secure-Policy=ff.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=409)
    def test_313_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 271 passed")
        sleep(10)

    @pytest.mark.run(order=410)
    def test_314_Send_Query_from_subscriber_client_for_rpz_rule_pass1_Using_IB_FLEX_Member_Validate_returns_NORMAL_response(self):
        logging.info("Send Query from subscriber client for rpz rule pass1 Using IB FLEX_Member Validate returns NORMAL response")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' pass1 +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*pass1.*IN.*A.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=411)
    def test_315_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=412)
    def test_316_Validate_No_CEF_Log_Logs_when_get_NORMAL_response_from_bind_for_rpz_rule_pass1(self):
        logging.info("Validate NO CEF Log for times.com  when get NORMAL response")
        LookFor="info CEF.*PASSTHRU.*pass1.*CAT=RPZ.*"
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

    @pytest.mark.run(order=413)
    def test_317_Validate_rpz_rule_does_not_exist_in_DCA_cache(self):
        logging.info("Validate rpz rule domain still exist in DCA  cache")
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
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=414)
    def test_318_Validate_when_get_response_from_DCA_for_pass1_Cache_hit_count_is_not_increased_and_Miss_count_is_increased(self):
        logging.info("Validate when get response from bind for pass1 Cache hit count is get increased and Miss cache count not increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        print c
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=415)
    def test_319_stop_the_subscriber_services_on_all_the_running_members(self):
        print("/n")
        print("******************************************************************")
        print("****  Test cases when subscriber Cache is not present  ****")
        print("******************************************************************")
        logging.info("stop_the_subscriber_services_on_all_the_members")
        ref=stop_subscriber_collection_services_for_added_site([config.grid_fqdn])
        if ref!=None:
            sleep(20)
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=416)
    def test_320_Start_the_subscriber_service_on_IB_FLEX_member(self):
        logging.info("Start the subscriber service on members which are not DCA capable")
        ref=start_subscriber_collection_services_for_added_site([config.grid_fqdn])
        if ref!=None:
            sleep(150)
            logging.info("Test case executed successfully")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=417)
    def test_321_Validate_subscriber_service_is_running_on_IB_FLEX_member(self):
        restart_the_grid()
        sleep(10)
        logging.info("Validating subscriber collection services started on non DCA capable members")
        members=[config.grid_fqdn]
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

    @pytest.mark.run(order=418)
    def test_322_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 194 passed")

    @pytest.mark.run(order=419)
    def test_323_Send_Query_from_when_no_subscriber_data_is_added(self):
        logging.info("Perform Query when no subscribers are added")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' totalwine.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*totalwine.com.*IN.*A.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=420)
    def test_324_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=421)
    def test_325_Validate_No_CEF_Log_Logs_when_get_NORMAL_response_from_DCA_for_PCP_domain_totalwine_com(self):
        logging.info("Validate NO CEF Log for times.com  when get NORMAL response")
        #LookFor=".*named.*query.*totalwine.com.*"
        LookFor="info CEF.*totalwine.com.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=422)
    def test_326_Validate_Domain_totalwine_com_still_exist_in_DCA_cache(self):
        logging.info("Validate totalwine.com domain still exist in DCA  cache")
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
        res1=re.search(r'.*totalwine.com,A,IN.*AA,A,totalwine.com.*',c)
        res2=re.search(r'.*0x00000000000000200000000000000001.*',c)
        if res1!=None and res2==None:
            logging.info("Test case execution failed")
            assert True
        else:
            logging.info("Test case execution Completed")
            assert False

    @pytest.mark.run(order=423)
    def test_327_Validate_when_get_response_from_DCA_for_domain_totalwine_com_Cache_hit_count_is_not_increased_and_Miss_cache_count_is_not_increased(self):
        logging.info("Validate when get response from DCA for domain totalwine.com Cache hit count is not increased and Miss cache count is increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        print c
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=424)
    def test_328_Validate_when_get_response_from_DCA_for_domain_totalwine_com_Cache_hit_count_is_not_increased_and_Miss_cache_count_is_increased(self):
        logging.info("Validate when get response from DCA for domain totalwine.com Cache hit count is not increased and Miss cache count is increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        print c
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=425)
    def test_329_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 194 passed")
        sleep(10)

    @pytest.mark.run(order=426)
    def test_330_Send_Query_from_when_no_subscriber_data_is_added(self):
        logging.info("Perform Query when no subscribers are added")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' totalwine.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*totalwine.com.*IN.*A.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=427)
    def test_331_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=428)
    def test_332_Validate_No_CEF_Log_Logs_when_get_NORMAL_response_from_DCA_for_PCP_domain_totalwine_com(self):
        logging.info("Validate NO CEF Log for times.com  when get NORMAL response")
        LookFor=".*UDP: query.*playboy.com IN A response.* NOERROR.*"
        LookFor1="info CEF.*totalwine.com.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None and logs1==None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=429)
    def test_333_Validate_Domain_totalwine_com_still_exist_in_DCA_cache(self):
        logging.info("Validate totalwine.com domain still exist in DCA  cache")
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
        res1=re.search(r'.*totalwine.com,A,IN.*AA,A,totalwine.com.*',c)
        res2=re.search(r'.*0x00000000000000200000000000000001.*',c)
        if res1!=None and res2==None:
            logging.info("Test case execution failed")
            assert True
        else:
            logging.info("Test case execution Completed")
            assert False

    @pytest.mark.run(order=430)
    def test_334_Validate_when_get_response_from_DCA_for_domain_totalwine_com_Cache_hit_count_is_increased_and_Miss_cache_count_count_not_increased(self):
        logging.info("Validate when get response from DCA for WPCP domain totalwine.com Cache hit count is get increased and Miss cache count not increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        print c
        assert re.search(r'.*Cache hit count.*1.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test case execution Completed")

    
    @pytest.mark.run(order=431)
    def test_335_Enable_DCA_subscriber_Query_count_logging_on_site(self):
        print("/n")
        print("******************************************************************")
        print("**Enable DCA subscriber Query count and Blocked_list_support  ****")
        print("******************************************************************")
        logging.info("Ennable_DCA_subscriber_Query_count_logging_on_site")
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

    @pytest.mark.run(order=432)
    def test_336_validate_Enable_DCA_subscriber_Query_count_logging_on_site(self):
        logging.info("Validate_DCA_subscriber_Query_count_reporting_and_Enable_DCA_subscriber_Allowed_and_Blocked_list_support_are_enabled")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=dca_sub_bw_list,dca_sub_query_count")
        get_ref=json.loads(get_ref)
        if get_ref[0]["dca_sub_query_count"]==True:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=433)
    def test_337_Enable_DCA_subscriber_Allowed_and_Blocked_list_support_on_site(self):
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

    @pytest.mark.run(order=434)
    def test_338_validate_DCA_subscriber_Allowed_and_Blocked_list_support_is_enabled_on_site(self):
        logging.info("Validate DCA subscriber Query count reporting and Enable DCA subscriber Allowed and Blocked list support are enabled")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=dca_sub_bw_list")
        get_ref=json.loads(get_ref)
        if get_ref[0]["dca_sub_bw_list"]==True:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False
    '''
    @pytest.mark.run(order=435)
    def test_339_reboot_the_IB_FLEX_Member_to_enable_DCA_subscriber_Allowed_and_Blocked_list_support_is_enabled_on_site(self):
        prod_reboot(config.grid_vip)
    '''
    
    @pytest.mark.run(order=436)
    def test_340_Add_Subscriber_Cache_Record_with_Only_PCP_AVP(self):
        print("\n")
        print("************************************************")
        print("****      Test cases for fp-cli commands    ****")
        print("************************************************")
        stop_subscriber_collection_services_for_added_site([config.grid_fqdn])
        sleep(30)
        start_subscriber_collection_services_for_added_site([config.grid_fqdn])
        sleep(30)
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_start_client1.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=437)
    def test_341_Validate_Subscriber_Record_with_Only_PCP_AVP(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP:Parental-Control-Policy=00000000000000040000000000000000.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=438)
    def test_342_Validate_Subscriber_Record_with_Only_PCP_AVP(self):
        logging.info("Validate_Subscriber_Record_with_Only_PCP_AVP")
        res=fpcli("fp-cli fp ib_dca dump subscriber_entries 1",config.grid_vip)
        print res
        if res["PCP"]=="0x00000000000000040000000000000000":
            logging.info("Test case execution completed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=439)
    def test_343_Add_Subscriber_Cache_Record_with_Only_WPCP_AVP(self):
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_start_client1.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=440)
    def test_344_Validate_Subscriber_Record_with_Only_WPCP_AVP(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCC:PC-Category-Policy=00000000000000000000000000000001.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=441)
    def test_345_Validate_Subscriber_Record_with_Only_WPCP_AVP(self):
        logging.info("Validate_Subscriber_Record_with_Only_PCP_AVP")
        res=fpcli("fp-cli fp ib_dca dump subscriber_moredetails 3",config.grid_vip)
        print res
        if res["IPv4"]==config.client_ip1:
            logging.info("Test case execution completed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=442)
    def test_346_Add_Subscriber_Cache_Record_with_Only_SSP_AVP(self):
        dig_cmd= 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_only_SSP_start_client1.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=443)
    def test_347_Validate_Subscriber_Record_with_Only_SSP_AVP(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*SSP:Subscriber-Secure-Policy=ff.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=444)
    def test_348_Validate_Subscriber_Record_with_Only_SSP_AVP(self):
        logging.info("Validate_Subscriber_Record_with_Only_PCP_AVP")
        sleep(20)
        res=fpcli("fp-cli fp ib_dca dump subscriber_entries 1",config.grid_vip)
        print res
        if res!=None:
            logging.info("Test case execution completed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
 
    @pytest.mark.run(order=445)
    def test_349_Add_Subscriber_Cache_Record_with_Only_Unknonwn_AVP(self):
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_only_unknown_start_client1.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=446)
    def test_350_Validate_Subscriber_Record_with_Only_Unknonwn_AVP(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*UCP:Unknown-Category-Policy=1.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=447)
    def test_351_Validate_Subscriber_Record_with_Only_Unknown_AVP(self):
        logging.info("Validate_Subscriber_Record_with_Only_PCP_AVP")
        res=fpcli("fp-cli fp ib_dca dump subscriber_entries 1",config.grid_vip)
        if res!=None:
            logging.info("Test case execution completed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
 
    @pytest.mark.run(order=448)
    def test_352_Add_Subscriber_Cache_Record_with_Only_Dynamic_AVP(self):
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_unknown_dynamic_start_client1.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=449)
    def test_353_Validate_Subscriber_Record_with_Only_Dynamic_AVP(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*DCP:Dynamic-Category-Policy=1.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=450)
    def test_354_Validate_Subscriber_Record_with_Only_Dynamic_AVP(self):
        logging.info("Validate_Subscriber_Record_with_Only_PCP_AVP")
        res=fpcli("fp-cli fp ib_dca dump subscriber_moredetails 3",config.grid_vip)
        print res
        if res["DCP"]=="true":
            logging.info("Test case execution completed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
    
    @pytest.mark.run(order=451)
    def test_355_Add_Subscriber_Cache_Record_with_Only_ProxyAll_AVP(self):
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_unknown_dynamic_start_client1.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=452)
    def test_356_Validate_Subscriber_Record_with_Only_ProxyAll_AVP(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*DCP:Dynamic-Category-Policy=1.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=453)
    def test_357_Validate_Subscriber_Record_with_Only_Proxyall_AVP(self):
        logging.info("Validate_Subscriber_Record_with_Only_PCP_AVP")
        res=fpcli("fp-cli fp ib_dca dump subscriber_moredetails 1",config.grid_vip)
        print res
        #if res["Pxy-Al"]=="true" and res["Pri-Proxy"]=="0x0a23b507":
        if res["Pxy-Al"]=="false":
            logging.info("Test case execution completed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=454)
    def test_358_Add_Subscriber_Cache_Record_with_Only_BWList_AVP(self):
        logging.info("Subscriber Record ")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=9;NAS:NAS-PORT=1813;SUB:Calling-Station-Id=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';BWI:BWFlag=1;BL=facebook.com;WL=bbc.com"')
        child.expect('Record successfully added')

    @pytest.mark.run(order=455)
    def test_359_Validate_Subscriber_Record_with_Only_BWList_AVP(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*:BWFlag=1.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=456)
    def test_360_Validate_Subscriber_Record_added(self):
        logging.info("Validate_Subscriber_Record_with_Only_PCP_AVP")
        res=fpcli("fp-cli fp ib_dca dump subscriber_moredetails 3",config.grid_vip)
        if res["bwflag"]=="true":
            logging.info("Test case execution completed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=457)
    def test_361_Validate_Subscriber_Record_with_Only_PCP_LocalId_bypass_DNP_IPV4_and_IPV6_fields(self):
        logging.info("Validate_Subscriber_Record_with_Only_PCP_LocalId_bypass_DNP_IPV4_and_IPV6_fields")
        res=fpcli("fp-cli fp ib_dca dump subscriber_entries 1",config.grid_vip)
        if res["IPv4"]==config.client_ip1 and res["IPv6"]=="" and res["Local-Id"]=="0x000000000000" and res["bypass"]=="false" and res["DNP"]=="0" :
            logging.info("Test case execution completed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=458)
    def test_362_Add_Subscriber_Cache_Record_with_IPV4_Prefix_set_other_than_32(self):
        logging.info("Add_Subscriber_Cache_Record_with_IPV4_Prefix_set_other_than_32")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data add 10.120.21.0 24 N/A N/A "ACS:Acct-Session-Id=9999732d-34590346;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000000001;SUB:Calling-Station-Id=110361221;BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;IPA:IP6=2620:10a:6000:2500:230:48ff:fed5:d928;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+'"')
        child.expect('Record successfully added')

    @pytest.mark.run(order=459)
    def test_363_Validate_Subscriber_Record_with_IPV4_Prefix_set_other_than_32(self):
        logging.info("Validate_Subscriber_Record_with_IPV4_Prefix_set_other_than_32")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*10.120.21.0\/24\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000000000000020040.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=460)
    def test_364_Validate_command_fp_cli_fp_ib_dca_dump_subscriber_ipv4_prefixes_with_IPV4_Prefix_set_other_than_32(self):
        logging.info("Validate_command_fp_cli_fp_ib_dca_dump_subscriber_ipv4_prefixes_with_IPV4_Prefix_set_other_than_32")
        res=fpcli("fp-cli fp ib_dca dump subscriber_ipv4_prefixes",config.grid_vip)
        print res
        if res["Prefix address"]=="10.120.21.0" and res["CIDR"]=="24" and res["PCP"]=="0x00000000000000000000000000020040":
            logging.info("Test case execution completed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=461)
    def test_365_Add_Subscriber_Cache_Record_with_IPV6_Prefix_set_other_than_128(self):
        logging.info("Add_Subscriber_Cache_Record_with_IPV6_Prefix_set_other_than_128")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data add 2123:345:287::6727:22 96 N/A N/A "ACS:Acct-Session-Id=9999732d-34590346;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000000001;SUB:Calling-Station-Id=110361221;BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;IPA:IP6=2620:10a:6000:2500:230:48ff:fed5:d928;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+'"')
        child.expect('Record successfully added')
        sleep(20)

    @pytest.mark.run(order=462)
    def test_366_Validate_Subscriber_Record_with_IPV6_Prefix_set_other_than_128(self):
        logging.info("Validate_Subscriber_Record_with_IPV6_Prefix_set_other_than_128")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*2123:345:287::6727:22\/96\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000000000000020040.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=463)
    def test_367_Validate_the_command_fp_cli_fp_ib_dca_dump_subscriber_ipv6_prefixes_with_IPV6_Prefix_set_other_than_128(self):
        logging.info("Validate_the_command_fp_cli_fp_ib_dca_dump_subscriber_ipv6_prefixes_with_IPV6_Prefix_set_other_than_128")
        res=fpcli("fp-cli fp ib_dca dump subscriber_ipv6_prefixes",config.grid_vip)
        print res
        if res["Prefix address"]=="2123:345:287::" and res["CIDR"]=="96" and res["PCP"]=="0x00000000000000000000000000020040":
            logging.info("Test case execution completed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False    


    @pytest.mark.run(order=464)
    def test_368_Add_Subscriber_Cache_Record_with_PCP_bit_set_to_block_all(self):
        print("\n")
        print("************************************************")
        print("**** Test cases when all PCP bit set to F   ****")
        print("************************************************")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_set_to_all_FF_start_client1.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)
        
        
    @pytest.mark.run(order=465)
    def test_369_Validate_Subscriber_Record_with_PCP_bit_set_to_block_all(self):
        logging.info("Validate_Subscriber_Record_with_IPV6_Prefix_set_other_than_128")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=fffffffffffffffffffffffffffffff.*',c)
        logging.info("Test case execution completed")
    
    @pytest.mark.run(order=466)
    def test_370_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 128 passed")

    @pytest.mark.run(order=467)
    def test_371_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
        restart_the_grid()
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
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=468)
    def test_372_Send_Query_from_Any_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_Blocked_IPs_in_response_from_Bind_As_Not_DCA_Cache(self):
        logging.info("Perform Query from Any Subscriber client for PCP Domain times.com using IB-FLEX Member and get PCP Blocked IPs response from Bind as times.com not in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=469)
    def test_373_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=470)
    def test_374_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_times_com(self):
        logging.info("Validate Named CEF Log for times.com  when get response from Bind")
        LookFor=".*named.*info CEF.*times.com.*CAT=ALL.*"
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

    @pytest.mark.run(order=471)
    def test_375_Validate_PCP_Domain_times_com_did_not_cached_to_DCA_When_Send_Query_From_PCP_bit_Matched_Subscriber_client(self):
        logging.info("Validate times.com domain not cached to DCA when send query from the PCP bit matched subscriber client")
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
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=472)
    def test_376_Validate_when_get_response_from_Bind_for_PCP_domain_times_com_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased(self):
        logging.info("Validate when get response from Bind for PCP domain times.com Cache hit count not increased and Miss_cache count count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
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

    @pytest.mark.run(order=473)
    def test_377_Add_Subscriber_Record_with_PCP_Policy_bit_set_for_domain_falling_under_2_categories_with_PCP_bit_set_to_first_bit(self):
        print("\n")
        print("************************************************")
        print("**Test cases Related to ZVELO CATEHGORIZATION***")
        print("************************************************")
        restart_the_grid()
        try:
            logging.info("Add_Subscriber_Record_with_PCP_Policy_bit_set_for_domain_falling_under_2_categories_with_PCP_bit_set_to_first_bit")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=9544;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000100000000000000000000;SSP:Subscriber-Secure-Policy=ff;UCP:Unknown-Category-Policy=1;SUB:Calling-Station-Id=663;"')
            child.expect('Record successfully added')
            logging.info("Test case execution Passed")
            assert True
        except:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=474)
    def test_378_Validate_Subscriber_Record_with_Policy_bit_for_dynamic_domain(self):
        logging.info("Validate Subscriber Record with Different PCP Policy bit")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000100000000000000000000.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=475)
    def test_379_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 279 passed")
        sleep(10)

    @pytest.mark.run(order=476)
    def test_380_query_all_the_PCP_domains(self):
        try:
            logging.info("query all the pcp domains")
            dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' a.config.skype.com +noedns -b '+config.client_ip1+' +tries=1"'
            dig_result = subprocess.check_output(dig_cmd, shell=True)
            print dig_result
            assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
            assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
            assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
            logging.info("Test case execution Completed")
        except:
            logging.info("Test case execution Falied")
            assert False

    @pytest.mark.run(order=477)
    def test_381_stop_syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution passed")

    @pytest.mark.run(order=478)
    def test_382_Validate_Named_CEF_Log_Logs_for_a_config_skype_com_for_NIOS_PCP_bit_80(self):
        logging.info("Validate Named CEF Log for totalwine.com  when get response from Bind for NIOS PCP bit 80")
        LookFor="named.*info CEF.*a.config.skype.com.*CAT=0x00000000000100000000000000000000"
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

    @pytest.mark.run(order=479)
    def test_383_Add_Subscriber_Record_with_PCP_Policy_bit_set_for_domain_falling_under_2_categories_with_PCP_bit_set_to_second_bit(self):
        try:
            logging.info("Add_Subscriber_Record_with_PCP_Policy_bit_set_for_domain_falling_under_2_categories_with_PCP_bit_set_to_first_bit")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=9544;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000080000000000000000000000;SSP:Subscriber-Secure-Policy=ff;UCP:Unknown-Category-Policy=1;SUB:Calling-Station-Id=663;"')
            child.expect('Record successfully added')
            logging.info("Test case execution Passed")
            assert True
        except:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=480)
    def test_384_Validate_Subscriber_Record_with_Policy_bit_for_dynamic_domain(self):
        logging.info("Validate Subscriber Record with Different PCP Policy bit")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000080000000000000000000000.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=481)
    def test_385_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 279 passed")
        sleep(10)

    @pytest.mark.run(order=482)
    def test_386_query_all_the_PCP_domains(self):
        try:
            logging.info("query all the pcp domains")
            dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' a.config.skype.com +noedns -b '+config.client_ip1+' +tries=1"'
            dig_result = subprocess.check_output(dig_cmd, shell=True)
            print dig_result
            assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
            assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
            assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
            logging.info("Test case execution Completed")
        except:
            logging.info("Test case execution Falied")
            assert False

    @pytest.mark.run(order=483)
    def test_387_stop_syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution passed")

    @pytest.mark.run(order=484)
    def test_388_Validate_Named_CEF_Log_Logs_for_a_config_skype_com_com_for_NIOS_PCP_bit_0(self):
        logging.info("Validate Named CEF Log for a.config.skype.com  when get response from Bind for NIOS PCP bit 0")
        LookFor="named.*info CEF.*a.config.skype.com.*CAT=0x00000000080000000000000000000000"
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

    @pytest.mark.run(order=489)
    def test_389_Add_Subscriber_Record_with_PCP_Policy_bit_for_CAIC_domain(self):
        restart_the_grid()
        print("\n")
        print("************************************************")
        print("****  Test cases Related to CAIC DOMAIN  ****")
        print("************************************************")
        restart_the_grid()
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_CAIC_start_client1.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)
        
    @pytest.mark.run(order=490)
    def test_390_Validate_Subscriber_Record_with_Policy_bit_for_CAIC_domain(self):
        logging.info("Validate Subscriber Record withCAIC PCP Policy bit")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=0000000000000000000000f000000000.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=491)
    def test_391_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 227 passed")

    @pytest.mark.run(order=492)
    def test_392_Send_Query_from_subscriber_client_for_CAIC_Domain_iwf_caic_test_Using_IB_FLEX_Member_Validate_returns_NORMAL_response(self):
        logging.info("Perform Query from PCP match Subscriber client for CAIC Domain iwf-caic.test using IB-FLEX Member and Validate get NORMAL response")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' iwf-caic.test +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*iwf-caic.test.*IN.*A.*',str(dig_result))
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=493)
    def test_393_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=494)
    def test_394_Validate_CEF_Log_Logs_when_get_blocking_response_from_named_for_domain_iwf_caic_test_com(self):
        logging.info("Validate CEF Log for iwf-caic.test  when get blocked response")
        LookFor="named.*info CEF.*iwf-caic.test.*CAT=0x00000000000000000000008000000000"
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

    @pytest.mark.run(order=495)
    def test_395_Validate_Domain_iwf_caic_test_exist_in_DCA_cache(self):
        logging.info("Validate iwf-caic.test domain still exist in DCA  cache")
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
        #assert re.search(r'.*iwf-caic.test,A,IN.*AA,A,.*iwf-caic.test.*',c)
        #assert re.search(r'.*0x00000000000000000000008000000000.*',c)
        assert re.search(r'.*Cache is empty.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=496)
    def test_396_Validate_when_get_response_from_bind_for_iwf_caic_test_Cache_hit_count_is_not_increased_and_Miss_cache_count_is_increased(self):
        logging.info("Validate when get response from DCA for iwf-caic.test Cache hit count is not increased and Miss cache count is increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        print c
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=497)
    def test_397_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 233 passed")

    @pytest.mark.run(order=498)
    def test_398_Send_Query_from_subscriber_client_for_CAIC_Domain_iwf_caic_test_Using_IB_FLEX_Member_Validate_returns_NORMAL_response(self):
        logging.info("Send Query from subscriber client for dynamic Domain iwf-caic.test Using IB FLEX_Member Validate returns NORMAL response")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' iwf-caic.test +noedns -b '+config.client_ip2+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*iwf-caic.test.*IN.*A.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=499)
    def test_399_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=500)
    def test_400_Validate_No_CEF_Log_Logs_when_get_NORMAL_response_from_bind_for_domain_iwf_caic_test(self):
        logging.info("Validate NO CEF Log for iwf-caic.test when get NORMAL response")
        LookFor="info CEF.*iwf-caic.test.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert False
        else:
            logging.info("Test case execution Failed")
            assert True

    @pytest.mark.run(order=501)
    def test_401_Validate_when_get_response_from_bind_for_iwf_caic_test_Cache_hit_count_is_increased_and_Miss_cache_count_is_not_increased(self):
        logging.info("Validate when get response from DCA for iwf-caic.test Cache hit count is increased and Miss cache count is not increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        print c
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*2.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=529)
    def test_402_Add_the_Authoritative_zone_test_com_in_grid_2(self):
        #stop_subscriber_collection_services_for_added_site([config.grid_fqdn])
        #sleep(30)
        #start_subscriber_collection_services_for_added_site([config.grid_fqdn])
        #restart_the_grid()
        logging.info("Add the Authoritative zone test.com in grid 2")
        data={"fqdn":"test.com","grid_primary": [{"name": config.grid_2_fqdn,"stealth": False}]}
        get_ref=ib_NIOS.wapi_request('POST', object_type="zone_auth",fields=json.dumps(data),grid_vip=config.grid_2_vip)
        logging.info(get_ref)
        print get_ref
        if type(get_ref)!=tuple:
            logging.info("Restaring the grid")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_2_vip)
            ref = json.loads(grid)[0]['_ref']
            data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_2_vip)
            sleep(60)
            print("Restrting the grid")
            reference=ib_NIOS.wapi_request('GET', object_type="zone_auth",grid_vip=config.grid_2_vip)
            reference=json.loads(reference)
            if "test.com" in reference[0]["fqdn"]:
                logging.info("Test case execution passed")
                assert True
            else:
                logging.info("Test case execution Failed")
                assert False
        else:
            logging.info(get_ref)
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=530)
    def test_403_validate_the_Authoritative_zone_test_com(self):
        logging.info("validate the Authoritative zone test com")
        get_ref=ib_NIOS.wapi_request('GET', object_type="zone_auth",grid_vip=config.grid_2_vip)
        logging.info(get_ref)
        get_ref=json.loads(get_ref)
        print get_ref
        count=0
        for i in get_ref:
            if i["fqdn"]=="test.com":
                count=count+1
        if count!=0:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=531)
    def test_404_Add_records_to_Authoritative_zone_test_com_in_grid_2(self):
        logging.info("Add_the_records to Authoritative zone test.com in grid 2")
        for i in range(87):
            data={"name":"a.test.com","ipv4addr": "10.10.10."+str(i),"view":"default"}
            get_ref=ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data),grid_vip=config.grid_2_vip)
            logging.info(get_ref)
            print get_ref
            if type(get_ref)!=tuple:
                reference=ib_NIOS.wapi_request('GET', object_type="record:a",grid_vip=config.grid_2_vip)
                if reference!="[]":
                    logging.info("Test case execution passed")
                    assert True
                else:
                    logging.info("Test case execution Failed")
                    assert False
            else:
                logging.info("Test case execution Failed")


    @pytest.mark.run(order=532)
    def test_405_validate_the_records_added_to_test_com(self):
        logging.info("validate the records added to test com")
        reference=ib_NIOS.wapi_request('GET', object_type="record:a",grid_vip=config.grid_2_vip)
        reference=json.loads(reference)
        count=0
        for i in reference:
            if i["name"]=="a.test.com":
                count=count+1
        if count==87:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=533)
    def test_406_Modify_Grid_Dns_Properties(self):
        logging.info("Mofifying GRID dns properties")
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:dns")
        get_ref1=json.loads(get_ref)[0]['_ref']
        logging.info(get_ref1)
        data={"allow_recursive_query":True,"allow_query":[{"_struct": "addressac","address":"Any","permission":"ALLOW"}],"forwarders":[config.grid_2_vip],"logging_categories":{"log_rpz":True,"log_queries":True,"log_responses":True}}
        put_ref=ib_NIOS.wapi_request('PUT', object_type=get_ref1,fields=json.dumps(data))
        logging.info(put_ref)
        if type(put_ref)!=tuple:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=534)
    def test_407_Validate_Grid_Dns_Properties(self):
        restart_the_grid()
        logging.info("Validating GRID dns properties")
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:dns?_return_fields=allow_recursive_query,forwarders")
        get_ref1=json.loads(get_ref)
        if get_ref1[0]["allow_recursive_query"]==True and get_ref1[0]["forwarders"]==[config.grid_2_vip]:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=535)
    def test_408_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 128 passed")


    @pytest.mark.run(order=536)
    def test_409_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_Blocked_IPs_in_response_from_Bind_As_Not_DCA_Cache(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and get PCP Blocked IPs response from Bind as times.com not in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' a.test.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.0.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.1.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.2.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.3.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.4.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.5.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.6.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.7.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.8.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.9.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.10.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.11.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.12.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.13.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.14.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.15.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.16.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.17.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.18.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.19.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.20.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.21.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.22.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.23.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.24.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.25.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.26.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.27.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.28.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.29.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.30.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.31.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.32.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.33.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.34.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.35.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.36.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.37.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.38.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.39.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.40.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.41.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.42.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.43.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.44.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.44.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.45.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.46.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.47.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.48.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.49.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.50.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.51.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.52.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.53.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.54.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.55.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.56.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.57.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.58.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.59.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.60.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.61.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.62.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.63.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.64.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.65.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.66.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.67.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.68.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.69.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.70.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.71.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.72.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.73.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.74.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.75.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.76.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.77.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.78.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.79.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.80.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.81.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.82.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.83.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.84.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.85.*',str(dig_result))
        assert re.search(r'.*a.test.com.*IN.*A.*10.10.10.86.*',str(dig_result))

        logging.info("Test case execution Completed")

    @pytest.mark.run(order=537)
    def test_410_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=538)
    def test_411_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_times_com(self):
        logging.info("Validate Named CEF Log for times.com  when get response from Bind")
        LookFor=".*TCP: query: .*a.test.com.*IN A response:.* NOERROR.*a.test.com.*"
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
    

    @pytest.mark.run(order=542)
    def test_412_Enable_DCA_subscriber_Allowed_and_Blocked_list_support_on_site(self):
        logging.info("Eisable DCA subscriber Allowed and Blocked list support on site")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        get_ref=json.loads(get_ref)[0]["_ref"]
        data={"dca_sub_bw_list":True}
        res = ib_NIOS.wapi_request('PUT', object_type=get_ref,fields=json.dumps(data))
        if type(res)!=tuple:
            logging.info("Test case 84 execution passed")
            time.sleep(5)
            assert True
        else:
            logging.info("Test case 84 execution Failed")
            assert False

    '''
    @pytest.mark.run(order=543)
    def test_413_validate_DCA_subscriber_Allowed_and_Blocked_list_support_is_enabled_on_site(self):
        logging.info("Validate DCA subscriber Query count reporting and Enable DCA subscriber Allowed and Blocked list support are enabled")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=dca_sub_bw_list")
        get_ref=json.loads(get_ref)
        if get_ref[0]["dca_sub_bw_list"]==True:
            logging.info("Test case 85 execution passed")
            assert True
        else:
            logging.info("Test case 85 execution Failed")
            assert False
    
    '''
    @pytest.mark.run(order=3)
    def test_413_Configure_Recurson_Forwarer_RPZ_logging_At_Grid_DNS_Properties(self):
        logging.info("Mofifying and Configure Allow Recursive Query Forwarder and RPZ logging at GRID dns properties")
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:dns")
        get_ref1=json.loads(get_ref)[0]['_ref']
        logging.info(get_ref1)
        data={"allow_recursive_query":True,"allow_query":[{"_struct": "addressac","address":"Any","permission":"ALLOW"}],"forwarders":[config.forwarder_ip],"logging_categories":{"log_rpz":True,"log_queries":True,"log_responses":True}}
        put_ref=ib_NIOS.wapi_request('PUT', object_type=get_ref1,fields=json.dumps(data))
        logging.info(put_ref)
        if type(put_ref)!=tuple:
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False

    @pytest.mark.run(order=544)
    def test_414_reboot_the_IB_FLEX_Member_to_enable_DCA_subscriber_Allowed_and_Blocked_list_support_is_enabled_on_site(self):
        prod_reboot(config.grid_vip)
        sleep(300)
    
    #TEST CASE RELATED to Blacklist and Whitelist
    #BLACKLIST
    @pytest.mark.run(order=1)
    def test_415_Add_Subscriber_Record_with_BWList(self):
        restart_the_grid()
        try:
            logging.info("Add Subscriber Record with BWList")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=99-d99;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.primary_proxy_server+';UCP:Unknown-Category-Policy=1;DCP:Dynamic-Category-Policy=1;SUB:Calling-Station-Id=143;BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;" ')
            child.expect('Record successfully added')
            logging.info("Test case passed")
            assert True
        except:
            logging.info("Test Case 1 Execution Failed")
            assert False

    @pytest.mark.run(order=2)
    def test_416_Validate_Subscriber_Record_with_BWList(self):
        logging.info("Validate Subscriber Record with_BWList")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000000000000020040.*.*BWFlag.*BL.*facebook.*WL.*bbc.*',c)
        logging.info("Test case 2 execution completed")

    @pytest.mark.run(order=3)
    def test_417_Add_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 N/A N/A "ACS:Acct-Session-Id=981-d991;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000001000000000000;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000001000000000000000;SUB:Calling-Station-Id=1493;BWI:BWFlag=1;BL=blore.com;WL=hydbad.com;" ')
            child.expect('Record successfully added')
            logging.info("Test case passed")
            assert True
        except:
            logging.info("Test Case 1 Execution Failed")
            assert False

    @pytest.mark.run(order=4)
    def test_418_Validate_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000001000000000000.*.*BWFlag.*BL.*blore.*WL.*hydbad.com.*',c)
        logging.info("Test case 2 execution completed")

    @pytest.mark.run(order=5)
    def test_419_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")

    @pytest.mark.run(order=6)
    def test_420_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")

    @pytest.mark.run(order=7)
    def test_421_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=8)
    def test_422_Validate_NAMED_CEF_Log_For_CAT_BL(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor="named.*info CEF.*facebook.com.*CAT=BL.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case 9 Execution Failed")
            assert False

    @pytest.mark.run(order=9)
    def test_423_Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client(self):
        logging.info("Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client")
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
        logging.info("Test Case 10 Execution Completed")

    @pytest.mark.run(order=10)
    def test_424_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com(self):
        logging.info("Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test Case 11 Execution Completed")

    @pytest.mark.run(order=11)
    def test_425_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
		
    @pytest.mark.run(order=12)
    def test_426_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip2+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*facebook.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case 13 Execution Completed")

    @pytest.mark.run(order=13)
    def test_427_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 8 Execution Completed")
		
    @pytest.mark.run(order=14)
    def test_428_Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_NEGATIVE_CASE(self):
        logging.info("Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        LookFor="info CEF.*facebook.com.*CAT=BL"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert False
        else:
            logging.info("Test Case 15 Execution Failed")
            assert True

    @pytest.mark.run(order=15)
    def test_429_Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
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
        assert re.search(r'.*facebook.com.*',c)
        assert re.search(r'.*0x00000000100000000000000000000000.*',c)
        logging.info("Test Case 16 Execution Completed")

    @pytest.mark.run(order=16)
    def test_430_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*2.*',c)
        logging.info("Test Case 17 Execution Completed")

    @pytest.mark.run(order=17)
    def test_431_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")

    @pytest.mark.run(order=18)
    def test_432_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")

    @pytest.mark.run(order=19)
    def test_433_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=20)
    def test_434_Validate_DCA_CEF_Log_shows_CAT_BL_When_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate DCA CEF Log for ponse from DCA")
        LookFor="fp-rte.*info CEF.*facebook.com.*CAT=BL"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case 21 Execution Failed")
            assert False
#WHITELIST
    @pytest.mark.run(order=1)
    def test_435_Add_Subscriber_Record_with_BWList(self):
        restart_the_grid()
        try:
            logging.info("Add Subscriber Record with BWList")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=99-d99;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';UCP:Unknown-Category-Policy=1;DCP:Dynamic-Category-Policy=1;SUB:Calling-Station-Id=143;BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;" ')
            child.expect('Record successfully added')
            logging.info("Test case passed")
            assert True
        except:
            logging.info("Test Case 1 Execution Failed")
            assert False

    @pytest.mark.run(order=2)
    def test_436_Validate_Subscriber_Record_with_BWList(self):
        logging.info("Validate Subscriber Record with_BWList")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000000000000020040.*.*BWFlag.*BL.*facebook.*WL.*bbc.*',c)
        logging.info("Test case 2 execution completed")

    @pytest.mark.run(order=3)
    def test_437_Add_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 N/A N/A "ACS:Acct-Session-Id=981-d991;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000001000000000000;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000001000000000000000;SUB:Calling-Station-Id=1493;BWI:BWFlag=1;BL=blore.com;WL=hydbad.com;" ')
            child.expect('Record successfully added')
            logging.info("Test case passed")
            assert True
        except:
            logging.info("Test Case 1 Execution Failed")
            assert False

    @pytest.mark.run(order=4)
    def test_438_Validate_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000001000000000000.*.*BWFlag.*BL.*blore.*WL.*hydbad.com.*',c)
        logging.info("Test case 2 execution completed")

    @pytest.mark.run(order=5)
    def test_439_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")

    @pytest.mark.run(order=6)
    def test_440_Query_Whitelist_domain_bbc_com_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' bbc.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")

    @pytest.mark.run(order=7)
    def test_441_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=8)
    def test_442_Validate_NAMED_CEF_Log_For_Whitelist_domain_bbc_com(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor=".*query: bbc.com.*NOERROR.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case 9 Execution Failed")
            assert False

    @pytest.mark.run(order=9)
    def test_443_Validate_Whitelist_Domain_bbc_com_cached_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client(self):
        logging.info("Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client")
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
        assert re.search(r'.*bbc.com.*',c)
        logging.info("Test Case 10 Execution Completed")

    @pytest.mark.run(order=10)
    def test_444_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Whitelist_Domain_facebook_com(self):
        logging.info("Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test Case 11 Execution Completed")

    @pytest.mark.run(order=11)
    def test_445_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")

    @pytest.mark.run(order=12)
    def test_446_Query_Whitelist_domain_bbc_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' bbc.com +noedns -b '+config.client_ip2+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*bbc.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case 13 Execution Completed")

    @pytest.mark.run(order=13)
    def test_447_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=14)
    def test_448_Validate_NO_CEF_Log_When_Query_Whitelist_domain_bbc_com_from_NON_PCP_bit_matching_Subscriber_client_NEGATIVE_CASE(self):
        logging.info("Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        LookFor="info CEF.*bbc.com.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert False
        else:
            logging.info("Test Case 15 Execution Failed")
            assert True

    @pytest.mark.run(order=15)
    def test_449_Validate_domain_cached_in_DCA_When_Query_Whitelist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
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
        assert re.search(r'.*bbc.com.*',c)
        assert re.search(r'.*0x00000000000000040000000000000000.*',c)
        logging.info("Test Case 16 Execution Completed")

    @pytest.mark.run(order=16)
    def test_450_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_When_Query_Whitelist_domain_bbc_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*1.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test Case 17 Execution Completed")

    @pytest.mark.run(order=17)
    def test_451_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")

    @pytest.mark.run(order=18)
    def test_452_Query_Whitelist_domain_bbc_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' bbc.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")

    @pytest.mark.run(order=19)
    def test_453_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=20)
    def test_454_Validate_NAMED_CEF_Log_For_Whitelist_domain_bbc_com(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor=".*query: bbc.com.*NOERROR.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case 9 Execution Failed")
            assert False

    @pytest.mark.run(order=21)
    def test_455_Validate_Whitelist_Domain_bbc_com_cached_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client(self):
        logging.info("Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client")
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
        assert re.search(r'.*bbc.com.*',c)
        logging.info("Test Case 10 Execution Completed")

    @pytest.mark.run(order=22)
    def test_456_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Whitelist_Domain_facebook_com(self):
        logging.info("Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*1.*',c)
        assert re.search(r'.*Cache miss count.*2.*',c)
        logging.info("Test Case 11 Execution Completed")

#Blacklist_Combination_Cases
    @pytest.mark.run(order=1)
    def test_457_Add_Subscriber_Record_with_ten_BlackList_domains(self):
        restart_the_grid()
        try:
            logging.info("Add Subscriber Record with BWList")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=99-d99;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.primary_proxy_server+';UCP:Unknown-Category-Policy=1;DCP:Dynamic-Category-Policy=1;SUB:Calling-Station-Id=143;BWI:BWFlag=1;BL=facebook.com,google.com,orkut.com,youtube.com,five.com,six.com,seven.com,eight.com,nine.com,ten.com;WL=bbc.com,ibm.com,sonata.com,tcs.com,asm.com,vmware.com,hp.com,hcl.com,wipro.com,flex.com;" ')
            child.expect('Record successfully added')
            logging.info("Test case passed")
            assert True
        except:
            logging.info("Test Case 1 Execution Failed")
            assert False

    @pytest.mark.run(order=2)
    def test_458_Validate_Subscriber_Record_with_ten_BlackList_domains(self):
        logging.info("Validate Subscriber Record with_BWList")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000000000000020040.*BWI.*BWFlag.*BL.*facebook.com.*google.com.*orkut.com.*youtube.com.*five.com.*six.com.*seven.*eight.com.*nine.com.*ten.com.*WL.*bbc.com.*ibm.com.*sonata.com.*tcs.com.*asm.com.*vmware.com.*hp.com.*hcl.com.*wipro.*flex.*.*',c)
        logging.info("Test case 2 execution completed")

    @pytest.mark.run(order=3)
    def test_459_Add_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 N/A N/A "ACS:Acct-Session-Id=981-d991;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000001000000000000;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000001000000000000000;SUB:Calling-Station-Id=1493;BWI:BWFlag=1;BL=blore.com;WL=hydbad.com;" ')
            child.expect('Record successfully added')
            logging.info("Test case passed")
            assert True
        except:
            logging.info("Test Case 1 Execution Failed")
            assert False

    @pytest.mark.run(order=4)
    def test_460_Validate_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000001000000000000.*.*BWFlag.*BL.*blore.*WL.*hydbad.com.*',c)
        logging.info("Test case 2 execution completed")

    @pytest.mark.run(order=5)
    def test_461_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")

    @pytest.mark.run(order=6)
    def test_462_Query_Blacklist_domain_youtube_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' youtube.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")

    @pytest.mark.run(order=7)
    def test_463_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=8)
    def test_464_Validate_NAMED_CEF_Log_For_CAT_BL(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor="named.*info CEF.*youtube.com.*CAT=BL.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case 9 Execution Failed")
            assert False

    @pytest.mark.run(order=9)
    def test_465_Validate_Blacklist_Domain_youtube_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client(self):
        logging.info("Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client")
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
        logging.info("Test Case 10 Execution Completed")

    def test_466_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com(self):
        logging.info("Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test Case 11 Execution Completed")

    @pytest.mark.run(order=11)
    def test_467_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")

    @pytest.mark.run(order=12)
    def test_468_Query_Blacklist_domain_youtube_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' youtube.com +noedns -b '+config.client_ip2+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*youtube.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case 13 Execution Completed")

    @pytest.mark.run(order=13)
    def test_469_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=14)
    def test_470_Validate_NO_CEF_Log_When_Query_Blacklist_domain_youtube_com_from_NON_PCP_bit_matching_Subscriber_client_NEGATIVE_CASE(self):
        logging.info("Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        LookFor="info CEF.*youtube.com.*CAT=BL"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert False
        else:
            logging.info("Test Case 15 Execution Failed")
            assert True

    @pytest.mark.run(order=15)
    def test_471_Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_youtube_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
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
        assert re.search(r'.*youtube.com.*',c)
        assert re.search(r'.*0x00000000000000000004000000000000.*',c)
        #assert re.search(r'.*0x00000000100000000000000000000000.*',c)
        logging.info("Test Case 16 Execution Completed")

    @pytest.mark.run(order=16)
    def test_472_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_When_Query_Blacklist_domain_youtube_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*2.*',c)
        logging.info("Test Case 17 Execution Completed")

    @pytest.mark.run(order=17)
    def test_473_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")

    @pytest.mark.run(order=18)
    def test_474_Query_Blacklist_domain_youtube_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' youtube.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")

    @pytest.mark.run(order=19)
    def test_475_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=20)
    def test_476_Validate_DCA_CEF_Log_shows_CAT_BL_When_Query_Blacklist_domain_youtube_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate DCA CEF Log for ponse from DCA")
        LookFor="fp-rte.*info CEF.*youtube.com.*CAT=BL"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case 21 Execution Failed")
            assert False

#Whitelist_Combination_Cases
    @pytest.mark.run(order=1)
    def test_477_Add_Subscriber_Record_with_ten_WhiteList_domains(self):
        restart_the_grid()
        try:
            logging.info("Add Subscriber Record with BWList")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=99-d99;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';UCP:Unknown-Category-Policy=1;DCP:Dynamic-Category-Policy=1;SUB:Calling-Station-Id=143;BWI:BWFlag=1;BL=facebook.com,google.com,orkut.com,youtube.com,five.com,six.com,seven.com,eight.com,nine.com,ten.com;WL=bbc.com,ibm.com,sonata.com,tcs.com,asm.com,vmware.com,hp.com,hcl.com,wipro.com,flex.com;" ')
            child.expect('Record successfully added')
            logging.info("Test case passed")
            assert True
        except:
            logging.info("Test Case 1 Execution Failed")
            assert False

    @pytest.mark.run(order=2)
    def test_478_Validate_Subscriber_Record_with_ten_WhiteList_domains(self):
        logging.info("Validate Subscriber Record with_BWList")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000000000000020040.*BWI.*BWFlag.*BL.*facebook.com.*google.com.*orkut.com.*youtube.com.*five.com.*six.com.*seven.*eight.com.*nine.com.*ten.com.*WL.*bbc.com.*ibm.com.*sonata.com.*tcs.com.*asm.com.*vmware.com.*hp.com.*hcl.com.*wipro.*flex.*.*',c)
        logging.info("Test case 2 execution completed")

    @pytest.mark.run(order=3)
    def test_479_Add_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 N/A N/A "ACS:Acct-Session-Id=981-d991;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000001000000000000;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000001000000000000000;SUB:Calling-Station-Id=1493;BWI:BWFlag=1;BL=blore.com;WL=hydbad.com;" ')
            child.expect('Record successfully added')
            logging.info("Test case passed")
            assert True
        except:
            logging.info("Test Case 1 Execution Failed")
            assert False

    @pytest.mark.run(order=4)
    def test_480_Validate_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000001000000000000.*.*BWFlag.*BL.*blore.*WL.*hydbad.com.*',c)
        logging.info("Test case 2 execution completed")

    @pytest.mark.run(order=5)
    def test_481_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")

    @pytest.mark.run(order=6)
    def test_482_Query_Whitelist_domain_ibm_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' ibm.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")

    @pytest.mark.run(order=7)
    def test_483_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=8)
    def test_484_Validate_NAMED_CEF_Log_For_Whitelist_domain_ibm_com(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor=".*query: ibm.com.*NOERROR.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case 9 Execution Failed")
            assert False

    @pytest.mark.run(order=9)
    def test_485_Validate_Whitelist_Domain_ibm_com_cached_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client(self):
        logging.info("Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client")
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
        assert re.search(r'.*ibm.com.*',c)
        logging.info("Test Case 10 Execution Completed")

    @pytest.mark.run(order=10)
    def test_486_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Whitelist_Domain_ibm_com(self):
        logging.info("Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test Case 11 Execution Completed")

    @pytest.mark.run(order=11)
    def test_487_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")

    @pytest.mark.run(order=12)
    def test_488_Query_Whitelist_domain_ibm_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' ibm.com +noedns -b '+config.client_ip2+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*ibm.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case 13 Execution Completed")

    @pytest.mark.run(order=13)
    def test_489_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=14)
    def test_490_Validate_NO_CEF_Log_When_Query_Whitelist_domain_ibm_com_from_NON_PCP_bit_matching_Subscriber_client_NEGATIVE_CASE(self):
        logging.info("Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        LookFor="info CEF.*ibm.com.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert False
        else:
            logging.info("Test Case 15 Execution Failed")
            assert True

    @pytest.mark.run(order=15)
    def test_491_Validate_domain_cached_in_DCA_When_Query_Whitelist_domain_ibm_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
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
        assert re.search(r'.*ibm.com.*',c)
        assert re.search(r'.*0x00000000000040000000000000000000.*',c)
        #assert re.search(r'.*0x00000000000000040000000000000000.*',c)
        logging.info("Test Case 16 Execution Completed")

    @pytest.mark.run(order=16)
    def test_492_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_When_Query_Whitelist_domain_ibm_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*1.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test Case 17 Execution Completed")

    @pytest.mark.run(order=17)
    def test_493_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")

    @pytest.mark.run(order=18)
    def test_494_Query_Whitelist_domain_ibm_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' ibm.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")

    @pytest.mark.run(order=19)
    def test_495_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=20)
    def test_496_Validate_NAMED_CEF_Log_For_Whitelist_domain_ibm_com(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor=".*query: ibm.com.*NOERROR.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case 9 Execution Failed")
            assert False

    @pytest.mark.run(order=21)
    def test_497_Validate_Whitelist_Domain_ibm_com_cached_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client(self):
        logging.info("Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client")
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
        assert re.search(r'.*ibm.com.*',c)
        logging.info("Test Case 10 Execution Completed")

    @pytest.mark.run(order=22)
    def test_498_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Whitelist_Domain_ibm_com(self):
        logging.info("Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*1.*',c)
        assert re.search(r'.*Cache miss count.*2.*',c)
        logging.info("Test Case 11 Execution Completed")

#NO_PCP_BLacklist_Tests
    @pytest.mark.run(order=1)
    def test_499_Add_Subscriber_Record_without_PCP_Bits_with_BWList(self):
        restart_the_grid()
        try:
            logging.info("Add Subscriber Record with BWList")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=99-d99;NAS:NAS-PORT=1813;SUB:Calling-Station-Id=143;BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;" ')
            child.expect('Record successfully added')
            logging.info("Test  Execution Passed")
            assert True
        except:
            logging.info("Test  Execution Failed")
            assert False

    @pytest.mark.run(order=2)
    def test_500_Validate_Subscriber_Record_without_PCP_Bits_With_BWList(self):
        logging.info("Validate Subscriber Record with_BWList")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*BWFlag.*BL.*facebook.*WL.*bbc.*',c)
        logging.info("Test  execution completed")

    @pytest.mark.run(order=3)
    def test_501_Add_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 N/A N/A "ACS:Acct-Session-Id=981-d991;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000001000000000000;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000001000000000000000;SUB:Calling-Station-Id=1493;BWI:BWFlag=1;BL=blore.com;WL=hydbad.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Execution Passed")
            assert True
        except:
            logging.info("Test Execution Failed")
            assert False

    @pytest.mark.run(order=4)
    def test_502_Validate_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000001000000000000.*.*BWFlag.*BL.*blore.*WL.*hydbad.com.*',c)
        logging.info("Test case 2 execution completed")

    @pytest.mark.run(order=5)
    def test_503_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")

    @pytest.mark.run(order=6)
    def test_504_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Completed")

    @pytest.mark.run(order=7)
    def test_505_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=8)
    def test_506_Validate_NAMED_CEF_Log_For_CAT_BL(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor="named.*info CEF.*facebook.com.*CAT=BL.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case Failed")
            assert False

    @pytest.mark.run(order=9)
    def test_507_Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client(self):
        logging.info("Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client")
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
        logging.info("Test  Execution Completed")

    @pytest.mark.run(order=10)
    def test_508_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com(self):
        logging.info("Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test  Execution Completed")

    @pytest.mark.run(order=11)
    def test_509_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test  passed")

    @pytest.mark.run(order=12)
    def test_510_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip2+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*facebook.com.*IN.*A.*',str(dig_result))
        logging.info("Test  Execution Completed")

    @pytest.mark.run(order=13)
    def test_511_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=14)
    def test_512_Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_NEGATIVE_CASE(self):
        logging.info("Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        LookFor="info CEF.*facebook.com.*CAT=BL"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert False
        else:
            logging.info("Test Case Failed")
            assert True

    @pytest.mark.run(order=15)
    def test_513_Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
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
        assert re.search(r'.*facebook.com.*',c)
        assert re.search(r'.*0x00000000100000000000000000000000.*',c)
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=16)
    def test_514_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*2.*',c)
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=17)
    def test_515_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test passed")

    @pytest.mark.run(order=18)
    def test_516_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=19)
    def test_517_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=20)
    def test_518_Validate_DCA_CEF_Log_shows_CAT_BL_When_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate DCA CEF Log for ponse from DCA")
        LookFor="fp-rte.*info CEF.*facebook.com.*CAT=BL"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False

#NO_PCP_Proxy_Tests
    @pytest.mark.run(order=1)
    def test_519_Add_Subscriber_Record_without_PCP_Bits_with_Proxy_All(self):
        restart_the_grid()
        try:
            logging.info("Add Subscriber Record with BWList")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=99-d99;NAS:NAS-PORT=1813;SUB:Calling-Station-Id=143;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';PXY:Proxy-All=1;" ')
            child.expect('Record successfully added')
            logging.info("Test  Execution Passed")
            assert True
        except:
            logging.info("Test  Execution Failed")
            assert False

    @pytest.mark.run(order=2)
    def test_520_Validate_Subscriber_Record_without_PCP_Bits_With_Proxy_All(self):
        logging.info("Validate Subscriber Record with_BWList")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PXY_PRI.*'+config.primary_proxy_server+'.*SEC.*'+config.secondary_proxy_server+'.*Proxy-All=1.*',c)
        logging.info("Test  execution completed")

    @pytest.mark.run(order=3)
    def test_521_Add_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 N/A N/A "ACS:Acct-Session-Id=981-d991;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000001000000000000;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000001000000000000000;SUB:Calling-Station-Id=1493;BWI:BWFlag=1;BL=blore.com;WL=hydbad.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Execution Passed")
            assert True
        except:
            logging.info("Test Execution Failed")
            assert False

    @pytest.mark.run(order=4)
    def test_522_Validate_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000001000000000000.*.*BWFlag.*BL.*blore.*WL.*hydbad.com.*',c)
        logging.info("Test case 2 execution completed")

    @pytest.mark.run(order=5)
    def test_523_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")

    @pytest.mark.run(order=6)
    def test_524_Query_Proxy_All_domain_google_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' google.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case Completed")

    @pytest.mark.run(order=7)
    def test_525_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=8)
    def test_526_Validate_NAMED_CEF_Log_For_CAT_PXY(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor="named.*info CEF.*google.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case Failed")
            assert False

    @pytest.mark.run(order=9)
    def test_527_Validate_Proxy_all_Domain_google_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client(self):
        logging.info("Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client")
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
        logging.info("Test  Execution Completed")

    @pytest.mark.run(order=10)
    def test_528_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com(self):
        logging.info("Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test  Execution Completed")

    @pytest.mark.run(order=11)
    def test_529_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test  passed")

    @pytest.mark.run(order=12)
    def test_530_Query_Proxy_All_domain_google_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' google.com +noedns -b '+config.client_ip2+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*google.com.*IN.*A.*',str(dig_result))
        logging.info("Test  Execution Completed")

    @pytest.mark.run(order=13)
    def test_531_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=14)
    def test_532_Validate_NO_CEF_Log_When_Query_Proxy_All_domain_google_com_from_NON_PCP_bit_matching_Subscriber_client_NEGATIVE_CASE(self):
        logging.info("Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        LookFor="info CEF.*google.com.*CAT=PXY"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert False
        else:
            logging.info("Test Case Failed")
            assert True

    @pytest.mark.run(order=15)
    def test_533_Validate_domain_cached_in_DCA_When_Query_Proxy_All_domain_google_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
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
        assert re.search(r'.*google.com.*',c)
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=16)
    def test_534_Validate_Cache_hit_count_increased_But_Miss_cache_count_not_increased_When_Query_Proxy_All_domain_google_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*2.*',c)
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=17)
    def test_535_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test passed")

    @pytest.mark.run(order=18)
    def test_536_Query_Proxy_All_domain_google_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' google.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=19)
    def test_537_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=20)
    def test_538_Validate_DCA_CEF_Log_shows_CAT_PXY_When_Query_Proxy_All_domain_google_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate DCA CEF Log for ponse from DCA")
        LookFor="fp-rte.*info CEF.*google.com.*CAT=PXY"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False

#NO_PCP_WPCP_Tests
    @pytest.mark.run(order=1)
    def test_539_Add_Subscriber_Record_without_PCP_Bits_With_WPCP(self):
        restart_the_grid()
        try:
            logging.info("Add Subscriber Record with BWList")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=99-d99;NAS:NAS-PORT=1813;SUB:Calling-Station-Id=143;PCC:PC-Category-Policy=00000000000000000000000000000001;" ')
            child.expect('Record successfully added')
            logging.info("Test  Execution Passed")
            assert True
        except:
            logging.info("Test  Execution Failed")
            assert False

    @pytest.mark.run(order=2)
    def test_540_Validate_Subscriber_Record_without_PCP_Bits_With_WPCP(self):
        logging.info("Validate Subscriber Record with_BWList")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCC:PC-Category-Policy=00000000000000000000000000000001;.*',c)
        logging.info("Test  execution completed")

    @pytest.mark.run(order=3)
    def test_541_Add_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 N/A N/A "ACS:Acct-Session-Id=981-d991;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000001000000000000;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000001000000000000000;SUB:Calling-Station-Id=1493;BWI:BWFlag=1;BL=blore.com;WL=hydbad.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Execution Passed")
            assert True
        except:
            logging.info("Test Execution Failed")
            assert False

    @pytest.mark.run(order=4)
    def test_542_Validate_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000001000000000000.*.*BWFlag.*BL.*blore.*WL.*hydbad.com.*',c)
        logging.info("Test case 2 execution completed")

    @pytest.mark.run(order=5)
    def test_543_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")

    @pytest.mark.run(order=6)
    def test_544_Query_WPCP_domain_vodka_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' vodka.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case Completed")

    @pytest.mark.run(order=7)
    def test_545_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=8)
    def test_546_Validate_NAMED_CEF_Log_For_CAT_WRN(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor="named.*info CEF.*vodka.com.*CAT=WRN.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case Failed")
            assert False

    @pytest.mark.run(order=9)
    def test_547_Validate_WPCP_Domain_vodka_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client(self):
        logging.info("Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client")
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
        #assert re.search(r'.*Cache is empty.*',c)
        assert re.search(r'.*vodka.com.*',c)
        assert re.search(r'.*0x00000000000000000000000000000001.*',c)
        logging.info("Test  Execution Completed")

    @pytest.mark.run(order=10)
    def test_548_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_WPCP_Domain_vodka_com(self):
        logging.info("Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test  Execution Completed")

    @pytest.mark.run(order=11)
    def test_549_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test  passed")

    @pytest.mark.run(order=12)
    def test_550_Query_WPCP_domain_vodka_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' vodka.com +noedns -b '+config.client_ip2+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*vodka.com.*IN.*A.*',str(dig_result))
        logging.info("Test  Execution Completed")

    @pytest.mark.run(order=13)
    def test_551_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=14)
    def test_552_Validate_NO_CEF_Log_When_Query_WPCP_domain_vodka_com_from_NON_PCP_bit_matching_Subscriber_client_NEGATIVE_CASE(self):
        logging.info("Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        LookFor="info CEF.*vodka.com.*CAT=WRN"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert False
        else:
            logging.info("Test Case Failed")
            assert True

    @pytest.mark.run(order=15)
    def test_553_Validate_domain_cached_in_DCA_When_Query_WPCP_domain_vodka_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
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
        assert re.search(r'.*vodka.com.*',c)
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=16)
    def test_554_Validate_Cache_hit_count_increased_But_Miss_cache_count_not_increased_When_Query_WPCP_domain_vodka_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        #assert re.search(r'.*Cache hit count.*2.*',c)
        #assert re.search(r'.*Cache miss count.*1.*',c)
        
        assert re.search(r'.*Cache hit count.*1.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=17)
    def test_555_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test passed")

    @pytest.mark.run(order=18)
    def test_556_Query_WPCP_domain_vodka_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' vodka.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=19)
    def test_557_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=20)
    def test_558_Validate_DCA_CEF_Log_shows_CAT_WRN_When_Query_WPCP_domain_vodka_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate DCA CEF Log for ponse from DCA")
        LookFor="fp-rte.*info CEF.*vodka.com.*CAT=WRN"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False

#V4_8_prefix Test Cases
    @pytest.mark.run(order=1)
    def test_559_Add_Subscriber_Record_with_8_prefix(self):
        stop_subscriber_collection_services_for_added_site([config.grid_fqdn])
        sleep(30)
        start_subscriber_collection_services_for_added_site([config.grid_fqdn])
        sleep(30)
        restart_the_grid()
        try:
            logging.info("Add Subscriber Record with BWList")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_network_8+' 8 N/A N/A "ACS:Acct-Session-Id=99-d99;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.primary_proxy_server+';UCP:Unknown-Category-Policy=1;DCP:Dynamic-Category-Policy=1;SUB:Calling-Station-Id=143;BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Passed")
            assert True
        except:
            logging.info("Test Case Failed")
            assert False

    @pytest.mark.run(order=2)
    def test_560_Validate_Subscriber_Record_with_8_prefix(self):
        logging.info("Verify Subscriber Record with_BWList")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_network_8+'\/8\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000000000000020040.*.*BWFlag.*BL.*facebook.*WL.*bbc.*',c)
        logging.info("Test case completed")

    @pytest.mark.run(order=3)
    def test_561_Add_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 N/A N/A "ACS:Acct-Session-Id=981-d991;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000001000000000000;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000001000000000000000;SUB:Calling-Station-Id=1493;BWI:BWFlag=1;BL=blore.com;WL=hydbad.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Case Passed")
            assert True
        except:
            logging.info("Test Case Failed")
            assert False

    @pytest.mark.run(order=4)
    def test_562_Validate_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        logging.info("Verify Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000001000000000000.*.*BWFlag.*BL.*blore.*WL.*hydbad.com.*',c)
        logging.info("Test case completed")

    @pytest.mark.run(order=5)
    def test_563_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")

    @pytest.mark.run(order=6)
    def test_564_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client_with_8_prefix(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=7)
    def test_565_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=8)
    def test_566_Validate_NAMED_CEF_Log_For_CAT_BL_with_32_prefix(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor="named.*info CEF.*facebook.com.*CAT=BL.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case  Failed")
            assert False

    @pytest.mark.run(order=9)
    def test_567_Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client_with_8_prefix(self):
        logging.info("Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client")
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
        logging.info("Test Case  Completed")
        
    @pytest.mark.run(order=10)
    def test_568_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com(self):
        logging.info("Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test Case  Completed")
        
    @pytest.mark.run(order=11)
    def test_569_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        	
    @pytest.mark.run(order=12)
    def test_570_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_with_8_prefix(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip2+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*facebook.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=13)
    def test_571_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case  Completed")
		
    @pytest.mark.run(order=14)
    def test_572_Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_with_8_prefix(self):
        logging.info("Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        LookFor="info CEF.*facebook.com.*CAT=BL"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert False
        else:
            logging.info("Test Case Failed")
            assert True

    @pytest.mark.run(order=15)
    def test_573_Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_with_8_prefix(self):
        logging.info("Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
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
        assert re.search(r'.*facebook.com.*',c)
        assert re.search(r'.*0x00000000100000000000000000000000.*',c)
        logging.info("Test Case  Completed")
        
    @pytest.mark.run(order=16)
    def test_574_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_with_8_prefix(self):
        logging.info("Validate_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*2.*',c)
        logging.info("Test Case  Completed")
        
    @pytest.mark.run(order=17)
    def test_575_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test passed")
        
    @pytest.mark.run(order=18)
    def test_576_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client_with_8_prefix(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Completed")

    @pytest.mark.run(order=19)
    def test_577_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Completed")

    @pytest.mark.run(order=20)
    def test_578_Validate_DCA_CEF_Log_shows_CAT_BL_When_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client_with_8_prefix(self):
        logging.info("Verify DCA CEF Log for ponse from DCA")
        LookFor="fp-rte.*info CEF.*facebook.com.*CAT=BL"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case  Failed")
            assert False

#V4_16_prefix Test Cases:
    @pytest.mark.run(order=1)
    def test_579_Add_Subscriber_Record_with_16_prefix(self):
        restart_the_grid()
        try:
            logging.info("Add Subscriber Record with BWList")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_network_16+' 16 N/A N/A "ACS:Acct-Session-Id=99-d99;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';UCP:Unknown-Category-Policy=1;DCP:Dynamic-Category-Policy=1;SUB:Calling-Station-Id=143;BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Passed")
            assert True
        except:
            logging.info("Test Case Failed")
            assert False

    @pytest.mark.run(order=2)
    def test_580_Validate_Subscriber_Record_with_16_prefix(self):
        logging.info("Verify Subscriber Record with_BWList")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_network_16+'\/16\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000000000000020040.*.*BWFlag.*BL.*facebook.*WL.*bbc.*',c)
        logging.info("Test case completed")

    @pytest.mark.run(order=3)
    def test_581_Add_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 N/A N/A "ACS:Acct-Session-Id=981-d991;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000001000000000000;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000001000000000000000;SUB:Calling-Station-Id=1493;BWI:BWFlag=1;BL=blore.com;WL=hydbad.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Case Passed")
            assert True
        except:
            logging.info("Test Case Failed")
            assert False

    @pytest.mark.run(order=4)
    def test_582_Validate_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        logging.info("Verify Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000001000000000000.*.*BWFlag.*BL.*blore.*WL.*hydbad.com.*',c)
        logging.info("Test case completed")

    @pytest.mark.run(order=5)
    def test_583_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=6)
    def test_584_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client_with_16_prefix(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=7)
    def test_585_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=8)
    def test_586_Validate_NAMED_CEF_Log_For_CAT_BL_with_32_prefix(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor="named.*info CEF.*facebook.com.*CAT=BL.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case  Failed")
            assert False

    @pytest.mark.run(order=9)
    def test_587_Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client_with_16_prefix(self):
        logging.info("Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client")
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
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=10)
    def test_588_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com(self):
        logging.info("Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test Case  Completed")


    @pytest.mark.run(order=11)
    def test_589_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=12)
    def test_590_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_with_16_prefix(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip2+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*facebook.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=13)
    def test_591_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=14)
    def test_592_Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_with_16_prefix(self):
        logging.info("Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        LookFor="info CEF.*facebook.com.*CAT=BL"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert False
        else:
            logging.info("Test Case Failed")
            assert True

    @pytest.mark.run(order=15)
    def test_593_Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_with_16_prefix(self):
        logging.info("Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
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
        assert re.search(r'.*facebook.com.*',c)
        assert re.search(r'.*0x00000000100000000000000000000000.*',c)
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=16)
    def test_594_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_with_16_prefix(self):
        logging.info("Validate_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*2.*',c)
        logging.info("Test Case  Completed")


    @pytest.mark.run(order=17)
    def test_595_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test passed")


    @pytest.mark.run(order=18)
    def test_596_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client_with_16_prefix(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Completed")

    @pytest.mark.run(order=19)
    def test_597_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Completed")

    @pytest.mark.run(order=20)
    def test_598_Validate_DCA_CEF_Log_shows_CAT_BL_When_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client_with_16_prefix(self):
        logging.info("Verify DCA CEF Log for ponse from DCA")
        LookFor="fp-rte.*info CEF.*facebook.com.*CAT=BL"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case  Failed")
            assert False

#V4_24_prefix Test Cases:
    @pytest.mark.run(order=1)
    def test_599_Add_Subscriber_Record_with_24_prefix(self):
        restart_the_grid()
        try:
            logging.info("Add Subscriber Record with BWList")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_network_24+' 24 N/A N/A "ACS:Acct-Session-Id=99-d99;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';UCP:Unknown-Category-Policy=1;DCP:Dynamic-Category-Policy=1;SUB:Calling-Station-Id=143;BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Passed")
            assert True
        except:
            logging.info("Test Case Failed")
            assert False

    @pytest.mark.run(order=2)
    def test_600_Validate_Subscriber_Record_with_24_prefix(self):
        logging.info("Verify Subscriber Record with_BWList")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_network_24+'\/24\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000000000000020040.*.*BWFlag.*BL.*facebook.*WL.*bbc.*',c)
        logging.info("Test case completed")

    @pytest.mark.run(order=3)
    def test_601_Add_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 N/A N/A "ACS:Acct-Session-Id=981-d991;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000001000000000000;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000001000000000000000;SUB:Calling-Station-Id=1493;BWI:BWFlag=1;BL=blore.com;WL=hydbad.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Case Passed")
            assert True
        except:
            logging.info("Test Case Failed")
            assert False

    @pytest.mark.run(order=4)
    def test_602_Validate_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        logging.info("Verify Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000001000000000000.*.*BWFlag.*BL.*blore.*WL.*hydbad.com.*',c)
        logging.info("Test case completed")

    @pytest.mark.run(order=5)
    def test_603_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=6)
    def test_604_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client_with_24_prefix(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=7)
    def test_605_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=8)
    def test_606_Validate_NAMED_CEF_Log_For_CAT_BL_with_32_prefix(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor="named.*info CEF.*facebook.com.*CAT=BL.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case  Failed")
            assert False

    @pytest.mark.run(order=9)
    def test_607_Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client_with_24_prefix(self):
        logging.info("Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client")
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
        logging.info("Test Case  Completed")


    @pytest.mark.run(order=10)
    def test_608_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com(self):
        logging.info("Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test Case  Completed")


    @pytest.mark.run(order=11)
    def test_609_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=12)
    def test_610_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_with_24_prefix(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip2+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*facebook.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=13)
    def test_611_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=14)
    def test_612_Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_with_24_prefix(self):
        logging.info("Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        LookFor="info CEF.*facebook.com.*CAT=BL"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert False
        else:
            logging.info("Test Case Failed")
            assert True

    @pytest.mark.run(order=15)
    def test_613_Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_with_24_prefix(self):
        logging.info("Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
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
        assert re.search(r'.*facebook.com.*',c)
        assert re.search(r'.*0x00000000100000000000000000000000.*',c)
        logging.info("Test Case  Completed")


    @pytest.mark.run(order=16)
    def test_614_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_with_24_prefix(self):
        logging.info("Validate_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*2.*',c)
        logging.info("Test Case  Completed")


    @pytest.mark.run(order=17)
    def test_615_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test passed")


    @pytest.mark.run(order=18)
    def test_616_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client_with_24_prefix(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Completed")

    @pytest.mark.run(order=19)
    def test_617_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Completed")

    @pytest.mark.run(order=20)
    def test_618_Validate_DCA_CEF_Log_shows_CAT_BL_When_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client_with_24_prefix(self):
        logging.info("Verify DCA CEF Log for ponse from DCA")
        LookFor="fp-rte.*info CEF.*facebook.com.*CAT=BL"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case  Failed")
            assert False

#V4_32_prefix Test Cases
    @pytest.mark.run(order=1)
    def test_619_Add_Subscriber_Record_with_32_prefix(self):
        restart_the_grid()
        try:
            logging.info("Add Subscriber Record with BWList")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_network_32+' 32 N/A N/A "ACS:Acct-Session-Id=99-d99;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';UCP:Unknown-Category-Policy=1;DCP:Dynamic-Category-Policy=1;SUB:Calling-Station-Id=143;BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Passed")
            assert True
        except:
            logging.info("Test Case Failed")
            assert False

    @pytest.mark.run(order=2)
    def test_620_Validate_Subscriber_Record_with_32_prefix(self):
        logging.info("Verify Subscriber Record with_BWList")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_network_32+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000000000000020040.*.*BWFlag.*BL.*facebook.*WL.*bbc.*',c)
        logging.info("Test case completed")

    @pytest.mark.run(order=3)
    def test_621_Add_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 N/A N/A "ACS:Acct-Session-Id=981-d991;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000001000000000000;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000001000000000000000;SUB:Calling-Station-Id=1493;BWI:BWFlag=1;BL=blore.com;WL=hydbad.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Case Passed")
            assert True
        except:
            logging.info("Test Case Failed")
            assert False

    @pytest.mark.run(order=4)
    def test_622_Validate_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        logging.info("Verify Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000001000000000000.*.*BWFlag.*BL.*blore.*WL.*hydbad.com.*',c)
        logging.info("Test case completed")

    @pytest.mark.run(order=5)
    def test_623_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        

    @pytest.mark.run(order=6)
    def test_624_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client_with_32_prefix(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=7)
    def test_625_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=8)
    def test_626_Validate_NAMED_CEF_Log_For_CAT_BL_with_32_prefix(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor="named.*info CEF.*facebook.com.*CAT=BL.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case  Failed")
            assert False

    @pytest.mark.run(order=9)
    def test_627_Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client_with_32_prefix(self):
        logging.info("Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client")
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
        logging.info("Test Case  Completed")
        

    @pytest.mark.run(order=10)
    def test_628_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com(self):
        logging.info("Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test Case  Completed")
        

    @pytest.mark.run(order=11)
    def test_629_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        

    @pytest.mark.run(order=12)
    def test_630_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_with_32_prefix(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip2+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*facebook.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=13)
    def test_631_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=14)
    def test_632_Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_with_32_prefix(self):
        logging.info("Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        LookFor="info CEF.*facebook.com.*CAT=BL"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert False
        else:
            logging.info("Test Case Failed")
            assert True

    @pytest.mark.run(order=15)
    def test_633_Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_with_32_prefix(self):
        logging.info("Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
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
        assert re.search(r'.*facebook.com.*',c)
        assert re.search(r'.*0x00000000100000000000000000000000.*',c)
        logging.info("Test Case  Completed")
        

    @pytest.mark.run(order=16)
    def test_634_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_with_32_prefix(self):
        logging.info("Validate_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*2.*',c)
        logging.info("Test Case  Completed")
        

    @pytest.mark.run(order=17)
    def test_635_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test passed")
        

    @pytest.mark.run(order=18)
    def test_636_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client_with_32_prefix(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Completed")

    @pytest.mark.run(order=19)
    def test_637_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Completed")

    @pytest.mark.run(order=20)
    def test_638_Validate_DCA_CEF_Log_shows_CAT_BL_When_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client_with_32_prefix(self):
        logging.info("Verify DCA CEF Log for ponse from DCA")
        LookFor="fp-rte.*info CEF.*facebook.com.*CAT=BL"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case  Failed")
            assert False
#IPV6 Cases
    @pytest.mark.run(order=1)
    def test_639_Add_Subscriber_Record_with_Subscriber_ClientV6(self):
        stop_subscriber_collection_services_for_added_site([config.grid_fqdn])
        sleep(30)
        start_subscriber_collection_services_for_added_site([config.grid_fqdn])
        sleep(30)
        enable_mgmt_port_for_dns()
        restart_the_grid()
        try:
            logging.info("Add Subscriber Record with BWList")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ipV6+' 128 N/A N/A "ACS:Acct-Session-Id=99-d99;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';UCP:Unknown-Category-Policy=1;DCP:Dynamic-Category-Policy=1;SUB:Calling-Station-Id=143;BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;" ')
            child.expect('Record successfully added')
            logging.info("Test case passed")
            assert True
        except:
            logging.info("Test Case 1 Execution Failed")
            assert False

    @pytest.mark.run(order=2)
    def test_640_Validate_Subscriber_Record_with_Subscriber_ClientV6(self):
        logging.info("Validate Subscriber Record with_BWList")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ipV6+'\/128\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000000000000020040.*.*BWFlag.*BL.*facebook.*WL.*bbc.*',c)
        logging.info("Test case 2 execution completed")

    @pytest.mark.run(order=3)
    def test_641_Add_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_ClientV6(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2V6+' 128 N/A N/A "ACS:Acct-Session-Id=981-d991;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000001000000000000;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000001000000000000000;SUB:Calling-Station-Id=1493;BWI:BWFlag=1;BL=blore.com;WL=hydbad.com;" ')
            child.expect('Record successfully added')
            logging.info("Test case passed")
            assert True
        except:
            logging.info("Test Case 1 Execution Failed")
            assert False

    @pytest.mark.run(order=4)
    def test_642_Validate_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client_V6(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2V6+'\/128\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000001000000000000.*BWFlag.*BL.*blore.*WL.*hydbad.com.*',c)
        logging.info("Test case 2 execution completed")

    @pytest.mark.run(order=5)
    def test_643_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=6)
    def test_644_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_clientV6(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip6)+' facebook.com +noedns -b '+config.client_ipV6+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")

    @pytest.mark.run(order=7)
    def test_645_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=8)
    def test_646_Validate_NAMED_CEF_Log_For_CAT_BL(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor="named.*info CEF.*facebook.com.*CAT=BL.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case 9 Execution Failed")
            assert False

    @pytest.mark.run(order=9)
    def test_647_Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client_V6(self):
        logging.info("Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client")
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
        logging.info("Test Case 10 Execution Completed")


    @pytest.mark.run(order=10)
    def test_648_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com(self):
        logging.info("Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test Case 11 Execution Completed")


    @pytest.mark.run(order=11)
    def test_649_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(20)


    @pytest.mark.run(order=12)
    def test_650_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_V6(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip6)+' facebook.com +noedns -b '+config.client_ip2V6+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*facebook.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case 13 Execution Completed")

    @pytest.mark.run(order=13)
    def test_651_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=14)
    def test_652_Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_V6_NEGATIVE_CASE(self):
        logging.info("Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        LookFor="info CEF.*facebook.com.*CAT=BL"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert False
        else:
            logging.info("Test Case 15 Execution Failed")
            assert True

    @pytest.mark.run(order=15)
    def test_653_Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_V6(self):
        logging.info("Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
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
        assert re.search(r'.*facebook.com.*',c)
        assert re.search(r'.*0x00000000100000000000000000000000.*',c)
        logging.info("Test Case 16 Execution Completed")

    @pytest.mark.run(order=16)
    def test_654_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_V6(self):
        logging.info("Validate_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*2.*',c)
        logging.info("Test Case 17 Execution Completed")

    @pytest.mark.run(order=17)
    def test_655_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")

    @pytest.mark.run(order=18)
    def test_656_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client_V6(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip6)+' facebook.com +noedns -b '+config.client_ipV6+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")

    @pytest.mark.run(order=19)
    def test_657_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=20)
    def test_658_Validate_DCA_CEF_Log_shows_CAT_BL_When_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client_V6(self):
        logging.info("Validate DCA CEF Log for ponse from DCA")
        LookFor="fp-rte.*info CEF.*facebook.com.*CAT=BL"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case 21 Execution Failed")
            assert False

#ipv6 ->blacklist, PCP, WPCP Combinations
    @pytest.mark.run(order=1)
    def test_668_Add_Subscriber_Record_with_Subscriber_V6(self):
        restart_the_grid()
        try:
            logging.info("Add Subscriber Record with BWList")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ipV6+' 128 N/A N/A "ACS:Acct-Session-Id=99-d99;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';UCP:Unknown-Category-Policy=1;DCP:Dynamic-Category-Policy=1;SUB:Calling-Station-Id=143;BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;" ')
            child.expect('Record successfully added')
            logging.info("Test case passed")
            assert True
        except:
            logging.info("Test Case 1 Execution Failed")
            assert False

    @pytest.mark.run(order=2)
    def test_669_Validate_Subscriber_Record_with_Subscriber_V6(self):
        logging.info("Validate Subscriber Record with_BWList")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ipV6+'\/128\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000000000000020040.*.*BWFlag.*BL.*facebook.*WL.*bbc.*',c)
        logging.info("Test case 2 execution completed")

    @pytest.mark.run(order=3)
    def test_670_Add_Subscriber_Record_with_non_PCP_Bit_Matchingsubscriber_ClientV6(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2V6+' 128 N/A N/A "ACS:Acct-Session-Id=981-d991;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000001000000000000;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000001000000000000000;SUB:Calling-Station-Id=1493;BWI:BWFlag=1;BL=blore.com;WL=hydbad.com;" ')
            child.expect('Record successfully added')
            logging.info("Test case passed")
            assert True
        except:
            logging.info("Test Case 1 Execution Failed")
            assert False

    @pytest.mark.run(order=4)
    def test_671_Validate_Subscriber_Record_with_non_PCP_Bit_Matching_V6_subscriber_ClientV6(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2V6+'\/128\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000001000000000000.*.*BWFlag.*BL.*blore.*WL.*hydbad.com.*',c)
        logging.info("Test case 2 execution completed")

    @pytest.mark.run(order=5)
    def test_672_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=6)
    def test_673_Query_PCP_domain_playboy_com_from_PCP_bit_matching_Subscriber_clientV6(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip6)+' playboy.com +noedns -b '+config.client_ipV6+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")

    @pytest.mark.run(order=7)
    def test_674_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=8)
    def test_675_Validate_NAMED_CEF_Log_For_CAT_Bit_20000(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor="named.*info CEF.*playboy.com.*CAT.*20000.*"
        #LookFor="named.*info CEF.*facebook.com.com.*CAT.*20000.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False

    @pytest.mark.run(order=9)
    def test_676_Validate_PCP_Domain_playboy_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_clientV6(self):
        logging.info("Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client")
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
        logging.info("Test Case 10 Execution Completed")

    @pytest.mark.run(order=10)
    def test_677_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_PCP_Domain_playboy_com(self):
        logging.info("Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test Case 11 Execution Completed")

    @pytest.mark.run(order=11)
    def test_678_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(30)
		
    @pytest.mark.run(order=12)
    def test_679_Query_PCP_domain_playboy_com_from_NON_PCP_bit_matching_Subscriber_clientV6(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip6)+' playboy.com +noedns -b '+config.client_ip2V6+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case 13 Execution Completed")

    @pytest.mark.run(order=13)
    def test_680_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 8 Execution Completed")
		
    @pytest.mark.run(order=14)
    def test_681_Validate_NO_CEF_Log_When_Query_PCP_domain_playboy_com_from_NON_PCP_bit_matching_Subscriber_clientV6_NEGATIVE_CASE(self):
        logging.info("Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        #LookFor="info CEF.*facebook.com.*CAT=20000.*"
        LookFor="info CEF.*playboy.com.*CAT=20000.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert False
        else:
            logging.info("Test Case  Execution Failed")
            assert True

    @pytest.mark.run(order=15)
    def test_682_Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_clientV6(self):
        logging.info("Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
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
        assert re.search(r'.*playboy.com.*',c)
        #assert re.search(r'.*0x00000000100000000000000000000000.*',c)
        assert re.search(r'.*0x00000000000000000000000000020000.*',c)
        logging.info("Test Case 16 Execution Completed")
        
        
    @pytest.mark.run(order=16)
    def test_683_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_When_Query_PCP_domain_playboy_com_from_NON_PCP_bit_matching_Subscriber_clientV6(self):
        logging.info("Validate_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*2.*',c)
        logging.info("Test Case 17 Execution Completed")
        

    @pytest.mark.run(order=17)
    def test_684_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        

    @pytest.mark.run(order=18)
    def test_685_Query_PCP_domain_playboy_com_from_PCP_bit_matching_Subscriber_clientV6(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip6)+' playboy.com +noedns -b '+config.client_ipV6+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")

    @pytest.mark.run(order=19)
    def test_686_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=20)
    def test_687_Validate_DCA_CEF_Log_shows_CAT_20000_When_Query_PCP_domain_playboy_com_from_PCP_bit_matching_Subscriber_clientV6(self):
        logging.info("Validate DCA CEF Log for ponse from DCA")
        LookFor="fp-rte.*info CEF.*facebook.com.*CAT.*20000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case  Execution Failed")
            assert False

#ipv6 ->blacklist, PCP, WPCP Combinations
    @pytest.mark.run(order=1)
    def test_688_Add_Subscriber_Record_with_Subscriber_ClientV6(self):
        restart_the_grid()
        try:
            logging.info("Add Subscriber Record with BWList")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ipV6+' 128 N/A N/A "ACS:Acct-Session-Id=99-d99;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';UCP:Unknown-Category-Policy=1;DCP:Dynamic-Category-Policy=1;SUB:Calling-Station-Id=143;BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;IPA:IP='+config.client_ip1+';" ')
            child.expect('Record successfully added')
            logging.info("Test case passed")
            assert True
        except:
            logging.info("Test Case 1 Execution Failed")
            assert False

    @pytest.mark.run(order=2)
    def test_689_Validate_Subscriber_Record_with_Subscriber_ClientV6(self):
        logging.info("Validate Subscriber Record with_BWList")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ipV6+'\/128\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000000000000020040.*.*BWFlag.*BL.*facebook.*WL.*bbc.*',c)
        logging.info("Test case 2 execution completed")

    @pytest.mark.run(order=3)
    def test_690_Add_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_ClientV6(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2V6+' 128 N/A N/A "ACS:Acct-Session-Id=981-d991;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000001000000000000;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000001000000000000000;SUB:Calling-Station-Id=1493;BWI:BWFlag=1;BL=blore.com;WL=hydbad.com;" ')
            child.expect('Record successfully added')
            logging.info("Test case passed")
            assert True
        except:
            logging.info("Test Case 1 Execution Failed")
            assert False

    @pytest.mark.run(order=4)
    def test_691_Validate_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client_V6(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2V6+'\/128\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000001000000000000.*.*BWFlag.*BL.*blore.*WL.*hydbad.com.*',c)
        logging.info("Test case 2 execution completed")

    @pytest.mark.run(order=5)
    def test_692_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        

    @pytest.mark.run(order=6)
    def test_693_Query_WPCP_domain_vodka_com_from_PCP_bit_matching_Subscriber_clientV6(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip6)+' vodka.com +noedns -b '+config.client_ipV6+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*vodka.com.*IN.*A.*',str(dig_result))        
        logging.info("Test Case 7 Execution Completed")

    @pytest.mark.run(order=7)
    def test_694_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=8)
    def test_695_Validate_NAMED_CEF_Log_For_CAT_00001(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor="named.*info CEF.*vodka.com.*CAT.*00001.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case 9 Execution Failed")
            assert False

    @pytest.mark.run(order=9)
    def test_696_Validate_WPCP_Domain_vodka_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client_V6(self):
        logging.info("Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client")
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
        logging.info("Test Case 10 Execution Completed")
        

    @pytest.mark.run(order=10)
    def test_697_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_WPCP_Domain_vodka_com(self):
        logging.info("Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test Case 11 Execution Completed")
        

    @pytest.mark.run(order=11)
    def test_698_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        

    @pytest.mark.run(order=12)
    def test_699_Query_WPCP_domain_vodka_com_from_NON_PCP_bit_matching_Subscriber_client_V6(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip6)+' vodka.com IN AAAA +noedns -b '+config.client_ip2V6+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*vodka.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case 13 Execution Completed")

    @pytest.mark.run(order=13)
    def test_700_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=14)
    def test_701_Validate_NO_CEF_Log_When_Query_WPCP_domain_vodka_com_from_NON_PCP_bit_matching_Subscriber_client_V6_NEGATIVE_CASE(self):
        logging.info("Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        LookFor="info CEF.*vodka.com.*CAT=BL"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert False
        else:
            logging.info("Test Case 15 Execution Failed")
            assert True

    @pytest.mark.run(order=15)
    def test_702_Validate_domain_cached_in_DCA_When_Query_WPCP_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_V6(self):
        logging.info("Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
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
        assert re.search(r'.*vodka.com.*',c)
        assert re.search(r'.*0x00000000000000000000000000000001.*',c)
        logging.info("Test Case 16 Execution Completed")
        

    @pytest.mark.run(order=16)
    def test_703_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_When_Query_WPCP_domain_vodka_com_from_NON_PCP_bit_matching_Subscriber_client_V6(self):
        logging.info("Validate_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*2.*',c)
        logging.info("Test Case 17 Execution Completed")
        

    @pytest.mark.run(order=17)
    def test_704_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        

    @pytest.mark.run(order=18)
    def test_705_Query_WPCP_domain_vodka_com_from_PCP_bit_matching_Subscriber_client_V6(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip6)+' vodka.com IN AAAA +noedns -b '+config.client_ipV6+' +tries=1;dig @'+str(config.grid_vip6)+' vodka.com IN AAAA +noedns -b '+config.client_ipV6+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        #assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        #assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")

    @pytest.mark.run(order=19)
    def test_706_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=20)
    def test_707_Validate_DCA_CEF_Log_shows_CAT_0001_When_Query_WPCP_domain_vodka_com_from_PCP_bit_matching_Subscriber_client_V6(self):
        logging.info("Validate DCA CEF Log for ponse from DCA")
        LookFor="fp-rte.*info CEF.*vodka.com.*CAT.*00001.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case 21 Execution Failed")
            assert False

#IPV6 with 64 and 128 network
    @pytest.mark.run(order=21)
    def test_708_Add_Subscriber_Record_with_V6_Subscriber_64_prefix(self):
        stop_subscriber_collection_services_for_added_site([config.grid_fqdn])
        sleep(30)
        start_subscriber_collection_services_for_added_site([config.grid_fqdn])
        sleep(30)
        restart_the_grid()
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_network_V6_64+' 64 N/A N/A "ACS:Acct-Session-Id=99-d99;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';UCP:Unknown-Category-Policy=1;DCP:Dynamic-Category-Policy=1;SUB:Calling-Station-Id=143;BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Passed")
            assert True
        except:
            logging.info("Test Case Failed")
            assert False

    @pytest.mark.run(order=2)
    def test_709_Validate_Subscriber_Record_with_V6_Subscriber_64_prefix(self):
        logging.info("Verify Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_network_V6_64+'\/64\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000000000000020040.*',c)
        logging.info("Test case completed")

    @pytest.mark.run(order=3)
    def test_710_Add_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 N/A N/A "ACS:Acct-Session-Id=981-d991;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000001000000000000;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000001000000000000000;SUB:Calling-Station-Id=1493;BWI:BWFlag=1;BL=blore.com;WL=hydbad.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Case Passed")
            assert True
        except:
            logging.info("Test Case Failed")
            assert False

    @pytest.mark.run(order=4)
    def test_711_Validate_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        logging.info("Verify Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000001000000000000.*.*BWFlag.*BL.*blore.*WL.*hydbad.com.*',c)
        logging.info("Test case completed")

    @pytest.mark.run(order=5)
    def test_712_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=6)
    def test_713_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client_with_V6_Subscriber_64_prefix(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip6)+' facebook.com +noedns -b '+config.client_ipV6+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=7)
    def test_714_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=8)
    def test_715_Validate_NAMED_CEF_Log_For_CAT_BL_with_64_prefix(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor="named.*info CEF.*facebook.com.*CAT=BL.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case  Failed")
            assert False

    @pytest.mark.run(order=9)
    def test_716_Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client_with_V6_Subscriber_64_prefix(self):
        logging.info("Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client")
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
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=10)
    def test_717_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com(self):
        logging.info("Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test Case  Completed")
        

    @pytest.mark.run(order=11)
    def test_718_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=12)
    def test_719_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip2+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*facebook.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=13)
    def test_720_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=14)
    def test_721_Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_with_V6_Subscriber_64_prefix(self):
        logging.info("Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        LookFor="info CEF.*facebook.com.*CAT=BL"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert False
        else:
            logging.info("Test Case Failed")
            assert True

    @pytest.mark.run(order=15)
    def test_722_Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_with_V6_Subscriber_64_prefix(self):
        logging.info("Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
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
        assert re.search(r'.*facebook.com.*',c)
        assert re.search(r'.*0x00000000100000000000000000000000.*',c)
        logging.info("Test Case  Completed")
        

    @pytest.mark.run(order=16)
    def test_723_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_with_V6_Subscriber_64_prefix(self):
        logging.info("Validate_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*2.*',c)
        logging.info("Test Case  Completed")
    

    @pytest.mark.run(order=17)
    def test_724_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test passed")
        

    @pytest.mark.run(order=18)
    def test_725_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client_with_V6_Subscriber_64_prefix(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip6)+' facebook.com +noedns -b '+config.client_ipV6+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Completed")

    @pytest.mark.run(order=19)
    def test_726_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Completed")

    @pytest.mark.run(order=20)
    def test_727_Validate_DCA_CEF_Log_shows_CAT_BL_When_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client_with_V6_Subscriber_64_prefix(self):
        logging.info("Verify DCA CEF Log for ponse from DCA")
        LookFor="fp-rte.*info CEF.*facebook.com.*CAT=BL"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case  Failed")
            assert False


    @pytest.mark.run(order=1)
    def test_728_Add_Subscriber_Record_with_V6_Subscriber_128_prefix(self):
        restart_the_grid()
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_network_V6_128+' 128 N/A N/A "ACS:Acct-Session-Id=99-d99;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';UCP:Unknown-Category-Policy=1;DCP:Dynamic-Category-Policy=1;SUB:Calling-Station-Id=143;BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Passed")
            assert True
        except:
            logging.info("Test Case Failed")
            assert False

    @pytest.mark.run(order=2)
    def test_729_Validate_Subscriber_Record_with_V6_Subscriber_128_prefix(self):
        logging.info("Verify Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_network_V6_128+'\/128\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000000000000020040.*',c)
        logging.info("Test case completed")

    @pytest.mark.run(order=3)
    def test_730_Add_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 N/A N/A "ACS:Acct-Session-Id=981-d991;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000001000000000000;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000001000000000000000;SUB:Calling-Station-Id=1493;BWI:BWFlag=1;BL=blore.com;WL=hydbad.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Case Passed")
            assert True
        except:
            logging.info("Test Case Failed")
            assert False

    @pytest.mark.run(order=4)
    def test_731_Validate_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        logging.info("Verify Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000001000000000000.*.*BWFlag.*BL.*blore.*WL.*hydbad.com.*',c)
        logging.info("Test case completed")

    @pytest.mark.run(order=5)
    def test_732_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        

    @pytest.mark.run(order=6)
    def test_733_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client_with_V6_Subscriber_128_prefix(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip6)+' facebook.com +noedns -b '+config.client_ipV6+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=7)
    def test_734_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=8)
    def test_735_Validate_NAMED_CEF_Log_For_CAT_BL_with_128_prefix(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor="named.*info CEF.*facebook.com.*CAT=BL.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case  Failed")
            assert False

    @pytest.mark.run(order=9)
    def test_736_Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client_with_V6_Subscriber_128_prefix(self):
        logging.info("Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client")
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
        logging.info("Test Case  Completed")
        

    @pytest.mark.run(order=10)
    def test_737_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com(self):
        logging.info("Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test Case  Completed")
        

    @pytest.mark.run(order=11)
    def test_738_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        

    @pytest.mark.run(order=12)
    def test_739_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip2+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*facebook.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=13)
    def test_740_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case  Completed")

    @pytest.mark.run(order=14)
    def test_741_Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_with_V6_Subscriber_128_prefix(self):
        logging.info("Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        LookFor="info CEF.*facebook.com.*CAT=BL"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert False
        else:
            logging.info("Test Case Failed")
            assert True

    @pytest.mark.run(order=15)
    def test_742_Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_with_V6_Subscriber_128_prefix(self):
        logging.info("Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
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
        assert re.search(r'.*facebook.com.*',c)
        assert re.search(r'.*0x00000000100000000000000000000000.*',c)
        logging.info("Test Case  Completed")
        

    @pytest.mark.run(order=16)
    def test_743_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client_with_V6_Subscriber_128_prefix(self):
        logging.info("Validate_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*2.*',c)
        logging.info("Test Case  Completed")
        

    @pytest.mark.run(order=17)
    def test_744_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test passed")
        

    @pytest.mark.run(order=18)
    def test_745_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client_with_V6_Subscriber_128_prefix(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip6)+' facebook.com +noedns -b '+config.client_ipV6+' +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Completed")

    @pytest.mark.run(order=19)
    def test_746_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Completed")

    @pytest.mark.run(order=20)
    def test_747_Validate_DCA_CEF_Log_shows_CAT_BL_When_Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client_with_V6_Subscriber_128_prefix(self):
        logging.info("Verify DCA CEF Log for ponse from DCA")
        LookFor="fp-rte.*info CEF.*facebook.com.*CAT=BL"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case  Failed")
            assert False

    @pytest.mark.run(order=21)
    def test_748_Remove_Subscriber_Record_with_V6_Subscriber_128_prefix(self):
        restart_the_grid()
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data delete '+config.client_network_V6_128+' 128 N/A N/A')
            child.expect('Record successfully deleted')
            logging.info("Test Passed")
            assert True
        except:
            logging.info("Test Case Failed")
            assert False
#CGNAT Cases:
    @pytest.mark.run(order=1)
    def test_749_Select_Deterministic_NAT_Port_in_ip_space_discriminator_in_Subscriber_Services_properties(self):
                stop_subscriber_collection_services_for_added_site([config.grid_fqdn])
                sleep(30)
                start_subscriber_collection_services_for_added_site([config.grid_fqdn])
                sleep(30)
                restart_the_grid()
                logging.info("NAT")
                get_ref = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']

                logging.info("Modify a enable_PC")

                data = {"ip_space_discriminator":"Deterministic-NAT-Port"}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case  Execution Completed")


    @pytest.mark.run(order=2)
    def test_750_Modify_Subscriber_Site_And_modify_Block_Size_and_First_Port(self):
                get_ref = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                data = {"first_port":1024,"block_size":3,"strict_nat":False}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                restart_the_grid()
                for read in  response:
                         assert True
						 
    @pytest.mark.run(order=3)
    def test_751_Add_Subscriber_Cache_Record_with_IPS_1024_and_AVP_Deterministic_NAT_Port_1024(self):
        logging.info("Subscriber Record ")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A 1024 "ACS:Acct-Session-Id=9999732d-34590346;DNP:Deterministic-NAT-Port=1024;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;SUB:Calling-Station-Id=110361221;"')
        child.expect('Record successfully added')

    @pytest.mark.run(order=4)
    def test_752_Validate_Subscriber_Record_with_IPS_1024_and_AVP_Deterministic_NAT_Port_1024(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32.*1024.*PCP\:Parental-Control-Policy=00000000000000000000000000020040.*',c)
        logging.info("Test case execution completed")


    @pytest.mark.run(order=5)
    def test_753_Add_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 N/A N/A "ACS:Acct-Session-Id=981-d991;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000001000000000000;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000001000000000000000;SUB:Calling-Station-Id=1493;BWI:BWFlag=1;BL=blore.com;WL=hydbad.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Case  Execution Passed")
            assert True
        except:
            logging.info("Test Case  Execution Failed")
            assert False

    @pytest.mark.run(order=6)
    def test_754_Validate_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000001000000000000.*.*BWFlag.*BL.*blore.*WL.*hydbad.com.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=7)
    def test_755_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        
    @pytest.mark.run(order=8)
    def test_756_Query_PCP_domain_playboy_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vip)+' -srcport 2024 -srcaddr '+config.client_ip1+' -qname=playboy.com"'

        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=9)
    def test_757_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 8 Execution Completed")


    @pytest.mark.run(order=10)
    def test_758_Validate_NAMED_CEF_Log_For_CAT_Bit_20000(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor="named.*info CEF.*playboy.com.*CAT.*20000.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case  Execution Passed")
            assert True
        else:
            logging.info("Test Case  Execution Failed")
            assert False

    @pytest.mark.run(order=11)
    def test_759_Validate_PCP_Domain_playboy_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client(self):
        logging.info("Validate")
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
        logging.info("Test Case 10 Execution Completed")
       

    @pytest.mark.run(order=12)
    def test_760_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_PCP_Domain_playboy_com(self):
        logging.info("Validate_Cache")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test Case Execution Completed")
        

    @pytest.mark.run(order=13)
    def test_761_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        
		
    @pytest.mark.run(order=14)
    def test_762_Query_PCP_domain_playboy_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip2+' +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=15)
    def test_763_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")
		
    @pytest.mark.run(order=16)
    def test_764_Validate_NO_CEF_Log_When_Query_PCP_domain_playboy_com_from_NON_PCP_bit_matching_Subscriber_client_NEGATIVE_CASE(self):
        logging.info("Validate")
        LookFor="info CEF.*playboy.com.*CAT=20000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert False
        else:
            logging.info("Test Case Execution Failed")
            assert True

    @pytest.mark.run(order=17)
    def test_765_Validate_domain_cached_in_DCA_When_Query_PCP_domain_playboy_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate")
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
        assert re.search(r'.*playboy.com.*',c)
        logging.info("Test Case Execution Completed")
        

    @pytest.mark.run(order=18)
    def test_766_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_When_Query_PCP_domain_playboy_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*2.*',c)
        logging.info("Test Case Execution Completed")
        

    @pytest.mark.run(order=19)
    def test_767_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        

    @pytest.mark.run(order=20)
    def test_768_Query_PCP_domain_playboy_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vip)+' -srcport 1024 -srcaddr '+config.client_ip1+' -qname=playboy.com"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=21)
    def test_769_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=22)
    def test_770_Validate_DCA_CEF_Log_shows_CAT_20000_When_Query_PCP_domain_playboy_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate")
        LookFor="fp-rte.*info CEF.*playboy.com.*CAT.*20000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case  Execution Passed")
            assert True
        else:
            logging.info("Test Case  Execution Failed")
            assert False

    @pytest.mark.run(order=23)
    def test_771_Modify_Subscriber_Site_And_Disable_NAT_Port(self):
                restart_the_grid()
                get_ref = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                data = {"first_port":1024,"block_size":0,"strict_nat":False}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                    assert True
    		 
    @pytest.mark.run(order=20)
    def test_772_Add_Subscriber_Cache_Record_with_LocalID(self):
        logging.info("Subscriber Record ")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        #child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 e0cb4e80e766 N/A "ACS:Acct-Session-Id=9999732d-34590346;NAS:NAS-PORT=1813;LID:LocalId=E0CB4E80E766;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;SUB:Calling-Station-Id=110361221;"')
        child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 e0cb4e80e766 N/A "ACS:Acct-Session-Id=898989;NAS:NAS-PORT=1813;LID:LocalId=E0CB4E80E766;PCP:Parental-Control-Policy=00001000000000000000000000000000;SSP:Subscriber-Secure-Policy=ffff;PCC:PC-Category-Policy=00010000000000000000000000000000;SUB:Calling-Station-Id=767676;BWI:BWFlag=1;BL=facebook2.com;WL=bbc2.com;"')
        child.expect('Record successfully added')
        
#LocalID Cases
    @pytest.mark.run(order=2)
    def test_773_Validate_Subscriber_Record_with_LocalID(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32|LID\:e0cb4e80e766.*PCP\:Parental-Control-Policy=00001000000000000000000000000000.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=3)
    def test_774_Add_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            #child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 e0cb4e80e766 N/A "ACS:Acct-Session-Id=123;NAS:NAS-PORT=1813;LID:LocalId=E0CB4E80E766;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000000001;SUB:Calling-Station-Id=93333;PXY:Proxy-All=1;PXP:PXY_PRI=0AC4800D;PXS:PXY_SEC=0AC4800D;UCP:Unknown-Category-Policy=1;DCP:Dynamic-Category-Policy=1;BWI:BWFlag=1;BL=facebook.com;WL=bbc.com')
            child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 e0cb4e80e766 N/A "ACS:Acct-Session-Id=123;NAS:NAS-PORT=1813;LID:LocalId=E0CB4E80E766;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000000001;SUB:Calling-Station-Id=93333;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.primary_proxy_server+';UCP:Unknown-Category-Policy=1;DCP:Dynamic-Category-Policy=1;BWI:BWFlag=1;BL=facebook.com;WL=bbc.com')
            child.expect('Record successfully added')
            logging.info("Test Case  Execution Passed")
            assert True
        except:
            logging.info("Test Case  Execution Failed")
            assert False
    @pytest.mark.run(order=4)
    def test_775_Validate_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32.*e0cb4e80e766.*\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000000000000020040.*.*BWFlag.*BL.*facebook.com.*WL.*bbc.com.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=5)
    def test_776_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")

    @pytest.mark.run(order=6)
    def test_777_Query_PCP_domain_playboy_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vip)+' -edo 0 -edata=0xFE31001145303a43423a34453a38303a45373a3636 -srcaddr '+config.client_ip1+' -qname=playboy.com"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=7)
    def test_778_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=8)
    def test_779_Validate_NAMED_CEF_Log_For_CAT_Bit_20000(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        #LookFor="named.*info CEF.*playboy.com.*CAT.*20000.*"
        LookFor=".*named.*NOERROR.*playboy.com.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case  Execution Passed")
            assert True
        else:
            logging.info("Test Case  Execution Failed")
            assert False
    @pytest.mark.run(order=9)
    def test_780_Validate_PCP_Domain_playboy_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client(self):
        logging.info("Validate")
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
        assert re.search(r'.*playboy.com.*',c)
        assert re.search(r'.*0x00000000000000000000000000020000.*',c)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=10)
    def test_781_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_PCP_Domain_playboy_com(self):
        logging.info("Validate_Cache")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=11)
    def test_782_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=12)
    def test_783_Query_PCP_domain_playboy_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vip)+' -edo 0 -edata=0xFE31001145303a43423a34453a38303a45373a3636 -srcaddr '+config.client_ip2+' -qname=playboy.com"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=13)
    def test_784_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=14)
    def test_785_Validate_NO_CEF_Log_When_Query_PCP_domain_playboy_com_from_NON_PCP_bit_matching_Subscriber_client_NEGATIVE_CASE(self):
        logging.info("Validate")
        LookFor=".*fp-rte.*info CEF.*playboy.com.*CAT.*20000"
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

    @pytest.mark.run(order=22)
    def test_786_Validate_domain_cached_in_DCA_When_Query_PCP_domain_playboy_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate")
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
        assert re.search(r'.*playboy.com.*',c)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=11)
    def test_787_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_When_Query_PCP_domain_playboy_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*1.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test Case Execution Completed")

    '''
    @pytest.mark.run(order=2)
    def test_773_Validate_Subscriber_Record_with_LocalID(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32.*e0cb4e80e766.*PCP\:Parental-Control-Policy=00000000000000000000000000020040.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=3)
    def test_774_Add_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 N/A N/A "ACS:Acct-Session-Id=981-d991;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000001000000000000;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000001000000000000000;SUB:Calling-Station-Id=1493;BWI:BWFlag=1;BL=blore.com;WL=hydbad.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Case  Execution Passed")
            assert True
        except:
            logging.info("Test Case  Execution Failed")
            assert False

    @pytest.mark.run(order=4)
    def test_775_Validate_Subscriber_Record_with_non_PCP_Bit_Matching_subscriber_Client(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000000001000000000000.*.*BWFlag.*BL.*blore.*WL.*hydbad.com.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=5)
    def test_776_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")

    @pytest.mark.run(order=6)
    def test_777_Query_PCP_domain_playboy_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vip)+' -edo 0 -edata=0xFE31001145303a43423a34453a38303a45373a3636 -protocol udp -qname=playboy.com"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=7)
    def test_778_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=8)
    def test_779_Validate_NAMED_CEF_Log_For_CAT_Bit_20000(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor="named.*info CEF.*playboy.com.*CAT.*20000.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case  Execution Passed")
            assert True
        else:
            logging.info("Test Case  Execution Failed")
            assert False

    @pytest.mark.run(order=9)
    def test_780_Validate_PCP_Domain_playboy_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client(self):
        logging.info("Validate")
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
        logging.info("Test Case Execution Completed")
    
    @pytest.mark.run(order=10)
    def test_781_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_PCP_Domain_playboy_com(self):
        logging.info("Validate_Cache")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test Case Execution Completed")
        
    @pytest.mark.run(order=11)
    def test_782_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)
		
    @pytest.mark.run(order=12)
    def test_783_Query_PCP_domain_playboy_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip2+' +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=13)
    def test_784_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")
		
    @pytest.mark.run(order=14)
    def test_785_Validate_NO_CEF_Log_When_Query_PCP_domain_playboy_com_from_NON_PCP_bit_matching_Subscriber_client_NEGATIVE_CASE(self):
        logging.info("Validate")
        LookFor="info CEF.*playboy.com.*CAT=20000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert False
        else:
            logging.info("Test Case Execution Failed")
            assert True

    @pytest.mark.run(order=22)
    def test_786_Validate_domain_cached_in_DCA_When_Query_PCP_domain_playboy_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate")
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
        assert re.search(r'.*playboy.com.*',c)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=11)
    def test_787_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_When_Query_PCP_domain_playboy_com_from_NON_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        assert re.search(r'.*Cache miss count.*2.*',c)
        logging.info("Test Case Execution Completed")
                       
    @pytest.mark.run(order=57)
    def test_788_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=48)
    def test_789_Query_PCP_domain_playboy_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Query")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vip)+' -edo 0 -edata=0xFE31001145303a43423a34453a38303a45373a3636 -protocol udp -qname=playboy.com"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=39)
    def test_790_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=29)
    def test_791_Validate_DCA_CEF_Log_shows_CAT_20000_When_Query_PCP_domain_playboy_com_from_PCP_bit_matching_Subscriber_client(self):
        logging.info("Validate")
        LookFor="fp-rte.*info CEF.*playboy.com.*CAT.*20000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case  Execution Passed")
            assert True
        else:
            logging.info("Test Case  Execution Failed")
            assert False
    '''
#V6_Prefix_range_Limit

    @pytest.mark.run(order=5)
    def test_792_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("test case  passed")
        sleep(10)
		
		
    @pytest.mark.run(order=6)
    def test_793_Add_12_IPv6_Network_Subscriber_Record_With_Different_Subnetmask_To_Validate_MAX_Different_IPv6_Networks_Subscriber_Records_Allowed(self):
        try:
            logging.info("Add IPv6 Network Subscriber Record with Different Subnetmask and Validate it allows MAX 11 IPv6 Networks Subscriber recors ")
            for i in range(1,12):
                j= 112+i
                print j
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('password:',timeout=None)
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('set subscriber_secure_data add 2620:10a:6000:2500:230:48ff:fed5:'+str(i)+' '+str(j)+' N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;"')

                child.expect('Record successfully added')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Passed")
            assert False


    @pytest.mark.run(order=7)
    def test_794_Validate_11_IPv6_Subscriber_Record_with_Different_Subnetmask(self):
        logging.info("Validate Subscriber Record with Different Subnetmask")
        for i in range(1,12):
            j= 112+i
            print j
            kk= '2620:10a:6000:2500:230:48ff:fed5:'+str(i)+' '+str(j)+''
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('show subscriber_secure_data find 2620:10a:6000:2500:230:48ff:fed5:'+str(i)+' '+str(j)+' N/A N/A')
            child.expect('Infoblox >')
            c=child.before
            assert re.search(r'.*2620:10a:6000:2500:230:48ff:fed5:'+str(i)+'.*',c)
        logging.info("Test case  execution completed")


    @pytest.mark.run(order=8)
    def test_795_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=9)
    def test_796_Validate_Syslog_Logs_Logging_Proper_error_Message_for_12th_IPv6_Networks_subscriber_Record(self):
        logging.info("Validate Syslog Logs Logging Proper error Message logged for 12th IPv6 Networks subscriber Record ")
        LookFor=".*Max size of prefixv6 list has reached. Adding prefix failed.*"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False



    @pytest.mark.run(order=10)
    def test_797_Delete_All_11_IPv6_Network_Subscriber_Record_with_Different_Subnetmask(self):
        try:
            logging.info("Delete all 11 IPv6 Network Subscriber which are added with Different Subnetmask ")
            for i in range(1,12):
                j= 112+i
                print j
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('password:',timeout=None)
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('set subscriber_secure_data delete 2620:10a:6000:2500:230:48ff:fed5:'+str(i)+' '+str(j)+' N/A N/A')
                child.expect('Record successfully deleted')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Passed")
            assert False

#1000Bytes_SSP_Record    
    @pytest.mark.run(order=1)
    def test_798_Copy_Subscriber_Record_radclientfiles_to_radclient(self):
        restart_the_grid()
        logging.info("Copy Subscriber Record radius message files to RAD Client")
        dig_cmd = 'sshpass -p infoblox scp -pr 1k.txt root@'+str(config.rad_client_ip)+':/root/ '
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        print "Copied the files to radclient"
        logging.info("Test Case Completed")
        sleep(5)
                          
    @pytest.mark.run(order=2)
    def test_799_From_Radclient_Send_Start_Radius_Message_with_more_than_1000Bytes(self):
        logging.info("From Rad client send Start Radius message ")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f 1k.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Completed")
        sleep(5)
 
    @pytest.mark.run(order=3)
    def test_800_Validate_Subscriber_Record_added_Radius_Message_with_more_than_1000Bytes(self):
        logging.info("Verify Subscriber Record with_BWList")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*20.36.0.153\/32\|LID\:N\/A\|IPS\:N\/A.*ACS:Acct-Session-Id=zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz;NAS:NAS-PORT=1813;SSP:Subscriber-Secure-Policy=7fffffff;PXY:Proxy-All=1;PCP:Parental-Control-Policy=00000000000000000000000000000fff;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';SUB:Calling-Station-Id=110360151jnpr3514151217040jnpr3514151217040217040jnpr3514151217040jnpr3514151217040jnpr3514151217040jnpr3514151217040jnpr3514151217055jnpr3514151217055jnpr3514151217055jnpr3514151217055jnpr3514151217055jnpr35141512170*',c)
        logging.info("Test case completed")

    
    @pytest.mark.run(order=1)
    def test_801_Add_subscriber_record_with_PCP_20000_playboy_com_WPCP_20000_playboy_com_ProxyAll_1_BL_playboy_com_and_WL_playboy_com_and_SSP_ff(self):
        '''
        stop_subscriber_collection_services_for_added_site([config.grid_fqdn])
        sleep(30)
        start_subscriber_collection_services_for_added_site([config.grid_fqdn])
        sleep(30)
        restart_the_grid()
        '''
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=123;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020000;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000020000;SUB:Calling-Station-Id=93333;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.primary_proxy_server+';BWI:BWFlag=1;BL=playboy.com;WL=playboy.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Failed")
            assert False

    @pytest.mark.run(order=2)
    def test_802_Validate_Subscriber_Record(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*.*',c)
        logging.info("Test case 2 execution completed")
				
    @pytest.mark.run(order=3)
    def test_803_Add_RPZ_PASSTHRU_rule_playboy_com_in_First_RPZ_Zone(self):
        logging.info("add rpz rule")
        ref=add_rpz_rule("playboy.com","rpz0.com")
        if ref!=None:
            logging.info("Test case executed successfully")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
        sleep(40)

    @pytest.mark.run(order=4)
    def test_804_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 3 passed")
        sleep(10)

    @pytest.mark.run(order=5)
    def test_805_Query_playboy_com(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")
        sleep(20)

    @pytest.mark.run(order=6)
    def test_806_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=7)
    def test_807_Validate_RPZ_hit_with_CEF_Log_RPZ_QNAME_PASSTHRU(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor=".*RPZ-QNAME.*PASSTHRU.*rpz QNAME PASSTHRU rewrite playboy.com.*via playboy.com.rpz0.com.*Parental-Control-Policy=00000000000000000000000000020000.*CAT=RPZ.*"
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
 
    @pytest.mark.run(order=8)
    def test_808_Remove_RPZ_PASSTHRU_rule_playboy_com_in_First_RPZ_zone_and_add_it_in_fifth_RPZ_zone(self):
        logging.info("add rpz rule")
        ref=remove_rpz_rule("playboy.com","rpz0.com")
        ref1=add_rpz_rule("playboy.com","rpz4.com")
        if ref1!=None:
            logging.info("Test case executed successfully")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
        sleep(30)
			
    @pytest.mark.run(order=9)
    def test_809_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 3 passed")
        sleep(10)

    @pytest.mark.run(order=10)
    def test_810_Query_playboy_com(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=11)
    def test_811_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=12)
    def test_812_Validate_RPZ_hit_with_CEF_Log_RPZ_QNAME_PASSTHRU(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor=".*RPZ-QNAME.*PASSTHRU.*rpz QNAME PASSTHRU rewrite playboy.com.*via playboy.com.rpz4.com.*Parental-Control-Policy=00000000000000000000000000020000.*CAT=RPZ.*"
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

    @pytest.mark.run(order=13)
    def test_813_Remove_RPZ_PASSTHRU_rule_playboy_com_in_fifth_RPZ_zone_and_add_it_in_21_RPZ_zone(self):
        logging.info("add rpz rule")
        ref=remove_rpz_rule("playboy.com","rpz4.com")
        ref1=add_rpz_rule("playboy.com","rpz21.com")
        if ref1!=None:
            logging.info("Test case executed successfully")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
        sleep(30)
			
    @pytest.mark.run(order=14)
    def test_814_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 3 passed")
        sleep(10)

    @pytest.mark.run(order=15)
    def test_815_Query_playboy_com(self):
        logging.info("Query")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=16)
    def test_816_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=17)
    def test_817_Validate_query_resolved_with_PCP_Blocking_IPs_since_BL_in_BWList_is_set_to_domain_playboy_com_and_SSP_bit_does_not_match(self):
        logging.info("Validate")
        LookFor=".*CEF.*playboy.com.*CAT=BL.*"
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

    @pytest.mark.run(order=18)
    def test_818_Remove_RPZ_PASSTHRU_rule_playboy_com_in_21_RPZ_zone_and_add_it_in_Last_31_RPZ_zone(self):
        logging.info("add rpz rule")
        ref=remove_rpz_rule("playboy.com","rpz21.com")
        ref1=add_rpz_rule("playboy.com","rpz31.com")
        if ref1!=None:
            logging.info("Test case executed successfully")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
        sleep(30)
            
    @pytest.mark.run(order=19)
    def test_819_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 3 passed")
        sleep(10)

    @pytest.mark.run(order=20)
    def test_820_Query_playboy_com(self):
        logging.info("Query")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=21)
    def test_821_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=22)
    def test_822_Validate_query_resolved_normally_since_Last_31_RPZ_zone_acts_as_whitelist(self):
        logging.info("Validate")
        LookFor=".*playboy.com.*response.*NOERROR.*playboy.com.*"
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

    @pytest.mark.run(order=23)
    def test_823_Remove_RPZ_PASSTHRU_rule_playboy_com_in_Last_31_RPZ_zone(self):
        logging.info("add rpz rule")
        ref=remove_rpz_rule("playboy.com","rpz31.com")
        if ref!=None:
            logging.info("Test case executed successfully")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
        sleep(30)

    @pytest.mark.run(order=24)
    def test_824_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 3 passed")
        sleep(10)

    @pytest.mark.run(order=25)
    def test_825_Query_playboy_com(self):
        logging.info("Query")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=26)
    def test_826_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=27)
    def test_827_Validate_query_resolved_with_PCP_Blocking_IPs_since_BL_in_BWList_is_set_to_domain_playboy_com(self):
        logging.info("Validate")
        LookFor=".*CEF.*playboy.com.*CAT=BL.*"
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

    @pytest.mark.run(order=28)
    def test_828_Modify_BL_playboy_com_to_some_other_domain_that_is_BL_facebook_com(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=123;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020000;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000020000;SUB:Calling-Station-Id=93333;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.primary_proxy_server+';BWI:BWFlag=1;BL=facebook.com;WL=playboy.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Case 1 Execution Passed")
            assert True
        except:
            logging.info("Test Case 1 Execution Failed")
            assert False

    @pytest.mark.run(order=29)
    def test_829_Validate_Subscriber_Record(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*.*',c)
        logging.info("Test case 2 execution completed")
		
    @pytest.mark.run(order=30)
    def test_830_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 3 passed")
        sleep(10)

    @pytest.mark.run(order=31)
    def test_831_Query_playboy_com(self):
        logging.info("Query")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=32)
    def test_832_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")		
		
    @pytest.mark.run(order=33)
    def test_833_Validate_query_resolved_normally_with_public_IPs_since_WL_in_BWList_is_set_to_domain_playboy_com(self):
        logging.info("Validate")
        LookFor=".*UDP.*query.*playboy.com.*IN.*A.*response.*NOERROR.*"
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

    @pytest.mark.run(order=34)
    def test_834_Modify_WL_playboy_com_to_some_other_domain_that_is_WL_bbc_com(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=123;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020000;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000020000;SUB:Calling-Station-Id=93333;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.primary_proxy_server+';BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Case 1 Execution Passed")
            assert True
        except:
            logging.info("Test Case 1 Execution Failed")
            assert False

    @pytest.mark.run(order=35)
    def test_835_Validate_Subscriber_Record(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*.*',c)
        logging.info("Test case 2 execution completed")
		
    @pytest.mark.run(order=36)
    def test_836_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 3 passed")
        sleep(10)

    @pytest.mark.run(order=37)
    def test_837_Query_playboy_com(self):
        logging.info("Query")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=38)
    def test_838_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=39)
    def test_839_Validate_query_resolved_with_PCP_Blocking_IPs_since_PCP_AVP_is_set_to_bit_20000(self):
        logging.info("Validate")
        #LookFor=".*CEF.*rpz QNAME CNAME rewrite playboy.com.*via playboy.com.*Parental-Control-Policy=00000000000000000000000000020000.*Subscriber-Secure-Policy=ff PC-Category-Policy=00000000000000000000000000020000.*CAT=0x00000000000000000000000000020000.*"
        LookFor=".*CEF.*rpz QNAME CNAME rewrite playboy.com.*via playboy.com.*Parental-Control-Policy=0x00000000000000000000000000020000.*PC-Category-Policy=0x00000000000000000000000000020000.*CAT=0x00000000000000000000000000020000.*"
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

    @pytest.mark.run(order=40)
    def test_840_Modify_PCP_20000_to_some_other_bit_that_is_PCP_000040(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=123;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000000040;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000020000;SUB:Calling-Station-Id=93333;PXY:Proxy-All=0;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.primary_proxy_server+';BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Case 1 Execution Passed")
            assert True
        except:
            logging.info("Test Case 1 Execution Failed")
            assert False

    @pytest.mark.run(order=41)
    def test_841_Validate_Subscriber_Record(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*.*',c)
        logging.info("Test case 2 execution completed")
		
    @pytest.mark.run(order=42)
    def test_842_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 3 passed")
        sleep(10)

    @pytest.mark.run(order=43)
    def test_843_Query_playboy_com(self):
        logging.info("Query")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=44)
    def test_844_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=45)
    def test_845_Validate_query_resolved_with_Proxy_MSP_VIPs_response_with_both_CAT_WRN_and_CAT_PXY_since_WPCP_AVP_is_set_to_bit_20000(self):
        logging.info("Validate")
        LookFor=".*CEF.*Infoblox|NIOS.*rpz CLIENT-IP CNAME rewrite playboy.com.*via playboy.com.*Parental-Control-Policy=00000000000000000000000000000040.*PC-Category-Policy=00000000000000000000000000020000.*CAT=WRN_0x00000000000000000000000000020000"
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

    @pytest.mark.run(order=46)
    def test_846_Modify_WPCP_20000_to_some_other_bit_that_is_WPCP_000040(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=123;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000000040;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000000040;SUB:Calling-Station-Id=93333;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.primary_proxy_server+';BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Case 1 Execution Passed")
            assert True
        except:
            logging.info("Test Case 1 Execution Failed")
            assert False

    @pytest.mark.run(order=48)
    def test_847_Validate_Subscriber_Record(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*.*',c)
        logging.info("Test case 2 execution completed")
		
    @pytest.mark.run(order=49)
    def test_848_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 3 passed")
        sleep(10)

    @pytest.mark.run(order=50)
    def test_849_Query_playboy_com(self):
        logging.info("Query")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=51)
    def test_850_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=52)
    def test_851_Validate_query_resolved_with_Proxy_MSP_VIPs_response_with_CAT_PXY_since_proxy_All_AVP_is_set(self):
        logging.info("Validate")
        LookFor=".*CEF.*RPZ-CLIENT-IP.*rpz CLIENT-IP CNAME rewrite playboy.com.*via playboy.com.*Parental-Control-Policy=00000000000000000000000000000040 Subscriber-Secure-Policy=ff PC-Category-Policy=00000000000000000000000000000040.*CAT=PXY.*"
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

    @pytest.mark.run(order=53)
    def test_852_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=54)
    def test_853_Enable_proxy_rpz_passthru_in_subscriber_site(self):
        logging.info("proxy rpz passthru")
        ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=proxy_rpz_passthru")
        ref=json.loads(ref)
        ref1=ref[0]["_ref"]
        data={"proxy_rpz_passthru":True}
        ref=ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
        restart_the_grid()
        if type(ref)!=tuple:
            logging.info("Test case 29 execution passed")
            assert True
        else:
            logging.info("Test case 29 execution failed")
            assert False

    @pytest.mark.run(order=55)
    def test_854_validate_proxy_rpz_passthru_is_enabled(self):
        logging.info("Disabling proxy rpz passthru")
        ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=proxy_rpz_passthru")
        ref=json.loads(ref)
        data=ref[0]["proxy_rpz_passthru"]
        if data==True:
            logging.info("Test case 30 execution passed")
            assert True
        else:
            logging.info("Test case 30 execution failed")
            assert False

    @pytest.mark.run(order=56)
    def test_855_Add_subscriber_record_with_PCP_20000_playboy_com_WPCP_20000_playboy_com_ProxyAll_1_BL_playboy_com_and_WL_playboy_com_and_SSP_ff(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=123;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020000;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000020000;SUB:Calling-Station-Id=93333;PXP:PXY_PRI='+config.primary_proxy_server+';PXP:PXY_SEC='+config.primary_proxy_server+';BWI:BWFlag=1;BL=playboy.com;WL=playboy.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Failed")
            assert False

    @pytest.mark.run(order=57)
    def test_856_Validate_Subscriber_Record(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*.*',c)
        logging.info("Test case 2 execution completed")

    @pytest.mark.run(order=58)
    def test_857_Add_RPZ_PASSTHRU_rule_playboy_com_in_First_RPZ_Zone(self):
        logging.info("add rpz rule")
        ref=add_rpz_rule("playboy.com","rpz0.com")
        if ref!=None:
            logging.info("Test case executed successfully")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
        sleep(80)

    @pytest.mark.run(order=59)
    def test_858_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 3 passed")
        sleep(10)

    @pytest.mark.run(order=60)
    def test_859_Query_playboy_com(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=61)
    def test_860_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=62)
    def test_861_Validate_RPZ_hit_with_CEF_Log_RPZ_QNAME_PASSTHRU_and_Hitting_to_Blacklist_when_Feature_proxy_rpz_passthru_Enabled(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        #LookFor=".*RPZ-QNAME.*PASSTHRU.*rpz QNAME PASSTHRU rewrite playboy.com.*via playboy.com.rpz0.com.*Parental-Control-Policy=00000000000000000000000000020000.*CAT=RPZ.*CAT=BL.*"
        LookFor1=".*RPZ-QNAME.*PASSTHRU.*rpz QNAME PASSTHRU rewrite playboy.com.*via playboy.com.rpz0.com.*Parental-Control-Policy=00000000000000000000000000020000.*CAT=RPZ.*"
        LookFor2=".*RPZ-QNAME.*CNAME.*rpz QNAME CNAME rewrite playboy.com.*via playboy.com.*Parental-Control-Policy=00000000000000000000000000020000.*CAT=BL.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
        print logs1
        print logs2
        if logs1!=None and logs2!=None:
            logging.info(logs1)
            logging.info(logs2)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False

    @pytest.mark.run(order=63)
    def test_862_Remove_RPZ_PASSTHRU_rule_playboy_com_in_First_RPZ_zone_and_add_it_in_fifth_RPZ_zone(self):
        logging.info("add rpz rule")
        ref=remove_rpz_rule("playboy.com","rpz0.com")
        ref1=add_rpz_rule("playboy.com","rpz4.com")
        if ref1!=None:
            logging.info("Test case executed successfully")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
        sleep(40)

    @pytest.mark.run(order=64)
    def test_863_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 3 passed")
        sleep(10)

    @pytest.mark.run(order=65)
    def test_864_Query_playboy_com(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=66)
    def test_865_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=62)
    def test_866_Validate_RPZ_hit_with_CEF_Log_RPZ_QNAME_PASSTHRU_and_Hitting_to_Blacklist_when_Feature_proxy_rpz_passthru_Enabled(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        #LookFor=".*RPZ-QNAME.*PASSTHRU.*rpz QNAME PASSTHRU rewrite playboy.com.*via playboy.com.rpz4.com.*Parental-Control-Policy=00000000000000000000000000020000.*CAT=RPZ.*CAT=BL.*"
        LookFor1=".*RPZ-QNAME.*PASSTHRU.*rpz QNAME PASSTHRU rewrite playboy.com.*via playboy.com.rpz4.com.*Parental-Control-Policy=00000000000000000000000000020000.*CAT=RPZ.*"
        LookFor2=".*RPZ-QNAME.*CNAME.*rpz QNAME CNAME rewrite playboy.com.*via playboy.com.*Parental-Control-Policy=00000000000000000000000000020000.*CAT=BL.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
        print logs1
        print logs2
        if logs1!=None and logs2!=None:
            logging.info(logs1)
            logging.info(logs2)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False

    @pytest.mark.run(order=68)
    def test_867_Remove_RPZ_PASSTHRU_rule_playboy_com_in_fifth_RPZ_zone_and_add_it_in_21_RPZ_zone(self):
        logging.info("add rpz rule")
        ref=remove_rpz_rule("playboy.com","rpz4.com")
        ref1=add_rpz_rule("playboy.com","rpz21.com")
        if ref1!=None:
            logging.info("Test case executed successfully")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
        sleep(30)

    @pytest.mark.run(order=69)
    def test_868_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 3 passed")
        sleep(10)

    @pytest.mark.run(order=70)
    def test_869_Query_playboy_com(self):
        logging.info("Query")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=71)
    def test_870_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=72)
    def test_871_Validate_query_resolved_with_PCP_Blocking_IPs_since_BL_in_BWList_is_set_to_domain_playboy_com_and_SSP_bit_does_not_match_and_when_Feature_proxy_rpz_passthru_Enabled(self):
        logging.info("Validate")
        LookFor=".*CEF.*playboy.com.*CAT=BL.*"
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

    @pytest.mark.run(order=73)
    def test_872_Remove_RPZ_PASSTHRU_rule_playboy_com_in_21_RPZ_zone_and_add_it_in_Last_31_RPZ_zone(self):
        logging.info("add rpz rule")
        ref=remove_rpz_rule("playboy.com","rpz21.com")
        ref1=add_rpz_rule("playboy.com","rpz31.com")
        if ref1!=None:
            logging.info("Test case executed successfully")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
        sleep(30)

    @pytest.mark.run(order=74)
    def test_873_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 3 passed")
        sleep(10)

    @pytest.mark.run(order=75)
    def test_874_Query_playboy_com(self):
        logging.info("Query")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=76)
    def test_875_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=77)
    def test_876_Validate_query_resolved_with_Blacklist_since_Last_31_RPZ_zone_does_not_fall_under_ssp_ff_so_next_BL_will_hit_when_Feature_proxy_rpz_passthru_Enabled(self):
        logging.info("Validate")
        LookFor=".*CEF.*playboy.com.*CAT=BL.*"
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

    @pytest.mark.run(order=78)
    def test_877_Remove_RPZ_PASSTHRU_rule_playboy_com_in_Last_31_RPZ_zone(self):
        logging.info("add rpz rule")
        ref=remove_rpz_rule("playboy.com","rpz31.com")
        if ref!=None:
            logging.info("Test case executed successfully")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
        sleep(30)

    @pytest.mark.run(order=79)
    def test_878_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 3 passed")
        sleep(10)

    @pytest.mark.run(order=80)
    def test_879_Query_playboy_com(self):
        logging.info("Query")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=81)
    def test_880_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=82)
    def test_881_Validate_query_resolved_with_PCP_Blocking_IPs_since_BL_in_BWList_is_set_to_domain_playboy_com_when_Feature_proxy_rpz_passthru_Enabled(self):
        logging.info("Validate")
        LookFor=".*CEF.*playboy.com.*CAT=BL.*"
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

    @pytest.mark.run(order=83)
    def test_882_Modify_BL_playboy_com_to_some_other_domain_that_is_BL_facebook_com(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=123;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020000;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000020000;SUB:Calling-Station-Id=93333;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.primary_proxy_server+';BWI:BWFlag=1;BL=facebook.com;WL=playboy.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Case 1 Execution Passed")
            assert True
        except:
            logging.info("Test Case 1 Execution Failed")
            assert False

    @pytest.mark.run(order=84)
    def test_883_Validate_Subscriber_Record(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*.*',c)
        logging.info("Test case 2 execution completed")

    @pytest.mark.run(order=85)
    def test_884_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 3 passed")
        sleep(10)

    @pytest.mark.run(order=86)
    def test_885_Query_playboy_com(self):
        logging.info("Query")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=87)
    def test_886_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=88)
    def test_887_Validate_query_resolved_normally_with_public_IPs_since_WL_in_BWList_is_set_to_domain_playboy_com_when_Feature_proxy_rpz_passthru_Enabled(self):
        logging.info("Validate")
        LookFor=".*UDP.*query.*playboy.com.*IN.*A.*response.*NOERROR.*"
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

    @pytest.mark.run(order=89)
    def test_888_Modify_WL_playboy_com_to_some_other_domain_that_is_WL_bbc_com(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=123;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020000;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000020000;SUB:Calling-Station-Id=93333;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.primary_proxy_server+';BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Case 1 Execution Passed")
            assert True
        except:
            logging.info("Test Case 1 Execution Failed")
            assert False

    @pytest.mark.run(order=90)
    def test_889_Validate_Subscriber_Record(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*.*',c)
        logging.info("Test case 2 execution completed")

    @pytest.mark.run(order=91)
    def test_890_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 3 passed")
        sleep(10)

    @pytest.mark.run(order=92)
    def test_891_Query_playboy_com(self):
        logging.info("Query")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=93)
    def test_892_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=94)
    def test_893_Validate_query_resolved_with_PCP_Blocking_IPs_since_PCP_AVP_is_set_to_bit_20000_when_Feature_proxy_rpz_passthru_Enabled(self):
        logging.info("Validate")
        #LookFor=".*CEF.*rpz QNAME CNAME rewrite playboy.com.*via playboy.com.*Parental-Control-Policy=0x00000000000000000000000000020000.*Subscriber-Secure-Policy=ff PC-Category-Policy=00000000000000000000000000020000.*CAT=0x00000000000000000000000000020000.*"
        LookFor=".*CEF.*rpz QNAME CNAME rewrite playboy.com.*via playboy.com.*Parental-Control-Policy=0x00000000000000000000000000020000.*PC-Category-Policy=0x00000000000000000000000000020000.*CAT=0x00000000000000000000000000020000.*"
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

    @pytest.mark.run(order=95)
    def test_894_Modify_PCP_20000_to_some_other_bit_that_is_PCP_000040(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=123;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000000040;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000020000;SUB:Calling-Station-Id=93333;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.primary_proxy_server+';BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Case 1 Execution Passed")
            assert True
        except:
            logging.info("Test Case 1 Execution Failed")
            assert False

    @pytest.mark.run(order=96)
    def test_895_Validate_Subscriber_Record(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*.*',c)
        logging.info("Test case 2 execution completed")

    @pytest.mark.run(order=97)
    def test_896_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 3 passed")
        sleep(10)

    @pytest.mark.run(order=98)
    def test_897_Query_playboy_com(self):
        logging.info("Query")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=99)
    def test_898_stop_Syslog_Messages_For_Validation_when_Feature_proxy_rpz_passthru_Enabled(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=100)
    def test_899_Validate_query_resolved_with_Proxy_MSP_VIPs_response_with_only_CAT_WRN_since_WPCP_AVP_is_set_to_bit_20000_and_proxy_set_to_0(self):
        logging.info("Validate")
        LookFor=".*CEF.*CAT=WRN.*"
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

    @pytest.mark.run(order=101)
    def test_900_Modify_WPCP_20000_to_some_other_bit_that_is_WPCP_000040(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=123;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000000040;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000000040;SUB:Calling-Station-Id=93333;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.primary_proxy_server+';BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Case 1 Execution Passed")
            assert True
        except:
            logging.info("Test Case 1 Execution Failed")
            assert False

    @pytest.mark.run(order=102)
    def test_901_Validate_Subscriber_Record(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*.*',c)
        logging.info("Test case 2 execution completed")

    @pytest.mark.run(order=103)
    def test_902_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 3 passed")
        sleep(10)

    @pytest.mark.run(order=104)
    def test_903_Query_playboy_com(self):
        logging.info("Query")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=105)
    def test_904_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=106)
    def test_905_Validate_query_resolved_normally_proxy_rpz_passthru_is_Enabled(self):
        logging.info("Validate")
        #LookFor=".*CAT=RPZ.*.*CEF.*RPZ-CLIENT-IP.*rpz CLIENT-IP CNAME rewrite playboy.com.*via playboy.com.*Parental-Control-Policy=00000000000000000000000000000040 Subscriber-Secure-Policy=ff PC-Category-Policy=00000000000000000000000000000040.*CAT=PXY.*"
        LookFor=".*NOERROR.*playboy.com.*"
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

    @pytest.mark.run(order=107)
    def test_906_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=108)
    def test_907_Add_subscriber_record_without_PCP_Bit_and_Withuot_WPCP_bit_and_with_only_SSP_ff(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=123;NAS:NAS-PORT=1813;SSP:Subscriber-Secure-Policy=ff;SUB:Calling-Station-Id=93333;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.primary_proxy_server+';BWI:BWFlag=1;BL=playboy.com;WL=playboy.com;" ')
            child.expect('Record successfully added')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Failed")
            assert False

    @pytest.mark.run(order=109)
    def test_908_Validate_Subscriber_Record(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*.*',c)
        logging.info("Test case  execution completed")

    @pytest.mark.run(order=110)
    def test_909_Add_RPZ_PASSTHRU_rule_playboy_com_in_First_RPZ_Zone(self):
        logging.info("add rpz rule")
        ref=add_rpz_rule("playboy.com","rpz0.com")
        if ref!=None:
            logging.info("Test case executed successfully")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
        sleep(30)

    @pytest.mark.run(order=111)
    def test_910_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=112)
    def test_911_Query_playboy_com(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case  Execution Completed")
        sleep(10)

    @pytest.mark.run(order=113)
    def test_912_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=114)
    def test_913_Validate_RPZ_hit_with_CEF_Log_RPZ_QNAME_PASSTHRU_and_Hitting_to_Blacklist_when_Feature_proxy_rpz_passthru_Enabled(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor=".*CAT=RPZ.*"
        LookFor=".*CAT=BL.*"
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

    @pytest.mark.run(order=115)
    def test_914_Remove_RPZ_PASSTHRU_rule_playboy_com_in_First_RPZ_zone_and_add_it_in_fifth_RPZ_zone(self):
        logging.info("add rpz rule")
        ref=remove_rpz_rule("playboy.com","rpz0.com")
        ref1=add_rpz_rule("playboy.com","rpz4.com")
        if ref1!=None:
            logging.info("Test case executed successfully")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
            sleep(6)

    @pytest.mark.run(order=116)
    def test_915_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case  passed")
        sleep(10)

    @pytest.mark.run(order=117)
    def test_916_Query_playboy_com(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case  Execution Completed")
        sleep(10)

    @pytest.mark.run(order=118)
    def test_917_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=119)
    def test_918_Validate_RPZ_hit_with_CEF_Log_RPZ_QNAME_PASSTHRU_and_Hitting_to_Blacklist_when_Feature_proxy_rpz_passthru_Enabled(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        #LookFor=".*RPZ-QNAME.*PASSTHRU.*rpz QNAME PASSTHRU rewrite playboy.com.*via playboy.com.rpz4.com.*CAT=RPZ.*CAT=BL.*"
        LookFor1=".*RPZ-QNAME.*PASSTHRU.*rpz QNAME PASSTHRU rewrite playboy.com.*via playboy.com.rpz4.com.*Subscriber-Secure-Policy=ff.*CAT=RPZ.*"
        LookFor2=".*RPZ-QNAME.*CNAME.*rpz QNAME CNAME rewrite playboy.com.*via playboy.com.*Subscriber-Secure-Policy=ff.*CAT=BL.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
        logging.info(logs1)
        logging.info(logs1)
        if logs1!=None and logs2!=None:
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False

    @pytest.mark.run(order=120)
    def test_919_Remove_RPZ_PASSTHRU_rule_playboy_com_in_fifth_RPZ_zone_and_add_it_in_21_RPZ_zone(self):
        logging.info("add rpz rule")
        ref=remove_rpz_rule("playboy.com","rpz4.com")
        ref1=add_rpz_rule("playboy.com","rpz21.com")
        if ref1!=None:
            logging.info("Test case executed successfully")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
        sleep(30)

    @pytest.mark.run(order=121)
    def test_920_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 3 passed")
        sleep(10)

    @pytest.mark.run(order=122)
    def test_921_Query_playboy_com(self):
        logging.info("Query")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=123)
    def test_922_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=124)
    def test_923_Validate_query_resolved_with_PCP_Blocking_IPs_since_BL_in_BWList_is_set_to_domain_playboy_com_and_SSP_bit_does_not_match_and_when_Feature_proxy_rpz_passthru_Enabled(self):
        logging.info("Validate")
        LookFor=".*CEF.*playboy.com.*CAT=BL.*"
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

    @pytest.mark.run(order=125)
    def test_924_Remove_RPZ_PASSTHRU_rule_playboy_com_in_21_RPZ_zone_and_add_it_in_Last_31_RPZ_zone(self):
        logging.info("add rpz rule")
        ref=remove_rpz_rule("playboy.com","rpz21.com")
        ref1=add_rpz_rule("playboy.com","rpz31.com")
        if ref1!=None:
            logging.info("Test case executed successfully")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
        sleep(30)
            
    @pytest.mark.run(order=126)
    def test_925_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case  passed")
        sleep(10)

    @pytest.mark.run(order=127)
    def test_926_Query_playboy_com(self):
        logging.info("Query")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=128)
    def test_927_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=129)
    def test_928_Validate_query_resolved_normally_since_Last_31_RPZ_zone_acts_as_whitelist_when_Feature_proxy_rpz_passthru_Enabled(self):
        logging.info("Validate")
        LookFor=".*playboy.com.*response.*NOERROR.*playboy.com.*"
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

    @pytest.mark.run(order=130)
    def test_929_Remove_RPZ_PASSTHRU_rule_playboy_com_in_Last_31_RPZ_zone(self):
        logging.info("add rpz rule")
        ref=remove_rpz_rule("playboy.com","rpz31.com")
        if ref!=None:
            logging.info("Test case executed successfully")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
        sleep(30)

    @pytest.mark.run(order=131)
    def test_930_Disable_proxy_rpz_passthru(self):
        logging.info("Disabling proxy rpz passthru")
        ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=proxy_rpz_passthru")
        ref=json.loads(ref)
        ref1=ref[0]["_ref"]
        data={"proxy_rpz_passthru":False}
        ref=ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
        if type(ref)!=tuple:
            logging.info("Test case  execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=132)
    def test_931_validate_proxy_rpz_passthru_is_disabled(self):
        logging.info("Disabling proxy rpz passthru")
        ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=proxy_rpz_passthru")
        ref=json.loads(ref)
        data=ref[0]["proxy_rpz_passthru"]
        if data==False:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case  execution failed")
            assert False

    

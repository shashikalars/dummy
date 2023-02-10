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

def validate_public_suffix_list (IP_address,command,Host_address=config.client_ip):
    try:
        logging.info ("Checking Log Info")
        connection=SSH(str(IP_address))
        result= connection.send_command(command)
        return result
    except grep:
        logging.info ("Pattern not found")


def enable_mgmt_port_for_dns(member):
    ref=mem_ref_string(member)
    data={"use_lan_ipv6_port":True,"use_mgmt_ipv6_port":True}
    ref1=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
    logging.info (ref1)
    time.sleep(30)
    
def change_default_route():
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
    child.logfile=sys.stdout
    child.expect('#')
    child.sendline('ip route del default via '+config.unit_1_router+' dev eth1 table main')
    child.expect('#')
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
    

def reboot_the_member(operation):
        logging.info("change the memory of a member")
        cmd="reboot_system -H "+str(vm_id)+" -a "+operation
        result = subprocess.check_output(cmd, shell=True)
        print result

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

def change_default_route():
    ref=ib_NIOS.wapi_request('GET', object_type="grid")
    ref=json.loads(ref)[0]['_ref']
    data={"enable_gui_api_for_lan_vip":"true","dns_resolver_setting": {"resolvers": [config.resolver_ip]}}
    #data={"dns_resolver_setting": {"resolvers": ["10.0.2.35"]}}
    ref1=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
    child.logfile=sys.stdout
    child.expect('#')
    child.sendline('ip route del default via '+config.unit_1_router+' dev eth1 table main')
    child.expect('#')
    child.sendline('ip route add default via 10.36.0.1 dev eth0 table main')
    child.sendline('exit')
    child.expect(pexpect.EOF)
    time.sleep(20)

def enable_GUI_and_API_access_through_LAN_and_MGMT():
    ref=ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.Master1_MGMT_IP)
    print ref
    ref=json.loads(ref)[0]['_ref']
    print ref
    data={"enable_gui_api_for_lan_vip":True}
    ref1=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data),grid_vip=config.Master1_MGMT_IP)
    print ref1
    time.sleep(120)

class Network(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_001_start_TP_service(self):
        enable_GUI_and_API_access_through_LAN_and_MGMT()
        #change_default_route()
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
        sleep(300)
        logging.info("Test Case 2 Execution Completed")
        assert True
 
    @pytest.mark.run(order=1)
    def test_002_Start_DNS_Service(self):
        logging.info("Start DNS Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        logging.info(get_ref)
        res = json.loads(get_ref)
        for i in res:
            ref=i["_ref"]
            logging.info("Modify a enable_dns")
            data = {"enable_dns": True,"use_mgmt_port":True}
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
        #data={"allow_recursive_query":True,"allow_query":[{"_struct": "addressac","address":"Any","permission":"ALLOW"}],"forwarders":[config.forwarder_ip],"logging_categories":{"log_rpz":True}}
        data={"allow_recursive_query":True,"allow_query":[{"_struct": "addressac","address":"Any","permission":"ALLOW"}],"forwarders":[config.forwarder_ip],"logging_categories":{"log_rpz":True,"log_queries":True,"log_responses":True}}
        put_ref=ib_NIOS.wapi_request('PUT', object_type=get_ref1,fields=json.dumps(data))
        logging.info(put_ref)
	print put_ref
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
        change_default_route()
        logging.info("Enabling parental control with proxy settings")
        response = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber")
        response = json.loads(response)
        response=response[0]["_ref"]
        logging.info(response)
        data={"enable_parental_control": True,"cat_acctname":"infoblox_sdk", "cat_password":"LinWmRRDX0q","category_url":"https://dl.zvelo.com/","pc_zone_name":"pc.com","cat_update_frequency":1}
	    #data={"enable_parental_control": True,"cat_acctname":"infoblox_sdk", "cat_password":"LinWmRRDX0q","category_url":"https://dl.zvelo.com/","pc_zone_name":"pc.com","cat_update_frequency":1,"proxy_url":config.zvelo_proxy,"proxy_username":config.zvelo_username,"proxy_password":config.zvelo_password}
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
        #proxy_url=response[0]["proxy_url"]
        if pc==True and act_name=="infoblox_sdk":
            logging.info("Test Case execution passed")
            assert True
        else:
            logging.info("Test Case execution Failed")
            assert False
    
    @pytest.mark.run(order=14)
    def  test_009_Add_the_Subscriber_Site_as_site2_DCA_Subscriber_Query_count_and_DCA_Blocklist_White_List_Enabled(self):
        logging.info("Addsubscriber site site2 with IB-FLEX DCA Subscriber Query Count and DCA Blocklist whitelist Enable")
        data={"name":"site2","maximum_subscribers":100000,"members":[{"name":config.grid_fqdn},{"name":config.grid_member1_fqdn},{"name":config.grid_member2_fqdn}],"nas_gateways":[{"ip_address":config.rad_client_ip,"name":"nas1","shared_secret":"testing123"},{"ip_address":config.rad_client_ip_lan,"name":"nas2","shared_secret":"testing123"}],"dca_sub_query_count":True,"dca_sub_bw_list":True}
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
    def  test_010_Validate_subscriber_site_site2_Is_Added_with_IB_FLEX_Member_DCA_Subscriber_Query_count_and_DCA_Blocklist_White_List_Enabled(self):
        logging.info("Validating subscriber site site2 added with IB-FLEX DCA Subscriber Query Count and DCA Blocklist whitelist Enable")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=dca_sub_query_count,dca_sub_bw_list,dca_sub_bw_list")
        reference=json.loads(reference)
        if reference[0]["dca_sub_query_count"]==True and reference[0]["dca_sub_bw_list"]==True:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=16)
    def test_011_Start_the_subscriber_service_on_members_and_Validate(self):
        logging.info("Start the subscriber service on members and validate")
        member=[config.grid_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn]
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
    def test_012_start_DCA_service_on_Grid_Master_Member(self):
        logging.info("Enable DCA on the IB-FLEX Grid Master member")
        data = {"enable_dns": True, "enable_dns_cache_acceleration": True}
        DCA_capable=[config.grid_member1_fqdn]
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

    @pytest.mark.run(order=18)
    def test_013_Validate_DCA_service_running_on_Grid_Master_Member(self):
        logging.info("Validate_DCA_service_running")
        sys_log_master = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member1_vip)+' " tail -4000 /infoblox/var/infoblox.log"'
        out1 = commands.getoutput(sys_log_master)
        logging.info (out1)
        res1=re.search(r'DNS cache acceleration is now started',out1)
        if res1!=None:
            logging.info("Test Case Execution passed")
            assert True
        else:
            logging.info("Test Case Execution failed")
            assert False

    @pytest.mark.run(order=9)
    def test_014_start_category_download_Messages_logs_on_master(self):
        logging.info("Starting category download Messages Logs on master")
        log("start","/storage/zvelo/log/category_download.log",config.grid_vip)
        log("start","/storage/zvelo/log/category_download.log",config.grid_member1_vip)
        log("start","/storage/zvelo/log/category_download.log",config.grid_member2_vip)
        logging.info("Test case 116 execution passed")
        time.sleep(2300)

    @pytest.mark.run(order=10)
    def test_015_stop_category_download_Messages_logs_on_master(self):
        logging.info("Stop Syslog Messages Logs on master")
        log("stop","/storage/zvelo/log/category_download.log",config.grid_vip)
        log("stop","/storage/zvelo/log/category_download.log",config.grid_member1_vip)
        log("stop","/storage/zvelo/log/category_download.log",config.grid_member2_vip)
        logging.info("Test case execution passed")

    @pytest.mark.run(order=11)
    def test_016_validate_for_zvelo_download_data_completion_on_master(self):
        time.sleep(10)
        logging.info("Validating category download Messages Logs for data completion")
        LookFor=".*zvelodb download completed.*"
        logs=logv(LookFor,"/storage/zvelo/log/category_download.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case Execution passed")
            assert True
        else:
            logging.info("Test Case Execution failed")
            assert False

    @pytest.mark.run(order=11)
    def test_017_validate_for_zvelo_download_data_completion_on_member1(self):
        time.sleep(10)
        logging.info("Validating category download Messages Logs for data completion")
        LookFor=".*zvelodb download completed.*"
        logs=logv(LookFor,"/storage/zvelo/log/category_download.log",config.grid_member1_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case Execution passed")
            assert True
        else:
            logging.info("Test Case Execution failed")
            assert False

    @pytest.mark.run(order=11)
    def test_018_validate_for_zvelo_download_data_completion_on_member2(self):
        time.sleep(10)
        logging.info("Validating category download Messages Logs for data completion")
        LookFor=".*zvelodb download completed.*"
        logs=logv(LookFor,"/storage/zvelo/log/category_download.log",config.grid_member2_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case Execution passed")
            assert True
        else:
            logging.info("Test Case Execution failed")
            assert False

    
    @pytest.mark.run(order=35)
    def test_020_validate_public_suffix_list_file_on_member1(self):
        logging.info("validate_public_suffix_list_file_on_member1")
        public_suffix_list=validate_public_suffix_list(config.grid_member1_vip,"ls /storage/subscriber_services/ | grep -i 'public_suffix_list.dat'")
        if public_suffix_list!=[]:
            logging.info("Test case 34 Execution passed")
            assert True
        else:
            logging.info("Test case 34 Execution failed")
            assert False
    
    @pytest.mark.run(order=12)
    def test_021_In_Grid_Properties_Configure_Loopback_IP_as_Primary_DNS_Resolver(self):
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
    def test_022_Validate_At_Grid_Properties_DNS_Resolver_Is_Configured_with_loopback_IP(self):
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
    def  test_023_update_the_Subscriber_Site_as_site2_With_blocking_ips(self):
        logging.info("Update the subscriber site with blocking ips")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        reference=json.loads(reference)[0]["_ref"]
        logging.info("Adding blocking ip's to subscriber site site2")
        data={"blocking_ipv4_vip1": "1.1.1.1","blocking_ipv4_vip2": "2.2.2.2","msps":[{"ip_address": config.proxy_server1}],"spms": [{"ip_address": "10.12.11.11"}]}       
        get_ref=ib_NIOS.wapi_request('PUT', object_type=reference,fields=json.dumps(data))
        logging.info(get_ref)
        print(get_ref)
        restart_the_grid()
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
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=15)
    def  test_024_Validate_subscriber_site_site2_Is_updated_with_blocking_ips(self):
        restart_the_grid()
        logging.info("Validating subscriber site site2 updated with blocking ip's")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=blocking_ipv4_vip1,blocking_ipv4_vip2")
        reference=json.loads(reference)
        if reference[0]["blocking_ipv4_vip1"]=="1.1.1.1" and reference[0]["blocking_ipv4_vip2"]=="2.2.2.2":
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
    
    #Site level test cases
    @pytest.mark.run(order=121)
    def test_025_Validate_default_value_set_for_bypass_in_site_level(self):
        logging.info("Validate default value set for bypass in site level")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass site site2')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")
    
    @pytest.mark.run(order=25)
    def test_026_stop_the_subscriber_services_on_all_the_members(self):
        logging.info("stop the subscriber services on all the members")
        ref=stop_subscriber_collection_services_for_added_site([config.grid_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn])
        if ref!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=26)
    def test_027_delete_the_subscriber_site_site2(self):
        logging.info("delete the subscriber site site2")
        ref=delete_subscriber_site("site2")
        if ref!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
    
    @pytest.mark.run(order=39)
    def test_028_Add_the_subscriber_site_SITE2_with_2_members_one_is_DCA_capable(self):
        logging.info("Add the subscriber site site2 with 2 members one is DCA capable")
        data={"blocking_ipv4_vip1": "1.1.1.1","blocking_ipv4_vip2": "2.2.2.2","msps":[{"ip_address": config.proxy_server1}],"spms": [{"ip_address": "10.12.11.11"}],"name":"site2","maximum_subscribers":100000,"members":[{"name":config.grid_fqdn},{"name":config.grid_member1_fqdn}],"nas_gateways":[{"ip_address":config.rad_client_ip,"name":"nas1","shared_secret":"testing123"},{"ip_address":config.rad_client_ip_lan,"name":"nas2","shared_secret":"testing123"}],"dca_sub_query_count":True,"dca_sub_bw_list":True}
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
    def  test_029_validate_the_subscriber_site_SITE2_is_addeed(self):
        logging.info("validate the subscriber site site2 is added")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        reference=json.loads(reference)
        if reference[0]["name"]=="site2":
            logging.info("Test case execution passed")
            sleep(20)
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=39)
    def test_030_Add_the_subscriber_site_SITE3_with_2_members(self):
        logging.info("Add the subscriber site with 2 members")
        data={"blocking_ipv4_vip1": "1.1.1.1","blocking_ipv4_vip2": "2.2.2.2","msps":[{"ip_address": config.proxy_server1}],"spms": [{"ip_address": "10.12.11.11"}],"name":"site3","maximum_subscribers":100000,"members":[{"name":config.grid_member2_fqdn}],"nas_gateways":[{"ip_address":config.rad_client_ip,"name":"nas1","shared_secret":"testing123"},{"ip_address":config.rad_client_ip_lan,"name":"nas2","shared_secret":"testing123"}]}
        get_ref=ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data))
        logging.info(get_ref)
        print get_ref
        if type(get_ref)!=tuple:
            reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
            reference=json.loads(reference)
            if reference[1]["name"]==data["name"]:
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
    def  test_031_validate_the_subscriber_site_SITE3_is_added_with_2_members(self):
        logging.info("validate the subscriber site site3 with 2 members")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        reference=json.loads(reference)
        if reference[1]["name"]=="site3":
            logging.info("Test case execution passed")
            sleep(20)
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=41)
    def test_032_Start_the_subscriber_service_on_all_the_members(self):
        logging.info("Start the subscriber service on all the members")
        ref=start_subscriber_collection_services_for_added_site([config.grid_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn])
        if ref!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=42)
    def test_033_Validate_subscriber_service_is_running_on_members(self):
        restart_the_grid()
        logging.info("Validating subscriber collection services started on members")
        members=[config.grid_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn]
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
    
    @pytest.mark.run(order=272)
    def test_034_start_infoblox_Messages_logs_on_master(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("test case passed")

    @pytest.mark.run(order=121)
    def test_035_set_bypass_value_to_on_in_site_level_for_site2(self):
        logging.info("set bypass value to on in site level for site2")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass on site site2')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member1_fqdn+'.*',c)
        sleep(20)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=122)
    def test_036_stop_Syslog_Messages_Logs_on_master(self):
        logging.info("Stopping Syslog Logs on DCA Member")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=123)
    def test_037_Validate_for_bypass_logs_on_master(self):
        logging.info("Validate for bypass logs")
        LookFor=".*Subscriber Secure Bypass enabled on the member "+config.grid_fqdn+".*"
        LookFor1=".*Subscriber Secure Bypass enabled on the member "+config.grid_member1_fqdn+".*"
        logs1=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        logs2=logv(LookFor1,"/infoblox/var/infoblox.log",config.grid_vip)
        logging.info(logs1)
        if logs1!=None and logs2!=None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False
    ''' 
    @pytest.mark.run(order=106)
    def test_038_Replace_radcient_client_ips_In_Radius_message_files_with_Configuration_file_values(self):
        logging.info("Replace Radclient IPs in radius message files with configuration file values")
        dig_cmd = 'sed -i s/rad_client_ip/'+str(config.rad_client_ip)+'/g RFE_9980_part1_radfiles/*; sed -i s/client_ip/'+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/*;sed -i s/client_ip2/'+str(config.client_ip2)+'/g RFE_9980_part1_radfiles/*;sed -i s/client_ip3/'+str(config.client_ip3)+'/g RFE_9980_part1_radfiles/*;sed -i s/client_ip4/'+str(config.client_ip4)+'/g RFE_9980_part1_radfiles/*; sed -i s/client_network_8/'+str(config.client_network_8)+'/g RFE_9980_part1_radfiles/*;sed -i s/client_network_24/'+str(config.client_network_24)+'/g RFE_9980_part1_radfiles/*; sed -i s/client_network_16/'+str(config.client_network_16)+'/g RFE_9980_part1_radfiles/*; sed -i s/client_network_32/'+str(config.client_network_32)+'/g RFE_9980_part1_radfiles/*'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)
    '''
    @pytest.mark.run(order=106)
    def test_038_Replace_radcient_client_ips_In_Radius_message_files_with_Configuration_file_values(self):
        logging.info("Replace Radclient IPs in radius message files with configuration file values")
        dig_cmd = 'sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_PCP_start_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip2)+'/g RFE_9980_part1_radfiles/RFE_9980_PCP_start_client2.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_PCP_stop_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_PCP_update_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_PCP_zvelo_block_start_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_PCP_zvelo_cat1_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_PCP_zvelo_cat2_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_qc_false_update_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_SSP_start_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_unknown_dynamic_start_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_WPCP_start_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_WPCP_stop_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_WPCP_update_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_CAIC_start_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_non_sub_start_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_only_SSP_start_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_only_unknown_start_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_PCP_set_to_all_FF_start_client1.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip2)+'/g RFE_9980_part1_radfiles/RFE_9980_non_sub_start_client2.txt;sed -i s/Framed-IP-Address.*/Framed-IP-Address\ \=\ '+str(config.client_ip1)+'/g RFE_9980_part1_radfiles/RFE_9980_WPCP_start_client2.txt;'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)

    @pytest.mark.run(order=107)
    def test_039_Copy_Subscriber_Record_radfiles_to_radclient(self):
        logging.info("Copy Subscriber Record radius message files to RAD Client")
        dig_cmd = 'sshpass -p infoblox scp -pr RFE_9980_part1_radfiles root@'+str(config.rad_client_ip)+':/root/'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        print "Copied the files to radclient"
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=116)
    def test_040_From_Radclient_Send_Start_Radius_Message_to_the_site2_member_where_bypass_is_enabled_at_site_level(self):
        logging.info("From Rad client send Start Radius message to_the_site_members_where_bypass_is_enabled at site level")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_start_client1.txt -r 1 '+str(config.Master1_MGMT_IP)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(20)

    @pytest.mark.run(order=117)
    def test_041_Validate_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
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

    @pytest.mark.run(order=120)
    def test_042_start_Syslog_Messages_logs_on_site2_Member_where_the_bypass_is_enabled(self):
        logging.info("Starting Syslog Messages Logs on site2 Member where the bypass is enabled")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 128 passed")
        sleep(20)

    @pytest.mark.run(order=121)
    def test_043_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
        logging.info("Validate DCA Cache content shows Cache is empty")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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
    def test_044_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_for_site2_Member_where_bypass_is_enabled(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com for site2 member where bypass is enabled")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        res1=re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        res2=re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        res3=re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        res4=re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        if res1!=None and res2!=None and res3==None and res4==None:
            assert True
            sleep(20)
        else:
            assert False
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=123)
    def test_045_stop_Syslog_Messages_Logs_on_site2_Member(self):
        logging.info("Stopping Syslog Logs on site2 Member")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=124)
    def test_046_Validate_logs_when_get_response_from_Bind_for_PCP_domain_times_com_for_site2_member_where_bypass_is_enabled(self):
        logging.info("Validate logs for times.com  when get response from Bind for PCP domain times.com for site2 member where bypass is enabled")
        LookFor1=".*named.*info CEF.*times.com.*"
        LookFor2=".*NOERROR.*times.com.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_member1_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_member1_vip)
        if logs1==None and logs2!=None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=125)
    def test_047_Validate_PCP_Domain_times_com_cached_to_DCA_When_Send_Query_From_PCP_bit_Matched_Subscriber_client(self):
        logging.info("Validate times.com domain cached to DCA when send query from the PCP bit matched subscriber client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=126)
    def test_048_Validate_when_get_response_from_Bind_for_PCP_domain_times_com_Cache_hit_count_not_increased_and_Miss_cache_count_increased(self):
        logging.info("Validate when get response from Bind for PCP domain times.com Cache hit count not increased and Miss cache count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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

    @pytest.mark.run(order=120)
    def test_049_start_Syslog_Messages_logs_on_site2_Member_where_bypass_is_enabled(self):
        logging.info("Starting Syslog Messages Logs on site2 member where bypass is enabled")
        log("start","/var/log/syslog",config.grid_member1_vip)
        sleep(20)
        logging.info("test case 128 passed")

    @pytest.mark.run(order=122)
    def test_050_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_for_site2_Member_where_bypass_is_enabled(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com for site2 member where bypass is enabled")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        sleep(10)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=123)
    def test_051_stop_Syslog_Messages_Logs_on_site2_Member_where_bypass_is_enabled(self):
        logging.info("Stopping Syslog Logs on site 2 member where bypass is enabled")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=124)
    def test_052_Validate_no_Logs_when_get_response_from_DCA_for_PCP_domain_times_com_from_site2_member(self):
        logging.info("Validate Named CEF Log for times.com  when get response from DCA")
        LookFor1=".*named.*info CEF.*times.com.*"
        LookFor2=".*NOERROR.*times.com.*IN A.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_member1_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_member1_vip)
        if logs1==None and logs2==None:
            logging.info("Test case execution Passed")
            sleep(20)
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=126)
    def test_053_Validate_when_get_response_from_DCA_for_PCP_domain_times_com_Cache_hit_count_increased_and_Miss_cache_count_not_increased(self):
        logging.info("Validate when get response from Bind for PCP domain times.com Cache hit count increased and Miss_cache count not increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*1.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=116)
    def test_054_From_Radclient_Send_Start_Radius_Message_to_the_site3_member_where_bypass_is_not_enabled_at_site_level(self):
        restart_the_grid()
        logging.info("From Rad client send Start Radius message to_the_site3 members where bypass is not enabled at site level")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_start_client1.txt -r 1 '+str(config.grid_member2_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(20)

    @pytest.mark.run(order=117)
    def test_055_Validate_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
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

    @pytest.mark.run(order=120)
    def test_056_start_Syslog_Messages_logs_on_site3_Member(self):
        logging.info("Starting Syslog Messages Logs on site3 Member")
        log("start","/var/log/syslog",config.grid_member2_vip)
        logging.info("test case 128 passed")
        sleep(10)

    @pytest.mark.run(order=122)
    def test_057_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_site3_Member_Validate_returns_Blocked_IPs_in_response(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using site3 Member and get PCP Blocked IPs response")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member2_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site3-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site3-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        sleep(10)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=123)
    def test_058_stop_Syslog_Messages_Logs_on_site3_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_member2_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=124)
    def test_059_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_times_com_for_site3_member(self):
        logging.info("Validate Named CEF Log for times.com  when get response from Bind for PCP domain times.com for site3 member")
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


    @pytest.mark.run(order=25)
    def test_060_stop_the_subscriber_services_on_all_the_members(self):
        logging.info("stop the subscriber services on all the members")
        ref=stop_subscriber_collection_services_for_added_site([config.grid_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn])
        if ref!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=26)
    def test_061_delete_the_subscriber_site_site2_and_site3(self):
        logging.info("delete the subscriber site site2")
        ref1=delete_subscriber_site("site2")
        ref2=delete_subscriber_site("site3")
        if ref1!=None and ref2!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=39)
    def test_062_Add_the_subscriber_site_site2_with_no_members(self):
        logging.info("Add the subscriber site with no members")
        data={"blocking_ipv4_vip1": "1.1.1.1","blocking_ipv4_vip2": "2.2.2.2","msps":[{"ip_address": config.proxy_server1}],"spms": [{"ip_address": "10.12.11.11"}],"name":"site2","maximum_subscribers":100000,"nas_gateways":[{"ip_address":config.rad_client_ip,"name":"nas1","shared_secret":"testing123"},{"ip_address":config.rad_client_ip_lan,"name":"nas2","shared_secret":"testing123"}]}
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
    def  test_063_validate_the_subscriber_site_site2_is_added_with_no_members(self):
        logging.info("validate the subscriber site site2 is added with no members")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        reference=json.loads(reference)
        if reference[0]["name"]=="site2":
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=272)
    def test_064_start_infoblox_Messages_logs_on_master(self):
        logging.info("Starting infoblox Messages Logs on master")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("test case passed")

    @pytest.mark.run(order=121)
    def test_065_show_bypass_value_in_site_level_when_no_members_assigned_to_site2(self):
        logging.info("show bypass value in site level when no members assigned to site2")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass site site2')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure site <site2> does not contain any members..*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=121)
    def test_066_set_bypass_value_to_on_in_site_level_when_no_members_assigned_to_site2(self):
        logging.info("set bypass value to on in site level when no members assigned to site2")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass on site site2')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure site <site2> does not contain any members..*',c)
        logging.info("Test case execution Completed")
        sleep(20)

    @pytest.mark.run(order=122)
    def test_067_stop_infoblox_Messages_Logs_on_master(self):
        logging.info("Stopping Syslog Logs on Master")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=123)
    def test_068_Validate_infoblox_logs_for_bypass_message(self):
        logging.info("Validate infoblox logs for bypass message")
        LookFor=".*set subscriber_secure_data bypass on site site2.*"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=39)
    def test_069_Add_the_subscriber_site_site2_with_IB_FLEX_and_815_member_without_enabling_subscriber_service(self):
        logging.info("Add_the_subscriber_site_site2_with master and 815 member_without_enabling subscriber service")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        get_ref=json.loads(get_ref)
        ref=get_ref[0]["_ref"]
        #data={"members":[{"name":config.grid_member2_fqdn}]}
        data={"members":[{"name":config.grid_member1_fqdn},{"name":config.grid_member2_fqdn}]}
        get_ref=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
        logging.info(get_ref)
        print get_ref
        if type(get_ref)!=tuple:
            reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
            reference=json.loads(reference)
            if reference[0]["name"]=="site2":
                logging.info("Test case execution passed")
                sleep(20)
                assert True
            else:
                logging.info("Test case execution Failed")
                assert False
        else:
            logging.info(get_ref)
            logging.info("Test case execution failed")
            assert False
    
    @pytest.mark.run(order=15)
    def  test_070_Validate_subscriber_site_site2_Is_Added_with_master_and_815_member_without_enabling_subscriber_service(self):
        logging.info("Validating subscriber site site2 added with 2225 and 815 member without enabling subscriber service")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=members")
        reference=json.loads(reference)
        print reference[0]["members"][0]["name"]
        print reference[0]["members"][1]["name"]
        if reference[0]["members"][0]["name"]==config.grid_member1_fqdn and reference[0]["members"][1]["name"]==config.grid_member2_fqdn:
            logging.info("Test case execution passed")
            assert True
            sleep(50)
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=121)
    def test_071_set_bypass_value_to_ON_in_site_level_when_members_assigned_to_site_without_enabling_the_service_in_site2(self):
        logging.info("set bypass value to on in site level when members assigned to site without enabling the service in site2")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass on site site2')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")
        sleep(20)

    @pytest.mark.run(order=121)
    def test_072_validate_bypass_value_to_ON_in_site_level_when_members_assigned_to_site_without_starting_subscriber_services(self):
        logging.info("show bypass value to on in site level when members assigned to site without enabling subscriber services")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass site site2')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=41)
    def test_073_Start_the_subscriber_service_on_members_of_site2(self):
        logging.info("Start the subscriber service on site2 members")
        ref=start_subscriber_collection_services_for_added_site([config.grid_member1_fqdn,config.grid_member2_fqdn])
        if ref!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=42)
    def test_074_Validate_subscriber_service_is_running_on_site2_members(self):
        restart_the_grid()
        logging.info("Validating subscriber collection services started on site2 members")
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

    @pytest.mark.run(order=116)
    def test_075_From_Radclient_Send_Start_Radius_Message_to_the_site2_members(self):
        logging.info("From Rad client send Start Radius message to_the_site2 members")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_start_client1.txt -r 1 '+str(config.grid_member1_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=117)
    def test_076_Validate_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000040000000000000000.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=120)
    def test_077_start_Syslog_Messages_logs_on_site2_Member_815(self):
        logging.info("Starting Syslog Messages Logs on site2 Member 815")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 128 passed")
        sleep(20)

    @pytest.mark.run(order=122)
    def test_078_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_for_site2_member_815(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        res1=re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        res2=re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        res3=re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        res4=re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        if res1!=None and res2!=None and res3==None and res4==None:
            assert True
            sleep(10)
        else:
            assert False
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=123)
    def test_079_stop_Syslog_Messages_Logs_on_Member_815(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=124)
    def test_080_Validate_syslogs_when_get_response_for_PCP_domain_times_com(self):
        logging.info("Validate syslogs_when_get_response_for_PCP_domain_times_com")
        LookFor1=".*named.*info CEF.*times.com.*"
        LookFor2=".*NOERROR.*times.com.*IN A.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_member1_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_member1_vip)
        if logs1==None and logs2!=None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=120)
    def test_081_start_Syslog_Messages_logs_on_2225_Member(self):
        logging.info("Starting Syslog Messages Logs on master Member")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 128 passed")
        sleep(30)

    @pytest.mark.run(order=121)
    def test_082_Validate_DCA_Cache_content_shows_Cache_is_empty_for_site2_member_2225(self):
        logging.info("Validate DCA Cache content shows Cache is empty for site2 member 2225")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel-cache')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*times.com.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=122)
    def test_083_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_com_for_site2_member_2225(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        res1=re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        res2=re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        res3=re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        res4=re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        if res1!=None and res2!=None and res3==None and res4==None:
            assert True
            sleep(10)
        else:
            assert False
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=123)
    def test_084_stop_Syslog_Messages_Logs_on_2225_Member(self):
        logging.info("Stopping Syslog Logs on 2225 member")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")


    @pytest.mark.run(order=125)
    def test_085_Validate_PCP_Domain_times_com_did_not_cached_to_DCA_When_Send_Query_From_PCP_bit_Matched_Subscriber_client_for_2225_member(self):
        logging.info("Validate times.com domain not cached to DCA when send query from the PCP bit matched subscriber client for 2225 member")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=126)
    def test_086_Validate_when_get_response_from_Bind_for_PCP_domain_times_com_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased(self):
        logging.info("Validate when get response from Bind for PCP domain times.com Cache hit count not increased and Miss_cache count count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*1.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=120)
    def test_087_start_Syslog_Messages_logs_on_2225_Member(self):
        logging.info("Starting Syslog Messages Logs on 2225 Member")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 128 passed")
        sleep(10)

    @pytest.mark.run(order=122)
    def test_088_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_2225_Member(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using 2225 Member")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        sleep(20)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=123)
    def test_089_stop_Syslog_Messages_Logs_on_2225_Member(self):
        logging.info("Stopping Syslog Logs on 2225 member")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=124)
    def test_090_Validate_Named_CEF_Log_Logs_when_get_response_from_DCA_for_PCP_domain_times_com(self):
        logging.info("Validate Named CEF Log for times.com  when get response from DCA")
        LookFor1=".*named.*info CEF.*times.com.*"
        LookFor2=".*NOERROR.*times.com.*IN A.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_member1_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_member1_vip)
        if logs1==None and logs2==None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=126)
    def test_091_Validate_when_get_response_from_DCA_for_PCP_domain_times_com_Cache_hit_count_increased_and_Miss_cache_count_not_increased(self):
        logging.info("Validate when get response from Bind for PCP domain times.com Cache hit count increased and Miss_cache count not increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*2.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test case execution Completed")
    
    @pytest.mark.run(order=126)
    def test_092_power_off_the_member_2225(self):
        logging.info("power off the member")
        cmd="reboot_system -H "+str(config.member1_vm_id)+" -a poweroff"
        result = subprocess.check_output(cmd, shell=True)
        print result
        sleep(20)

    @pytest.mark.run(order=272)
    def test_093_start_Syslog_Messages_logs_on_master(self):
        logging.info("Starting Syslog Messages Logs on master")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("test case passed")

    @pytest.mark.run(order=121)
    def test_094_set_bypass_value_to_off_in_site_level_when_2225_member_assigned_to_site_went_offline(self):
        logging.info("set bypass value to off in site level when 2225  member assigned to site went offline")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass off site site2')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Failed to set Subscriber Secure Bypass state on the member '+config.grid_member1_fqdn+': connection failure.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=121)
    def test_095_validate_bypass_value_to_off_in_site_level_when_2225_member_assigned_to_site_went_offline(self):
        logging.info("show bypass value to on in site level when 2225 member assigned to site went offline")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass site site2')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Failed to retrieve Subscriber Secure Bypass state from the member '+config.grid_member1_fqdn+': connection failure.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=122)
    def test_096_stop_Syslog_Messages_Logs_on_master(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=123)
    def test_097_Validate_bypass_logs_when_2225_member_went_offline(self):
        logging.info("Validate bypass logs when 2225 member went offline")
        LookFor=".*Subscriber Secure Bypass disabled on the member "+config.grid_member2_fqdn+".*"
        LookFor1='.*Failed to set Subscriber Secure Bypass state on the member '+config.grid_member1_fqdn+': connection failure.*'
        print LookFor1
        logs1=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        logs2=logv(LookFor1,"/infoblox/var/infoblox.log",config.grid_vip)
        print logs1
        print logs2
        logging.info(logs1)
        if logs1!=None and logs2!=None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False
    
    @pytest.mark.run(order=126)
    def test_098_poweron_the_IBFLEX_member(self):
        logging.info("poweron the IB_FLEX member")
        cmd="reboot_system -H "+str(config.member1_vm_id)+" -a poweron"
        result = subprocess.check_output(cmd, shell=True)
        print result
        sleep(300)

    @pytest.mark.run(order=121)
    def test_099_validate_bypass_value_to_on_in_site_level_when_members_assigned_to_site_went_offline_become_online(self):
        logging.info("show bypass value to on in site level when members assigned to site went offline")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass site site2')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member1_fqdn+'.*.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=121)
    def test_100_set_bypass_value_to_on_in_site_level_when_the_site_does_not_exist(self):
        logging.info("show bypass value to on in site level when the site does not exist")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass on site site10')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure site <site10> does not exist..*',c)

    @pytest.mark.run(order=121)
    def test_101_show_bypass_value_in_site_level_when_the_site_does_not_exist(self):
        logging.info("show bypass value to on in site level when the site does not exist")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass site site10')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure site <site10> does not exist..*',c)

    #OVERRIDE FROM GRID LEVEL
    @pytest.mark.run(order=39)
    def test_102_Add_the_subscriber_site_site3_with_2_members(self):
        logging.info("Add the subscriber site site3 with  1415 and ib flex member")
        data={"blocking_ipv4_vip1": "1.1.1.1","blocking_ipv4_vip2": "2.2.2.2","msps":[{"ip_address": config.proxy_server1}],"spms": [{"ip_address": "10.12.11.11"}],"name":"site3","maximum_subscribers":100000,"members":[{"name":config.grid_fqdn}],"nas_gateways":[{"ip_address":config.rad_client_ip,"name":"nas1","shared_secret":"testing123"},{"ip_address":config.rad_client_ip_lan,"name":"nas2","shared_secret":"testing123"}],"dca_sub_query_count":True,"dca_sub_bw_list":True}
        get_ref=ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data))
        logging.info(get_ref)
        print get_ref
        if type(get_ref)!=tuple:
            reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
            reference=json.loads(reference)
            if reference[1]["name"]==data["name"]:
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
    def  test_103_validate_the_subscriber_site_site3_is_added(self):
        logging.info("validate the subscriber site site3 is added")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        reference=json.loads(reference)
        if reference[1]["name"]=="site3":
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=41)
    def test_104_Start_the_subscriber_service_on_members(self):
        logging.info("Start the subscriber service on members")
        ref=start_subscriber_collection_services_for_added_site([config.grid_fqdn])
        if ref!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=42)
    def test_105_Validate_subscriber_service_is_running_on_members(self):
        restart_the_grid()
        sleep(30)
        logging.info("Validating subscriber collection services started on members")
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


    @pytest.mark.run(order=121)
    def test_106_set_bypass_value_to_off_in_grid_level(self):
        logging.info("show bypass value to off in grid level")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass off grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_fqdn+'.*.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member2_fqdn+'.*.*',c)


    @pytest.mark.run(order=121)
    def test_107_show_bypass_value_in_grid_level(self):
        logging.info("show bypass value to off on grid level")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_fqdn+'.*.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member2_fqdn+'.*.*',c)

    @pytest.mark.run(order=121)
    def test_108_set_bypass_value_to_on_in_site_level_site2_when_set_to_off_at_grid_level(self):
        logging.info("set bypass value to on in site level when set to off at grid leve")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass on site site2')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")
        sleep(20)

    @pytest.mark.run(order=121)
    def test_109_validate_bypass_value_to_on_in_site_level_site2_when_set_to_off_at_grid_level(self):
        logging.info("show bypass value to on in site level site2 whenset to off at grid level")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass site site2')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=116)
    def test_110_From_Radclient_Send_Start_Radius_Message_to_the_site2_members_where_bypass_is_enabled_at_site_level(self):
        logging.info("From Rad client send Start Radius message to_the_site2 members where bypass is enabled at site level")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_start_client1.txt -r 1 '+str(config.Member1_MGMT_IP)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=117)
    def test_111_Validate_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000040000000000000000.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=120)
    def test_112_start_Syslog_Messages_logs_on_site2_Member(self):
        logging.info("Starting Syslog Messages Logs on site2 Member")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 128 passed")
        sleep(20)


    @pytest.mark.run(order=122)
    def test_113_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_com_using_2225_member(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using 2225 member")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        res1=re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        res2=re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        res3=re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        res4=re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        if res1!=None and res2!=None and res3==None and res4==None:
            assert True
            sleep(10)
        else:
            assert False
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=123)
    def test_114_stop_Syslog_Messages_Logs_on_2225_Member(self):
        logging.info("Stopping Syslog Logs on 2225 member")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=124)
    def test_115_Validate_syslogs_when_get_response_for_PCP_domain_times_com(self):
        logging.info("Validate syslogs_when_get_response_for_PCP_domain_times_com")
        LookFor1=".*named.*info CEF.*times.com.*"
        LookFor2=".*NOERROR.*times.com.*IN A.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_member1_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_member1_vip)
        if logs1==None and logs2!=None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=125)
    def test_116_Validate_PCP_Domain_times_com_did_not_cached_to_DCA_When_Send_Query_From_PCP_bit_Matched_Subscriber_client(self):
        logging.info("Validate times.com domain not cached to DCA when send query from the PCP bit matched subscriber client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=126)
    def test_117_Validate_when_get_response_from_Bind_for_PCP_domain_times_com_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased(self):
        logging.info("Validate when get response from Bind for PCP domain times.com Cache hit count not increased and Miss_cache count count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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

    @pytest.mark.run(order=122)
    def test_118_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_2225_Member(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB_FLEX Member")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        sleep(10)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=126)
    def test_119_Validate_when_get_response_from_Bind_for_PCP_domain_times_com_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased(self):
        logging.info("Validate when get response from Bind for PCP domain times.com Cache hit count not increased and Miss_cache count count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*1.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=121)
    def test_120_set_bypass_value_to_on_in_grid_level(self):
        logging.info("show bypass value to on in grid level")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass on grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_fqdn+'.*.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member2_fqdn+'.*.*',c)
        sleep(20)


    @pytest.mark.run(order=121)
    def test_121_show_bypass_value_in_grid_level(self):
        logging.info("show bypass value to on in grid level")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_fqdn+'.*.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member2_fqdn+'.*.*',c)

    @pytest.mark.run(order=121)
    def test_122_set_bypass_value_to_off_in_site_level_site2_when_set_to_on_at_grid_level(self):
        logging.info("set bypass value to off in site level when set to on at grid level")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass off site site2')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")
        sleep(50)

    @pytest.mark.run(order=121)
    def test_123_validate_bypass_value_to_off_in_site_level_site2_when_set_to_on_at_grid_level(self):
        logging.info("show bypass value to off in site level site2 whenset to on at grid level")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass site site2')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=116)
    def test_124_From_Radclient_Send_Start_Radius_Message_to_the_site3_members_where_bypass_is_not_enabled_at_site_level_IBFLEX_member(self):
        logging.info("From Rad client send Start Radius message to_the_site2 members where bypass is not enabled at site level ib flex member")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_start_client1.txt -r 1 '+str(config.grid_member1_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=117)
    def test_125_Validate_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        restart_the_grid()
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000040000000000000000.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=116)
    def test_126_From_Radclient_Send_Start_Radius_Message_to_the_site3_members_where_bypass_is_not_enabled_at_site_level_ib_flex_member(self):
        logging.info("From Rad client send Start Radius message to_the_site2 members where bypass is not enabled at site level")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_start_client2.txt -r 1 '+str(config.grid_member1_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=117)
    def test_127_Validate_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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
    def test_128_start_Syslog_Messages_logs_on_site2_member(self):
        logging.info("Starting Syslog Messages Logs on site2 Member")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 128 passed")
        sleep(20)


    @pytest.mark.run(order=122)
    def test_129_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_using_ib_flex_member(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using ib flex member")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        res1=re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        res2=re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        res3=re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        res4=re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        if res1!=None and res2!=None and res3!=None and res4!=None:
            assert True
            sleep(10)
        else:
            assert False
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=123)
    def test_130_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on ib flex member")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=124)
    def test_131_Validate_syslogs_when_get_response_for_PCP_domain_times_com(self):
        logging.info("Validate syslogs_when_get_response_for_PCP_domain_times_com")
        LookFor1=".*named.*info CEF.*times.com.*"
        LookFor2=".*NOERROR.*times.com.*IN A.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_member1_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_member1_vip)
        if logs1!=None and logs2!=None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False
    
    @pytest.mark.run(order=125)
    def test_132_Validate_PCP_Domain_times_com_did_not_cached_to_DCA_When_Send_Query_From_PCP_bit_Matched_Subscriber_client(self):
        logging.info("Validate times.com domain not cached to DCA when send query from the PCP bit matched subscriber client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel-cache')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        res1=re.search(r'.*times.com,A,IN.*AA,A,times.com.*',c)
        res2=re.search(r'.*0x00000000000000040000000000000000.*',c)
        if res1==None and res2==None:
            assert True
        else:
            assert False
        logging.info("Test case execution Completed")
    
    @pytest.mark.run(order=126)
    def test_133_Validate_when_get_response_from_Bind_for_PCP_domain_times_com_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased(self):
        logging.info("Validate when get response from Bind for PCP domain times.com Cache hit count not increased and Miss_cache count count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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

    @pytest.mark.run(order=120)
    def test_134_start_Syslog_Messages_logs_on_IB_FLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB FLEX Member")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 128 passed")
        sleep(20)


    @pytest.mark.run(order=122)
    def test_135_Send_Query_from_PCP_bit_not_match_Subscriber_client_for_PCP_Domain_times(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip2+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        res1=re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        res2=re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        res3=re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        res4=re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        if res1!=None and res2!=None and res3==None and res4==None:
            assert True
            sleep(20)
        else:
            assert False
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=123)
    def test_136_stop_Syslog_Messages_Logs_on_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=124)
    def test_137_Validate_syslogs_when_get_response_for_PCP_domain_times_com(self):
        logging.info("Validate syslogs_when_get_response_for_PCP_domain_times_com")
        LookFor1=".*named.*info CEF.*times.com.*"
        LookFor2=".*NOERROR.*times.com.*IN A.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_member1_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_member1_vip)
        if logs1==None and logs2!=None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=125)
    def test_138_Validate_PCP_Domain_times_com_cached_to_DCA_When_Send_Query_From_PCP_not_bit_Matched_Subscriber_client(self):
        logging.info("Validate times.com domain cached to DCA when send query from the PCP bit matched subscriber client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel-cache')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        res1=re.search(r'.*times.com,A,IN.*AA,A,times.com.*',c)
        print res1
        res2=re.search(r'.*0x00000000000000040000000000000000.*',c)
        print res2
        if res1!=None and res2!=None:
            assert True
        else:
            assert False
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=126)
    def test_139_Validate_when_get_response_from_Bind_for_PCP_domain_times_com_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased(self):
        logging.info("Validate when get response from Bind for PCP domain times.com Cache hit count not increased and Miss_cache count count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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

    @pytest.mark.run(order=120)
    def test_140_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 128 passed")
        sleep(20)


    @pytest.mark.run(order=122)
    def test_141_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB_FLEX Member")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        res1=re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        res2=re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        res3=re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        res4=re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        if res1!=None and res2!=None and res3!=None and res4!=None:
            assert True
            sleep(10)
        else:
            assert False

    @pytest.mark.run(order=123)
    def test_142_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=124)
    def test_143_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_times_com(self):
        logging.info("Validate Named CEF Log for times.com  when get response from Bind")
        LookFor1=".*fp-rte.*info CEF.*times.com.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_member1_vip)
        if logs1!=None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=126)
    def test_144_Validate_when_get_response_from_Bind_for_PCP_domain_times_com_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased(self):
        logging.info("Validate when get response from Bind for PCP domain times.com Cache hit count not increased and Miss_cache count count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*1.*',c)
        assert re.search(r'.*Cache miss count.*.*',c)
        logging.info("Test case execution Completed")

    #Member level test cases

    @pytest.mark.run(order=121)
    def test_145_set_bypass_value_to_off_in_grid_level(self):
        logging.info("show bypass value to off in grid level")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass off grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_fqdn+'.*.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member2_fqdn+'.*.*',c)
        sleep(20)


    @pytest.mark.run(order=121)
    def test_146_show_bypass_value_in_grid_level(self):
        logging.info("show bypass value to off in grid level")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_fqdn+'.*.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member2_fqdn+'.*.*',c)

    @pytest.mark.run(order=121)
    def test_147_set_bypass_value_to_off_at_site_level(self):
        logging.info("set bypass value to off at site level")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass off site site2')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")
        sleep(20)

    @pytest.mark.run(order=121)
    def test_148_validate_bypass_value_to_off_in_site_level(self):
        logging.info("show bypass value to off in site level")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass site site2')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=121)
    def test_149_set_bypass_value_to_on_in_member_level(self):
        logging.info("show bypass value to off in grid level")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass on')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member1_fqdn+'.*',c)
        sleep(20)

    @pytest.mark.run(order=121)
    def test_150_show_bypass_value_on_in_member_level(self):
        logging.info("show bypass value to on in member level")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member1_fqdn+'.*',c)

    @pytest.mark.run(order=116)
    def test_151_From_Radclient_Send_Start_Radius_Message_to_member_where_bypass_is_enabled_at_member_level(self):
        restart_the_grid()
        logging.info("From Rad client send Start Radius message to the member where bypass is enabled at member level")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_start_client1.txt -r 1 '+str(config.Member1_MGMT_IP)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=117)
    def test_152_Validate_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000040000000000000000.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=116)
    def test_153_From_Radclient_Send_Start_Radius_Message_to_the_members_where_bypass_is_enabled_at_member_level(self):
        restart_the_grid()
        logging.info("From Rad client send Start Radius message to the member where bypass is enabled at member level")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_start_client2.txt -r 1 '+str(config.grid_member1_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=117)
    def test_154_Validate_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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
    def test_155_start_Syslog_Messages_logs_on_site2_Member(self):
        logging.info("Starting Syslog Messages Logs on site2 Member")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 128 passed")
        sleep(10)


    @pytest.mark.run(order=122)
    def test_156_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        res1=re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        res2=re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        res3=re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        res4=re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        if res1!=None and res2!=None and res3==None and res4==None:
            assert True
        else:
            assert False
        logging.info("Test case execution Completed")
        sleep(20)

    @pytest.mark.run(order=123)
    def test_157_stop_Syslog_Messages_Logs_on_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=124)
    def test_158_Validate_syslogs_when_get_response_for_PCP_domain_times_com(self):
        logging.info("Validate syslogs_when_get_response_for_PCP_domain_times_com")
        LookFor1=".*named.*info CEF.*times.com.*"
        LookFor2=".*NOERROR.*times.com.*IN A.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_member1_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_member1_vip)
        if logs1==None and logs2!=None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=125)
    def test_159_Validate_PCP_Domain_times_com_did_not_cached_to_DCA_When_Send_Query_From_PCP_bit_Matched_Subscriber_client(self):
        logging.info("Validate times.com domain not cached to DCA when send query from the PCP bit matched subscriber client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel-cache')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        res1=re.search(r'.*times.com,A,IN.*AA,A,times.com.*',c)
        res2=re.search(r'.*0x00000000000000040000000000000000.*',c)
        if res1!=None and res2==None:
            assert True
        else:
            assert False
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=126)
    def test_160_Validate_when_get_response_from_Bind_for_PCP_domain_times_com_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased(self):
        logging.info("Validate when get response from Bind for PCP domain times.com Cache hit count not increased and Miss_cache count count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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

    @pytest.mark.run(order=120)
    def test_161_start_Syslog_Messages_logs_on_site2_Member(self):
        logging.info("Starting Syslog Messages Logs on site2 Member")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 128 passed")
        sleep(20)

    @pytest.mark.run(order=122)
    def test_162_Send_Query_from_PCP_bit_not_match_Subscriber_client_for_PCP_Domain_times(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        res1=re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        res2=re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        res3=re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        res4=re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        if res1!=None and res2!=None and res3==None and res4==None:
            assert True
        else:
            assert False
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=123)
    def test_163_stop_Syslog_Messages_Logs_on_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=124)
    def test_164_Validate_syslogs_when_get_response_for_PCP_domain_times_com(self):
        logging.info("Validate syslogs_when_get_response_for_PCP_domain_times_com")
        LookFor1=".*named.*info CEF.*times.com.*"
        LookFor2=".*NOERROR.*times.com.*IN A.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_member1_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_member1_vip)
        if logs1==None and logs2==None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=125)
    def test_165_Validate_PCP_Domain_times_com_not_cached_to_DCA_When_Send_Query_From_PCP_not_bit_Matched_Subscriber_client(self):
        logging.info("Validate times.com domain cached to DCA when send query from the PCP bit matched subscriber client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel-cache')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        res1=re.search(r'.*times.com,A,IN.*AA,A,times.com.*',c)
        res2=re.search(r'.*0x00000000000000040000000000000000.*',c)
        if res1!=None and res2==None:
            assert True
        else:
            assert False
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=126)
    def test_166_Validate_when_get_response_from_Bind_for_PCP_domain_times_com_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased(self):
        logging.info("Validate when get response from Bind for PCP domain times.com Cache hit count not increased and Miss_cache count count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*1.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test case execution Completed")
#9980

    @pytest.mark.run(order=61)
    def test_167_Enable_DCA_subscriber_Query_count_logging_on_site_site3(self):
        logging.info("Enable DCA subscriber Query count logging on site site3")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        print get_ref
        get_ref=json.loads(get_ref)[0]["_ref"]
        data={"dca_sub_query_count":True,"dca_sub_bw_list":True}
        res = ib_NIOS.wapi_request('PUT', object_type=get_ref,fields=json.dumps(data))
        print res
        if type(res)!=tuple:
            logging.info("Test case execution passed")
            time.sleep(5)
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=62)
    def test_168_validate_Enable_DCA_subscriber_Query_count_logging_on_site(self):
        logging.info("Validate DCA subscriber Query count reporting and Enable DCA subscriber Allowed and Blocked list support are enabled")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=dca_sub_bw_list,dca_sub_query_count")
        get_ref=json.loads(get_ref)
        print get_ref
        if get_ref[1]["dca_sub_query_count"]==True and get_ref[1]["dca_sub_bw_list"]==True:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=62)
    def test_169_reboot_the_system(self):
        prod_reboot(config.grid_member1_vip)

    @pytest.mark.run(order=116)
    def test_170_From_Radclient_Send_Start_Radius_Message_to_member_where_bypass_is_enabled_at_member_level(self):
        restart_the_grid()
        logging.info("From Rad client send Start Radius message to the member where bypass is enabled at member level")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_start_client1.txt -r 1 '+str(config.grid_member1_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(50)

    @pytest.mark.run(order=117)
    def test_171_Validate_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000040000000000000000.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=116)
    def test_172_From_Radclient_Send_Start_Radius_Message_to_the_members_where_bypass_is_enabled_at_member_level(self):
        restart_the_grid()
        logging.info("From Rad client send Start Radius message to the member where bypass is enabled at member level")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_start_client2.txt -r 1 '+str(config.grid_member1_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=117)
    def test_173_Validate_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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
    def test_174_start_Syslog_Messages_logs_on_site2_Member(self):
        logging.info("Starting Syslog Messages Logs on site2 Member")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 128 passed")
        sleep(20)


    @pytest.mark.run(order=122)
    def test_175_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        res1=re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        res2=re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        res3=re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        res4=re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        if res1!=None and res2!=None and res3==None and res4==None:
            sleep(20)
            assert True
        else:
            assert False
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=123)
    def test_176_stop_Syslog_Messages_Logs_on_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=124)
    def test_177_Validate_syslogs_when_get_response_for_PCP_domain_times_com(self):
        logging.info("Validate syslogs_when_get_response_for_PCP_domain_times_com")
        LookFor1=".*named.*info CEF.*times.com.*"
        LookFor2=".*NOERROR.*times.com.*IN A.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_member1_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_member1_vip)
        if logs1==None and logs2!=None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=125)
    def test_178_Validate_PCP_Domain_times_com_did_not_cached_to_DCA_When_Send_Query_From_PCP_bit_Matched_Subscriber_client(self):
        logging.info("Validate times.com domain not cached to DCA when send query from the PCP bit matched subscriber client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel-cache')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        res1=re.search(r'.*times.com,A,IN.*AA,A,times.com.*',c)
        res2=re.search(r'.*0x00000000000000040000000000000000.*',c)
        if res1!=None and res2==None:
            assert True
        else:
            assert False
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=126)
    def test_179_Validate_when_get_response_from_Bind_for_PCP_domain_times_com_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased(self):
        logging.info("Validate when get response from Bind for PCP domain times.com Cache hit count not increased and Miss_cache count count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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

    @pytest.mark.run(order=120)
    def test_180_start_Syslog_Messages_logs_on_site2_Member(self):
        logging.info("Starting Syslog Messages Logs on site2 Member")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 128 passed")
        sleep(20)

    @pytest.mark.run(order=122)
    def test_181_Send_Query_from_PCP_not_match_Subscriber_client_for_PCP_Domain_times(self):
        logging.info("Perform Query from PCP match Subscriber client for PCP Domain times.com")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        res1=re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        res2=re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        res3=re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        res4=re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        if res1!=None and res2!=None and res3==None and res4==None:
            assert True
        else:
            assert False
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=123)
    def test_182_stop_Syslog_Messages_Logs_on_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=124)
    def test_183_Validate_syslogs_when_get_response_for_PCP_domain_times_com(self):
        logging.info("Validate syslogs_when_get_response_for_PCP_domain_times_com")
        LookFor1=".*named.*info CEF.*times.com.*"
        LookFor2=".*NOERROR.*times.com.*IN A.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_member1_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_member1_vip)
        if logs1==None and logs2==None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=126)
    def test_184_Validate_when_get_response_from_Bind_for_PCP_domain_times_com_Cache_hit_count_not_increased_and_Miss_cache_count_increased(self):
        logging.info("Validate when get response from Bind for PCP domain times.com Cache hit count not increased and Miss cache count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*1.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test case execution Completed")


    @pytest.mark.run(order=120)
    def test_185_start_Syslog_Messages_logs_on_site2_Member(self):
        logging.info("Starting Syslog Messages Logs on site2 Member")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 128 passed")
        sleep(20)


    @pytest.mark.run(order=122)
    def test_186_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        res1=re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        res2=re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        res3=re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        res4=re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        if res1!=None and res2!=None and res3==None and res4==None:
            assert True
        else:
            assert False
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=123)
    def test_187_stop_Syslog_Messages_Logs_on_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=124)
    def test_188_Validate_syslogs_when_get_response_for_PCP_domain_times_com(self):
        logging.info("Validate syslogs_when_get_response_for_PCP_domain_times_com")
        #LookFor1=".*named.*info CEF.*times.com.*"
        LookFor2=".*NOERROR.*times.com.*IN A.*"
        #logs1=logv(LookFor1,"/var/log/syslog",config.grid_member1_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_member1_vip)
        if logs2==None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=126)
    def test_189_Validate_when_get_response_from_DCA_for_PCP_domain_times_com_Cache_hit_count_increased_and_Miss_cache_count_not_increased(self):
        logging.info("Validate when get response from Bind for PCP domain times.com Cache hit count increased and Miss_cache not count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*2.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test case execution Completed")
    
    @pytest.mark.run(order=37)
    def test_190_Add_Subscriber_Record_with_whitelist_set_to_netflix_and_blacklist_set_to_linkedin(self):
        try:
            logging.info("Add_Subscriber_Record_with_whitelist_set_to_netflix_and_blacklist_set_to_linkedin")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=9999732d-34590346;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;PXP:PXY_PRI=0ac4065f;PXS:PXY_SEC=0AC4800D;SUB:Calling-Station-Id=110361221;BWI:BWFlag=1;BL=linkedin.com;WL=netflix.com;"')
            child.expect('Record successfully added')
            logging.info("Test Case 37 Execution Passed")
            assert True
        except:
            logging.info("Test Case 37 Execution Failed")
            assert False

    @pytest.mark.run(order=38)
    def test_191_Validate_Subscriber_Record_with_whitelist_set_to_netflix_and_blacklist_set_to_linkedin(self):
        logging.info("Validate_Subscriber_Record_with_whitelist_set_to_netflix_and_blacklist_set_to_linkedin")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'/32|LID:N/A|IPS:N/A.*',c)
        logging.info("Test case 38 execution completed")

    @pytest.mark.run(order=39)
    def test_192_start_Syslog_Messages_logs_on_master(self):
        logging.info("Starting Syslog Messages Logs on master")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 39 passed")
        sleep(10)

    @pytest.mark.run(order=122)
    def test_193_Send_Query_for_linkedin_com(self):
        logging.info("Perform Query from PCP match Subscriber client for PCP Domain times.com")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' linkedin.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        res1=re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        res2=re.search(r'.*linkedin.com.*IN.*A.*',str(dig_result))
        res3=re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        res4=re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        if res1!=None and res2!=None and res3==None and res4==None:
            assert True
            sleep(20)
        else:
            assert False
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=41)
    def test_194_stop_Syslog_Messages_Logs_on_master(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test Case 41 Execution Completed")

    @pytest.mark.run(order=42)
    def test_195_Validate_linkedin_com_returns_public_IPs_in_response(self):
        logging.info("Validate_linkedin_com_returns_public_IPs_in_response")
        logging.info("Validating Sylog Messages Logs")
        LookFor="response.*NOERROR.*linkedin.com.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
        logging.info(logs)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 42 Execution Passed")
            assert True
        else:
            logging.info("Test Case 42 Execution Failed")
            assert False

    @pytest.mark.run(order=125)
    def test_196_Validate_PCP_Domain_linkedin_com_cached_to_DCA_When_Send_Query_From_PCP_bit_Matched_Subscriber_client(self):
        logging.info("Validate times.com domain not cached to DCA when send query from the PCP bit matched subscriber client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel-cache')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        res1=re.search(r'.*linkedin.com,A,IN.*AA,A,linkedin.com.*',c)
        if res1!=None:
            assert True
        else:
            assert False
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=20)
    def test_197_add_32_rpz_zone(self):
        logging.info("Adding 32 RPZ zones")
        for i in range(31,-1,-1):
            print str(i)
            #data={"fqdn": "rpz"+str(i)+".com","grid_primary":[{"name": config.grid_fqdn,"stealth":False},{"name": config.grid_fqdn1,"stealth":False},{"name": config.grid_fqdn2,"stealth":False}]}
            data={"fqdn": "rpz"+str(i)+".com","grid_primary":[{"name": config.grid_member1_fqdn,"stealth":False}]}
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
    def test_198_restart_the_grid(self):
        logging.info("Restaring the grid")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(60)
        logging.info("Test Case 21 Execution passed")

    @pytest.mark.run(order=22)
    def test_199_validate_32_rpz_zone_added(self):
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

    @pytest.mark.run(order=29)
    def test_200_enable_proxy_rpz_passthru(self):
        logging.info("Disabling proxy rpz passthru")
        ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=proxy_rpz_passthru")
        ref=json.loads(ref)
        ref1=ref[0]["_ref"]
        data={"proxy_rpz_passthru":True}
        ref=ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
        if type(ref)!=tuple:
            logging.info("Test case 29 execution passed")
            assert True
        else:
            logging.info("Test case 29 execution failed")
            assert False

    @pytest.mark.run(order=30)
    def test_201_validate_proxy_rpz_passthru_is_enabled(self):
        restart_the_grid()
        logging.info("Enabling proxy rpz passthru")
        ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=proxy_rpz_passthru")
        ref=json.loads(ref)
        data=ref[0]["proxy_rpz_passthru"]
        if data==True:
            logging.info("Test case 30 execution passed")
            assert True
            sleep(20)
        else:
            logging.info("Test case 30 execution failed")
            assert False

    @pytest.mark.run(order=85)
    def test_202_Add_Subscriber_Record_with_SSP_ff(self):
        logging.info("Add Subscriber Record with Proxy-All=1, Dynamic=0, Unknown=0 and with specific 128 bits for PCP and WPCP")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=9999732d-34590346;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000000001;SUB:Calling-Station-Id=110361221;BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;IPA:IP6=2620:10a:6000:2500:230:48ff:fed5:d928;PXP:PXY_PRI=0AC4800D;PXS:PXY_SEC=0AC4800D"')
        child.expect('Record successfully added')
        logging.info("test case 85 Completed")

    @pytest.mark.run(order=86)
    def test_203_Validate_Subscriber_Record_with_SSP_set_to_ff(self):
        logging.info("Validate Subscriber Record with SSP set to ff")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*10.36.0.151/32|LID:N/A|IPS:N/A.*',c)
        logging.info("Test case 86 execution Completed")


    @pytest.mark.run(order=112)
    def test_204_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 112 Execution Completed")

    @pytest.mark.run(order=113)
    def test_205_Query_First_8_RPZ_Passthru_rules(self):
        try:
            logging.info("Query last RPZ passthru rule")
            for i in range(8):
                dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@10.36.0.151 "dig @'+str(config.grid_member1_vip)+' pass'+str(i)+' +noedns -b 10.36.0.151"'
                dig_cmd1 = os.system(dig_cmd)
            logging.info("Test Case 113 Execution Passed")
            sleep(20)
            assert True
        except:
            logging.info("Test Case 113 Execution Failed")
            assert False

    @pytest.mark.run(order=114)
    def test_206_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test Case 114 Execution Completed")

    @pytest.mark.run(order=115)
    def test_207_Validate_First_8_RPZ_Passthru_returns_Public_IPs_in_response(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(8):
            LookFor="response.*NOERROR.*pass"+str(i)+".*IN.*A"
            logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
            logging.info(logs)
            if logs!=None:
                logging.info(logs)
                logging.info("Test Case 115 Execution Passed")
                sleep(20)
                assert True
            else:
                logging.info("Test Case 115 Execution Failed")
                assert False

    @pytest.mark.run(order=116)
    def test_208_Validate_CEF_Log_for_PASSTHRU_in_syslog(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(5):
            LookFor="PASSTHRU rewrite pass"+str(i)+".* via pass"+str(i)+".rpz"+str(i)+".com"
            logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
            logging.info (logs)
            LookFor2="RPZ"
            logs2=logv(LookFor2,"/var/log/syslog",config.grid_member1_vip)
            logging.info (logs2)
            if logs!=None and logs2!=None:
                logging.info(logs)
                logging.info("Test Case 116 Execution Passed")
                assert True
            else:
                logging.info("Test Case 116 Execution Failed")
                assert False

    @pytest.mark.run(order=117)
    def test_209_Validate_all_these_8_RPZ_Passthru_rules_did_not_cache_in_dca(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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
    def test_210_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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

    @pytest.mark.run(order=121)
    def test_211_set_bypass_value_to_off_in_member_level(self):
        restart_the_grid()
        logging.info("show bypass value to off in grid level")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass off')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member1_fqdn+'.*',c)
        sleep(20)

    @pytest.mark.run(order=121)
    def test_212_show_bypass_value_off_in_member_level(self):
        logging.info("show bypass value to off in member level")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member1_fqdn+'.*',c)
    
    @pytest.mark.run(order=116)
    def test_213_From_Radclient_Send_Start_Radius_Message_with_PCP_Policy_and_Proxy_All_Configured(self):
        restart_the_grid()
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_start_client1.txt -r 1 '+str(config.grid_member1_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=117)
    def test_214_Validate_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000040000000000000000.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=116)
    def test_215_From_Radclient_Send_Start_Radius_Message_with_PCP_Policy_and_Proxy_All_Configured(self):
        restart_the_grid()
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_start_client2.txt -r 1 '+str(config.grid_member1_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(5)

    @pytest.mark.run(order=119)
    def test_216_Validate_Subscriber_Record_without_Proxy_all_set_and_Different_PCP_Policy_bit_than_above(self):
        logging.info("Validate Subscriber Record without Proxy-All set different PCP Policy bit than the above")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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
    def test_217_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 128 passed")
        sleep(20)

    @pytest.mark.run(order=122)
    def test_218_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_Blocked_IPs_in_response_from_Bind_As_Not_DCA_Cache(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and get PCP Blocked IPs response from Bind as times.com not in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test case execution Completed")
        sleep(20)

    @pytest.mark.run(order=123)
    def test_219_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=124)
    def test_220_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_times_com(self):
        logging.info("Validate Named CEF Log for times.com  when get response from Bind")
        LookFor=".*named.*info CEF.*times.com.*CAT=0x00000000000000040000000000000000.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
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
    def test_221_Validate_PCP_Domain_times_com_did_not_cached_to_DCA_When_Send_Query_From_PCP_bit_Matched_Subscriber_client(self):
        logging.info("Validate times.com domain not cached to DCA when send query from the PCP bit matched subscriber client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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
    def test_222_Validate_when_get_response_from_Bind_for_PCP_domain_times_com_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased(self):
        logging.info("Validate when get response from Bind for PCP domain times.com Cache hit count not increased and Miss_cache count count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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
    def test_223_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 135 passed")
        sleep(20)

    @pytest.mark.run(order=128)
    def test_224_Send_Query_from_NON_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_cached_DCA_with_PCP_word(self):
        logging.info("Perform Query from NON PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and Validate get NORMAL response times.com domain is cached to DCA with PCP word")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip2+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=129)
    def test_225_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=130)
    def test_226_Validate_NO_CEF_Log_Logs_when_get_NORMAL_response_for_PCP_domain_times_com_when_send_query_from_NON_PCP_bit_match_client(self):
        logging.info("Validate NO CEF Log for times.com  when get NORMAL response when send query from NON PCP bit match client")
        LookFor="info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
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
    def test_227_Validate_PCP_Domain_times_com_get_cached_to_DCA_When_Send_Query_From_NON_PCP_bit_Matched_Subscriber_client(self):
        logging.info("Validate times.com domain get cached to DCA when send query from the NON PCP bit matched subscriber client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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
    def test_228_Validate_when_get_response_from_Bind_for_PCP_domain_times_com_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased(self):
        logging.info("Validate when get response from Bind for PCP domain times.com Cache hit count not increased ansd Miss_cache count count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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
    def test_229_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 141 passed")

    @pytest.mark.run(order=134)
    def test_230_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_Blocked_IPs_in_response_from_DCA_As_times_com_domain_is_already_DCA_Cache(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and get PCP Blocked IPs response from DCA as times.com is already in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test case execution Completed")
        sleep(20)

    @pytest.mark.run(order=135)
    def test_231_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=136)
    def test_232_Validate_DCA_CEF_Log_Logs_when_get_response_from_DCA_for_PCP_domain_times_com(self):
        logging.info("Validate DCA CEF Log for times.com  when get response from DCA")
        LookFor="fp-rte.*info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
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
    def test_233_Validate_when_get_response_from_DCA_for_PCP_domain_times_com_Cache_hit_count_is_increased_and_Miss_cache_count_count_not_increased(self):
        logging.info("Validate when get response from DCA for PCP domain times.com Cache hit count is get increased and Miss cache count not increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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

    @pytest.mark.run(order=121)
    def test_234_set_bypass_value_to_off_in_grid_level(self):
        restart_the_grid()
        logging.info("show bypass value to off in grid level")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass off grid')
        child.expect('Infoblox >')
        c= child.before
        #assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member2_fqdn+'.*',c)
        sleep(20)
    
    @pytest.mark.run(order=121)
    def test_235_show_bypass_value_to_off_in_grid_level(self):
        restart_the_grid()
        logging.info("show bypass value to off in grid level")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass grid')
        child.expect('Infoblox >')
        c= child.before
        #assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member2_fqdn+'.*',c)
        sleep(20)



#9981
    @pytest.mark.run(order=37)
    def test_236_Add_Subscriber_Record_with_whitelist_set_to_netflix_and_blacklist_set_to_linkedin(self):
        restart_the_grid()
        try:
            logging.info("Add_Subscriber_Record_with_whitelist_set_to_netflix_and_blacklist_set_to_linkedin")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=9999732d-34590346;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;PXP:PXY_PRI=0ac4065f;PXS:PXY_SEC=0AC4800D;SUB:Calling-Station-Id=110361221;BWI:BWFlag=1;BL=linkedin;WL=netflix;"')
            child.expect('Record successfully added')
            logging.info("Test Case 37 Execution Passed")
            assert True
        except:
            logging.info("Test Case 37 Execution Failed")
            assert False

    @pytest.mark.run(order=38)
    def test_237_Validate_Subscriber_Record_with_whitelist_set_to_netflix_and_blacklist_set_to_linkedin(self):
        logging.info("Validate_Subscriber_Record_with_whitelist_set_to_netflix_and_blacklist_set_to_linkedin")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'/32|LID:N/A|IPS:N/A.*',c)
        logging.info("Test case 38 execution completed")


    @pytest.mark.run(order=39)
    def test_238_start_Syslog_Messages_logs_on_master(self):
        logging.info("Starting Syslog Messages Logs on master")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 39 passed")
        sleep(20)

    @pytest.mark.run(order=40)
    def test_239_Query_linkedin_com(self):
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' linkedin.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        res1=re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        res2=re.search(r'.*linkedin.com.*IN.*A.*',str(dig_result)) 
        res3=re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        res4=re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        if res1!=None and res2!=None and res3!=None and res4!=None:
            sleep(20)
            assert True
        else:
            assert False

    @pytest.mark.run(order=41)
    def test_240_stop_Syslog_Messages_Logs_on_master(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test Case 41 Execution Completed")

    @pytest.mark.run(order=42)
    def test_241_Validate_linkedin_com_returns_Blocked_IPs_in_response(self):
        logging.info("Validate_linkedin_com_returns_Blocked_IPs_in_response")
        logging.info("Validating Sylog Messages Logs")
        LookFor="response.*NOERROR.*linkedin.com.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
        logging.info(logs)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 42 Execution Passed")
            assert True
        else:
            logging.info("Test Case 42 Execution Failed")
            assert False

    @pytest.mark.run(order=43)
    def test_242_Validate_CEF_Log_for_linkedin_in_syslog(self):
        logging.info("Validate_CEF_Log_for_linkedin_in_syslog")
        LookFor="linkedin"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
        logging.info(logs)
        LookFor1="site2-blocking.pc.com.*IN A 2.2.2.2"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_member1_vip)
        logging.info(logs1)
        print logs1
        LookFor2="CAT=BL"
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_member1_vip)
        logging.info(logs2)
        if logs!=None and logs1!=None and logs2!=None:
            logging.info(logs)
            logging.info("Test Case 43 Execution Passed")
            assert True
        else:
            logging.info("Test Case 43 Execution Failed")
            assert False

    @pytest.mark.run(order=44)
    def test_243_Validate_linkedin_com_did_not_cache_in_dca(self):
        logging.info("Validate_linkedin_com_did_not_cache_in_dca")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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
    def test_244_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
        logging.info("Validate_DCA_Cache_content_shows_Cache_is_empty")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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

#9982
    
    @pytest.mark.run(order=144)
    def test_245_enable_proxy_rpz_passthru(self):
        logging.info("enable_proxy_rpz_passthru")
        ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=proxy_rpz_passthru")
        ref=json.loads(ref)
        ref1=ref[0]["_ref"]
        data={"proxy_rpz_passthru":True}
        ref=ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
        if type(ref)!=tuple:
            restart_the_grid()
            assert True
        else:
            logging.info("test case 144 Execution failed")
            assert False

    @pytest.mark.run(order=145)
    def test_246_validate_proxy_rpz_passthru_is_enabled(self):
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

    @pytest.mark.run(order=133)
    def test_247_Add_Subscriber_Record_with_SSP_Bit_set_to_ffffffff(self):
        logging.info("Add Subscriber Record with SSP=ffffffff")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=9999732d-34590346;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ffffffff;PCC:PC-Category-Policy=00000000000000000000000000000001;SUB:Calling-Station-Id=110361221;BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;IPA:IP6=2620:10a:6000:2500:230:48ff:fed5:d928;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+'"')
        child.expect('Record successfully added')
        logging.info("test case 133 passed")

    @pytest.mark.run(order=134)
    def test_248_Validate_Subscriber_Record_with_SSP_set_to_0(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'/32|LID:N/A|IPS:N/A.*',c)
        logging.info("Test case 134 execution Completed")

    @pytest.mark.run(order=146)
    def test_249_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 146 Execution  passed")
        sleep(20)

    @pytest.mark.run(order=147)
    def test_250_Query_ALL_31_RPZ_Passthru_rules_from_0_to_32(self):
        try:
            logging.info("Query last RPZ passthru rule")
            for i in range(31):
                dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+config.client_ip1+' "dig @'+str(config.grid_member1_vip)+' pass'+str(i)+' +noedns -b '+config.client_ip1+'"'
                dig_cmd1 = os.system(dig_cmd)
            logging.info("test case 147 Execution passed")
            assert True
        except:
            logging.info("test case 147 Execution failed")
            assert False
        sleep(30)

    @pytest.mark.run(order=148)
    def test_251_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test Case 148 Execution Completed")

    @pytest.mark.run(order=149)
    def test_252_Validate_All_32_RPZ_Passthru_returns_Proxy_vips_in_response(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(31):
            LookFor="response.*NOERROR.*pass4.*IN A .*"+config.pxy_log+".*"
            logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
            logging.info(logs)
            if logs!=None:
                logging.info(logs)
                logging.info("Test Case 149 Execution Passed")
                assert True
            else:
                logging.info("Test Case 149 Execution Failed")
                assert False

    @pytest.mark.run(order=150)
    def test_253_Validate_CEF_Log_for_PASSTHRU_in_syslog(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(31):
            LookFor="PASSTHRU rewrite pass"+str(i)+".* via pass"+str(i)+".rpz"+str(i)+".com"
            logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
            logging.info (logs)
            LookFor2="PASSTHRU"
            logs2=logv(LookFor2,"/var/log/syslog",config.grid_member1_vip)
            logging.info (logs2)
            if logs!=None and logs2!=None:
                logging.info(logs)
                logging.info("Test Case 150 Execution Passed")
                assert True
            else:
                logging.info("Test Case 150 Execution Failed")
                assert False

    @pytest.mark.run(order=151)
    def test_254_Validate_all_these_32_RPZ_Passthru_rules_did_not_cache_in_dca(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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
    def test_255_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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
    def test_256_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 153 Execution Completed")
        sleep(20)


    @pytest.mark.run(order=154)
    def test_257_Query_Last_RPZ_Passthru_rule_31(self):
        try:
            logging.info("Query last RPZ passthru rule")
            for i in range(31,32):
                dig_cmd = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+config.client_ip1+' "dig @'+str(config.grid_member1_vip)+' pass'+str(i)+' +noedns -b '+config.client_ip1+'"'
                dig_cmd1 = os.system(dig_cmd)
            logging.info("test case 154 Execution passed")
            assert True
        except:
            logging.info("test case 154 Execution failed")
            assert False
        sleep(20)

    @pytest.mark.run(order=155)
    def test_258_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test Case 155 Execution Completed")


    @pytest.mark.run(order=156)
    def test_259_Validate_Last_RPZ_Passthru_returns_Public_ip_in_response(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(31,32):
            LookFor="response.*NOERROR.*pass"+str(i)+".*IN.*A"
            logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
            logging.info(logs)
            if logs!=None:
                logging.info(logs)
                logging.info("Test Case 156 Execution Passed")
                assert True
            else:
                logging.info("Test Case 156 Execution Failed")
                assert False

    
    @pytest.mark.run(order=157)
    def test_260_Validate_CEF_Log_for_PASSTHRU_in_syslog(self):
        logging.info("Validating Sylog Messages Logs")
        for i in range(31,32):
            LookFor="PASSTHRU rewrite pass"+str(i)+".* via pass"+str(i)+".rpz"+str(i)+".com"
            logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
            logging.info (logs)
            LookFor2="PASSTHRU"
            logs2=logv(LookFor2,"/var/log/syslog",config.grid_member1_vip)
            logging.info (logs2)
            if logs==None and logs2==None:
                logging.info(logs)
                logging.info("Test Case 157 Execution Passed")
                assert True
            else:
                logging.info("Test Case 157 Execution Failed")
                assert False

    @pytest.mark.run(order=158)
    def test_261_Validate_last_RPZ_Passthru_rule_cached_in_dca(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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
    def test_262_Validate_DCA_Cache_content_shows_pass31(self):
        logging.info("Validate passthru queries are not cached by DCA")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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
        assert re.search(r'.*pass31.*',c)
        logging.info("Test case 159 execution Completed")

#Grid level cases
    
    @pytest.mark.run(order=23)
    def test_263_stop_the_subscriber_services_on_all_the_members(self):
        logging.info("stop the subscriber services on all the members")
        ref=stop_subscriber_collection_services_for_added_site([config.grid_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn])
        if ref!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=24)
    def test_264_delete_the_subscriber_site_site2(self):
        logging.info("delete the subscriber site site2")
        ref=delete_subscriber_site("site2")
        ref1=delete_subscriber_site("site3")
        if ref!=None and ref1 !=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
    
    @pytest.mark.run(order=25)
    def test_265_show_bypass_value_to_on_in_grid_level_when_site_doesnt_exist(self):
        logging.info("set bypass value to on in grid level when site doesn't exist")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*The grid does not contain any Subscriber Secure sites..*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=26)
    def test_266_set_bypass_value_to_on_in_grid_level_when_site_doesnt_exist(self):
        logging.info("set bypass value to on in grid level when site doesn't exist")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass on grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*The grid does not contain any Subscriber Secure sites..*',c)
        logging.info("Test case execution Completed")
        sleep(20)

    @pytest.mark.run(order=27)
    def test_267_Add_the_subscriber_site_site5_with_no_members(self):
        logging.info("Add the subscriber site with no members")
        data={"blocking_ipv4_vip1": "1.1.1.1","blocking_ipv4_vip2": "2.2.2.2","msps":[{"ip_address": config.proxy_server1}],"spms": [{"ip_address": "10.12.11.11"}],"name":"site5","maximum_subscribers":100000,"nas_gateways":[{"ip_address":config.rad_client_ip,"name":"nas1","shared_secret":"testing123"},{"ip_address":config.rad_client_ip_lan,"name":"nas2","shared_secret":"testing123"}]}
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

    @pytest.mark.run(order=28)
    def test_268_validate_the_subscriber_site_site5_is_added_with_no_members(self):
        logging.info("validate the subscriber site with no members one is DCA capable")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        reference=json.loads(reference)
        if reference[0]["name"]=="site5":
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=29)
    def test_269_show_bypass_value_in_grid_level_when_no_members_assigned_to_site(self):
        logging.info("show bypass value in site level when no members assigned to site")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure site <site5> does not contain any members..*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=30)
    def test_270_set_bypass_value_in_grid_level_when_no_members_assigned_to_site(self):
        logging.info("set bypass value in site level when no members assigned to site")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass on grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure site <site5> does not contain any members..*',c)
        logging.info("Test case execution Completed")
        sleep(20)

    @pytest.mark.run(order=31)
    def test_271_Add_the_Subscriber_Site_as_site2_With_IB_FLEX_Member_DCA_Subscriber_Query_count_and_DCA_Blocklist_White_List_Enabled(self):
        logging.info("Addsubscriber site site2 with IB-FLEX DCA Subscriber Query Count and DCA Blocklist whitelist Enable")
        data={"blocking_ipv4_vip1": "1.1.1.1","blocking_ipv4_vip2": "2.2.2.2","msps":[{"ip_address": config.proxy_server1}],"spms": [{"ip_address": "10.12.11.11"}],"name":"site2","maximum_subscribers":100000,"members":[{"name":config.grid_fqdn},{"name":config.grid_member1_fqdn},{"name":config.grid_member2_fqdn}],"nas_gateways":[{"ip_address":config.rad_client_ip,"name":"nas1","shared_secret":"testing123"},{"ip_address":config.rad_client_ip_lan,"name":"nas2","shared_secret":"testing123"}],"dca_sub_query_count":True,"dca_sub_bw_list":True}
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

    @pytest.mark.run(order=32)
    def  test_272_Validate_subscriber_site_site2_Is_Added_with_IB_FLEX_Member_DCA_Subscriber_Query_count_and_DCA_Blocklist_White_List_Enabled(self):
        logging.info("Validating subscriber site site2 added with IB-FLEX DCA Subscriber Query Count and DCA Blocklist whitelist Enable")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=blocking_ipv4_vip1,blocking_ipv4_vip2,dca_sub_query_count,dca_sub_bw_list,dca_sub_bw_list")
        reference=json.loads(reference)
        if reference[0]["blocking_ipv4_vip1"]=="1.1.1.1" and reference[0]["blocking_ipv4_vip2"]=="2.2.2.2" and reference[0]["dca_sub_query_count"]==True and reference[0]["dca_sub_bw_list"]==True:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=33)
    def test_273_Start_the_subscriber_service_on_members(self):
        logging.info("Start the subscriber service on members")
        ref=start_subscriber_collection_services_for_added_site([config.grid_fqdn,config.grid_member1_fqdn,config.grid_member2_fqdn])
        if ref!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=34)
    def test_274_Validate_subscriber_service_is_running_on_members(self):
        restart_the_grid()
        logging.info("Validating subscriber collection services started on members")
        members=[config.grid_fqdn,config.grid_member2_fqdn,config.grid_member1_fqdn]
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
                    sleep(20)
                else:
                    logging.info("Test case execution Failed")
                    assert False

    
    @pytest.mark.run(order=35)
    def test_275_set_to_default_value_for_bypass_in_grid_level(self):
        logging.info("set to default value for bypass in site level")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass off grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member2_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member1_fqdn+'.*',c)
        logging.info("Test case execution Completed")
        sleep(20)
    
    @pytest.mark.run(order=36)
    def test_276_Add_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        try:
            logging.info("Add Subscriber Record with PCP Policy for News Category")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;"')
            child.expect('Record successfully added')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Failed")
            assert False

    @pytest.mark.run(order=37)
    def test_277_Validate_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=38)
    def test_278_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=39)
    def test_279_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_Blocked_IPs_in_response_from_Bind_As_Not_DCA_Cache(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and get PCP Blocked IPs response from Bind as times.com not in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test case execution Completed")
        sleep(15)

    @pytest.mark.run(order=40)
    def test_280_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=41)
    def test_281_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_times_com(self):
        logging.info("Validate Named CEF Log for times.com  when get response from Bind")
        LookFor=".*named.*info CEF.*times.com.*CAT=0x00000000000000040000000000000000.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=42)
    def test_282_Validate_PCP_Domain_times_com_did_not_cached_to_DCA_When_Send_Query_From_PCP_bit_Matched_Subscriber_client(self):
        logging.info("Validate times.com domain not cached to DCA when send query from the PCP bit matched subscriber client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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

    @pytest.mark.run(order=43)
    def test_283_start_Syslog_Messages_logs_on_Member2(self):
        logging.info("Starting Syslog Messages Logs on Member2")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=44)
    def test_284_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_Member2_Validate_returns_Blocked_IPs_in_response_from_Bind(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using Member2 and get PCP Blocked IPs response from Bind")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test case execution Completed")
        sleep(20)

    @pytest.mark.run(order=45)
    def test_285_stop_Syslog_Messages_Logs_on_Member2(self):
        logging.info("Stopping Syslog Logs on member2")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=46)
    def test_286_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_times_com(self):
        logging.info("Validate Named CEF Log for times.com  when get response from Bind")
        LookFor=".*named.*info CEF.*times.com.*CAT=0x00000000000000040000000000000000.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    
    @pytest.mark.run(order=47)
    def test_287_start_Syslog_Messages_logs_on_GM(self):
        logging.info("Starting Syslog Messages Logs on GM")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=48)
    def test_288_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_GM_Validate_returns_Blocked_IPs_in_response_from_Bind(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using GM and get PCP Blocked IPs response from Bind")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test case execution Completed")
        sleep(20)

    @pytest.mark.run(order=49)
    def test_289_stop_Syslog_Messages_Logs_on_GM(self):
        logging.info("Stopping Syslog Logs on GM")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=50)
    def test_290_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_times_com(self):
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


    @pytest.mark.run(order=51)
    def test_291_set_bypass_value_in_grid_level_to_on(self):
        restart_the_grid()
        logging.info("set bypass value in grid level to on")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass on grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Site: site2.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")
        sleep(20)

    @pytest.mark.run(order=52)
    def test_292_show_bypass_value_in_grid_level_when_set_to_on(self):
        logging.info("show bypass value in grid level when set to on")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Site: site2.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")

#Checking Bypass working for flex member(Member1)

    @pytest.mark.run(order=53)
    def test_293_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=54)
    def test_294_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
        logging.info("Validate DCA Cache content shows Cache is empty")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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

    @pytest.mark.run(order=55)
    def test_295_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_Blocked_IPs_in_response_from_Bind_As_Not_DCA_Cache(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and get PCP Blocked IPs response from Bind as times.com not in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        res1=re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        res2=re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        res3=re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        res4=re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        if res1!=None and res2!=None and res3==None and res4==None:
            sleep(20)
            assert True
        else:
            assert False
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=56)
    def test_296_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=57)
    def test_297_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_times_com(self):
        logging.info("Validate Named CEF Log for times.com  when get response from Bind")
        LookFor1=".*named.*info CEF.*times.com.*"
        LookFor2=".*NOERROR.*times.com.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_member1_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_member1_vip)
        if logs1==None and logs2!=None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=58)
    def test_298_Validate_PCP_Domain_times_com_did_not_cached_to_DCA_When_Send_Query_From_PCP_bit_Matched_Subscriber_client(self):
        logging.info("Validate times.com domain not cached to DCA when send query from the PCP bit matched subscriber client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=59)
    def test_299_Validate_when_get_response_from_Bind_for_PCP_domain_times_com_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased(self):
        logging.info("Validate when get response from Bind for PCP domain times.com Cache hit count not increased and Miss_cache count count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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

    @pytest.mark.run(order=60)
    def test_300_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=61)
    def test_301_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB_FLEX Member")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        logging.info("Test case execution Completed")
        sleep(20)

    @pytest.mark.run(order=62)
    def test_302_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=63)
    def test_303_Validate_Named_CEF_Log_Logs_when_get_response_from_DCA_for_PCP_domain_times_com(self):
        logging.info("Validate Named CEF Log for times.com  when get response from DCA")
        LookFor1=".*named.*info CEF.*times.com.*"
        LookFor2=".*NOERROR.*times.com.*IN A.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_member1_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_member1_vip)
        if logs1==None and logs2==None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=64)
    def test_304_Validate_when_get_response_from_DCA_for_PCP_domain_times_com_Cache_hit_count_increased_and_Miss_cache_count_not_increased(self):
        logging.info("Validate when get response from Bind for PCP domain times.com Cache hit count increased and Miss_cache count not increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*1.*',c)
        assert re.search(r'.*Cache miss count.*1.*',c)
        logging.info("Test case execution Completed")


#Checking Bypass working for Member2

    @pytest.mark.run(order=65)
    def test_305_start_Syslog_Messages_logs_on_Member2(self):
        logging.info("Starting Syslog Messages Logs on Member2")
        log("start","/var/log/syslog",config.grid_member2_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=66)
    def test_306_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_Member2_Validate_returns_Normal_response_from_Bind(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using Member2 and validate returns normal response")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member2_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        res1=re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        res2=re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        res3=re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        res4=re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        if res1!=None and res2!=None and res3==None and res4==None:
            sleep(20)
            assert True
        else:
            assert False
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=67)
    def test_307_stop_Syslog_Messages_Logs_on_Member2(self):
        logging.info("Stopping Syslog Logs on member2")
        log("stop","/var/log/syslog",config.grid_member2_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=68)
    def test_308_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_times_com(self):
        logging.info("Validate Named CEF Log for times.com  when get response from Bind")
        LookFor1=".*named.*info CEF.*times.com.*"
        LookFor2=".*NOERROR.*times.com.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_member2_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_member2_vip)
        if logs1==None and logs2!=None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

#Checking Bypass working for Master

    @pytest.mark.run(order=69)
    def test_309_start_Syslog_Messages_logs_on_GM(self):
        logging.info("Starting Syslog Messages Logs on GM")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=70)
    def test_310_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_GM_Validate_returns_Normal_response_from_Bind(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using GM and validate returns normal response")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        res1=re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        res2=re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        res3=re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        res4=re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        if res1!=None and res2!=None and res3==None and res4==None:
            sleep(10)
            assert True
        else:
            assert False
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=71)
    def test_311_stop_Syslog_Messages_Logs_on_GM(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=72)
    def test_312_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_times_com(self):
        logging.info("Validate Named CEF Log for times.com  when get response from Bind")
        LookFor1=".*named.*info CEF.*times.com.*"
        LookFor2=".*NOERROR.*times.com.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
        if logs1==None and logs2!=None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False
#Testing after bypass set off at grid level

    @pytest.mark.run(order=73)
    def test_313_set_bypass_value_in_grid_level_to_off(self):
        logging.info("set bypass value in grid level to off")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass off grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Site: site2.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")
        sleep(50)

    @pytest.mark.run(order=74)
    def test_314_show_bypass_value_in_grid_level_when_set_to_off(self):
        logging.info("show bypass value in grid level when set to off")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Site: site2.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")
        sleep(20)
        
    @pytest.mark.run(order=116)
    def test_315_From_Radclient_Send_Start_Radius_Message_with_PCP_Policy_and_Proxy_All_Configured(self):
        restart_the_grid()
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part1_radfiles/RFE_9980_PCP_start_client1.txt -r 1 '+str(config.grid_member1_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case 34 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=117)    
    def test_316_Validate_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before        
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000040000000000000000.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=75)
    def test_317_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=76)
    def test_318_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_Blocked_IPs_in_response_from_Bind_As_Not_in_DCA_Cache_with_PCP_word(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and get PCP Blocked IPs response from Bind as times.com not in DCA cache with PCP word")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test case execution Completed")
        sleep(20)

    @pytest.mark.run(order=77)
    def test_319_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=78)
    def test_320_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_times_com(self):
        logging.info("Validate Named CEF Log for times.com  when get response from Bind")
        LookFor=".*named.*info CEF.*times.com.*CAT=0x00000000000000040000000000000000.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

    @pytest.mark.run(order=79)
    def test_321_Validate_when_get_response_from_Bind_for_PCP_domain_times_com_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased(self):
        logging.info("Validate when get response from Bind for PCP domain times.com Cache hit count not increased and Miss_cache count count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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

    @pytest.mark.run(order=80)
    def test_322_start_Syslog_Messages_logs_on_Member2(self):
        logging.info("Starting Syslog Messages Logs on Member2")
        log("start","/var/log/syslog",config.grid_member2_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=81)
    def test_323_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_Member2_Validate_returns_Blocked_IPs_in_response_from_Bind(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using Member2 and get PCP Blocked IPs response from Bind")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member2_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test case execution Completed")
        sleep(10)

    @pytest.mark.run(order=82)
    def test_324_stop_Syslog_Messages_Logs_on_Member2(self):
        logging.info("Stopping Syslog Logs on member2")
        log("stop","/var/log/syslog",config.grid_member2_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=83)
    def test_325_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_times_com(self):
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

    @pytest.mark.run(order=84)
    def test_326_start_Syslog_Messages_logs_on_GM(self):
        logging.info("Starting Syslog Messages Logs on GM")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=85)
    def test_327_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_GM_Validate_returns_Blocked_IPs_in_response_from_Bind(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using GM and get PCP Blocked IPs response from Bind")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test case execution Completed")
        sleep(20)

    @pytest.mark.run(order=86)
    def test_328_stop_Syslog_Messages_Logs_on_GM(self):
        logging.info("Stopping Syslog Logs on GM")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=87)
    def test_329_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_times_com(self):
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

#Check Bypass functionality after stopping subscriber service
    @pytest.mark.run(order=88)
    def test_330_stop_the_subscriber_services_on_member2(self):
        logging.info("stop the subscriber services on member2")
        ref=stop_subscriber_collection_services_for_added_site([config.grid_member2_fqdn])
        if ref!=None:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=89)
    def test_331_set_bypass_value_in_grid_level_to_on(self):
        logging.info("set bypass value in grid level to on")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass on grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Site: site2.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")
        sleep(10)

    @pytest.mark.run(order=90)
    def test_332_show_bypass_value_in_grid_level_when_set_to_on(self):
        logging.info("show bypass value in grid level when set to on")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Site: site2.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=91)
    def test_333_Start_the_subscriber_service_on_member2(self):
        logging.info("Start the subscriber service on member2")
        ref=start_subscriber_collection_services_for_added_site([config.grid_member2_fqdn])
        if ref!=None:
            logging.info("Test case execution passed")
            assert True
            sleep(20)
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=92)
    def test_334_Validate_subscriber_service_is_running_on_member2(self):
        #restart_the_grid()
        logging.info("Validating subscriber collection services started on member2")
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

    @pytest.mark.run(order=93)
    def test_335_start_Syslog_Messages_logs_on_Member2(self):
        logging.info("Starting Syslog Messages Logs on Member2")
        log("start","/var/log/syslog",config.grid_member2_vip)
        logging.info("test case 128 passed")
        sleep(10)

    @pytest.mark.run(order=94)
    def test_336_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_Member2_Validate_returns_Normal_response_from_Bind(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using Member2 and validate returns normal response")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member2_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        res1=re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        res2=re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        res3=re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        res4=re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        if res1!=None and res2!=None and res3==None and res4==None:
            sleep(20)
            assert True
        else:
            assert False
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=95)
    def test_337_stop_Syslog_Messages_Logs_on_Member2(self):
        logging.info("Stopping Syslog Logs on member2")
        log("stop","/var/log/syslog",config.grid_member2_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=96)
    def test_338_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_times_com(self):
        logging.info("Validate Named CEF Log for times.com  when get response from Bind")
        LookFor1=".*named.*info CEF.*times.com.*"
        LookFor2=".*NOERROR.*times.com.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_member2_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_member2_vip)
        if logs1==None and logs2!=None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

#Bypass functionality after member reboot


    @pytest.mark.run(order=97)
    def test_339_show_bypass_value_in_grid_level_when_set_to_on(self):
        logging.info("show bypass value in grid level when set to on")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Site: site2.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=98)
    def test_340_Validate_product_reboot(self):
        logging.info("Validate product reboot")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('reboot')
        child.expect(':')
        child.sendline('y')
        sleep(240)
        logging.info("Test case  Execution Completed")

    @pytest.mark.run(order=99)
    def test_341_show_bypass_value_in_grid_level_after_member2_reboot(self):
        logging.info("show bypass value in grid level after member2 reboot")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Site: site2.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=100)
    def test_342_start_Syslog_Messages_logs_on_Member2(self):
        logging.info("Starting Syslog Messages Logs on Member2")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=101)
    def test_343_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_Member2_Validate_returns_Normal_response_from_Bind(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using Member2 and validate returns normal response")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        res1=re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        res2=re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        res3=re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        res4=re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        if res1!=None and res2!=None and res3==None and res4==None:
            sleep(10)
            assert True
        else:
            assert False
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=102)
    def test_344_stop_Syslog_Messages_Logs_on_Member2(self):
        logging.info("Stopping Syslog Logs on member2")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=103)
    def test_345_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_times_com(self):
        logging.info("Validate Named CEF Log for times.com  when get response from Bind")
        LookFor1=".*named.*info CEF.*times.com.*"
        LookFor2=".*NOERROR.*times.com.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_member1_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_member1_vip)
        if logs1==None and logs2!=None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

# Bypass functionality after rc restart


    @pytest.mark.run(order=104)
    def test_346_show_bypass_value_in_grid_level_when_set_to_on(self):
        logging.info("show bypass value in grid level when set to on")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Site: site2.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=105)
    def test_347_do_RC_restart_on_member(self):
        logging.info("do RC restart on memeber")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('/infoblox/rc restart')
        sleep(150)
        child.expect('#')
        child.sendline('exit')
        logging.info("Test case Execution Completed")

    @pytest.mark.run(order=106)
    def test_348_show_bypass_value_in_grid_level_after_member2_reboot(self):
        logging.info("show bypass value in grid level after member2 reboot")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Site: site2.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=107)
    def test_349_start_Syslog_Messages_logs_on_Member2(self):
        logging.info("Starting Syslog Messages Logs on Member2")
        log("start","/var/log/syslog",config.grid_member1_vip)
        sleep(10)
        logging.info("test case passed")

    @pytest.mark.run(order=108)
    def test_350_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_Member2_Validate_returns_Normal_response_from_Bind(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using Member2 and validate returns normal response")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        res1=re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        res2=re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        res3=re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        res4=re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        if res1!=None and res2!=None and res3==None and res4==None:
	    sleep(30)
            assert True
        else:
            assert False
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=109)
    def test_351_stop_Syslog_Messages_Logs_on_Member2(self):
        logging.info("Stopping Syslog Logs on member2")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")


#Bypass functionality for HA
    '''
    @pytest.mark.run(order=111)
    def test_350_show_bypass_value_in_grid_level_when_set_to_on(self):
        logging.info("show bypass value in grid level when set to on")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Site: site2.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member2_fqdn+'.*',c)
        #assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member3_fqdn+'.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=112)
    def test_351_start_Syslog_Messages_logs_on_HA(self):
        logging.info("Starting Syslog Messages Logs on Member2")
        log("start","/var/log/syslog",config.grid_member1_vip)
        sleep(10)
        logging.info("test case 112 passed")

    @pytest.mark.run(order=113)
    def test_352_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_HA_Validate_returns_Normal_response_from_Bind(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using Member2 and validate returns normal response")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        res1=re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        res2=re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        res3=re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        res4=re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        if res1!=None and res2!=None and res3==None and res4==None:
            sleep(10)
            assert True
        else:
            assert False
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=114)
    def test_353_stop_Syslog_Messages_Logs_on_HA(self):
        logging.info("Stopping Syslog Logs on member2")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=115)
    def test_354_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_times_com(self):
        logging.info("Validate Named CEF Log for times.com  when get response from Bind")
        LookFor1=".*named.*info CEF.*times.com.*"
        LookFor2=".*NOERROR.*times.com.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_member1_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_member1_vip)
        if logs1==None and logs2!=None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False

#Check Bypass functionality after HA failover


    @pytest.mark.run(order=116)
    def test_355_show_bypass_value_for_HA_member_when_set_to_on(self):
        logging.info("show bypass value for ha member when set to on")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member1_fqdn+'.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=117)
    def test_356_HA_pair_failover(self):
        logging.info("Validate HA failover after memeber reboot")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('reboot')
        child.expect(':')
        child.sendline('y')
        sleep(660)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=118)
    def test_357_show_bypass_value_for_HA_member_when_set_to_on(self):
        cmd1 = 'whoami'
        cmd_result1 = subprocess.check_output(cmd1, shell=True)
        cmd_result1=cmd_result1.strip('\n')
        print cmd_result1
        cmd = 'rm -v /home/'+cmd_result1+'/.ssh/known_hosts'
        cmd_result = subprocess.check_output(cmd, shell=True)
        print cmd_result
        logging.info("show bypass value for ha member when set to on")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member1_fqdn+'.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=119)
    def test_358_start_Syslog_Messages_logs_on_HA(self):
        logging.info("Starting Syslog Messages Logs on Member2")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=120)
    def test_359_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_HA_Validate_returns_Normal_response_from_Bind(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using Member2 and validate returns normal response")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        res1=re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        res2=re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        res3=re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        res4=re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        if res1!=None and res2!=None and res3==None and res4==None:
            sleep(10)
            assert True
        else:
            assert False
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=121)
    def test_360_stop_Syslog_Messages_Logs_on_HA(self):
        logging.info("Stopping Syslog Logs on member2")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=122)
    def test_361_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_times_com(self):
        logging.info("Validate Named CEF Log for times.com  when get response from Bind")
        LookFor1=".*named.*info CEF.*times.com.*"
        LookFor2=".*NOERROR.*times.com.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_member1_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_member1_vip)
        if logs1==None and logs2!=None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False
    '''
#Bypass functionality after Grid backup/restore
 
    @pytest.mark.run(order=123)
    def test_362_show_bypass_value_in_grid_level_when_set_to_on(self):
        logging.info("show bypass value in grid level when set to on")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Site: site2.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")
    
    @pytest.mark.run(order=124)
    def test_363_GRID_BACKUP(self):
        print ("Take Grid Backup")
        data = {"type": "BACKUP"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data))
        res = json.loads(response)
        URL=res['url']
        print("URL is : %s", URL)
        infoblox_log_validation ='curl -k -u admin:infoblox -H  "content-type: application/force-download" "' + str(URL) +'" -o "database.bak"'
        print ("infoblox.log",infoblox_log_validation)
        out2 = commands.getoutput(infoblox_log_validation)
        print("logs are",out2)
        print ("Backup is Done")
        read  = re.search(r'201',URL)
        for read in  response:
                assert True
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=125)
    def test_364_GRID_RESTORE(self):
        logging.info("Grid Restore")
        response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=uploadinit")
        print response
        res = json.loads(response)
        URL=res['url']
        token1=res['token']
        print("URL is : %s", URL)
        print("Token is %s",token1)
        infoblox_log_validation ='curl -k -u admin:infoblox -H content_type="content-typemultipart-formdata" ' + str(URL) +' -F file=@database.bak'
        print infoblox_log_validation
        out2 = commands.getoutput(infoblox_log_validation)
        print ("out2$$$$$$",out2)
        data2={"mode":"NORMAL","nios_data":True,"token":token1}
        print ("&*&*&*&*&*&*",data2)
        response2 = ib_NIOS.wapi_request('POST', object_type="fileop?_function=restoredatabase",fields=json.dumps(data2))
        sleep(400)
        logging.info("Validate Syslog afer perform queries")
        infoblox_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str( config.grid_vip) + ' " tail -3000 /infoblox/var/infoblox.log "'
        out1 = commands.getoutput(infoblox_log_validation)
        print out1
        logging.info(out1)
        assert re.search(r'restore_node complete',out1)
        sleep(50)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=126)
    def test_365_set_support_access_after_restore(self):
        try:
            logging.info("set support access after restore")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')            
            child.sendline('set support_access')
            child.expect('y or n\):')
            child.sendline('y')
            child.expect('y or n\):')
            child.sendline('y')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Failed")
            assert False
    
    @pytest.mark.run(order=126)
    def test_366_Add_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        try:
            logging.info("Add Subscriber Record with PCP Policy for News Category")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip1+' 32 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;"')
            child.expect('Record successfully added')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Failed")
            assert False

    @pytest.mark.run(order=127)
    def test_367_Validate_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case execution completed")


    @pytest.mark.run(order=128)
    def test_368_show_bypass_value_in_grid_level_when_set_to_on(self):
        logging.info("show bypass value in grid level when set to on")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Site: site2.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")


    @pytest.mark.run(order=129)
    def test_369_start_Syslog_Messages_logs_on_Member2(self):
        #cmd1 = 'whoami'
        #cmd_result1 = subprocess.check_output(cmd1, shell=True)
        #cmd_result1=cmd_result1.strip('\n')
        #print cmd_result1
        #cmd = 'rm -v /home/'+cmd_result1+'/.ssh/known_hosts'
        #cmd_result = subprocess.check_output(cmd, shell=True)
        #print cmd_result
        logging.info("Starting Syslog Messages Logs on Member2")
        log("start","/var/log/syslog",config.grid_member2_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=130)
    def test_370_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_Member2_Validate_returns_Normal_response_from_Bind(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using Member2 and validate returns normal response")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_member2_vip)+' times.com +noedns -b '+config.client_ip1+' IN A +tries=0"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        res1=re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        res2=re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        res3=re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        res4=re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        if res1!=None and res2!=None and res3==None and res4==None:
            sleep(20)
            assert True
        else:
            assert False
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=131)
    def test_371_stop_Syslog_Messages_Logs_on_Member2(self):
        logging.info("Stopping Syslog Logs on member2")
        log("stop","/var/log/syslog",config.grid_member2_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=132)
    def test_372_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_times_com(self):
        logging.info("Validate Named CEF Log for times.com  when get response from Bind")
        LookFor1=".*named.*info CEF.*times.com.*"
        LookFor2=".*NOERROR.*times.com.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_member2_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_member2_vip)
        if logs1==None and logs2!=None:
            logging.info("Test case execution Passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False
    
#IPV6 Cases
    
    @pytest.mark.run(order=73)
    def test_373_set_bypass_value_in_grid_level_to_on(self):
        enable_mgmt_port_for_dns(config.grid_member1_fqdn)
        restart_the_grid()
        sleep(100)
        logging.info("set bypass value in grid level to on")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass on grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Site: site2.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")
        sleep(10)

    @pytest.mark.run(order=74)
    def test_374_show_bypass_value_in_grid_level_when_set_to_on(self):
        logging.info("show bypass value in grid level when set to off")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Site: site2.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass enabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=1)
    def test_375_Add_Subscriber_Record_with_Subscriber_V6(self):
        restart_the_grid()
        try:
            logging.info("Add Subscriber Record with BWList")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ipV6+' 128 N/A N/A "ACS:Acct-Session-Id=99-d99;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000000000000000020040;SSP:Subscriber-Secure-Policy=ff;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI=0a23b507;PXS:PXY_SEC=0a23b507;UCP:Unknown-Category-Policy=1;DCP:Dynamic-Category-Policy=1;SUB:Calling-Station-Id=143;BWI:BWFlag=1;BL=facebook.com;WL=bbc.com;" ')
            child.expect('Record successfully added')
            logging.info("Test case passed")
            assert True
        except:
            logging.info("Test Case 1 Execution Failed")
            assert False

    @pytest.mark.run(order=2)
    def test_376_Validate_Subscriber_Record_with_Subscriber_V6(self):
        logging.info("Validate Subscriber Record with_BWList")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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
    def test_377_Add_Subscriber_Record_with_non_PCP_Bit_Matchingsubscriber_ClientV6(self):
        try:
            logging.info("Add Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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
    def test_378_Validate_Subscriber_Record_with_non_PCP_Bit_Matching_V6_subscriber_ClientV6(self):
        logging.info("Validate Subscriber Record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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
    def test_379_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=6)
    def test_380_Query_PCP_domain_playboy_com_from_PCP_bit_matching_Subscriber_clientV6(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip6)+' playboy.com +noedns -b '+config.client_ipV6+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        res1=re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        res2=re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        res3= re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        if res1!=None and res2==None and res3==None:
            sleep(10)
            assert True
        else:
            assert False
        logging.info("Test Case 7 Execution Completed")

    @pytest.mark.run(order=7)
    def test_381_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=8)
    def test_382_Validate_NAMED_CEF_Log_For_CAT_Bit_20000(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor="named.*info CEF.*playboy.com.*CAT.*20000.*"
        #LookFor="named.*info CEF.*facebook.com.com.*CAT.*20000.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False

    @pytest.mark.run(order=9)
    def test_383_Validate_PCP_Domain_playboy_com_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_clientV6(self):
        logging.info("Validate_Blacklist_Domain_facebook_com_did_not_cache_into_DCA_When_Send_Query_From_PCP_bit_Matching_Subscriber_client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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
        logging.info("Test Case 10 Execution Completed")

    @pytest.mark.run(order=10)
    def test_384_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_PCP_Domain_playboy_com(self):
        logging.info("Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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
    def test_385_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=12)
    def test_386_Query_PCP_domain_playboy_com_from_NON_PCP_bit_matching_Subscriber_clientV6(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip6)+' playboy.com +noedns -b '+config.client_ip2V6+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case 13 Execution Completed")
        sleep(20)

    @pytest.mark.run(order=13)
    def test_387_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=14)
    def test_388_Validate_NO_CEF_Log_When_Query_PCP_domain_playboy_com_from_NON_PCP_bit_matching_Subscriber_clientV6_NEGATIVE_CASE(self):
        logging.info("Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        #LookFor="info CEF.*facebook.com.*CAT=20000.*"
        LookFor="info CEF.*playboy.com.*CAT=20000.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert False
        else:
            logging.info("Test Case  Execution Failed")
            assert True
    
    @pytest.mark.run(order=16)
    def test_389_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_When_Query_PCP_domain_playboy_com_from_NON_PCP_bit_matching_Subscriber_clientV6(self):
        logging.info("Validate_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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


    @pytest.mark.run(order=73)
    def test_390_set_bypass_value_in_grid_level_to_off(self):
        logging.info("set bypass value in grid level to off")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass off grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Site: site2.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member2_fqdn+'.*',c)
        logging.info("Test case execution Completed")
        sleep(20)

    @pytest.mark.run(order=74)
    def test_391_show_bypass_value_in_grid_level_when_set_to_off(self):
        logging.info("show bypass value in grid level when set to off")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass grid')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Site: site2.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member1_fqdn+'.*',c)
        assert re.search(r'.*Subscriber Secure Bypass disabled on the member '+config.grid_member2_fqdn+'.*',c)
 

    @pytest.mark.run(order=5)
    def test_392_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=6)
    def test_393_Query_PCP_domain_playboy_com_from_PCP_bit_matching_Subscriber_clientV6(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip6)+' playboy.com +noedns -b '+config.client_ipV6+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=7)
    def test_394_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test Case 8 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=8)
    def test_395_Validate_NAMED_CEF_Log_For_CAT_Bit_20000(self):
        logging.info("Validate_CEF_Log_For_CAT_BL")
        LookFor="named.*info CEF.*playboy.com.*CAT.*20000.*"
        #LookFor="named.*info CEF.*facebook.com.com.*CAT.*20000.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False

    @pytest.mark.run(order=10)
    def test_396_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_PCP_Domain_playboy_com(self):
        logging.info("Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_For_Blacklist_Domain_facebook_com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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

    @pytest.mark.run(order=11)
    def test_397_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case passed")
        sleep(30)


    @pytest.mark.run(order=12)
    def test_398_Query_PCP_domain_playboy_com_from_NON_PCP_bit_matching_Subscriber_clientV6(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip6)+' playboy.com +noedns -b '+config.client_ip2V6+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case 13 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=13)
    def test_399_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=14)
    def test_400_Validate_NO_CEF_Log_When_Query_PCP_domain_playboy_com_from_NON_PCP_bit_matching_Subscriber_clientV6_NEGATIVE_CASE(self):
        logging.info("Validate_NO_CEF_Log_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        #LookFor="info CEF.*facebook.com.*CAT=20000.*"
        LookFor="info CEF.*playboy.com.*CAT=20000.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
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
    def test_401_Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_clientV6(self):
        logging.info("Validate_domain_cached_in_DCA_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
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
    def test_402_Validate_Cache_hit_count_not_increased_But_Miss_cache_count_increased_When_Query_PCP_domain_playboy_com_from_NON_PCP_bit_matching_Subscriber_clientV6(self):
        logging.info("Validate_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased_When_Query_Blacklist_domain_facebook_com_from_NON_PCP_bit_matching_Subscriber_client")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*1.*',c)
        assert re.search(r'.*Cache miss count.*3.*',c)
        logging.info("Test Case 17 Execution Completed")

    @pytest.mark.run(order=17)
    def test_403_start_Syslog_Messages_For_Validation(self):
        logging.info("Start Syslog Messages for Validation case ")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=18)
    def test_404_Query_PCP_domain_playboy_com_from_PCP_bit_matching_Subscriber_clientV6(self):
        logging.info("Query_Blacklist_domain_facebook_com_from_PCP_bit_matching_Subscriber_client")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip6)+' playboy.com +noedns -b '+config.client_ipV6+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case 7 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=19)
    def test_405_stop_Syslog_Messages_For_Validation(self):
        logging.info("Stop Syslog Message")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=20)
    def test_406_Validate_DCA_CEF_Log_shows_CAT_20000_When_Query_PCP_domain_playboy_com_from_PCP_bit_matching_Subscriber_clientV6(self):
        logging.info("Validate DCA CEF Log for ponse from DCA")
        LookFor="fp-rte.*info CEF.*playboy.com.*CAT.*20000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test case passed")
            assert True
        else:
            logging.info("Test Case  Execution Failed")
            assert False



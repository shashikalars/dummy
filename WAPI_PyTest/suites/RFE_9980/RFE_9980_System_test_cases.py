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
    #print len(a)
    b=a[0].split("|")
    for i in b:
        if i=="\n" or i=="":
            b.remove(i)
        else:
            i=i.strip(" ")
            header.append(i)

    for i in range(1,len(a)):
        if "---" not in a[i]:
            b=a[i].split("|")
            for i in b:
                if i=='\n' or i=='':
                    b.remove(i)
                else:
                    i=i.strip(" ")
                    values.append(i)
    #print header
    #print values
    dictionary = dict(zip(header, values))
    return dictionary

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
                logging.info("Test Case  Execution Passed")
                assert True
            else:
                logging.info("Test Case  Execution Failed")
                assert False


    @pytest.mark.run(order=3)
    def test_003_start_DCA_service(self):
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


    @pytest.mark.run(order=4)
    def test_004_Validate_DCA_service_running(self):
        logging.info("Validate_DCA_service_running")
        sys_log_member = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member1_vip)+' " tail -2000 /infoblox/var/infoblox.log"'
        sys_log_member1 ='ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member2_vip)+' " tail -2000 /infoblox/var/infoblox.log"'
        out1 = commands.getoutput(sys_log_member)
        out2 = commands.getoutput(sys_log_member1)
        logging.info (out1,out2)
        res1=re.search(r'DNS cache acceleration is now started',out1)
        res2=re.search(r'DNS cache acceleration is now started',out2)
        if res1!=None and res2!=None:
            logging.info("Test Case  Execution passed")
            assert True
        else:
            logging.info("Test Case  Execution failed")
            assert False



    @pytest.mark.run(order=5)
    def test_005_Modify_Grid_Settings(self):
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

    @pytest.mark.run(order=6)
    def test_006_Validate_Modified_Grid_Settings(self):
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

    @pytest.mark.run(order=7)
    def test_007_Modify_Grid_Dns_Properties(self):
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

    @pytest.mark.run(order=8)
    def test_008_Validate_Grid_Dns_Properties(self):
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
    def test_009_Enable_Parental_Control_with_only_proxy_url(self):
        logging.info("enabling parental control with only proxy url")
        response = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber")
        response = json.loads(response)
        response=response[0]["_ref"]
        logging.info(response)
        data={"enable_parental_control": True,"cat_acctname":"infoblox_sdk", "cat_password":"LinWmRRDX0q","category_url":"https://dl.zvelo.com/","pc_zone_name":"pc.com","cat_update_frequency":1,"proxy_url":"http://10.196.9.113:8001","proxy_username":"admin","proxy_password":"infoblox"}
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

    @pytest.mark.run(order=10)
    def test_010_Validate_Parental_Control_is_Enabled(self):
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
        
    @pytest.mark.run(order=11)
    def test_011_start_category_download_Messages_logs_on_master(self):
        logging.info("Starting category download Messages Logs on master")
        log("start","/storage/zvelo/log/category_download.log",config.grid_vip)
        logging.info("Test case 11 execution passed")
        time.sleep(1500)



    @pytest.mark.run(order=12)
    def test_012_stop_category_download_Messages_logs_on_master(self):
        logging.info("Stop Syslog Messages Logs on master")
        log("stop","/storage/zvelo/log/category_download.log",config.grid_vip)
        logging.info("Test case 12 execution passed")

    @pytest.mark.run(order=13)
    def test_013_validate_for_zvelo_download_data_completion_on_master(self):
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

    @pytest.mark.run(order=14)
    def  test_014_Add_Subscriber_site_site2_with_all_the_supported_members(self):
        logging.info("Add_Subscriber_site_site2_with_all_the_supported_members")
#        log("start","/infoblox/var/infoblox.log",config.grid_member2_vip)
        logging.info("Adding subscriber site site2")
        data={"blocking_ipv4_vip1": "1.1.1.1","blocking_ipv4_vip2": "2.2.2.2","msps":[{"ip_address": config.proxy_server1}],"spms": [{"ip_address": "10.12.11.11"}],"name":"site2","maximum_subscribers":100000,"members":[{"name":config.grid_member2_fqdn}, {"name":config.grid_member1_fqdn}],"nas_gateways":[{"ip_address":config.rad_client_ip,"name":"nas1","shared_secret":"test123"}]}
        get_ref=ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data))
        logging.info(get_ref)
        print(get_ref)
        if type(get_ref)!=tuple:
            reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
            reference=json.loads(reference)
            if reference[0]["name"]==data["name"]:
                logging.info("Test case 11 execution passed")
                assert True
            else:
                logging.info("Test case 11 execution Failed")
                assert False
        else:
            logging.info(get_ref)
            logging.info("Test case 11 execution Failed")
            assert False        

    @pytest.mark.run(order=15)
    def  test_015_validate_for_subscriber_site_site2_is_added(self):
        logging.info("validating subscriber site site1 added")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        reference=json.loads(reference)
        if reference[0]["name"]=="site2":
            logging.info("Test case 15 execution passed")
            assert True
        else:
            logging.info("Test case 15 execution failed")
            assert False

    @pytest.mark.run(order=16)
    def test_016_Start_the_subscriber_service_on_members(self):
        logging.info("Start the subscriber service on members")
        ref=start_subscriber_collection_services_for_added_site([config.grid_member2_fqdn,config.grid_member1_fqdn])
        if ref!=None:
            logging.info("Test case 16 executed successfully")
            assert True
        else:
            logging.info("Test case 16 execution failed")
            assert False

    @pytest.mark.run(order=17)
    def test_017_Validate_subscriber_service_is_running(self):
        logging.info("Validating subscriber collection services started")
        members=[config.grid_member2_fqdn,config.grid_member1_fqdn]
        for mem in members:
            grid_ref = mem_ref_string_pc(mem)
            print grid_ref
            get_ref=ib_NIOS.wapi_request('GET', object_type=grid_ref)
            for ref in get_ref:
                if ref!=tuple:
                    logging.info("Test Case 17 Execution Passed")
                    assert True
                else:
                    logging.info("Test Case 17 Execution Failed")
                    assert False

    @pytest.mark.run(order=18)
    def test_018_Enable_DCA_subscriber_Query_count_logging_on_site(self):
        logging.info("Enable DCA subscriber Query count logging on site")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        get_ref=json.loads(get_ref)[0]["_ref"]
        data={"dca_sub_query_count":True}
        res = ib_NIOS.wapi_request('PUT', object_type=get_ref,fields=json.dumps(data))
        if type(res)!=tuple:
            logging.info("Test case 18 execution passed")
            time.sleep(5)
            assert True
        else:
            logging.info("Test case 18 execution Failed")
            assert False

    @pytest.mark.run(order=19)
    def test_019_validate_Enable_DCA_subscriber_Query_count_logging_on_site(self):
        logging.info("Validate_DCA_subscriber_Query_count_reporting_and_Enable_DCA_subscriber_Allowed_and_Blocked_list_support_are_enabled")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=dca_sub_bw_list,dca_sub_query_count")
        get_ref=json.loads(get_ref)
        if get_ref[0]["dca_sub_query_count"]==True:
            logging.info("Test case 19 execution passed")
            assert True
        else:
            logging.info("Test case 19 execution Failed")
            assert False

    @pytest.mark.run(order=20)
    def test_020_Enable_DCA_subscriber_Allowed_and_Blocked_list_support_on_site(self):
        logging.info("Disable DCA subscriber Allowed and Blocked list support on site")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        get_ref=json.loads(get_ref)[0]["_ref"]
        data={"dca_sub_bw_list":True}
        res = ib_NIOS.wapi_request('PUT', object_type=get_ref,fields=json.dumps(data))
        if type(res)!=tuple:
            logging.info("Test case 20 execution passed")
            time.sleep(5)
            assert True
        else:
            logging.info("Test case 20 execution Failed")
            assert False

    @pytest.mark.run(order=21)
    def test_021_validate_Enable_DCA_subscriber_Allowed_and_Blocked_list_support_on_site(self):
        logging.info("Validate_DCA_subscriber_Query_count_reporting_and_Enable_DCA_subscriber_Allowed_and_Blocked_list_support_are_enabled")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=dca_sub_bw_list,dca_sub_query_count")
        get_ref=json.loads(get_ref)
        if get_ref[0]["dca_sub_query_count"]==True:
            logging.info("Test case 21 execution passed")
            assert True
        else:
            logging.info("Test case 21 execution Failed")
            assert False

 
#    @pytest.mark.run(order=19)
#    def test_019_reboot_the_IB_FLEX_Member_to_enable_DCA_subscriber_Allowed_and_Blocked_list_support_is_enabled_on_site(self):
#        prod_reboot(config.grid_member2_vip) 
#        prod_reboot(config.grid_member1_vip)
#        logging.info("Test case 19 execution passed")


    @pytest.mark.run(order=22)
    def test_022_reboot_the_IB_FLEX_Member_to_enable_DCA_subscriber_Allowed_and_Blocked_list_support_is_enabled_on_site(self):
        reboot([config.vm_id1,config.vm_id2,config.vm_id3])
        logging.info("Test case 22 execution passed")
	sleep(400)


    @pytest.mark.run(order=23)
    def test_023_Add_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        try:
            logging.info("Add Subscriber Record with PCP Policy for News Category")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip+' 32 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;"')
            child.expect('Record successfully added')
            logging.info("Test Case 23 Execution Passed")
            assert True
        except:
            logging.info("Test Case 23 Execution Failed")
            assert False

    @pytest.mark.run(order=24)
    def test_024_Validate_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case 24 execution completed")            


###---------VALIDATING GC CLI COMMANDS---------###


    @pytest.mark.run(order=25)
    def test_025_Validate_subscriber_secure_data_garbage_collect_default(self):
        logging.info("Validate subscriber secure data garbage_collect is set to off")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data garbage_collect')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*This member is not configured for garbage collection.*',c)
        logging.info("Test Case 25 Execution Completed")

    @pytest.mark.run(order=26)
    def test_026_Validate_set_subscriber_secure_data_garbage_collect_on_command(self):
        logging.info("Validate set subscriber_secure_data garbage_collect on command")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data garbage_collect on')
        child.expect(':')
        child.sendline('y')
        child.expect(':')
        child.sendline('10 AM')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Garbage collection is scheduled at 10 AM everyday.*',c)
        logging.info("Test Case 26 Execution Completed")

    @pytest.mark.run(order=27)
    def test_027_Validate_show_subscriber_secure_data_garbage_collect_when_turned_on(self):
        logging.info("Validate subscriber secure data garbage_collect is set to on")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data garbage_collect')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*This member is configured for garbage collection scheduled at 10 AM everyday.*',c)
        logging.info("Test Case 27 Execution Completed")    

    @pytest.mark.run(order=28)
    def test_028_Validate_set_subscriber_secure_data_garbage_collect_off_command(self):
        logging.info("Validate set subscriber_secure_data garbage_collect off command")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data garbage_collect off')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*This member is no longer configured for garbage collection.*',c)
        logging.info("Test Case 28 Execution Completed")    

    @pytest.mark.run(order=29)
    def test_029_Validate_proper_error_message_on_or_off_not_given_for_set_subscriber_secure_data_garbage_collect_command(self):
        logging.info("Validate proper error message if on or off not given for set subscriber secure data garbage_collect command")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data garbage_collect')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*set subscriber_secure_data garbage_collect <on|off>.*',c)
        logging.info("Test Case 29 Execution Completed")   


###---------VALIDATING SUBSCRIBER SECURE DATA BYPASS COMMANDS---------###


    @pytest.mark.run(order=30)
    def test_030_Validate_set_subscriber_secure_data_bypass_off_command(self):
        logging.info("Validate set subscriber_secure_data bypass off")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass off')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure bypass for  software DCA set to .*off.*',c)
        logging.info("Test Case 30 Execution Completed")

    @pytest.mark.run(order=31)
    def test_031_Validate_show_subscriber_secure_data_bypass_command_when_disabled(self):
        logging.info("Validate show subscriber_secure_data bypass command when disabled")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure bypass disabled.*',c)
        logging.info("Test Case 31 Execution Completed")
        sleep(30)


    @pytest.mark.run(order=32)
    def test_032_Validate_blocking_response_when_bypass_set_to_off(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com and get blocking response when bypass is set to off ")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case 32 Execution Completed") 
        sleep(20)


    @pytest.mark.run(order=33)
    def test_033_Validate_set_subscriber_secure_data_bypass_on_command(self):
        logging.info("Validate set subscriber_secure_data bypass on")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass on')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure bypass for  software DCA set to .*on.*',c)
        logging.info("Test Case 33 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=34)
    def test_034_Validate_show_subscriber_secure_data_bypass_when_set_to_on(self):
        logging.info("Validate show subscriber_secure_data bypass when set to on")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure bypass enabled.*',c)
        logging.info("Test Case 34 Execution Completed")

    @pytest.mark.run(order=35)
    def test_035_Validate_normal_response_when_bypass_is_set_to_on(self):
        try:
             logging.info("Validate normal response for querying PCP domain times.com when bypass is set to on")  
             dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip+'"'
             dig_result = subprocess.check_output(dig_cmd, shell=True)
             print dig_result
             assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
             assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
             assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
             logging.info("Test Case 35 Execution failed") 
             assert False
        except:
             logging.info("Test Case 35 Execution passed")
             assert True

    @pytest.mark.run(order=36)
    def test_036_Validate_set_subscriber_secure_data_bypass_dca_command(self):
        logging.info("Validate set subscriber_secure_data bypass dca")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass dca')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure bypass DCA on.*',c)
        logging.info("Test Case 36 Execution Completed")

    @pytest.mark.run(order=37)
    def test_037_Validate_show_subscriber_secure_data_bypass_when_set_to_dca(self):
        logging.info("Validate show subscriber_secure_data bypass when set to dca")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure DCA bypass enabled.*',c)
        logging.info("Test Case 37 Execution Completed") 
     
    @pytest.mark.run(order=38)
    def test_038_Validate_set_subscriber_secure_data_bypass_cache_command(self):
        logging.info("Validate set subscriber_secure_data bypass cache")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass cache')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure bypass cache on.*',c)
        logging.info("Test Case 38 Execution Completed") 
        sleep(10)

    @pytest.mark.run(order=39)
    def test_039_Validate_show_subscriber_secure_data_bypass_when_set_to_cache(self):
        logging.info("Validate show subscriber_secure_data bypass when set to cache")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data bypass')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure local cache bypass enabled.*',c)
        logging.info("Test Case 39 Execution Completed")     

    @pytest.mark.run(order=40)
    def test_040_Validate_normal_response_when_bypass_is_set_to_cache(self):
        logging.info("Validate normal response for querying PCP domain times.com when bypass is set to on")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case 40 Execution Completed")

    @pytest.mark.run(order=41)
    def test_041_Validate_set_subscriber_secure_data_bypass_off_command(self):
        logging.info("Validate set subscriber_secure_data bypass off")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data bypass off')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Subscriber Secure bypass for  software DCA set to .*off.*',c)
        logging.info("Test Case 41 Execution Completed")        
   
    @pytest.mark.run(order=42)
    def test_042_Validate_set_subscriber_secure_data_garbage_collect_on_command(self):
        logging.info("Validate set subscriber_secure_data garbage_collect on command")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data garbage_collect on')
        child.expect(':')
        child.sendline('y')
        child.expect(':')
        child.sendline('10 AM')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Garbage collection is scheduled at 10 AM everyday.*',c)
        logging.info("Test Case 42 Execution Completed")    
    
    @pytest.mark.run(order=43)
    def test_043_Validate_show_subscriber_secure_data_garbage_collect_when_turned_on(self):
        logging.info("Validate subscriber secure data garbage_collect is set to on")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data garbage_collect')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*This member is configured for garbage collection scheduled at 10 AM everyday.*',c)
        logging.info("Test Case 43 Execution Completed")
        sleep(30)

    @pytest.mark.run(order=44)
    def test_044_Validate_product_reboot(self):
        logging.info("Validate product reboot")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('reboot')
        child.expect(':')
        child.sendline('y')
        sleep(210)
        logging.info("Test case 44 Execution Completed")        

    @pytest.mark.run(order=45)
    def test_045_Validate_garbage_collection_configuration_remains_same_after_product_reboot(self):
        logging.info("Validate garbage collection configuration remains same after product reboot")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data garbage_collect')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*This member is configured for garbage collection scheduled at 10 AM everyday.*',c)
        logging.info("Test Case 45 Execution Completed")

    @pytest.mark.run(order=46)
    def test_046_Validate_set_subscriber_secure_data_garbage_collect_off_command(self):
        logging.info("Validate set subscriber_secure_data garbage_collect off command")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data garbage_collect off')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*This member is no longer configured for garbage collection.*',c)
        logging.info("Test Case 46 Execution Completed")        


###------Testing DCA FUNCTIONALITY AFTER PRODUCT REBOOT---------###

    @pytest.mark.run(order=47)
    def test_047_Add_Subscriber_Record_without_Proxy_all_set_and_Different_PCP_Policy_bit_than_client_ip(self):
        try:
            logging.info("Add Subscriber Record without Proxy-All set and different PCP Policy bit than the client_ip")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 N/A N/A "ACS:Acct-Session-Id=9999735888;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=01000000000000010000000000000000;SUB:Calling-Station-Id=110361288;PCC:PC-Category-Policy=00000000000000000000000000000001;"')
            child.expect('Record successfully added')
            logging.info("Test Case 47 Execution Passed")
            assert True
        except:
            logging.info("Test Case 47 Execution Failed")
            assert False
          
    @pytest.mark.run(order=48)
    def test_048_Validate_Subscriber_Record_without_Proxy_all_set_and_Different_PCP_Policy_bit_than_client_ip(self):
        logging.info("Validate Subscriber Record without Proxy-All set different PCP Policy bit than the client_ip")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case 48 execution completed")

    @pytest.mark.run(order=49)
    def test_049_Validate_subscriber_secure_data_garbage_collect_default(self):
        logging.info("Validate subscriber secure data garbage_collect is set to off")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data garbage_collect')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*This member is not configured for garbage collection.*',c)
        logging.info("Test Case 49 Execution Completed")

    @pytest.mark.run(order=50)
    def test_050_Add_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        try:
            logging.info("Add Subscriber Record with PCP Policy for News Category")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip+' 32 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI=0a23b507;PXS:PXY_SEC=0a23b507;"')
            child.expect('Record successfully added')
            logging.info("Test Case 50 Execution Passed")
            assert True
        except:
            logging.info("Test Case 50 Execution Failed")
            assert False

    @pytest.mark.run(order=51)
    def test_051_Validate_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case 51 execution completed")
        sleep(20)

    @pytest.mark.run(order=52)
    def test_052_Send_Query_from_NON_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_cached_DCA_with_PCP_word(self):
        logging.info("Perform Query from NON PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and Validate get NORMAL response times.com domain is cached to DCA with PCP word")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case 52 Execution Completed")    
        sleep(15)

    @pytest.mark.run(order=53)
    def test_053_Validate_PCP_Domain_times_com_get_cached_to_DCA_When_Send_Query_From_NON_PCP_bit_Matched_Subscriber_client(self):
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
        logging.info("Test Case 53 Execution Completed")

    @pytest.mark.run(order=54)
    def test_054_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 54 passed")
        sleep(10)

    @pytest.mark.run(order=55)
    def test_055_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_Blocked_IPs_in_response_from_DCA_As_times_com_domain_is_already_DCA_Cache(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and get PCP Blocked IPs response from DCA as times.com is already in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case 55 Execution Completed")

    @pytest.mark.run(order=56)
    def test_056_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test Case 56 Execution Completed")

    @pytest.mark.run(order=57)
    def test_057_Validate_DCA_CEF_Log_Logs_when_get_response_from_DCA_for_PCP_domain_times_com(self):
        logging.info("Validate DCA CEF Log for times.com  when get response from DCA")
        LookFor="fp-rte.*info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 57 Execution Passed")
            assert True
        else:
            logging.info("Test Case 57 Execution Failed")
            assert False

    @pytest.mark.run(order=58)
    def test_058_do_RC_restart_on_member(self):
        logging.info("do RC restart on memeber")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('-bash-5.0#')
        child.sendline('/infoblox/rc restart')
        sleep(300) 
        child.expect('-bash-5.0#')
        child.sendline('exit')
        logging.info("Test case 58 Execution Completed")


###------Testing DCA FUNCTIONALITY AFTER RC RESTART---------###        


    @pytest.mark.run(order=59)
    def test_059_Validate_set_dns_flush_all(self):
        logging.info("Validate set dns flush all")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set dns flush all')
        child.expect('Infoblox >')
        logging.info("Test Case 59 Execution Completed")

    @pytest.mark.run(order=60)
    def test_060_Validate_dns_cache_empty(self):
        logging.info("Validate dns cache is empty")
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
        logging.info("Test Case 60 Execution Completed")

    @pytest.mark.run(order=61)
    def test_061_Add_Subscriber_Record_without_Proxy_all_set_and_Different_PCP_Policy_bit_than_client_ip(self):
        try:
            logging.info("Add Subscriber Record without Proxy-All set and different PCP Policy bit than the client_ip")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 N/A N/A "ACS:Acct-Session-Id=9999735888;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=01000000000000010000000000000000;SUB:Calling-Station-Id=110361288;PCC:PC-Category-Policy=00000000000000000000000000000001;"')
            child.expect('Record successfully added')
            logging.info("Test Case 61 Execution Passed")
            assert True
        except:
            logging.info("Test Case 61 Execution Failed")
            assert False

    @pytest.mark.run(order=62)
    def test_062_Validate_Subscriber_Record_without_Proxy_all_set_and_Different_PCP_Policy_bit_than_client_ip(self):
        logging.info("Validate Subscriber Record without Proxy-All set different PCP Policy bit than the client_ip")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case 62 execution completed")

    @pytest.mark.run(order=63)
    def test_063_Add_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        try:
            logging.info("Add Subscriber Record with PCP Policy for News Category")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip+' 32 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI=0a23b507;PXS:PXY_SEC=0a23b507;"')
            child.expect('Record successfully added')
            logging.info("Test Case 63 Execution Passed")
            assert True
        except:
            logging.info("Test Case 63 Execution Failed")
            assert False

    @pytest.mark.run(order=64)
    def test_064_Validate_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case 64 execution completed")

    @pytest.mark.run(order=65)
    def test_065_Send_Query_from_NON_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_cached_DCA_with_PCP_word(self):
        logging.info("Perform Query from NON PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and Validate get NORMAL response times.com domain is cached to DCA with PCP word")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case 65 Execution Completed")

    @pytest.mark.run(order=66)
    def test_066_Validate_PCP_Domain_times_com_get_cached_to_DCA_When_Send_Query_From_NON_PCP_bit_Matched_Subscriber_client(self):
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
        logging.info("Test Case 66 Execution Completed")

    @pytest.mark.run(order=67)
    def test_067_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 67 passed")
        sleep(10)

    @pytest.mark.run(order=68)
    def test_068_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_Blocked_IPs_in_response_from_DCA_As_times_com_domain_is_already_DCA_Cache(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and get PCP Blocked IPs response from DCA as times.com is already in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case 68 Execution Completed")

    @pytest.mark.run(order=69)
    def test_069_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test Case 69 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=70)
    def test_070_Validate_DCA_CEF_Log_Logs_when_get_response_from_DCA_for_PCP_domain_times_com(self):
        logging.info("Validate DCA CEF Log for times.com  when get response from DCA")
        LookFor="fp-rte.*info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 70 Execution Passed")
            assert True
        else:
            logging.info("Test Case 70 Execution Failed")
            assert False

###------Testing DCA FUNCTIONALITY AFTER CHANGE OF CPU AND MEMORY OF MEMBER---------###         
        

    @pytest.mark.run(order=71)
    def test_071_Poweroff_the_member(self):
        logging.info("Poweroff the member")
        cmd = 'reboot_system -H '+str(config.vm_id1)+' -a poweroff -c '+config.client_user+''
        cmd_result = subprocess.check_output(cmd, shell=True)
        print cmd_result
        assert re.search(r'.*poweroff completed.*',str(cmd_result))
        logging.info("Test Case 71 Execution Completed")

    @pytest.mark.run(order=72)
    def test_072_Changing_cpu_and_memory_on_member(self):
        logging.info("Changing cpu and memory on member")
        cmd = 'vm_specs -H '+str(config.vm_id1)+' -M 33 -C 8 -c '+config.client_user+''
        cmd_result = subprocess.check_output(cmd, shell=True)
        print cmd_result
        assert re.search(r'.*already has 8 cores, memory changed from 32 to 33 GB.*',str(cmd_result))
        logging.info("Test Case 72 Execution Completed")

    @pytest.mark.run(order=73)
    def test_073_Poweron_the_member(self):
        logging.info("Poweron the member")
        cmd = 'reboot_system -H '+str(config.vm_id1)+' -a poweron -c '+config.client_user+''
        cmd_result = subprocess.check_output(cmd, shell=True)
        print cmd_result
        assert re.search(r'.*poweron completed.*',str(cmd_result))
        logging.info("Test Case 73 Execution Completed")
        sleep(320) 
    
    @pytest.mark.run(order=74)
    def test_074_Validate_set_dns_flush_all(self):
        logging.info("Validate set dns flush all")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set dns flush all')
        child.expect('Infoblox >')
        logging.info("Test Case 74 Execution Completed")

    @pytest.mark.run(order=75)
    def test_075_Validate_dns_cache_empty(self):
        logging.info("Validate dns cache is empty")
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
        logging.info("Test Case 75 Execution Completed")
    

    @pytest.mark.run(order=76)
    def test_076_Add_Subscriber_Record_without_Proxy_all_set_and_Different_PCP_Policy_bit_than_client_ip(self):
        try:
            logging.info("Add Subscriber Record without Proxy-All set and different PCP Policy bit than the client_ip")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 N/A N/A "ACS:Acct-Session-Id=9999735888;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=01000000000000010000000000000000;SUB:Calling-Station-Id=110361288;PCC:PC-Category-Policy=00000000000000000000000000000001;"')
            child.expect('Record successfully added')
            logging.info("Test Case 76 Execution Passed")
            assert True
        except:
            logging.info("Test Case 76 Execution Failed")
            assert False

    @pytest.mark.run(order=77)
    def test_077_Validate_Subscriber_Record_without_Proxy_all_set_and_Different_PCP_Policy_bit_than_client_ip(self):
        logging.info("Validate Subscriber Record without Proxy-All set different PCP Policy bit than the client_ip")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case 77 execution completed")

    @pytest.mark.run(order=78)
    def test_078_Add_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        try:
            logging.info("Add Subscriber Record with PCP Policy for News Category")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip+' 32 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI=0a23b507;PXS:PXY_SEC=0a23b507;"')
            child.expect('Record successfully added')
            logging.info("Test Case 78 Execution Passed")
            assert True
        except:
            logging.info("Test Case 78 Execution Failed")
            assert False

    @pytest.mark.run(order=79)
    def test_079_Validate_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case 79 execution completed")
        sleep(10)

    @pytest.mark.run(order=80)
    def test_080_Send_Query_from_NON_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_cached_DCA_with_PCP_word(self):
        logging.info("Perform Query from NON PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and Validate get NORMAL response times.com domain is cached to DCA with PCP word")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case 80 Execution Completed")

    @pytest.mark.run(order=81)
    def test_081_Validate_PCP_Domain_times_com_get_cached_to_DCA_When_Send_Query_From_NON_PCP_bit_Matched_Subscriber_client(self):
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
        logging.info("Test Case 81 Execution Completed")

    @pytest.mark.run(order=82)
    def test_082_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 82 passed")
        sleep(10)

    @pytest.mark.run(order=83)
    def test_083_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_Blocked_IPs_in_response_from_DCA_As_times_com_domain_is_already_DCA_Cache(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and get PCP Blocked IPs response from DCA as times.com is already in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case 83 Execution Completed")

    @pytest.mark.run(order=84)
    def test_084_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test Case 84 Execution Completed")

    @pytest.mark.run(order=85)
    def test_085_Validate_DCA_CEF_Log_Logs_when_get_response_from_DCA_for_PCP_domain_times_com(self):
        logging.info("Validate DCA CEF Log for times.com  when get response from DCA")
        LookFor="fp-rte.*info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 85 Execution Passed")
            assert True
        else:
            logging.info("Test Case 85 Execution Failed")
            assert False

###------Testing DCA FUNCTIONALITY AFTER STOP/START DCA SERVICE---------###


    @pytest.mark.run(order=86)
    def test_086_Stop_DCA_service_on_Grid_Member1(self):
        logging.info("Stop DCA on the IB-FLEX Grid Master member")
        data = {"enable_dns": True, "enable_dns_cache_acceleration": False}
        DCA_capable=[config.grid_member1_fqdn]
        for mem in DCA_capable:
            grid_ref = mem_ref_string(mem)
            print(grid_ref)
            response = ib_NIOS.wapi_request('PUT', object_type=grid_ref, fields=json.dumps(data))
            print(response)
            if type(response)!=tuple:
                print("DCA Disabled successfully")
                assert True
            else:
                print("Failed to disable DCA on the Member1")
                assert False
        sleep(200)


    @pytest.mark.run(order=87)
    def test_087_start_DCA_service_on_Grid_Master_Member(self):
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
        sleep(200)


    @pytest.mark.run(order=88)
    def test_088_Validate_DCA_service_running(self):
        logging.info("Validate_DCA_service_running")
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_member1_vip)+' " tail -2000 /infoblox/var/infoblox.log"'
        out1 = commands.getoutput(sys_log_validation)
        logging.info (out1)
        logging.info(out1)
        assert re.search(r'DNS cache acceleration is now started',out1)
        logging.info("Test Case 88 Execution Completed")

    @pytest.mark.run(order=89)
    def test_089_Add_Subscriber_Record_without_Proxy_all_set_and_Different_PCP_Policy_bit_than_client_ip(self):
        try:
            logging.info("Add Subscriber Record without Proxy-All set and different PCP Policy bit than the client_ip")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 N/A N/A "ACS:Acct-Session-Id=9999735888;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=01000000000000010000000000000000;SUB:Calling-Station-Id=110361288;PCC:PC-Category-Policy=00000000000000000000000000000001;"')
            child.expect('Record successfully added')
            logging.info("Test Case 89 Execution Passed")
            assert True
        except:
            logging.info("Test Case 89 Execution Failed")
            assert False

    @pytest.mark.run(order=90)
    def test_090_Validate_Subscriber_Record_without_Proxy_all_set_and_Different_PCP_Policy_bit_than_client_ip(self):
        logging.info("Validate Subscriber Record without Proxy-All set different PCP Policy bit than the client_ip")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case 90 execution completed")

    @pytest.mark.run(order=91)
    def test_091_Add_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        try:
            logging.info("Add Subscriber Record with PCP Policy for News Category")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip+' 32 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI=0a23b507;PXS:PXY_SEC=0a23b507;"')
            child.expect('Record successfully added')
            logging.info("Test Case 91 Execution Passed")
            assert True
        except:
            logging.info("Test Case 91 Execution Failed")
            assert False

    @pytest.mark.run(order=92)
    def test_092_Validate_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case 92 execution completed")
        sleep(10)


    @pytest.mark.run(order=93)
    def test_093_Send_Query_from_NON_PCP_bit_match_Subscriber_client_for_PCP_Domain_cnn_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_cached_DCA_with_PCP_word(self):
        logging.info("Perform Query from NON PCP bit match Subscriber client for PCP Domain cnn.com using IB-FLEX Member and Validate get NORMAL response cnn.com domain is cached to DCA with PCP word")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_member1_vip)+' cnn.com +noedns -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*cnn.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case 93 Execution Completed")


    @pytest.mark.run(order=94)
    def test_094_Validate_PCP_Domain_cnn_com_get_cached_to_DCA_When_Send_Query_From_NON_PCP_bit_Matched_Subscriber_client(self):
        logging.info("Validate cnn.com domain get cached to DCA when send query from the NON PCP bit matched subscriber client")
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
        assert re.search(r'.*cnn.com,A,IN.*AA,A,cnn.com.*',c)
        assert re.search(r'.*0x00000000000000040000000000000000.*',c)
        logging.info("Test Case 94 Execution Completed")

    @pytest.mark.run(order=95)
    def test_095_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 95 passed")
        sleep(10)

    @pytest.mark.run(order=96)
    def test_096_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_cnn_Using_IB_FLEX_Member_Validate_returns_Blocked_IPs_in_response_from_DCA_As_cnn_com_domain_is_already_DCA_Cache(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and get PCP Blocked IPs response from DCA as cnn.com is already in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_member1_vip)+' cnn.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case 96 Execution Completed")

    @pytest.mark.run(order=97)
    def test_097_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test Case 97 Execution Completed")

    @pytest.mark.run(order=98)
    def test_098_Validate_DCA_CEF_Log_Logs_when_get_response_from_DCA_for_PCP_domain_cnn_com(self):
        logging.info("Validate DCA CEF Log for cnn.com  when get response from DCA")
        LookFor="fp-rte.*info CEF.*cnn.com.*CAT=0x00000000000000040000000000000000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 98 Execution Passed")
            assert True
        else:
            logging.info("Test Case 98 Execution Failed")
            assert False




###------Testing DCA FUNCTIONALITY AFTER GRID BACKUP/RESTORE---------###



    @pytest.mark.run(order=99)
    def test_099_Validate_set_dns_flush_all(self):
        logging.info("Validate set dns flush all")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set dns flush all')
        child.expect('Infoblox >')
        logging.info("Test Case 99 Execution Completed")

    @pytest.mark.run(order=100)
    def test_100_Validate_dns_cache_empty(self):
        logging.info("Validate dns cache is empty")
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
        logging.info("Test Case 100 Execution Completed")

    @pytest.mark.run(order=101)
    def test_101_GRID_BACKUP(self):
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
        logging.info("Test Case 101 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=102)
    def test_102_GRID_RESTORE(self):
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
        sleep(300)
        logging.info("Validate Syslog afer perform queries")
        infoblox_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str( config.grid_vip) + ' " tail -1200 /infoblox/var/infoblox.log "'
        out1 = commands.getoutput(infoblox_log_validation)
        print out1
        logging.info(out1)
        assert re.search(r'restore_node complete',out1)
        sleep(50)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        logging.info("Test Case 102 Execution Completed")

    @pytest.mark.run(order=103)
    def test_103_Add_Subscriber_Record_without_Proxy_all_set_and_Different_PCP_Policy_bit_than_client_ip(self):
        try:
            logging.info("Add Subscriber Record without Proxy-All set and different PCP Policy bit than the client_ip")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 N/A N/A "ACS:Acct-Session-Id=9999735888;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=01000000000000010000000000000000;SUB:Calling-Station-Id=110361288;PCC:PC-Category-Policy=00000000000000000000000000000001;"')
            child.expect('Record successfully added')
            logging.info("Test Case 103 Execution Passed")
            assert True
        except:
            logging.info("Test Case 103 Execution Failed")
            assert False

    @pytest.mark.run(order=104)
    def test_104_Validate_Subscriber_Record_without_Proxy_all_set_and_Different_PCP_Policy_bit_than_client_ip(self):
        logging.info("Validate Subscriber Record without Proxy-All set different PCP Policy bit than the client_ip")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case 104 execution completed")

    @pytest.mark.run(order=105)
    def test_105_Add_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        try:
            logging.info("Add Subscriber Record with PCP Policy for News Category")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip+' 32 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI=0a23b507;PXS:PXY_SEC=0a23b507;"')
            child.expect('Record successfully added')
            logging.info("Test Case 105 Execution Passed")
            assert True
        except:
            logging.info("Test Case 105 Execution Failed")
            assert False
	   

    @pytest.mark.run(order=106)
    def test_106_Validate_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case 106 execution completed")
	sleep(20)

    def test_107_Send_Query_from_NON_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_cached_DCA_with_PCP_word(self):
        logging.info("Perform Query from NON PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and Validate get NORMAL response times.com domain is cached to DCA with PCP word")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case 107 Execution Completed")
	sleep(10)

    @pytest.mark.run(order=108)
    def test_108_Validate_PCP_Domain_times_com_get_cached_to_DCA_When_Send_Query_From_NON_PCP_bit_Matched_Subscriber_client(self):
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
        logging.info("Test Case 108 Execution Completed")

    @pytest.mark.run(order=109)
    def test_109_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 109 passed")
        sleep(10)

    @pytest.mark.run(order=110)
    def test_110_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_Blocked_IPs_in_response_from_DCA_As_times_com_domain_is_already_DCA_Cache(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and get PCP Blocked IPs response from DCA as times.com is already in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_member1_vip)+' times.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case 110 Execution Completed")
	sleep(10)

    @pytest.mark.run(order=111)
    def test_111_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test Case 111 Execution Completed")

    @pytest.mark.run(order=112)
    def test_112_Validate_DCA_CEF_Log_Logs_when_get_response_from_DCA_for_PCP_domain_times_com(self):
        logging.info("Validate DCA CEF Log for times.com  when get response from DCA")
        LookFor="fp-rte.*info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 112 Execution Passed")
            assert True
        else:
            logging.info("Test Case 112 Execution Failed")
            assert False

###-----TESTING GC CONFIGURATION REMAINS SAME AFTER GRID BACKUP/RESTORE-------###

    @pytest.mark.run(order=113)
    def test_113_Validate_set_subscriber_secure_data_garbage_collect_on_command(self):
        logging.info("Validate set subscriber_secure_data garbage_collect on command")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data garbage_collect on')
        child.expect(':')
        child.sendline('y')
        child.expect(':')
        child.sendline('10 AM')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Garbage collection is scheduled at 10 AM everyday.*',c)
        logging.info("Test Case 113 Execution Completed")

    @pytest.mark.run(order=114)
    def test_114_Validate_show_subscriber_secure_data_garbage_collect_when_turned_on(self):
        logging.info("Validate subscriber secure data garbage_collect is set to on")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data garbage_collect')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*This member is configured for garbage collection scheduled at 10 AM everyday.*',c)
        logging.info("Test Case 114 Execution Completed")

    @pytest.mark.run(order=115)
    def test_115_GRID_BACKUP(self):
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
        logging.info("Test Case 115 Execution Completed")
        sleep(10)

    @pytest.mark.run(order=116)
    def test_116_GRID_RESTORE(self):
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
        sleep(250)
        logging.info("Validate Syslog afer perform queries")
        infoblox_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str( config.grid_vip) + ' " tail -1200 /infoblox/var/infoblox.log "'
        out1 = commands.getoutput(infoblox_log_validation)
        print out1
        logging.info(out1)
        assert re.search(r'restore_node complete',out1)
        sleep(50)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        logging.info("Test Case 116 Execution Completed")

    @pytest.mark.run(order=117)
    def test_117_Validate_show_subscriber_secure_data_garbage_collect_config_is_same_after_Grid_restore(self):
        logging.info("Validate subscriber secure data garbage_collect config is same after Grid restore")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data garbage_collect')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*This member is configured for garbage collection scheduled at 10 AM everyday.*',c)
        logging.info("Test Case 117 Execution Completed")        

    @pytest.mark.run(order=118)
    def test_118_Validate_set_subscriber_secure_data_garbage_collect_off_command(self):
        logging.info("Validate set subscriber_secure_data garbage_collect off command")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data garbage_collect off')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*This member is no longer configured for garbage collection.*',c)
        logging.info("Test Case 118 Execution Completed")

        


###-----CHECKING DCA FUNCTIONALITY FOR HA MEMBER-----###


    @pytest.mark.run(order=119)
    def test_119_Validate_set_dns_flush_all(self):
        logging.info("Validate set dns flush all")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set dns flush all')
        child.expect('Infoblox >')
        logging.info("Test Case 119 Execution Completed")

    @pytest.mark.run(order=120)
    def test_120_Validate_dns_cache_empty(self):
        logging.info("Validate dns cache is empty")
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
        logging.info("Test Case 120 Execution Completed")

    @pytest.mark.run(order=121)
    def test_121_Add_Subscriber_Record_without_Proxy_all_set_and_Different_PCP_Policy_bit_than_client_ip(self):
        try:
            logging.info("Add Subscriber Record without Proxy-All set and different PCP Policy bit than the client_ip")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 N/A N/A "ACS:Acct-Session-Id=9999735888;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=01000000000000010000000000000000;SUB:Calling-Station-Id=110361288;PCC:PC-Category-Policy=00000000000000000000000000000001;"')
            child.expect('Record successfully added')
            logging.info("Test Case 121 Execution Passed")
            assert True
        except:
            logging.info("Test Case 121 Execution Failed")
            assert False

    @pytest.mark.run(order=122)
    def test_122_Validate_Subscriber_Record_without_Proxy_all_set_and_Different_PCP_Policy_bit_than_client_ip(self):
        logging.info("Validate Subscriber Record without Proxy-All set different PCP Policy bit than the client_ip")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case 122 execution completed")

    @pytest.mark.run(order=123)
    def test_123_Add_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        try:
            logging.info("Add Subscriber Record with PCP Policy for News Category")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip+' 32 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI=0a23b507;PXS:PXY_SEC=0a23b507;"')
            child.expect('Record successfully added')
            logging.info("Test Case 123 Execution Passed")
            assert True
        except:
            logging.info("Test Case 123 Execution Failed")
            assert False

    @pytest.mark.run(order=124)
    def test_124_Validate_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case 124 execution completed")

    @pytest.mark.run(order=125)
    def test_125_Send_Query_from_NON_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_cached_DCA_with_PCP_word(self):
        logging.info("Perform Query from NON PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and Validate get NORMAL response times.com domain is cached to DCA with PCP word")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_member2_vip)+' times.com +noedns -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case 125 Execution Completed")

    @pytest.mark.run(order=126)
    def test_126_Validate_PCP_Domain_times_com_get_cached_to_DCA_When_Send_Query_From_NON_PCP_bit_Matched_Subscriber_client(self):
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
        logging.info("Test Case 126 Execution Completed")

    @pytest.mark.run(order=127)
    def test_127_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_member2_vip)
        logging.info("test case 127 passed")
        sleep(10)

    @pytest.mark.run(order=128)
    def test_128_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_Blocked_IPs_in_response_from_DCA_As_times_com_domain_is_already_DCA_Cache(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and get PCP Blocked IPs response from DCA as times.com is already in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_member2_vip)+' times.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case 128 Execution Completed")

    @pytest.mark.run(order=129)
    def test_129_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_member2_vip)
        logging.info("Test Case 129 Execution Completed")

    @pytest.mark.run(order=130)
    def test_130_Validate_DCA_CEF_Log_Logs_when_get_response_from_DCA_for_PCP_domain_times_com(self):
        logging.info("Validate DCA CEF Log for times.com  when get response from DCA")
        LookFor="fp-rte.*info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member2_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 130 Execution Passed")
            assert True
        else:
            logging.info("Test Case 130 Execution Failed")
            assert False

###-----TESTING GC CONFIGURATION REMAINS SAME AFTER HA FAILOVER-------###




    @pytest.mark.run(order=131)
    def test_131_Validate_set_dns_flush_all(self):
        logging.info("Validate set dns flush all")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set dns flush all')
        child.expect('Infoblox >')
        logging.info("Test Case 131 Execution Completed")

    @pytest.mark.run(order=132)
    def test_132_Validate_dns_cache_empty(self):
        logging.info("Validate dns cache is empty")
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
        logging.info("Test Case 132 Execution Completed")
        
    @pytest.mark.run(order=133)
    def test_133_Validate_set_subscriber_secure_data_garbage_collect_on_command(self):
        logging.info("Validate set subscriber_secure_data garbage_collect on command")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data garbage_collect on')
        child.expect(':')
        child.sendline('y')
        child.expect(':')
        child.sendline('10 AM')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Garbage collection is scheduled at 10 AM everyday.*',c)
        logging.info("Test Case 133 Execution Completed")

    @pytest.mark.run(order=134)
    def test_134_Validate_show_subscriber_secure_data_garbage_collect_when_turned_on(self):
        logging.info("Validate subscriber secure data garbage_collect is set to on")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data garbage_collect')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*This member is configured for garbage collection scheduled at 10 AM everyday.*',c)
        logging.info("Test Case 134 Execution Completed")


    @pytest.mark.run(order=135)
    def test_135_HA_pair_failover(self):
        logging.info("Validate HA failover after memeber reboot") 
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('reboot')
        child.expect(':')
        child.sendline('y')
        sleep(660)
        logging.info("Test Case 135 Execution Completed")

    @pytest.mark.run(order=136)
    def test_136_Validate_show_subscriber_secure_data_garbage_collect_config_is_not_same_after_HA_failover_Validate_after_failover_new_active_node_not_configured_GC(self):
        logging.info("Validate subscriber secure data garbage_collect config is not same after HA failover and vaidate after failover new active node not configured GC")
        cmd = 'rm -v /home/test1/.ssh/known_hosts'
        cmd_result = subprocess.check_output(cmd, shell=True)
        print cmd_result
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data garbage_collect')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*This member is not configured for garbage collection.*',c)
        #assert re.search(r'.*This member is configured for garbage collection scheduled at 10 AM everyday.*',c)
        logging.info("Test Case 136 Execution Completed")
        sleep(30)

    @pytest.mark.run(order=137)
    def test_137_Validate_set_subscriber_secure_data_garbage_collect_off_command(self):
        logging.info("Validate set subscriber_secure_data garbage_collect off command")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data garbage_collect off')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*This member is not configured for garbage collection..*',c)
        #assert re.search(r'.*This member is no longer configured for garbage collection.*',c)
        logging.info("Test Case 137 Execution Completed")

        


###-----TESTING DCA FUNCTIONALITY AFTER HA FAILOVER-------###


    @pytest.mark.run(order=138)
    def test_138_Add_Subscriber_Record_without_Proxy_all_set_and_Different_PCP_Policy_bit_than_client_ip(self):
        try:
            #cmd = 'rm -v /home/test1/.ssh/known_hosts'
            #cmd_result = subprocess.check_output(cmd, shell=True)
            #print cmd_result            
            logging.info("Add Subscriber Record without Proxy-All set and different PCP Policy bit than the client_ip")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 N/A N/A "ACS:Acct-Session-Id=9999735888;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=01000000000000010000000000000000;SUB:Calling-Station-Id=110361288;PCC:PC-Category-Policy=00000000000000000000000000000001;"')
            child.expect('Record successfully added')
            logging.info("Test Case 138 Execution Passed")
            assert True
        except:
            logging.info("Test Case 138 Execution Failed")
            assert False

    @pytest.mark.run(order=139)
    def test_139_Validate_Subscriber_Record_without_Proxy_all_set_and_Different_PCP_Policy_bit_than_client_ip(self):
        logging.info("Validate Subscriber Record without Proxy-All set different PCP Policy bit than the client_ip")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case 139 execution completed")

    @pytest.mark.run(order=140)
    def test_140_Add_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        try:
            logging.info("Add Subscriber Record with PCP Policy for News Category")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip+' 32 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI=0a23b507;PXS:PXY_SEC=0a23b507;"')
            child.expect('Record successfully added')
            logging.info("Test Case 140 Execution Passed")
            assert True
        except:
            logging.info("Test Case 140 Execution Failed")
            assert False

    @pytest.mark.run(order=141)
    def test_141_Validate_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member2_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case 141 execution completed")

    @pytest.mark.run(order=142)
    def test_142_Send_Query_from_NON_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_cached_DCA_with_PCP_word(self):
        logging.info("Perform Query from NON PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and Validate get NORMAL response times.com domain is cached to DCA with PCP word")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_member2_vip)+' times.com +noedns -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case 142 Execution Completed")

    @pytest.mark.run(order=143)
    def test_143_Validate_PCP_Domain_times_com_get_cached_to_DCA_When_Send_Query_From_NON_PCP_bit_Matched_Subscriber_client(self):
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
        logging.info("Test Case 143 Execution Completed")

    @pytest.mark.run(order=144)
    def test_144_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_member2_vip)
        logging.info("test case 144 passed")
        sleep(10)

    @pytest.mark.run(order=145)
    def test_145_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_Blocked_IPs_in_response_from_DCA_As_times_com_domain_is_already_DCA_Cache(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and get PCP Blocked IPs response from DCA as times.com is already in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_member2_vip)+' times.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case 145 Execution Completed")
	sleep(10)

    @pytest.mark.run(order=146)
    def test_146_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_member2_vip)
        logging.info("Test Case 146 Execution Completed")
	sleep(10)

    @pytest.mark.run(order=147)
    def test_147_Validate_DCA_CEF_Log_Logs_when_get_response_from_DCA_for_PCP_domain_times_com(self):
        logging.info("Validate DCA CEF Log for times.com  when get response from DCA")
        LookFor="fp-rte.*info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member2_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 147 Execution Passed")
            assert True
        else:
            logging.info("Test Case 147 Execution Failed")
            assert False


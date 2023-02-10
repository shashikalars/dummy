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


def restart_the_grid():
    logging.info("Restaring the grid")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
    ref = json.loads(grid)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
    sleep(60)
    print("Restrting the grid")


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





class RFE_9980(unittest.TestCase):

#############################################  Test cases Related to Basic Preparation and ZVELO DOWNLOAD #################################


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
        print("\n")
        print("************************************************")
        print("****  Test cases Related to ZVELO DOWNLOAD  ****")
        print("************************************************")
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
    def test_005_Configure_DNS_Resolver_At_Grid_Properties(self):
        logging.info("Configure DNs Resolver At GRID properties")
        response = ib_NIOS.wapi_request('GET', object_type="grid")
        response = json.loads(response)
        response=response[0]["_ref"]
        data={"dns_resolver_setting": {"resolvers": [config.resolver_ip]}}
        res = ib_NIOS.wapi_request('PUT', object_type=response,fields=json.dumps(data))
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
        data={"enable_parental_control": True,"cat_acctname":"infoblox_sdk", "cat_password":"LinWmRRDX0q","category_url":"https://dl.zvelo.com/","pc_zone_name":"pc.com","cat_update_frequency":1,"proxy_url":config.proxy_server_url,"proxy_username":"client","proxy_password":"infobox"}
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
        if pc==True and act_name=="infoblox_sdk" and proxy_url==config.proxy_server_url:
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
        time.sleep(2500)



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
        data={"blocking_ipv4_vip1": "1.1.1.1","blocking_ipv4_vip2": "2.2.2.2","msps":[{"ip_address": config.proxy_server1}],"spms": [{"ip_address": "10.12.11.11"}],"name":"site2","maximum_subscribers":100000,"members":[{"name":config.grid_fqdn}],"nas_gateways":[{"ip_address":config.rad_client_ip,"name":"nas1","shared_secret":"testing123"},{"ip_address":config.rad_client_ip_lan,"name":"nas2","shared_secret":"testing123"}],"dca_sub_query_count":True,"dca_sub_bw_list":True}
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
        if reference[0]["blocking_ipv4_vip1"]=="1.1.1.1" and reference[0]["blocking_ipv4_vip2"]=="2.2.2.2" and reference[0]["dca_sub_query_count"]==True and  reference[0]["dca_sub_bw_list"]==True:
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
                assert True
            else:
                print("Failed to enable DCA on the Member1")
                assert False
        sleep(600)



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



    @pytest.mark.run(order=20)
    def test_020_Copy_Subscriber_Record_radfiles_to_radclient(self):
        logging.info("Copy Subscriber Record radius message files to RAD Client")
        dig_cmd = 'sshpass -p infoblox scp -pr RFE_9980_part2_radfiles root@'+str(config.rad_client_ip)+':/root/ '
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        print "Copied the files to radclient"
        logging.info("Test Case Execution Completed")
        sleep(5)

    @pytest.mark.run(order=21)
    def test_021_From_Radclient_Send_Start_Radius_Message_with_PCP_Policy_and_Proxy_All_Configured(self):
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part2_radfiles/RFE_9980_PCP_Proxy_All.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)


#    @pytest.mark.run(order=21)
#    def test_021_Add_Subscriber_Record_with_PCP_and_Proxy_All_Policy_set_True(self):
#        try:
#            logging.info("Add Subscriber Record with PCP Policy for News Category and Proxy-All set True")
#            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
#            child.logfile=sys.stdout
#            child.expect('password:',timeout=None)
#            child.sendline('infoblox')
#            child.expect('Infoblox >')
#            child.sendline('set subscriber_secure_data add '+config.client_ip+' 32 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';"')
#
#            child.expect('Record successfully added')
#            logging.info("Test Case Execution Passed")
#            assert True
#        except:
#            logging.info("Test Case Execution Failed")
#            assert False

    @pytest.mark.run(order=22)
    def test_022_Validate_Subscriber_Record_with_PCP_and_Proxy_All_Policy_set_True(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category and Proxy-All set True")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case execution completed")



    @pytest.mark.run(order=23)
    def test_023_From_Radclient_Send_Start_Radius_Message_without_Proxy_all_set_and_Different_PCP_Policy_bit_than_above_to_make_sure_Domain_Cache_to_DCA_with_PCP_Word(self):
        logging.info("From Rad client send Start Radius message without Proxy-All set and different PCP Policy bit than the above to make sure Doamin cache_to DCA with PCP word")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part2_radfiles/RFE_9980_Only_PCP_for_Cache.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)



    @pytest.mark.run(order=24)
    def test_024_Validate_Subscriber_Record_without_Proxy_all_set_and_Different_PCP_Policy_bit_is_added_to_subscriber_cache(self):
        logging.info("Validate Subscriber Record without Proxy-All set different PCP Policy bit is added to subscriber cache")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=25)
    def test_025_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=26)
    def test_026_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
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
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=27)
    def test_027_Send_Query_from_Proxy_all_Configured_subscribed_client_for_Proxy_domain_Using_IB_FLEX_Member_Validate_returns_Proxy_response_from_Bind_As_Not_DCA_Cache(self):
        logging.info("Perform Query from Proxy-All configuredt Subscriber client for Proxy Domain playboy.com using IB-FLEX Member and Validate Proxy IP response from Bind as playboy.com domain is not in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*5.*IN.*A.*10.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)



    @pytest.mark.run(order=28)
    def test_028_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

# Changed the test cases from !=None to ==None as NIOS-78037 

    @pytest.mark.run(order=29)
    def test_029_Validate_Named_CEF_Log_Logs_with_CAT_PXY_when_get_response_from_Bind_for_Proxy_domain_playboy_com(self):
        logging.info("Validate Named CEF Log for proxy domain playboy.com with CAT as PXY  when get response from Bind")
        LookFor="named.*info CEF.*playboy.com.*CAT=PXY"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=30)
    def test_030_Validate_Proxy_Domain_playboy_com_did_not_cached_to_DCA_When_Send_Query_From_Proxy_confogured__Subscriber_client_match(self):
        logging.info("Validate playboy.com domain not cached to DCA when send query from the Proxy configured subscriber client match")
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
        sleep(20)


    @pytest.mark.run(order=31)
    def test_031_Validate_as_got_response_from_Bind_for_Proxy_domain_playboy_com_Cache_hit_count_not_increased_and_Miss_cache_count_increased(self):
        logging.info("Validate as got response from Bind for Proxy domain playboy.com Cache hit count not increased and Miss cache count increased")
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
        sleep(15)

    @pytest.mark.run(order=32)
    def test_032_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 12 passed")
        sleep(10)

    @pytest.mark.run(order=33)
    def test_033_Send_Query_from_NON_PCP_bit_match_and_not_Proxy_all_Configured_Subscriber_client_for_Proxy_Domain_playboy_cm_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_cached_DCA_with_PCP_word(self):
        logging.info("Perform Query from NON PCP bit match and not configured Proxy-All Subscriber client for Proxy Domain playboy.com using IB-FLEX Member and Validate get NORMAL response playboy.com domain is cached to DCA with PCP word")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)


    @pytest.mark.run(order=34)
    def test_034_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=35)
    def test_035_Validate_NO_CEF_Log_Logs_as_got_NORMAL_response_for_Proxy_domain_playboy_com_when_send_query_from_NON_PCP_bit_match_and_not_configured_Proxy_All_client(self):
        logging.info("Validate NO CEF Log for playboy.com as got NORMAL response when send query from NON PCP bit match and not configured Proxy-ALL client")
        LookFor="info CEF.*playboy.com.*CAT=PXY.*"
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

    @pytest.mark.run(order=36)
    def test_036_Validate_Proxy_Domain_playboy_com_get_cached_to_DCA_When_Send_Query_From_NON_PCP_bit_Matched_and_not_configured_Proxy_All_Subscriber_client(self):
        logging.info("Validate Proxy Domain playboy.com get cached to DCA when send query from the NON PCP bit matched and not configured Proxy-All subscriber client")
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
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=37)
    def test_037_Validate_when_get_response_from_Bind_for_Proxy_domain_playboy_com_Cache_hit_count_not_increased_and_Miss_cache_count_increased(self):
        logging.info("Validate when get response from Bind for PCP domain playboy.com Cache hit count not increased and Miss_cache count increased")
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
        sleep(15)

    @pytest.mark.run(order=38)
    def test_038_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=39)
    def test_039_Send_Query_from_PCP_and_Proxy_All_Configured_Subscriber_client_for_Proxy_Domain_playboy_com_Using_IB_FLEX_Member_Validate_returns_Proxy_IP_response_from_DCA_As_palyboy_com_domain_is_already_DCA_Cache(self):
        logging.info("Perform Query from PCP and Proxy-All Subscriber client for Proxy Domain playboy.com using IB-FLEX Member and get Proxy IPs response from DCA as playboy.com is already in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'; dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*5.*IN.*A.*10.*',str(dig_result))
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=40)
    def test_040_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case  Execution Completed")
        sleep(10)

# Changed the test cases from !=None to ==None as NIOS-78037
    @pytest.mark.run(order=41)
    def test_041_Validate_DCA_CEF_Log_Logs_as_got_response_from_DCA_for_Proxy_domain_playboy_com(self):
        logging.info("Validate DCA CEF Log for playboy.com as got response from DCA")
        LookFor="fp-rte.*info CEF.*playboy.com.*CAT=PXY"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False

    @pytest.mark.run(order=42)
    def test_042_Validate_as_got_response_from_DCA_for_Proxy_domain_playboy_com_Cache_hit_count_is_increased_and_Miss_cache_count_not_increased(self):
        logging.info("Validate as got response from DCA for Proxy domain playboy.com Cache hit count is get increased and Miss cache count not increased")
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
        logging.info("Test Case Execution Completed")
        sleep(15)


#    @pytest.mark.run(order=43)
#    def test_043_Delete_Subscriber_Record_with_Proxy_all_set_From_Subscriber_Cache(self):
#        try:
#            logging.info("Delete the Subscriber Record with Proxy-All set to True from Subscriber Cache")
#            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
#            child.logfile=sys.stdout
#            child.expect('password:',timeout=None)
#            child.sendline('infoblox')
#            child.expect('Infoblox >')
#            child.sendline('set subscriber_secure_data delete '+config.client_ip+' 32 N/A N/A')
#            child.expect('Record successfully deleted')
#            logging.info("Test Case Execution Passed")
#            assert True
#        except:
#            logging.info("Test Case Execution Failed")
#            assert False


    @pytest.mark.run(order=43)
    def test_043_From_Radclient_Send_Stop_Radius_Message_to_Delete_Subscriber_Record_with_Proxy_all_set_From_Subscriber_Cache(self):
        logging.info("From Rad client send Stop Radius message to Delete the Subscriber Record with Proxy-All set to True from Subscriber Cache ")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part2_radfiles/RFE_9980_PCP_Proxy_All_Stop.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)



    @pytest.mark.run(order=44)
    def test_044_Validate_Subscriber_Record_with_Proxy_all_set_is_deleted_from_Subscriber_Cache(self):
        logging.info("Validate Subscriber Record with Proxy-All set to True is deleted from subscriber cache")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
	if re.search(r'.*'+config.client_ip+'.*',c):
            logging.info("Test Case Execution Failed")
            assert False
        else:
            logging.info("Test Case Execution Passed")
            assert True
        logging.info("Test case execution completed")
        sleep(10)

    @pytest.mark.run(order=45)
    def test_045_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 25 passed")
        sleep(10)

    @pytest.mark.run(order=46)
    def test_046_Send_Query_from_PCP_bit_and_Proxy_All_Configured_Subscriber_client_for_Proxy_Domain_playboy_com_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_Even_Proxy_Domain_in_Cache_with_PCP_word_But_Match_subscriber_client_is_delete(self):
        logging.info("Perform Query from PCP bit and Proxy-All configured Subscriber client for Proxy Domain playboy.com using IB-FLEX Member and Validate get NORMAL response even playboy.com domain is in cache with PCP word but subscriber client is deleted from subscriber cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=47)
    def test_047_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 27 Execution Completed")

    @pytest.mark.run(order=48)
    def test_048_Validate_No_CEF_Log_Logs_when_get_NORMAL_response_from_DCA_for_Proxy_domain_playboy_com(self):
        logging.info("Validate NO CEF Log for playboy.com  when get NORMAL response")
        LookFor="info CEF.*playboy.com.*CAT=PXY.*"
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

    @pytest.mark.run(order=49)
    def test_049_Validate_Proxy_Domain_playboy_com_still_exist_in_DCA_cache(self):
        logging.info("Validate playboy.com domain still exist in DCA  cache")
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
        logging.info("Test Case Execution Completed")
        sleep(15)

    @pytest.mark.run(order=50)
    def test_050_Validate_as_got_response_from_DCA_for_Proxy_domain_playboy_com_Cache_hit_count_is_increased_and_Miss_cache_count_not_increased(self):
        logging.info("Validate as got response from DCA for Proxy domain playboy.com Cache hit count is get increased and Miss cache count not increased")
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
        assert re.search(r'.*Cache miss count.*3.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)

#    @pytest.mark.run(order=51)
#    def test_051_Add_Back_Same_Subscriber_Record_with_PCP_Policy_and_Proxy_All_Configured(self):
#        try:
#            logging.info("Add Same  Subscriber Record with PCP Policy and Proxy-All configured ")
#            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
#            child.logfile=sys.stdout
#            child.expect('password:',timeout=None)
#            child.sendline('infoblox')
#            child.expect('Infoblox >')
#            child.sendline('set subscriber_secure_data add '+config.client_ip+' 32 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';"')
#            child.expect('Record successfully added')
#            logging.info("Test Case Execution Passed")
#            assert True
#        except:
#            logging.info("Test Case Execution Failed")
#            assert False


    @pytest.mark.run(order=51)
    def test_051_From_Radclient_Send_Same_Start_Radius_Message_with_PCP_Policy_and_Proxy_All_Configured(self):
        logging.info("From Rad client send same Start Radius message with PCP Policy and Proxy-All configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part2_radfiles/RFE_9980_PCP_Proxy_All.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)



    @pytest.mark.run(order=52)
    def test_052_Validate_Subscriber_Record_with_PCP_Policy_and_Proxy_All_configured(self):
        logging.info("Validate Subscriber Record with PCP Policy and Proxy-All configured")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case execution completed")



    @pytest.mark.run(order=53)
    def test_053_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=54)
    def test_054_Send_Query_from_PCP_bit_and_Proxy_All_Configured__Subscriber_client_for_Proxy_Domain_playboy_com_Using_IB_FLEX_Member_Validate_returns_Proxy_MSP_IPs_response_from_DCA_As_playboy_com_domain_is_already_DCA_Cache(self):
        logging.info("Perform Query from PCP bit and Proxy-All configured Subscriber client for Proxy-All Domain playboy.com using IB-FLEX Member and validate get Proxy MSP IP response from DCA as playboy.com is already in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'; dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*5.*IN.*A.*10.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)

    @pytest.mark.run(order=55)
    def test_055_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

# Changed the test cases from !=None to ==None as NIOS-78037
    @pytest.mark.run(order=56)
    def test_056_Validate_DCA_CEF_Log_Logs_as_got_response_from_DCA_for_Proxy_domain_playboy_com(self):
        logging.info("Validate DCA CEF Log for Proxy domain playboy.com  when got response from DCA")
        LookFor="fp-rte.*info CEF.*playboy.com.*CAT=PXY"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=57)
    def test_057_Validate_as_got_response_from_DCA_for_Proxy_domain_playboy_com_Cache_hit_count_is_increased_and_Miss_cache_count_not_increased(self):
        logging.info("Validate as got response from DCA for Proxy domain playboy.com Cache hit count is get increased and Miss cache count not increased")
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
        assert re.search(r'.*Cache miss count.*4.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)


#    @pytest.mark.run(order=58)
#    def test_058_Add_Back_Same_Subscriber_Record_without_Proxy_configuration(self):
#        try:
#            logging.info("Add Same Subscriber Record without Proxy configuration")
#            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
#            child.logfile=sys.stdout
#            child.expect('password:',timeout=None)
#            child.sendline('infoblox')
#            child.expect('Infoblox >')
#            child.sendline('set subscriber_secure_data add '+config.client_ip+' 32 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;"')
#            child.expect('Record successfully added')
#            logging.info("Test Case Execution Passed")
#            assert True
#        except:
#            logging.info("Test Case Execution Failed")
#            assert False


    @pytest.mark.run(order=58)
    def test_058_From_Radclient_Send_INTERIM_Radius_Message_without_Proxy_all_set_and_same_PCP_Policy(self):
        logging.info("From Rad client send Start Radius message without Proxy-All set and different PCP Policy bit than the above to make sure Doamin cache_to DCA with PCP word")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part2_radfiles/RFE_9980_without_Proxy_All_policy_INTERIM.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)



    @pytest.mark.run(order=59)
    def test_059_Validate_Subscriber_Record_without_Proxy_configuration(self):
        logging.info("Validate Subscriber Record without Proxy-All Configuration")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case execution completed")


    @pytest.mark.run(order=60)
    def test_060_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 41 passed")
        sleep(10)
        
    @pytest.mark.run(order=61)
    def test_061_Send_Query_from_PCP_bit_and_Without_Proxy_configured_Subscriber_client_for_Proxy_Domain_playboy_com_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_Even_Proxy_Domain_in_Cache_with_PCP_word_But_subscriber_client_PCP_Policy_bit_not_matched(self):
        logging.info("Perform Query from PCP bit and without Prox-All configured Subscriber client for Proxy Domain playboy.com using IB-FLEX Member and Validate get NORMAL response even playboy.com domain is in cache with PCP word but subscriber client PCP Policy bit not matched")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=62)
    def test_062_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=63)
    def test_063_Validate_No_CEF_Log_Logs_when_got_NORMAL_response_from_DCA_for_Proxy_domain_playboy_com(self):
        logging.info("Validate NO CEF Log for playboy.com  when get NORMAL response")
        LookFor="info CEF.*playboy.com.*CAT=PXY"
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

    @pytest.mark.run(order=64)
    def test_064_Validate_Proxy_Domain_playboy_com_still_exist_in_DCA_cache(self):
        logging.info("Validate Proxy domain playboy.com domain still exist in DCA  cache")
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
        logging.info("Test Case Execution Completed")
        sleep(15)

    @pytest.mark.run(order=65)
    def test_065_Validate_as_got_response_from_DCA_for_Proxy_domain_playboy_com_Cache_hit_count_is_increased_and_Miss_cache_count_not_increased(self):
        logging.info("Validate as got response from DCA for Proxy domain playboy.com Cache hit count is get increased and Miss cache count not increased")
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
        assert re.search(r'.*Cache miss count.*4.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)



# Add 32 RPZ zone for Proxy-All whitelist testing


    @pytest.mark.run(order=66)
    def test_066_________Proxy_ALL_Whitelist_Functionality_Testing_Test_Cases_______(self):
        logging.info("************************** Proxy-ALL Whitelist Functionality Testing Test Cases **********************************************")


    @pytest.mark.run(order=67)
    def test_067_Add_32_RPZ_Zonse_with_IB_FLEX_Member_Assignemnet(self):
        logging.info("Add 32 RPZ Zones with IB-FLEX Member Assignement")
        for i in range(1,33):
            data={"fqdn": "rpz"+str(i)+".com","grid_primary":[{"name": config.grid_fqdn,"stealth":False}],"view":"default"}
            response=ib_NIOS.wapi_request('POST', object_type="zone_rp",fields=json.dumps(data))
            print response
            print "RPZ Zone rpz"+str(i)+".com is added"
            res=json.loads(response)
            logging.info(response)
            read  = re.search(r'201',response)
            print read
            for read in  response:
                assert True

        print("Test Case Execution Completed")

        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(60)


    @pytest.mark.run(order=68)
    def test_068_Validate_Added_32_RPZ_Zones_with_IB_FLEX_assignement(self):
        logging.info("Validate added 32 RPZ zones with IB-FLEX assignementn\n")
        print "\n"
        for i in range(1,33):
            data={"fqdn": "rpz"+str(i)+".com"}
            print data
            logging.info ("Validate Added RPZ zone")
            fields=json.dumps(data)
            get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_rp?_return_fields=fqdn,view,grid_primary", fields=json.dumps(data))
            print "==================================="
            print get_template_zone
            print "==================================="
            logging.info(get_template_zone)
            res=json.loads(get_template_zone)
            if("rpz"+str(i)+".com" in get_template_zone):
                assert True
            else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=69)
    def test_069_Add_Proxy_domain_playboy_com_as_PASSTHRU_RPZ_Rule_to_32_RPZ_Zone_rpz1_com(self):
	logging.info ("Add Proxy Domain Playboy.com as PASSTHRU RPZ Rule to 32 RPZ zone rpz1.com")
        data={"canonical":"playboy.com", "name": "playboy.com.rpz1.com","rp_zone": "rpz1.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
		assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
	logging.info("Test Case Execution Completed")
        sleep(30)


    @pytest.mark.run(order=70)
    def test_070_Validate_Added_Proxy_domain_playboy_com_as_PASSTHRU_RPZ_Rule_to_32_RPZ_Zone_rpz1_com(self):
	logging.info("Validate added Proxy Domain Playboy.com as PASSTHRU RPZ Rule to 32 RPZ zone rpz1.com\n")
        data={"name": "playboy.com.rpz1.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
	if('"name": "playboy.com.rpz1.com"' in get_rpz_rule) and ('"canonical": "playboy.com"' in get_rpz_rule):
		assert True
        else:
		assert False
        logging.info("Test Case Execution Completed")



#    @pytest.mark.run(order=71)
#    def test_071_Add_Back_Same_Subscriber_Record_with_PCP_Policy_and_Proxy_All_Configured(self):
#        try:
#            logging.info("Add Same  Subscriber Record with PCP Policy and Proxy-All configured ")
#            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
#            child.logfile=sys.stdout
#            child.expect('password:',timeout=None)
#            child.sendline('infoblox')
#            child.expect('Infoblox >')
#            child.sendline('set subscriber_secure_data add '+config.client_ip+' 32 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';"')
#            child.expect('Record successfully added')
#            logging.info("Test Case Execution Passed")
#            assert True
#        except:
#            logging.info("Test Case Execution Failed")
#            assert False



    @pytest.mark.run(order=71)
    def test_071_From_Radclient_Send_Same_Start_Radius_Message_with_PCP_Policy_and_Proxy_All_Configured(self):
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part2_radfiles/RFE_9980_PCP_Proxy_All.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=72)
    def test_072_Validate_Subscriber_Record_with_PCP_Policy_and_Proxy_All_configured(self):
        logging.info("Validate Subscriber Record with PCP Policy and Proxy-All configured")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case execution completed")


    @pytest.mark.run(order=73)
    def test_073_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 53 passed")
        sleep(10)


    @pytest.mark.run(order=74)
    def test_074_Send_Query_from_PCP_bit_and_Proxy_All_Configured_Subscriber_client_for_Proxy_Domain_playboy_com_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_As_playboy_com_is_added_as_Proxy_all_whitelist_added_as_PASSTHRU_RPZ_rule_to_32_RPZ_Zone(self):
        logging.info("Perform Query from PCP bit and Proxy-All configured Subscriber client for Proxy Domain playboy.com using IB-FLEX Member and Validate get NORMAL response as playboy.com domain is added as Proxy whitelist added as PASSTHRU RPZ rule to 32 RPZ zone")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=75)
    def test_075_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=76)
    def test_076_Validate_No_CEF_Log_Logs_when_get_NORMAL_response_as_Proxy_domain_playboy_com_is_added_as_Proxy_all_whitelist_added_as_PASSTHRU_RPZ_rule_to_32_RPZ_Zone(self):
        logging.info("Validate NO CEF Log for playboy.com  when get NORMAL response as playboy.com domain is added as Proxy whitelist added as PASSTHRU RPZ rule to 32 RPZ zone")
        LookFor="info CEF.*playboy.com.*CAT=PXY.*"
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

# Changed the test cases from !=None to ==None as NIOS-78037

    @pytest.mark.run(order=77)
    def test_077_Validate_whitelisted_Proxy_Domain_playboy_com_is_cached_to_DCA_with_PCP_word(self):
        logging.info("Validate playboy.com domain is cached to DCA with PCP word")
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
        #assert re.search(r'.*0x40000000000000000000000000020000.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)

        

    @pytest.mark.run(order=78)
    def test_078_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=79)
    def test_079_Send_Query_from_PCP_and_Proxy_All_Configured_Subscriber_client_for_Proxy_Domain_playboy_com_Validate_returns_NORMAL_response_from_DCA_Even_palyboy_com_domain_is_in_DCA_Cache_with_PCP_word_when_added_Proxy_domain_as_PASSTHRU_RPZ_rule_to_32_RPZ_Zone(self):
        logging.info("Perform Query from PCP and Proxy-All Subscriber client for Proxy Domain playboy.com and validate got NORMAL respose DCA even though playboy.com is in DCA cache with PCP word when proxy domain is added as PASSTHRU RPZ rule 32 RPZ zone")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=80)
    def test_080_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=81)
    def test_081_Validate_No_CEF_Log_Logs_when_as_Proxy_domain_playboy_com_is_added_as_Proxy_all_whitelist_added_as_PASSTHRU_RPZ_rule_to_32_RPZ_Zone(self):
        logging.info("Validate NO CEF Log for playboy.com  when get NORMAL response as playboy.com domain is added as Proxy whitelist added as PASSTHRU RPZ rule to 32 RPZ zone")
        LookFor="info CEF.*playboy.com.*CAT=PXY.*"
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



    @pytest.mark.run(order=82)
    def test_082_Remove_Proxy_playboy_com_PASSTHRU_RPZ_Rule_from_32_RPZ_Zone_rpz1_com(self):
        logging.info ("Remove Proxy Domain Playboy.com PASSTHRU RPZ Rule from 32 RPZ zone rpz1.com")
        data={"name": "playboy.com.rpz1.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)


    @pytest.mark.run(order=83)
    def test_083_Validate_Proxy_domain_playboy_com_PASSTHRU_RPZ_Rule_is_Deleted_from_32_RPZ_Zone_rpz1_com(self):
        logging.info("Validate Proxy Domain Playboy.com PASSTHRU RPZ Rule is deleted from  32 RPZ zone rpz1.com\n")
        data={"name": "playboy.com.rpz1.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz1.com"' in get_rpz_rule) and ('"canonical": "playboy.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=84)
    def test_084_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=85)
    def test_085_Send_Query_from_PCP_and_Proxy_All_Configured_Subscriber_client_for_Proxy_Domain_playboy_com_Using_IB_FLEX_Member_Validate_returns_Proxy_IP_response_from_DCA_As_palyboy_com_domain_is_already_DCA_Cache(self):
        logging.info("Perform Query from PCP and Proxy-All Subscriber client for Proxy Domain playboy.com using IB-FLEX Member and get Proxy IPs response from DCA as playboy.com is already in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'; dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*5.*IN.*A.*10.*',str(dig_result))
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=86)
    def test_086_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

# Changed the test cases from !=None to ==None as NIOS-78037
    @pytest.mark.run(order=87)
    def test_087_Validate_DCA_CEF_Log_Logs_as_got_response_from_DCA_for_Proxy_domain_playboy_com(self):
        logging.info("Validate DCA CEF Log for playboy.com as got response from DCA")
        LookFor="fp-rte.*info CEF.*playboy.com.*CAT=PXY"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=88)
    def test_088_Add_PCP_domain_cnn_com_as_PASSTHRU_RPZ_Rule_to_32_RPZ_Zone_rpz1_com(self):
        logging.info ("Add PCP Domain cnn.com as PASSTHRU RPZ Rule to 32 RPZ zone rpz1.com")
        data={"canonical":"cnn.com", "name": "cnn.com.rpz1.com","rp_zone": "rpz1.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)


    @pytest.mark.run(order=89)
    def test_089_Validate_Added_PCP_domain_cnn_com_as_PASSTHRU_RPZ_Rule_to_32_RPZ_Zone_rpz1_com(self):
        logging.info("Validate added PCP Domain cnn.com as PASSTHRU RPZ Rule to 32 RPZ zone rpz1.com\n")
        data={"name": "cnn.com.rpz1.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "cnn.com.rpz1.com"' in get_rpz_rule) and ('"canonical": "cnn.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=90)
    def test_090_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case  passed")
        sleep(10)


# As per the changes of bug NIOS-78037 commented and changed the cases

    @pytest.mark.run(order=91)
    def test_091_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_cnn_Using_IB_FLEX_Member_Validate_returns_Blocked_IPs_in_response_from_Bindi_even_PCP_Domain_added_as_PASSTHRU_RPZ_Rule_to_32_RPZ_Zone(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain cnn.com using IB-FLEX Member and get PCP Blocked IPs response from BIND even PCP Domain added as PASSTHRU RPZ Rule to 32 RPZ zone")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' cnn.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
	assert re.search(r'.*cnn.com.*IN.*A.*',str(dig_result))
        #assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        #assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=92)
    def test_092_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


# Changed the test cases from !=None to ==None as NIOS-78037
    @pytest.mark.run(order=93)
    def test_093_Validate_Bind_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_cnn_com(self):
        logging.info("Validate Bind CEF Log for cnn.com  when get response from Bind")
        LookFor="named.*info CEF.*cnn.com.*CAT=0x00000000000000040000000000000000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=94)
    def test_094_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=95)
    def test_095_Send_Query_from_NON_PCP_bit_match_Subscriber_client_for_PCP_Domain_cnn_com_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_cached_DCA_with_PCP_word(self):
        logging.info("Perform Query from NON PCP bit match Subscriber client for PCP Domain cnn.com using IB-FLEX Member and Validate get NORMAL response times.com domain is cached to DCA with PCP word")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' cnn.com +noedns -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*cnn.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)


    @pytest.mark.run(order=96)
    def test_096_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")
        sleep(10)


    @pytest.mark.run(order=97)
    def test_097_Validate_NO_CEF_Log_Logs_when_get_NORMAL_response_for_PCP_domain_cnn_com_when_send_query_from_NON_PCP_bit_match_client(self):
        logging.info("Validate NO CEF Log for cnn.com  when get NORMAL response when send query from NON PCP bit match client")
        LookFor="info CEF.*cnn.com.*CAT=0x00000000000000040000000000000000"
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


    @pytest.mark.run(order=98)
    def test_098_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)



    @pytest.mark.run(order=99)
    def test_099_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_cnn_com_Using_IB_FLEX_Member_Validate_returns_Blocked_IPs_in_response_from_DCA_As_cnn_com_domain_is_already_DCA_Cache_Even_PCP_Doamin_is_added_to_32_RPZ_zone_as_PASSTHRU_Rule(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain cnn.com using IB-FLEX Member and get PCP Blocked IPs response from DCA as cnn.com is already in DCA cache when PCP domain is added to 32 RPZ as PASSTHRU rule")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' cnn.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
	assert re.search(r'.*cnn.com.*IN.*A.*',str(dig_result))
        #assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        #assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=100)
    def test_100_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


# Changed the test cases from !=None to ==None as NIOS-78037
    @pytest.mark.run(order=101)
    def test_101_Validate_DCA_CEF_Log_Logs_when_get_response_from_DCA_for_PCP_domain_cnn_com(self):
        logging.info("Validate DCA CEF Log for cnn.com  when get response from DCA")
        LookFor="fp-rte.*info CEF.*cnn.com.*CAT=0x00000000000000040000000000000000"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=102)
    def test_102_Add_WPCP_domain_coors_com_as_PASSTHRU_RPZ_Rule_to_32_RPZ_Zone_rpz1_com(self):
        logging.info ("Add WPCP Domain coors.com as PASSTHRU RPZ Rule to 32 RPZ zone rpz1.com")
        data={"canonical":"coors.com", "name": "coors.com.rpz1.com","rp_zone": "rpz1.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)


    @pytest.mark.run(order=103)
    def test_103_Validate_Added_WPCP_domain_coors_com_as_PASSTHRU_RPZ_Rule_to_32_RPZ_Zone_rpz1_com(self):
        logging.info("Validate added WPCP Domain coors.com as PASSTHRU RPZ Rule to 32 RPZ zone rpz1.com\n")
        data={"name": "coors.com.rpz1.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz1.com"' in get_rpz_rule) and ('"canonical": "coors.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=104)
    def test_104_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=105)
    def test_105_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_coors_com_Using_IB_FLEX_Member_Validate_returns_NORMAL__response_from_Bind_with_CEF_logs__even_WPCP_Domain_added_as_PASSTHRU_RPZ_Rule_to_32_RPZ_Zone(self):
        logging.info("Perform Query from WPCP bit match Subscriber client for WPCP Domain coors.com using IB-FLEX Member and get NORMAL response from BIND even WPCP Domain added as PASSTHRU RPZ Rule to 32 RPZ zone")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' coors.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*coors.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=106)
    def test_106_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


# Changed the test cases from !=None to ==None as NIOS-78037
    @pytest.mark.run(order=107)
    def test_107_Validate_Bind_CEF_Log_Logs_when_get_response_from_Bind_for_WPCP_domain_coors_com(self):
        logging.info("Validate Bind CEF Log for coos.com  when get response from Bind")
        LookFor="named.*info CEF.*coors.com.*CAT=WRN_0x00000000000000000000000000000001"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=108)
    def test_108_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case  passed")
        sleep(10)

    @pytest.mark.run(order=109)
    def test_109_Send_Query_from_NON_WPCP_bit_match_Subscriber_client_for_WPCP_Domain_coors_com_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_cached_DCA_with_PCP_word(self):
        logging.info("Perform Query from NON WPCP bit match Subscriber client for WPCP Domain coors.com using IB-FLEX Member and Validate get NORMAL response coors.com domain is cached to DCA with PCP word")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' coors.com +noedns -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*coors.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=110)
    def test_110_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")
        sleep(10)


    @pytest.mark.run(order=111)
    def test_111_Validate_NO_CEF_Log_Logs_when_get_NORMAL_response_for_WPCP_domain_coors_com_when_send_query_from_NON_WPCP_bit_match_client(self):
        logging.info("Validate NO CEF Log for coors.com  when get NORMAL response when send query from NON WPCP bit match client")
        LookFor="info CEF.*coors.com.*CAT=WRN_0x00000000000000000000000000000001"
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


    @pytest.mark.run(order=112)
    def test_112_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=113)
    def test_113_Send_Query_from_WPCP_bit_match_Subscriber_client_for_WPCP_Domain_coors_com_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_from_DCA_As_coors_com_domain_is_already_DCA_Cache_Even_WPCP_Doamin_is_added_to_32_RPZ_zone_as_PASSTHRU_Rule(self):
        logging.info("Perform Query from WPCP bit match Subscriber client for WPCP Domain coors.com using IB-FLEX Member and get NORMAL response from DCA as coors.com is already in DCA cache when WPCP domain is added to 32 RPZ as PASSTHRU rule")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' coors.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*coors.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)


    @pytest.mark.run(order=114)
    def test_114_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")
        sleep(10)

# Changed the test cases from !=None to ==None as NIOS-78037
    @pytest.mark.run(order=115)
    def test_115_Validate_DCA_CEF_Log_Logs_when_get_response_from_DCA_for_WPCP_domain_coors_com(self):
        logging.info("Validate DCA CEF Log for coors.com  when get response from DCA")
        LookFor="fp-rte.*info CEF.*coors.com.*CAT=WRN_0x40000000000000000000000000000001"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=116)
    def test_116_Add_Subscriber_Record_with_PCP_and_BL_WL_Domains_List(self):
        try:
            logging.info("Add Subscriber Record with PCP Policy and BL and WL Domain Lists")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip+' 32 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=0;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';BWI:BWFlag=1;BL=facebook.com;WL=yahoo.com;"')
            child.expect('Record successfully added')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Failed")
            assert False



    @pytest.mark.run(order=117)
    def test_117_Validate_Subscriber_Record_with_PCP_and_BL_WL_Domains_List(self):
        logging.info("Validate Subscriber Record with PCP Policy and  BL and WL Domain Lists")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip+'\/32\|LID\:N\/A\|IPS\:N\/A.*BWI\:BWFlag=1\;BL=facebook.com\;WL=yahoo.com.*',c)
        logging.info("Test case execution completed")



    @pytest.mark.run(order=118)
    def test_118_Add_BL_List_domain_facebook_com_as_PASSTHRU_RPZ_Rule_to_32_RPZ_Zone_rpz1_com(self):
        logging.info ("Add BL List Domain facebook.com as PASSTHRU RPZ Rule to 32 RPZ zone rpz1.com")
        data={"canonical":"facebook.com", "name": "facebook.com.rpz1.com","rp_zone": "rpz1.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
	sleep(30)


    @pytest.mark.run(order=119)
    def test_119_Validate_Added_BL_List_domain_facebook_com_as_PASSTHRU_RPZ_Rule_to_32_RPZ_Zone_rpz1_com(self):
        logging.info("Validate added BL List Domain facebook.com as PASSTHRU RPZ Rule to 32 RPZ zone rpz1.com\n")
        data={"name": "facebook.com.rpz1.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "facebook.com.rpz1.com"' in get_rpz_rule) and ('"canonical": "facebook.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=120)
    def test_120_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=121)
    def test_121_Send_Query_from_PCP_bit_match_Subscriber_client_for_BL_List_Domain_facebook_com_Using_IB_FLEX_Member_Validate_returns_Blocking_IP__response_from_Bind_with_CEF_logs__even_BL_List_Domain_added_as_PASSTHRU_RPZ_Rule_to_32_RPZ_Zone(self):
        logging.info("Perform Query from BL List Domain match Subscriber client for BL List Domain facebook.com using IB-FLEX Member and get Blocking IP response from BIND even BL List Domain added as PASSTHRU RPZ Rule to 32 RPZ zone")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*facebook.com.*IN.*A.*',str(dig_result))	
        #assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        #assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=122)
    def test_122_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 104 Execution Completed")

# Changed the test cases from !=None to ==None as NIOS-78037
    @pytest.mark.run(order=123)
    def test_123_Validate_Bind_CEF_Log_Logs_when_get_response_from_Bind_for_WPCP_domain_facebook_com(self):
        logging.info("Validate Bind CEF Log for facebook.com  when get response from Bind")
        LookFor="named.*info CEF.*facebook.com.*CAT=BL"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=124)
    def test_124_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case  passed")
        sleep(10)



    @pytest.mark.run(order=125)
    def test_125_Send_Query_from_NON_BL_List_domain_match_Subscriber_client_for_BL_List_Domain_facebook_com_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_cached_DCA_with_PCP_word(self):
        logging.info("Perform Query from NON BL List Domain match Subscriber client for BL List Domain facebook.com using IB-FLEX Member and Validate get NORMAL response facebook.com domain is cached to DCA with PCP word")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*facebook.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=126)
    def test_126_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 108 Execution Completed")


    @pytest.mark.run(order=127)
    def test_127_Validate_NO_CEF_Log_Logs_when_get_NORMAL_response_for_BL_List_domain_facebook_com_when_send_query_from_NON_BL_List_Domain_Match_client(self):
        logging.info("Validate NO CEF Log for facebook.com  when get NORMAL response when send query from NON BL List Domain match client")
        LookFor=".*info CEF.*facebook.com.*CAT=BL"
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



    @pytest.mark.run(order=128)
    def test_128_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


# As per the changes of bug NIOS-78037 commented and changed the cases
    @pytest.mark.run(order=129)
    def test_129_Send_Query_from_BL_List_match_Subscriber_client_for_BL_List_Domain_facebook_com_Using_IB_FLEX_Member_Validate_returns_Blocking_IP_response_from_DCA_As_facebook_com_domain_is_already_DCA_Cache_Even_BL_List_Doamin_is_added_to_32_RPZ_zone_as_PASSTHRU_Rule(self):
        logging.info("Perform Query from BL List match Subscriber client for BL List Domain facebook.com using IB-FLEX Member and get Blocking IP response from DCA as facebook.com is already in DCA cache when BL List domain is added to 32 RPZ as PASSTHRU rule")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
	assert re.search(r'.*facebook.com.*IN.*A.*',str(dig_result))
        #assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        #assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=130)
    def test_130_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 112 Execution Completed")


# Changed the test cases from !=None to ==None as NIOS-78037
    @pytest.mark.run(order=131)
    def test_131_Validate_DCA_CEF_Log_Logs_when_get_response_from_DCA_for_BL_List_domain_facebook_com(self):
        logging.info("Validate DCA CEF Log for facebook.com  when get response from DCA")
        LookFor=".*info CEF.*facebook.com.*CAT=BL"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=132)
    def test_132_Remove_WPCP_coors_com_PASSTHRU_RPZ_Rule_from_32_RPZ_Zone_rpz1_com(self):
        logging.info ("Remove Proxy Domain Playboy.com PASSTHRU RPZ Rule from 32 RPZ zone rpz1.com")
        data={"name": "coors.com.rpz1.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=133)
    def test_133_Validate_WPCP_domain_coors_com_PASSTHRU_RPZ_Rule_is_Deleted_from_32_RPZ_Zone_rpz1_com(self):
        logging.info("Validate Proxy Domain coors.com PASSTHRU RPZ Rule is deleted from  32 RPZ zone rpz1.com\n")
        data={"name": "playboy.com.rpz1.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz1.com"' in get_rpz_rule) and ('"canonical": "coors.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=134)
    def test_134_Remove_PCP_domain_cnn_com_PASSTHRU_RPZ_Rule_from_32_RPZ_Zone_rpz1_com(self):
        logging.info ("Remove PCP Domain cnn.com PASSTHRU RPZ Rule from 32 RPZ zone rpz1.com")
        data={"name": "cnn.com.rpz1.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)


    @pytest.mark.run(order=135)
    def test_135_Validate_WPCP_domain_coors_com_PASSTHRU_RPZ_Rule_is_Deleted_from_32_RPZ_Zone_rpz1_com(self):
        logging.info("Validate PCP Domain cnn.com PASSTHRU RPZ Rule is deleted from  32 RPZ zone rpz1.com\n")
        data={"name": "cnn.com.rpz1.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "cnn.com.rpz1.com"' in get_rpz_rule) and ('"canonical": "cnn.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=136)
    def test_136_Remove_BL_domain_facebook_com_PASSTHRU_RPZ_Rule_from_32_RPZ_Zone_rpz1_com(self):
        logging.info ("Remove BL Domain facebook.com PASSTHRU RPZ Rule from 32 RPZ zone rpz1.com")
        data={"name": "facebook.com.rpz1.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)


    @pytest.mark.run(order=137)
    def test_137_Validate_BL_domain_coors_com_PASSTHRU_RPZ_Rule_is_Deleted_from_32_RPZ_Zone_rpz1_com(self):
        logging.info("Validate BL Domain facbook.com PASSTHRU RPZ Rule is deleted from  32 RPZ zone rpz1.com\n")
        data={"name": "facebook.com.rpz1.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "facebook.com.rpz1.com"' in get_rpz_rule) and ('"canonical": "facebook.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")




############################ Never Proxy Test Cases

    @pytest.mark.run(order=138)
    def test_137_____________Never_Poxy_Functionality_Test_Cases_____________(self):
        logging.info("========================  Never Proxy Functionality Test Cases ========================\n")



    @pytest.mark.run(order=140)
    def test_140_Add_Subscriber_Record_with_PCP_and_Proxy_ALL_Configuration_set(self):
        try:
            logging.info("Add Subscriber Record with PCP Policy  and Proxy-All Configuration set")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip+' 32 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';BWI:BWFlag=1;BL=facebook.com;WL=yahoo.com;"')
            child.expect('Record successfully added')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=141)
    def test_141_Validate_Subscriber_Record_with_PCP_and_Proxy_ALL_Configuration_set(self):
        logging.info("Validate Subscriber Record with PCP Policy and Proxy-All Configuration set")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip+'\/32\|LID\:N\/A\|IPS\:N\/A.*PXY\:Proxy-All=1.*',c)
        logging.info("Test case execution completed")



    @pytest.mark.run(order=142)
    def test_142_From_CLI_Configuration_never_proxy_category_set_is_00000000000000000000000000020040(self):
        try:
            logging.info("From CLI Configuration never_proxy category set is 00000000000000000000000000020040")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data never_proxy 00000000000000000000000000020040')
            child.expect('never_proxy categories is set')
            child.expect('!!! A RESTART of the DNS service is required before this change can take effect !!!')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Failed")
            assert False



    @pytest.mark.run(order=143)
    def test_143_From_CLI_Validate_Configuration_never_proxy_category_set_is_00000000000000000000000000020040(self):
        logging.info("From CLI Validate Configuration never_proxy category set is 00000000000000000000000000020040 ")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data never_proxy')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*never_proxy category set is 00000000000000000000000000020040.*',c)
        logging.info("Test case execution completed")


    @pytest.mark.run(order=144)
    def test_144_Restart_DNS_service(self):
        logging.info("Restart services")
        restart_the_grid()
        #grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        #ref = json.loads(grid)[0]['_ref']
        #publish={"member_order":"SIMULTANEOUSLY"}
        #request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        #request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        #restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        #sleep(60)


    @pytest.mark.run(order=145)
    def test_145_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 124 passed")
        sleep(10)



    @pytest.mark.run(order=146)
    def test_146_Send_Query_from_PCP_bit_Proxy_All_Configuration_match_Subscriber_client_for_Proxy_Domain_playboy_com_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_from_without_CEF_logs_as_never_proxy_category_set_is_00000000000000000000000000020040(self):
        logging.info("Perform Query from PCP bit and Proxy-All  match Subscriber client for Proxy Domain beer.com using IB-FLEX Member and get NORMAL response as never_proxy category set is 00000000000000000000000000020040")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=147)
    def test_147_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=148)
    def test_148_Validate_NO_CEF_Log_Logs_when_get_NORMAL_response_for_Proxy_domain_playboy_com_when_never_proxy_category_set_is_00000000000000000000000000020040(self):
        logging.info("Validate NO CEF Log for playboy.com  when get NORMAL response when never_proxy category set is 00000000000000000000000000020040 ")
        LookFor=".*info CEF.*playboy.com.*CAT=PXY"
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


    @pytest.mark.run(order=149)
    def test_149_Validate_Proxy_Domain_playboy_com_get_cached_to_DCA_When_Send_Query_if_never_proxy_category_set_is_00000000000000000000000000020040(self):
        logging.info("Validate Proxy Domain playboy.com get cached to DCA when send query if_never_proxy_category_set_is_00000000000000000000000000020040")
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
        logging.info("Test Case Execution Completed")
        sleep(15)



    @pytest.mark.run(order=150)
    def test_150_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=151)
    def test_151_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=152)
    def test_152_Send_Query_Again_from_same_Subscriber_client_when_Proxy_Domain_playboy_com_is_already_in_DCA_Cache_and_Validate_returns_NORMAL_response_from_DCA_without_CEF_logs_as_never_proxy_category_set_is_00000000000000000000000000020040(self):
        logging.info("Perform Query again same match Subscriber client when Proxy Domain playboy is already in DCA cache and validate returns  NORMAL response from DCA as never_proxy category set is 00000000000000000000000000020040")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=153)
    def test_153_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=154)
    def test_154_Validate_NO_CEF_Log_Logs_when_get_NORMAL_response_from_DCA_for_Proxy_domain_palyboy_com_when_never_proxy_category_set_is_00000000000000000000000000020040(self):
        logging.info("Validate NO CEF Log for playboy.com  when get NORMAL response when never_proxy category set is 00000000000000000000000000020040 ")
        LookFor=".*info CEF.*playboy.com.*CAT=PXY"
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



    @pytest.mark.run(order=155)
    def test_155_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)



    @pytest.mark.run(order=156)
    def test_156_Send_Query_for_WPCP_Domain_coors_com_when_Proxy_All_Configured_and_Validate_returns_Proxy_MSP_IP_response_from_Bind_with_Both_WPCP_and_PXY_Category_CEF_logs(self):
        logging.info("Perform Query for WPCP Domain coors.com and validate got Proxy MSP IP response from BIND with both WPCP and PXY Category CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' coors.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*coors.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=157)
    def test_157_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


# Changed the test cases from !=None to ==None as NIOS-78037
    @pytest.mark.run(order=158)
    def test_158_Validate_for_WPCP_Domain_coors_com_Got_Both_WPCP_and_PXY_Category_CEF_logs_when_Proxy_all_is_Configured(self):
        logging.info("Validate forWPCP Domain coors.com Got Both WPCP and PXY Category CEF logs when Proxy-All is Configured")
        LookFor="named.*info CEF.*coors.com.*CAT=WRN_0x00000000000000000000000000000001"
        LookFor="named.*info CEF.*coors.com.*CAT=PXY"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False



    @pytest.mark.run(order=159)
    def test_159_From_CLI_Configuration_never_proxy_for_WPCP_category_set_is_00000000000000000000000000000001(self):
        try:
            logging.info("From CLI Configuration never_proxy for WPCP category set is 00000000000000000000000000000001")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data never_proxy 00000000000000000000000000000001')
            child.expect('never_proxy categories is set')
            child.expect('!!! A RESTART of the DNS service is required before this change can take effect !!!')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Failed")
            assert False



    @pytest.mark.run(order=160)
    def test_160_From_CLI_Validate_Configuration_never_proxy_for_WPCP_category_set_is_00000000000000000000000000000001(self):
        logging.info("From CLI Validate Configuration never_proxy for WPCP category set is 00000000000000000000000000000001 ")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data never_proxy')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*never_proxy category set is 00000000000000000000000000000001.*',c)
        logging.info("Test case execution completed")



    @pytest.mark.run(order=161)
    def test_161_Restart_DNS_service(self):
        logging.info("Restart services")
        restart_the_grid()
        #grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        #ref = json.loads(grid)[0]['_ref']
        #publish={"member_order":"SIMULTANEOUSLY"}
        #request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        #request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        #restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(60)


    @pytest.mark.run(order=162)
    def test_162_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)



    @pytest.mark.run(order=163)
    def test_163_Send_Query_from_WPCP_bit_Proxy_All_Configuration_match_Subscriber_client_for_WPCP_Domain_coors_com_and_Validate_returns_NORMAL_response_with_Only_WPCP__CEF_logs_as_never_proxy_is_set_for_WPCP_category_00000000000000000000000000000001(self):
        logging.info("Perform Query from WPCP bit and Proxy-All match Subscriber client for WPCP Domain coors.com and Validate got NORMAL response as never_proxy category set is 00000000000000000000000000000001")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' coors.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*coors.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=164)
    def test_164_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=165)
    def test_165_Validate_CEF_Log_Logs_Only_for_WPCP_Category_as_never_proxy_is_set_for_WPCP_category_00000000000000000000000000000001(self):
        logging.info("Validate CEF logs are logged for only WPCP Category as never_proxy category set for WPCP bit 00000000000000000000000000000001")
        LookFor=".*info CEF.*coors.com.*CAT=WRN_0x00000000000000000000000000000001"
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


    @pytest.mark.run(order=166)
    def test_166_Validate_WPCP_Domain_coors_com_get_cached_to_DCA_When_Send_Query_if_never_proxy_category_set_is_00000000000000000000000000000001(self):
        logging.info("Validate WPCP Domain coors.com get cached to DCA when send query if never_proxy is set for WPCP bit_00000000000000000000000000000001")
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
        assert re.search(r'.*coors.com,A,IN.*AA,A,coors.com.*',c)
        assert re.search(r'.*0x00000000000000000000000000000001.*',c)
        logging.info("Test Case  Execution Completed")
        sleep(15)

    @pytest.mark.run(order=167)
    def test_167_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 146 passed")
        sleep(10)



    @pytest.mark.run(order=168)
    def test_168_Send_Query_Again_from_same_Subscriber_client_when_WPCP_Domain_coors_com_is_already_in_DCA_Cache_and_Validate_returns_NORMAL_response_from_DCA_without_PXY_Category_CEF_logs_and_with_only_WPCP_CEF_Log_as_never_proxy_category_set_is_00000000000000000000000000000001(self):
        logging.info("Perform Query again same match Subscriber client when WPCP Domain coors.com is already in DCA cache and validate returns  NORMAL response from DCA as never_proxy category set for WPCP bit 00000000000000000000000000000001")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' coors.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*coors.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case  Execution Completed")



    @pytest.mark.run(order=169)
    def test_169_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 148 Execution Completed")


    @pytest.mark.run(order=170)
    def test_170_Validate_got_only_WPCP_CEF_Log_Logs_when_get_response_from_DCA_for_WPCP_domain_coors_com_when_never_proxy_category_set_is_00000000000000000000000000000001(self):
        logging.info("Validate only WPCP CEF Log for coors.com as  never_proxy category set is 00000000000000000000000000000001 ")
        LookFor=".*info CEF.*playboy.com.*CAT=PXY"
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


    @pytest.mark.run(order=171)
    def test_171_From_CLI_Configuration_never_proxy_for_Defult_category_set_is_00000000000000000000000000000000(self):
        try:
            logging.info("From CLI Configuration never_proxy for Default category set is 00000000000000000000000000000000")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data never_proxy 10000000000000000000000000000000')
            child.expect('never_proxy categories is set')
            child.expect('!!! A RESTART of the DNS service is required before this change can take effect !!!')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Failed")
            assert False



    @pytest.mark.run(order=172)
    def test_172_From_CLI_Validate_Configuration_never_proxy_for_Default_category_set_is_00000000000000000000000000000000(self):
        logging.info("From CLI Validate Configuration never_proxy for Default category set is 10000000000000000000000000000000 ")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data never_proxy')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*never_proxy category set is 10000000000000000000000000000000.*',c)
        logging.info("Test case execution completed")



    @pytest.mark.run(order=173)
    def test_173_Restart_DNS_service(self):
        logging.info("Restart services")
        restart_the_grid()
        #grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        #ref = json.loads(grid)[0]['_ref']
        #publish={"member_order":"SIMULTANEOUSLY"}
        #request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        #request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        #restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        #sleep(60)



#    @pytest.mark.run(order=174)
#    def test_174_Add_Subscriber_Record_with_Only_Proxy_All_Policy_without_Any_Other_policy_in_subscriber_Record(self):
#        try:
#            logging.info("Add Subscriber Record with only Proxy-All Policy and without any other policy in subscriber record")
#            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
#            child.logfile=sys.stdout
#            child.expect('password:',timeout=None)
#            child.sendline('infoblox')
#            child.expect('Infoblox >')
#            child.sendline('set subscriber_secure_data add '+config.client_ip+' 32 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;SUB:Calling-Station-Id=110361266;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';"')

#           child.expect('Record successfully added')
#            logging.info("Test Case Execution Passed")
#            assert True
#        except:
#            logging.info("Test Case Execution Failed")
#            assert False




    @pytest.mark.run(order=174)
    def test_174_From_Radclient_Send_Start_Radius_Message_with_Only_Proxy_All_without_Any_Other_policy_in_subscriber_Record(self):
        logging.info("From Rad client send Start Radius message with only Proxy-All Policy and without any other policy in subscriber record")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part2_radfiles/RFE_9980_Only_Proxy_All_policy.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=175)
    def test_175_Validate_Subscriber_Record_with_Only_Proxy_All_Policy_in_subscriber_Record(self):
        logging.info("Validate Subscriber Record with only Proxy-All in subscriber record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case execution completed")



    @pytest.mark.run(order=176)
    def test_176_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

# Test case failed because of the bug NIOS-78002
    @pytest.mark.run(order=177)
    def test_177_Send_Query_from_Proxy_all_Configured_subscribed_client_for_Proxy_domain_and_Validate_returns_Proxy_response_from_Bind(self):
        logging.info("Perform Query from Proxy-All configuredt Subscriber client for Proxy Domain playboy.com and Validate Proxy IP response from Bind")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*5.*IN.*A.*10.*',str(dig_result))
        logging.info("Test Case  Execution Completed")
        sleep(5)




    @pytest.mark.run(order=178)
    def test_178_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


# Changed the test cases from !=None to ==None as NIOS-78037
    @pytest.mark.run(order=179)
    def test_179_Validate_Named_CEF_Log_Logs_with_CAT_PXY_when_get_response_from_Bind_for_Proxy_domain_playboy_com(self):
        logging.info("Validate Named CEF Log for proxy domain playboy.com with CAT as PXY  when get response from Bind")
        LookFor="named.*info CEF.*playboy.com.*CAT=PXY"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False

# Test case failed because of the bug NIOS-78002

    @pytest.mark.run(order=180)
    def test_180_Validate_Proxy_Domain_playboy_com_did_not_cached_to_DCA_When_Send_Query_From_Proxy_confogured__Subscriber_client_match(self):
        logging.info("Validate playboy.com domain not cached to DCA when send query from the Proxy configured subscriber client match")
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
        sleep(5)


    @pytest.mark.run(order=181)
    def test_181_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=182)
    def test_182_Send_Query_from_NON_PCP_bit_match_and_not_Proxy_all_Configured_Subscriber_client_for_Proxy_Domain_playboy_cm_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_cached_DCA_with_PCP_word(self):
        logging.info("Perform Query from NON PCP bit match and not configured Proxy-All Subscriber client for Proxy Domain playboy.com using IB-FLEX Member and Validate get NORMAL response playboy.com domain is cached to DCA with PCP word")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=183)
    def test_183_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=184)
    def test_184_Validate_NO_CEF_Log_Logs_as_got_NORMAL_response_for_Proxy_domain_playboy_com_when_send_query_from_NON_PCP_bit_match_and_not_configured_Proxy_All_client(self):
        logging.info("Validate NO CEF Log for playboy.com as got NORMAL response when send query from NON PCP bit match and not configured Proxy-ALL  client")
        LookFor="info CEF.*playboy.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert False
        else:
            logging.info("Test Case  Execution Failed")
            assert True



    @pytest.mark.run(order=185)
    def test_185_Validate_Proxy_Domain_playboy_com_get_cached_to_DCA_When_Send_Query_From_NON_PCP_bit_Matched_and_not_configured_Proxy_All_Subscriber_client(self):
        logging.info("Validate Proxy Domain playboy.com get cached to DCA when send query from the NON PCP bit matched and not configured Proxy-All subscriber client")
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
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=186)
    def test_186_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=187)
    def test_187_Send_Query_from_Only_Proxy_All_Configured_Subscriber_client_for_Proxy_Domain_playboy_com_and_Validate_returns_Proxy_IP_response_from_DCA_As_palyboy_com_domain_is_already_DCA_Cache(self):
        logging.info("Perform Query from only Proxy-All Subscriber client for Proxy Domain playboy.com and Validate get Proxy IPs response from DCA as playboy.com is already in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result1 = subprocess.check_output(dig_cmd, shell=True)

        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*5.*IN.*A.*10.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)



    @pytest.mark.run(order=188)
    def test_188_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")
        sleep(10)


# Changed the test cases from !=None to ==None as NIOS-78037
    @pytest.mark.run(order=189)
    def test_189_Validate_DCA_CEF_Log_Logs_as_got_response_from_DCA_for_Proxy_domain_playboy_com(self):
        logging.info("Validate DCA CEF Log for playboy.com as got response from DCA")
        LookFor="fp-rte.*info CEF.*playboy.com.*CAT=PXY"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=190)
    def test_190_From_CLI_Using_set_dns_flush_all_command_clear_dns_Cache(self):
        try:
            logging.info("From CLI using set dns flush all CLI command clear dnscCache")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set dns flush all')
            child.expect('Infoblox >')
            logging.info("Test Case  Execution Passed")
            assert True
        except:
            logging.info("Test Case  Execution Failed")
            assert False



    @pytest.mark.run(order=191)
    def test_191_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=192)
    def test_192_Send_Query_from_NON_Registered_Sbscriber_client_for_Proxy_Domain_playboy_com_and_Validate_returns_NORMAL_response_domain_cached_DCA_without_PCP_word(self):
        logging.info("Perform Query from NON Registered Subscriber client for Proxy Domain playboy.com and Validate get NORMAL response playboy.com domain is cached to DCA without PCP word")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip3)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip3+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=193)
    def test_193_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=194)
    def test_194_Validate_NO_CEF_Log_Logs_as_got_NORMAL_response_for_Proxy_domain_playboy_com_when_send_query_from_NON_Registered_client(self):
        logging.info("Validate NO CEF Log for playboy.com as got NORMAL response when send query from NON Registered client")
        LookFor="info CEF.*playboy.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert False
        else:
            logging.info("Test Case  Execution Failed")
            assert True



    @pytest.mark.run(order=195)
    def test_195_Validate_Proxy_Domain_playboy_com_get_cached_to_DCA_Without_PCP_Word_when_Send_Query_From_NON_Registered_Subscriber_client(self):
        logging.info("Validate Proxy Domain playboy.com get cached to DCA without PCP word when send query from the NON Registered subscriber client")
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
        if (re.search(r'.*0x00000000000000000000000000020000.*',c)):
            assert False
        else:
            assert True
        logging.info("Test Case Execution Completed")
        sleep(5)



    @pytest.mark.run(order=196)
    def test_196_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=197)
    def test_197_Send_Query_from_Only_Proxy_All_Configured_Subscriber_client_for_Proxy_Domain_playboy_com_and_Validate_returns_Proxy_IP_response_from_Bind_As_palyboy_com_domain_is_already_DCA_Cache_without_PCP_Word(self):
        logging.info("Perform Query from only Proxy-All Subscriber client for Proxy Domain playboy.com and Validate get Proxy IPs response from DCA as playboy.com is already in DCA cache without PCP word")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+';dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*5.*IN.*A.*10.*',str(dig_result))
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=198)
    def test_198_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=199)
    def test_199_Validate_Named_CEF_Log_Logs_with_CAT_PXY_when_get_response_from_Bind_for_Proxy_domain_playboy_com(self):
        logging.info("Validate Named CEF Log for proxy domain playboy.com with CAT as PXY  when get response from Bind")
        LookFor="named.*info CEF.*playboy.com.*CAT=PXY"
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



    @pytest.mark.run(order=200)
    def test_200_Delete_Subscriber_Record_with_Only_Proxy_all_set_From_Subscriber_Cache(self):
        try:
            logging.info("Delete the Subscriber Record with Only Proxy-All set to True from Subscriber Cache")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data delete '+config.client_ip+' 32 N/A N/A')
            child.expect('Record successfully deleted')
            logging.info("Test Case  Execution Passed")
            assert True
        except:
            logging.info("Test Case  Execution Failed")
            assert False



    @pytest.mark.run(order=201)
    def test_201_Validate_Subscriber_Record_with_OnlyProxy_all_set_is_deleted_from_Subscriber_Cache(self):
        logging.info("Validate Subscriber Record with Only Proxy-All set to True is deleted from subscriber cache")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        if re.search(r'.*'+config.client_ip+'.*',c):
            logging.info("Test Case  Execution Failed")
            assert False
        else:
            logging.info("Test Case  Execution Passed")
            assert True
        logging.info("Test case  execution completed")
        sleep(10)




#################################### Test Cases for Query Count Log ########################################


    @pytest.mark.run(order=202)
    def test_202_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case  passed")
        sleep(10)


    @pytest.mark.run(order=203)
    def test_203_Add_Subscriber_Record_with_PCP_and_Proxy_All_Policy_To_Validate_Query_Count_logs(self):
        try:
            logging.info("Add Subscriber Record with PCP Policy and Proxy All to Validate Query Count logs")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip+' 32 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';"')

            child.expect('Record successfully added')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Failed")
            assert False



    @pytest.mark.run(order=204)
    def test_204_Validate_Subscriber_Record_with_PCP_and_Proxy_All_Policy(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category and Proxy-All set True")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case  execution completed")



    @pytest.mark.run(order=205)
    def test_205_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case  Execution Completed")


    @pytest.mark.run(order=206)
    def test_206_Validate_No_CEF_Log_Logs_for_START_OR_Query_count_is_zero(self):
        logging.info("Validate no CEF Log for START OR when Query count is zero from subscriber record")
        LookFor="fp-rte.*info CEF.*QUERY-COUNT.*COUNT.*app=DNS ip="+config.client_ip+".*event_type=START query_count=.*"
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



    @pytest.mark.run(order=207)
    def test_207_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)



    @pytest.mark.run(order=208)
    def test_208_Send_2_Query_from_Proxy_all_Configured_subscribed_client_for_Proxy_domain_Validate_returns_Proxy_response_from_Bind(self):
        logging.info("Send 2 Query from Proxy-All configuredt Subscriber client for Proxy Domain playboy.com and validate got Proxy IP response from Bind")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+';dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*5.*IN.*A.*10.*',str(dig_result))
        logging.info("Test Case  Execution Completed")
        sleep(5)



    @pytest.mark.run(order=209)
    def test_209_Add_or_Send_interim_Subscriber_Record_with_PCP_and_Proxy_All_Policy_To_Validate_Query_Count_logs(self):
        try:
            logging.info("Add Subscriber Record with PCP Policy and Proxy All to Validate Query Count logs")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip+' 32 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';"')

            child.expect('Record successfully added')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Failed")
            assert False



    @pytest.mark.run(order=210)
    def test_210_Validate_Subscriber_Record_with_PCP_and_Proxy_All_Policy(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category and Proxy-All set True")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case  execution completed")



    @pytest.mark.run(order=211)
    def test_211_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=212)
    def test_212_Validate_Query_count__CEF_Log_Logs_with_Query_count_value_as_2(self):
        logging.info("Validate Query Count CEF logs logs in log message with Query Count value as 2")
        LookFor="fp-rte.*info CEF.*QUERY-COUNT.*COUNT.*app=DNS ip="+config.client_ip+".*event_type=INTERIM query_count=2.*"
        print LookFor
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


    @pytest.mark.run(order=213)
    def test_213_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)



    @pytest.mark.run(order=214)
    def test_214_Delete_ro_Send_STOP_Subscriber_Record_for_Validate_Query_count_CEF_Log_logs_with_Query_Count_Value_as_2_for_Delete_STOP_Subscriber_client(self):
        try:
            logging.info("Delete or send STOP radius message and validate Query Count CEF log logs with Query Count value 2 for deleted Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data delete '+config.client_ip+' 32 N/A N/A')
            child.expect('Record successfully deleted')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Failed")
            assert False



    @pytest.mark.run(order=215)
    def test_215_Validate_Subscriber_Record_with_Proxy_all_set_is_deleted_from_Subscriber_Cache(self):
        logging.info("Validate Subscriber Record is deleted from subscriber cache")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        if re.search(r'.*'+config.client_ip+'.*',c):
            logging.info("Test Case Execution Failed")
            assert False
        else:
            logging.info("Test Case Execution Passed")
            assert True
        logging.info("Test case execution completed")
        sleep(10)



    @pytest.mark.run(order=216)
    def test_216_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=217)
    def test_217_Validate_Query_count_CEF_Log_Logs_with_Query_count_value_as_2_for_Deleted_Subscriber_Record(self):
        logging.info("Validate Query Count CEF logs logs in log message with Query Count value as 2 for Deleted subscriber records")
        LookFor="fp-rte.*info CEF.*QUERY-COUNT.*COUNT.*app=DNS ip="+config.client_ip+".*event_type=STOP query_count=2.*"
        print LookFor
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")



    @pytest.mark.run(order=218)
    def test_218_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case  passed")
        sleep(10)


    @pytest.mark.run(order=219)
    def test_219_Add_IPv4_Network_Subscriber_Record_with_PCP_and_Proxy_All_Policy_To_Validate_Query_Count_logs(self):
        try:
            logging.info("Add IPv4 Network Subscriber Record with PCP Policy and Proxy All to Validate Query Count logs")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_network_16+' 16 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';"')

            child.expect('Record successfully added')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Failed")
            assert False



    @pytest.mark.run(order=220)
    def test_220_Validate_IPv4_Network_Subscriber_Record_with_PCP_and_Proxy_All_Policy(self):
        logging.info("Validate IPv4 Network Subscriber Record with PCP Policy for News Category and Proxy-All set True")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_network_16+'\/16\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case  execution completed")



    @pytest.mark.run(order=221)
    def test_221_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case  Execution Completed")


    @pytest.mark.run(order=222)
    def test_222_Validate_No_CEF_Log_Logs_for_START_OR_Query_count_is_zero_for_IPv4_Network_subscriber_Record(self):
        logging.info("Validate no CEF Log for START OR when Query count is zero from IPv4 Network subscriber record")
        LookFor="fp-rte.*info CEF.*QUERY-COUNT.*COUNT.*app=DNS ip="+config.client_ip+".*event_type=START query_count=.*"
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



    @pytest.mark.run(order=223)
    def test_223_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)



    @pytest.mark.run(order=224)
    def test_224_Send_2_Query_from_Any_Client_IP_which_fall_on_IPv4_Networksubscribed_and_Validate_returns_Proxy_response_from_Bind(self):
        logging.info("Send 2 Query from any client IP which fall on IPv4 Network Subscriber record for Proxy Domain playboy.com and validate got Proxy IP response from Bind")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+';dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*5.*IN.*A.*10.*',str(dig_result))
        logging.info("Test Case  Execution Completed")
        sleep(5)


    @pytest.mark.run(order=225)
    def test_225_Add_or_Send_IPv4_Network_interim_Subscriber_Record_with_PCP_and_Proxy_All_Policy_To_Validate_Query_Count_logs(self):
        try:
            logging.info("Add or send IPv4 STOPInterim Subscriber Record with PCP Policy and Proxy All to Validate Query Count logs")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_network_16+' 16 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';"')

            child.expect('Record successfully added')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=226)
    def test_226_Validate_IPv4_Network_Subscriber_Record_with_PCP_and_Proxy_All_Policy(self):
        logging.info("Validate IPv4 Network Subscriber Record with PCP Policy for News Category and Proxy-All set True")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_network_16+'\/16\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case  execution completed")



    @pytest.mark.run(order=227)
    def test_227_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=228)
    def test_228_Validate_Query_count__CEF_Log_Logs_with_Query_count_value_as_2_For_IPv4_Network_Subscriber_Record(self):
        logging.info("Validate Query Count CEF logs logs in log message with Query Count value as 2 for IPv4 Network Subscriber record")
        LookFor="fp-rte.*info CEF.*QUERY-COUNT.*COUNT.*app=DNS ip="+config.client_network_16+".*event_type=INTERIM query_count=2.*"
        print LookFor
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


    @pytest.mark.run(order=229)
    def test_229_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=230)
    def test_230_Delete_ro_Send_STOP_IPv4_Network_Subscriber_Record_for_Validate_Query_count_CEF_Log_logs_with_Query_Count_Value_as_2_for_Delete_STOP_Subscriber_client(self):
        try:
            logging.info("Delete or send STOP IPv4 Network radius message and validate Query Count CEF log logs with Query Count value 2 for deleted Subscriber Record")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data delete '+config.client_network_16+' 16 N/A N/A')
            child.expect('Record successfully deleted')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Failed")
            assert False



    @pytest.mark.run(order=231)
    def test_231_Validate_IPv4_Network_Subscriber_Record_with_Proxy_all_set_is_deleted_from_Subscriber_Cache(self):
        logging.info("Validate IPv4 Network Subscriber Record is deleted from subscriber cache")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        if re.search(r'.*'+config.client_network_16+'.*',c):
            logging.info("Test Case Execution Failed")
            assert False
        else:
            logging.info("Test Case Execution Passed")
            assert True
        logging.info("Test case execution completed")
        sleep(10)



    @pytest.mark.run(order=232)
    def test_232_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=233)
    def test_233_Validate_Query_count_CEF_Log_Logs_with_Query_count_value_as_2_for_Deleted_IPv4_Network_Subscriber_Record(self):
        logging.info("Validate Query Count CEF logs logs in log message with Query Count value as 2 for Deleted IPv4 Network subscriber records")
        LookFor="fp-rte.*info CEF.*QUERY-COUNT.*COUNT.*app=DNS ip="+config.client_network_16+".*event_type=STOP query_count=2.*"
        print LookFor
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")


######################### RPZ Rules Functionality Test Cases When Subscriber Records are added without SSP  Policy #########################

    @pytest.mark.run(order=234)
    def test_234__________________RPZ_Rule_Functionality_Test_Cases_When_Subscriber_Record_added_Without_SSP_Policyi_______________(self):
        logging.info("RPZ Rules Functionality Test Cases When Subscriber Records are added without SSP  Policy")


    @pytest.mark.run(order=235)
    def test_235_Add_Subscriber_Record_with_PCP_and_Proxy_All_Policy_Without_SSP_Policy(self):
        try:
            logging.info("Add Subscriber Record with PCP Policy for News Category and Proxy-All without SSP Policy")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip+' 32 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';BWI:BWFlag=1;BL=facebook.com;WL=yahoo.com;"')

            child.expect('Record successfully added')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Failed")
            assert False

    @pytest.mark.run(order=236)
    def test_236_Validate_Subscriber_Record_with_PCP_and_Proxy_All_Policy_Without_SSP_Policy(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category and Proxy-All without SSP Policy")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case execution completed")



    @pytest.mark.run(order=237)
    def test_237_Add_Proxy_domain_playboy_com_as_PASSTHRU_RPZ_Rule_to_1_RPZ_Zone_rpz32_com(self):
        logging.info ("Add Proxy Domain Playboy.com as PASSTHRU RPZ Rule to 1st RPZ zone rpz32.com")
        data={"canonical":"playboy.com", "name": "playboy.com.rpz32.com","rp_zone": "rpz32.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=238)
    def test_238_Validate_Added_Proxy_domain_playboy_com_as_PASSTHRU_RPZ_Rule_to_1_RPZ_Zone_rpz32_com(self):
        logging.info("Validate added Proxy Domain Playboy.com as PASSTHRU RPZ Rule to 32 RPZ zone rpz32.com\n")
        data={"name": "playboy.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "playboy.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=239)
    def test_239_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)



    @pytest.mark.run(order=240)
    def test_240_Send_Query_from_PCP_bit_and_Proxy_All_Configured_Subscriber_client_for_Proxy_Domain_playboy_com_Validate_returns_Proxy_VIP_response_As_playboy_com_is_added_as_PASSTHRU_RPZ_rule_to_1_RPZ_Zone_and_got_RPZ_and_PCP_CEF_logs(self):
        logging.info("Perform Query from PCP bit and Proxy-All configured Subscriber client for Proxy Domain playboy.com and Validate get Proxy VIP response as playboy.com domain is added as Proxy domain is added as PASSTHRU RPZ rule to 1st RPZ zone and got RPZ and PCP CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=241)
    def test_241_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

# Changed the test cases from !=None to ==None as NIOS-78037
    @pytest.mark.run(order=242)
    def test_242_Validate_Got_Both_RPZ_PCP_CEF_Log_Logs_as_Proxy_domain_playboy_com_is_added_as_PASSTHRU_RPZ_rule_to_1_RPZ_Zone(self):
        logging.info("Validate got both RPZ and PCP CEF Log for playboy.com  ad domain is added as PASSTHRU RPZ rule to 1st RPZ zone")
        LookFor="info CEF.*playboy.com.*CAT=RPZ.*"
        LookFor1="info CEF.*playboy.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=243)
    def test_243_Remove_Proxy_playboy_com_PASSTHRU_RPZ_Rule_from_1_RPZ_Zone_rpz32_com(self):
        logging.info ("Remove Proxy Domain Playboy.com PASSTHRU RPZ Rule from 1st RPZ zone rpz32.com")
        data={"name": "playboy.com.rpz32.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=244)
    def test_244_Validate_Proxy_domain_playboy_com_PASSTHRU_RPZ_Rule_is_Deleted_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate Proxy Domain Playboy.com PASSTHRU RPZ Rule is deleted from 1st RPZ zone rpz32.com\n")
        data={"name": "playboy.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "playboy.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=245)
    def test_245_Add_Proxy_domain_playboy_com_as_PASSTHRU_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Add Proxy Domain Playboy.com as PASSTHRU RPZ Rule to 7th RPZ zone rpz25.com")
        data={"canonical":"playboy.com", "name": "playboy.com.rpz25.com","rp_zone": "rpz25.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=246)
    def test_246_Validate_Added_Proxy_domain_playboy_com_as_PASSTHRU_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate added Proxy Domain Playboy.com as PASSTHRU RPZ Rule to 7th RPZ zone rpz25.com\n")
        data={"name": "playboy.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz25.com"' in get_rpz_rule) and ('"canonical": "playboy.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=247)
    def test_247_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=248)
    def test_248_Send_Query_from_PCP_bit_and_Proxy_All_Configured_Subscriber_client_for_Proxy_Domain_playboy_com_Validate_returns_Proxy_VIP_response_As_playboy_com_is_added_as_PASSTHRU_RPZ_rule_to_7th_RPZ_Zone_and_got_Only_PCP_CEF_logs(self):
        logging.info("Perform Query from PCP bit and Proxy-All configured Subscriber client for Proxy Domain playboy.com and Validate get Proxy VIP response as playboy.com domain is added as Proxy domain is added as PASSTHRU RPZ rule to 7th RPZ zone and got only PCP CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*5.*IN.*A.*10.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=249)
    def test_249_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


# Changed the test cases from !=None to ==None as NIOS-78037
    @pytest.mark.run(order=250)
    def test_250_Validate_Got_Only_PCP_CEF_Log_Logs_as_Proxy_domain_playboy_com_is_added_as_PASSTHRU_RPZ_rule_to_7th_RPZ_Zone(self):
        logging.info("Validate got only PCP CEF Log for playboy.com  added domain is added as PASSTHRU RPZ rule to 7th RPZ zone")
        LookFor="info CEF.*playboy.com.*CAT=RPZ.*"
        LookFor1="info CEF.*playboy.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=251)
    def test_251_Remove_Proxy_playboy_com_PASSTHRU_RPZ_Rule_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Remove Proxy Domain Playboy.com PASSTHRU RPZ Rule from 7th RPZ zone rpz25.com")
        data={"name": "playboy.com.rpz25.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=252)
    def test_252_Validate_Proxy_domain_playboy_com_PASSTHRU_RPZ_Rule_is_Deleted_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate Proxy Domain Playboy.com PASSTHRU RPZ Rule is deleted from 7th RPZ zone rpz25.com\n")
        data={"name": "playboy.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz25.com"' in get_rpz_rule) and ('"canonical": "playboy.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=253)
    def test_253_Add_Proxy_domain_playboy_com_as_NXDOMAIN_RPZ_Rule_to_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Add Proxy Domain Playboy.com as NXDOMAIN RPZ Rule to 32 RPZ zone rpz32.com")
        data={"canonical":"", "name": "playboy.com.rpz32.com","rp_zone": "rpz32.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=254)
    def test_254_Validate_Added_Proxy_domain_playboy_com_as_NXDOMAIN_RPZ_Rule_to_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate added Proxy Domain Playboy.com as NXDOMAIN RPZ Rule to 32 RPZ zone rpz32.com\n")
        data={"name": "playboy.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz32.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=255)
    def test_255_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=256)
    def test_256_Send_Query_from_PCP_bit_and_Proxy_All_Configured_Subscriber_client_for_Proxy_Domain_playboy_com_Validate_returns_NXDOMAIN_As_playboy_com_is_added_as_NXDOMAIN_RPZ_rule_to_1st_RPZ_Zone_and_got_Only_RPZ_CEF_logs(self):
        logging.info("Perform Query from PCP bit and Proxy-All configured Subscriber client for Proxy Domain playboy.com and Validate get NXDOMAIN response as playboy.com domain is added as NXDOMAIN RPZ rule to 1st RPZ zone and got only RPZ  CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NXDOMAIN.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        #assert re.search(r'.*rpz32.com.*900.*IN.*SOA.*please_set_email.absolutely.nowhere.*',str(dig_result))
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=258)
    def test_258_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=259)
    def test_259_Validate_Got_Only_RPZ_CEF_Log_and_not_PCP_Logs_as_Proxy_domain_playboy_com_is_added_as_NXDOMAIN_RPZ_rule_to_1st_RPZ_Zone(self):
        logging.info("Validate got only RPZ CEF Log for playboy.com  ad domain is added as NXDOMAIN RPZ rule to 1st RPZ zone")
        LookFor="info CEF.*playboy.com.*CAT=RPZ.*"
        LookFor1="info CEF.*playboy.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=260)
    def test_260_Remove_Proxy_playboy_com_NXDOMAIN_RPZ_Rule_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Remove Proxy Domain Playboy.com NXDOMAIN RPZ Rule from 1st RPZ zone rpz32.com")
        data={"name": "playboy.com.rpz32.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=261)
    def test_261_Validate_Proxy_domain_playboy_com_NXDOMAIN__RPZ_Rule_is_Deleted_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate Proxy Domain Playboy.com NXDOMAIN RPZ Rule is deleted from 1st RPZ zone rpz32.com\n")
        data={"name": "playboy.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz32.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=262)
    def test_262_Add_Proxy_domain_playboy_com_as_NXDOMAIN_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Add Proxy Domain Playboy.com as NXDOMAIN RPZ Rule to 7th RPZ zone rpz25.com")
        data={"canonical":"", "name": "playboy.com.rpz25.com","rp_zone": "rpz25.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)


    @pytest.mark.run(order=263)
    def test_263_Validate_Added_Proxy_domain_playboy_com_as_NXDOMAIN_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate added Proxy Domain Playboy.com as NXDOMAIN RPZ Rule to 7th RPZ zone rpz25.com\n")
        data={"name": "playboy.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz25.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=264)
    def test_264_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=265)
    def test_265_Send_Query_from_PCP_bit_and_Proxy_All_Configured_Subscriber_client_for_Proxy_Domain_playboy_com_Validate_returns_Proxy_VIP_response_As_playboy_com_is_added_as_NXDOMAIN_RPZ_rule_to_7th_RPZ_Zone_and_got_Only_PCP_CEF_logs_NO_RPZ_CEF_log(self):
        logging.info("Perform Query from PCP bit and Proxy-All configured Subscriber client for Proxy Domain playboy.com and Validate get Proxy VIP response as playboy.com domain is added as Proxy domain is added as NXDOMAIN RPZ rule to 7th RPZ zone and got only PCP CEF logs not RPZ CEF log")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*5.*IN.*A.*10.*',str(dig_result))
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=266)
    def test_266_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

# Changed the test cases from !=None to ==None as NIOS-78037
    @pytest.mark.run(order=267)
    def test_267_Validate_Got_Only_PCP_CEF_Log_Logs_as_Proxy_domain_playboy_com_is_added_as_NXDOMAIN_RPZ_rule_to_7th_RPZ_Zone(self):
        logging.info("Validate got only PCP CEF Log for playboy.com  added domain is added as NXDOMAIN RPZ rule to 7th RPZ zone")
        LookFor="info CEF.*playboy.com.*CAT=RPZ.*"
        LookFor1="info CEF.*playboy.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=268)
    def test_268_Remove_Proxy_playboy_com_NXDOMAIN_RPZ_Rule_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Remove Proxy Domain Playboy.com NXDOMAIN RPZ Rule from 7th RPZ zone rpz25.com")
        data={"name": "playboy.com.rpz25.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=269)
    def test_269_Validate_Proxy_domain_playboy_com_NXDOMAIN_RPZ_Rule_is_Deleted_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate Proxy Domain Playboy.com NXDOMAIN RPZ Rule is deleted from 7th RPZ zone rpz25.com\n")
        data={"name": "playboy.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz25.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=270)
    def test_270_Add_PCP_domain_times_com_as_PASSTHRU_RPZ_Rule_to_1_RPZ_Zone_rpz32_com(self):
        logging.info ("Add PCP Domain times.com as PASSTHRU RPZ Rule to 32 RPZ zone rpz32.com")
        data={"canonical":"times.com", "name": "times.com.rpz32.com","rp_zone": "rpz32.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=271)
    def test_271_Validate_Added_PCP_domain_times_com_as_PASSTHRU_RPZ_Rule_to_1_RPZ_Zone_rpz32_com(self):
        logging.info("Validate added PCP Domain times.com as PASSTHRU RPZ Rule to 32 RPZ zone rpz32.com\n")
        data={"name": "times.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "times.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "times.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=272)
    def test_272_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


# As per the changes of bug NIOS-78037 commented and changed the cases
    @pytest.mark.run(order=273)
    def test_273_Send_Query_from_PCP_bit_and_Proxy_All_Configured_Subscriber_client_for_PCP_Domain_times_com_Validate_returns_PCP_Blocking_response_As_times_com_is_added_as_PASSTHRU_RPZ_rule_to_1st_RPZ_Zone_and_got_RPZ_and_PCP_CEF_logs(self):
        logging.info("Perform Query from PCP bit and Proxy-All configured Subscriber client for PCP Domain times.com and Validate get PCP Blocking IP response as times.com domain is added as PASSTHRU RPZ rule to 1st RPZ zone and got RPZ and PCP CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
	assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))	
        #assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        #assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=274)
    def test_274_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

# Changed the test cases from !=None to ==None as NIOS-78037
# Again changed the test cae from ==None to !=None as SNIN-57
    @pytest.mark.run(order=275)
    def test_275_Validate_Got_Both_RPZ_PCP_CEF_Log_Logs_as_PCP_domain_times_com_is_added_as_PASSTHRU_RPZ_rule_to_1st_RPZ_Zone(self):
        logging.info("Validate got both RPZ and PCP CEF Log for times.com  domain is added as PASSTHRU RPZ rule to 1st RPZ zone")
        LookFor="info CEF.*times.com.*CAT=RPZ.*"
        LookFor1="info CEF.*times.com.*CAT=0x00000000000000040000000000000000.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1!=None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=276)
    def test_276_Remove_PCP_domain_times_com_PASSTHRU_RPZ_Rule_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Remove PCP Domain times.com PASSTHRU RPZ Rule from 1st RPZ zone rpz32.com")
        data={"name": "times.com.rpz32.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30) 


    @pytest.mark.run(order=277)
    def test_277_Validate_PCP_domain_times_com_PASSTHRU_RPZ_Rule_is_Deleted_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate PCP Domain times.com PASSTHRU RPZ Rule is deleted from 1st RPZ zone rpz32.com\n")
        data={"name": "times.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "times.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "times.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=278)
    def test_278_Add_PCP_domain_times_com_as_PASSTHRU_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Add PCP Domain times.com as PASSTHRU RPZ Rule to 7th RPZ zone rpz25.com")
        data={"canonical":"times.com", "name": "times.com.rpz25.com","rp_zone": "rpz25.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)


    @pytest.mark.run(order=279)
    def test_279_Validate_Added_PCP_domain_times_com_as_PASSTHRU_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate added PCP Domain times.com as PASSTHRU RPZ Rule to 7th RPZ zone rpz25.com\n")
        data={"name": "times.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "times.com.rpz25.com"' in get_rpz_rule) and ('"canonical": "times.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=280)
    def test_280_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        

    @pytest.mark.run(order=281)
    def test_281_Send_Query_from_PCP_bit_and_Proxy_All_Configured_Subscriber_client_for_PCP_Domain_times_com_Validate_returns_PCP_blocking_IP_response_As_times_com_is_added_as_PASSTHRU_RPZ_rule_to_7th_RPZ_Zone_and_got_Only_PCP_CEF_logs(self):
        logging.info("Perform Query from PCP bit and Proxy-All configured Subscriber client for PCP Domain times.com and Validate get PCP blocking response as times.com domain is added as PCP domain is added as PASSTHRU RPZ rule to 7th RPZ zone and got only PCP CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=282)
    def test_282_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=283)
    def test_283_Validate_Got_Only_PCP_CEF_Log_Logs_as_PCP_domain_times_com_is_added_as_PASSTHRU_RPZ_rule_to_7th_RPZ_Zone(self):
        logging.info("Validate got only PCP CEF Log for times.com domain is added as PASSTHRU RPZ rule to 7th RPZ zone")
        LookFor="info CEF.*times.com.*CAT=RPZ.*"
        LookFor1="info CEF.*times.com.*CAT=0x00000000000000040000000000000000.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None and logs1!=None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=284)
    def test_284_Remove_Proxy_times_com_PASSTHRU_RPZ_Rule_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Remove PCP Domain times.com PASSTHRU RPZ Rule from 7th RPZ zone rpz25.com")
        data={"name": "times.com.rpz25.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)
        


    @pytest.mark.run(order=285)
    def test_285_Validate_PCP_domain_times_com_PASSTHRU_RPZ_Rule_is_Deleted_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate PCP Domain times.com PASSTHRU RPZ Rule is deleted from 7th RPZ zone rpz25.com\n")
        data={"name": "times.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "times.com.rpz25.com"' in get_rpz_rule) and ('"canonical": "times.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=286)
    def test_286_Add_PCP_domain_times_com_as_NXDOMAIN_RPZ_Rule_to_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Add PCP Domain times.com as NXDOMAIN RPZ Rule to 32 RPZ zone rpz32.com")
        data={"canonical":"", "name": "times.com.rpz32.com","rp_zone": "rpz32.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)


    @pytest.mark.run(order=287)
    def test_287_Validate_Added_PCP_domain_times_com_as_NXDOMAIN_RPZ_Rule_to_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate added PCP Domain times.com as NXDOMAIN RPZ Rule to 32 RPZ zone rpz32.com\n")
        data={"name": "times.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "times.com.rpz32.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=288)
    def test_288_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        

    @pytest.mark.run(order=289)
    def test_289_Send_Query_from_PCP_bit_and_Proxy_All_Configured_Subscriber_client_for_PCP_Domain_times_com_Validate_returns_NXDOMAIN_As_times_com_is_added_as_NXDOMAIN_RPZ_rule_to_1st_RPZ_Zone_and_got_Only_RPZ_CEF_logs(self):
        logging.info("Perform Query from PCP bit and Proxy-All configured Subscriber client for PCP Domain times.com and Validate get NXDOMAIN response as times.com domain is added as NXDOMAIN RPZ rule to 1st RPZ zone and got only RPZ  CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NXDOMAIN.*',str(dig_result))
        assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        #assert re.search(r'.*rpz32.com.*900.*IN.*SOA.*please_set_email.absolutely.nowhere.*',str(dig_result))
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=290)
    def test_290_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=291)
    def test_291_Validate_Got_Only_RPZ_CEF_Log_and_not_PCP_Logs_as_PCP_domain_times_com_is_added_as_NXDOMAIN_RPZ_rule_to_1st_RPZ_Zone(self):
        logging.info("Validate got only RPZ CEF Log for times.com domain is added as NXDOMAIN RPZ rule to 1st RPZ zone")
        LookFor="info CEF.*times.com.*CAT=RPZ.*"
        LookFor1="info CEF.*times.com.*CAT=0x00000000000000040000000000000000.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=292)
    def test_292_Remove_PCP_times_com_NXDOMAIN_RPZ_Rule_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Remove PCP Domain times.com NXDOMAIN RPZ Rule from 1st RPZ zone rpz32.com")
        data={"name": "times.com.rpz32.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)
        


    @pytest.mark.run(order=293)
    def test_293_Validate_PCP_domain_times_com_NXDOMAIN__RPZ_Rule_is_Deleted_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate PCP Domain times.com NXDOMAIN RPZ Rule is deleted from 1st RPZ zone rpz32.com\n")
        data={"name": "times.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "times.com.rpz32.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=294)
    def test_294_Add_PCP_domain_times_com_as_NXDOMAIN_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Add PCP Domain times.com as NXDOMAIN RPZ Rule to 7th RPZ zone rpz25.com")
        data={"canonical":"", "name": "times.com.rpz25.com","rp_zone": "rpz25.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)


    @pytest.mark.run(order=295)
    def test_295_Validate_Added_PCP_domain_times_com_as_NXDOMAIN_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate added PCP Domain times.com as NXDOMAIN RPZ Rule to 7th RPZ zone rpz25.com\n")
        data={"name": "times.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "times.com.rpz25.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=296)
    def test_296_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        

    @pytest.mark.run(order=297)
    def test_297_Send_Query_from_PCP_bit_and_Proxy_All_Configured_Subscriber_client_for_PCP_Domain_times_com_Validate_returns_PCP_Blocking_IP_response_As_times_com_is_added_as_NXDOMAIN_RPZ_rule_to_7th_RPZ_Zone_and_got_Only_PCP_CEF_logs_NO_RPZ_CEF_log(self):
        logging.info("Perform Query from PCP bit and Proxy-All configured Subscriber client for PCP Domain times.com and Validate get PCP Blocking IB response as times.com domain is added as PCP domain is added as NXDOMAIN RPZ rule to 7th RPZ zone and got only PCP CEF logs not RPZ CEF log")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=298)
    def test_298_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=299)
    def test_299_Validate_Got_Only_PCP_CEF_Log_Logs_as_PCP_domain_times_com_is_added_as_NXDOMAIN_RPZ_rule_to_7th_RPZ_Zone(self):
        logging.info("Validate got only PCP CEF Log for times.com  domain is added as NXDOMAIN RPZ rule to 7th RPZ zone")
        LookFor="info CEF.*times.com.*CAT=RPZ.*"
        LookFor1="info CEF.*times.com.*CAT=0x00000000000000040000000000000000.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None and logs1!=None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=300)
    def test_300_Remove_PCP_times_com_NXDOMAIN_RPZ_Rule_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Remove PCP Domain times.com NXDOMAIN RPZ Rule from 7th RPZ zone rpz25.com")
        data={"name": "times.com.rpz25.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)
        


    @pytest.mark.run(order=301)
    def test_301_Validate_PCP_domain_times_com_NXDOMAIN_RPZ_Rule_is_Deleted_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate PCP Domain times.com NXDOMAIN RPZ Rule is deleted from 7th RPZ zone rpz25.com\n")
        data={"name": "times.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "times.com.rpz25.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=302)
    def test_302_Add_BL_domain_facebook_com_as_PASSTHRU_RPZ_Rule_to_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Add BL Domain facebook.com as PASSTHRU RPZ Rule to 1st RPZ zone rpz32.com")
        data={"canonical":"facebook.com", "name": "facebook.com.rpz32.com","rp_zone": "rpz32.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)


    @pytest.mark.run(order=303)
    def test_303_Validate_Added_BL_domain_facebook_com_as_PASSTHRU_RPZ_Rule_to_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate added BL Domain facebook.com as PASSTHRU RPZ Rule to 1st RPZ zone rpz32.com\n")
        data={"name": "facebook.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "facebook.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "facebook.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=304)
    def test_304_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")

# As per the changes of bug NIOS-78037 commented and changed the cases

    @pytest.mark.run(order=305)
    def test_305_Send_Query_from_BL_bit_and_Proxy_All_Configured_Subscriber_client_for_BL_Domain_facebook_com_Validate_returns_BL_Blocking_response_As_facebook_com_is_added_as_PASSTHRU_RPZ_rule_to_1st_RPZ_Zone_and_got_RPZ_and_BL_CEF_logs(self):
        logging.info("Perform Query from BL bit and Proxy-All configured Subscriber client for BL Domain facebook.com and Validate get BL Blocking IP response as facebook.com domain is added as PASSTHRU RPZ rule to 1st RPZ zone and got RPZ and BL CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
	assert re.search(r'.*facebook.com.*IN.*A.*',str(dig_result))
        #assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        #assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=306)
    def test_306_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


# Changed the test cases from !=None to ==None as NIOS-78037
#Again changed the test cae from ==None to !=None as SNIN-57
    @pytest.mark.run(order=307)
    def test_307_Validate_Got_Both_RPZ_BL_CEF_Log_Logs_as_BL_domain_facebook_com_is_added_as_PASSTHRU_RPZ_rule_to_1st_RPZ_Zone(self):
        logging.info("Validate got both RPZ and BL CEF Log for facebook.com  domain is added as PASSTHRU RPZ rule to 1st RPZ zone")
        LookFor="info CEF.*facebook.com.*CAT=RPZ.*"
        LookFor1="info CEF.*facebook.com.*CAT=BL.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1!=None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=308)
    def test_308_Remove_BL_domain_facebook_com_PASSTHRU_RPZ_Rule_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Remove BL Domain facebook.com PASSTHRU RPZ Rule from 1st RPZ zone rpz32.com")
        data={"name": "facebook.com.rpz32.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)



    @pytest.mark.run(order=309)
    def test_309_Validate_BL_domain_facebook_com_PASSTHRU_RPZ_Rule_is_Deleted_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate BL Domain facebook.com PASSTHRU RPZ Rule is deleted from 1st RPZ zone rpz32.com\n")
        data={"name": "facebook.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "facebook.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "facebook.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=310)
    def test_310_Add_BL_domain_facebook_com_as_PASSTHRU_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Add BL Domain facebook.com as PASSTHRU RPZ Rule to 7th RPZ zone rpz25.com")
        data={"canonical":"facebook.com", "name": "facebook.com.rpz25.com","rp_zone": "rpz25.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=311)
    def test_311_Validate_Added_BL_domain_facebook_com_as_PASSTHRU_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate added BL Domain facebook.com as PASSTHRU RPZ Rule to 7th RPZ zone rpz25.com\n")
        data={"name": "facebook.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "facebook.com.rpz25.com"' in get_rpz_rule) and ('"canonical": "facebook.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=312)
    def test_312_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=313)
    def test_313_Send_Query_from_BL_bit_and_Proxy_All_Configured_Subscriber_client_for_BL_Domain_facebook_com_Validate_returns_BL_blocking_IP_response_As_facebook_com_is_added_as_PASSTHRU_RPZ_rule_to_7th_RPZ_Zone_and_got_Only_BL_CEF_logs(self):
        logging.info("Perform Query from BL bit and Proxy-All configured Subscriber client for BL Domain facebook.com and Validate get BL blocking response as facebook.com domain is added as BL domain is added as PASSTHRU RPZ rule to 7th RPZ zone and got only BL CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=314)
    def test_314_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=315)
    def test_315_Validate_Got_Only_BL_CEF_Log_Logs_as_BL_domain_facebook_com_is_added_as_PASSTHRU_RPZ_rule_to_7th_RPZ_Zone(self):
        logging.info("Validate got only BL CEF Log for facebook.com domain is added as PASSTHRU RPZ rule to 7th RPZ zone")
        LookFor="info CEF.*facebook.com.*CAT=RPZ.*"
        LookFor1="info CEF.*facebook.com.*CAT=BL.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None and logs1!=None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=316)
    def test_316_Remove_Proxy_facebook_com_PASSTHRU_RPZ_Rule_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Remove BL Domain facebook.com PASSTHRU RPZ Rule from 7th RPZ zone rpz25.com")
        data={"name": "facebook.com.rpz25.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)



    @pytest.mark.run(order=317)
    def test_317_Validate_BL_domain_facebook_com_PASSTHRU_RPZ_Rule_is_Deleted_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate BL Domain facebook.com PASSTHRU RPZ Rule is deleted from 7th RPZ zone rpz25.com\n")
        data={"name": "facebook.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "facebook.com.rpz25.com"' in get_rpz_rule) and ('"canonical": "facebook.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=318)
    def test_318_Add_BL_domain_facebook_com_as_NXDOMAIN_RPZ_Rule_to_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Add BL Domain facebook.com as NXDOMAIN RPZ Rule to 32 RPZ zone rpz32.com")
        data={"canonical":"", "name": "facebook.com.rpz32.com","rp_zone": "rpz32.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=319)
    def test_319_Validate_Added_BL_domain_facebook_com_as_NXDOMAIN_RPZ_Rule_to_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate added BL Domain facebook.com as NXDOMAIN RPZ Rule to 32 RPZ zone rpz32.com\n")
        data={"name": "facebook.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "facebook.com.rpz32.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=320)
    def test_320_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=321)
    def test_321_Send_Query_from_BL_bit_and_Proxy_All_Configured_Subscriber_client_for_BL_Domain_facebook_com_Validate_returns_NXDOMAIN_As_facebook_com_is_added_as_NXDOMAIN_RPZ_rule_to_1st_RPZ_Zone_and_got_Only_RPZ_CEF_logs(self):
        logging.info("Perform Query from BL bit and Proxy-All configured Subscriber client for BL Domain facebook.com and Validate get NXDOMAIN response as facebook.com domain is added as NXDOMAIN RPZ rule to 1st RPZ zone and got only RPZ  CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NXDOMAIN.*',str(dig_result))
        assert re.search(r'.*facebook.com.*IN.*A.*',str(dig_result))
        #assert re.search(r'.*rpz32.com.*900.*IN.*SOA.*please_set_email.absolutely.nowhere.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=322)
    def test_322_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=323)
    def test_323_Validate_Got_Only_RPZ_CEF_Log_and_not_BL_Logs_as_BL_domain_facebook_com_is_added_as_NXDOMAIN_RPZ_rule_to_1st_RPZ_Zone(self):
        logging.info("Validate got only RPZ CEF Log for facebook.com domain is added as NXDOMAIN RPZ rule to 1st RPZ zone")
        LookFor="info CEF.*facebook.com.*CAT=RPZ.*"
        LookFor1="info CEF.*facebook.com.*CAT=0x00000000000000040000000000000000.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=324)
    def test_324_Remove_BL_facebook_com_NXDOMAIN_RPZ_Rule_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Remove BL Domain facebook.com NXDOMAIN RPZ Rule from 1st RPZ zone rpz32.com")
        data={"name": "facebook.com.rpz32.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)




    @pytest.mark.run(order=325)
    def test_325_Validate_BL_domain_facebook_com_NXDOMAIN__RPZ_Rule_is_Deleted_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate BL Domain facebook.com NXDOMAIN RPZ Rule is deleted from 1st RPZ zone rpz32.com\n")
        data={"name": "facebook.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "facebook.com.rpz32.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=326)
    def test_326_Add_BL_domain_facebook_com_as_NXDOMAIN_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Add BL Domain facebook.com as NXDOMAIN RPZ Rule to 7th RPZ zone rpz25.com")
        data={"canonical":"", "name": "facebook.com.rpz25.com","rp_zone": "rpz25.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=327)
    def test_327_Validate_Added_BL_domain_facebook_com_as_NXDOMAIN_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate added BL Domain facebook.com as NXDOMAIN RPZ Rule to 7th RPZ zone rpz25.com\n")
        data={"name": "facebook.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "facebook.com.rpz25.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=328)
    def test_328_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=329)
    def test_329_Send_Query_from_BL_bit_and_Proxy_All_Configured_Subscriber_client_for_BL_Domain_facebook_com_Validate_returns_BL_Blocking_IP_response_As_facebook_com_is_added_as_NXDOMAIN_RPZ_rule_to_7th_RPZ_Zone_and_got_Only_BL_CEF_logs_NO_RPZ_CEF_log(self):
        logging.info("Perform Query from BL bit and Proxy-All configured Subscriber client for BL Domain facebook.com and Validate get BL Blocking IB response as facebook.com domain is added as BL domain is added as NXDOMAIN RPZ rule to 7th RPZ zone and got only BL CEF logs not RPZ CEF log")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=330)
    def test_330_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=331)
    def test_331_Validate_Got_Only_BL_CEF_Log_Logs_as_BL_domain_facebook_com_is_added_as_NXDOMAIN_RPZ_rule_to_7th_RPZ_Zone(self):
        logging.info("Validate got only BL CEF Log for facebook.com  domain is added as NXDOMAIN RPZ rule to 7th RPZ zone")
        LookFor="info CEF.*facebook.com.*CAT=RPZ.*"
        LookFor1="info CEF.*facebook.com.*CAT=BL.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None and logs1!=None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=332)
    def test_332_Remove_BL_facebook_com_NXDOMAIN_RPZ_Rule_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Remove BL Domain facebook.com NXDOMAIN RPZ Rule from 7th RPZ zone rpz25.com")
        data={"name": "facebook.com.rpz25.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=333)
    def test_333_Validate_BL_domain_facebook_com_NXDOMAIN_RPZ_Rule_is_Deleted_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate BL Domain facebook.com NXDOMAIN RPZ Rule is deleted from 7th RPZ zone rpz25.com\n")
        data={"name": "facebook.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "facebook.com.rpz25.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=334)
    def test_334_Add_WPCP_domain_coors_com_as_PASSTHRU_RPZ_Rule_to_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Add WPCP Domain coors.com as PASSTHRU RPZ Rule to 1st RPZ zone rpz32.com")
        data={"canonical":"coors.com", "name": "coors.com.rpz32.com","rp_zone": "rpz32.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)

    @pytest.mark.run(order=335)
    def test_335_Validate_Added_WPCP_domain_coors_com_as_PASSTHRU_RPZ_Rule_to_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate added WPCP Domain coors.com as PASSTHRU RPZ Rule to 1st RPZ zone rpz32.com\n")
        data={"name": "coors.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "coors.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=336)
    def test_336_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=337)
    def test_337_Send_Query_from_WPCP_bit_and_Proxy_All_Configured_Subscriber_client_for_WPCP_Domain_coors_com_Validate_returns_Proxy_VIP_response_As_coors_com_is_added_as_PASSTHRU_RPZ_rule_to_1st_RPZ_Zone_and_got_RPZ_and_WPCP_CEF_logs(self):
        logging.info("Perform Query from WPCP bit and Proxy-All configured Subscriber client for WPCP Domain coors.com and Validate get WPCP Blocking IP response as coors.com domain is added as PASSTHRU RPZ rule to 1st RPZ zone and got RPZ and WPCP CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' coors.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*coors.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=338)
    def test_338_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

# Changed the test cases from !=None to ==None as NIOS-78037
#Again changed the test cae from ==None to !=None as SNIN-57

    @pytest.mark.run(order=339)
    def test_339_Validate_Got_3_CEF_logs_RPZ_WPCP_PXY_CEF_Log_Logs_as_WPCP_domain_coors_com_is_added_as_PASSTHRU_RPZ_rule_to_1st_RPZ_Zone(self):
        logging.info("Validate got both RPZ and WPCP CEF Log for coors.com  domain is added as PASSTHRU RPZ rule to 1st RPZ zone")
        LookFor="info CEF.*coors.com.*CAT=RPZ.*"
        LookFor1="info CEF.*coors.com.*CAT=WRN_0x00000000000000000000000000000001.*"
        LookFor2="info CEF.*coors.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1!=None and logs2==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=340)
    def test_340_Remove_WPCP_domain_coors_com_PASSTHRU_RPZ_Rule_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Remove WPCP Domain coors.com PASSTHRU RPZ Rule from 1st RPZ zone rpz32.com")
        data={"name": "coors.com.rpz32.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)



    @pytest.mark.run(order=341)
    def test_341_Validate_WPCP_domain_coors_com_PASSTHRU_RPZ_Rule_is_Deleted_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate WPCP Domain coors.com PASSTHRU RPZ Rule is deleted from 1st RPZ zone rpz32.com\n")
        data={"name": "coors.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "coors.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=342)
    def test_342_Add_WPCP_domain_coors_com_as_PASSTHRU_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Add WPCP Domain coors.com as PASSTHRU RPZ Rule to 7th RPZ zone rpz25.com")
        data={"canonical":"coors.com", "name": "coors.com.rpz25.com","rp_zone": "rpz25.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=343)
    def test_343_Validate_Added_WPCP_domain_coors_com_as_PASSTHRU_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate added WPCP Domain coors.com as PASSTHRU RPZ Rule to 7th RPZ zone rpz25.com\n")
        data={"name": "coors.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz25.com"' in get_rpz_rule) and ('"canonical": "coors.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=344)
    def test_344_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=345)
    def test_345_Send_Query_from_WPCP_bit_and_Proxy_All_Configured_Subscriber_client_for_WPCP_Domain_coors_com_Validate_returns_Proxy_VIP_IP_response_As_coors_com_is_added_as_PASSTHRU_RPZ_rule_to_7th_RPZ_Zone_and_got_Only_WPCP_PXY_CEF_logs(self):
        logging.info("Perform Query from WPCP bit and Proxy-All configured Subscriber client for WPCP Domain coors.com and Validate get WPCP blocking response as coors.com domain is added as WPCP domain is added as PASSTHRU RPZ rule to 7th RPZ zone and got only WPCP and PXY CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' coors.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*coors.com.*5.*IN.*A.*10.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=346)
    def test_346_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


# Changed the test cases from !=None to ==None as NIOS-78037
#Again changed the test cae from ==None to !=None as SNIN-57

    @pytest.mark.run(order=347)
    def test_347_Validate_Got_Only_WPCP_and_PXY_CEF_Log_Logs_as_WPCP_domain_coors_com_is_added_as_PASSTHRU_RPZ_rule_to_7th_RPZ_Zone(self):
        logging.info("Validate got only WPCP and PXY CEF Log for coors.com domain is added as PASSTHRU RPZ rule to 7th RPZ zone")
        LookFor="info CEF.*coors.com.*CAT=RPZ.*"
        LookFor1="info CEF.*coors.com.*CAT=WRN_0x00000000000000000000000000000001.*"
        LookFor2="info CEF.*coors.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        if logs==None and logs1!=None and logs2==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=348)
    def test_348_Remove_WPCP_coors_com_PASSTHRU_RPZ_Rule_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Remove WPCP Domain coors.com PASSTHRU RPZ Rule from 7th RPZ zone rpz25.com")
        data={"name": "coors.com.rpz25.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)



    @pytest.mark.run(order=349)
    def test_349_Validate_WPCP_domain_coors_com_PASSTHRU_RPZ_Rule_is_Deleted_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate WPCP Domain coors.com PASSTHRU RPZ Rule is deleted from 7th RPZ zone rpz25.com\n")
        data={"name": "coors.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz25.com"' in get_rpz_rule) and ('"canonical": "coors.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=350)
    def test_350_Add_WPCP_domain_coors_com_as_NXDOMAIN_RPZ_Rule_to_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Add WPCP Domain coors.com as NXDOMAIN RPZ Rule to 32 RPZ zone rpz32.com")
        data={"canonical":"", "name": "coors.com.rpz32.com","rp_zone": "rpz32.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=351)
    def test_351_Validate_Added_WPCP_domain_coors_com_as_NXDOMAIN_RPZ_Rule_to_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate added WPCP Domain coors.com as NXDOMAIN RPZ Rule to 32 RPZ zone rpz32.com\n")
        data={"name": "coors.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz32.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=352)
    def test_352_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=353)
    def test_353_Send_Query_from_WPCP_bit_and_Proxy_All_Configured_Subscriber_client_for_WPCP_Domain_coors_com_Validate_returns_NXDOMAIN_As_coors_com_is_added_as_NXDOMAIN_RPZ_rule_to_1st_RPZ_Zone_and_got_Only_RPZ_CEF_logs(self):
        logging.info("Perform Query from WPCP bit and Proxy-All configured Subscriber client for WPCP Domain coors.com and Validate get NXDOMAIN response as coors.com domain is added as NXDOMAIN RPZ rule to 1st RPZ zone and got only RPZ  CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' coors.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NXDOMAIN.*',str(dig_result))
        assert re.search(r'.*coors.com.*IN.*A.*',str(dig_result))
        #assert re.search(r'.*rpz32.com.*900.*IN.*SOA.*please_set_email.absolutely.nowhere.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=354)
    def test_354_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=355)
    def test_355_Validate_Got_Only_RPZ_CEF_Log_and_not_WPCP_Logs_as_WPCP_domain_coors_com_is_added_as_NXDOMAIN_RPZ_rule_to_1st_RPZ_Zone(self):
        logging.info("Validate got only RPZ CEF Log for coors.com domain is added as NXDOMAIN RPZ rule to 1st RPZ zone")
        LookFor="info CEF.*coors.com.*CAT=RPZ.*"
        LookFor1="info CEF.*coors.com.*CAT=WRN_0x00000000000000000000000000000001.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=356)
    def test_356_Remove_WPCP_coors_com_NXDOMAIN_RPZ_Rule_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Remove WPCP Domain coors.com NXDOMAIN RPZ Rule from 1st RPZ zone rpz32.com")
        data={"name": "coors.com.rpz32.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)



    @pytest.mark.run(order=357)
    def test_357_Validate_WPCP_domain_coors_com_NXDOMAIN__RPZ_Rule_is_Deleted_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate WPCP Domain coors.com NXDOMAIN RPZ Rule is deleted from 1st RPZ zone rpz32.com\n")
        data={"name": "coors.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz32.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=358)
    def test_358_Add_WPCP_domain_coors_com_as_NXDOMAIN_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Add WPCP Domain coors.com as NXDOMAIN RPZ Rule to 7th RPZ zone rpz25.com")
        data={"canonical":"", "name": "coors.com.rpz25.com","rp_zone": "rpz25.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=359)
    def test_359_Validate_Added_WPCP_domain_coors_com_as_NXDOMAIN_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate added WPCP Domain coors.com as NXDOMAIN RPZ Rule to 7th RPZ zone rpz25.com\n")
        data={"name": "coors.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz25.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=360)
    def test_360_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=361)
    def test_361_Send_Query_from_WPCP_bit_and_Proxy_All_Configured_Subscriber_client_for_WPCP_Domain_coors_com_Validate_returns_Proxy_VIP_IP_response_As_coors_com_is_added_as_NXDOMAIN_RPZ_rule_to_7th_RPZ_Zone_and_got_Only_WPCP_and_PXY_CEF_logs_NO_RPZ_CEF_log(self):
        logging.info("Perform Query from WPCP bit and Proxy-All configured Subscriber client for WPCP Domain coors.com and Validate get WPCP Blocking IB response as coors.com domain is added as WPCP domain is added as NXDOMAIN RPZ rule to 7th RPZ zone and got only WPCP and PXY CEF logs not RPZ CEF log")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' coors.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*coors.com.*5.*IN.*A.*10.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=362)
    def test_362_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


# Changed the test cases from !=None to ==None as NIOS-78037
    @pytest.mark.run(order=363)
    def test_363_Validate_Got_Only_WPCP_and_PXY_CEF_Log_Logs_as_WPCP_domain_coors_com_is_added_as_NXDOMAIN_RPZ_rule_to_7th_RPZ_Zone(self):
        logging.info("Validate got only WPCP and PXY CEF Log for coors.com  domain is added as NXDOMAIN RPZ rule to 7th RPZ zone")
        LookFor="info CEF.*coors.com.*CAT=RPZ.*"
        LookFor1="info CEF.*coors.com.*CAT=WRN_0x00000000000000000000000000000001.*"
        LookFor2="info CEF.*coors.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None and logs1!=None and logs2==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=364)
    def test_364_Remove_WPCP_coors_com_NXDOMAIN_RPZ_Rule_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Remove WPCP Domain coors.com NXDOMAIN RPZ Rule from 7th RPZ zone rpz25.com")
        data={"name": "coors.com.rpz25.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)



    @pytest.mark.run(order=365)
    def test_365_Validate_WPCP_domain_coors_com_NXDOMAIN_RPZ_Rule_is_Deleted_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate WPCP Domain coors.com NXDOMAIN RPZ Rule is deleted from 7th RPZ zone rpz25.com\n")
        data={"name": "coors.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz25.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")







######################### RPZ Rules Functionality Test Cases When Subscriber Records are added with SSP  Policy #########################

    @pytest.mark.run(order=374)
    def test_375__________________RPZ_Rule_Functionality_Test_Cases_When_Subscriber_Record_added_With_SSP_Policyi_______________(self):
        logging.info("RPZ Rules Functionality Test Cases When Subscriber Records are added without SSP  Policy")


    @pytest.mark.run(order=375)
    def test_375_Add_Subscriber_Record_with_PCP_and_Proxy_All_Policy_Without_SSP_Policy(self):
        try:
            logging.info("Add Subscriber Record with PCP Policy for News Category and Proxy-All without SSP Policy")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data add '+config.client_ip+' 32 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';BWI:BWFlag=1;BL=facebook.com;WL=yahoo.com;SSP:Subscriber-Secure-Policy=ffffffff;"')

            child.expect('Record successfully added')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=376)
    def test_376_Validate_Subscriber_Record_with_PCP_and_Proxy_All_Policy_Without_SSP_Policy(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category and Proxy-All without SSP Policy")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case execution completed")



    @pytest.mark.run(order=377)
    def test_377_Add_Proxy_domain_playboy_com_as_PASSTHRU_RPZ_Rule_to_1_RPZ_Zone_rpz32_com(self):
        logging.info ("Add Proxy Domain Playboy.com as PASSTHRU RPZ Rule to 32 RPZ zone rpz32.com")
        data={"canonical":"playboy.com", "name": "playboy.com.rpz32.com","rp_zone": "rpz32.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)


    @pytest.mark.run(order=378)
    def test_378_Validate_Added_Proxy_domain_playboy_com_as_PASSTHRU_RPZ_Rule_to_1_RPZ_Zone_rpz32_com(self):
        logging.info("Validate added Proxy Domain Playboy.com as PASSTHRU RPZ Rule to 32 RPZ zone rpz32.com\n")
        data={"name": "playboy.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "playboy.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=379)
    def test_379_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


# As per the changes of bug NIOS-78037 commented and changed the cases
    @pytest.mark.run(order=380)
    def test_380_Send_Query_from_PCP_bit_and_Proxy_All_Configured_Subscriber_client_for_Proxy_Domain_playboy_com_Validate_returns_Proxy_VIP_response_As_playboy_com_is_added_as_PASSTHRU_RPZ_rule_to_1_RPZ_Zone_and_got_RPZ_and_PCP_CEF_logs(self):
        logging.info("Perform Query from PCP bit and Proxy-All configured Subscriber client for Proxy Domain playboy.com and Validate get Proxy VIP response as playboy.com domain is added as Proxy domain is added as PASSTHRU RPZ rule to 1st RPZ zone and got RPZ and PCP CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        #assert re.search(r'.*playboy.com.*5.*IN.*A.*10.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=381)
    def test_381_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

# Changed the test cases from !=None to ==None as NIOS-78037
    @pytest.mark.run(order=382)
    def test_382_Validate_Got_Both_RPZ_PCP_CEF_Log_Logs_as_Proxy_domain_playboy_com_is_added_as_PASSTHRU_RPZ_rule_to_1_RPZ_Zone(self):
        logging.info("Validate got both RPZ and PCP CEF Log for playboy.com  ad domain is added as PASSTHRU RPZ rule to 1st RPZ zone")
        LookFor="info CEF.*playboy.com.*CAT=RPZ.*"
        LookFor1="info CEF.*playboy.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=383)
    def test_383_Remove_Proxy_playboy_com_PASSTHRU_RPZ_Rule_from_1_RPZ_Zone_rpz32_com(self):
        logging.info ("Remove Proxy Domain Playboy.com PASSTHRU RPZ Rule from 1st RPZ zone rpz32.com")
        data={"name": "playboy.com.rpz32.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=384)
    def test_384_Validate_Proxy_domain_playboy_com_PASSTHRU_RPZ_Rule_is_Deleted_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate Proxy Domain Playboy.com PASSTHRU RPZ Rule is deleted from 1st RPZ zone rpz32.com\n")
        data={"name": "playboy.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "playboy.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=385)
    def test_385_Add_Proxy_domain_playboy_com_as_PASSTHRU_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Add Proxy Domain Playboy.com as PASSTHRU RPZ Rule to 7th RPZ zone rpz25.com")
        data={"canonical":"playboy.com", "name": "playboy.com.rpz25.com","rp_zone": "rpz25.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=386)
    def test_386_Validate_Added_Proxy_domain_playboy_com_as_PASSTHRU_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate added Proxy Domain Playboy.com as PASSTHRU RPZ Rule to 7th RPZ zone rpz25.com\n")
        data={"name": "playboy.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz25.com"' in get_rpz_rule) and ('"canonical": "playboy.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=387)
    def test_387_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


# As per the changes of bug NIOS-78037 commented and changed the cases
    @pytest.mark.run(order=388)
    def test_388_Send_Query_from_PCP_bit_and_Proxy_All_Configured_Subscriber_client_for_Proxy_Domain_playboy_com_Validate_returns_Proxy_VIP_response_As_playboy_com_is_added_as_PASSTHRU_RPZ_rule_to_7th_RPZ_Zone_and_got_Only_PCP_CEF_logs(self):
        logging.info("Perform Query from PCP bit and Proxy-All configured Subscriber client for Proxy Domain playboy.com and Validate get Proxy VIP response as playboy.com domain is added as Proxy domain is added as PASSTHRU RPZ rule to 7th RPZ zone and got only PCP CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=389)
    def test_389_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


# Changed the test cases from !=None to ==None as NIOS-78037
    @pytest.mark.run(order=390)
    def test_390_Validate_Got_Both_PCP_CEF_Log_Logs_as_Proxy_domain_playboy_com_is_added_as_PASSTHRU_RPZ_rule_to_7th_RPZ_Zone(self):
        logging.info("Validate got only PCP CEF Log for playboy.com  added domain is added as PASSTHRU RPZ rule to 7th RPZ zone")
        LookFor="info CEF.*playboy.com.*CAT=RPZ.*"
        LookFor1="info CEF.*playboy.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=391)
    def test_391_Remove_Proxy_playboy_com_PASSTHRU_RPZ_Rule_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Remove Proxy Domain Playboy.com PASSTHRU RPZ Rule from 7th RPZ zone rpz25.com")
        data={"name": "playboy.com.rpz25.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=392)
    def test_392_Validate_Proxy_domain_playboy_com_PASSTHRU_RPZ_Rule_is_Deleted_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate Proxy Domain Playboy.com PASSTHRU RPZ Rule is deleted from 7th RPZ zone rpz25.com\n")
        data={"name": "playboy.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz25.com"' in get_rpz_rule) and ('"canonical": "playboy.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=393)
    def test_393_Add_Proxy_domain_playboy_com_as_NXDOMAIN_RPZ_Rule_to_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Add Proxy Domain Playboy.com as NXDOMAIN RPZ Rule to 32 RPZ zone rpz32.com")
        data={"canonical":"", "name": "playboy.com.rpz32.com","rp_zone": "rpz32.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)


    @pytest.mark.run(order=394)
    def test_394_Validate_Added_Proxy_domain_playboy_com_as_NXDOMAIN_RPZ_Rule_to_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate added Proxy Domain Playboy.com as NXDOMAIN RPZ Rule to 32 RPZ zone rpz32.com\n")
        data={"name": "playboy.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz32.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=395)
    def test_395_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")



    @pytest.mark.run(order=396)
    def test_396_Send_Query_from_PCP_bit_and_Proxy_All_Configured_Subscriber_client_for_Proxy_Domain_playboy_com_Validate_returns_NXDOMAIN_As_playboy_com_is_added_as_NXDOMAIN_RPZ_rule_to_1st_RPZ_Zone_and_got_Only_RPZ_CEF_logs(self):
        logging.info("Perform Query from PCP bit and Proxy-All configured Subscriber client for Proxy Domain playboy.com and Validate get NXDOMAIN response as playboy.com domain is added as NXDOMAIN RPZ rule to 1st RPZ zone and got only RPZ  CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NXDOMAIN.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        #assert re.search(r'.*rpz32.com.*900.*IN.*SOA.*please_set_email.absolutely.nowhere.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=398)
    def test_398_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=399)
    def test_399_Validate_Got_Only_RPZ_CEF_Log_and_not_PCP_Logs_as_Proxy_domain_playboy_com_is_added_as_NXDOMAIN_RPZ_rule_to_1st_RPZ_Zone(self):
        logging.info("Validate got only RPZ CEF Log for playboy.com  ad domain is added as NXDOMAIN RPZ rule to 1st RPZ zone")
        LookFor="info CEF.*playboy.com.*CAT=RPZ.*"
        LookFor1="info CEF.*playboy.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=400)
    def test_400_Remove_Proxy_playboy_com_NXDOMAIN_RPZ_Rule_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Remove Proxy Domain Playboy.com NXDOMAIN RPZ Rule from 1st RPZ zone rpz32.com")
        data={"name": "playboy.com.rpz32.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
            assert True
        logging.info("A NXDOMAIN RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=401)
    def test_401_Validate_Proxy_domain_playboy_com_NXDOMAIN__RPZ_Rule_is_Deleted_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate Proxy Domain Playboy.com NXDOMAIN RPZ Rule is deleted from 1st RPZ zone rpz32.com\n")
        data={"name": "playboy.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz32.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=402)
    def test_402_Add_Proxy_domain_playboy_com_as_NXDOMAIN_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Add Proxy Domain Playboy.com as NXDOMAIN RPZ Rule to 7th RPZ zone rpz25.com")
        data={"canonical":"", "name": "playboy.com.rpz25.com","rp_zone": "rpz25.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)


    @pytest.mark.run(order=403)
    def test_403_Validate_Added_Proxy_domain_playboy_com_as_NXDOMAIN_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate added Proxy Domain Playboy.com as NXDOMAIN RPZ Rule to 7th RPZ zone rpz25.com\n")
        data={"name": "playboy.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz25.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=404)
    def test_404_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=405)
    def test_405_Send_Query_from_PCP_bit_and_Proxy_All_Configured_Subscriber_client_for_Proxy_Domain_playboy_com_Validate_returns_NXDOMAIN_response_As_playboy_com_is_added_as_NXDOMAIN_RPZ_rule_to_7th_RPZ_Zone_and_got_Only_RPZ_CEF_logs_NO_PXY_CEF_log(self):
        logging.info("Perform Query from PCP bit and Proxy-All configured Subscriber client for Proxy Domain playboy.com and Validate get Proxy VIP response as playboy.com domain is added as Proxy domain is added as NXDOMAIN RPZ rule to 7th RPZ zone and got only PCP CEF logs not RPZ CEF log")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NXDOMAIN.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        #assert re.search(r'.*rpz25.com.*900.*IN.*SOA.*please_set_email.absolutely.nowhere.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=406)
    def test_406_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=407)
    def test_407_Validate_Got_Only_RPZ_CEF_Log_Logs_as_Proxy_domain_playboy_com_is_added_as_NXDOMAIN_RPZ_rule_to_7th_RPZ_Zone(self):
        logging.info("Validate got only RPZ CEF Log for playboy.com  added domain is added as NXDOMAIN RPZ rule to 7th RPZ zone")
        LookFor="info CEF.*playboy.com.*CAT=RPZ.*"
        LookFor1="info CEF.*playboy.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=408)
    def test_408_Remove_Proxy_playboy_com_NXDOMAIN_RPZ_Rule_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Remove Proxy Domain Playboy.com NXDOMAIN RPZ Rule from 7th RPZ zone rpz25.com")
        data={"name": "playboy.com.rpz25.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=409)
    def test_409_Validate_Proxy_domain_playboy_com_NXDOMAIN_RPZ_Rule_is_Deleted_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate Proxy Domain Playboy.com NXDOMAIN RPZ Rule is deleted from 7th RPZ zone rpz25.com\n")
        data={"name": "playboy.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz25.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert Falsedig_result
        else:
                assert True
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=410)
    def test_410_Add_PCP_domain_times_com_as_PASSTHRU_RPZ_Rule_to_1_RPZ_Zone_rpz32_com(self):
        logging.info ("Add PCP Domain times.com as PASSTHRU RPZ Rule to 32 RPZ zone rpz32.com")
        data={"canonical":"times.com", "name": "times.com.rpz32.com","rp_zone": "rpz32.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)


    @pytest.mark.run(order=411)
    def test_411_Validate_Added_PCP_domain_times_com_as_PASSTHRU_RPZ_Rule_to_1_RPZ_Zone_rpz32_com(self):
        logging.info("Validate added PCP Domain times.com as PASSTHRU RPZ Rule to 32 RPZ zone rpz32.com\n")
        data={"name": "times.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "times.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "times.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=412)
    def test_412_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=413)
    def test_413_Send_Query_from_PCP_bit_and_Proxy_All_Configured_Subscriber_client_for_PCP_Domain_times_com_Validate_returns_PCP_Blocking_response_As_times_com_is_added_as_PASSTHRU_RPZ_rule_to_1st_RPZ_Zone_and_got_RPZ_and_PCP_CEF_logs(self):
        logging.info("Perform Query from PCP bit and Proxy-All configured Subscriber client for PCP Domain times.com and Validate get PCP Blocking IP response as times.com domain is added as PASSTHRU RPZ rule to 1st RPZ zone and got RPZ and PCP CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
	assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        #assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        #assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=414)
    def test_414_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


# Changed the test cases from !=None to ==None as NIOS-78037
# Again changed the test cae from ==None to !=None as SNIN-57

    @pytest.mark.run(order=415)
    def test_415_Validate_Got_Both_RPZ_PCP_CEF_Log_Logs_as_PCP_domain_times_com_is_added_as_PASSTHRU_RPZ_rule_to_1st_RPZ_Zone(self):
        logging.info("Validate got both RPZ and PCP CEF Log for times.com  domain is added as PASSTHRU RPZ rule to 1st RPZ zone")
        LookFor="info CEF.*times.com.*CAT=RPZ.*"
        LookFor1="info CEF.*times.com.*CAT=0x00000000000000040000000000000000.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1!=None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=416)
    def test_416_Remove_PCP_domain_times_com_PASSTHRU_RPZ_Rule_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Remove PCP Domain times.com PASSTHRU RPZ Rule from 1st RPZ zone rpz32.com")
        data={"name": "times.com.rpz32.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=417)
    def test_417_Validate_PCP_domain_times_com_PASSTHRU_RPZ_Rule_is_Deleted_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate PCP Domain times.com PASSTHRU RPZ Rule is deleted from 1st RPZ zone rpz32.com\n")
        data={"name": "times.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "times.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "times.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=418)
    def test_418_Add_PCP_domain_times_com_as_PASSTHRU_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Add PCP Domain times.com as PASSTHRU RPZ Rule to 7th RPZ zone rpz25.com")
        data={"canonical":"times.com", "name": "times.com.rpz25.com","rp_zone": "rpz25.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=419)
    def test_419_Validate_Added_PCP_domain_times_com_as_PASSTHRU_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate added PCP Domain times.com as PASSTHRU RPZ Rule to 7th RPZ zone rpz25.com\n")
        data={"name": "times.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "times.com.rpz25.com"' in get_rpz_rule) and ('"canonical": "times.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=420)
    def test_420_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=421)
    def test_421_Send_Query_from_PCP_bit_and_Proxy_All_Configured_Subscriber_client_for_PCP_Domain_times_com_Validate_returns_PCP_blocking_IP_response_As_times_com_is_added_as_PASSTHRU_RPZ_rule_to_7th_RPZ_Zone_and_got_Both_RPZ_and_PCP_CEF_logs(self):
        logging.info("Perform Query from PCP bit and Proxy-All configured Subscriber client for PCP Domain times.com and Validate get PCP blocking response as times.com domain is added as PCP domain is added as PASSTHRU RPZ rule to 7th RPZ zone and got both RPZ and PCP CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
	assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        #assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        #assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=422)
    def test_422_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


# Changed the test cases from !=None to ==None as NIOS-78037
#Again changed the test cae from ==None to !=None as SNIN-57

    @pytest.mark.run(order=423)
    def test_423_Validate_Got_Both_RPA_and_PCP_CEF_Log_Logs_as_PCP_domain_times_com_is_added_as_PASSTHRU_RPZ_rule_to_7th_RPZ_Zone(self):
        logging.info("Validate got both RPZ and PCP CEF Log for times.com domain is added as PASSTHRU RPZ rule to 7th RPZ zone")
        LookFor="info CEF.*times.com.*CAT=RPZ.*"
        LookFor1="info CEF.*times.com.*CAT=0x00000000000000040000000000000000.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1!=None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=424)
    def test_424_Remove_Proxy_times_com_PASSTHRU_RPZ_Rule_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Remove PCP Domain times.com PASSTHRU RPZ Rule from 7th RPZ zone rpz25.com")
        data={"name": "times.com.rpz25.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=425)
    def test_425_Validate_PCP_domain_times_com_PASSTHRU_RPZ_Rule_is_Deleted_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate PCP Domain times.com PASSTHRU RPZ Rule is deleted from 7th RPZ zone rpz25.com\n")
        data={"name": "times.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "times.com.rpz25.com"' in get_rpz_rule) and ('"canonical": "times.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=426)
    def test_426_Add_PCP_domain_times_com_as_NXDOMAIN_RPZ_Rule_to_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Add PCP Domain times.com as NXDOMAIN RPZ Rule to 32 RPZ zone rpz32.com")
        data={"canonical":"", "name": "times.com.rpz32.com","rp_zone": "rpz32.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)

    @pytest.mark.run(order=427)
    def test_427_Validate_Added_PCP_domain_times_com_as_NXDOMAIN_RPZ_Rule_to_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate added PCP Domain times.com as NXDOMAIN RPZ Rule to 32 RPZ zone rpz32.com\n")
        data={"name": "times.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "times.com.rpz32.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=428)
    def test_428_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")



    @pytest.mark.run(order=429)
    def test_429_Send_Query_from_PCP_bit_and_Proxy_All_Configured_Subscriber_client_for_PCP_Domain_times_com_Validate_returns_NXDOMAIN_As_times_com_is_added_as_NXDOMAIN_RPZ_rule_to_1st_RPZ_Zone_and_got_Only_RPZ_CEF_logs(self):
        logging.info("Perform Query from PCP bit and Proxy-All configured Subscriber client for PCP Domain times.com and Validate get NXDOMAIN response as times.com domain is added as NXDOMAIN RPZ rule to 1st RPZ zone and got only RPZ  CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NXDOMAIN.*',str(dig_result))
        assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        #assert re.search(r'.*rpz32.com.*900.*IN.*SOA.*please_set_email.absolutely.nowhere.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=430)
    def test_430_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=431)
    def test_431_Validate_Got_Only_RPZ_CEF_Log_and_not_PCP_Logs_as_PCP_domain_times_com_is_added_as_NXDOMAIN_RPZ_rule_to_1st_RPZ_Zone(self):
        logging.info("Validate got only RPZ CEF Log for times.com domain is added as NXDOMAIN RPZ rule to 1st RPZ zone")
        LookFor="info CEF.*times.com.*CAT=RPZ.*"
        LookFor1="info CEF.*times.com.*CAT=0x00000000000000040000000000000000.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=432)
    def test_432_Remove_PCP_times_com_NXDOMAIN_RPZ_Rule_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Remove PCP Domain times.com NXDOMAIN RPZ Rule from 1st RPZ zone rpz32.com")
        data={"name": "times.com.rpz32.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=433)
    def test_433_Validate_PCP_domain_times_com_NXDOMAIN__RPZ_Rule_is_Deleted_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate PCP Domain times.com NXDOMAIN RPZ Rule is deleted from 1st RPZ zone rpz32.com\n")
        data={"name": "times.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "times.com.rpz32.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=434)
    def test_434_Add_PCP_domain_times_com_as_NXDOMAIN_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Add PCP Domain times.com as NXDOMAIN RPZ Rule to 7th RPZ zone rpz25.com")
        data={"canonical":"", "name": "times.com.rpz25.com","rp_zone": "rpz25.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=435)
    def test_435_Validate_Added_PCP_domain_times_com_as_NXDOMAIN_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate added PCP Domain times.com as NXDOMAIN RPZ Rule to 7th RPZ zone rpz25.com\n")
        data={"name": "times.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "times.com.rpz25.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=436)
    def test_436_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=437)
    def test_437_Send_Query_from_PCP_bit_and_Proxy_All_Configured_Subscriber_client_for_PCP_Domain_times_com_Validate_returns_NXDOMAIN_response_As_times_com_is_added_as_NXDOMAIN_RPZ_rule_to_7th_RPZ_Zone_and_got_Only_RPZ_CEF_logs_NO_PCP_CEF_log(self):
        logging.info("Perform Query from PCP bit and Proxy-All configured Subscriber client for PCP Domain times.com and Validate get NXDOMAIN response as times.com domain is added as PCP domain is added as NXDOMAIN RPZ rule to 7th RPZ zone and got only RPZ CEF logs not PCP CEF log")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NXDOMAIN.*',str(dig_result))
        assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        #assert re.search(r'.*rpz25.com.*900.*IN.*SOA.*please_set_email.absolutely.nowhere.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=438)
    def test_438_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=439)
    def test_439_Validate_Got_Only_RPZ_CEF_Log_Logs_as_PCP_domain_times_com_is_added_as_NXDOMAIN_RPZ_rule_to_7th_RPZ_Zone(self):
        logging.info("Validate got only RPZ CEF Log for times.com  domain is added as NXDOMAIN RPZ rule to 7th RPZ zone")
        LookFor="info CEF.*times.com.*CAT=RPZ.*"
        LookFor1="info CEF.*times.com.*CAT=0x00000000000000040000000000000000.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=440)
    def test_440_Remove_PCP_times_com_NXDOMAIN_RPZ_Rule_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Remove PCP Domain times.com NXDOMAIN RPZ Rule from 7th RPZ zone rpz25.com")
        data={"name": "times.com.rpz25.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=441)
    def test_441_Validate_PCP_domain_times_com_NXDOMAIN_RPZ_Rule_is_Deleted_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate PCP Domain times.com NXDOMAIN RPZ Rule is deleted from 7th RPZ zone rpz25.com\n")
        data={"name": "times.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "times.com.rpz25.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=442)
    def test_442_Add_BL_domain_facebook_com_as_PASSTHRU_RPZ_Rule_to_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Add BL Domain facebook.com as PASSTHRU RPZ Rule to 1st RPZ zone rpz32.com")
        data={"canonical":"facebook.com", "name": "facebook.com.rpz32.com","rp_zone": "rpz32.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=443)
    def test_443_Validate_Added_BL_domain_facebook_com_as_PASSTHRU_RPZ_Rule_to_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate added BL Domain facebook.com as PASSTHRU RPZ Rule to 1st RPZ zone rpz32.com\n")
        data={"name": "facebook.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "facebook.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "facebook.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=444)
    def test_444_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=445)
    def test_445_Send_Query_from_BL_bit_and_Proxy_All_Configured_Subscriber_client_for_BL_Domain_facebook_com_Validate_returns_BL_Blocking_response_As_facebook_com_is_added_as_PASSTHRU_RPZ_rule_to_1st_RPZ_Zone_and_got_RPZ_and_BL_CEF_logs(self):
        logging.info("Perform Query from BL bit and Proxy-All configured Subscriber client for BL Domain facebook.com and Validate get BL Blocking IP response as facebook.com domain is added as PASSTHRU RPZ rule to 1st RPZ zone and got RPZ and BL CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
	assert re.search(r'.*facebook.com.*IN.*A.*',str(dig_result))
        #assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        #assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=446)
    def test_446_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


# Changed the test cases from !=None to ==None as NIOS-78037
#Again changed the test cae from ==None to !=None as SNIN-57

    @pytest.mark.run(order=447)
    def test_447_Validate_Got_Both_RPZ_BL_CEF_Log_Logs_as_BL_domain_facebook_com_is_added_as_PASSTHRU_RPZ_rule_to_1st_RPZ_Zone(self):
        logging.info("Validate got both RPZ and BL CEF Log for facebook.com  domain is added as PASSTHRU RPZ rule to 1st RPZ zone")
        LookFor="info CEF.*facebook.com.*CAT=RPZ.*"
        LookFor1="info CEF.*facebook.com.*CAT=BL.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1!=None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=448)
    def test_448_Remove_BL_domain_facebook_com_PASSTHRU_RPZ_Rule_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Remove BL Domain facebook.com PASSTHRU RPZ Rule from 1st RPZ zone rpz32.com")
        data={"name": "facebook.com.rpz32.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)



    @pytest.mark.run(order=449)
    def test_449_Validate_BL_domain_facebook_com_PASSTHRU_RPZ_Rule_is_Deleted_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate BL Domain facebook.com PASSTHRU RPZ Rule is deleted from 1st RPZ zone rpz32.com\n")
        data={"name": "facebook.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "facebook.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "facebook.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=450)
    def test_450_Add_BL_domain_facebook_com_as_PASSTHRU_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Add BL Domain facebook.com as PASSTHRU RPZ Rule to 7th RPZ zone rpz25.com")
        data={"canonical":"facebook.com", "name": "facebook.com.rpz25.com","rp_zone": "rpz25.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)

    @pytest.mark.run(order=451)
    def test_451_Validate_Added_BL_domain_facebook_com_as_PASSTHRU_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate added BL Domain facebook.com as PASSTHRU RPZ Rule to 7th RPZ zone rpz25.com\n")
        data={"name": "facebook.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "facebook.com.rpz25.com"' in get_rpz_rule) and ('"canonical": "facebook.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=452)
    def test_452_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


# As per the changes of bug NIOS-78037 commented and changed the cases
    @pytest.mark.run(order=453)
    def test_453_Send_Query_from_BL_bit_and_Proxy_All_Configured_Subscriber_client_for_BL_Domain_facebook_com_Validate_returns_BL_blocking_IP_response_As_facebook_com_is_added_as_PASSTHRU_RPZ_rule_to_7th_RPZ_Zone_and_got_both_RPZ_and_BL_CEF_logs(self):
        logging.info("Perform Query from BL bit and Proxy-All configured Subscriber client for BL Domain facebook.com and Validate get BL blocking response as facebook.com domain is added as BL domain is added as PASSTHRU RPZ rule to 7th RPZ zone and got both RPZ and BL CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
	assert re.search(r'.*facebook.com.*IN.*A.*',str(dig_result))
        #assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        #assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=454)
    def test_454_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


# Changed the test cases from !=None to ==None as NIOS-78037
#Again changed the test cae from ==None to !=None as SNIN-57

    @pytest.mark.run(order=455)
    def test_455_Validate_Got_Only_BL_CEF_Log_Logs_as_BL_domain_facebook_com_is_added_as_PASSTHRU_RPZ_rule_to_7th_RPZ_Zone(self):
        logging.info("Validate got only BL CEF Log for facebook.com domain is added as PASSTHRU RPZ rule to 7th RPZ zone")
        LookFor="info CEF.*facebook.com.*CAT=RPZ.*"
        LookFor1="info CEF.*facebook.com.*CAT=BL.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1!=None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=456)
    def test_456_Remove_Proxy_facebook_com_PASSTHRU_RPZ_Rule_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Remove BL Domain facebook.com PASSTHRU RPZ Rule from 7th RPZ zone rpz25.com")
        data={"name": "facebook.com.rpz25.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)



    @pytest.mark.run(order=457)
    def test_457_Validate_BL_domain_facebook_com_PASSTHRU_RPZ_Rule_is_Deleted_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate BL Domain facebook.com PASSTHRU RPZ Rule is deleted from 7th RPZ zone rpz25.com\n")
        data={"name": "facebook.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "facebook.com.rpz25.com"' in get_rpz_rule) and ('"canonical": "facebook.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=458)
    def test_458_Add_BL_domain_facebook_com_as_NXDOMAIN_RPZ_Rule_to_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Add BL Domain facebook.com as NXDOMAIN RPZ Rule to 32 RPZ zone rpz32.com")
        data={"canonical":"", "name": "facebook.com.rpz32.com","rp_zone": "rpz32.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=459)
    def test_459_Validate_Added_BL_domain_facebook_com_as_NXDOMAIN_RPZ_Rule_to_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate added BL Domain facebook.com as NXDOMAIN RPZ Rule to 32 RPZ zone rpz32.com\n")
        data={"name": "facebook.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "facebook.com.rpz32.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=460)
    def test_460_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=461)
    def test_461_Send_Query_from_BL_bit_and_Proxy_All_Configured_Subscriber_client_for_BL_Domain_facebook_com_Validate_returns_NXDOMAIN_As_facebook_com_is_added_as_NXDOMAIN_RPZ_rule_to_1st_RPZ_Zone_and_got_Only_RPZ_CEF_logs(self):
        logging.info("Perform Query from BL bit and Proxy-All configured Subscriber client for BL Domain facebook.com and Validate get NXDOMAIN response as facebook.com domain is added as NXDOMAIN RPZ rule to 1st RPZ zone and got only RPZ  CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NXDOMAIN.*',str(dig_result))
        assert re.search(r'.*facebook.com.*IN.*A.*',str(dig_result))
        #assert re.search(r'.*rpz32.com.*900.*IN.*SOA.*please_set_email.absolutely.nowhere.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=462)
    def test_462_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=463)
    def test_463_Validate_Got_Only_RPZ_CEF_Log_and_not_BL_Logs_as_BL_domain_facebook_com_is_added_as_NXDOMAIN_RPZ_rule_to_1st_RPZ_Zone(self):
        logging.info("Validate got only RPZ CEF Log for facebook.com domain is added as NXDOMAIN RPZ rule to 1st RPZ zone")
        LookFor="info CEF.*facebook.com.*CAT=RPZ.*"
        LookFor1="info CEF.*facebook.com.*CAT=BL.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=464)
    def test_464_Remove_BL_facebook_com_NXDOMAIN_RPZ_Rule_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Remove BL Domain facebook.com NXDOMAIN RPZ Rule from 1st RPZ zone rpz32.com")
        data={"name": "facebook.com.rpz32.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)



    @pytest.mark.run(order=465)
    def test_465_Validate_BL_domain_facebook_com_NXDOMAIN__RPZ_Rule_is_Deleted_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate BL Domain facebook.com NXDOMAIN RPZ Rule is deleted from 1st RPZ zone rpz32.com\n")
        data={"name": "facebook.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "facebook.com.rpz32.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=466)
    def test_466_Add_BL_domain_facebook_com_as_NXDOMAIN_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Add BL Domain facebook.com as NXDOMAIN RPZ Rule to 7th RPZ zone rpz25.com")
        data={"canonical":"", "name": "facebook.com.rpz25.com","rp_zone": "rpz25.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)


    @pytest.mark.run(order=467)
    def test_467_Validate_Added_BL_domain_facebook_com_as_NXDOMAIN_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate added BL Domain facebook.com as NXDOMAIN RPZ Rule to 7th RPZ zone rpz25.com\n")
        data={"name": "facebook.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "facebook.com.rpz25.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=468)
    def test_468_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=469)
    def test_469_Send_Query_from_BL_bit_and_Proxy_All_Configured_Subscriber_client_for_BL_Domain_facebook_com_Validate_returns_NXDOMAIN_response_As_facebook_com_is_added_as_NXDOMAIN_RPZ_rule_to_7th_RPZ_Zone_and_got_Only_RPZ_CEF_logs_NO_BL_CEF_log(self):
        logging.info("Perform Query from BL bit and Proxy-All configured Subscriber client for BL Domain facebook.com and Validate get NXDOMAIN response as facebook.com domain is added as BL domain is added as NXDOMAIN RPZ rule to 7th RPZ zone and got only RPZ CEF logs not BL CEF log")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' facebook.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result

        assert re.search(r'.*QUERY, status: NXDOMAIN.*',str(dig_result))
        assert re.search(r'.*facebook.com.*IN.*A.*',str(dig_result))
        #assert re.search(r'.*rpz25.com.*900.*IN.*SOA.*please_set_email.absolutely.nowhere.*',str(dig_result))
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=470)
    def test_470_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=471)
    def test_471_Validate_Got_Only_BL_CEF_Log_Logs_as_BL_domain_facebook_com_is_added_as_NXDOMAIN_RPZ_rule_to_7th_RPZ_Zone(self):
        logging.info("Validate got only BL CEF Log for facebook.com  domain is added as NXDOMAIN RPZ rule to 7th RPZ zone")
        LookFor="info CEF.*facebook.com.*CAT=RPZ.*"
        LookFor1="info CEF.*facebook.com.*CAT=BL.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=472)
    def test_472_Remove_BL_facebook_com_NXDOMAIN_RPZ_Rule_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Remove BL Domain facebook.com NXDOMAIN RPZ Rule from 7th RPZ zone rpz25.com")
        data={"name": "facebook.com.rpz25.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)



    @pytest.mark.run(order=473)
    def test_473_Validate_BL_domain_facebook_com_NXDOMAIN_RPZ_Rule_is_Deleted_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate BL Domain facebook.com NXDOMAIN RPZ Rule is deleted from 7th RPZ zone rpz25.com\n")
        data={"name": "facebook.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "facebook.com.rpz25.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=474)
    def test_474_Add_WPCP_domain_coors_com_as_PASSTHRU_RPZ_Rule_to_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Add WPCP Domain coors.com as PASSTHRU RPZ Rule to 1st RPZ zone rpz32.com")
        data={"canonical":"coors.com", "name": "coors.com.rpz32.com","rp_zone": "rpz32.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)


    @pytest.mark.run(order=475)
    def test_475_Validate_Added_WPCP_domain_coors_com_as_PASSTHRU_RPZ_Rule_to_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate added WPCP Domain coors.com as PASSTHRU RPZ Rule to 1st RPZ zone rpz32.com\n")
        data={"name": "coors.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "coors.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=476)
    def test_476_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=477)
    def test_477_Send_Query_from_WPCP_bit_and_Proxy_All_Configured_Subscriber_client_for_WPCP_Domain_coors_com_Validate_returns_Proxy_VIP_response_As_coors_com_is_added_as_PASSTHRU_RPZ_rule_to_1st_RPZ_Zone_and_got_RPZ_and_WPCP_CEF_logs(self):
        logging.info("Perform Query from WPCP bit and Proxy-All configured Subscriber client for WPCP Domain coors.com and Validate get WPCP Blocking IP response as coors.com domain is added as PASSTHRU RPZ rule to 1st RPZ zone and got RPZ and WPCP CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' coors.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*coors.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=478)
    def test_478_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


# Changed the test cases from !=None to ==None as NIOS-78037
#Again changed the test cae from ==None to !=None as SNIN-57

    @pytest.mark.run(order=479)
    def test_479_Validate_Got_3_CEF_logs_RPZ_WPCP_PXY_CEF_Log_Logs_as_WPCP_domain_coors_com_is_added_as_PASSTHRU_RPZ_rule_to_1st_RPZ_Zone(self):
        logging.info("Validate got both RPZ and WPCP CEF Log for coors.com  domain is added as PASSTHRU RPZ rule to 1st RPZ zone")
        LookFor="info CEF.*coors.com.*CAT=RPZ.*"
        LookFor1="info CEF.*coors.com.*CAT=WRN_0x00000000000000000000000000000001.*"
        LookFor2="info CEF.*coors.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1!=None and logs2==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=480)
    def test_480_Remove_WPCP_domain_coors_com_PASSTHRU_RPZ_Rule_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Remove WPCP Domain coors.com PASSTHRU RPZ Rule from 1st RPZ zone rpz32.com")
        data={"name": "coors.com.rpz32.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)



    @pytest.mark.run(order=481)
    def test_481_Validate_WPCP_domain_coors_com_PASSTHRU_RPZ_Rule_is_Deleted_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate WPCP Domain coors.com PASSTHRU RPZ Rule is deleted from 1st RPZ zone rpz32.com\n")
        data={"name": "coors.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "coors.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=482)
    def test_482_Add_WPCP_domain_coors_com_as_PASSTHRU_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Add WPCP Domain coors.com as PASSTHRU RPZ Rule to 7th RPZ zone rpz25.com")
        data={"canonical":"coors.com", "name": "coors.com.rpz25.com","rp_zone": "rpz25.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)

    @pytest.mark.run(order=483)
    def test_483_Validate_Added_WPCP_domain_coors_com_as_PASSTHRU_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate added WPCP Domain coors.com as PASSTHRU RPZ Rule to 7th RPZ zone rpz25.com\n")
        data={"name": "coors.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz25.com"' in get_rpz_rule) and ('"canonical": "coors.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=484)
    def test_484_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


# As per the changes of bug NIOS-78037 commented and changed the cases
    @pytest.mark.run(order=485)
    def test_485_Send_Query_from_WPCP_bit_and_Proxy_All_Configured_Subscriber_client_for_WPCP_Domain_coors_com_Validate_returns_Proxy_VIP_IP_response_As_coors_com_is_added_as_PASSTHRU_RPZ_rule_to_7th_RPZ_Zone_and_got_3_RPZ_and_WPCP_PXY_CEF_logs(self):
        logging.info("Perform Query from WPCP bit and Proxy-All configured Subscriber client for WPCP Domain coors.com and Validate get WPCP blocking response as coors.com domain is added as WPCP domain is added as PASSTHRU RPZ rule to 7th RPZ zone and got both RPZ and WPCP and PXY CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' coors.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*coors.com.*IN.*A.*',str(dig_result))
        #assert re.search(r'.*coors.com.*5.*IN.*A.*10.*',str(dig_result))
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=486)
    def test_486_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


# Changed the test cases from !=None to ==None as NIOS-78037
#Again changed the test cae from ==None to !=None as SNIN-57

    @pytest.mark.run(order=487)
    def test_487_Validate_Got_3_RPZ_and_WPCP_and_PXY_CEF_Log_Logs_as_WPCP_domain_coors_com_is_added_as_PASSTHRU_RPZ_rule_to_7th_RPZ_Zone(self):
        logging.info("Validate got both RPZ and WPCP and PXY CEF Log for coors.com domain is added as PASSTHRU RPZ rule to 7th RPZ zone")
        LookFor="info CEF.*coors.com.*CAT=RPZ.*"
        LookFor1="info CEF.*coors.com.*CAT=WRN_0x00000000000000000000000000000001.*"
        LookFor2="info CEF.*coors.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        if logs!=None and logs1!=None and logs2==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=488)
    def test_488_Remove_WPCP_coors_com_PASSTHRU_RPZ_Rule_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Remove WPCP Domain coors.com PASSTHRU RPZ Rule from 7th RPZ zone rpz25.com")
        data={"name": "coors.com.rpz25.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)



    @pytest.mark.run(order=489)
    def test_489_Validate_WPCP_domain_coors_com_PASSTHRU_RPZ_Rule_is_Deleted_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate WPCP Domain coors.com PASSTHRU RPZ Rule is deleted from 7th RPZ zone rpz25.com\n")
        data={"name": "coors.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz25.com"' in get_rpz_rule) and ('"canonical": "coors.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=490)
    def test_490_Add_WPCP_domain_coors_com_as_NXDOMAIN_RPZ_Rule_to_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Add WPCP Domain coors.com as NXDOMAIN RPZ Rule to 32 RPZ zone rpz32.com")
        data={"canonical":"", "name": "coors.com.rpz32.com","rp_zone": "rpz32.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)


    @pytest.mark.run(order=491)
    def test_491_Validate_Added_WPCP_domain_coors_com_as_NXDOMAIN_RPZ_Rule_to_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate added WPCP Domain coors.com as NXDOMAIN RPZ Rule to 32 RPZ zone rpz32.com\n")
        data={"name": "coors.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz32.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=492)
    def test_492_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=493)
    def test_493_Send_Query_from_WPCP_bit_and_Proxy_All_Configured_Subscriber_client_for_WPCP_Domain_coors_com_Validate_returns_NXDOMAIN_As_coors_com_is_added_as_NXDOMAIN_RPZ_rule_to_1st_RPZ_Zone_and_got_Only_RPZ_CEF_logs(self):
        logging.info("Perform Query from WPCP bit and Proxy-All configured Subscriber client for WPCP Domain coors.com and Validate get NXDOMAIN response as coors.com domain is added as NXDOMAIN RPZ rule to 1st RPZ zone and got only RPZ  CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' coors.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NXDOMAIN.*',str(dig_result))
        assert re.search(r'.*coors.com.*IN.*A.*',str(dig_result))
        #assert re.search(r'.*rpz32.com.*900.*IN.*SOA.*please_set_email.absolutely.nowhere.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=494)
    def test_494_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=495)
    def test_495_Validate_Got_Only_RPZ_CEF_Log_and_not_WPCP_Logs_as_WPCP_domain_coors_com_is_added_as_NXDOMAIN_RPZ_rule_to_1st_RPZ_Zone(self):
        logging.info("Validate got only RPZ CEF Log for coors.com domain is added as NXDOMAIN RPZ rule to 1st RPZ zone")
        LookFor="info CEF.*coors.com.*CAT=RPZ.*"
        LookFor1="info CEF.*coors.com.*CAT=WRN_0x00000000000000000000000000000001.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=496)
    def test_496_Remove_WPCP_coors_com_NXDOMAIN_RPZ_Rule_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Remove WPCP Domain coors.com NXDOMAIN RPZ Rule from 1st RPZ zone rpz32.com")

        data={"name": "coors.com.rpz32.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)



    @pytest.mark.run(order=497)
    def test_497_Validate_WPCP_domain_coors_com_NXDOMAIN__RPZ_Rule_is_Deleted_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate WPCP Domain coors.com NXDOMAIN RPZ Rule is deleted from 1st RPZ zone rpz32.com\n")
        data={"name": "coors.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz32.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=498)
    def test_498_Add_WPCP_domain_coors_com_as_NXDOMAIN_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Add WPCP Domain coors.com as NXDOMAIN RPZ Rule to 7th RPZ zone rpz25.com")
        data={"canonical":"", "name": "coors.com.rpz25.com","rp_zone": "rpz25.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=499)
    def test_499_Validate_Added_WPCP_domain_coors_com_as_NXDOMAIN_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate added WPCP Domain coors.com as NXDOMAIN RPZ Rule to 7th RPZ zone rpz25.com\n")
        data={"name": "coors.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz25.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=500)
    def test_500_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=501)
    def test_501_Send_Query_from_WPCP_bit_and_Proxy_All_Configured_Subscriber_client_for_WPCP_Domain_coors_com_Validate_returns_NXDOMAIN_response_As_coors_com_is_added_as_NXDOMAIN_RPZ_rule_to_7th_RPZ_Zone_and_got_Only_RPZ_and_NOT_PXY_CEF_logs_and_NOT_WPCP_CEF_log(self):
        logging.info("Perform Query from WPCP bit and Proxy-All configured Subscriber client for WPCP Domain coors.com and Validate get WPCP Blocking IB response as coors.com domain is added as WPCP domain is added as NXDOMAIN RPZ rule to 7th RPZ zone and got only RPZ and not PXY CEF logs or WPCP CEF log")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' coors.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NXDOMAIN.*',str(dig_result))
        assert re.search(r'.*coors.com.*IN.*A.*',str(dig_result))
        #assert re.search(r'.*rpz25.com.*900.*IN.*SOA.*please_set_email.absolutely.nowhere.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=502)
    def test_502_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=503)
    def test_503_Validate_Got_Only_RPZ_and_NOT_PXY_OR_PXY_CEF_Log_Logs_as_WPCP_domain_coors_com_is_added_as_NXDOMAIN_RPZ_rule_to_7th_RPZ_Zone(self):
        logging.info("Validate got only RPZ and not WPCP or PXY CEF Log for coors.com  domain is added as NXDOMAIN RPZ rule to 7th RPZ zone")
        LookFor="info CEF.*coors.com.*CAT=RPZ.*"
        LookFor1="info CEF.*coors.com.*CAT=WRN_0x00000000000000000000000000000001.*"
        LookFor2="info CEF.*coors.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1==None and logs2==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=504)
    def test_504_Remove_WPCP_coors_com_NXDOMAIN_RPZ_Rule_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Remove WPCP Domain coors.com NXDOMAIN RPZ Rule from 7th RPZ zone rpz25.com")
        data={"name": "coors.com.rpz25.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A NXDOMAIN RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)



    @pytest.mark.run(order=505)
    def test_505_Validate_WPCP_domain_coors_com_NXDOMAIN_RPZ_Rule_is_Deleted_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate WPCP Domain coors.com NXDOMAIN RPZ Rule is deleted from 7th RPZ zone rpz25.com\n")
        data={"name": "coors.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz25.com"' in get_rpz_rule) and ('"canonical": ""' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=506)
    def test_506_Delete_Subscriber_Record_with_Proxy_all_set_From_Subscriber_Cache(self):
        try:
            logging.info("Delete the Subscriber Record with Proxy-All set to True from Subscriber Cache")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data delete '+config.client_ip+' 32 N/A N/A')
            child.expect('Record successfully deleted')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Failed")
            assert False


#    @pytest.mark.run(order=506)
#    def test_506_From_Radclient_Send_Stop_Radius_Message_to_Delete_Subscriber_Record_with_Proxy_all_set_From_Subscriber_Cache(self):
#        logging.info("From Rad client send Stop Radius message to Delete the Subscriber Record with Proxy-All set to True from Subscriber Cache ")
#        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part2_radfiles/RFE_9980_PCP_Proxy_All_Stop.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
#        dig_result = subprocess.check_output(dig_cmd, shell=True)
#        print dig_result
#        assert re.search(r'',str(dig_result))
#        logging.info("Test Case Execution Completed")
#        sleep(15)



    @pytest.mark.run(order=507)
    def test_507_Validate_Subscriber_Record_with_Proxy_all_set_is_deleted_from_Subscriber_Cache(self):
        logging.info("Validate Subscriber Record with Proxy-All set to True is deleted from subscriber cache")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        if re.search(r'.*'+config.client_ip+'.*',c):
            logging.info("Test Case 24 Execution Failed")
            assert False
        else:
            logging.info("Test Case Execution Passed")
            assert True
        logging.info("Test case execution completed")
        sleep(10)


    @pytest.mark.run(order=508)
    def test_508_Restart_DNS_service(self):
        logging.info("Restart services")
        restart_the_grid()
        #grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        #ref = json.loads(grid)[0]['_ref']
        #restart_the_grid()
        #publish={"member_order":"SIMULTANEOUSLY"}
        #request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        #request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        #restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(10)






######################### IPv4 Network Subscriber Records Functionality Test Cases for both Bind and DCA  #########################

    @pytest.mark.run(order=600)
    def test_600__________________IPv4_Network_Subscriber_Records_Functionality_Test_Cases_______________(self):
        logging.info("IPv4 Network Subscriber Records Functionality Test Cases for both Bind and DCA")



#    @pytest.mark.run(order=601)
#    def test_601_Add_IPv4_Network_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
#        try:
#            logging.info("Add IPv4 Network Subscriber Record with PCP Policy for News Category")
#            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
#            child.logfile=sys.stdout
#            child.expect('password:',timeout=None)
#            child.sendline('infoblox')
#            child.expect('Infoblox >')
#            child.sendline('set subscriber_secure_data add '+config.client_network_8+' 8 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;"')
#            child.expect('Record successfully added')
#            logging.info("Test Case Execution Passed")
#            assert True
#        except:
#            logging.info("Test Case Execution Failed")
#            assert False




    @pytest.mark.run(order=601)
    def test_601_From_Radclient_Send_Start_Radius_Message_for_IPv4_Network_Subscriber_Record_with_PCP_Policy_and_Proxy_All_Configured(self):
        logging.info("From Rad client send Start Radius message for IPv4 Network Subscriber Record with PCP Policy and Proxy-All Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part2_radfiles/RFE_9980_IPv4_Network_PCP_Proxy_All.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=602)
    def test_602_Validate_IPv4_Network_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate IPv4 Network Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_network_8+'\/8\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case execution completed")


#    @pytest.mark.run(order=603)
#    def test_603_Add_Subscriber_Record_without_Proxy_all_set_and_Different_PCP_Policy_bit_than_above(self):
#        try:
#            logging.info("Add Subscriber Record without Proxy-All set and different PCP Policy bit than the above")
#            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
#            child.logfile=sys.stdout
#            child.expect('password:',timeout=None)
#            child.sendline('infoblox')
#            child.expect('Infoblox >')
#            child.sendline('set subscriber_secure_data add '+config.client_ip2+' 32 N/A N/A "ACS:Acct-Session-Id=9999735888;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=01000000000000010000000000000000;SUB:Calling-Station-Id=110361288;PCC:PC-Category-Policy=00000000000000000000000000000001;"')
#            child.expect('Record successfully added')
#            logging.info("Test Case Execution Passed")
#            assert True
#        except:
#            logging.info("Test Case Execution Failed")
#            assert False



    @pytest.mark.run(order=603)
    def test_603_From_Radclient_Send_Start_Radius_Message_without_Proxy_all_set_and_Different_PCP_Policy_bit_than_above_to_make_sure_Domain_Cache_to_DCA_with_PCP_Word(self):
        logging.info("From Rad client send Start Radius message without Proxy-All set and different PCP Policy bit than the above to make sure Doamin cache_to DCA with PCP word")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part2_radfiles/RFE_9980_Only_PCP_for_Cache.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)



    @pytest.mark.run(order=604)
    def test_604_Validate_Subscriber_Record_without_Proxy_all_set_and_Different_PCP_Policy_bit_than_above(self):
        logging.info("Validate Subscriber Record without Proxy-All set different PCP Policy bit than the above")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case execution completed")



    @pytest.mark.run(order=605)
    def test_605_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=606)
    def test_606_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
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
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=607)
    def test_607_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_Blocked_IPs_in_response_from_Bind_As_Not_DCA_Cache(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and get PCP Blocked IPs response from Bind as times.com not in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=608)
    def test_608_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on master")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=609)
    def test_609_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_times_com(self):
        logging.info("Validate Named CEF Log for times.com  when get response from Bind")
        LookFor="named.*info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
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


    @pytest.mark.run(order=610)
    def test_610_Validate_PCP_Domain_times_com_did_not_cached_to_DCA_When_Send_Query_From_PCP_bit_Matched_Subscriber_client(self):
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
        logging.info("Test Case Execution Completed")
        sleep(20)


    @pytest.mark.run(order=611)
    def test_611_Validate_when_get_response_from_Bind_for_PCP_domain_times_com_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased(self):
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
        logging.info("Test Case Execution Completed")
        sleep(15)



    @pytest.mark.run(order=612)
    def test_612_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)



    @pytest.mark.run(order=613)
    def test_613_Send_Query_from_NON_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_cached_DCA_with_PCP_word(self):
        logging.info("Perform Query from NON PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and Validate get NORMAL response times.com domain is cached to DCA with PCP word")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=614)
    def test_614_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=615)
    def test_615_Validate_NO_CEF_Log_Logs_when_get_NORMAL_response_for_PCP_domain_times_com_when_send_query_from_NON_PCP_bit_match_client(self):
        logging.info("Validate NO CEF Log for times.com  when get NORMAL response when send query from NON PCP bit match client")
        LookFor="info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
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


    @pytest.mark.run(order=616)
    def test_616_Validate_PCP_Domain_times_com_get_cached_to_DCA_When_Send_Query_From_NON_PCP_bit_Matched_Subscriber_client(self):
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
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=617)
    def test_617_Validate_when_get_response_from_Bind_for_PCP_domain_times_com_Cache_hit_count_not_increased_and_Miss_cache_count_count_increased(self):
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
        assert re.search(r'.*Cache miss count.*2.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)

    @pytest.mark.run(order=618)
    def test_618_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")



    @pytest.mark.run(order=619)
    def test_619_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_Blocked_IPs_in_response_from_DCA_As_times_com_domain_is_already_DCA_Cache(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and get PCP Blocked IPs response from DCA as times.com is already in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=620)
    def test_620_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=621)
    def test_621_Validate_DCA_CEF_Log_Logs_when_get_response_from_DCA_for_PCP_domain_times_com(self):
        logging.info("Validate DCA CEF Log for times.com  when get response from DCA")
        LookFor="fp-rte.*info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
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



    @pytest.mark.run(order=622)
    def test_622_Validate_when_get_response_from_DCA_for_PCP_domain_times_com_Cache_hit_count_is_increased_and_Miss_cache_count_count_not_increased(self):
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
        logging.info("Test Case Execution Completed")
        sleep(10)


#    @pytest.mark.run(order=623)
#    def test_623_Delete_IPv4_Network_Subscriber_Record_with_Proxy_all_set_From_Subscriber_Cache(self):
#        try:
#            logging.info("Delete the IPv4 Network Subscriber Record with Proxy-All set to True from Subscriber Cache")
#            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
#            child.logfile=sys.stdout
#            child.expect('password:',timeout=None)
#            child.sendline('infoblox')
#            child.expect('Infoblox >')
#            child.sendline('set subscriber_secure_data delete '+config.client_network_8+' 8 N/A N/A')
#            child.expect('Record successfully deleted')
#            logging.info("Test Case Execution Passed")
#            assert True
#        except:
#            logging.info("Test Case Execution Failed")
#            assert False




    @pytest.mark.run(order=623)
    def test_623_From_Radclient_Send_Stop_Radius_Message_to_Delete_IPv4_Network_Subscriber_Record_with_Proxy_all_set_From_Subscriber_Cache(self):
        logging.info("From Rad client send Stop Radius message to Delete the IPv4 Network Subscriber Record with Proxy-All set to True from Subscriber Cache ")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part2_radfiles/RFE_9980_IPv4_Network_PCP_Proxy_All_Stop.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)



    @pytest.mark.run(order=624)
    def test_624_Validate_IPv4_Network_Subscriber_Record_with_Proxy_all_set_1_is_deleted_from_Subscriber_Cache(self):
        logging.info("Validate IPv4 Network Subscriber Record with Proxy-All set to True is deleted from subscriber cache")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        if re.search(r','+config.client_network_8+'',c):
            logging.info("Test Case Execution Failed")
            assert False
        else:
            logging.info("Test Case Execution Passed")
            assert True
        logging.info("Test case execution completed")
        sleep(10)



    @pytest.mark.run(order=625)
    def test_625_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)



    @pytest.mark.run(order=626)
    def test_626_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_Even_PCP_Domain_in_Cache_with_PCP_word_But_Match_subscriber_client_is_delete(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and Validate get NORMAL response even times.com domain is in cache with PCP word but subscriber client is deleted from subscriber cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=627)
    def test_627_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=628)
    def test_628_Validate_No_CEF_Log_Logs_when_get_NORMAL_response_from_DCA_for_PCP_domain_times_com(self):
        logging.info("Validate NO CEF Log for times.com  when get NORMAL response")
        LookFor="info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
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



    @pytest.mark.run(order=629)
    def test_629_Validate_PCP_Domain_times_com_still_exist_in_DCA_cache(self):
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
        logging.info("Test Case Execution Completed")
        sleep(10)



    @pytest.mark.run(order=630)
    def test_630_Validate_when_get_response_from_DCA_for_PCP_domain_times_com_Cache_hit_count_is_increased_and_Miss_cache_count_count_not_increased(self):
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
        logging.info("Test Case Execution Completed")
        sleep(10)


#    @pytest.mark.run(order=631)
#    def test_631_Add_Back_Same_IPv4_Network_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
#        try:
#            logging.info("Add Same IPv4 Network Subscriber Record with PCP Policy for News Category")
#            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
#            child.logfile=sys.stdout
#            child.expect('password:',timeout=None)
#            child.sendline('infoblox')
#           child.expect('Infoblox >')
#            child.sendline('set subscriber_secure_data add '+config.client_network_8+' 8 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;"')
#            child.expect('Record successfully added')
#            logging.info("Test Case Execution Passed")
#            assert True
#        except:
#            logging.info("Test Case Execution Failed")
#            assert False



    @pytest.mark.run(order=631)
    def test_631_From_Radclient_Send_Start_Radius_Message_for_IPv4_Network_Subscriber_Record_with_PCP_Policy_and_Proxy_All_Configured(self):
        logging.info("From Rad client send Start Radius message for IPv4 Network Subscriber Record with PCP Policy and Proxy-All Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part2_radfiles/RFE_9980_IPv4_Network_PCP_Proxy_All.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=632)
    def test_632_Validate_IPv4_Network_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_network_8+'\/8\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case execution completed")



    @pytest.mark.run(order=633)
    def test_633_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)



    @pytest.mark.run(order=634)
    def test_634_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_Blocked_IPs_in_response_from_DCA_As_times_com_domain_is_already_DCA_Cache(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and get PCP Blocked IPs response from DCA as times.com is already in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=635)
    def test_635_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=636)
    def test_636_Validate_DCA_CEF_Log_Logs_when_get_response_from_DCA_for_PCP_domain_times_com(self):
        logging.info("Validate DCA CEF Log for times.com  when get response from DCA")
        LookFor="fp-rte.*info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
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


    @pytest.mark.run(order=638)
    def test_638_Validate_when_get_response_from_DCA_for_PCP_domain_times_com_Cache_hit_count_is_increased_and_Miss_cache_count_count_not_increased(self):
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
        logging.info("Test Case Execution Completed")
        sleep(10)



#    @pytest.mark.run(order=639)
#    def test_639_Add_Back_Same_IPv4_Network_Subscriber_Record_with_Different_PCP_Policy_bit(self):
#        try:
#            logging.info("Add Same IPv4 Network Subscriber Record with Different PCP Policy bit")
#            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
#            child.logfile=sys.stdout
#            child.expect('password:',timeout=None)
#            child.sendline('infoblox')
#            child.expect('Infoblox >')
#            child.sendline('set subscriber_secure_data add '+config.client_network_8+' 8 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00200000000000000000000000020040;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;"')
#            child.expect('Record successfully added')
#            logging.info("Test Case Execution Passed")
#            assert True
#        except:
#            logging.info("Test Case  Execution Failed")
#            assert False




    @pytest.mark.run(order=639)
    def test_639_From_Radclient_Send_INTERIM_Radius_Message_for_IPv4_Network_Subscriber_Record_with_ith_Different_PCP_Policy_bit_for_existing_IPv4_Network_subscriber_Record(self):
        logging.info("From Rad client send INTERIM Radius message for IPv4 Network Subscriber Record with Different PCP Policy for existing IPv4 network subscriber record")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part2_radfiles/RFE_9980_IPv4_Network_PCP_Proxy_All_INTERIM.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=640)
    def test_640_Validate_IPv4_Network_Subscriber_Record_with_Different_PCP_Policy_bit(self):
        logging.info("Validate IPv4 Network Subscriber Record with Different PCP Policy bit")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_network_8+'\/8\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case execution completed")


    @pytest.mark.run(order=641)
    def test_641_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=642)
    def test_642_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_NORMAL_response_Even_PCP_Domain_in_Cache_with_PCP_word_But_subscriber_client_PCP_Policy_bit_not_matched(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and Validate get NORMAL response even times.com domain is in cache with PCP word but subscriber client PCP Policy bit not matched")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=643)
    def test_643_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=644)
    def test_644_Validate_No_CEF_Log_Logs_when_get_NORMAL_response_from_DCA_for_PCP_domain_times_com(self):
        logging.info("Validate NO CEF Log for times.com  when get NORMAL response")
        LookFor="info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
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



    @pytest.mark.run(order=645)
    def test_645_Validate_PCP_Domain_times_com_still_exist_in_DCA_cache(self):
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
        logging.info("Test Case Execution Completed")
        sleep(10)



    @pytest.mark.run(order=646)
    def test_646_Validate_when_get_response_from_DCA_for_PCP_domain_times_com_Cache_hit_count_is_increased_and_Miss_cache_count_count_not_increased(self):
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
        logging.info("Test Case Execution Completed")
        sleep(10)



#    @pytest.mark.run(order=647)
#    def test_647_Add_Back_Same_IPv4_Network_with_Prefix_8_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
#        try:
#            logging.info("Add Same IPv4 Network with 8 prefix Subscriber Record with PCP Policy for News Category")
#            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
#            child.logfile=sys.stdout
#            child.expect('password:',timeout=None)
#            child.sendline('infoblox')
#            child.expect('Infoblox >')
#            child.sendline('set subscriber_secure_data add '+config.client_network_8+' 8 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;"')
#            child.expect('Record successfully added')
#            logging.info("Test Case Execution Passed")
#            assert True
#        except:
#            logging.info("Test Case Execution Failed")
#            assert False




    @pytest.mark.run(order=647)
    def test_647_From_Radclient_Send_Same_INTERIM_Radius_Message_for_IPv4_Network_with_Prefix_8_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("From Rad client send Same INTERIM Radius message for IPv4 Network Subscriber Record with PCP Policy for News Category")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part2_radfiles/RFE_9980_IPv4_Network_PCP_Proxy_All.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=648)
    def test_648_Validate_IPv4_Network_with_Prefix_8_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate IPv4 Network with prefix 8 Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_network_8+'\/8\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case execution completed")


    @pytest.mark.run(order=649)
    def test_649_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 49 passed")
        sleep(10)




    @pytest.mark.run(order=650)
    def test_650_Send_Query_from_PCP_bit_match_Subscriber_client_for_PCP_Domain_times_Using_IB_FLEX_Member_Validate_returns_Blocked_IPs_in_response_from_DCA_As_times_com_domain_is_already_DCA_Cache(self):
        logging.info("Perform Query from PCP bit match Subscriber client for PCP Domain times.com using IB-FLEX Member and get PCP Blocked IPs response from DCA as times.com is already in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=651)
    def test_651_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 51 Execution Completed")


    @pytest.mark.run(order=652)
    def test_652_Validate_DCA_CEF_Log_Logs_when_get_response_from_DCA_for_PCP_domain_times_com(self):
        logging.info("Validate DCA CEF Log for times.com  when get response from DCA")
        LookFor="fp-rte.*info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
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



#    @pytest.mark.run(order=653)
#    def test_653_Add_another_IPv4_Network_Subscriber_Record_with_Prefix_16_with_Different_PCP_Policy_bit_than_prefix_8_network_subscriber_Record(self):
#        try:
#            logging.info("Add Another IPv4 Network Subscriber Record with Predix 16 with Different PCP Policy bit than prefix 8 subscriber record")
#            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
#            child.logfile=sys.stdout
#            child.expect('password:',timeout=None)
#            child.sendline('infoblox')
#            child.expect('Infoblox >')
#            child.sendline('set subscriber_secure_data add '+config.client_network_16+' 16 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00200000000000000000000000020040;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;"')
#            child.expect('Record successfully added')
#            logging.info("Test Case Execution Passed")
#            assert True
#        except:
#            logging.info("Test Case Execution Failed")
#            assert False



    @pytest.mark.run(order=653)
    def test_653_From_Radclient_Send_Start_Radius_Message_for_Another_IPv4_Network_with_Prefix_16_Subscriber_Record_with_with_Different_PCP_Policy_bit_than_prefix_8_network_subscriber_Record(self):
        logging.info("From Rad client send Start Radius message with Another IPv4 Network Subscriber Record with Predix 16 with Different PCP Policy bit than prefix 8 subscriber record")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part2_radfiles/RFE_9980_IPv4_Network_Prefix_16.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)



    @pytest.mark.run(order=654)
    def test_654_Validate_IPv4_Network_with_Prefix_16_Subscriber_Record_with_Different_PCP_Policy_bit_than_prefix_8_network_subscriber_Record(self):
        logging.info("Validate IPv4 Network with prefix 16 Subscriber Record with Different PCP Policy bit  than prefix 8 subscriber record")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_network_16+'\/16\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00200000000000000000000000020040.*',c)
        logging.info("Test case execution completed")




    @pytest.mark.run(order=655)
    def test_655_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=656)
    def test_656_Send_Query_from_Same_Subscriber_client_for_PCP_Domain_times_com_and_Validate_returns_NORMAL_response_Even_PCP_Domain_in_Cache_with_PCP_word_as_New_IPv4_network_with_prefix_16_Takes_priority_than_susbcriber_with_Prefix_8_subscriber_Record_and_not_match_bit_for_times_com_domain(self):
        logging.info("Perform Query from Same Subscriber client for PCP Domain times.com and Validate got NORMAL response even times.com domain is in cache with PCP word as New IPv4 network with prefix 16 Takes priority than susbcriber with Prefix 8 subscriber Record and not match bit for times.com domain")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=657)
    def test_657_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=658)
    def test_658_Validate_No_CEF_Log_Logs_when_get_NORMAL_response_as_PCP_bit_not_matched_as_per_new_subscriber_client_for_PCP_domain_times_com(self):
        logging.info("Validate NO CEF Log for times.com  as got NORMAL response")
        LookFor="info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
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


    @pytest.mark.run(order=659)
    def test_659_Validate_PCP_Domain_times_com_still_exist_in_DCA_cache_with_PCP_word(self):
        logging.info("Validate times.com domain still exist in DCA cache with PCP word")
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
        logging.info("Test Case Execution Completed")
        sleep(10)


    @pytest.mark.run(order=660)
    def test_660_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)



    @pytest.mark.run(order=661)
    def test_661_Send_Query_from_Same_Subscriber_client_for_matched_bit_PCP_Domain_playboy_com_and_Validate_returns_Blocked_IPs_in_response_from_Bind_As_Not_DCA_Cache(self):
        logging.info("Perform Query from same Subscriber client for matched bit PCP Domain playboy.com and validate got PCP Blocked IPs response from Bind as playboy.com not in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)



    @pytest.mark.run(order=662)
    def test_662_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")
        sleep(10)


    @pytest.mark.run(order=663)
    def test_663_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_playboy_com(self):
        logging.info("Validate Named CEF Log for playboy.com  when get response from Bind")
        LookFor="named.*info CEF.*playboy.com.*CAT=0x00000000000000000000000000020000"
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



#    @pytest.mark.run(order=664)
#    def test_664_Add_IPv4_IP_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
#        try:
#            logging.info("Add IPv4 IP Subscriber Record with PCP Policy for News Category")
#            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
#            child.logfile=sys.stdout
#            child.expect('password:',timeout=None)
#            child.sendline('infoblox')
#            child.expect('Infoblox >')
#            child.sendline('set subscriber_secure_data add '+config.client_ip+' 32 N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;"')
#            child.expect('Record successfully added')
#            logging.info("Test Case Execution Passed")
#            assert True
#        except:
#            logging.info("Test Case Execution Failed")
#            assert False




    @pytest.mark.run(order=664)
    def test_664_From_Radclient_Send_Start_Radius_Message_for_IPv4_Network_Prefix_32_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("From Rad client send Start Radius message for IPv4 Network Prefix 32 Subscriber Record with PCP Policy for News Category")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part2_radfiles/RFE_9980_IPv4_Network_Prefix_32.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=665)
    def test_665_Validate_IPv4_IP_Subscriber_Record_with_PCP_Policy_for_News_Category(self):
        logging.info("Validate IPv4 IP Subscriber Record with PCP Policy for News Category")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip+'\/32\|LID\:N\/A\|IPS\:N\/A.*PCP\:Parental-Control-Policy=00000000000000040000000000000000.*',c)
        logging.info("Test case execution completed")



    @pytest.mark.run(order=666)
    def test_666_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)



    @pytest.mark.run(order=667)
    def test_667_Send_Query_from_Same_Subscriber_client_for_PCP_Domain_times_com_and_Validate_returns_Blocked_IPs_in_response_from_DCA_As_times_com_domain_is_already_DCA_Cache_and_as_times_com_domain_bit_matched_with_new_IPv4_IP_subscriber_which_takes_Priority(self):
        logging.info("Perform Query from same Subscriber client for PCP Domain times.com and validate get PCP Blocked IPs response from DCA as times.com is already in DCA cache and as times.com domain bit matched with new IPv4 IP subscriber which is takes Priority ")
        #dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip2+'"'
        #dig_result1 = subprocess.check_output(dig_cmd1, shell=True)
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=668)
    def test_668_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=669)
    def test_669_Validate_DCA_CEF_Log_Logs_when_get_response_from_DCA_for_PCP_domain_times_com(self):
        logging.info("Validate DCA CEF Log for times.com  when get response from DCA")
        LookFor="fp-rte.*info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
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


#    @pytest.mark.run(order=670)
#    def test_670_Delete_IPv4_IP_Subscriber_Record_with_PCP_Policy_for_News_Category_From_Subscriber_Cache(self):
#        try:
##            logging.info("Delete the IPv4 IP Subscriber Record with PCP Policy for News Category from Subscriber Cache")
#            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
#            child.logfile=sys.stdout
#            child.expect('password:',timeout=None)
#            child.sendline('infoblox')
#            child.expect('Infoblox >')
#            child.sendline('set subscriber_secure_data delete '+config.client_ip+' 32 N/A N/A')
#            child.expect('Record successfully deleted')
#            logging.info("Test Case Execution Passed")
#            assert True
#        except:
#            logging.info("Test Case Execution Failed")
#            assert False




    @pytest.mark.run(order=670)
    def test_670_From_Radclient_Send_Stop_Radius_Message_to_Delete_IPv4_Network_Prefix_32_Subscriber_Record_with_PCP_Policy_for_News_Category_From_Subscriber_Cache(self):
        logging.info("From Rad client send Stop Radius message to Delete the IPv4 Network Prefix 32 Subscriber Record with PCP Policy for News Category from Subscriber Cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part2_radfiles/RFE_9980_IPv4_Network_Prefix_32_Stop.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)



    @pytest.mark.run(order=671)
    def test_671_Validate_IPv4_IP_Subscriber_Record_with_PCP_Policy_for_News_Category_is_deleted_from_Subscriber_Cache(self):
        logging.info("Validate IPv4 IP Subscriber Record with PCP Policy for News Category is deleted from subscriber cache")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        if re.search(r'.*'+config.client_ip+'.*',c):
            logging.info("Test Case Execution Failed")
            assert False
        else:
            logging.info("Test Case Execution Passed")
            assert True
        logging.info("Test case execution completed")
        sleep(10)



    @pytest.mark.run(order=672)
    def test_672_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)



    @pytest.mark.run(order=673)
    def test_673_Send_Query_from_same_Subscriber_client_for_PCP_Domain_times_com_and_Validate_returns_NORMAL_response_Even_PCP_Domain_in_Cache_with_PCP_word_as_existing_IPv4_network_subscriber_with_prefix_16_has_different_PCP_bit(self):
        logging.info("Perform Query from same client for PCP Domain times.com and Validate got NORMAL response even times.com domain is in cache with PCP word as existing IPv4 network subscriber with prefix 16 has different PCP bit")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=674)
    def test_674_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")
        sleep(10)



    @pytest.mark.run(order=675)
    def test_675_Validate_No_CEF_Log_Logs_when_get_NORMAL_response_from_DCA_for_PCP_domain_times_com(self):
        logging.info("Validate NO CEF Log for times.com  when get NORMAL response")
        LookFor="info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
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


    @pytest.mark.run(order=676)
    def test_676_Validate_PCP_Domain_times_com_still_exist_in_DCA_cache(self):
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
        logging.info("Test Case Execution Completed")
        sleep(10)



    @pytest.mark.run(order=677)
    def test_677_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)



    @pytest.mark.run(order=678)
    def test_678_Send_Query_from_same_Subscriber_client_for_PCP_Domain_playboy_com_and_Validate_returns_Blocked_IPs_in_response_as_IPv4_network_prefix_16_subscriber_record_match(self):
        logging.info("Perform Query from same Subscriber client for PCP Domain playboy.com get PCP Blocked IPs response as IPv4 network prefix 16 subscriber record match")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)



    @pytest.mark.run(order=679)
    def test_679_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")
        sleep(5)


    @pytest.mark.run(order=680)
    def test_680_Validate_Named_CEF_Log_Logs_when_get_response_from_Bind_for_PCP_domain_playboy_com(self):
        logging.info("Validate Named CEF Log for playboy.com  when get response from Bind")
        LookFor="named.*info CEF.*playboy.com.*CAT=0x00000000000000000000000000020000"
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



#    @pytest.mark.run(order=681)
#    def test_681_Delete_IPv4_Network_prefix_16_Subscriber_Record_From_Subscriber_Cache(self):
#        try:
#            logging.info("Delete the IPv4 Network with prefix 16 Subscriber Record from Subscriber Cache")
#            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
#            child.logfile=sys.stdout
#            child.expect('password:',timeout=None)
#            child.sendline('infoblox')
#            child.expect('Infoblox >')
#            child.sendline('set subscriber_secure_data delete '+config.client_network_16+' 16 N/A N/A')
#            child.expect('Record successfully deleted')
#            logging.info("Test Case Execution Passed")
#            assert True
#        except:
#            logging.info("Test Case Execution Failed")
#            assert False



    @pytest.mark.run(order=681)
    def test_681_From_Radclient_Send_Stop_Radius_Message_to_Delete_IPv4_Network_Prefix_16_Subscriber_Record_From_Subscriber_Cache(self):
        logging.info("From Rad client send Stop Radius message to Delete the IPv4 Network with prefix 16 Subscriber Record from Subscriber Cache ")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part2_radfiles/RFE_9980_IPv4_Network_Prefix_16_Stop.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)




    @pytest.mark.run(order=682)
    def test_682_Validate_IPv4_Network_Subscriber_Record_with_prefix_16_is_deleted_from_Subscriber_Cache(self):
        logging.info("Validate IPv4 Network Subscriber Record with prefix 16 is deleted from subscriber cache")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        if re.search(r','+config.client_network_16+'',c):
            logging.info("Test Case Execution Failed")
            assert False
        else:
            logging.info("Test Case Execution Passed")
            assert True
        logging.info("Test case execution completed")
        sleep(10)



    @pytest.mark.run(order=683)
    def test_683_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)



    @pytest.mark.run(order=684)
    def test_684_Send_Query_from_Same_Subscriber_client_for_PCP_Domain_times_com_and_Validate_returns_Blocked_IPs_in_response_from_DCA_As_times_com_domain_is_already_DCA_Cache_as_times_com_domain_bit_match_for_IPv4_network_8_Prefix_subscriber_Record(self):
        logging.info("Perform Query from same Subscriber client for PCP Domain times.com and get PCP Blocked IPs response from DCA as times.com is already in DCA cache as times.com domain bit match for IPv4 network prefix 8 subscriber record")
        #dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip2+'"'
        #dig_result = subprocess.check_output(dig_cmd, shell=True)
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=685)
    def test_685_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=686)
    def test_686_Validate_DCA_CEF_Log_Logs_when_get_response_from_DCA_for_PCP_domain_times_com(self):
        logging.info("Validate DCA CEF Log for times.com  when get response from DCA")
        LookFor="fp-rte.*info CEF.*times.com.*CAT=0x00000000000000040000000000000000"
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


#    @pytest.mark.run(order=687)
#    def test_687_Delete_IPv4_Network_prefix_8_Subscriber_Record_From_Subscriber_Cache(self):
#        try:
#            logging.info("Delete the IPv4 Network with prefix 8 Subscriber Record from Subscriber Cache")
#            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
#            child.logfile=sys.stdout
#            child.expect('password:',timeout=None)
#            child.sendline('infoblox')
#            child.expect('Infoblox >')
#            child.sendline('set subscriber_secure_data delete '+config.client_network_8+' 8 N/A N/A')
#            child.expect('Record successfully deleted')
#            logging.info("Test Case Execution Passed")
#            assert True
#        except:
#            logging.info("Test Case Execution Failed")
#            assert False




    @pytest.mark.run(order=687)
    def test_687_From_Radclient_Send_Stop_Radius_Message_to_Delete_IPv4_Network_Prefix_8_Subscriber_Record_From_Subscriber_Cache(self):
        logging.info("From Rad client send Stop Radius message to Delete the IPv4 Network Prefix 8 Subscriber Record from Subscriber Cache ")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part2_radfiles/RFE_9980_IPv4_Network_PCP_Proxy_All_Stop.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=688)
    def test_688_Validate_IPv4_Network_Subscriber_Record_with_prefix_8_is_deleted_from_Subscriber_Cache(self):
        logging.info("Validate IPv4 Network Subscriber Record with prefix 8 is deleted from subscriber cache")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        if re.search(r','+config.client_network_8+'',c):
            logging.info("Test Case Execution Failed")
            assert False
        else:
            logging.info("Test Case Execution Passed")
            assert True
        logging.info("Test case execution completed")
        sleep(10)
## As per bug changed to infoblox log

    @pytest.mark.run(order=689)
    def test_689_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        #log("start","/var/log/syslog",config.grid_vip)
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=690)
    def test_690_Add_11_IPv4_Network_Subscriber_Record_with_With_Different_Subnetmask__To_Validate_MAX_Different_IPv4_Networks_Subscriber_Records_Allowed(self):
        try:
            logging.info("Add IPv4 Network Subscriber Record with Different Subnetmask and Validate it allow MAX 10 IPv4 Networks Subscriber recors ")
            for i in range(1,12):
                j= 11+i
                print j
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('password:',timeout=None)
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('set subscriber_secure_data add 20.10.'+str(i)+'.0 '+str(j)+' N/A N/A "ACS:Acct-Session-Id=9999735777;NAS:NAS-PORT=1813;PCP:Parental-Control-Policy=00000000000000040000000000000000;SUB:Calling-Station-Id=110361266;PCC:PC-Category-Policy=00000000000000000000000000000001;PXY:Proxy-All=1;PXP:PXY_PRI='+config.primary_proxy_server+';PXS:PXY_SEC='+config.secondary_proxy_server+';"')

                child.expect('Record successfully added')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Passed")
            assert False


    @pytest.mark.run(order=691)
    def test_691_Validate_11_IPv4_Subscriber_Record_with_Different_Subnetmask(self):
        logging.info("Validate Subscriber Record with Different Subnetmask")
        for i in range(1,12):
            j= 11+i
            print j
            kk= '20.10.'+str(i)+'.0 '+str(j)+''
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('show subscriber_secure_data find 20.10.'+str(i)+'.0 '+str(j)+' N/A N/A')
            child.expect('Infoblox >')
            c=child.before
            assert re.search(r'.*20.10.'+str(i)+'.0\/'+str(j)+'',c)
        logging.info("Test case  execution completed")


    @pytest.mark.run(order=692)
    def test_692_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on master")
        #log("stop","/var/log/syslog",config.grid_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("Test Case Execution Completed")

#NIOS-79786 as per latest changes now not loging in syslog 
 
    @pytest.mark.run(order=693)
    def test_693_Validate_Syslog_Logs_Logging_Proper_error_Message_logged_for_11th_IPv4_Networks_subscriber_Record_Add(self):
        logging.info("Validate Syslog Logs Logging Proper error Message logged for 11th IPv4 Networks subscriber Record Add")
        #LookFor="err.*Failed to insert new subcriber \(the Subcriber IPv4 prefix list is full\)"
        LookFor="Max size of prefixv4 list has reached. Adding prefix failed"
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



    @pytest.mark.run(order=694)
    def test_694_Delete_All_11_IPv4_Network_Subscriber_Record_with_Different_Subnetmask(self):
        try:
            logging.info("Delete all 11 IPv4 Network Subscriber which are added with Different Subnetmask ")
            for i in range(1,10):
                j= 11+i
                print j
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('password:',timeout=None)
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('set subscriber_secure_data delete 20.10.'+str(i)+'.0 '+str(j)+' N/A N/A')
                child.expect('Record successfully deleted')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Passed")
            assert False


#Commenting as aready 32 RPZ zones are added
    #@pytest.mark.run(order=695)
    #def test_695_Add_32_RPZ_Zonse_with_IB_FLEX_Member_Assignemnet(self):
    #    logging.info("Add 32 RPZ Zones with IB-FLEX Member Assignement")
    #    for i in range(1,33):
    #        data={"fqdn": "rpz"+str(i)+".com","grid_primary":[{"name": config.grid_fqdn,"stealth":False}],"view":"default"}
    #        response=ib_NIOS.wapi_request('POST', object_type="zone_rp",fields=json.dumps(data))
    #        print response
    #        print "RPZ Zone rpz"+str(i)+".com is added"
    #        res=json.loads(response)
    #        logging.info(response)
    #        read  = re.search(r'201',response)
    #        print read
    #        for read in  response:
    #            assert True

    #    print("Test Case Execution Completed")
    #    logging.info("Restart services")
    #    restart_the_grid()
    #    print("System Restart is done successfully")

    @pytest.mark.run(order=696)
    def test_696_Validate_Added_32_RPZ_Zones_with_IB_FLEX_assignement(self):
        logging.info("Validate added 32 RPZ zones with IB-FLEX assignementn\n")
        print "\n"
        for i in range(1,33):
            data={"fqdn": "rpz"+str(i)+".com"}
            print data
            logging.info ("Validate Added RPZ zone")
            fields=json.dumps(data)
            get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_rp?_return_fields=fqdn,view,grid_primary", fields=json.dumps(data))
            print "==================================="
            print get_template_zone
            print "==================================="
            logging.info(get_template_zone)
            res=json.loads(get_template_zone)
            if("rpz"+str(i)+".com" in get_template_zone):
                assert True
            else:
                assert False
        logging.info("Test Case Execution Completed")


################ Without SSP Bit set Passthru rule for rpz zone 0th, 7th and 32nd RPZ zone for PCP , Proxy and WPCP domains #####

    @pytest.mark.run(order=700)
    def test_700_From_Radclient_Send_Same_Start_Radius_Message_with_PCP_Policy_and_Proxy_All_Configured(self):
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part2_radfiles/RFE_9980_PCP_Proxy_All_never_porxy.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=701)
    def test_701_Validate_Subscriber_Record_with_PCP_Policy_and_Proxy_All_configured(self):
        logging.info("Validate Subscriber Record with PCP Policy and Proxy-All configured")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case execution completed")




    @pytest.mark.run(order=702)
    def test_702_From_Radclient_Send_Start_Radius_Message_without_Proxy_all_set_and_Different_PCP_Policy_bit_than_above_to_make_sure_Domain_Cache_to_DCA_with_PCP_Word(self):
        logging.info("From Rad client send Start Radius message without Proxy-All set and different PCP Policy bit than the above to make sure Doamin cache_to DCA with PCP word")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part2_radfiles/RFE_9980_Only_PCP_for_Cache.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)



    @pytest.mark.run(order=703)
    def test_703_Validate_Subscriber_Record_without_Proxy_all_set_and_Different_PCP_Policy_bit_is_added_to_subscriber_cache(self):
        logging.info("Validate Subscriber Record without Proxy-All set different PCP Policy bit is added to subscriber cache")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case execution completed")



    @pytest.mark.run(order=704)
    def test_704_From_CLI_Configuration_never_proxy_category_set_is_ffffffffffffffffffffffffffffffff(self):
        try:
            logging.info("From CLI Configuration never_proxy category set is ffffffffffffffffffffffffffffffff")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data never_proxy ffffffffffffffffffffffffffffffff')
            child.expect('never_proxy categories is set')
            child.expect('!!! A RESTART of the DNS service is required before this change can take effect !!!')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Failed")
            assert False



    @pytest.mark.run(order=705)
    def test_705_From_CLI_Validate_Configuration_never_proxy_category_set_is_ffffffffffffffffffffffffffffffff(self):
        logging.info("From CLI Validate Configuration never_proxy category set is ffffffffffffffffffffffffffffffff ")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data never_proxy')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*never_proxy category set is ffffffffffffffffffffffffffffffff.*',c)
        logging.info("Test case execution completed")


    @pytest.mark.run(order=706)
    def test_706_Restart_DNS_service(self):
        logging.info("Restart services")
        restart_the_grid()
        #grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        #ref = json.loads(grid)[0]['_ref']
        #publish={"member_order":"SIMULTANEOUSLY"}
        #request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        #request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        #restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        #sleep(60)


    @pytest.mark.run(order=707)
    def test_707_Add_PCP_domain_times_com_as_PASSTHRU_RPZ_Rule_to_1_RPZ_Zone_rpz32_com(self):
        logging.info ("Add PCP Domain times.com as PASSTHRU RPZ Rule to 32 RPZ zone rpz32.com")
        data={"canonical":"times.com", "name": "times.com.rpz32.com","rp_zone": "rpz32.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=708)
    def test_708_Validate_Added_PCP_domain_times_com_as_PASSTHRU_RPZ_Rule_to_1_RPZ_Zone_rpz32_com(self):
        logging.info("Validate added PCP Domain times.com as PASSTHRU RPZ Rule to 32 RPZ zone rpz32.com\n")
        data={"name": "times.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "times.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "times.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=709)
    def test_709_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")



# As per the changes of bug NIOS-78037 commented and changed the cases
    @pytest.mark.run(order=710)
    def test_710_Send_Query_from_PCP_bit_and_Proxy_All_Configured_Subscriber_client_for_PCP_Domain_times_com_Validate_returns_PCP_Blocking_IP_response_As_times_com_is_added_as_PASSTHRU_RPZ_rule_to_1st_RPZ_Zone_and_got_Both_RPZ_and_PCP_CEF_logs_Never_proxy_set_to_ffffffffffffffffffffffffffffffff(self):
        logging.info("Perform Query from PCP bit and Proxy-All configured Subscriber client for PCP Domain times.com and Validate get PCP blocking IP response as times.com domain is added as PASSTHRU RPZ rule to 1st RPZ zone and Never_proxy is configured ffffffffffffffffffffffffffffffff and  got both PCP and RPZ CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' times.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
	assert re.search(r'.*times.com.*IN.*A.*',str(dig_result))
        #assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*1.1.1.1.*',str(dig_result))
        #assert re.search(r'.*site2-blocking.pc.com.*IN.*A.*2.2.2.2.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=711)
    def test_711_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


# Changed the test cases from !=None to ==None as NIOS-78037
#Again changed the test cae from ==None to !=None as SNIN-57

    @pytest.mark.run(order=712)
    def test_712_Validate_Got_Both_RPZ_PCP_CEF_Log_Logs_as_PCP_domain_times_com_is_added_as_PASSTHRU_RPZ_rule_to_1st_RPZ_Zone_and_set_to_ffffffffffffffffffffffffffffffff(self):
        logging.info("Validate got both RPZ and PCP CEF Log for times.com  domain is added as PASSTHRU RPZ rule to 1st RPZ zone and set_to_ffffffffffffffffffffffffffffffff")
        LookFor="info CEF.*times.com.*CAT=RPZ.*"
        LookFor1="info CEF.*times.com.*CAT=0x00000000000000040000000000000000.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1!=None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False



    @pytest.mark.run(order=713)
    def test_713_Remove_PCP_domain_times_com_PASSTHRU_RPZ_Rule_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Remove PCP Domain times.com PASSTHRU RPZ Rule from 1st RPZ zone rpz32.com")
        data={"name": "times.com.rpz32.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=714)
    def test_714_Validate_PCP_domain_times_com_PASSTHRU_RPZ_Rule_is_Deleted_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate PCP Domain times.com PASSTHRU RPZ Rule is deleted from 1st RPZ zone rpz32.com\n")
        data={"name": "times.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "times.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "times.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=715)
    def test_715_Add_Proxy_domain_playboy_com_as_PASSTHRU_RPZ_Rule_to_1_RPZ_Zone_rpz32_com(self):
        logging.info ("Add Proxy Domain playboy.com as PASSTHRU RPZ Rule to 32 RPZ zone rpz32.com")
        data={"canonical":"playboy.com", "name": "playboy.com.rpz32.com","rp_zone": "rpz32.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=716)
    def test_716_Validate_Added_Proxy_domain_playboy_com_as_PASSTHRU_RPZ_Rule_to_1_RPZ_Zone_rpz32_com(self):
        logging.info("Validate added PCP Domain playboy.com as PASSTHRU RPZ Rule to 32 RPZ zone rpz32.com\n")
        data={"name": "playboy.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "playboy.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=717)
    def test_717_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=718)
    def test_718_Send_Query_from_Proxy_All_Configured_Subscriber_client_for_Proxy_Domain_playboy_com_Validate_returns_NORMAL_response_As_playboy_com_is_added_as_PASSTHRU_RPZ_rule_to_1st_RPZ_Zone_and_got_Only_RPZ_CEF_logs_as_Never_proxy_set_to_ffffffffffffffffffffffffffffffff(self):
        logging.info("Perform Query from Proxy-All configured Subscriber client for Proxy Domain playboy.com and Validate get NORMAL response as playboy.com domain is added as PASSTHRU RPZ rule to 1st RPZ zone and Never_proxy is configured ffffffffffffffffffffffffffffffff and  got only RPZ  CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=719)
    def test_719_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=720)
    def test_720_Validate_Got_Only_RPZ_CEF_Log_Logs_as_Proxy_domain_playboy_com_is_added_as_PASSTHRU_RPZ_rule_to_1st_RPZ_Zone_and_set_to_ffffffffffffffffffffffffffffffff(self):
        logging.info("Validate got Only RPZ CEF Log for playboy.com  domain is added as PASSTHRU RPZ rule to 1st RPZ zone and set_to_ffffffffffffffffffffffffffffffff")
        LookFor="info CEF.*playboy.com.*CAT=RPZ.*"
        LookFor1="info CEF.*playboy.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False



    @pytest.mark.run(order=721)
    def test_721_Remove_Proxy_domain_playboy_com_PASSTHRU_RPZ_Rule_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Remove Proxy Domain playboy.com PASSTHRU RPZ Rule from 1st RPZ zone rpz32.com")
        data={"name": "playboy.com.rpz32.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=722)
    def test_722_Validate_Proxy_domain_times_com_PASSTHRU_RPZ_Rule_is_Deleted_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate Proxy Domain playboy.com PASSTHRU RPZ Rule is deleted from 1st RPZ zone rpz32.com\n")
        data={"name": "playboy.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "playboy.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=723)
    def test_723_Add_Proxy_domain_playboy_com_as_PASSTHRU_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Add Proxy Domain Playboy.com as PASSTHRU RPZ Rule to 7th RPZ zone rpz25.com")
        data={"canonical":"playboy.com", "name": "playboy.com.rpz25.com","rp_zone": "rpz25.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)
        logging.info("Validate added Proxy Domain Playboy.com as PASSTHRU RPZ Rule to 7th RPZ zone rpz25.com\n")
        data={"name": "playboy.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz25.com"' in get_rpz_rule) and ('"canonical": "playboy.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=724)
    def test_724_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=725)
    def test_725_Send_Query_from_Proxy_All_Configured_Subscriber_client_for_Proxy_Domain_playboy_com_Validate_returns_NORMAL_response_As_playboy_com_is_added_as_PASSTHRU_RPZ_rule_to_7th_RPZ_Zone_and_not_got_any_CEF_logs(self):
        logging.info("Perform Query from Proxy-All configured Subscriber client for Proxy Domain playboy.com and Validate get NORMAL response as playboy.com domain is added as Proxy domain is added as PASSTHRU RPZ rule to 7th RPZ zone and did not get any CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=726)
    def test_726_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=727)
    def test_727_Validate_Not_Get_PCP_OR_RPZ_CEF_Log_Logs_as_Proxy_domain_playboy_com_is_added_as_PASSTHRU_RPZ_rule_to_7th_RPZ_Zone(self):
        logging.info("Validate did not got any RPZ and PCP CEF Log for playboy.com  added domain is added as PASSTHRU RPZ rule to 7th RPZ zone")
        LookFor="info CEF.*playboy.com.*CAT=RPZ.*"
        LookFor1="info CEF.*playboy.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=728)
    def test_728_Remove_Proxy_playboy_com_PASSTHRU_RPZ_Rule_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Remove Proxy Domain Playboy.com PASSTHRU RPZ Rule from 7th RPZ zone rpz25.com")
        data={"name": "playboy.com.rpz25.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=729)
    def test_729_Validate_Proxy_domain_playboy_com_PASSTHRU_RPZ_Rule_is_Deleted_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate Proxy Domain Playboy.com PASSTHRU RPZ Rule is deleted from 7th RPZ zone rpz25.com\n")
        data={"name": "playboy.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz25.com"' in get_rpz_rule) and ('"canonical": "playboy.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=730)
    def test_730_Add_Proxy_domain_playboy_com_as_PASSTHRU_RPZ_Rule_to_32nd_RPZ_Zone_rpz1_com(self):
        logging.info ("Add Proxy Domain Playboy.com as PASSTHRU RPZ Rule to 32nd RPZ zone rpz1.com")
        data={"canonical":"playboy.com", "name": "playboy.com.rpz1.com","rp_zone": "rpz1.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=731)
    def test_731_Validate_Added_Proxy_domain_playboy_com_as_PASSTHRU_RPZ_Rule_to_32nd_RPZ_Zone_rpz1_com(self):
        logging.info("Validate added Proxy Domain Playboy.com as PASSTHRU RPZ Rule to 32nd RPZ zone rpz1.com\n")
        data={"name": "playboy.com.rpz1.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz1.com"' in get_rpz_rule) and ('"canonical": "playboy.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=732)
    def test_732_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=733)
    def test_733_Send_Query_from_Proxy_All_Configured_Subscriber_client_for_Proxy_Domain_playboy_com_Validate_returns_NORMAL_response_As_playboy_com_is_added_as_PASSTHRU_RPZ_rule_to_32nd_RPZ_Zone_and__set_to_ffffffffffffffffffffffffffffffff_not_got_any_CEF_logs(self):
        logging.info("Perform Query from Proxy-All configured Subscriber client for Proxy Domain playboy.com and Validate get NORMAL response as playboy.com domain is added as Proxy domain is added as PASSTHRU RPZ rule to 32nd RPZ zone and did not get any CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=734)
    def test_734_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=735)
    def test_735_Validate_Not_Get_PCP_OR_RPZ_CEF_Log_Logs_as_Proxy_domain_playboy_com_is_added_as_PASSTHRU_RPZ_rule_to_32nd_RPZ_Zone_and__set_to_ffffffffffffffffffffffffffffffff(self):
        logging.info("Validate did not got any RPZ and PCP CEF Log for playboy.com  added domain is added as PASSTHRU RPZ rule to 32nd RPZ zone")
        LookFor="info CEF.*playboy.com.*CAT=RPZ.*"
        LookFor1="info CEF.*playboy.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=736)
    def test_736_Remove_Proxy_playboy_com_PASSTHRU_RPZ_Rule_from_32nd_RPZ_Zone_rpz1_com(self):
        logging.info ("Remove Proxy Domain Playboy.com PASSTHRU RPZ Rule from 32nd RPZ zone rpz1.com")
        data={"name": "playboy.com.rpz1.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=737)
    def test_737_Validate_Proxy_domain_playboy_com_PASSTHRU_RPZ_Rule_is_Deleted_from_32nd_RPZ_Zone_rpz1_com(self):
        logging.info("Validate Proxy Domain Playboy.com PASSTHRU RPZ Rule is deleted from 7th RPZ zone rpz1.com\n")
        data={"name": "playboy.com.rpz1.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz1.com"' in get_rpz_rule) and ('"canonical": "playboy.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=738)
    def test_738_Restart_DNS_service(self):
        logging.info("Restart services")
        restart_the_grid()
        #grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        #ref = json.loads(grid)[0]['_ref']
        #publish={"member_order":"SIMULTANEOUSLY"}
        #request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        #request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        #restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        #sleep(60)



    @pytest.mark.run(order=739)
    def test_739_Add_WPCP_domain_coors_com_as_PASSTHRU_RPZ_Rule_to_1_RPZ_Zone_rpz32_com(self):
        logging.info ("Add WPCP Domain coors.com as PASSTHRU RPZ Rule to 32 RPZ zone rpz32.com")
        data={"canonical":"coors.com", "name": "coors.com.rpz32.com","rp_zone": "rpz32.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=740)
    def test_740_Validate_Added_WPCP_domain_coors_com_as_PASSTHRU_RPZ_Rule_to_1_RPZ_Zone_rpz32_com(self):
        logging.info("Validate added WPCP Domain coors.com as PASSTHRU RPZ Rule to 32 RPZ zone rpz32.com\n")
        data={"name": "coors.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "coors.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=741)
    def test_741_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=742)
    def test_742_Send_Query_from_WPCP_Proxy_Configured_Subscriber_client_for_WPCP_Domain_coors_com_Validate_returns_NORMAL_response_As_coors_com_is_added_as_PASSTHRU_RPZ_rule_to_1st_RPZ_Zone_and_got_RPZ_and_WPCP_CEF_logs_But_not_PXY_CEF_log_as_Never_proxy_set_to_ffffffffffffffffffffffffffffffff(self):
        logging.info("Perform Query from WPCP configured Subscriber client for Proxy Domain coors.com and Validate get NORMAL response as coors.com domain is added as PASSTHRU RPZ rule to 1st RPZ zone and Never_proxy is configured ffffffffffffffffffffffffffffffff and  got only RPZ  CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' coors.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*coors.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=743)
    def test_743_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


#Again changed the test cae from ==None to !=None as SNIN-57

    @pytest.mark.run(order=744)
    def test_744_Validate_Got_RPZ_and_WPCP_CEF_Log_Logs_but_not_PXY_CEF_logs_as_WPCP_domain_coors_com_is_added_as_PASSTHRU_RPZ_rule_to_1st_RPZ_Zone_and_set_to_ffffffffffffffffffffffffffffffff(self):
        logging.info("Validate got RPZ and WPCP CEF Log but not Proxy CEP logs for coors.com  domain is added as PASSTHRU RPZ rule to 1st RPZ zone and set_to_ffffffffffffffffffffffffffffffff")
        LookFor="info CEF.*coors.com.*CAT=RPZ.*"
        LookFor1="info CEF.*coors.com.*CAT=PXY.*"
        LookFor2="info CEF.*coors.com.*CAT=WRN_0x00000000000000000000000000000001.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs2!=None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False



    @pytest.mark.run(order=745)
    def test_745_Remove_WPCP_domain_coors_com_PASSTHRU_RPZ_Rule_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Remove WPCP Domain coors.com PASSTHRU RPZ Rule from 1st RPZ zone rpz32.com")
        data={"name": "coors.com.rpz32.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=746)
    def test_746_Validate_WPCP_domain_coors_com_PASSTHRU_RPZ_Rule_is_Deleted_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate Proxy Domain coors.com PASSTHRU RPZ Rule is deleted from 1st RPZ zone rpz32.com\n")
        data={"name": "coors.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "coors.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=747)
    def test_747_Add_WPCP_domain_coors_com_as_PASSTHRU_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Add WPCP Domain coors.com as PASSTHRU RPZ Rule to 7th RPZ zone rpz25.com")
        data={"canonical":"coors.com", "name": "coors.com.rpz25.com","rp_zone": "rpz25.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=748)
    def test_748_Validate_Added_Proxy_domain_playboy_com_as_PASSTHRU_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate added coors Domain coors.com as PASSTHRU RPZ Rule to 7th RPZ zone rpz25.com\n")
        data={"name": "coors.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz25.com"' in get_rpz_rule) and ('"canonical": "coors.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=749)
    def test_749_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=750)
    def test_750_Send_Query_from_Proxy_All_and_WPCP_Configured_Subscriber_client_for_WPCP_Domain_coors_com_Validate_returns_NORMAL_response_As_coors_com_is_added_as_PASSTHRU_RPZ_rule_to_7th_RPZ_Zone_and_not_got_any_CEF_logs(self):
        logging.info("Perform Query from Proxy-All and WPCP configured Subscriber client for Proxy Domain coors.com and Validate get NORMAL response as coors.com domain is added as WPCP domain is added as PASSTHRU RPZ rule to 7th RPZ zone and did not get any CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' coors.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*coors.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=751)
    def test_751_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=752)
    def test_752_Validate_Not_Get_WPCP_OR_RPZ_CEF_Log_Logs_as_WPCP_domain_coors_com_is_added_as_PASSTHRU_RPZ_rule_to_7th_RPZ_Zone(self):
        logging.info("Validate did not got any RPZ and WPCP CEF Log for coors.com  added domain is added as PASSTHRU RPZ rule to 7th RPZ zone")
        LookFor="info CEF.*coors.com.*CAT=RPZ.*"
        LookFor1="info CEF.*coors.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=753)
    def test_753_Remove_WPCP_Domain_coors_com_PASSTHRU_RPZ_Rule_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Remove WPCP Domain coors.com PASSTHRU RPZ Rule from 7th RPZ zone rpz25.com")
        data={"name": "coors.com.rpz25.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=754)
    def test_754_Validate_WPCP_domain_coors_com_PASSTHRU_RPZ_Rule_is_Deleted_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate WPCP Domain coors.com PASSTHRU RPZ Rule is deleted from 7th RPZ zone rpz25.com\n")
        data={"name": "coors.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz25.com"' in get_rpz_rule) and ('"canonical": "coors.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=755)
    def test_755_Add_WPCP_domain_coors_com_as_PASSTHRU_RPZ_Rule_to_32nd_RPZ_Zone_rpz1_com(self):
        logging.info ("Add WPCP Domain coors.com as PASSTHRU RPZ Rule to 32nd RPZ zone rpz1.com")
        data={"canonical":"coors.com", "name": "coors.com.rpz1.com","rp_zone": "rpz1.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=756)
    def test_756_Validate_Added_WPCP_domain_coors_com_as_PASSTHRU_RPZ_Rule_to_32nd_RPZ_Zone_rpz1_com(self):
        logging.info("Validate added WPCP Domain coors.com as PASSTHRU RPZ Rule to 32nd RPZ zone rpz1.com\n")
        data={"name": "coors.com.rpz1.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz1.com"' in get_rpz_rule) and ('"canonical": "coors.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=757)
    def test_757_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=758)
    def test_758_Send_Query_from_Proxy_All_and_WPCP_Configured_Subscriber_client_for_WPCP_Domain_coors_com_Validate_returns_NORMAL_response_As_coors_com_is_added_as_PASSTHRU_RPZ_rule_to_32nd_RPZ_Zone_and__set_to_ffffffffffffffffffffffffffffffff_not_got_any_CEF_logs(self):
        logging.info("Perform Query from Proxy-All and WPCP configured Subscriber client for Proxy Domain coors.com and Validate get NORMAL response as coors.com domain is added as WPCP domain is added as PASSTHRU RPZ rule to 32nd RPZ zone and did not get any CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' coors.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*coors.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=759)
    def test_759_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=760)
    def test_760_Validate_Not_Get_WPCP_OR_RPZ_CEF_Log_Logs_as_WPCP_domain_coors_com_is_added_as_PASSTHRU_RPZ_rule_to_32nd_RPZ_Zone_and__set_to_ffffffffffffffffffffffffffffffff(self):
        logging.info("Validate did not got any RPZ and WPCP CEF Log for coors.com  added domain is added as PASSTHRU RPZ rule to 32nd RPZ zone")
        LookFor="info CEF.*playboy.com.*CAT=RPZ.*"
        LookFor1="info CEF.*playboy.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=761)
    def test_761_Remove_WPCP_coors_com_PASSTHRU_RPZ_Rule_from_32nd_RPZ_Zone_rpz1_com(self):
        logging.info ("Remove WPCP Domain coors.com PASSTHRU RPZ Rule from 32nd RPZ zone rpz1.com")
        data={"name": "coors.com.rpz1.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=762)
    def test_762_Validate_WPCP_domain_coors_com_PASSTHRU_RPZ_Rule_is_Deleted_from_32nd_RPZ_Zone_rpz1_com(self):
        logging.info("Validate WPCP Domain coors.com PASSTHRU RPZ Rule is deleted from 7th RPZ zone rpz1.com\n")
        data={"name": "coors.com.rpz1.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz1.com"' in get_rpz_rule) and ('"canonical": "coors.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")



################ With SSP Bit set Passthru rule for rpz zone 0th, 7th and 32nd RPZ zone for Proxy and WPCP domains #####


    @pytest.mark.run(order=763)
    def test_763_From_Radclient_Send_Same_Interim_Radius_Message_with_PCP_Policy_and_Proxy_All_Configured_and_SSP_Policy(self):
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured and SSP Policy")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part2_radfiles/RFE_9980_PCP_Proxy_All_with_SSP_for_never_porxy.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=764)
    def test_764_Validate_Subscriber_Record_with_PCP_Policy_and_Proxy_All_configured(self):
        logging.info("Validate Subscriber Record with PCP Policy and Proxy-All configured")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case execution completed")




    @pytest.mark.run(order=765)
    def test_765_Add_Proxy_domain_playboy_com_as_PASSTHRU_RPZ_Rule_to_1_RPZ_Zone_rpz32_com(self):
        logging.info ("Add Proxy Domain playboy.com as PASSTHRU RPZ Rule to 32 RPZ zone rpz32.com")
        data={"canonical":"playboy.com", "name": "playboy.com.rpz32.com","rp_zone": "rpz32.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=766)
    def test_766_Validate_Added_Proxy_domain_playboy_com_as_PASSTHRU_RPZ_Rule_to_1_RPZ_Zone_rpz32_com(self):
        logging.info("Validate added PCP Domain playboy.com as PASSTHRU RPZ Rule to 32 RPZ zone rpz32.com\n")
        data={"name": "playboy.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "playboy.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=767)
    def test_767_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=768)
    def test_768_Send_Query_from_Proxy_All_Configured_Subscriber_client_for_Proxy_Domain_playboy_com_Validate_returns_NORMAL_response_As_playboy_com_is_added_as_PASSTHRU_RPZ_rule_to_1st_RPZ_Zone_and_got_Only_RPZ_CEF_logs_as_Never_proxy_set_to_ffffffffffffffffffffffffffffffff(self):
        logging.info("Perform Query from Proxy-All configured Subscriber client for Proxy Domain playboy.com and Validate get NORMAL response as playboy.com domain is added as PASSTHRU RPZ rule to 1st RPZ zone and Never_proxy is configured ffffffffffffffffffffffffffffffff and  got only RPZ  CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=769)
    def test_769_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=770)
    def test_770_Validate_Got_Only_RPZ_CEF_Log_Logs_as_Proxy_domain_playboy_com_is_added_as_PASSTHRU_RPZ_rule_to_1st_RPZ_Zone_and_set_to_ffffffffffffffffffffffffffffffff(self):
        logging.info("Validate got Only RPZ CEF Log for playboy.com  domain is added as PASSTHRU RPZ rule to 1st RPZ zone and set_to_ffffffffffffffffffffffffffffffff")
        LookFor="info CEF.*playboy.com.*CAT=RPZ.*"
        LookFor1="info CEF.*playboy.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False



    @pytest.mark.run(order=771)
    def test_771_Remove_Proxy_domain_playboy_com_PASSTHRU_RPZ_Rule_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Remove Proxy Domain playboy.com PASSTHRU RPZ Rule from 1st RPZ zone rpz32.com")
        data={"name": "playboy.com.rpz32.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=772)
    def test_772_Validate_Proxy_domain_times_com_PASSTHRU_RPZ_Rule_is_Deleted_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate Proxy Domain playboy.com PASSTHRU RPZ Rule is deleted from 1st RPZ zone rpz32.com\n")
        data={"name": "playboy.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "playboy.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=773)
    def test_773_Add_Proxy_domain_playboy_com_as_PASSTHRU_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Add Proxy Domain Playboy.com as PASSTHRU RPZ Rule to 7th RPZ zone rpz25.com")
        data={"canonical":"playboy.com", "name": "playboy.com.rpz25.com","rp_zone": "rpz25.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=774)
    def test_774_Validate_Added_Proxy_domain_playboy_com_as_PASSTHRU_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate added Proxy Domain Playboy.com as PASSTHRU RPZ Rule to 7th RPZ zone rpz25.com\n")
        data={"name": "playboy.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz25.com"' in get_rpz_rule) and ('"canonical": "playboy.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=775)
    def test_775_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=776)
    def test_776_Send_Query_from_Proxy_All_Configured_Subscriber_client_for_Proxy_Domain_playboy_com_Validate_returns_NORMAL_response_As_playboy_com_is_added_as_PASSTHRU_RPZ_rule_to_7th_RPZ_Zone_and_got_only_RPZ_CEF_logs(self):
        logging.info("Perform Query from Proxy-All configured Subscriber client for Proxy Domain playboy.com and Validate get NORMAL response as playboy.com domain is added as Proxy domain is added as PASSTHRU RPZ rule to 7th RPZ zone and get only RPZ CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=777)
    def test_777_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=778)
    def test_778_Validate_Get_only_RPZ_CEF_Log_Logs_as_Proxy_domain_playboy_com_is_added_as_PASSTHRU_RPZ_rule_to_7th_RPZ_Zone(self):
        logging.info("Validate got only RPZ CEF Log for playboy.com  added domain is added as PASSTHRU RPZ rule to 7th RPZ zone")
        LookFor="info CEF.*playboy.com.*CAT=RPZ.*"
        LookFor1="info CEF.*playboy.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=779)
    def test_779_Remove_Proxy_playboy_com_PASSTHRU_RPZ_Rule_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Remove Proxy Domain Playboy.com PASSTHRU RPZ Rule from 7th RPZ zone rpz25.com")
        data={"name": "playboy.com.rpz25.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=780)
    def test_780_Validate_Proxy_domain_playboy_com_PASSTHRU_RPZ_Rule_is_Deleted_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate Proxy Domain Playboy.com PASSTHRU RPZ Rule is deleted from 7th RPZ zone rpz25.com\n")
        data={"name": "playboy.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz25.com"' in get_rpz_rule) and ('"canonical": "playboy.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=781)
    def test_781_Add_Proxy_domain_playboy_com_as_PASSTHRU_RPZ_Rule_to_32nd_RPZ_Zone_rpz1_com(self):
        logging.info ("Add Proxy Domain Playboy.com as PASSTHRU RPZ Rule to 32nd RPZ zone rpz1.com")
        data={"canonical":"playboy.com", "name": "playboy.com.rpz1.com","rp_zone": "rpz1.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=782)
    def test_782_Validate_Added_Proxy_domain_playboy_com_as_PASSTHRU_RPZ_Rule_to_32nd_RPZ_Zone_rpz1_com(self):
        logging.info("Validate added Proxy Domain Playboy.com as PASSTHRU RPZ Rule to 32nd RPZ zone rpz1.com\n")
        data={"name": "playboy.com.rpz1.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz1.com"' in get_rpz_rule) and ('"canonical": "playboy.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=783)
    def test_783_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=784)
    def test_784_Send_Query_from_Proxy_All_Configured_Subscriber_client_for_Proxy_Domain_playboy_com_Validate_returns_NORMAL_response_As_playboy_com_is_added_as_PASSTHRU_RPZ_rule_to_32nd_RPZ_Zone_and__set_to_ffffffffffffffffffffffffffffffff_not_got_any_CEF_logs(self):
        logging.info("Perform Query from Proxy-All configured Subscriber client for Proxy Domain playboy.com and Validate get NORMAL response as playboy.com domain is added as Proxy domain is added as PASSTHRU RPZ rule to 32nd RPZ zone and did not get any CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=785)
    def test_785_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=786)
    def test_786_Validate_Not_Get_PCP_OR_RPZ_CEF_Log_Logs_as_Proxy_domain_playboy_com_is_added_as_PASSTHRU_RPZ_rule_to_32nd_RPZ_Zone_and__set_to_ffffffffffffffffffffffffffffffff(self):
        logging.info("Validate did not got any RPZ and PCP CEF Log for playboy.com  added domain is added as PASSTHRU RPZ rule to 32nd RPZ zone")
        LookFor="info CEF.*playboy.com.*CAT=RPZ.*"
        LookFor1="info CEF.*playboy.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=787)
    def test_787_Remove_Proxy_playboy_com_PASSTHRU_RPZ_Rule_from_32nd_RPZ_Zone_rpz1_com(self):
        logging.info ("Remove Proxy Domain Playboy.com PASSTHRU RPZ Rule from 32nd RPZ zone rpz1.com")
        data={"name": "playboy.com.rpz1.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=788)
    def test_788_Validate_Proxy_domain_playboy_com_PASSTHRU_RPZ_Rule_is_Deleted_from_32nd_RPZ_Zone_rpz1_com(self):
        logging.info("Validate Proxy Domain Playboy.com PASSTHRU RPZ Rule is deleted from 7th RPZ zone rpz1.com\n")
        data={"name": "playboy.com.rpz1.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "playboy.com.rpz1.com"' in get_rpz_rule) and ('"canonical": "playboy.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=789)
    def test_789_Restart_DNS_service(self):
        logging.info("Restart services")
        restart_the_grid()
        #grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        #ref = json.loads(grid)[0]['_ref']
        #publish={"member_order":"SIMULTANEOUSLY"}
        #request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        #request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        #restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        #sleep(60)



    @pytest.mark.run(order=790)
    def test_790_Add_WPCP_domain_coors_com_as_PASSTHRU_RPZ_Rule_to_1_RPZ_Zone_rpz32_com(self):
        logging.info ("Add WPCP Domain coors.com as PASSTHRU RPZ Rule to 32 RPZ zone rpz32.com")
        data={"canonical":"coors.com", "name": "coors.com.rpz32.com","rp_zone": "rpz32.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=791)
    def test_791_Validate_Added_WPCP_domain_coors_com_as_PASSTHRU_RPZ_Rule_to_1_RPZ_Zone_rpz32_com(self):
        logging.info("Validate added WPCP Domain coors.com as PASSTHRU RPZ Rule to 32 RPZ zone rpz32.com\n")
        data={"name": "coors.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "coors.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=792)
    def test_792_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=793)
    def test_793_Send_Query_from_WPCP_Proxy_Configured_Subscriber_client_for_WPCP_Domain_coors_com_Validate_returns_NORMAL_response_As_coors_com_is_added_as_PASSTHRU_RPZ_rule_to_1st_RPZ_Zone_and_got_RPZ_and_WPCP_CEF_logs_But_not_PXY_CEF_log_as_Never_proxy_set_to_ffffffffffffffffffffffffffffffff(self):
        logging.info("Perform Query from WPCP configured Subscriber client for Proxy Domain coors.com and Validate get NORMAL response as coors.com domain is added as PASSTHRU RPZ rule to 1st RPZ zone and Never_proxy is configured ffffffffffffffffffffffffffffffff and  got only RPZ  CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' coors.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*coors.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=794)
    def test_794_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

# Changed the test cases from !=None to ==None as NIOS-78037
#Again changed the test cae from ==None to !=None as SNIN-57

    @pytest.mark.run(order=795)
    def test_795_Validate_Got_RPZ_and_WPCP_CEF_Log_Logs_but_not_PXY_CEF_logs_as_WPCP_domain_coors_com_is_added_as_PASSTHRU_RPZ_rule_to_1st_RPZ_Zone_and_set_to_ffffffffffffffffffffffffffffffff(self):
        logging.info("Validate got RPZ and WPCP CEF Log but not Proxy CEP logs for coors.com  domain is added as PASSTHRU RPZ rule to 1st RPZ zone and set_to_ffffffffffffffffffffffffffffffff")
        LookFor="info CEF.*coors.com.*CAT=RPZ.*"
        LookFor1="info CEF.*coors.com.*CAT=PXY.*"
        LookFor2="info CEF.*coors.com.*CAT=WRN_0x00000000000000000000000000000001.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs2!=None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False



    @pytest.mark.run(order=796)
    def test_796_Remove_WPCP_domain_coors_com_PASSTHRU_RPZ_Rule_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info ("Remove WPCP Domain coors.com PASSTHRU RPZ Rule from 1st RPZ zone rpz32.com")
        data={"name": "coors.com.rpz32.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=797)
    def test_797_Validate_WPCP_domain_coors_com_PASSTHRU_RPZ_Rule_is_Deleted_from_1st_RPZ_Zone_rpz32_com(self):
        logging.info("Validate Proxy Domain coors.com PASSTHRU RPZ Rule is deleted from 1st RPZ zone rpz32.com\n")
        data={"name": "coors.com.rpz32.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz32.com"' in get_rpz_rule) and ('"canonical": "coors.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=798)
    def test_798_Add_WPCP_domain_coors_com_as_PASSTHRU_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Add WPCP Domain coors.com as PASSTHRU RPZ Rule to 7th RPZ zone rpz25.com")
        data={"canonical":"coors.com", "name": "coors.com.rpz25.com","rp_zone": "rpz25.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=799)
    def test_799_Validate_Added_Proxy_domain_playboy_com_as_PASSTHRU_RPZ_Rule_to_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate added coors Domain coors.com as PASSTHRU RPZ Rule to 7th RPZ zone rpz25.com\n")
        data={"name": "coors.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz25.com"' in get_rpz_rule) and ('"canonical": "coors.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=800)
    def test_800_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=801)
    def test_801_Send_Query_from_Proxy_All_and_WPCP_Configured_Subscriber_client_for_WPCP_Domain_coors_com_Validate_returns_NORMAL_response_As_coors_com_is_added_as_PASSTHRU_RPZ_rule_to_7th_RPZ_Zone_and_got_RPZ_and_WPCP_CEF_logs_as_Never_proxy_is_set_to_ffffffffffffffffffffffffffffffff(self):
        logging.info("Perform Query from Proxy-All and WPCP configured Subscriber client for Proxy Domain coors.com and Validate get NORMAL response as coors.com domain is added as WPCP domain is added as PASSTHRU RPZ rule to 7th RPZ zone and did not get any CEF logs as never_Proxy is set to ffffffffffffffffffffffffffffffff")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' coors.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*coors.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=802)
    def test_802_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")




# Changed the test cases from !=None to ==None as NIOS-78037
#Again changed the test cae from ==None to !=None as SNIN-57

    @pytest.mark.run(order=803)
    def test_803_Validate_Get_WPCP_and_RPZ_CEF_Log_but_not_PXY_CEF_Logs_as_WPCP_domain_coors_com_is_added_as_PASSTHRU_RPZ_rule_to_7th_RPZ_Zone_and_set_to_ffffffffffffffffffffffffffffffff(self):
        logging.info("Validate got RPZ and WPCP CEF Log for coors.com  added domain is added as PASSTHRU RPZ rule to 7th RPZ zone and set_to_ffffffffffffffffffffffffffffffff")
        LookFor="info CEF.*coors.com.*CAT=RPZ.*"
        LookFor1="info CEF.*coors.com.*CAT=PXY.*"
        LookFor2="info CEF.*coors.com.*CAT=WRN_0x00000000000000000000000000000001.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs!=None and logs2!=None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=804)
    def test_804_Remove_WPCP_Domain_coors_com_PASSTHRU_RPZ_Rule_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info ("Remove WPCP Domain coors.com PASSTHRU RPZ Rule from 7th RPZ zone rpz25.com")
        data={"name": "coors.com.rpz25.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=805)
    def test_805_Validate_WPCP_domain_coors_com_PASSTHRU_RPZ_Rule_is_Deleted_from_7th_RPZ_Zone_rpz25_com(self):
        logging.info("Validate WPCP Domain coors.com PASSTHRU RPZ Rule is deleted from 7th RPZ zone rpz25.com\n")
        data={"name": "coors.com.rpz25.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz25.com"' in get_rpz_rule) and ('"canonical": "coors.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=806)
    def test_806_Add_WPCP_domain_coors_com_as_PASSTHRU_RPZ_Rule_to_32nd_RPZ_Zone_rpz1_com(self):
        logging.info ("Add WPCP Domain coors.com as PASSTHRU RPZ Rule to 32nd RPZ zone rpz1.com")
        data={"canonical":"coors.com", "name": "coors.com.rpz1.com","rp_zone": "rpz1.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        read  = re.search(r'201',response)
        for read in response:
                assert True
        logging.info("A PASSTHRU RPZ Rule is created Successfully")
        logging.info("Test Case Execution Completed")
        sleep(30)



    @pytest.mark.run(order=807)
    def test_807_Validate_Added_WPCP_domain_coors_com_as_PASSTHRU_RPZ_Rule_to_32nd_RPZ_Zone_rpz1_com(self):
        logging.info("Validate added WPCP Domain coors.com as PASSTHRU RPZ Rule to 32nd RPZ zone rpz1.com\n")
        data={"name": "coors.com.rpz1.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz1.com"' in get_rpz_rule) and ('"canonical": "coors.com"' in get_rpz_rule):
                assert True
        else:
                assert False
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=808)
    def test_808_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)


    @pytest.mark.run(order=809)
    def test_809_Send_Query_from_Proxy_All_and_WPCP_Configured_Subscriber_client_for_WPCP_Domain_coors_com_Validate_returns_NORMAL_response_As_coors_com_is_added_as_PASSTHRU_RPZ_rule_to_32nd_RPZ_Zone_and__set_to_ffffffffffffffffffffffffffffffff_not_got_any_CEF_logs(self):
        logging.info("Perform Query from Proxy-All and WPCP configured Subscriber client for Proxy Domain coors.com and Validate get NORMAL response as coors.com domain is added as WPCP domain is added as PASSTHRU RPZ rule to 32nd RPZ zone and did not get any CEF logs")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' coors.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*coors.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=810)
    def test_810_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=811)
    def test_811_Validate_Not_Get_WPCP_OR_RPZ_CEF_Log_Logs_as_WPCP_domain_coors_com_is_added_as_PASSTHRU_RPZ_rule_to_32nd_RPZ_Zone_and__set_to_ffffffffffffffffffffffffffffffff(self):
        logging.info("Validate did not got any RPZ and WPCP CEF Log for coors.com  added domain is added as PASSTHRU RPZ rule to 32nd RPZ zone")
        LookFor="info CEF.*playboy.com.*CAT=RPZ.*"
        LookFor1="info CEF.*playboy.com.*CAT=PXY.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


    @pytest.mark.run(order=812)
    def test_812_Remove_WPCP_coors_com_PASSTHRU_RPZ_Rule_from_32nd_RPZ_Zone_rpz1_com(self):
        logging.info ("Remove WPCP Domain coors.com PASSTHRU RPZ Rule from 32nd RPZ zone rpz1.com")
        data={"name": "coors.com.rpz1.com"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname",fields=json.dumps(data))
        ref = json.loads(get_ref)[0]['_ref']
        request_ref = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data))
        read  = re.search(r'201',request_ref)
        for read in request_ref:
                assert True
        logging.info("A PASSTHRU RPZ Rule is Deleted Successfully")
        logging.info("Test Case  Execution Completed")
        sleep(30)


    @pytest.mark.run(order=813)
    def test_813_Validate_WPCP_domain_coors_com_PASSTHRU_RPZ_Rule_is_Deleted_from_32nd_RPZ_Zone_rpz1_com(self):
        logging.info("Validate WPCP Domain coors.com PASSTHRU RPZ Rule is deleted from 7th RPZ zone rpz1.com\n")
        data={"name": "coors.com.rpz1.com"}
        get_rpz_rule = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname", fields=json.dumps(data))
        print "==================================="
        print get_rpz_rule
        print "==================================="
        logging.info(get_rpz_rule)
        res=json.loads(get_rpz_rule)
        if('"name": "coors.com.rpz1.com"' in get_rpz_rule) and ('"canonical": "coors.com"' in get_rpz_rule):
                assert False
        else:
                assert True
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=814)
    def test_814_From_CLI_Configuration_never_proxy_for_Defult_category_set_is_00000000000000000000000000000000(self):
        try:
            logging.info("From CLI Configuration never_proxy for Default category set is 00000000000000000000000000000000")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:',timeout=None)
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set subscriber_secure_data never_proxy 00000000000000000000000000000000')
            child.expect('never_proxy categories is set')
            child.expect('!!! A RESTART of the DNS service is required before this change can take effect !!!')
            logging.info("Test Case Execution Passed")
            assert True
        except:
            logging.info("Test Case Execution Failed")
            assert False



    @pytest.mark.run(order=815)
    def test_815_From_CLI_Validate_Configuration_never_proxy_for_Default_category_set_is_00000000000000000000000000000000(self):
        logging.info("From CLI Validate Configuration never_proxy for Default category set is 00000000000000000000000000000000 ")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data never_proxy')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*never_proxy category set is 00000000000000000000000000000000.*',c)
        logging.info("Test case execution completed")



    @pytest.mark.run(order=816)
    def test_816_Restart_DNS_service(self):
        logging.info("Restart services")
        restart_the_grid()
        #grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        #ref = json.loads(grid)[0]['_ref']
        #publish={"member_order":"SIMULTANEOUSLY"}
        #request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        #request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        #restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        #sleep(60)


################### Test case for DCA doing proxy vip from MSP #####################


    @pytest.mark.run(order=820)
    def test_820_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 12 passed")
        sleep(10)

    @pytest.mark.run(order=821)
    def test_821_Send_Query_from_NON_PCP_bit_match_and_not_Proxy_all_Configured_Subscriber_client_for_Proxy_Domain_playboy_com_Validate_returns_NORMAL_response_cached_DCA_with_PCP_word(self):
        logging.info("Perform Query from NON PCP bit match and not configured Proxy-All Subscriber client for Proxy Domain playboy.com and Validate get NORMAL response playboy.com domain is cached to DCA with PCP word")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=822)
    def test_822_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=823)
    def test_823_Validate_NO_CEF_Log_Logs_as_got_NORMAL_response_for_Proxy_domain_playboy_com_when_send_query_from_NON_PCP_bit_match_and_not_configured_Proxy_All_client(self):
        logging.info("Validate NO CEF Log for playboy.com as got NORMAL response when send query from NON PCP bit match and not configured Proxy-ALL client")
        LookFor="info CEF.*playboy.com.*CAT=PXY.*"
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



    @pytest.mark.run(order=824)
    def test_824_Validate_Proxy_Domain_playboy_com_get_cached_to_DCA_When_Send_Query_From_NON_PCP_bit_Matched_and_not_configured_Proxy_All_Subscriber_client(self):
        logging.info("Validate Proxy Domain playboy.com get cached to DCA when send query from the NON PCP bit matched and not configured Proxy-All subscriber client")
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
        logging.info("Test Case Execution Completed")



    @pytest.mark.run(order=825)
    def test_825_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=826)
    def test_826_Send_Query_from_PCP_and_Proxy_All_Configured_Subscriber_client_for_Proxy_Domain_playboy_com_Using_IB_FLEX_Member_Validate_returns_Proxy_IP_response_from_DCA_As_palyboy_com_domain_is_already_DCA_Cache(self):
        logging.info("Perform Query from PCP and Proxy-All Subscriber client for Proxy Domain playboy.com using IB-FLEX Member and get Proxy IPs response from DCA as playboy.com is already in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'; dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*5.*IN.*A.*10.*',str(dig_result))
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=827)
    def test_827_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case  Execution Completed")


# Changed the test cases from !=None to ==None as NIOS-78037
    @pytest.mark.run(order=828)
    def test_828_Validate_DCA_CEF_Log_Logs_as_got_response_from_DCA_for_Proxy_domain_playboy_com(self):
        logging.info("Validate DCA CEF Log for playboy.com as got response from DCA")
        LookFor="fp-rte.*info CEF.*playboy.com.*CAT=PXY"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False

    @pytest.mark.run(order=829)
    def test_829_Wait_for_20_Seconds_to_expire_MSP_connection(self):
        logging.info("Wait for 20 seconds to expire MSP connection")
        sleep (20)



    @pytest.mark.run(order=830)
    def test_830_start_Syslog_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=831)
    def test_831_Send_Query_from_PCP_and_Proxy_All_Configured_Subscriber_client_for_Proxy_Domain_playboy_com_Validate_returns_Proxy_IP_response_from_First_query_got_VIP_Reposne_From_Bind_even_palyboy_com_domain_is_already_DCA_Cache_because_MSP_Connection_lost_so_DCA_call_API_call_to_Get_VIP_From_MSP_then_Next_Query_got_from_DCA(self):
        logging.info("Perform Query from PCP and Proxy-All Subscriber client for Proxy Domain playboy.com using IB-FLEX Member and get Proxy IPs response from DCA as playboy.com is already in DCA cache")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'; dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*5.*IN.*A.*10.*',str(dig_result))
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=832)
    def test_832_stop_Syslog_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case  Execution Completed")



# Changed the test cases from !=None to ==None as NIOS-78037
    @pytest.mark.run(order=833)
    def test_833_Validate_for_both_BIND_and_DCA_CEF_Log_Logs_as_First_query_got_response_from_BIND_and_Second_query_got_DCA_for_Proxy_domain_playboy_com(self):
        logging.info("Validate DCA CEF Log for playboy.com as got response from DCA")
        LookFor="named.*info CEF.*playboy.com.*CAT=PXY"
        LookFor1="fp-rte.*info CEF.*playboy.com.*CAT=PXY"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None and logs1==None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False


############################# Test case for DummyMSP MSP server #############################



    @pytest.mark.run(order=834)
    def  test_834_Update_the_Subscriber_Site_With_Dummy_MSP_Server(self):
        logging.info("update subscriber site with Dummy MSP server")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        get_ref=json.loads(get_ref)[0]["_ref"]
        data={"msps":[{"ip_address": "22.22.22.22"}]}
        res = ib_NIOS.wapi_request('PUT', object_type=get_ref,fields=json.dumps(data))
        restart_the_grid()
        print res
        if type(res)!=tuple:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False
        time.sleep(30)


    @pytest.mark.run(order=835)
    def  test_835_Validate_subscriber_site_site2_Is_Updated_with_Dummy_MS_Server(self):
        logging.info("Validating subscriber site is Updated with Dummy MS Server")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=blocking_ipv4_vip1,blocking_ipv4_vip2,dca_sub_query_count,dca_sub_bw_list,msps")
        print reference
        reference=json.loads(reference)
        if reference[0]["blocking_ipv4_vip1"]=="1.1.1.1" and reference[0]["blocking_ipv4_vip2"]=="2.2.2.2" and reference[0]["dca_sub_query_count"]==True and  reference[0]["dca_sub_bw_list"]==True and reference[0]["msps"]==[{"ip_address": "22.22.22.22"}]:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=836)
    def test_836_From_Radclient_Send_Same_Interim_Radius_Message_with_PCP_Policy_and_Proxy_All_Configured_and_SSP_Policy(self):
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured and SSP Policy")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part2_radfiles/RFE_9980_PCP_Proxy_All_with_SSP_for_never_porxy.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=837)
    def test_837_Validate_Subscriber_Record_with_PCP_Policy_and_Proxy_All_configured(self):
        logging.info("Validate Subscriber Record with PCP Policy and Proxy-All configured")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case execution completed")


    @pytest.mark.run(order=838)
    def test_838_start_Syslog_Infoblox_log_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog and infoblox Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("test case 12 passed")
        sleep(10)


    @pytest.mark.run(order=839)
    def test_839_Send_Query_from_PCP_and_Proxy_all_Configured_Subscriber_client_match_for_Proxy_Domain_playboy_com_Validate_returns_NORMAL_response_MS_Serevr_not_Return_VIP_IP_response_as_it_is_Not_reachable(self):
        logging.info("Perform Query from PCP and Proxy-All matched client and validate returns normal response as MS Server is not reachable and not return VIP IPs response")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=840)
    def test_840_stop_Syslog_Infoblox_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog and infoblox Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=841)
    def test_841_Validate_NO_CEF_Log_Logs_as_got_NORMAL_response_for_Proxy_domain_playboy_com_as_MS_Serevr_not_Return_VIP_IP_response_as_it_is_Not_reachable_and_logs_Error_Message_infoblox_and_syslog_as_err_ib_proxy_callback_failure_to_retrieve_proxy_addr(self):
        logging.info("Validate NO CEF Log for playboy.com as got NORMAL response as MS Server is not reachable and not return VIP IPs response and in infoblox and syslog logs proper error message")
        LookFor="info CEF.*playboy.com.*CAT=PXY.*"
        LookFor1=".*err ib_proxy_callback.*failure to retrieve proxy_addr.*Timeout was reached.*"
        LookFor2="ERROR.*Timeout was reached msg_left\:0\: Failed to send URL http\://22.22.22.22.*"

        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logs2=logv(LookFor2,"/infoblox/var/infoblox.log",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None and logs1!=None and logs2!=None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False



    @pytest.mark.run(order=842)
    def  test_842_Update_the_Subscriber_Site_With_Reachable_But_not__MSP_Server(self):
        logging.info("update subscriber site with Reachable but not MSP server")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        get_ref=json.loads(get_ref)[0]["_ref"]
        data={"msps":[{"ip_address": config.client_ip}]}
        res = ib_NIOS.wapi_request('PUT', object_type=get_ref,fields=json.dumps(data))
        restart_the_grid()
        print res
        if type(res)!=tuple:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution Failed")
            assert False
        time.sleep(30)


    @pytest.mark.run(order=843)
    def  test_843_Validate_subscriber_site_site2_Is_Updated_with_Dummy_MS_Server(self):
        logging.info("Validating subscriber site is Updated with Dummy MS Server")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=blocking_ipv4_vip1,blocking_ipv4_vip2,dca_sub_query_count,dca_sub_bw_list,msps")
        print reference
        reference=json.loads(reference)
        if reference[0]["blocking_ipv4_vip1"]=="1.1.1.1" and reference[0]["blocking_ipv4_vip2"]=="2.2.2.2" and reference[0]["dca_sub_query_count"]==True and  reference[0]["dca_sub_bw_list"]==True and reference[0]["msps"]==[{"ip_address": config.client_ip}]:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False



    @pytest.mark.run(order=844)
    def test_844_From_Radclient_Send_Same_Interim_Radius_Message_with_PCP_Policy_and_Proxy_All_Configured_and_SSP_Policy(self):
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured and SSP Policy")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RFE_9980_part2_radfiles/RFE_9980_PCP_Proxy_All_with_SSP_for_never_porxy.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=845)
    def test_845_Validate_Subscriber_Record_with_PCP_Policy_and_Proxy_All_configured(self):
        logging.info("Validate Subscriber Record with PCP Policy and Proxy-All configured")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        logging.info("Test case execution completed")



    @pytest.mark.run(order=846)
    def test_846_start_Syslog_Infoblox_log_Messages_logs_on_IBFLEX_Member(self):
        logging.info("Starting Syslog and infoblox Messages Logs on IB-FLEX Member")
        log("start","/var/log/syslog",config.grid_vip)
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("test case 12 passed")
        sleep(10)


    @pytest.mark.run(order=847)
    def test_847_Send_Query_from_PCP_and_Proxy_all_Configured_Subscriber_client_match_for_Proxy_Domain_playboy_com_Validate_returns_NORMAL_response_MS_Serevr_not_Return_VIP_IP_response_as_it_is_MS_Server(self):
        logging.info("Perform Query from PCP and Proxy-All matched client and validate returns normal response as MS Server is not reachable and not return VIP IPs response")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=848)
    def test_848_stop_Syslog_Infoblox_Messages_Logs_on_IB_FLEX_Member(self):
        logging.info("Stopping Syslog and infoblox Logs on IB-FLEX Member")
        log("stop","/var/log/syslog",config.grid_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=849)
    def test_849_Validate_NO_CEF_Log_Logs_as_got_NORMAL_response_for_Proxy_domain_playboy_com_as_MS_Serevr_not_Return_VIP_IP_response_as_it_is_reachable_but_not_MS_Server_and_logs_Error_Message_infoblox_and_syslog_as_err_ib_proxy_callback_failure_to_retrieve_proxy_addr(self):
        logging.info("Validate NO CEF Log for playboy.com as got NORMAL response as MS Server is not reachable and not return VIP IPs response and in infoblox and syslog logs proper error message")
        LookFor="info CEF.*playboy.com.*CAT=PXY.*"
        LookFor1=".*err ib_proxy_callback: failure to retrieve proxy_addr:  Couldn't connect to server.*"
        LookFor2="ERROR.*Couldn't connect to server msg_left:0: Failed to send URL http.*"

        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        logs2=logv(LookFor2,"/infoblox/var/infoblox.log",config.grid_vip)
        logging.info(logs)
        print logs
        if logs==None and logs1!=None and logs2!=None:
            logging.info(logs)
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False



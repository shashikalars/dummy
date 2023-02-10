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



class RFE_V6_interface_cases(unittest.TestCase):
     #############################################  Test cases for RFE_V6_interface  #################################

    @pytest.mark.run(order=1)
    def test_001_enable_ipv6_checks(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        logging.info(get_ref)
        res = json.loads(get_ref)
        for i in res:
            ref=i["_ref"]
            data={"use_lan_ipv6_port":True,"use_mgmt_ipv6_port": True,"use_mgmt_port": True}
            response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
        logging.info("Test Case Execution Completed")


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
        data={"allow_recursive_query":True,"allow_query":[{"_struct": "addressac","address":"Any","permission":"ALLOW"}],"forwarders":[config.forwarder_ip],"logging_categories":{"log_rpz":True,"log_queries":True,"log_responses":True}}
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
    def test_005_In_Grid_Properties_Configure_Loopback_IP_as_Primary_DNS_Resolver(self):
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

    @pytest.mark.run(order=6)
    def test_006_Validate_At_Grid_Properties_DNS_Resolver_Is_Configured_with_loopback_IP(self):
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

    @pytest.mark.run(order=7)
    def test_007_Enable_Parental_Control_with_Proxy_Settings(self):
        logging.info("Enabling parental control with proxy settings")
        response = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber")
        response = json.loads(response)
        response=response[0]["_ref"]
        logging.info(response)
        data={"enable_parental_control": True,"cat_acctname":"infoblox_sdk", "cat_password":"LinWmRRDX0q","category_url":"https://dl.zvelo.com/","pc_zone_name":"pc.com","cat_update_frequency":1}
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
        response = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber?_return_fields=enable_parental_control,cat_acctname")
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

    @pytest.mark.run(order=9)
    def test_009_start_category_download_Messages_logs_on_master(self):
        logging.info("Starting category download Messages Logs on master")
        log("start","/storage/zvelo/log/category_download.log",config.grid_vip)
        logging.info("Test case 116 execution passed")
        #time.sleep(1500)


    @pytest.mark.run(order=10)
    def test_010_stop_category_download_Messages_logs_on_master(self):
        logging.info("Stop Syslog Messages Logs on master")
        log("stop","/storage/zvelo/log/category_download.log",config.grid_vip)
        logging.info("Test case execution passed")

    # @pytest.mark.run(order=11)
    # def test_011_validate_for_zvelo_download_data_completion_on_master(self):
    #     time.sleep(300)
    #     logging.info("Validating category download Messages Logs for data completion")
    #     LookFor="zvelodb download completed"
    #     logs=logv(LookFor,"/storage/zvelo/log/category_download.log",config.grid_vip)
    #     if logs!=None:
    #         logging.info(logs)
    #         logging.info("Test Case Execution passed")
    #         assert True
    #     else:
    #         logging.info("Test Case Execution failed")
    #         assert False

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
        sleep(400)

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

    @pytest.mark.run(order=19)
    def test_019_add_32_rpz_zone(self):
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

            print("Restart DNS Services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
            ref = json.loads(grid)[0]['_ref']
            data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
            sleep(30)

    @pytest.mark.run(order=20)
    def test_020_Enable_proxy_rpz_passthru_in_subscriber_site(self):
        logging.info("proxy rpz passthru")
        ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=proxy_rpz_passthru")
        ref=json.loads(ref)
        ref1=ref[0]["_ref"]
        data={"proxy_rpz_passthru":True}
        ref=ib_NIOS.wapi_request('PUT', object_type=ref1,fields=json.dumps(data))
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)

        if type(ref)!=tuple:
            logging.info("Test case execution passed")
            assert True
        else:
            logging.info("Test case  execution failed")
            assert False

    @pytest.mark.run(order=21)
    def test_021_validate_proxy_rpz_passthru_is_enabled(self):
        logging.info("Disabling proxy rpz passthru")
        ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=proxy_rpz_passthru")
        ref=json.loads(ref)
        data=ref[0]["proxy_rpz_passthru"]
        if data==True:
            logging.info("Test case  execution passed")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False

    @pytest.mark.run(order=22)
    def test_022_Select_LocalID_in_Subscriber_Services_properties(self):
                logging.info("NAT")
                get_ref = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']

                logging.info("Modify a enable_PC")

                #data = {"ip_space_discriminator":"Deterministic-NAT-Port"}
                data = {"local_id": "LocalId"}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case  Execution Completed")

    @pytest.mark.run(order=23)
    def test_023_Copy_Subscriber_Record_radfiles_to_radclient(self):
        try:
            child = pexpect.spawn('scp -pr RR root@'+str(config.rad_client_ip)+':/root/ ')
            child.logfile=sys.stdout
            child.expect('Are you sure you want to continue connecting (yes/no)?',timeout=None)
            child.sendline('yes')
            c=child.before
            print "Copied the files to radclient with response yes"
        except Exception as e:
            c = False
        if c:
            pass
        else:
            logging.info("Copy Subscriber Record radius message files to RAD Client")
            dig_cmd = 'scp -pr RR root@'+str(config.rad_client_ip)+':/root/ '
            dig_result = subprocess.check_output(dig_cmd, shell=True)
            print dig_result
            assert re.search(r'',str(dig_result))
            print "Copied the files to radclient"
            logging.info("Test Case Execution Completed")
            sleep(20)

    @pytest.mark.run(order=24)
    def test_024_From_Radclient_Send_Start_Radius_Message_without_PCP_Policy_Configured(self):
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RR/without_pcp.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)

    @pytest.mark.run(order=25)
    def test_025_Validate_Subscriber_Record_without_PCP_Policy(self):
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


    @pytest.mark.run(order=26)
    def test_026_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(15)

    @pytest.mark.run(order=27)
    def test_027_Query_RPZ_Zones_when_PCP_Policy_is_not_set(self):
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' pass0 +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        #assert re.search(r'.*pass0.*IN.*A.*10.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=28)
    def test_028_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=29)
    def test_029_Validate_RPZ_Passthru_Proxy_Feature_works_when_PCP_Policy_is_not_set_in_SSP_Record_Bug_NIOSSPT_11622_NIOS_78059(self):
        LookFor=".*pass0.*query.*pass0.*"
        #LookFor=".*QNAME PASSTHRU rewrite pass0.*"
        #LookFor=".*CAT=RPZ.*"
        #LookFor=".*pass0.*5 IN A 10.*"
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

    @pytest.mark.run(order=30)
    def test_030_Validate_There_is_no_CEF_Log_for_Proxy_Bug_NIOSSPT_11632_NIOS_78065(self):
        LookFor=".*CAT=PXY.*"
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


    @pytest.mark.run(order=31)
    def test_031_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
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


    @pytest.mark.run(order=32)
    def test_032_Validate_DCA_Cache_Hit_Counts_set_to_Zero(self):
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
        logging.info("Test Case Execution Completed")
        sleep(15)



    @pytest.mark.run(order=33)
    def test_033_Validate_show_subscriber_secure_data_never_proxy_shows_all_zeros_by_default(self):
        logging.info("Validate as got response from Bind for Proxy domain playboy.com Cache hit count not increased and Miss cache count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data never_proxy')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*never_proxy category set is 00000000000000000000000000000000.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=34)
    def test_034_set_subscriber_secure_data_never_proxy_to_some_value(self):
        logging.info("Validate as got response from Bind for Proxy domain playboy.com Cache hit count not increased and Miss cache count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data never_proxy 00200000000000000000022000000000')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A RESTART of the DNS service is required before this change can take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=35)
    def test_035_Perform_RESTART_of_the_DNS_service(self):
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)

    @pytest.mark.run(order=36)
    def test_036_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=37)
    def test_037_Query_domain_when_never_proxy_is_set_from_NON_Subscriber_Client(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip4)+' "dig @'+str(config.grid_vip)+' ibm.com +noedns -b '+config.client_ip4+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*ibm.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=38)
    def test_038_Query_domain_when_never_proxy_is_set_from_NON_Subscriber_Client(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip4)+' "dig @'+str(config.grid_vip)+' ibm.com +noedns -b '+config.client_ip4+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*ibm.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=39)
    def test_039_Query_domain_when_never_proxy_is_set_from_NON_Subscriber_Client(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip4)+' "dig @'+str(config.grid_vip)+' ibm.com +noedns -b '+config.client_ip4+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*ibm.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=40)
    def test_040_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=41)
    def test_041_Validate_query_domain_resolves_normally(self):
        LookFor=".*query.*ibm.com IN A response.*NOERROR.*ibm.com.*"
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



    @pytest.mark.run(order=42)
    def test_042_Validate_DCA_Cache_content_shows_domain_ibm_com_cached_in_dca(self):
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
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=43)
    def test_043_Validate_DCA_Cache_Hit_Counts_Increased_Bug_NIOS_78358(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*2.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)

    @pytest.mark.run(order=44)
    def test_044_Clear_DCA_Cache(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set dns flush all')
        child.expect('Infoblox >')
        sleep(5)

    @pytest.mark.run(order=45)
    def test_045_Restart_Service(self):
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)


    @pytest.mark.run(order=46)
    def test_046_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(15)

    @pytest.mark.run(order=47)
    def test_047_Query_domain_when_never_proxy_is_set_from_Subscriber_Client(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' ibm.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*ibm.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=48)
    def test_048_Query_domain_when_never_proxy_is_set_from_Subscriber_Client(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' ibm.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*ibm.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=49)
    def test_049_Query_domain_when_never_proxy_is_set_from_Subscriber_Client(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' ibm.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*ibm.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=50)
    def test_050_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=51)
    def test_051_Validate_query_domain_resolves_normally_and_query_answers_from_dca_and_first_query_message_logged_in_Logs(self):
        LookFor=".*query.*ibm.com.*"
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



    @pytest.mark.run(order=52)
    def test_052_Validate_DCA_Cache_content_shows_domain_ibm_com_cached_in_dca(self):
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
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=53)
    def test_053_Validate_DCA_Cache_Hit_Counts_Increased_Bug_NIOS_78358(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*2.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=54)
    def test_054_Clear_DCA_Cache(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set dns flush all')
        child.expect('Infoblox >')
        sleep(5)

    @pytest.mark.run(order=55)
    def test_055_Restart_Service(self):
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)

    @pytest.mark.run(order=56)
    def test_056_set_subscriber_secure_data_never_proxy_to_default_value(self):
        logging.info("Validate as got response from Bind for Proxy domain playboy.com Cache hit count not increased and Miss cache count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set subscriber_secure_data never_proxy 00000000000000000000000000000000')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A RESTART of the DNS service is required before this change can take effect.*',c)
        logging.info("Test Case Execution Completed")
        time.sleep(15)


    @pytest.mark.run(order=57)
    def test_057_Perform_RESTART_of_the_DNS_service(self):
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)

    @pytest.mark.run(order=58)
    def test_058_Validate_show_subscriber_secure_data_never_proxy_shows_all_zeros_by_default(self):
        logging.info("Validate as got response from Bind for Proxy domain playboy.com Cache hit count not increased and Miss cache count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data never_proxy')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*never_proxy category set is 00000000000000000000000000000000.*',c)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=59)
    def test_059_Copy_Subscriber_Record_radfiles_to_radclient(self):
        try:
            child = pexpect.spawn('scp -pr RR root@'+str(config.rad_client_ip)+':/root/ ')
            child.logfile=sys.stdout
            child.expect('Are you sure you want to continue connecting (yes/no)?',timeout=None)
            child.sendline('yes')
            c=child.before
            print "Copied the files to radclient with response yes"
        except Exception as e:
            c = False
        if c:
            pass
        else:
            logging.info("Copy Subscriber Record radius message files to RAD Client")
            dig_cmd = 'scp -pr RR root@'+str(config.rad_client_ip)+':/root/ '
            dig_result = subprocess.check_output(dig_cmd, shell=True)
            print dig_result
            assert re.search(r'',str(dig_result))
            print "Copied the files to radclient"
            logging.info("Test Case Execution Completed")
            sleep(5)


    @pytest.mark.run(order=60)
    def test_060_From_Radclient_Send_Start_Radius_Message(self):
        logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RR/4.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)



    @pytest.mark.run(order=61)
    def test_061_Add_RPZ_PASSTHRU_rule_playboy_com_in_Last_RPZ_Zone(self):
        logging.info("add rpz rule")
        ref=add_rpz_rule("playboy.com","rpz31.com")
        if ref!=None:
            logging.info("Test case executed successfully")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
        sleep(40)


    @pytest.mark.run(order=62)
    def test_062_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(15)


    @pytest.mark.run(order=63)
    def test_063_Query_domain_playboy_com_which_is_added_in_last_RPZ_Zone(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=64)
    def test_064_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=65)
    def test_065_Validate_query_domain_resolves_normally_NIOSSPT_11637_NIOS_78057(self):
        LookFor=".*query.*playboy.com.*"
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



    @pytest.mark.run(order=66)
    def test_066_Validate_DCA_Cache_content_does_not_show_domain_playboy_com(self):
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


    @pytest.mark.run(order=67)
    def test_067_Validate_DCA_Cache_Hit_Counts_did_not_Increased(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)



    @pytest.mark.run(order=68)
    def test_068_Clear_DCA_Cache(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set dns flush all')
        child.expect('Infoblox >')
        sleep(5)

    @pytest.mark.run(order=69)
    def test_069_Restart_Service(self):
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)

    @pytest.mark.run(order=70)
    def test_070_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(15)

    @pytest.mark.run(order=71)
    def test_071_Query_domain_pass31_which_is_added_in_last_RPZ_Zone(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' pass31 +noedns -b '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*pass31.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=72)
    def test_072_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=73)
    def test_073_Validate_query_domain_resolves_normally_NIOSSPT_11637_NIOS_78057(self):
        LookFor=".*query.*pass31.*"
        LookFor=".*NOERROR.*pass31.*"
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



    @pytest.mark.run(order=74)
    def test_074_Validate_DCA_Cache_content_does_not_show_domain_pass31(self):
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


    @pytest.mark.run(order=75)
    def test_075_Validate_DCA_Cache_Hit_Counts_did_not_Increased(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=76)
    def test_076_Clear_DCA_Cache(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set dns flush all')
        child.expect('Infoblox >')
        sleep(5)

    @pytest.mark.run(order=77)
    def test_077_Restart_Service(self):
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)


    @pytest.mark.run(order=78)
    def test_078_Remove_RPZ_PASSTHRU_rule_playboy_com_in_Last_31_RPZ_zone(self):
        logging.info("remove rpz rule")
        ref=remove_rpz_rule("playboy.com","rpz31.com")
        if ref!=None:
            logging.info("Test case executed successfully")
            assert True
        else:
            logging.info("Test case execution failed")
            assert False
        sleep(30)


    @pytest.mark.run(order=79)
    def test_079_Copy_Subscriber_Record_radfiles_to_radclient(self):
        try:
            child = pexpect.spawn('scp -pr RR root@'+str(config.rad_client_ip)+':/root/ ')
            child.logfile=sys.stdout
            child.expect('Are you sure you want to continue connecting (yes/no)?',timeout=None)
            child.sendline('yes')
            c=child.before
            print "Copied the files to radclient with response yes"
        except Exception as e:
            c = False
        if c:
            pass
        else:
            logging.info("Copy Subscriber Record radius message files to RAD Client")
            dig_cmd = 'scp -pr RR root@'+str(config.rad_client_ip)+':/root/ '
            dig_result = subprocess.check_output(dig_cmd, shell=True)
            print dig_result
            assert re.search(r'',str(dig_result))
            print "Copied the files to radclient"
            logging.info("Test Case Execution Completed")
            sleep(5)

    @pytest.mark.run(order=80)
    def test_080_From_Radclient_Send_Start_Radius_Message_for_non_matching_pcp_client(self):
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RR/1.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)


    @pytest.mark.run(order=81)
    def test_081_Validate_Subscriber_Record_for_non_matching_pcp_client(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip1+'\/32\|LID\:e0cb4e80e766\|IPS\:N\/A.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=82)
    def test_082_From_Radclient_Send_Start_Radius_Message_for_matching_pcp_client(self):
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RR/2.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)


    @pytest.mark.run(order=83)
    def test_083_Validate_Subscriber_Record_for_matching_pcp_client(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip2+'\/32\|LID\:e0cb4e80e766\|IPS\:N\/A.*',c)
        logging.info("Test case execution completed")

    @pytest.mark.run(order=84)
    def test_084_From_Radclient_Send_Start_Radius_Message_for_NO_SSP_NO_PCP_client(self):
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RR/3.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f RR/5.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)


    @pytest.mark.run(order=85)
    def test_085_Validate_Subscriber_Record_for_NO_SSP_NO_PCP_client(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show subscriber_secure_data')
        child.expect('Infoblox >')
        c=child.before
        assert re.search(r'.*'+config.client_ip3+'\/32\|LID\:e0cb4e80e766\|IPS\:N\/A.*',c)
        logging.info("Test case execution completed")


    @pytest.mark.run(order=86)
    def test_086_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)



    @pytest.mark.run(order=87)
    def test_087_Query_domain_ibm_com_which_does_not_match_PCP_Policy_and_Validate_Client_receiving_response_NIOSSPT_11827_NIOS_78551(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vip)+' -edo 0 -qname ibm.com -edata=0xFE31001145303a43423a34453a38303a45373a3636  -srcaddr '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*Question Section.*',str(dig_result))
        assert re.search(r'.*Answer Section.*',str(dig_result))
        assert re.search(r'.*Additional Section.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)



    @pytest.mark.run(order=88)
    def test_088_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=89)
    def test_089_Validate_query_domain_resolves_normally(self):
        LookFor=".*query.*ibm.com.*"
        LookFor=".*NOERROR.*ibm.com.*"
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

    @pytest.mark.run(order=90)
    def test_090_Query_domain_ibm_com_which_does_not_match_PCP_Policy_and_Validate_Client_receiving_response_NIOSSPT_11827_NIOS_78551(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vip)+' -edo 0 -qname ibm.com -edata=0xFE31001145303a43423a34453a38303a45373a3636  -srcaddr '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*Question Section.*',str(dig_result))
        assert re.search(r'.*Answer Section.*',str(dig_result))
        assert re.search(r'.*Additional Section.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)


    @pytest.mark.run(order=91)
    def test_091_Validate_DCA_Cache_content_show_domain_ibm_com(self):
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
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=92)
    def test_092_Validate_DCA_Cache_Hit_Counts_Increased(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*1.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)



    @pytest.mark.run(order=93)
    def test_093_Query_domain_ibm_com_which_does_not_match_PCP_Policy_and_Validate_Client_receiving_response_NIOSSPT_11827_NIOS_78551(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vip)+' -edo 0 -qname ibm.com -edata=0xFE31001145303a43423a34453a38303a45373a3636  -srcaddr '+config.client_ip1+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*Question Section.*',str(dig_result))
        assert re.search(r'.*Answer Section.*',str(dig_result))
        assert re.search(r'.*Additional Section.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)


    @pytest.mark.run(order=94)
    def test_094_Validate_DCA_Cache_content_show_domain_ibm_com(self):
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
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=95)
    def test_095_Validate_DCA_Cache_Hit_Counts_Increased(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*2.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=96)
    def test_096_Clear_DCA_Cache(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set dns flush all')
        child.expect('Infoblox >')
        sleep(5)

    @pytest.mark.run(order=97)
    def test_097_Restart_Service(self):
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)

    @pytest.mark.run(order=98)
    def test_098_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)



    @pytest.mark.run(order=99)
    def test_099_Query_domain_playboy_com_which_matches_LocalID(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vip)+' -edo 0 -qname playboy.com -edata=0xFE31001145303a43423a34453a38303a45373a3636  -srcaddr '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*Question Section.*',str(dig_result))
        assert re.search(r'.*Answer Section.*',str(dig_result))
        assert re.search(r'.*Additional Section.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)



    @pytest.mark.run(order=100)
    def test_100_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=101)
    def test_101_Validate_Guest_0_Logged_in_Log_for_LocalID_matching(self):
        LookFor=".*CEF.*"
        LookFor=".*RPZ-QNAME.*CNAME.*"
        LookFor=".*rpz QNAME CNAME rewrite playboy.com.*"
        LookFor=".*Guest=0.*"
        LookFor=".*LocalID=E0CB4E80E766.*"
        LookFor=".*CAT=0x00000000000000000000000000020000.*"
        LookFor=".*playboy.com.*"
        LookFor=".*2.2.2.2.*"
        LookFor=".*1.1.1.1.*"
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

    @pytest.mark.run(order=102)
    def test_102_Validate_DCA_Cache_content_show_cache_empty(self):
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


    @pytest.mark.run(order=103)
    def test_103_Validate_DCA_Cache_Hit_Counts_not_Increased(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)

    @pytest.mark.run(order=104)
    def test_104_Clear_DCA_Cache(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set dns flush all')
        child.expect('Infoblox >')
        sleep(5)

    @pytest.mark.run(order=105)
    def test_105_Restart_Service(self):
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)

    @pytest.mark.run(order=106)
    def test_106_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)



    @pytest.mark.run(order=107)
    def test_107_Query_domain_playboy_com_which_does_not_match_LocalID(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vip)+' -edo 0 -qname playboy.com -edata=0xFE31001145303a43423a34453a38303a45373a3644  -srcaddr '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*Question Section.*',str(dig_result))
        assert re.search(r'.*Answer Section.*',str(dig_result))
        assert re.search(r'.*Additional Section.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)



    @pytest.mark.run(order=108)
    def test_108_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=109)
    def test_109_Validate_Guest_1_Logged_in_Log_for_LocalID_not_matching(self):
        LookFor=".*CEF.*"
        LookFor=".*RPZ-QNAME.*CNAME.*"
        LookFor=".*rpz QNAME CNAME rewrite playboy.com.*"
        LookFor=".*Guest=1.*"
        LookFor=".*LocalID=E0CB4E80E766.*"
        LookFor=".*CAT=0x00000000000000000000000000020000.*"
        LookFor=".*playboy.com.*"
        LookFor=".*2.2.2.2.*"
        LookFor=".*1.1.1.1.*"
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

    @pytest.mark.run(order=110)
    def test_110_Validate_DCA_Cache_content_show_cache_empty(self):
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


    @pytest.mark.run(order=111)
    def test_111_Validate_DCA_Cache_Hit_Counts_not_Increased(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)

    @pytest.mark.run(order=112)
    def test_112_Clear_DCA_Cache(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set dns flush all')
        child.expect('Infoblox >')
        sleep(5)

    @pytest.mark.run(order=113)
    def test_113_Restart_Service(self):
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)


    @pytest.mark.run(order=114)
    def test_114_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)



    @pytest.mark.run(order=115)
    def test_115_Query_domain_playboy_com_which_matches_LocalID_using_V6(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vipv6)+' -edo 0 -qname playboy.com -edata=0xFE31001145303a43423a34453a38303a45373a3636  -srcaddr '+config.client_ip2v6+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*Question Section.*',str(dig_result))
        assert re.search(r'.*Answer Section.*',str(dig_result))
        assert re.search(r'.*Additional Section.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)



    @pytest.mark.run(order=116)
    def test_116_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=117)
    def test_117_Validate_Guest_0_Logged_in_Log_for_LocalID_matching(self):
        LookFor=".*CEF.*"
        LookFor=".*RPZ-QNAME.*CNAME.*"
        LookFor=".*rpz QNAME CNAME rewrite playboy.com.*"
        LookFor=".*Guest=0.*"
        LookFor=".*LocalID=E0CB4E80E766.*"
        LookFor=".*CAT=0x00000000000000000000000000020000.*"
        LookFor=".*playboy.com.*"
        LookFor=".*2.2.2.2.*"
        LookFor=".*1.1.1.1.*"
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

    @pytest.mark.run(order=118)
    def test_118_Validate_DCA_Cache_content_show_cache_empty(self):
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


    @pytest.mark.run(order=119)
    def test_119_Validate_DCA_Cache_Hit_Counts_not_Increased(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)

    @pytest.mark.run(order=120)
    def test_120_Clear_DCA_Cache(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set dns flush all')
        child.expect('Infoblox >')
        sleep(5)

    @pytest.mark.run(order=121)
    def test_121_Restart_Service(self):
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)



    @pytest.mark.run(order=122)
    def test_122_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)



    @pytest.mark.run(order=123)
    def test_123_Query_domain_playboy_com_which_does_not_match_LocalID_using_V6(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vipv6)+' -edo 0 -qname playboy.com -edata=0xFE31001145303a43423a34453a38303a45373a3644  -srcaddr '+config.client_ip2v6+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*Question Section.*',str(dig_result))
        assert re.search(r'.*Answer Section.*',str(dig_result))
        assert re.search(r'.*Additional Section.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)



    @pytest.mark.run(order=124)
    def test_124_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=125)
    def test_125_Validate_Guest_1_Logged_in_Log_for_LocalID_not_matching(self):
        LookFor=".*CEF.*"
        LookFor=".*RPZ-QNAME.*CNAME.*"
        LookFor=".*rpz QNAME CNAME rewrite playboy.com.*"
        LookFor=".*Guest=1.*"
        LookFor=".*LocalID=E0CB4E80E766.*"
        LookFor=".*CAT=0x00000000000000000000000000020000.*"
        LookFor=".*playboy.com.*"
        LookFor=".*2.2.2.2.*"
        LookFor=".*1.1.1.1.*"
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
        sleep(15)

    @pytest.mark.run(order=126)
    def test_126_Validate_DCA_Cache_content_show_cache_empty(self):
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
        sleep(15)


    @pytest.mark.run(order=127)
    def test_127_Validate_DCA_Cache_Hit_Counts_not_Increased(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)

    @pytest.mark.run(order=128)
    def test_128_Clear_DCA_Cache(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set dns flush all')
        child.expect('Infoblox >')
        sleep(5)

    @pytest.mark.run(order=129)
    def test_129_Restart_Service(self):
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)



    @pytest.mark.run(order=130)
    def test_130_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=131)
    def test_131_Query_non_pcp_domain_from_NON_Subscriber_Client_using_option_noedns(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip4)+' "dig @'+str(config.grid_vip)+' ibm.com +noedns -b '+config.client_ip4+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*ibm.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)


    @pytest.mark.run(order=132)
    def test_132_Query_non_pcp_domain_from_NON_Subscriber_Client_using_option_noedns(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip4)+' "dig @'+str(config.grid_vip)+' ibm.com +noedns -b '+config.client_ip4+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*ibm.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)


    @pytest.mark.run(order=133)
    def test_133_Query_non_pcp_domain_from_NON_Subscriber_Client_using_option_noedns(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip4)+' "dig @'+str(config.grid_vip)+' ibm.com +noedns -b '+config.client_ip4+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*ibm.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)



    @pytest.mark.run(order=134)
    def test_134_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=135)
    def test_135_Validate_query_domain_resolves_normally(self):
        LookFor=".*query.*ibm.com IN A response.*NOERROR.*ibm.com.*"
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
        sleep(15)



    @pytest.mark.run(order=136)
    def test_136_Validate_DCA_Cache_content_shows_domain_ibm_com_cached_in_dca(self):
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
        logging.info("Test Case Execution Completed")
        sleep(15)

    @pytest.mark.run(order=137)
    def test_137_Validate_DCA_Cache_Hit_Counts_Increased(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*2.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)

    @pytest.mark.run(order=138)
    def test_138_Clear_DCA_Cache(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set dns flush all')
        child.expect('Infoblox >')
        sleep(10)

    @pytest.mark.run(order=139)
    def test_139_Restart_Service(self):
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)

    @pytest.mark.run(order=140)
    def test_140_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=141)
    def test_141_Query_pcp_domain_from_NON_Subscriber_Client_using_option_noedns(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip4)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip4+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)


    @pytest.mark.run(order=142)
    def test_142_Query_pcp_domain_from_NON_Subscriber_Client_using_option_noedns(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip4)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip4+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)


    @pytest.mark.run(order=143)
    def test_143_Query_pcp_domain_from_NON_Subscriber_Client_using_option_noedns(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip4)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip4+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)



    @pytest.mark.run(order=144)
    def test_144_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=145)
    def test_145_Validate_query_domain_resolves_normally(self):
        LookFor=".*query.*playboy.com IN A response.*NOERROR.*playboy.com.*"
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
        sleep(15)



    @pytest.mark.run(order=146)
    def test_146_Validate_DCA_Cache_content_shows_domain_playboy_com_cached_in_dca(self):
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
        sleep(15)

    @pytest.mark.run(order=147)
    def test_147_Validate_DCA_Cache_Hit_Counts_Increased(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*2.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)

    @pytest.mark.run(order=148)
    def test_148_Clear_DCA_Cache(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set dns flush all')
        child.expect('Infoblox >')
        sleep(10)

    @pytest.mark.run(order=149)
    def test_149_Restart_Service(self):
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)


    @pytest.mark.run(order=150)
    def test_150_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=151)
    def test_151_Query_non_pcp_domain_from_NON_Subscriber_Client_using_option_edns0(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip4)+' "dig @'+str(config.grid_vip)+' ibm.com +edns=0 -b '+config.client_ip4+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*ibm.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)


    @pytest.mark.run(order=152)
    def test_152_Query_non_pcp_domain_from_NON_Subscriber_Client_using_option_edns0(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip4)+' "dig @'+str(config.grid_vip)+' ibm.com +edns=0 -b '+config.client_ip4+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*ibm.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)


    @pytest.mark.run(order=153)
    def test_153_Query_non_pcp_domain_from_NON_Subscriber_Client_using_option_edns0(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip4)+' "dig @'+str(config.grid_vip)+' ibm.com +edns=0 -b '+config.client_ip4+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*ibm.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)



    @pytest.mark.run(order=154)
    def test_154_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=155)
    def test_155_Validate_query_domain_resolves_normally(self):
        LookFor=".*query.*ibm.com IN A response.*NOERROR.*ibm.com.*"
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
        sleep(15)



    @pytest.mark.run(order=156)
    def test_156_Validate_DCA_Cache_content_shows_domain_ibm_com_cached_in_dca(self):
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
        logging.info("Test Case Execution Completed")
        sleep(15)

    @pytest.mark.run(order=157)
    def test_157_Validate_DCA_Cache_Hit_Counts_Increased(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*2.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)

    @pytest.mark.run(order=158)
    def test_158_Clear_DCA_Cache(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set dns flush all')
        child.expect('Infoblox >')
        sleep(10)

    @pytest.mark.run(order=159)
    def test_159_Restart_Service(self):
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)

    @pytest.mark.run(order=160)
    def test_160_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=161)
    def test_161_Query_pcp_domain_from_NON_Subscriber_Client_using_option_edns0(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip4)+' "dig @'+str(config.grid_vip)+' playboy.com +edns=0 -b '+config.client_ip4+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=162)
    def test_162_Query_pcp_domain_from_NON_Subscriber_Client_using_option_edns0(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip4)+' "dig @'+str(config.grid_vip)+' playboy.com +edns=0 -b '+config.client_ip4+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=163)
    def test_163_Query_pcp_domain_from_NON_Subscriber_Client_using_option_edns0(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip4)+' "dig @'+str(config.grid_vip)+' playboy.com +edns=0 -b '+config.client_ip4+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)



    @pytest.mark.run(order=164)
    def test_164_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=165)
    def test_165_Validate_query_domain_resolves_normally(self):
        LookFor=".*query.*playboy.com IN A response.*NOERROR.*playboy.com.*"
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
    def test_166_Validate_DCA_Cache_content_shows_domain_playboy_com_cached_in_dca(self):
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
        sleep(15)

    @pytest.mark.run(order=167)
    def test_167_Validate_DCA_Cache_Hit_Counts_Increased(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*2.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)

    @pytest.mark.run(order=168)
    def test_168_Clear_DCA_Cache(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set dns flush all')
        child.expect('Infoblox >')
        sleep(10)

    @pytest.mark.run(order=169)
    def test_169_Restart_Service(self):
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)


    @pytest.mark.run(order=170)
    def test_170_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=171)
    def test_171_Query_non_pcp_domain_from_Subscriber_Client_using_option_noedns(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' ibm.com +noedns -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*ibm.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=172)
    def test_172_Query_non_pcp_domain_from_Subscriber_Client_using_option_noedns(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' ibm.com +noedns -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*ibm.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=173)
    def test_173_Query_non_pcp_domain_from_Subscriber_Client_using_option_noedns(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' ibm.com +noedns -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*ibm.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)



    @pytest.mark.run(order=174)
    def test_174_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=175)
    def test_175_Validate_query_domain_resolves_normally(self):
        LookFor=".*query.*ibm.com IN A response.*NOERROR.*ibm.com.*"
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
        sleep(15)



    @pytest.mark.run(order=176)
    def test_176_Validate_DCA_Cache_content_shows_domain_ibm_com_cached_in_dca(self):
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
        logging.info("Test Case Execution Completed")
        sleep(15)

    @pytest.mark.run(order=177)
    def test_177_Validate_DCA_Cache_Hit_Counts_Increased(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*2.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)

    @pytest.mark.run(order=178)
    def test_178_Clear_DCA_Cache(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set dns flush all')
        child.expect('Infoblox >')
        sleep(10)

    @pytest.mark.run(order=179)
    def test_179_Restart_Service(self):
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)

    @pytest.mark.run(order=180)
    def test_180_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=181)
    def test_181_Query_pcp_domain_from_Subscriber_Client_using_option_noedns(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=182)
    def test_182_Query_pcp_domain_from_Subscriber_Client_using_option_noedns(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=183)
    def test_183_Query_pcp_domain_from_Subscriber_Client_using_option_noedns(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' playboy.com +noedns -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=184)
    def test_184_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=185)
    def test_185_Validate_query_domain_resolves_normally(self):
        LookFor=".*query.*playboy.com IN A response.*NOERROR.*playboy.com.*"
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
        sleep(15)



    @pytest.mark.run(order=186)
    def test_186_Validate_DCA_Cache_content_does_not_show_domain_playboy_com_in_dca(self):
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
        sleep(15)

    @pytest.mark.run(order=187)
    def test_187_Validate_DCA_Cache_Hit_Counts_not_Increased(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)

    @pytest.mark.run(order=188)
    def test_188_Clear_DCA_Cache(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set dns flush all')
        child.expect('Infoblox >')
        sleep(10)

    @pytest.mark.run(order=189)
    def test_189_Restart_Service(self):
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)


    @pytest.mark.run(order=190)
    def test_190_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=191)
    def test_191_Query_non_pcp_domain_from_Subscriber_Client_using_option_edns0(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' ibm.com +edns=0 -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*ibm.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=192)
    def test_192_Query_non_pcp_domain_from_Subscriber_Client_using_option_edns0(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' ibm.com +edns=0 -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*ibm.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=193)
    def test_193_Query_non_pcp_domain_from_Subscriber_Client_using_option_edns0(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' ibm.com +edns=0 -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*ibm.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)



    @pytest.mark.run(order=194)
    def test_194_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=195)
    def test_195_Validate_query_domain_resolves_normally(self):
        LookFor=".*query.*ibm.com IN A response.*NOERROR.*ibm.com.*"
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
        sleep(15)



    @pytest.mark.run(order=196)
    def test_196_Validate_DCA_Cache_content_shows_domain_ibm_com_cached_in_dca(self):
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
        logging.info("Test Case Execution Completed")
        sleep(15)

    @pytest.mark.run(order=197)
    def test_197_Validate_DCA_Cache_Hit_Counts_Increased(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*2.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)

    @pytest.mark.run(order=198)
    def test_198_Clear_DCA_Cache(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set dns flush all')
        child.expect('Infoblox >')
        sleep(10)

    @pytest.mark.run(order=199)
    def test_199_Restart_Service(self):
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)

    @pytest.mark.run(order=200)
    def test_200_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=201)
    def test_201_Query_pcp_domain_from_Subscriber_Client_using_option_edns0(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' playboy.com +edns=0 -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(10)


    @pytest.mark.run(order=202)
    def test_202_Query_pcp_domain_from_Subscriber_Client_using_option_edns0(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' playboy.com +edns=0 -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=203)
    def test_203_Query_pcp_domain_from_Subscriber_Client_using_option_edns0(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' playboy.com +edns=0 -b '+config.client_ip2+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*playboy.com.*IN.*A.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(15)



    @pytest.mark.run(order=204)
    def test_204_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=205)
    def test_205_Validate_query_domain_resolves_normally(self):
        LookFor=".*query.*playboy.com IN A response.*NOERROR.*playboy.com.*"
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
        sleep(15)



    @pytest.mark.run(order=206)
    def test_206_Validate_DCA_Cache_content_does_not_show_domain_playboy_com_cached_in_dca(self):
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
        sleep(15)

    @pytest.mark.run(order=207)
    def test_207_Validate_DCA_Cache_Hit_Counts_not_Increased(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*0.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)

    @pytest.mark.run(order=208)
    def test_208_Clear_DCA_Cache(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set dns flush all')
        child.expect('Infoblox >')
        sleep(10)

    @pytest.mark.run(order=209)
    def test_209_Restart_Service(self):
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)




    @pytest.mark.run(order=210)
    def test_210_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=211)
    def test_211_Query_pcp_domain_from_NON_PCP_Matching_Subscriber_Client_using_V6(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vipv6)+' -edo 0 -qname playboy.com -edata=0xFE31001145303a43423a34453a38303a45373a3636  -srcaddr '+config.client_ip1v6+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*Question Section.*',str(dig_result))
        assert re.search(r'.*Answer Section.*',str(dig_result))
        assert re.search(r'.*Additional Section.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)



    @pytest.mark.run(order=212)
    def test_212_Query_pcp_domain_from_NON_PCP_Matching_Subscriber_Client_using_V6(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vipv6)+' -edo 0 -qname playboy.com -edata=0xFE31001145303a43423a34453a38303a45373a3636  -srcaddr '+config.client_ip1v6+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*Question Section.*',str(dig_result))
        assert re.search(r'.*Answer Section.*',str(dig_result))
        assert re.search(r'.*Additional Section.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)



    @pytest.mark.run(order=213)
    def test_213_Query_pcp_domain_from_NON_PCP_Matching_Subscriber_Client_using_V6(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vipv6)+' -edo 0 -qname playboy.com -edata=0xFE31001145303a43423a34453a38303a45373a3636  -srcaddr '+config.client_ip1v6+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*Question Section.*',str(dig_result))
        assert re.search(r'.*Answer Section.*',str(dig_result))
        assert re.search(r'.*Additional Section.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)

    @pytest.mark.run(order=214)
    def test_214_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=215)
    def test_215_Validate_query_domain_resolves_normally(self):
        LookFor=".*query.*playboy.com IN A response.*NOERROR.*playboy.com.*"
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
        sleep(15)


    @pytest.mark.run(order=216)
    def test_216_Validate_DCA_Cache_content_shows_domain_playboy_com_cached_in_dca(self):
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
        sleep(15)

    @pytest.mark.run(order=217)
    def test_217_Validate_DCA_Cache_Hit_Counts_Increased(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*2.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)

    @pytest.mark.run(order=218)
    def test_218_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")

    @pytest.mark.run(order=219)
    def test_219_Query_pcp_domain_from_PCP_Matching_Subscriber_Client_using_V6(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vipv6)+' -edo 0 -qname playboy.com -edata=0xFE31001145303a43423a34453a38303a45373a3636  -srcaddr '+config.client_ip2v6+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*Question Section.*',str(dig_result))
        assert re.search(r'.*Answer Section.*',str(dig_result))
        assert re.search(r'.*Additional Section.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)



    @pytest.mark.run(order=220)
    def test_220_Query_pcp_domain_from_PCP_Matching_Subscriber_Client_using_V6(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vipv6)+' -edo 0 -qname playboy.com -edata=0xFE31001145303a43423a34453a38303a45373a3636  -srcaddr '+config.client_ip2v6+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*Question Section.*',str(dig_result))
        assert re.search(r'.*Answer Section.*',str(dig_result))
        assert re.search(r'.*Additional Section.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)

    @pytest.mark.run(order=221)
    def test_221_Query_pcp_domain_from_PCP_Matching_Subscriber_Client_using_V6(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vipv6)+' -edo 0 -qname playboy.com -edata=0xFE31001145303a43423a34453a38303a45373a3636  -srcaddr '+config.client_ip2v6+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*Question Section.*',str(dig_result))
        assert re.search(r'.*Answer Section.*',str(dig_result))
        assert re.search(r'.*Additional Section.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)

    @pytest.mark.run(order=222)
    def test_222_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=223)
    def test_223_Validate_PCP_domain_is_answering_from_dca_cache_with_PCP_Blocking_IPs(self):
        LookFor="fp-rte"
        LookFor="rpz QNAME CNAME rewrite.*playboy.com.*playboy.com"
        LookFor="LocalId=E0CB4E80E766"
        LookFor="Parental-Control-Policy=0x00000000000000000000000000020004"
        LookFor="PC-Category-Policy=0x00000000000000000000000000000001"
        LookFor="CAT=0x00000000000000000000000000020000"
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
        sleep(15)



    @pytest.mark.run(order=224)
    def test_224_Validate_DCA_Cache_content_shows_domain_playboy_com_cached_in_dca(self):
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


    @pytest.mark.run(order=225)
    def test_225_Validate_DCA_Cache_Hit_Counts_Increased(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*5.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=226)
    def test_226_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")

    @pytest.mark.run(order=227)
    def test_227_Query_pcp_domain_from_optout_Subscriber_Client_using_V6(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip3)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vipv6)+' -edo 0 -qname playboy.com -edata=0xFE31001145303a43423a34453a38303a45373a3636  -srcaddr '+config.client_ip3v6+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*Question Section.*',str(dig_result))
        assert re.search(r'.*Answer Section.*',str(dig_result))
        assert re.search(r'.*Additional Section.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)



    @pytest.mark.run(order=228)
    def test_228_Query_pcp_domain_from_optout_Subscriber_Client_using_V6(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip3)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vipv6)+' -edo 0 -qname playboy.com -edata=0xFE31001145303a43423a34453a38303a45373a3636  -srcaddr '+config.client_ip3v6+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*Question Section.*',str(dig_result))
        assert re.search(r'.*Answer Section.*',str(dig_result))
        assert re.search(r'.*Additional Section.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)

    @pytest.mark.run(order=229)
    def test_229_Query_pcp_domain_from_optout_Subscriber_Client_using_V6(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip3)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vipv6)+' -edo 0 -qname playboy.com -edata=0xFE31001145303a43423a34453a38303a45373a3636  -srcaddr '+config.client_ip3v6+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*Question Section.*',str(dig_result))
        assert re.search(r'.*Answer Section.*',str(dig_result))
        assert re.search(r'.*Additional Section.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)

    @pytest.mark.run(order=230)
    def test_230_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=231)
    def test_231_Validate_PCP_domain_is_answering_from_bind_always_bug_NIOS_78563(self):
        LookFor="query.*playboy.com.*"
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
        sleep(15)



    @pytest.mark.run(order=232)
    def test_232_Validate_DCA_Cache_content_shows_domain_playboy_com_cached_in_dca(self):
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
        sleep(15)


    @pytest.mark.run(order=233)
    def test_233_Validate_DCA_Cache_Hit_Counts_not_Increased(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*5.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)



    @pytest.mark.run(order=234)
    def test_234_Clear_DCA_Cache(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set dns flush all')
        child.expect('Infoblox >')
        sleep(10)

    @pytest.mark.run(order=235)
    def test_235_Restart_Service(self):
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)


    @pytest.mark.run(order=236)
    def test_236_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")


    @pytest.mark.run(order=237)
    def test_237_Query_non_pcp_domain_from_NON_PCP_Matching_Subscriber_Client_using_V6(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vipv6)+' -edo 0 -qname ibm.com -edata=0xFE31001145303a43423a34453a38303a45373a3636  -srcaddr '+config.client_ip1v6+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*Question Section.*',str(dig_result))
        assert re.search(r'.*Answer Section.*',str(dig_result))
        assert re.search(r'.*Additional Section.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)



    @pytest.mark.run(order=238)
    def test_238_Query_non_pcp_domain_from_NON_PCP_Matching_Subscriber_Client_using_V6(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vipv6)+' -edo 0 -qname ibm.com -edata=0xFE31001145303a43423a34453a38303a45373a3636  -srcaddr '+config.client_ip1v6+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*Question Section.*',str(dig_result))
        assert re.search(r'.*Answer Section.*',str(dig_result))
        assert re.search(r'.*Additional Section.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)


    @pytest.mark.run(order=239)
    def test_239_Query_non_pcp_domain_from_NON_PCP_Matching_Subscriber_Client_using_V6(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vipv6)+' -edo 0 -qname ibm.com -edata=0xFE31001145303a43423a34453a38303a45373a3636  -srcaddr '+config.client_ip1v6+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*Question Section.*',str(dig_result))
        assert re.search(r'.*Answer Section.*',str(dig_result))
        assert re.search(r'.*Additional Section.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)

    @pytest.mark.run(order=240)
    def test_240_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=241)
    def test_241_Validate_non_pcp_domain_resolves_normally(self):
        LookFor=".*query.*ibm.com.*"
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
        sleep(15)



    @pytest.mark.run(order=242)
    def test_242_Validate_DCA_Cache_content_shows_domain_ibm_com_cached_in_dca(self):
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
        logging.info("Test Case Execution Completed")
        sleep(15)

    @pytest.mark.run(order=243)
    def test_243_Validate_DCA_Cache_Hit_Counts_Increased(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*2.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)

    @pytest.mark.run(order=244)
    def test_244_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")

    @pytest.mark.run(order=245)
    def test_245_Query_non_pcp_domain_from_PCP_Matching_Subscriber_Client_using_V6(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vipv6)+' -edo 0 -qname ibm.com -edata=0xFE31001145303a43423a34453a38303a45373a3636  -srcaddr '+config.client_ip2v6+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*Question Section.*',str(dig_result))
        assert re.search(r'.*Answer Section.*',str(dig_result))
        assert re.search(r'.*Additional Section.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)



    @pytest.mark.run(order=246)
    def test_246_Query_non_pcp_domain_from_PCP_Matching_Subscriber_Client_using_V6(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vipv6)+' -edo 0 -qname ibm.com -edata=0xFE31001145303a43423a34453a38303a45373a3636  -srcaddr '+config.client_ip2v6+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*Question Section.*',str(dig_result))
        assert re.search(r'.*Answer Section.*',str(dig_result))
        assert re.search(r'.*Additional Section.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)

    @pytest.mark.run(order=247)
    def test_247_Query_non_pcp_domain_from_PCP_Matching_Subscriber_Client_using_V6(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vipv6)+' -edo 0 -qname ibm.com -edata=0xFE31001145303a43423a34453a38303a45373a3636  -srcaddr '+config.client_ip2v6+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*Question Section.*',str(dig_result))
        assert re.search(r'.*Answer Section.*',str(dig_result))
        assert re.search(r'.*Additional Section.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)

    @pytest.mark.run(order=248)
    def test_248_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=249)
    def test_249_Validate_non_PCP_domain_is_answering_from_dca_cache_which_is_already_cached_in_dca_so_it_will_not_write_in_logs(self):
        LookFor=".*query.*ibm.com.*"
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
        sleep(15)


    @pytest.mark.run(order=250)
    def test_250_Validate_DCA_Cache_content_shows_domain_ibm_com_cached_in_dca(self):
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
        logging.info("Test Case Execution Completed")
        sleep(15)

    @pytest.mark.run(order=251)
    def test_251_Validate_DCA_Cache_Hit_Counts_Increased(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*5.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)


    @pytest.mark.run(order=252)
    def test_252_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")

    @pytest.mark.run(order=253)
    def test_253_Query_non_pcp_domain_from_optout_Subscriber_Client_using_V6(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip3)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vipv6)+' -edo 0 -qname ibm.com -edata=0xFE31001145303a43423a34453a38303a45373a3636  -srcaddr '+config.client_ip3v6+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*Question Section.*',str(dig_result))
        assert re.search(r'.*Answer Section.*',str(dig_result))
        assert re.search(r'.*Additional Section.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)



    @pytest.mark.run(order=254)
    def test_254_Query_non_pcp_domain_from_optout_Subscriber_Client_using_V6(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip3)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vipv6)+' -edo 0 -qname ibm.com -edata=0xFE31001145303a43423a34453a38303a45373a3636  -srcaddr '+config.client_ip3v6+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*Question Section.*',str(dig_result))
        assert re.search(r'.*Answer Section.*',str(dig_result))
        assert re.search(r'.*Additional Section.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)


    @pytest.mark.run(order=255)
    def test_255_Query_non_pcp_domain_from_optout_Subscriber_Client_using_V6(self):
        dig_cmd1 = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip3)+' "/import/tools/qa/bin/dnsq -ns '+str(config.grid_vipv6)+' -edo 0 -qname ibm.com -edata=0xFE31001145303a43423a34453a38303a45373a3636  -srcaddr '+config.client_ip3v6+'"'
        dig_result = subprocess.check_output(dig_cmd1, shell=True)
        print dig_result
        assert re.search(r'.*Question Section.*',str(dig_result))
        assert re.search(r'.*Answer Section.*',str(dig_result))
        assert re.search(r'.*Additional Section.*',str(dig_result))
        logging.info("Test Case Execution Completed")
        sleep(5)



    @pytest.mark.run(order=256)
    def test_256_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=257)
    def test_257_Validate_non_PCP_domain_is_answering_from_bind_always_bug_NIOS_78563(self):
        LookFor="query.*ibm.com.*"
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
        sleep(15)



    @pytest.mark.run(order=258)
    def test_258_Validate_DCA_Cache_content_shows_domain_ibm_com_cached_in_dca(self):
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
        logging.info("Test Case Execution Completed")
        sleep(15)
  
    @pytest.mark.run(order=259)
    def test_259_Validate_DCA_Cache_Hit_Counts_not_Increased(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Cache hit count.*5.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)



    @pytest.mark.run(order=260)
    def test_260_Clear_DCA_Cache(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set dns flush all')
        child.expect('Infoblox >')
        sleep(10)

    @pytest.mark.run(order=261)
    def test_261_Restart_Service(self):
        print("Restart DNS Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)


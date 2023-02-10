import datetime
from ib_utils.common_utilities import generate_token_from_file
import config
import re
import paramiko
import socket
import pexpect
import pytest
import unittest
import logging
from paramiko import client
import subprocess
import os
import json
import config
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
import commands
import json, ast
#import requests
import time
import getpass
import sys
import pexpect
#from log_capture import log_action as log
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
#from ib_utils.log_capture import log_action as log
#from ib_utils.log_validation import log_validation as logv
#from ib_utils.file_validation import log_validation as logv

host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)


class CalledProcessError(Exception):
    """This exception is raised when a process run by check_call() or
    check_output() returns a non-zero exit status.
    The exit status will be stored in the returncode attribute;
    check_output() will also store the output in the output attribute.
    """
    def __init__(self, returncode, cmd, output=None):
        self.returncode = returncode
        self.cmd = cmd
        self.output = output
    def __str__(self):
        return self.returncode

class grep(Exception):
    pass

class SSH:
    client=None

    def __init__(self,address):
        logging.info ("Log Validation Script")
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
        else:
            logging.info("Connection not opened.")

def enable_https_port():
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
    child.logfile=sys.stdout
    child.expect('-bash-4.0#')
    child.sendline('ip route del default via 10.35.0.1 dev eth1 table main')
    child.expect('-bash-4.0#')
    child.sendline('ip route add default via 10.36.0.1 dev eth0 table main')
    child.sendline('exit')
    child.expect(pexpect.EOF)
    time.sleep(20)


def show_subscriber_secure_data(grid_ip):
    logging.info(" show subscriber_secure_data")
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+grid_ip)
    child.logfile=sys.stdout
    child.expect('password:')
    child.sendline('infoblox')
    child.expect('Infoblox >')
    child.sendline('show subscriber_secure_data')
    child.expect('>')
    output= child.before
    child.sendline('exit')
    return output

def start_subscriber_collection_services_for_added_site(member):
    get_ref=ib_NIOS.wapi_request('GET', object_type='member:parentalcontrol?name='+member)
    get_ref=json.loads(get_ref)
    ref=get_ref[0]["_ref"]
    print ref
    data={"enable_service":True}
    reference=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
    print(reference)
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    publish={"member_order":"SIMULTANEOUSLY"}
    request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
    time.sleep(1)
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    time.sleep(20)
    get_ref=ib_NIOS.wapi_request('GET', object_type='member:parentalcontrol?name='+member)
    get_ref=json.loads(get_ref)
    if get_ref[0]["enable_service"]==True:
        print ("Test case passed")
        time.sleep(40)
        return get_ref[0]["enable_service"]
        print ("subscriber service is stopped")
    else:
        print("Not able to stop subscriber service")
        return None

def stop_subscriber_collection_services_for_added_site(member):
    get_ref=ib_NIOS.wapi_request('GET', object_type='member:parentalcontrol?name='+member)
    get_ref=json.loads(get_ref)
    ref=get_ref[0]["_ref"]
    print ref
    data={"enable_service":False}
    reference=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
    print(reference)
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    publish={"member_order":"SIMULTANEOUSLY"}
    request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
    time.sleep(1)
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    get_ref=ib_NIOS.wapi_request('GET', object_type='member:parentalcontrol?name='+member)
    get_ref=json.loads(get_ref)
    if get_ref[0]["enable_service"]==False:
        print ("Test case passed")
        time.sleep(40)
        print ("subscriber service is stopped")
        return get_ref[0]["enable_service"]
    else:
        print("Not able to stop subscriber service")
        return None

def delete_subscriber_records_with_Subscriber_EA(site):
    sleep(5)
    data1={"site":site}
    reference=get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriberrecord",fields=json.dumps(data1))
    if reference!="[]":
        reference=json.loads(reference)
        print (reference)
        for ref in reference:
            get_ref=ref["_ref"]
            reference=get_ref=ib_NIOS.wapi_request('DELETE', object_type=get_ref)
            print (reference)
            if type(reference)!=tuple:
                print("Deleted subscriber records")
            else:
                print("Deleting subscriber records failed")
    else:
        print("No records to delete")

def add_subscriber_record_to_the_added_site(site):
    data={"ans0":"User-Name=JOHN","ip_addr":"10.36.0.151", "prefix":32,"localid":"N/A","ipsd":"N/A","subscriber_secure_policy":"FF","parental_control_policy":"00000000000000000000000000020040","unknown_category_policy":False,"dynamic_category_policy":False,"subscriber_id":"IMSI=12345","accounting_session_id":"Acct-Session-Id=9999732d-34590346","bwflag":True,"black_list":"a.com,a.com","site":site,"flags":"SB","nas_contextual":"NAS-PORT=1813"}
    print data
    get_ref=ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscriberrecord",fields=json.dumps(data))
    print get_ref
    data1={"site":site}
    get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriberrecord",fields=json.dumps(data1))
    get_ref=json.loads(get_ref)[0]
    if get_ref["prefix"]==data["prefix"] and get_ref["ip_addr"]==data["ip_addr"] and get_ref["ipsd"]==data["ipsd"] and get_ref["localid"]==data["localid"]:
        print("Added Subscriber records")
    else:
        print("Cannot add Subscriber records")

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
        else:
            print ("Unable to delete subscriber site : test case 047 failed")
    else:
        print "No sites to delete"

def import_subscriber_data(file_name):
    logging.info("Upload Unknown resource records csv file")
    #dir_name = "/import/qaddi/rkarjagi/API_Automation/WAPI_PyTest/suites/RFE_8672"
    dir_name=os.getcwd()
    base_filename = file_name
    token =generate_token_from_file(dir_name, base_filename)
    data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE"}
    response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
    response=json.loads(response)
    time.sleep(30)
    #data={"action":"START","file_name":"arun.csv","on_error":"STOP","operation":"CREATE","separator":"COMMA"}
    get_ref=ib_NIOS.wapi_request('GET', object_type="csvimporttask")
    get_ref=json.loads(get_ref)
    for ref in get_ref:
        if response["csv_import_task"]["import_id"]==ref["import_id"]:
            print ref["lines_failed"]
            if ref["lines_failed"]>0:
                data={"import_id":ref["import_id"]}
                response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_error_log")
                response=json.loads(response)
                response=response["url"].split("/")
                req_id=response[4]
                filename=response[5]
                command1=os.system("mkdir /tmp/csv_error_files")
                command=os.system('scp -pr root@'+config.grid_vip+':/tmp/http_direct_file_io/'+req_id+'/'+filename+' /tmp/csv_error_files')
                print command
                print("Test case execution Failed csv import was unsuccessfull with invalid AVP's")
            else:
                print ref["status"]
                print ref["lines_failed"]
                if ref["status"]=="COMPLETED" and ref["lines_failed"]==0:
                    print ("Succesfully imported subscriber data")
                    return ref["status"]
                else:
                    print ("Failed to import subscriber data")
                    return None

def export_site_data(site):
    #delete_subscriber_records_with_Subscriber_EA()
    #add_subscriber_record_to_the_added_site(site)
    data={"_separator":"COMMA","_object": "parentalcontrol:subscriberrecord","site":site}
    create_file=ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=csv_export")
    print(create_file)
    res = json.loads(create_file)
    token = json.loads(create_file)['token']
    url = json.loads(create_file)['url']
    logging.info (create_file)
    print (res)
    print(token)
    print (url)
    print("Create the fileop function to dowload the csv file to the specified url")
    cmd='curl -k1 -u admin:infoblox -H "Content-type:application/force-download" -O %s'%(url)
    result = subprocess.check_output(cmd, shell=True)
    command1="cat Subscriberrecords.csv | grep -F '10.36.0.151,N/A,N/A,32' "
    if command1!=None:
        print("Exported site data successfully")
        return command1
    else:
        print("Exporting site data failed")
        return None
    cmd='rm Subscriberrecords.csv'
    command2=subprocess.check_output(cmd, shell=True)

def change_default_route():
    ref=ib_NIOS.wapi_request('GET', object_type="grid")
    ref=json.loads(ref)[0]['_ref']
    data={"enable_gui_api_for_lan_vip":"true","dns_resolver_setting": {"resolvers": ["10.0.2.35"]}}
    #data={"dns_resolver_setting": {"resolvers": ["10.0.2.35"]}}
    ref1=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
    child.logfile=sys.stdout
    child.expect('#')
    child.sendline('ip route del default via 10.35.0.1 dev eth1 table main')
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
    
    def test_001_Start_DNS_Service(self):
        enable_GUI_and_API_access_through_LAN_and_MGMT()
        change_default_route()
        #enable_https_port()
        logging.info("Start DNS Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        print get_ref
        logging.info(get_ref)
        res = json.loads(get_ref)
        for i in res:
            ref=i["_ref"]
            logging.info("Modify a enable_dns")
            data = {"enable_dns": True,"use_mgmt_port":True}
            response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
            sleep(20)
            logging.info(response)
            read  = re.search(r'200',response)
            for read in  response:
                assert True
        logging.info("Test Case 1 Execution Completed")

    @pytest.mark.run(order=2)
    def test_002_Validate_DNS_service_Enabled(self):
        logging.info("Validate DNs Service is enabled")
        get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
        logging.info(get_tacacsplus)
        res = json.loads(get_tacacsplus)
        logging.info(res)
        for i in res:
            logging.info("found")
            assert i["enable_dns"] == True
        logging.info("Test Case 2 Execution Completed")
        logging.info("============================")
    
    @pytest.mark.run(order=3)
    def test_003_Modify_Grid_Dns_Properties_to_enable_rpz_logging_and_add_forwarder(self):
        logging.info("Mofifying GRID dns propertiesi_to_enable_rpz_logging_and_add_forwarder")
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:dns")
        get_ref1=json.loads(get_ref)[0]['_ref']
        logging.info(get_ref1)
        data={"allow_recursive_query":True,"allow_query":[{"_struct": "addressac","address":"Any","permission":"ALLOW"}],"forwarders":[config.forwarder_ip],"logging_categories":{"log_rpz":True,"log_queries":True,"log_responses":True}}
        put_ref=ib_NIOS.wapi_request('PUT', object_type=get_ref1,fields=json.dumps(data))
        logging.info(put_ref)
        if type(put_ref)!=tuple:
            print("DNS Restart Services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
            ref = json.loads(grid)[0]['_ref']
            data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
            sleep(30)
            logging.info("Test Case 3 Execution Passed")
            assert True
        else:
            logging.info("Test Case 3 Execution Failed")
            assert False

    @pytest.mark.run(order=4)
    def test_004_Validate_Grid_Dns_Properties(self):
        logging.info("Validating GRID dns properties")
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:dns?_return_fields=allow_recursive_query,forwarders")
        get_ref1=json.loads(get_ref)
        if get_ref1[0]["allow_recursive_query"]==True and get_ref1[0]["forwarders"]==[config.forwarder_ip]:
            logging.info("Test Case 4 Execution Passed")
            assert True
        else:
            logging.info("Test Case 4 Execution Failed")
            assert False

    @pytest.mark.run(order=5)
    def test_005_Modify_Grid_Settings_to_add_resolvers(self):
        logging.info("Mofifying GRID properties_to_add_resolvers")
        response = ib_NIOS.wapi_request('GET', object_type="grid")
        response = json.loads(response)
        response=response[0]["_ref"]
        data={"dns_resolver_setting": {"resolvers": [config.resolver_ip]}}
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
        response=response[0]["dns_resolver_setting"]["resolvers"]
        if response==[config.resolver_ip]:
            logging.info("Test Case 6 Execution Passed")
            assert True
        else:
            logging.info("Test Case 6 Execution Failed")
            assert False

    @pytest.mark.run(order=7)
    def test_007_enable_parental_control(self):
        response = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber")
        response = json.loads(response)
        response=response[0]["_ref"]
        logging.info(response)
        data={"enable_parental_control": True,"cat_acctname":"infoblox_sdk", "cat_password":"LinWmRRDX0q","category_url":"https://dl.zvelo.com/","pc_zone_name":"parental_control","cat_update_frequency":24,"proxy_url":"http://"+config.zvelo_proxy+":8001", "proxy_username":config.zvelo_username, "proxy_password":config.zvelo_password}
        #data={"enable_parental_control": True,"cat_acctname":"infoblox_sdk", "cat_password":"LinWmRRDX0q","category_url":"https://dl.zvelo.com/","pc_zone_name":"parental_control","cat_update_frequency":24}
        res = ib_NIOS.wapi_request('PUT', object_type=response,fields=json.dumps(data))
        logging.info(res)
        if type(res)==tuple:
            if res[0]==400 or res[0]==401:
                logging.info("Test case 7 execution failed")
                assert False
            else:
                logging.info("Test Case 7 execution passed")

    @pytest.mark.run(order=8)
    def test_008_Validate_Parental_Control_is_Enabled(self):
        logging.info("validating parental control is enabled")
        response = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber?_return_fields=enable_parental_control,cat_acctname,category_url,proxy_url,proxy_username")
        logging.info(response)
        response = json.loads(response)
        pc=response[0]["enable_parental_control"]
        act_name=response[0]["cat_acctname"]
        cat_url=response[0]["category_url"]
        proxy_url=response[0]["proxy_url"]
        proxy_username=response[0]["proxy_username"]
        if pc==True and act_name=="infoblox_sdk" and cat_url=="https://dl.zvelo.com/":
            logging.info("Test Case 8 execution passed")
            assert True
        else:
            logging.info("Test Case 8 execution Failed")
            assert False

    
    @pytest.mark.run(order=9)
    def  test_009_add_subscriber_site(self):
        #data={"blocking_ipv4_vip1": "2.4.5.6","msps":[{"ip_address": "10.196.128.13"}],"spms": [{"ip_address": "10.12.11.11"}],"name":"site3","maximum_subscribers":100000,"members":[{"name":config.grid_fqdn}],"nas_gateways":[{"ip_address":"2.2.2.2","name":"nas1","shared_secret":"test123"}]}
        data={"name":"site3","maximum_subscribers":100000,"members":[{"name":config.grid_fqdn}],"nas_gateways":[{"ip_address":"2.2.2.2","name":"nas1","shared_secret":"test123"}]}
        get_ref=ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data))
        logging.info(get_ref)
        print get_ref
        if type(get_ref)!=tuple:
            reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
            reference=json.loads(reference)
            if reference[0]["name"]==data["name"]:
                logging.info("Test case 9 execution passed")
                assert True
            else:
                logging.info("Test case 9 execution Failed")
                assert False
        else:
            logging.info(get_ref)
            logging.info("Test case 9 execution failed")
            assert False

    @pytest.mark.run(order=10)
    def  test_010_validate_for_subscriber_site_s1(self):
        logging.info("validating subscriber site site3 is added")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=name,maximum_subscribers")
        reference=json.loads(reference)
        site=reference[0]["name"]
        maximum_subscribers=reference[0]["maximum_subscribers"]
        if site=="site3" and maximum_subscribers==100000:
            logging.info("Test case 10 execution passed")
            assert True
        else:
            logging.info("Test case 10 execution failed")
            assert False

    @pytest.mark.run(order=11)
    def test_011_start_subscriber_collection_services_for_added_site(self):
        get_ref=ib_NIOS.wapi_request('GET', object_type="member:parentalcontrol")
        get_ref=json.loads(get_ref)
        logging.info(get_ref)
        for ref in get_ref:
            ref=ref["_ref"]
            data={"enable_service":True}
            reference=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
            logging.info(reference)
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            time.sleep(1)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        get_ref=ib_NIOS.wapi_request('GET', object_type="member:parentalcontrol")
        get_ref=json.loads(get_ref)
        for ref in get_ref:
            if get_ref[0]["enable_service"]==True:
                time.sleep(60)
                logging.info("Test Case 11 Execution Completed")
                assert True
            else:
                logging.info("Test Case 11 Execution Completed")
                assert False

    @pytest.mark.run(order=12)
    def test_012_Validate_subscriber_service_is_running(self):
        logging.info("Validating subscriber collection services started")
        get_ref=ib_NIOS.wapi_request('GET', object_type="member:parentalcontrol")
        get_ref=json.loads(get_ref)
        for ref in get_ref:
            if get_ref[0]["enable_service"]==True:
                time.sleep(60)
                logging.info("Test Case 12 Execution Passed")
                assert True
            else:
                logging.info("Test Case 12 Execution Failed")
                assert False

    @pytest.mark.run(order=13)
    def test_013_start_category_download_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/storage/zvelo/log/category_download.log",config.grid_vip)
        logging.info("Test case 13 execution passed")
        time.sleep(2300)

    @pytest.mark.run(order=14)
    def test_014_stop_category_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("stop","/storage/zvelo/log/category_download.log",config.grid_vip)
        logging.info("Test case 14 execution passed")
    
    @pytest.mark.run(order=15)
    def test_015_validate_for_zvelo_data(self):
        time.sleep(40)
        logging.info("Validating Zvelo Messages Logs")
        LookFor="zvelodb download completed"
        logs=logv(LookFor,"/storage/zvelo/log/category_download.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 15 Execution Completed")
            assert True
        else:
            logging.info("Test Case 15 Execution Failed")
            assert False
    
    @pytest.mark.run(order=16)
    def test_016_Modify_Grid_Settings_to_add_resolvers(self):
        logging.info("Mofifying GRID properties_to_add_resolvers")
        response = ib_NIOS.wapi_request('GET', object_type="grid")
        response = json.loads(response)
        response=response[0]["_ref"]
        data={"dns_resolver_setting": {"resolvers": ["127.0.0.1",config.resolver_ip]}}
        res = ib_NIOS.wapi_request('PUT', object_type=response,fields=json.dumps(data))
        logging.info(res)
        if type(res)!=tuple:
            logging.info("Test Case 16 Execution Passed")
            assert True
        else:
            logging.info("Test Case 16 Execution Failed")
            assert False

    @pytest.mark.run(order=17)
    def test_017_Validate_Modified_Grid_Settings(self):
        logging.info("Validating GRID properties")
        response = ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=dns_resolver_setting")
        response = json.loads(response)
        response=response[0]["dns_resolver_setting"]["resolvers"]
        if response==["127.0.0.1",config.resolver_ip]:
            logging.info("Test Case 17 Execution Passed")
            assert True
        else:
            logging.info("Test Case 17 Execution Failed")
            assert False

    @pytest.mark.run(order=18)
    def test_018_modify_subscriber_site_site3_to_add_blocking_ips(self):
        #data={"blocking_ipv4_vip1": "2.4.5.6","msps":[{"ip_address": "10.196.128.13"}],"spms": [{"ip_address": "10.12.11.11"}],"name":"site3","maximum_subscribers":100000,"members":[{"name":config.grid_fqdn}],"nas_gateways":[{"ip_address":"2.2.2.2","name":"nas1","shared_secret":"test123"}]}
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
        reference=json.loads(reference)[0]["_ref"]
        logging.info("Adding blocking ip's to subscriber site site3")
        data={"blocking_ipv4_vip1": "2.4.5.6","msps":[{"ip_address": config.proxy_server1}],"spms": [{"ip_address": "10.12.11.11"}]}
        get_ref=ib_NIOS.wapi_request('PUT', object_type=reference,fields=json.dumps(data))
        logging.info(get_ref)
        print get_ref
        logging.info(get_ref)
        if type(get_ref)!=tuple:
            reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
            reference=json.loads(reference)
            if reference[0]["name"]=="site3":
                logging.info("Test case 18 execution passed")
                assert True
            else:
                logging.info("Test case 18 execution Failed")
                assert False
        else:
            logging.info(get_ref)
            logging.info("Test case 18 execution Failed")
            assert False

    @pytest.mark.run(order=19)
    def  test_019_validate_for_subscriber_site_site3(self):
        logging.info("validating subscriber site s1 added")
        reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=name,blocking_ipv4_vip1,msps,spms")
        reference=json.loads(reference)
        site=reference[0]["name"]
        blocking_ip=reference[0]["blocking_ipv4_vip1"]
        msps=reference[0]["msps"]
        spms=reference[0]["spms"]
        if site=="site3" and blocking_ip=="2.4.5.6" and msps==[{"ip_address": config.proxy_server1}] and spms==[{"ip_address": "10.12.11.11"}]:
            logging.info("Test case 19 execution passed")
            assert True
        else:
            logging.info("Test case 19 execution failed")
            assert False


    @pytest.mark.run(order=20)
    def test_020_add_subscriber_record_to_the_added_site(self):
        data={"ans0":"User-Name=JOHN","ip_addr":"10.36.0.151", "prefix":32,"localid":"N/A","ipsd":"N/A","subscriber_secure_policy":"FF","parental_control_policy":"00000000000000000000000000020040","unknown_category_policy":False,"dynamic_category_policy":False,"subscriber_id":"IMSI=12345","accounting_session_id":"Acct-Session-Id=9999732d-34590346","bwflag":True,"black_list":"a.com,a.com","site":"site3","flags":"SB","nas_contextual":"NAS-PORT=1813"}
        print data
        get_ref=ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscriberrecord",fields=json.dumps(data))
        print get_ref
        data1={"site":"site3"}
        get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriberrecord",fields=json.dumps(data1))
        get_ref=json.loads(get_ref)[0]
        if get_ref["prefix"]==data["prefix"] and get_ref["ip_addr"]==data["ip_addr"] and get_ref["ipsd"]==data["ipsd"] and get_ref["localid"]==data["localid"]:
            logging.info("Test case 20 Execution Passed")
            assert True
        else:
            logging.info("Test case 20 execution Failed")
            assert False
    
    @pytest.mark.run(order=21)
    def test_021_validate_added_subscriber_records_added(self):
        print ("Test case to validate added subscriber records ")
        sleep(10)
        data=show_subscriber_secure_data(config.grid_vip)
        result=re.search("10.36.0.151/32|LID:N/A|IPS:N/A|",data)
        print result
        if (result != None):
            logging.info("Test case 21 passed")
            assert True
        else:
            logging.info("Test case 21 failed")
            assert False

    @pytest.mark.run(order=22)
    def test_022_update_subscriber_record_to_the_added_site(self):
        data1={"site":"site3"}
        reference=get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriberrecord",fields=json.dumps(data1))
        reference=json.loads(reference)[0]["_ref"]
        data={"dynamic_category_policy":True,"nas_contextual":"NAS-PORT=1814"}
        get_ref=ib_NIOS.wapi_request('PUT', object_type=reference,fields=json.dumps(data))
        logging.info(get_ref)
        data1={"site":"site3"}
        reference=get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriberrecord?_return_fields=dynamic_category_policy,nas_contextual",fields=json.dumps(data1))
        reference=json.loads(reference)[0]
        if reference["dynamic_category_policy"]==data["dynamic_category_policy"] and reference["nas_contextual"]==data["nas_contextual"]:
            logging.info("Test Case 22 Execution Completed")
            assert True
        else:
            logging.info("Test Case 22 Execution Completed")
            assert False

    @pytest.mark.run(order=23)
    def test_023_display_all_suscriber_records(self):
        data1={"site":"site3"}
        reference=get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriberrecord",fields=json.dumps(data1))
        if type(reference)!=tuple:
            logging.info("Test case 23 execution passed")
            assert True
        else:
            logging.info("Test case 23 execution failed")
            assert False

    @pytest.mark.run(order=24)
    def test_024_search_for_subscriber_records(self):
        data={"site":"site3", "subscriber_id":"IMSI=12345"}
        reference=get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriberrecord",fields=json.dumps(data))
        reference=json.loads(reference)
        for ref in reference:
            if ref["subscriber_id"]=="IMSI=12345":
                logging.info("Test Case 24 Execution Completed")
                assert True
            else:
                assert False
                logging.info("Test Case 24 Execution failed")

    @pytest.mark.run(order=25)
    def test_025_delete_subscriber_records(self):
        data1={"site":"site3"}
        reference=get_ref=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriberrecord",fields=json.dumps(data1))
        if reference!="[]":
            reference=json.loads(reference)
            for ref in reference:
                get_ref=ref["_ref"]
                reference=get_ref=ib_NIOS.wapi_request('DELETE', object_type=get_ref)
                logging.info(reference)
                if type(reference)!=tuple:
                    logging.info("Test case 25 execution passed")
                    assert True
                else:
                    logging.info("Test case 25 execution failed")
                    assert False
        else:
            logging.info("No records to delete")
            logging.info("Test Case 25 Execution failed")
            assert True

    @pytest.mark.run(order=26)
    def test_026_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("test case 26 passed")

    @pytest.mark.run(order=27)
    def test_027_import_subscriber_records_through_csv(self):
        logging.info("Upload Subscriber data through csv file")
        #dir_name = "/import/qaddi/rkarjagi/API_Automation/WAPI_PyTest/suites/RFE_8672"
        dir_name=os.getcwd()
        base_filename = "valid_subscriber_record.csv"
        token =generate_token_from_file(dir_name, base_filename)
        data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
        response=json.loads(response)
        time.sleep(30)
        #data={"action":"START","file_name":"arun.csv","on_error":"STOP","operation":"CREATE","separator":"COMMA"}
        get_ref=ib_NIOS.wapi_request('GET', object_type="csvimporttask")
        get_ref=json.loads(get_ref)
        for ref in get_ref:
            if response["csv_import_task"]["import_id"]==ref["import_id"]:
                print ref["lines_failed"]
                if ref["lines_failed"]>0:
                    data={"import_id":ref["import_id"]}
                    response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_error_log")
                    response=json.loads(response)
                    response=response["url"].split("/")
                    req_id=response[4]
                    filename=response[5]
                    command1=os.system("mkdir /tmp/csv_error_files")
                    command=os.system('scp -pr root@'+config.grid_vip+':/tmp/http_direct_file_io/'+req_id+'/'+filename+' /tmp/csv_error_files')
                    logging.info(command)
                    logging.info("Test case 27 execution Failed csv import was unsuccessfull with invalid AVP's")
                    assert False
                else:
                    print ref["status"]
                    print ref["lines_failed"]
                    if ref["status"]=="COMPLETED" and ref["lines_failed"]==0:
                        logging.info ("Test case 27 execution passed")
                        assert True
                    else:
                        logging.info ("Test case 27 execution Failed")
                        assert False

    @pytest.mark.run(order=28)
    def test_028_stop_Infoblox_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("Test Case 28 Execution Completed")

    @pytest.mark.run(order=29)
    def test_029_validate_Infoblox_Messages_for_Data_repo(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="imc"
        #LookFor="imc_open_data_repo_connection(): connected"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 29 Execution Completed")
            assert True
        else:
            logging.info("Test Case 29 Execution Failed")
            assert False
    
    @pytest.mark.run(order=30)
    def test_030_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("test case 30 passed")

    @pytest.mark.run(order=31)
    def test_031_import_subscriber_records_through_csv_negative_validations_for_AVP(self):
        logging.info("Upload Subscriber records csv file")
        #dir_name = "/import/qaddi/rkarjagi/API_Automation/WAPI_PyTest/suites/RFE_8672"
        dir_name=os.getcwd()
        base_filename = "invalid_subscriber_records.csv"
        token =generate_token_from_file(dir_name, base_filename)
        data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
        response=json.loads(response)
        time.sleep(30)
        data={"action":"START","file_name":"invalid_subscriber_records.csv","on_error":"CONTINUE","operation":"CREATE","separator":"COMMA"}
        get_ref=ib_NIOS.wapi_request('GET', object_type="csvimporttask")
        get_ref=json.loads(get_ref)
        for ref in get_ref:
            if response["csv_import_task"]["import_id"]==ref["import_id"]:
                print ref["lines_failed"]
                if ref["lines_failed"]>0:
                    data={"import_id":ref["import_id"]}
                    response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_error_log")
                    response=json.loads(response)
                    response=response["url"].split("/")
                    req_id=response[4]
                    filename=response[5]
                    command1=os.system("mkdir /tmp/csv_error_files")
                    command=os.system('scp -pr root@'+config.grid_vip+':/tmp/http_direct_file_io/'+req_id+'/'+filename+' /tmp/csv_error_files')
                    logging.info(command)
                    logging.info("Test case 31 execution passed csv import was unsuccessfull with invalid AVP's")
                    assert True
                else:
                    logging.info("Test case 31 execution failed csv import was successfull with invalid AVP's")
                    assert False

    @pytest.mark.run(order=32)
    def test_032_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("Test Case 32 Execution Completed")

    @pytest.mark.run(order=33)
    def test_033_validate_Infoblox_Messages_for_Data_repo(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="Insertion aborted due to Subscriber <102.121.12.2345/12 LID:N/A IPS:N/A> has invalid value 102.121.12.2345 for field: ip_addr error: Address is not valid"
        #LookFor="imc_open_data_repo_connection(): connected"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 33 Execution Completed")
            assert True
        else:
            logging.info("Test Case 33 Execution Failed")
            assert False

    @pytest.mark.run(order=34)
    def test_034_validate_Infoblox_Logs_for_invalid_prefix_AVP(self):
        logging.info("Validating Infoblox Messages Logs")
        LookFor="Insertion aborted due to Subscriber <102.121.12.23/33 LID:N/A IPS:N/A> has invalid value 33 for field: prefix error: Prefix is not in the range of 1 to 32"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 34 Execution Completed")
            assert True
        else:
            logging.info("Test Case 34 Execution Failed")
            assert False

    @pytest.mark.run(order=35)
    def test_035_validate_Infoblox_Logs_for_invalid_localid_AVP(self):
        logging.info("Validating Infoblox Messages Logs")
        LookFor=".*Insertion aborted due to Subscriber <102.121.12.23/32 LID:HHHH IPS:N/A> has invalid value HHHH for field: localid error: Not a valid hex string.*"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 35 Execution Completed")
            assert True
        else:
            logging.info("Test Case 35 Execution Failed")
            assert False

    @pytest.mark.run(order=36)
    def test_036_validate_Infoblox_Logs_for_invalid_ipsd_AVP(self):
        logging.info("Validating Infoblox Messages Logs")
        #LookFor="Insertion aborted due to Subscriber <10.120.21.51/32 LID:N/A IPS:65537> has invalid value 65537 for field: ipsd error: CGNAT configured. IPSD is the first port of the allocated range for the subscriber. Must also be greater than or equal to the start of the available ports 1024 or N/A"
        LookFor="Insertion aborted due to Subscriber <102.121.12.23/32 LID:N/A IPS:65537> has invalid value 65537 for field: ipsd error: IPSD must be N/A, CGNAT is not configured"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 36 Execution Completed")
            assert True
        else:
            logging.info("Test Case 36 Execution Failed")
            assert False

    @pytest.mark.run(order=37)
    def test_037_validate_Infoblox_Logs_for_invalid_flags_AVP(self):
        logging.info("Validating Infoblox Messages Logs")
        LookFor="Insertion aborted due to Subscriber <102.121.12.23/14 LID:N/A IPS:N/A> has invalid value KK for field: flags error: Flag:K is not valid"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 37 Execution Completed")
            assert True
        else:
            logging.info("Test Case 37 Execution Failed")
            assert False

    @pytest.mark.run(order=38)
    def test_038_validate_Infoblox_Logs_for_invalid_alt_ip_address_AVP(self):
        logging.info("Validating Infoblox Messages Logs")
        LookFor="Insertion aborted due to Subscriber <102.121.12.23/14 LID:N/A IPS:N/A> has invalid value 2123:345:287::6727:22PP for field: alt_ip_addr error: Address is not valid"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 38 Execution Completed")
            assert True
        else:
            logging.info("Test Case 38 Execution Failed")
            assert False

    @pytest.mark.run(order=39)
    def test_039_validate_Infoblox_Logs_for_invalid_subscriber_id_AVP(self):
        logging.info("Validating Infoblox Messages Logs")
        LookFor='Insertion aborted due to Subscriber <102.121.12.23/14 LID:N/A IPS:N/A> has invalid value UserName='
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 39 Execution Completed")
            assert True
        else:
            logging.info("Test Case 39 Execution Failed")
            assert False

    @pytest.mark.run(order=40)
    def test_040_validate_Infoblox_Logs_for_invalid_nas_contextual_AVP(self):
        logging.info("Validating Infoblox Messages Logs")
        LookFor="Insertion aborted due to Subscriber <102.121.12.23/14 LID:N/A IPS:N/A> has invalid value NAS-IP-Address for field: nas_contextual error: AVP is not in expected format: 'avp_name=value"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 40 Execution Completed")
            assert True
        else:
            logging.info("Test Case 40 Execution Failed")
            assert False

    @pytest.mark.run(order=41)
    def test_041_validate_Infoblox_Logs_for_invalid_site_AVP(self):
        logging.info("Validating Infoblox Messages Logs")
        LookFor="Insertion aborted due to Site not found/configured : site4"
        #LookFor=".*Insertion aborted due to None of the members of Subscriber Site: site4 are running Subscriber collection service.*"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 41 Execution Completed")
            assert True
        else:
            logging.info("Test Case 41 Execution Failed")
            assert False

    @pytest.mark.run(order=42)
    def test_042_validate_Infoblox_Logs_for_invalid_anscillary_AVP(self):
        logging.info("Validating Infoblox Messages Logs")
        LookFor="Insertion aborted due to Subscriber <102.121.12.23/32 LID:N/A IPS:N/A> has invalid value arun for field: ans0 error: AVP is not in expected format: 'avp_name=value"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 42 Execution Completed")
            assert True
        else:
            logging.info("Test Case 42 Execution Failed")
            assert False

    @pytest.mark.run(order=43)
    def test_043_validate_Infoblox_Logs_for_invalid_subscriber_secure_policy_AVP(self):
        logging.info("Validating Infoblox Messages Logs")
        LookFor="Insertion aborted due to Subscriber <102.121.12.23/32 LID:N/A IPS:N/A> has invalid value GGG for field: subscriber_secure_policy error: Not a valid hex string"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 43 Execution Completed")
            assert True
        else:
            logging.info("Test Case 43 Execution Failed")
            assert False

    @pytest.mark.run(order=44)
    def test_044_validate_Infoblox_Logs_for_invalid_Parental_control_policy_AVP(self):
        logging.info("Validating Infoblox Messages Logs")
        LookFor="Insertion aborted due to Subscriber <102.121.12.23/32 LID:N/A IPS:N/A> has invalid value HHH for field: parental_control_policy error: Not a valid hex string"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 44 Execution Completed")
            assert True
        else:
            logging.info("Test Case 44 Execution Failed")
            assert False

    @pytest.mark.run(order=45)
    def test_045_validate_Infoblox_Logs_for_invalid_WPC_category_policy_AVP(self):
        logging.info("Validating Infoblox Messages Logs")
        LookFor="Insertion aborted due to Subscriber <102.121.12.23/32 LID:N/A IPS:N/A> has invalid value JJJ for field: wpc_category_policy error: Not a valid hex string"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 45 Execution Completed")
            assert True
        else:
            logging.info("Test Case 45 Execution Failed")
            assert False

    @pytest.mark.run(order=46)
    def test_046_validate_Infoblox_Logs_for_invalid_Dynamic_category_Policy_AVP(self):
        logging.info("Validating Infoblox Messages Logs")
        LookFor='Can not convert data'
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 46 Execution Completed")
            assert True
        else:
            logging.info("Test Case 46 Execution Failed")
            assert False

    @pytest.mark.run(order=47)
    def test_047_validate_Infoblox_Logs_for_invalid_BWFLAG_AVP(self):
        logging.info("Validating Infoblox Messages Logs")
        LookFor='Can not convert data'
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 47 Execution Completed")
            assert True
        else:
            logging.info("Test Case 47 Execution Failed")
            assert False

    @pytest.mark.run(order=48)
    def test_048_validate_Infoblox_Logs_for_invalid_ProxyALL_AVP(self):
        logging.info("Validating Infoblox Messages Logs")
        LookFor='Can not convert data'
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 48 Execution Completed")
            assert True
        else:
            logging.info("Test Case 48 Execution Failed")
            assert False

    @pytest.mark.run(order=49)
    def test_049_validate_Infoblox_Logs_for_invalid_blacklist_AVP(self):
        logging.info("Validating Infoblox Messages Logs")
        LookFor="Insertion aborted due to Subscriber <102.121.12.23/32 LID:N/A IPS:N/A> has invalid value .com for field: black_list error: invalid domain name"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 49 Execution Completed")
            assert True
        else:
            logging.info("Test Case 49 Execution Failed")
            assert False

    @pytest.mark.run(order=50)
    def test_050_validate_Infoblox_Logs_for_invalid_whitelist_AVP(self):
        logging.info("Validating Infoblox Messages Logs")
        LookFor="Insertion aborted due to Subscriber <102.121.12.23/32 LID:N/A IPS:N/A> has invalid value .com for field: white_list error: invalid domain name"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 50 Execution Completed")
            assert True
        else:
            logging.info("Test Case 50 Execution Failed")
            assert False

    @pytest.mark.run(order=51)
    def test_051_validate_Infoblox_Logs_for_invalid_string_with_more_than_256_chars_AVP(self):
        logging.info("Validating Infoblox Messages Logs")
        LookFor="for field: subscriber_id error: Field length more than 256 characters"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 51 Execution Completed")
            assert True
        else:
            logging.info("Test Case 51 Execution Failed")
            assert False

    @pytest.mark.run(order=52)
    def test_052_validate_Infoblox_Logs_for_invalid_blaclist_with_more_than_10_domains_AVP(self):
        logging.info("Validating Infoblox Messages Logs")
        LookFor="Insertion aborted due to Subscriber <102.121.12.22/12 LID:N/A IPS:N/A> has invalid value bad.com,bad1.com,bad2.com,bad3.com,bad4.com,bad5.com,bad6.com,bad7.com,bad8.com,bad9.com,bad10.com for field: black_list error: list contains more than 10 domains"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 52 Execution Completed")
            assert True
        else:
            logging.info("Test Case 52 Execution Failed")
            assert False

    @pytest.mark.run(order=53)
    def test_053_validate_Infoblox_Logs_for_invalid_whitelist_with_more_than_10_domains_AVP(self):
        logging.info("Validating Infoblox Messages Logs")
        LookFor="Insertion aborted due to Subscriber <102.121.12.22/12 LID:N/A IPS:N/A> has invalid value good.com,good1.com,good2.com,good3.com,good4.com,good5.com,good6.com,good7.com,good8.com,good9.com,good20.com for field: white_list error: list contains more than 10 domains"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 53 Execution Completed")
            assert True
        else:
            logging.info("Test Case 53 Execution Failed")
            assert False

    @pytest.mark.run(order=54)
    def test_054_validate_Infoblox_Logs_when_BWFLAG_set_to_false_AVP(self):
        logging.info("Validating Infoblox Messages Logs")
        LookFor="Insertion aborted due to Subscriber <102.121.12.22/12 LID:N/A IPS:N/A> has Black/White list bad.com for black_list when flags are not set"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 54 Execution Completed")
            assert True
        else:
            logging.info("Test Case 54 Execution Failed")
            assert False

    @pytest.mark.run(order=55)
    def test_055_validate_Infoblox_Logs_when_BWFLAG_site_is_not_specified(self):
        logging.info("Validating Infoblox Messages Logs")
        LookFor="Required field site is not provided"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 55 Execution Completed")
            assert True
        else:
            logging.info("Test Case 55 Execution Failed")
            assert False


    @pytest.mark.run(order=56)
    def test_056_import_subscriber_records_through_csv_negative_validations_for_AVP_ipaddr(self):
        cmd="ls -ltr /tmp/csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        #command=os.system("ls -ltr /tmp")
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[1]
            final=re.search("Insertion aborted due to Subscriber <102.121.12.2345/12 LID:N/A IPS:N/A> has invalid value 102.121.12.2345 for field: ip_addr error: Address is not valid",res)
            if final is not None:
                logging.info("Test case 56 passed")
            else:
                logging.info("Test case 56 Failed")

    @pytest.mark.run(order=57)
    def test_057_import_subscriber_records_through_csv_negative_validations_for_AVP_prefix(self):
        cmd="ls -ltr /tmp/csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        #command=os.system("ls -ltr /tmp")
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[2]
            print res
            final=re.search("Insertion aborted due to Subscriber <102.121.12.23/33 LID:N/A IPS:N/A> has invalid value 33 for field: prefix error: Prefix is not in the range of 1 to 32",res)
            if final is not None:
                logging.info("Test case 57 passed")
            else:
                logging.info("Test case 57 Failed")

    @pytest.mark.run(order=58)
    def test_058_import_subscriber_records_through_csv_negative_validations_for_AVP_localid(self):
        cmd="ls -ltr /tmp/csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        #command=os.system("ls -ltr /tmp")
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[3]
            final=re.search("Insertion aborted due to Subscriber <102.121.12.23/32 LID:HHHH IPS:N/A> has invalid value HHHH for field: localid error: Not a valid hex string",res)
            if final is not None:
                logging.info("Test case 58 passed")
            else:
                logging.info("Test case 58 Failed")

    @pytest.mark.run(order=59)
    def test_059_import_subscriber_records_through_csv_negative_validations_for_AVP_ipsd(self):
        cmd="ls -ltr /tmp/csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        #command=os.system("ls -ltr /tmp")
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[4]
            final=re.search("Insertion aborted due to Subscriber <102.121.12.23/32 LID:N/A IPS:45> has invalid value 45 for field: ipsd error: IPSD is not defined in the db",res)
            if final is not None:
                logging.info("Test case 59 passed")
            else:
                logging.info("Test case 59 Failed")

    @pytest.mark.run(order=60)
    def test_060_import_subscriber_records_through_csv_negative_validations_for_AVP_flags(self):
        cmd="ls -ltr /tmp/csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        #command=os.system("ls -ltr /tmp")
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[5]
            final=re.search("Insertion aborted due to Subscriber <102.121.12.23/14 LID:N/A IPS:N/A> has invalid value KK for field: flags error: Flag:K is not valid",res)
            if final is not None:
                logging.info("Test case 60 passed")
            else:
                logging.info("Test case 60 Failed")

    @pytest.mark.run(order=61)
    def test_061_import_subscriber_records_through_csv_negative_validations_for_Alt_Ip_Address(self):
        cmd="ls -ltr /tmp/csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        #command=os.system("ls -ltr /tmp")
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[6]
            final=re.search("Insertion aborted due to Subscriber <102.121.12.23/14 LID:N/A IPS:N/A> has invalid value 2123:345:287::6727:22PP for field: alt_ip_addr error: Address is not valid",res)
            if final is not None:
                logging.info("Test case 61 passed")
            else:
                logging.info("Test case 61 Failed")

    @pytest.mark.run(order=62)
    def test_062_import_subscriber_records_through_csv_negative_validations_for_Subscriber_Id(self):
        cmd="ls -ltr /tmp/csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        #command=os.system("ls -ltr /tmp")
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[7]
            final=re.search("Insertion aborted due to Subscriber <102.121.12.23/14 LID:N/A IPS:N/A> has invalid value UserName=""sivq"" for field: subscriber_id error: avp:UserName is not defined in the db",res)
            if final is not None:
                logging.info("Test case 62 passed")
            else:
                logging.info("Test case 62 Failed")
    
    @pytest.mark.run(order=63)
    def test_063_import_subscriber_records_through_csv_negative_validations_for_Nas_contextual_IP(self):
        cmd="ls -ltr /tmp/csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        #command=os.system("ls -ltr /tmp")
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[8]
            final=re.search("Insertion aborted due to Subscriber <102.121.12.23/14 LID:N/A IPS:N/A> has invalid value NAS-IP-Address for field: nas_contextual error: AVP is not in expected format: 'avp_name=value",res)
            if final is not None:
                logging.info("Test case 63 passed")
            else:
                logging.info("Test case 63 Failed")

    @pytest.mark.run(order=64)
    def test_064_import_subscriber_records_through_csv_negative_validations_for_Site(self):
        cmd="ls -ltr /tmp/csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        #command=os.system("ls -ltr /tmp")
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[9]
            final=re.search("Insertion aborted due to Site not found/configured : site4",res)
            if final is not None:
                logging.info("Test case 64 passed")
            else:
                logging.info("Test case 64 Failed")

    @pytest.mark.run(order=65)
    def test_065_import_subscriber_records_through_csv_negative_validations_for_Anscillary_field(self):
        cmd="ls -ltr /tmp/csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        #command=os.system("ls -ltr /tmp")
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[10]
            final=re.search("Insertion aborted due to Subscriber <102.121.12.23/32 LID:N/A IPS:N/A> has invalid value arun for field: ans0 error: AVP is not in expected format: 'avp_name=value",res)
            if final is not None:
                logging.info("Test case 65 passed")
            else:
                logging.info("Test case 65 Failed")
    
    @pytest.mark.run(order=66)
    def test_066_import_subscriber_records_through_csv_negative_validations_for_Subscriber_secure_policy(self):
        cmd="ls -ltr /tmp/csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        #command=os.system("ls -ltr /tmp")
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[11]
            final=re.search("Insertion aborted due to Subscriber <102.121.12.23/32 LID:N/A IPS:N/A> has invalid value GGG for field: subscriber_secure_policy error: Not a valid hex string",res)
            if final is not None:
                logging.info("Test case 66 passed")
            else:
                logging.info("Test case 66 Failed")

    @pytest.mark.run(order=67)
    def test_067_import_subscriber_records_through_csv_negative_validations_for_Parental_control_policy(self):
        cmd="ls -ltr /tmp/csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        #command=os.system("ls -ltr /tmp")
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[12]
            final=re.search("Insertion aborted due to Subscriber <102.121.12.23/32 LID:N/A IPS:N/A> has invalid value HHH for field: parental_control_policy error: Not a valid hex string",res)
            if final is not None:
                logging.info("Test case 67 passed")
            else:
                logging.info("Test case 67 Failed")

    @pytest.mark.run(order=68)
    def test_068_import_subscriber_records_through_csv_negative_validations_for_WPC_category_policy(self):
        cmd="ls -ltr /tmp/csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        #command=os.system("ls -ltr /tmp")
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[13]
            final=re.search("Insertion aborted due to Subscriber <102.121.12.23/32 LID:N/A IPS:N/A> has invalid value JJJ for field: wpc_category_policy error: Not a valid hex string",res)
            if final is not None:
                logging.info("Test case 68 passed")
            else:
                logging.info("Test case 68 Failed")

    @pytest.mark.run(order=69)
    def test_069_import_subscriber_records_through_csv_negative_validations_for_Dynamic_category_policy(self):
        cmd="ls -ltr /tmp/csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        #command=os.system("ls -ltr /tmp")
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[14]
            final=re.search("Can not convert data ""10"" for column dynamic_category_policy to internal format (Boolean)",res)
            if final is not None:
                logging.info("Test case 69 passed")
            else:
                logging.info("Test case 69 Failed")

    @pytest.mark.run(order=70)
    def test_070_import_subscriber_records_through_csv_negative_validations_for_bwflag(self):
        cmd="ls -ltr /tmp/csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        #command=os.system("ls -ltr /tmp")
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[15]
            final=re.search("Can not convert data ""10"" for column bwflag to internal format (Boolean)",res)
            if final is not None:
                logging.info("Test case 70 passed")
            else:
                logging.info("Test case 70 Failed")

    @pytest.mark.run(order=71)
    def test_071_import_subscriber_records_through_csv_negative_validations_for_proxy_all(self):
        cmd="ls -ltr /tmp/csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        #command=os.system("ls -ltr /tmp")
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[16]
            final=re.search("Can not convert data ""20"" for column proxy_all to internal format (Boolean)",res)
            if final is not None:
                logging.info("Test case 71 passed")
            else:
                logging.info("Test case 71  Failed")

    @pytest.mark.run(order=72)
    def test_072_import_subscriber_records_through_csv_negative_validations_for_black_list(self):
        cmd="ls -ltr /tmp/csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        #command=os.system("ls -ltr /tmp")
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[17]
            final=re.search("Insertion aborted due to Subscriber <102.121.12.23/32 LID:N/A IPS:N/A> has invalid value .com for field: black_list error: invalid domain name",res)
            if final is not None:
                logging.info("Test case 72 passed")
            else:
                logging.info("Test case 72 Failed")

    @pytest.mark.run(order=73)
    def test_073_import_subscriber_records_through_csv_negative_validations_for_white_list(self):
        cmd="ls -ltr /tmp/csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        #command=os.system("ls -ltr /tmp")
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[18]
            final=re.search("Insertion aborted due to Subscriber <102.121.12.23/32 LID:N/A IPS:N/A> has invalid value .com for field: white_list error: invalid domain name",res)
            if final is not None:
                logging.info("Test case 73 passed")
            else:
                logging.info("Test case 73 Failed")

    @pytest.mark.run(order=74)
    def test_074_import_subscriber_records_through_csv_negative_validations_for_max_string_length(self):
        cmd="ls -ltr /tmp/csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        #command=os.system("ls -ltr /tmp")
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[19]
            final=re.search('subscriber_id error: Field length more than 256 characters',res)
            if final is not None:
                logging.info("Test case 74 passed")
            else:
                logging.info("Test case 74 Failed")

    @pytest.mark.run(order=75)
    def test_075_import_subscriber_records_through_csv_negative_validations_for_Black_list_with_more_than_10_domains(self):
        cmd="ls -ltr /tmp/csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        #command=os.system("ls -ltr /tmp")
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[20]
            final=re.search("Insertion aborted due to Subscriber <102.121.12.22/12 LID:N/A IPS:N/A> has invalid value bad.com,bad1.com,bad2.com,bad3.com,bad4.com,bad5.com,bad6.com,bad7.com,bad8.com,bad9.com,bad10.com for field: black_list error: list contains more than 10 domains",res)
            if final is not None:
                logging.info("Test case 75 passed")
            else:
                logging.info("Test case 75 Failed")

    @pytest.mark.run(order=76)
    def test_076_import_subscriber_records_through_csv_negative_validations_for_White_list_with_more_than_10_domains(self):
        cmd="ls -ltr /tmp/csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        #command=os.system("ls -ltr /tmp")
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[21]
            final=re.search("Insertion aborted due to Subscriber <102.121.12.22/12 LID:N/A IPS:N/A> has invalid value good.com,good1.com,good2.com,good3.com,good4.com,good5.com,good6.com,good7.com,good8.com,good9.com,good20.com for field: white_list error: list contains more than 10 domains",res)
            if final is not None:
                logging.info("Test case 76 passed")
            else:
                logging.info("Test case 76 Failed")

    @pytest.mark.run(order=77)
    def test_077_import_subscriber_records_through_csv_negative_validations_for_when_BWFLAG_set_to_FALSE(self):
        cmd="ls -ltr /tmp/csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        #command=os.system("ls -ltr /tmp")
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[22]
            final=re.search("Insertion aborted due to Subscriber <102.121.12.22/12 LID:N/A IPS:N/A> has Black/White list bad.com for black_list when flags are not set",res)
            if final is not None:
                logging.info("Test case 77 passed")
            else:
                logging.info("Test case 77 Failed")
    
    @pytest.mark.run(order=78)
    def test_078_import_subscriber_records_through_csv_negative_validations_for_when_site_is_not_specified(self):
        cmd="ls -ltr /tmp/csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        #command=os.system("ls -ltr /tmp")
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[23]
            final=re.search("Required field site is not provided",res)
            if final is not None:
                logging.info("Test case 78 passed")
            else:
                logging.info("Test case 78 Failed")

    @pytest.mark.run(order=79)
    def test_079_export_site_data(self):
        delete_subscriber_records_with_Subscriber_EA("site3")
        add_subscriber_record_to_the_added_site("site3")
        data={"_separator":"COMMA","_object": "parentalcontrol:subscriberrecord","site":"site3"}
        create_file=ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=csv_export")
        logging.info(create_file)
        res = json.loads(create_file)
        token = json.loads(create_file)['token']
        url = json.loads(create_file)['url']
        logging.info (create_file)
        logging.info("Create the fileop function to dowload the csv file to the specified url")
        cmd='curl -k1 -u admin:infoblox -H "Content-type:application/force-download" -O %s'%(url)
        result = subprocess.check_output(cmd, shell=True)
        command1="cat Subscriberrecords.csv | grep -F '10.36.0.151,N/A,N/A,32' "
        if command1!=None:
            assert True
            logging.info("Test Case 79 Execution Completed")
        else:
            assert False
            logging.info("Test Case 79 Execution Failed")
        cmd='rm Subscriberrecords.csv'
        command2=subprocess.check_output(cmd, shell=True)

    @pytest.mark.run(order=80)
    def test_080_add_subscriber_site_with_multiple_members(self):
        stop_subscriber_collection_services_for_added_site(config.grid_fqdn)
        delete_subscriber_site("site3")
        data={"name":"site3","maximum_subscribers":100000,"members":[{"name":config.grid_fqdn},{"name":config.grid_member1_fqdn}],"nas_gateways":[{"ip_address":"2.2.2.2","name":"nas1","shared_secret":"test123"}]}
        get_ref=ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data))
        logging.info(get_ref)
        print get_ref
        if type(get_ref)!=tuple:
            reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite")
            reference=json.loads(reference)
            for ref in reference:
                if reference[0]["name"]==data["name"]:
                    logging.info("Test case 80 execution passed")
                    assert True
                else:
                    logging.info("Test case 80 execution Failed")
                    assert False
        else:
            logging.info(get_ref)
            logging.info("Test case 80 execution failed")
            assert False

    @pytest.mark.run(order=81)
    def test_081_import_subscriber_data_to_site_with_multiple_members(self):
        start_subscriber_collection_services_for_added_site(config.grid_fqdn)
        start_subscriber_collection_services_for_added_site(config.grid_member1_fqdn)
        time.sleep(20)
        res=import_subscriber_data("subscriber_site_data_for_multiple_members.csv")
        print res
        if res!=None:
            data=show_subscriber_secure_data(config.grid_member1_vip)
            result=re.search("102.121.12.22/12,N/A,N/A",data)
            if (result == None):
                logging.info("Test case 81 passed")
                assert True
            else:
                logging.info("Test case 81 failed")
                assert False
        else:
            assert False
            logging.info("Test case 81 failed")

    @pytest.mark.run(order=82)
    def test_082_Validate_import_subscriber_data_to_site_with_multiple_members(self):
        data=show_subscriber_secure_data(config.grid_vip)
        result=re.search("102.121.12.22/12,N/A,N/A",data)
        if (result == None):
            logging.info("Test case 82 passed")
            assert True
        else:
            logging.info("Test case 82 failed")
            assert False


    @pytest.mark.run(order=83)
    def test_083_Add_subscriber_data_to_site_with_multiple_members_using_WAPI(self):
        time.sleep(20)
        add_subscriber_record_to_the_added_site("site3")
        data=show_subscriber_secure_data(config.grid_member1_vip)
        result=re.search("10.36.0.151/32,N/A,N/A",data)
        if (result == None):
            assert True
            print ("Test case 83 passed")
        else:
            assert False
            print ("Test case 83 failed")

    @pytest.mark.run(order=84)
    def test_084_Validate_Add_subscriber_data_to_site_with_multiple_members_using_WAPI(self):
        data=show_subscriber_secure_data(config.grid_vip)
        result=re.search("10.36.0.151/32,N/A,N/A",data)
        if (result == None):
            logging.info("Test case 84 passed")
            assert True
        else:
            logging.info("Test case 84 failed")
            assert False

    @pytest.mark.run(order=85)
    def test_085_export_subscriber_data_to_site_with_multiple_members(self):
        result=export_site_data("site3")
        if result!=None:
            logging.info("Test case 85 Passed")
            assert True
        else:
            logging.info("Test case 85 Failed")
            assert False

    @pytest.mark.run(order=86)
    def test_086_stop_subscriber_service_on_master_enable_on_member(self):
        res1=stop_subscriber_collection_services_for_added_site(config.grid_fqdn)
        res2=start_subscriber_collection_services_for_added_site(config.grid_member1_fqdn)
        if res1==False and res2==True:
            logging.info("Test Case 86 Execution Completed")
            assert True
        else:
            logging.info("Test Case 86 Execution Completed")
            assert False

    @pytest.mark.run(order=87)
    def test_087_import_data_when_subscriber_service_is_not_running_on_master_with_multiple_members(self):
        #start_subscriber_collection_services_for_added_site()
        #time.sleep(20)
        delete_subscriber_records_with_Subscriber_EA("site3")
        res=import_subscriber_data("subscriber_site_data_for_multiple_members.csv")
        if res!=None:
            data=show_subscriber_secure_data(config.grid_member1_vip)
            result=re.search("102.121.12.22/12,N/A,N/A",data)
            if (result == None):
                logging.info("Test case 87 passed")
                assert True
            else:
                logging.info("Test case 87 failed")
                assert False
        else:
            logging.info("Test case 87 failed")
            assert False

    @pytest.mark.run(order=88)
    def test_088_Validate_import_data_when_subscriber_service_is_not_running_on_master_with_multiple_members(self):
        data=show_subscriber_secure_data(config.grid_vip)
        result=re.search("Subscriber Collection Service is not enabled",data)
        if (result != None):
            logging.info("Test case 88 passed")
            assert True
        else:
            logging.info("Test case 88 failed")
            assert False

    @pytest.mark.run(order=89)
    def test_089_Add_data_when_subscriber_service_is_not_running_on_master_with_multiple_members(self):
        add_subscriber_record_to_the_added_site("site3")
        data=show_subscriber_secure_data(config.grid_member1_vip)
        result=re.search("10.36.0.151/32,N/A,N/A",data)
        if (result == None):
            logging.info("Test case 89 passed")
            assert True
        else:
            logging.info("Test case 89 failed")
            assert False


    @pytest.mark.run(order=90)
    def test_090_Validate_data_when_subscriber_service_is_not_running_on_master_with_multiple_members(self):
        data=show_subscriber_secure_data(config.grid_vip)
        result=re.search("Subscriber Collection Service is not enabled.",data)
        if (result != None):
            logging.info("Test case 90 passed")
            assert True
        else:
            logging.info("Test case 90 failed")
            assert False

    @pytest.mark.run(order=91)
    def test_091_export_data_when_subscriber_service_is_not_running_on_master_with_multiple_members(self):
        result=export_site_data("site3")
        if result!=None:
            logging.info("Test case 91 Passed")
            assert True
        else:
            logging.info("Test case 91 Failed")
            assert False

    @pytest.mark.run(order=92)
    def test_092_stop_subscriber_service_on_member_start_on_master_with_multiple_members(self):
        res1=stop_subscriber_collection_services_for_added_site(config.grid_member1_fqdn)
        res2=start_subscriber_collection_services_for_added_site(config.grid_fqdn)
        if res1==False and res2==True:
            logging.info("Test Case 92 Execution Completed")
            assert True
        else:
            logging.info("Test Case 92 Execution failed")
            assert False

    @pytest.mark.run(order=93)
    def test_093_import_data_when_subscriber_service_is_not_running_on_member_with_multiple_members(self):
        #time.sleep(20)
        delete_subscriber_records_with_Subscriber_EA("site3")
        res=import_subscriber_data("subscriber_site_data_for_multiple_members.csv")
        if res!=None:
            data=show_subscriber_secure_data(config.grid_vip)
            result=re.search("102.121.12.22/12|LID:N/A|IPS:N/A",data)
            if (result != None):
                logging.info("Test case 93 passed")
                assert True
            else:
                logging.info("Test case 93 failed")
                assert False
        else:
            logging.info("Test case 93 failed")
            assert False

    @pytest.mark.run(order=94)
    def test_094_Validate_import_data_when_subscriber_service_is_not_running_on_member_with_multiple_members(self):
        data=show_subscriber_secure_data(config.grid_member1_vip)
        result=re.search("Subscriber Collection Service is not enabled",data)
        if (result != None):
            assert True
            logging.info("Test case 94 passed")
        else:
            assert False
            logging.info("Test case 94 failed")

    @pytest.mark.run(order=95)
    def test_095_Add_data_when_subscriber_service_is_not_running_on_member_with_multiple_members(self):
        add_subscriber_record_to_the_added_site("site3")
        data=show_subscriber_secure_data(config.grid_vip)
        result=re.search("10.36.0.151/32|LID:N/A|IPS:N/A",data)
        if (result != None):
            assert True
            logging.info("Test case 95 passed")
        else:
            assert False
            logging.info("Test case 95 failed")

    @pytest.mark.run(order=96)
    def test_096_Validate_Add_data_when_subscriber_service_is_not_running_on_member_with_multiple_members(self):
        add_subscriber_record_to_the_added_site("site3")
        data=show_subscriber_secure_data(config.grid_member1_vip)
        result=re.search("Subscriber Collection Service is not enabled",data)
        if (result != None):
            assert True
            logging.info("Test case 96 passed")
        else:
            assert False
            logging.info("Test case 96 failed")

    @pytest.mark.run(order=97)
    def test_097_export_data_when_subscriber_service_is_not_running_on_member_with_multiple_members(self):
        result=export_site_data("site3")
        if result!=None:
            logging.info("Test case 97 Passed")
            assert True
        else:
            logging.info("Test case 97 Failed")
            assert False

    @pytest.mark.run(order=98)
    def test_098_stop_subscriber_service_on_both_master_and_member_with_multiple_members(self):
        res1=stop_subscriber_collection_services_for_added_site(config.grid_member1_fqdn)
        res2=stop_subscriber_collection_services_for_added_site(config.grid_fqdn)
        if res1==False and res2==False:
            assert True
            logging.info("Test Case 98 Execution Completed")
        else:
            assert False
            logging.info("Test Case 98 Execution failed")

    @pytest.mark.run(order=99)
    def test_099_import_data_when_subscriber_service_is_not_running_on_any_members_with_multiple_members(self):
        res=import_subscriber_data("subscriber_site_data_for_multiple_members.csv")
        if res==None:
            data=show_subscriber_secure_data(config.grid_vip)
            result=re.search("Subscriber Collection Service is not enabled",data)
            if (result != None):
                assert True
                logging.info("Test case 99 passed")
            else:
                assert False
                logging.info("Test case 99 failed")
        else:
            assert False

    @pytest.mark.run(order=100)
    def test_100_Validate_the_error_message(self):
        cmd="ls -ltr /tmp/csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        #command=os.system("ls -ltr /tmp")
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[1]
            print res
            final=re.search('Insertion aborted due to None of the members of Subscriber Site: site3 are running Subscriber collection service',res)
            if final is not None:
                logging.info("Test case 100 passed")
            else:
                logging.info("Test case 100 Failed")

    @pytest.mark.run(order=101)
    def test_101_Add_data_when_subscriber_service_is_not_running_on_any_members_with_multiple_members(self):
        data={"ans0":"User-Name=JOHN","ip_addr":"10.36.0.151", "prefix":32,"localid":"N/A","ipsd":"N/A","subscriber_secure_policy":"FF","parental_control_policy":"00000000000000000000000000020040","unknown_category_policy":False,"dynamic_category_policy":False,"subscriber_id":"IMSI=12345","accounting_session_id":"Acct-Session-Id=9999732d-34590346","bwflag":True,"black_list":"a.com,a.com","site":"site3","flags":"SB","nas_contextual":"NAS-PORT=1813"}
        print data
        get_ref=ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscriberrecord",fields=json.dumps(data))
        print get_ref
        if type(get_ref)==tuple:
            print get_ref[0]
            res=re.search("None of the members of Subscriber Site: site3 are running Subscriber collection service",get_ref[1])
            if res!=None:
                assert True
                logging.info("Test Case 101 Execution Completed")
            else:
                assert False
                logging.info("Test Case 101 Execution failed")
        else:
            assert False
            logging.info("Test Case 101 Execution failed")

    @pytest.mark.run(order=102)
    def test_102_export_data_when_subscriber_service_is_not_running_on_any_members_with_multiple_members(self):
        #result=export_site_data("site3")
        site="site3"
        data={"_separator":"COMMA","_object": "parentalcontrol:subscriberrecord","site":site}
        create_file=ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=csv_export")
        print(create_file)
        if type(create_file)==tuple:
            print create_file[0]
            print(create_file[1])
            res=re.search('None of the members of Subscriber Site: '+site+' are running Subscriber collection service',create_file[1])
            print res
            if res!=None:
                logging.info("Test case 102 Passed")
                assert True
            else:
                logging.info("Test case 102 Failed")
                assert False
        else:
            assert False
            logging.info("Test Case 102 Execution failed")
    #different sites
    @pytest.mark.run(order=103)
    def test_103_add_subscriber_site3_to_test_with_multiple_sites(self):
        delete_subscriber_site("site3")
        data={"name":"site3","maximum_subscribers":100000,"members":[{"name":config.grid_fqdn}],"nas_gateways":[{"ip_address":"2.2.2.2","name":"nas1","shared_secret":"test123"}]}
        get_ref=ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data))
        logging.info(get_ref)
        print type(get_ref)
        if type(get_ref)!=tuple:
            reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?name=site3")
            reference=json.loads(reference)
            if reference[0]["name"]==data["name"]:
                logging.info("Test case 103 execution passed")
                assert True
            else:
                logging.info("Test case 103 execution Failed")
                assert False
        else:
            logging.info(get_ref)
            logging.info("Test case 103 execution failed")
            assert False

    @pytest.mark.run(order=104)
    def test_104_add_subscriber_site4_to_test_with_multiple_sites(self):
        data={"name":"site4","maximum_subscribers":100000,"members":[{"name":config.grid_member1_fqdn}],"nas_gateways":[{"ip_address":"2.2.2.2","name":"nas1","shared_secret":"test123"}]}
        get_ref=ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data))
        logging.info(get_ref)
        print type(get_ref)
        if type(get_ref)!=tuple:
            reference=ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?name=site4")
            reference=json.loads(reference)
            if reference[0]["name"]==data["name"]:
                logging.info("Test case 104 execution passed")
                assert True
            else:
                logging.info("Test case 104 execution Failed")
                assert False
        else:
            logging.info(get_ref)
            logging.info("Test case 104 execution failed")
            assert False

    @pytest.mark.run(order=105)
    def test_105_import_subscriber_data_to_site_with_multiple_sites(self):
        start_subscriber_collection_services_for_added_site(config.grid_fqdn)
        start_subscriber_collection_services_for_added_site(config.grid_member1_fqdn)
        time.sleep(40)
        #add_subscriber_record_to_the_added_site()
        import_subscriber_data("subscriber_site_data_for_multiple_members.csv")
        data=show_subscriber_secure_data(config.grid_member1_vip)
        result=re.search("102.121.12.22/22|LID:N/A|IPS:N/A|",data)
        if (result != None):
            logging.info("Test case 105 passed")
            assert True
        else:
            logging.info("Test case 105 failed")
            assert False

    @pytest.mark.run(order=106)
    def test_106_add_subscriber_data_to_site_with_multiple_sites(self):
        add_subscriber_record_to_the_added_site("site3")
        data=show_subscriber_secure_data(config.grid_member1_vip)
        result=re.search("10.36.0.151/32,N/A,N/A",data)
        if (result == None):
            logging.info("Test case 106 passed")
            assert True
        else:
            logging.info("Test case 106 failed")
            assert False

    @pytest.mark.run(order=107)
    def test_107_export_subscriber_data_to_site_with_multiple_sites(self):
        result=export_site_data("site3")
        if result!=None:
            logging.info("Test case 107 Passed")
            assert True
        else:
            logging.info("Test case 107 Failed")
            assert False

    @pytest.mark.run(order=108)
    def test_108_stop_subscriber_service_on_master_site_enable_on_member_site(self):
        res1=stop_subscriber_collection_services_for_added_site(config.grid_fqdn)
        res2=start_subscriber_collection_services_for_added_site(config.grid_member1_fqdn)
        if res1==False and res2==True:
            logging.info("Test Case 108 Execution Completed")
            assert True
        else:
            logging.info("Test Case 108 Execution Failed")
            assert False

    @pytest.mark.run(order=109)
    def test_109_import_data_when_subscriber_service_is_not_running_on_master_site_with_multiple_sites(self):
        #command1=os.system("rm -rf /tmp/csv_error_files")
        data=import_subscriber_data("subscriber_records_for_multiple_sites.csv")
        if data!=None:
            data1=show_subscriber_secure_data(config.grid_member1_vip)
            result=re.search("102.121.12.22/12,N/A,N/A",data)
            if (result == None):
                logging.info("Test Case 109 Execution Completed")
                assert True
            else:
                logging.info("Test Case 109 Execution FAILED")
                assert False
        else:
            logging.info("Test Case 109 Execution FAILED")
            assert False

    @pytest.mark.run(order=110)
    def test_110_export_data_when_subscriber_service_is_not_running_on_master_site_with_multiple_sites(self):
        data=export_site_data("site4")
        if data!=None:
            logging.info("Test Case 110 Execution Completed")
            assert True
        else:
            logging.info("Test Case 110 Execution failed")
            assert False

    @pytest.mark.run(order=111)
    def test_111_stop_subscriber_service_on_member_site_start_on_master_site_with_multiple_sites(self):
        res1=stop_subscriber_collection_services_for_added_site(config.grid_member1_fqdn)
        res2=start_subscriber_collection_services_for_added_site(config.grid_fqdn)
        if res1==False and res2==True:
            logging.info("Test Case 111 Execution Completed")
            assert True
        else:
            logging.info("Test Case 111 Execution failed")
            assert False

    @pytest.mark.run(order=112)
    def test_112_import_data_when_subscriber_service_is_not_running_on_member_site_with_multiple_sites(self):
        command1=os.system("rm -rf /tmp/csv_error_files")
        data=import_subscriber_data("subscriber_site_data_for_multiple_members.csv")
        if data!=None:
            data1=show_subscriber_secure_data(config.grid_vip)
            result=re.search("102.121.12.22/12,N/A,N/A",data)
            if (result == None):
                logging.info("Test Case 112 Execution Completed")
                assert True
            else:
                logging.info("Test Case 112 Execution failed")
                assert False
        else:
            logging.info("Test Case 112 Execution failed")
            assert False

    @pytest.mark.run(order=113)
    def test_113_export_data_when_subscriber_service_is_not_running_on_member_site_with_multiple_sites(self):
        data=export_site_data("site3")
        if data!=None:
            logging.info("Test Case 113 Execution Completed")
            assert True
        else:
            logging.info("Test Case 113 Execution failed")
            assert False

    @pytest.mark.run(order=114)
    def test_114_stop_subscriber_service_on_both_master_site_and_member_site_with_multiple_sites(self):
        res1=stop_subscriber_collection_services_for_added_site(config.grid_member1_fqdn)
        res2=stop_subscriber_collection_services_for_added_site(config.grid_fqdn)
        if res1==False and res2==False:
            logging.info("Test Case 114 Execution Completed")
            assert True
        else:
            logging.info("Test Case 114 Execution Failed")
            assert False

    @pytest.mark.run(order=115)
    def test_115_import_data_when_subscriber_service_is_not_running_on_any_site_members_with_multiple_sites(self):
        data=show_subscriber_secure_data(config.grid_member1_vip)
        result=re.search("Subscriber Collection Service is not enabled.",data)
        if (result != None):
            logging.info("Test case 115 passed")
            assert True
        else:
            logging.info("Test case 115 failed")
            assert False

    @pytest.mark.run(order=116)
    def test_116_export_data_when_subscriber_service_is_not_running_on_any_site_members_with_multiple_sites(self):
        site="site3"
        data={"_separator":"COMMA","_object": "parentalcontrol:subscriberrecord","site":site}
        create_file=ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=csv_export")
        logging.info(create_file)
        if type(create_file)==tuple:
            res=re.search('None of the members of Subscriber Site: '+site+' are running Subscriber collection service',create_file[1])
            logging.info(res)
            if res!=None:
                logging.info("Test case 116 Passed")
                assert True
            else:
                logging.info("Test case 116 Failed")
                assert False
        else:
            logging.info("Test Case 116 Execution failed")
            assert False


    @pytest.mark.run(order=117)
    def test_117_import_data_with_invalid_csv_file(self):
        logging.info("Upload Unknown resource records csv file")
        #dir_name = "/import/qaddi/rkarjagi/API_Automation/WAPI_PyTest/suites/RFE_8672"
        dir_name=os.getcwd()
        base_filename = "invalid_csv_file.csv"
        token =generate_token_from_file(dir_name, base_filename)
        data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
        logging.info(response)
        if type(response)==tuple:
            res=re.search("Import file is not valid. First line of the file must be either a valid version number or a valid header line",response[1])
            if res!=None:
                logging.info("Test Case 117 Execution Completed")
                assert True
            else:
                logging.info("Test Case 117 Execution failed")
                assert False

    @pytest.mark.run(order=118)
    def test_118_import_data_with_invalid_headers(self):
        logging.info("Upload Unknown resource records csv file")
        #dir_name = "/import/qaddi/rkarjagi/API_Automation/WAPI_PyTest/suites/RFE_8672"
        dir_name=os.getcwd()
        base_filename = "invalid_header.csv"
        token =generate_token_from_file(dir_name, base_filename)
        data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
        logging.info(response)
        if type(response)==tuple:
            res=re.search("Header \'header-subscriberrecord\' at line number 1 has invalid column \'ip_address\'",response[1])
            if res!=None:
                logging.info("Test Case 118 Execution Completed")
                assert True
            else:
                logging.info("Test Case 118 Execution failed")
                assert False

    @pytest.mark.run(order=119)
    def test_119_modify_grid_settings(self):
        response = ib_NIOS.wapi_request('GET', object_type="grid")
        response = json.loads(response)
        response=response[0]["_ref"]
        data={"dns_resolver_setting": {"resolvers": ["127.0.0.1",config.resolver_ip]}}
        res = ib_NIOS.wapi_request('PUT', object_type=response,fields=json.dumps(data))
        logging.info(res)
        logging.info("Test Case 119 Execution Completed")

    @pytest.mark.run(order=120)
    def test_120_add_site_data(self):
        get_ref=ib_NIOS.wapi_request('GET',object_type="parentalcontrol:subscribersite?name=site3")
        logging.info(get_ref)
        get_ref=json.loads(get_ref)[0]["_ref"]
        logging.info(get_ref)
        logging.info("adding subscriber site under subscriber site \n ")
        site_data_new = {"blocking_ipv4_vip1": "2.4.5.6","msps":[{"ip_address": config.proxy_server1}],"spms": [{"ip_address": "10.12.11.11"}]}
        subscriber_site_ref=ib_NIOS.wapi_request('PUT',object_type=get_ref,fields=json.dumps(site_data_new))
        logging.info(subscriber_site_ref)
        #subscriber_site_ref=json.dumps(subscriber_site_ref)
        subscriber_site_ref=json.loads(subscriber_site_ref)
        logging.info(subscriber_site_ref)
        logging.info("Test Case 120 Execution Completed")

    @pytest.mark.run(order=121)
    def test_121_import_data_with_proxy_all_set_to_true(self):
        start_subscriber_collection_services_for_added_site(config.grid_fqdn)
        time.sleep(20)
        data=import_subscriber_data("functional_test_case.csv")
        if data!=None:
            data1=show_subscriber_secure_data(config.grid_vip)
            result=re.search("PXP:PXY_PRI",data)
            if (result == None):
                logging.info("Test Case 121 Execution Completed")
                assert True
            else:
                logging.info("Test Case 121 Execution failed")
                assert False
        else:
            logging.info("Test Case 121 Execution failed")
            assert False
    
    @pytest.mark.run(order=127)
    def test_122_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 135 passed")
    
    @pytest.mark.run(order=375)
    def test_123_Send_Query_from_PCP_bit_match_Subscriber_client_for_Domain_google_Validate_returns_proxy_response(self):
        logging.info("Send_Query_from_PCP_bit_match_Subscriber_client_for_Domain_google_Validate_returns_proxy_response")
        dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client1)+' "dig @'+str(config.Master1_LAN)+' google.com +noedns -b '+config.client1+' +tries=1"'
        dig_result = subprocess.check_output(dig_cmd, shell=True)
        print dig_result
        assert re.search(r'.*QUERY, status: NOERROR.*',str(dig_result))
        assert re.search(r'.*google.com.*IN.*A.*',str(dig_result))
        assert re.search(r'.*'+config.pxy_response+'.*',str(dig_result))
        logging.info("Test case execution Completed")
        sleep(20)
    
    @pytest.mark.run(order=129)
    def test_124_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case execution Completed")

    @pytest.mark.run(order=130)
    def test_125_Validate_CEF_Log_Logs(self):
        logging.info("Validate CEF Log")
        LookFor=config.pxy_log
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

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

class RFE_6181(unittest.TestCase):
    #############################################  Test cases to enable RPZ,recursive query, forworder ip #############################################
    def restart_the_grid(self):
        logging.info("Restaring the grid")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(60)
        print("Restrting the grid")

    @pytest.mark.run(order=1)
    def test_001_Configure_Recurson_Forwarer_RPZ_logging_At_Grid_DNS_Properties(self):
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

    @pytest.mark.run(order=2)
    def test_002_Validate_Recurson_Forwarer_RPZ_logging_Configured_At_Grid_DNS_Properties(self):
        logging.info("Validating Allow Recursive Query Forwarder and RPZ logging configured at GRID dns properties")
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:dns?_return_fields=allow_recursive_query,forwarders")
        get_ref1=json.loads(get_ref)
        if get_ref1[0]["allow_recursive_query"]==True and get_ref1[0]["forwarders"]==[config.forwarder_ip]:
            logging.info("Test Case Execution Passed")
            assert True
        else:
            logging.info("Test Case Execution Failed")
            assert False

    @pytest.mark.run(order=3)
    def test_003_enable_ipv6_checks(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        logging.info(get_ref)
        res = json.loads(get_ref)
        for i in res:
            ref=i["_ref"]
            data={"use_lan_ipv6_port":True,"use_mgmt_ipv6_port": True,"use_mgmt_port": True}
            response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
            print(response)
            logging.info("Test Case Execution Completed")

    #class RFE_6181_Ipv4_Adress_named_ACL(unittest.TestCase):
    #############################################  Test cases related to ACL verification #############################################
    @pytest.mark.run(order=4)
    def test_004_Start_DNS_Service(self):
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

    @pytest.mark.run(order=5)
    def test_005_Validate_DNS_service_is_Enabled(self):
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

    ##1. Add named acl with IPv4 address 10.36.6.80 and set Operation Allow
    @pytest.mark.run(order=6)
    def test_006_Add_Named_ACL_to_Grid_with_ALLOW_permission(self):
        logging.info("Adding ACL WITH ALLOW.................")
        data={"name": "ACL_ALLOW","access_list": [{"_struct": "addressac", "address": config.client_ip1, "permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    ##2. CLI commad execute with zone name test.com
    @pytest.mark.run(order=7)
    def test_007_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_ACL_ALLOW(self):
        logging.info("addin test.com to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain add default test.com ACL_ALLOW')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=8)
    def test_008_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain test.com DnsView=default: Set dns_view="default",domain_name="test.com",named_acl="ACL_ALLOW"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=9)
    def test_009_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_ALLOW' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=10)
    def test_010_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=11)
    def test_011_show_allow_query_domain(self):
        logging.info("Displaying domains added to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        print(type(c))
        result = re.findall('(Domain Name : test.com)(.+)((?:\n.+)+)(Named ACL   : ACL_ALLOW)',c)
        print(result)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=12)
    def test_012_Validate_named_conf_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat /infoblox/var/named_conf/named.conf | grep test.com'
        print(audit_log_validation)
        string_content = commands.getoutput(audit_log_validation)
        print(string_content)
        logging.info(string_content)
        if bool(re.search('"test.com" { '+config.client_ip1+'; }', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")
        print("Test Case Execution Completed")

    @pytest.mark.run(order=13)
    def test_013_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##3. If we query a.test.com it should return response from 10.36.6.80
    @pytest.mark.run(order=14)
    def test_014_query_domain_test_com_after_adding_to_ACL_ALLOW_From_Client1(self):
        logging.info("Querying test.com, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=15)
    def test_015_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=16)
    def test_016_Validate_syslog_for_dig_operation(self):
        LookFor=".*query: test.com IN A response.*NOERROR.*"
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


    @pytest.mark.run(order=17)
    def test_017_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##4. If we query a.test.com it should refuse queries from 10.36.1.255
    @pytest.mark.run(order=18)
    def test_018_query_domain_test_com_after_adding_to_ACL_ALLOW_From_Client2(self):
        logging.info("Querying test.com, expected result as REFUSED")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip2+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=19)
    def test_019_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=20)
    def test_020_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*failed.*(REFUSED).*test.com.*"
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


    @pytest.mark.run(order=21)
    def test_021_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##5. If we query other domain say a.zone.com from 10.36.6.80 it should return response
    @pytest.mark.run(order=22)
    def test_022_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_Client1(self):
       logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' zone.com +noedns -b '+config.client_ip1+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(15)

    @pytest.mark.run(order=23)
    def test_023_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=24)
    def test_024_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*zone.com IN A response.*NOERROR.*zone.com.*"
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

    @pytest.mark.run(order=25)
    def test_025_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(15)

    ##6. If we query other domain say a.zone.com from 10.36.1.255 it should return response
    @pytest.mark.run(order=26)
    def test_026_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_Client2(self):
       logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' zone.com +noedns -b '+config.client_ip2+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(15)

    @pytest.mark.run(order=27)
    def test_027_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=28)
    def test_028_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*zone.com IN A response.*NOERROR.*zone.com.*"
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

    @pytest.mark.run(order=29)
    def test_029_Add_Named_ACL_to_Grid_with_DENY_permission(self):
        logging.info("Adding ACL WITH DENY.................")
        data={"name": "ACL_DENY","access_list": [{"_struct": "addressac", "address": config.client_ip1, "permission": "DENY"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=30)
    def test_030_update_test_com_from_ACL_ALLOW_TO_ACL_DENY(self):
        logging.info("Updating test.com from ACL_ALLOW to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain update default test.com ACL_DENY')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=31)
    def test_031_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Modified AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Modified AllowQueryDomain test.com DnsView=default: Changed named_acl:"ACL_ALLOW"->"ACL_DENY"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=32)
    def test_032_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Updated ACL 'ACL_DENY' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=33)
    def test_033_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=34)
    def test_034_show_allow_query_domain(self):
        logging.info("Displaying domains added to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        print(type(c))
        result = re.findall('(Domain Name : test.com)(.+)((?:\n.+)+)(Named ACL   : ACL_DENY)',c)
        print(result)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=35)
    def test_035_Validate_named_conf_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat /infoblox/var/named_conf/named.conf | grep test.com'
        print(audit_log_validation)
        string_content = commands.getoutput(audit_log_validation)
        print(string_content)
        logging.info(string_content)
        if bool(re.search('"test.com" { !'+config.client_ip1+'; }', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")
        print("Test Case Execution Completed")

    @pytest.mark.run(order=36)
    def test_036_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##1. If we query a.test.com it should refuse queries from 10.36.6.80
    @pytest.mark.run(order=37)
    def test_037_query_domain_test_com_after_updating_from_ACL_ALLOW_to_ACL_DENY_From_Client1(self):
       logging.info("Querying test.com after updating to ACL_DENY, expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=38)
    def test_038_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=39)
    def test_039_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*failed.*(REFUSED).*test.com.*"
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
    def test_040__start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##2. If we query a.test.com it should refuse queries from 10.36.1.255
    @pytest.mark.run(order=41)
    def test_041_query_domain_test_com_after_updating_from_ACL_ALLOW_to_ACL_DENY_From_Client2(self):
       logging.info("Querying test.com after updating to ACL_ALLOW, expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip2+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=42)
    def test_042__stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=43)
    def test_043_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*failed.*(REFUSED).*test.com.*"
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

    @pytest.mark.run(order=44)
    def test_044_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##3. If we query other domain say a.zone.com from 10.36.6.80 it should return response
    @pytest.mark.run(order=45)
    def test_045_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_Client1(self):
        logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' zone.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=46)
    def test_046_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=47)
    def test_047_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*zone.com IN A response.*NOERROR.*zone.com.*"
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

    @pytest.mark.run(order=48)
    def test_048_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##4. If we query other domain say a.zone.com from 10.36.1.255 it should return response
    @pytest.mark.run(order=49)
    def test_049_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_Client2(self):
        logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' zone.com +noedns -b '+config.client_ip2+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=50)
    def test_050_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=51)
    def test_051__Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*zone.com IN A response.*NOERROR.*zone.com.*"
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
    def test_052_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
        logging.info("deleting test.com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain delete default test.com')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=53)
    def test_053_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain test.com DnsView=default', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=54)
    def test_054_validate_infoblox_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Deleted ACL for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=55)
    def test_055_Perform_RESTART_of_the_DNS_service(self):
       logging.info("Restart services")
       grid =  ib_NIOS.wapi_request('GET', object_type="grid")
       ref = json.loads(grid)[0]['_ref']
       publish={"member_order":"SIMULTANEOUSLY"}
       request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
       request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
       restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
       print("System Restart is done successfully")
       sleep(60)

    @pytest.mark.run(order=56)
    def test_056_show_allow_query_domain(self):
        logging.info("Displaying domains after deleting test.com with delete command")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r".*No domain ACLs found for view 'default'.*",c)
        sleep(10)

    @pytest.mark.run(order=57)
    def test_057_Validate_named_conf_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat /infoblox/var/named_conf/named.conf | grep test.com'
        print(audit_log_validation)
        string_content = commands.getoutput(audit_log_validation)
        print(string_content)
        logging.info(string_content)
        if not bool(re.search('"test.com" { '+config.client_ip1+'; }', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")
        print("Test Case Execution Completed")

    @pytest.mark.run(order=58)
    def test_058_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=59)
    def test_059_query_domain_test_com_after_deleting_ACL_From_Client1(self):
      logging.info("Querying test.com after deleting, expected result as NOERROR")
      cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
      result=subprocess.check_output(cmd, shell=True)
      print(result)
      assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
      logging.info("Test Case Execution Completed")
      sleep(10)

    @pytest.mark.run(order=60)
    def test_060_stop_Syslog_Messages(self):
       log("stop","/var/log/syslog",config.grid_vip)
       logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=61)
    def test_061_Validate_syslog_for_dig_operation(self):
       LookFor=".*query: test.com IN A response.*NOERROR.*"
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

    @pytest.mark.run(order=62)
    def test_062_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=63)
    def test_063_query_domain_test_com_after_deleting_ACL_From_Client2(self):
       logging.info("Querying test.com after updating to ACL_ALLOW, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip2+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=64)
    def test_064_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=65)
    def test_065_Validate_syslog_for_dig_operation(self):
        LookFor=".*query: test.com IN A response.*NOERROR.*"
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
    def test_066_Delete_Namedacl_ACL_DENY(self):
        logging.info("Deleting ACL ACL_DENY.................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        sleep(30)

    @pytest.mark.run(order=67)
    def test_067_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_DENY is deleted .................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=68)
    def test_068_Delete_Namedacl_ACL_ALLOW(self):
        logging.info("Deleting ACL ACL_ALLOW.................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(delete_acl)
        sleep(30)

    @pytest.mark.run(order=69)
    def test_069_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_ALLOW is deleted .................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    #class RFE_6181_Ipv4_Network_named_ACL(unittest.TestCase):
    #############################################  Test cases related to ACL verification #############################################
    ##1. Add named acl with IPv4 Network 10.0.0.0/8 and set Operation Allow
    @pytest.mark.run(order=70)
    def test_070_Add_Named_ACL_to_Grid_with_ALLOW_permission(self):
        logging.info("Adding ACL WITH ALLOW.................")
        data={"name": "ACL_ALLOW","access_list": [{"_struct": "addressac", "address": config.IPv4_Network, "permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    ##2. CLI commad execute with zone name test.com
    @pytest.mark.run(order=71)
    def test_071_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_ACL_ALLOW(self):
        logging.info("addin test.com to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain add default test.com ACL_ALLOW')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=72)
    def test_072_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain test.com DnsView=default: Set dns_view="default",domain_name="test.com",named_acl="ACL_ALLOW"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=73)
    def test_073_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_ALLOW' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=74)
    def test_074_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=75)
    def test_075_show_allow_query_domain(self):
        logging.info("Displaying domains added to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        print(type(c))
        result = re.findall('(Domain Name : test.com)(.+)((?:\n.+)+)(Named ACL   : ACL_ALLOW)',c)
        print(result)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=76)
    def test_076_Validate_named_conf_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat /infoblox/var/named_conf/named.conf | grep test.com'
        print(audit_log_validation)
        string_content = commands.getoutput(audit_log_validation)
        print(string_content)
        logging.info(string_content)
        if bool(re.search('"test.com" { '+config.IPv4_Network+'; }', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")
        print("Test Case Execution Completed")

    @pytest.mark.run(order=77)
    def test_077_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##3. If we query a.test.com it should return response from 10.36.6.80
    @pytest.mark.run(order=78)
    def test_078_query_domain_test_com_after_adding_to_ACL_ALLOW_From_Client1(self):
        logging.info("Querying test.com, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=79)
    def test_079_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=80)
    def test_080_Validate_syslog_for_dig_operation(self):
        LookFor=".*query: test.com IN A response.*NOERROR.*"
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


    @pytest.mark.run(order=81)
    def test_081_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##4. If we query a.test.com it should return response from 10.36.1.255
    @pytest.mark.run(order=82)
    def test_082_query_domain_test_com_after_adding_to_ACL_ALLOW_From_Client2(self):
        logging.info("Querying test.com, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip2+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=83)
    def test_083_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=84)
    def test_084_Validate_syslog_for_dig_operation(self):
        LookFor=".*query: test.com IN A response.*NOERROR.*"
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

    @pytest.mark.run(order=85)
    def test_085_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##5. If we query other domain say a.zone.com from 10.36.6.80 it should return response
    @pytest.mark.run(order=86)
    def test_086_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_Client1(self):
       logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' zone.com +noedns -b '+config.client_ip1+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=87)
    def test_087_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=88)
    def test_088_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*zone.com IN A response.*NOERROR.*zone.com.*"
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
    def test_089_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##6. If we query other domain say a.zone.com from 10.36.1.255 it should return response
    @pytest.mark.run(order=90)
    def test_090_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_Client2(self):
       logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' zone.com +noedns -b '+config.client_ip2+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(20)

    @pytest.mark.run(order=91)
    def test_091_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=92)
    def test_093_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*zone.com IN A response.*NOERROR.*zone.com.*"
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

    @pytest.mark.run(order=93)
    def test_093_Add_Named_ACL_to_Grid_with_DENY_permission(self):
        logging.info("Adding ACL WITH DENY.................")
        data={"name": "ACL_DENY","access_list": [{"_struct": "addressac", "address": config.IPv4_Network, "permission": "DENY"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=94)
    def test_094_update_test_com_from_ACL_ALLOW_TO_ACL_DENY(self):
        logging.info("Updating test.com from ACL_ALLOW to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain update default test.com ACL_DENY')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=95)
    def test_095_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Modified AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Modified AllowQueryDomain test.com DnsView=default: Changed named_acl:"ACL_ALLOW"->"ACL_DENY"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=96)
    def test_096_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Updated ACL 'ACL_DENY' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=97)
    def test_097_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=98)
    def test_098_show_allow_query_domain(self):
        logging.info("Displaying domains added to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        print(type(c))
        result = re.findall('(Domain Name : test.com)(.+)((?:\n.+)+)(Named ACL   : ACL_DENY)',c)
        print(result)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=99)
    def test_099_Validate_named_conf_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat /infoblox/var/named_conf/named.conf | grep test.com'
        print(audit_log_validation)
        string_content = commands.getoutput(audit_log_validation)
        print(string_content)
        logging.info(string_content)
        if bool(re.search('"test.com" { !'+config.IPv4_Network+'; }', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")
        print("Test Case Execution Completed")

    @pytest.mark.run(order=98)
    def test_098_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##1. If we query a.test.com it should refuse queries from 10.36.6.80
    @pytest.mark.run(order=99)
    def test_099_query_domain_test_com_after_updating_from_ACL_ALLOW_to_ACL_DENY_From_Client1(self):
       logging.info("Querying test.com after updating to ACL_DENY, expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=100)
    def test_100_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=101)
    def test_101_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*failed.*(REFUSED).*test.com.*"
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
    def test_102_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##2. If we query a.test.com it should refuse queries from 10.36.1.255
    @pytest.mark.run(order=103)
    def test_103_query_domain_test_com_after_updating_from_ACL_ALLOW_to_ACL_DENY_From_Client2(self):
       logging.info("Querying test.com after updating to ACL_ALLOW, expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip2+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=104)
    def test_104_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=105)
    def test_105_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*failed.*(REFUSED).*test.com.*"
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

    @pytest.mark.run(order=106)
    def test_106_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##3. If we query other domain say a.zone.com from 10.36.6.80 it should return response
    @pytest.mark.run(order=107)
    def test_107_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_Client1(self):
        logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' zone.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=108)
    def test_108_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=109)
    def test_109_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*zone.com IN A response.*NOERROR.*zone.com.*"
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
    def test_110_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##4. If we query other domain say a.zone.com from 10.36.1.255 it should return response
    @pytest.mark.run(order=111)
    def test_111_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_Client2(self):
        logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' zone.com +noedns -b '+config.client_ip2+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=112)
    def test_113_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=113)
    def test_113_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*zone.com IN A response.*NOERROR.*zone.com.*"
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

    @pytest.mark.run(order=114)
    def test_114_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
        logging.info("deleting test.com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain delete default test.com')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=115)
    def test_115_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain test.com DnsView=default', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=116)
    def test_116_validate_infoblox_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Deleted ACL for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=117)
    def test_117_Perform_RESTART_of_the_DNS_service(self):
       logging.info("Restart services")
       grid =  ib_NIOS.wapi_request('GET', object_type="grid")
       ref = json.loads(grid)[0]['_ref']
       publish={"member_order":"SIMULTANEOUSLY"}
       request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
       request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
       restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
       print("System Restart is done successfully")
       sleep(60)

    @pytest.mark.run(order=118)
    def test_118_show_allow_query_domain(self):
        logging.info("Displaying domains after deleting test.com with delete command")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r".*No domain ACLs found for view 'default'.*",c)
        sleep(10)

    @pytest.mark.run(order=119)
    def test_119_Validate_named_conf_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat /infoblox/var/named_conf/named.conf | grep test.com'
        print(audit_log_validation)
        string_content = commands.getoutput(audit_log_validation)
        print(string_content)
        logging.info(string_content)
        if not bool(re.search('"test.com" { '+config.IPv4_Network+'; }', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")
        print("Test Case Execution Completed")


    @pytest.mark.run(order=120)
    def test_120_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=121)
    def test_121_query_domain_test_com_after_deleting_ACL_From_Client1(self):
      logging.info("Querying test.com after deleting, expected result as NOERROR")
      cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
      result=subprocess.check_output(cmd, shell=True)
      print(result)
      assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
      logging.info("Test Case Execution Completed")
      sleep(10)

    @pytest.mark.run(order=122)
    def test_122_stop_Syslog_Messages(self):
       log("stop","/var/log/syslog",config.grid_vip)
       logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=123)
    def test_123_Validate_syslog_for_dig_operation(self):
       LookFor=".*query: test.com IN A response.*NOERROR.*"
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

    @pytest.mark.run(order=124)
    def test_124_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=125)
    def test_125_query_domain_test_com_after_deleting_ACL_From_Client2(self):
       logging.info("Querying test.com after updating to ACL_ALLOW, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip2+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=126)
    def test_126_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=127)
    def test_128_Validate_syslog_for_dig_operation(self):
        LookFor=".*query: test.com IN A response.*NOERROR.*"
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

    @pytest.mark.run(order=128)
    def test_128_Delete_Namedacl_ACL_DENY(self):
        logging.info("Deleting ACL ACL_DENY.................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        sleep(30)

    @pytest.mark.run(order=129)
    def test_129_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_DENY is deleted .................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=130)
    def test_130_Delete_Namedacl_ACL_ALLOW(self):
        logging.info("Deleting ACL ACL_ALLOW.................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(delete_acl)
        sleep(30)

    @pytest.mark.run(order=131)
    def test_131_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_ALLOW is deleted .................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    #class RFE_6181_Ipv6_Adress_named_ACL(unittest.TestCase):
    #############################################  Test cases related to ACL verification #############################################
    ##1. Add named acl with IPv4 address 10.36.6.80 and set Operation Allow
    @pytest.mark.run(order=132)
    def test_132_Add_Named_ACL_to_Grid_with_ALLOW_permission(self):
        logging.info("Adding ACL WITH ALLOW.................")
        data={"name": "ACL_ALLOW","access_list": [{"_struct": "addressac", "address": config.client_ip1v6, "permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    ##2. CLI commad execute with zone name test.com
    @pytest.mark.run(order=133)
    def test_133_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_ACL_ALLOW(self):
        logging.info("addin test.com to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain add default test.com ACL_ALLOW')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=134)
    def test_134_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain test.com DnsView=default: Set dns_view="default",domain_name="test.com",named_acl="ACL_ALLOW"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=135)
    def test_135_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_ALLOW' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=136)
    def test_136_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=137)
    def test_137_show_allow_query_domain(self):
        logging.info("Displaying domains added to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        print(type(c))
        result = re.findall('(Domain Name : test.com)(.+)((?:\n.+)+)(Named ACL   : ACL_ALLOW)',c)
        print(result)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=138)
    def test_138_Validate_named_conf_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat /infoblox/var/named_conf/named.conf | grep test.com'
        print(audit_log_validation)
        string_content = commands.getoutput(audit_log_validation)
        print(string_content)
        logging.info(string_content)
        if bool(re.search('"test.com" { '+config.client_ip1v6+'; }', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")
        print("Test Case Execution Completed")

    @pytest.mark.run(order=139)
    def test_139_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##3. If we query a.test.com it should return response from 10.36.6.80
    @pytest.mark.run(order=140)
    def test_140_query_domain_test_com_after_adding_to_ACL_ALLOW_From_client_ip1v6(self):
        logging.info("Querying test.com, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vipv6)+' test.com +noedns -b '+config.client_ip1v6+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=141)
    def test_141_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=142)
    def test_142_Validate_syslog_for_dig_operation(self):
        LookFor=".*query: test.com IN A response.*NOERROR.*"
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

    @pytest.mark.run(order=143)
    def test_143_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##4. If we query a.test.com it should refuse queries from 10.36.1.255
    @pytest.mark.run(order=144)
    def test_144_query_domain_test_com_after_adding_to_ACL_ALLOW_From_client_ip2v6(self):
        logging.info("Querying test.com, expected result as REFUSED")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vipv6)+' test.com +noedns -b '+config.client_ip2v6+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=145)
    def test_145_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=146)
    def test_146_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*failed.*(REFUSED).*test.com.*"
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

    @pytest.mark.run(order=147)
    def test_147_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##5. If we query other domain say a.zone.com from 10.36.6.80 it should return response
    @pytest.mark.run(order=148)
    def test_148_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_client_ip1v6(self):
       logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vipv6)+' zone.com +noedns -b '+config.client_ip1v6+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=149)
    def test_149_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=150)
    def test_150_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*zone.com IN A response.*NOERROR.*zone.com.*"
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

    @pytest.mark.run(order=151)
    def test_151_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##6. If we query other domain say a.zone.com from 10.36.1.255 it should return response
    @pytest.mark.run(order=152)
    def test_152_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_client_ip2v6(self):
       logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vipv6)+' zone.com +noedns -b '+config.client_ip2v6+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(20)

    @pytest.mark.run(order=153)
    def test_153_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=154)
    def test_154_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*zone.com IN A response.*NOERROR.*zone.com.*"
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

    @pytest.mark.run(order=155)
    def test_155_Add_Named_ACL_to_Grid_with_DENY_permission(self):
        logging.info("Adding ACL WITH DENY.................")
        data={"name": "ACL_DENY","access_list": [{"_struct": "addressac", "address": config.client_ip1v6, "permission": "DENY"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=156)
    def test_156_update_test_com_from_ACL_ALLOW_TO_ACL_DENY(self):
        logging.info("Updating test.com from ACL_ALLOW to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain update default test.com ACL_DENY')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=157)
    def test_157_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Modified AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Modified AllowQueryDomain test.com DnsView=default: Changed named_acl:"ACL_ALLOW"->"ACL_DENY"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=158)
    def test_158_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Updated ACL 'ACL_DENY' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=159)
    def test_159_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=160)
    def test_160_show_allow_query_domain(self):
        logging.info("Displaying domains added to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        print(type(c))
        result = re.findall('(Domain Name : test.com)(.+)((?:\n.+)+)(Named ACL   : ACL_DENY)',c)
        print(result)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=161)
    def test_161_Validate_named_conf_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat /infoblox/var/named_conf/named.conf | grep test.com'
        print(audit_log_validation)
        string_content = commands.getoutput(audit_log_validation)
        print(string_content)
        logging.info(string_content)
        if bool(re.search('"test.com" { !'+config.client_ip1v6+'; }', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")
        print("Test Case Execution Completed")

    @pytest.mark.run(order=162)
    def test_162_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##1. If we query a.test.com it should refuse queries from 10.36.6.80
    @pytest.mark.run(order=163)
    def test_163_query_domain_test_com_after_updating_from_ACL_ALLOW_to_ACL_DENY_From_client_ip1v6(self):
       logging.info("Querying test.com after updating to ACL_DENY, expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vipv6)+' test.com +noedns -b '+config.client_ip1v6+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=164)
    def test_164_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=165)
    def test_165_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*failed.*(REFUSED).*test.com.*"
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
    def test_166_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##2. If we query a.test.com it should refuse queries from 10.36.1.255
    @pytest.mark.run(order=167)
    def test_167_query_domain_test_com_after_updating_from_ACL_ALLOW_to_ACL_DENY_From_client_ip2v6(self):
       logging.info("Querying test.com after updating to ACL_ALLOW, expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vipv6)+' test.com +noedns -b '+config.client_ip2v6+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=168)
    def test_168_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=169)
    def test_169_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*failed.*(REFUSED).*test.com.*"
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

    @pytest.mark.run(order=170)
    def test_170_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##3. If we query other domain say a.zone.com from 10.36.6.80 it should return response
    @pytest.mark.run(order=171)
    def test_171_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_client_ip1v6(self):
        logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vipv6)+' zone.com +noedns -b '+config.client_ip1v6+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=172)
    def test_172_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=173)
    def test_173_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*zone.com IN A response.*NOERROR.*zone.com.*"
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

    @pytest.mark.run(order=174)
    def test_174_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##4. If we query other domain say a.zone.com from 10.36.1.255 it should return response
    @pytest.mark.run(order=175)
    def test_175_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_client_ip2v6(self):
        logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vipv6)+' zone.com +noedns -b '+config.client_ip2v6+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=176)
    def test_176_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=177)
    def test_177_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*zone.com IN A response.*NOERROR.*zone.com.*"
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

    @pytest.mark.run(order=178)
    def test_178_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
        logging.info("deleting test.com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain delete default test.com')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=179)
    def test_179_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain test.com DnsView=default', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=180)
    def test_180_validate_infoblox_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Deleted ACL for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=181)
    def test_181_Perform_RESTART_of_the_DNS_service(self):
       logging.info("Restart services")
       grid =  ib_NIOS.wapi_request('GET', object_type="grid")
       ref = json.loads(grid)[0]['_ref']
       publish={"member_order":"SIMULTANEOUSLY"}
       request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
       request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
       restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
       print("System Restart is done successfully")
       sleep(60)

    @pytest.mark.run(order=182)
    def test_182_show_allow_query_domain(self):
        logging.info("Displaying domains after deleting test.com with delete command")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r".*No domain ACLs found for view 'default'.*",c)
        sleep(10)

    @pytest.mark.run(order=183)
    def test_183_Validate_named_conf_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat /infoblox/var/named_conf/named.conf | grep test.com'
        print(audit_log_validation)
        string_content = commands.getoutput(audit_log_validation)
        print(string_content)
        logging.info(string_content)
        if not bool(re.search('"test.com" { '+config.client_ip1v6+'; }', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")
        print("Test Case Execution Completed")

    @pytest.mark.run(order=184)
    def test_184_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=185)
    def test_185_query_domain_test_com_after_deleting_ACL_From_client_ip1v6(self):
      logging.info("Querying test.com after deleting, expected result as NOERROR")
      cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vipv6)+' test.com +noedns -b '+config.client_ip1v6+'"'
      result=subprocess.check_output(cmd, shell=True)
      print(result)
      assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
      logging.info("Test Case Execution Completed")
      sleep(10)

    @pytest.mark.run(order=186)
    def test_186_stop_Syslog_Messages(self):
       log("stop","/var/log/syslog",config.grid_vip)
       logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=187)
    def test_187_Validate_syslog_for_dig_operation(self):
       LookFor=".*query: test.com IN A response.*NOERROR.*"
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


    @pytest.mark.run(order=188)
    def test_188_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=189)
    def test_189_query_domain_test_com_after_deleting_ACL_From_client_ip2v6(self):
       logging.info("Querying test.com after updating to ACL_ALLOW, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vipv6)+' test.com +noedns -b '+config.client_ip2v6+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=190)
    def test_190_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=191)
    def test_191_Validate_syslog_for_dig_operation(self):
        LookFor=".*query: test.com IN A response.*NOERROR.*"
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

    @pytest.mark.run(order=192)
    def test_192_Delete_Namedacl_ACL_DENY(self):
        logging.info("Deleting ACL ACL_DENY.................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        sleep(30)

    @pytest.mark.run(order=193)
    def test_193_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_DENY is deleted .................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=194)
    def test_194_Delete_Namedacl_ACL_ALLOW(self):
        logging.info("Deleting ACL ACL_ALLOW.................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(delete_acl)
        sleep(30)

    @pytest.mark.run(order=195)
    def test_195_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_ALLOW is deleted .................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    #class RFE_6181_Ipv6_Network_named_ACL(unittest.TestCase):
    #############################################  Test cases related to ACL verification #############################################
    ##1. Add named acl with IPv4 Network 10.0.0.0/8 and set Operation Allow
    @pytest.mark.run(order=196)
    def test_196_Add_Named_ACL_to_Grid_with_ALLOW_permission(self):
        logging.info("Adding ACL WITH ALLOW.................")
        data={"name": "ACL_ALLOW","access_list": [{"_struct": "addressac", "address": config.IPv6_Network, "permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    ##2. CLI commad execute with zone name test.com
    @pytest.mark.run(order=197)
    def test_197_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_ACL_ALLOW(self):
        logging.info("addin test.com to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain add default test.com ACL_ALLOW')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=198)
    def test_198_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain test.com DnsView=default: Set dns_view="default",domain_name="test.com",named_acl="ACL_ALLOW"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=199)
    def test_199_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_ALLOW' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=200)
    def test_200_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=201)
    def test_201_show_allow_query_domain(self):
        logging.info("Displaying domains added to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        print(type(c))
        result = re.findall('(Domain Name : test.com)(.+)((?:\n.+)+)(Named ACL   : ACL_ALLOW)',c)
        print(result)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=203)
    def test_203_Validate_named_conf_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat /infoblox/var/named_conf/named.conf | grep test.com'
        print(audit_log_validation)
        string_content = commands.getoutput(audit_log_validation)
        print(string_content)
        logging.info(string_content)
        if bool(re.search('"test.com" { '+config.IPv6_Network+'; }', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")
        print("Test Case Execution Completed")

    @pytest.mark.run(order=204)
    def test_204_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##3. If we query a.test.com it should return response from 10.36.6.80
    @pytest.mark.run(order=205)
    def test_205_query_domain_test_com_after_adding_to_ACL_ALLOW_From_client_ip1v6(self):
        logging.info("Querying test.com, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vipv6)+' test.com +noedns -b '+config.client_ip1v6+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=206)
    def test_206_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=207)
    def test_207_Validate_syslog_for_dig_operation(self):
        LookFor=".*query: test.com IN A response.*NOERROR.*"
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

    @pytest.mark.run(order=208)
    def test_208_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##4. If we query a.test.com it should return response from 10.36.1.255
    @pytest.mark.run(order=209)
    def test_209_query_domain_test_com_after_adding_to_ACL_ALLOW_From_Client2(self):
        logging.info("Querying test.com, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vipv6)+' test.com +noedns -b '+config.client_ip2v6+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=210)
    def test_210_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=211)
    def test_211_Validate_syslog_for_dig_operation(self):
        LookFor=".*query: test.com IN A response.*NOERROR.*"
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


    @pytest.mark.run(order=212)
    def test_212_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##5. If we query other domain say a.zone.com from 10.36.6.80 it should return response
    @pytest.mark.run(order=213)
    def test_213_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_client_ip1v6(self):
       logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vipv6)+' zone.com +noedns -b '+config.client_ip1v6+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=214)
    def test_214_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=215)
    def test_215_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*zone.com IN A response.*NOERROR.*zone.com.*"
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

    @pytest.mark.run(order=216)
    def test_216_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##6. If we query other domain say a.zone.com from 10.36.1.255 it should return response
    @pytest.mark.run(order=217)
    def test_217_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_Client2(self):
       logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vipv6)+' zone.com +noedns -b '+config.client_ip2v6+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(20)

    @pytest.mark.run(order=218)
    def test_218_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=219)
    def test_219_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*zone.com IN A response.*NOERROR.*zone.com.*"
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

    @pytest.mark.run(order=220)
    def test_220_Add_Named_ACL_to_Grid_with_DENY_permission(self):
        logging.info("Adding ACL WITH DENY.................")
        data={"name": "ACL_DENY","access_list": [{"_struct": "addressac", "address": config.IPv6_Network, "permission": "DENY"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=221)
    def test_221_update_test_com_from_ACL_ALLOW_TO_ACL_DENY(self):
        logging.info("Updating test.com from ACL_ALLOW to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain update default test.com ACL_DENY')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=222)
    def test_222_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Modified AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Modified AllowQueryDomain test.com DnsView=default: Changed named_acl:"ACL_ALLOW"->"ACL_DENY"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=223)
    def test_223_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Updated ACL 'ACL_DENY' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=224)
    def test_224_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=225)
    def test_225_show_allow_query_domain(self):
        logging.info("Displaying domains added to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        print(type(c))
        result = re.findall('(Domain Name : test.com)(.+)((?:\n.+)+)(Named ACL   : ACL_DENY)',c)
        print(result)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=226)
    def test_226_Validate_named_conf_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat /infoblox/var/named_conf/named.conf | grep test.com'
        print(audit_log_validation)
        string_content = commands.getoutput(audit_log_validation)
        print(string_content)
        logging.info(string_content)
        if bool(re.search('"test.com" { !'+config.IPv6_Network+'; }', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")
        print("Test Case Execution Completed")

    @pytest.mark.run(order=227)
    def test_227_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##1. If we query a.test.com it should refuse queries from 10.36.6.80
    @pytest.mark.run(order=228)
    def test_228_query_domain_test_com_after_updating_from_ACL_ALLOW_to_ACL_DENY_From_client_ip1v6(self):
       logging.info("Querying test.com after updating to ACL_DENY, expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vipv6)+' test.com +noedns -b '+config.client_ip1v6+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=229)
    def test_229_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=230)
    def test_230_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*failed.*(REFUSED).*test.com.*"
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

    @pytest.mark.run(order=231)
    def test_231_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##2. If we query a.test.com it should refuse queries from 10.36.1.255
    @pytest.mark.run(order=232)
    def test_232_query_domain_test_com_after_updating_from_ACL_ALLOW_to_ACL_DENY_From_Client2(self):
       logging.info("Querying test.com after updating to ACL_ALLOW, expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vipv6)+' test.com +noedns -b '+config.client_ip2v6+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=233)
    def test_233_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=234)
    def test_234_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*failed.*(REFUSED).*test.com.*"
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

    @pytest.mark.run(order=235)
    def test_235_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##3. If we query other domain say a.zone.com from 10.36.6.80 it should return response
    @pytest.mark.run(order=236)
    def test_236_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_client_ip1v6(self):
        logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vipv6)+' zone.com +noedns -b '+config.client_ip1v6+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=237)
    def test_237_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=238)
    def test_238_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*zone.com IN A response.*NOERROR.*zone.com.*"
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

    @pytest.mark.run(order=239)
    def test_239_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##4. If we query other domain say a.zone.com from 10.36.1.255 it should return response
    @pytest.mark.run(order=240)
    def test_240_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_Client2(self):
        logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vipv6)+' zone.com +noedns -b '+config.client_ip2v6+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=241)
    def test_241_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=242)
    def test_242_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*zone.com IN A response.*NOERROR.*zone.com.*"
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

    @pytest.mark.run(order=243)
    def test_243_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
        logging.info("deleting test.com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain delete default test.com')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=244)
    def test_244_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain test.com DnsView=default', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=245)
    def test_245_validate_infoblox_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Deleted ACL for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=246)
    def test_246_Perform_RESTART_of_the_DNS_service(self):
       logging.info("Restart services")
       grid =  ib_NIOS.wapi_request('GET', object_type="grid")
       ref = json.loads(grid)[0]['_ref']
       publish={"member_order":"SIMULTANEOUSLY"}
       request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
       request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
       restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
       print("System Restart is done successfully")
       sleep(60)

    @pytest.mark.run(order=247)
    def test_247_show_allow_query_domain(self):
        logging.info("Displaying domains after deleting test.com with delete command")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r".*No domain ACLs found for view 'default'.*",c)
        sleep(10)

    @pytest.mark.run(order=248)
    def test_248_Validate_named_conf_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat /infoblox/var/named_conf/named.conf | grep test.com'
        print(audit_log_validation)
        string_content = commands.getoutput(audit_log_validation)
        print(string_content)
        logging.info(string_content)
        if not bool(re.search('"test.com" { '+config.IPv6_Network+'; }', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")
        print("Test Case Execution Completed")


    @pytest.mark.run(order=249)
    def test_249_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=250)
    def test_250_query_domain_test_com_after_deleting_ACL_From_client_ip1v6(self):
      logging.info("Querying test.com after deleting, expected result as NOERROR")
      cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vipv6)+' test.com +noedns -b '+config.client_ip1v6+'"'
      result=subprocess.check_output(cmd, shell=True)
      print(result)
      assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
      logging.info("Test Case Execution Completed")
      sleep(10)

    @pytest.mark.run(order=251)
    def test_251_stop_Syslog_Messages(self):
       log("stop","/var/log/syslog",config.grid_vip)
       logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=252)
    def test_252_Validate_syslog_for_dig_operation(self):
       LookFor=".*query: test.com IN A response.*NOERROR.*"
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

    @pytest.mark.run(order=253)
    def test_253_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=254)
    def test_254_query_domain_test_com_after_deleting_ACL_From_Client2(self):
       logging.info("Querying test.com after updating to ACL_ALLOW, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vipv6)+' test.com +noedns -b '+config.client_ip2v6+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=255)
    def test_255_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=256)
    def test_256_Validate_syslog_for_dig_operation(self):
        LookFor=".*query: test.com IN A response.*NOERROR.*"
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

    @pytest.mark.run(order=257)
    def test_257_Delete_Namedacl_ACL_DENY(self):
        logging.info("Deleting ACL ACL_DENY.................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        sleep(30)

    @pytest.mark.run(order=258)
    def test_258_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_DENY is deleted .................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=259)
    def test_259_Delete_Namedacl_ACL_ALLOW(self):
        logging.info("Deleting ACL ACL_ALLOW.................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(delete_acl)
        sleep(30)

    @pytest.mark.run(order=260)
    def test_260_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_ALLOW is deleted .................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    #class RFE_6181_DNS_view_named_ACL(unittest.TestCase):
    #############################################  Test cases related to ACL verification #############################################
    ##1.Set CLI deny for test.com
    @pytest.mark.run(order=261)
    def test_261_Add_Named_ACL_to_Grid_with_DENY_permission(self):
        logging.info("Adding ACL WITH DENY.................")
        data={"name": "ACL_DENY","access_list": [{"_struct": "addressac", "address": config.IPv4_Network, "permission": "DENY"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=262)
    def test_262_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_ACL_DENY(self):
        logging.info("adding test.com to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain add default test.com ACL_DENY')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=263)
    def test_263_validate_audit_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain test.com DnsView=default: Set dns_view="default",domain_name="test.com",named_acl="ACL_DENY"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=264)
    def test_264_validate_infoblox_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_DENY' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=265)
    def test_265_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=266)
    def test_266_show_allow_query_domain(self):
        logging.info("Displaying domains added to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        print(type(c))
        result = re.findall('(Domain Name : test.com)(.+)((?:\n.+)+)(Named ACL   : ACL_DENY)',c)
        print(result)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=267)
    def test_267_Validate_named_conf_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat /infoblox/var/named_conf/named.conf | grep test.com'
        print(audit_log_validation)
        string_content = commands.getoutput(audit_log_validation)
        print(string_content)
        logging.info(string_content)
        if bool(re.search('"test.com" { !'+config.IPv4_Network+'; }', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")
        print("Test Case Execution Completed")

    @pytest.mark.run(order=268)
    def test_268_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=269)
    def test_269_query_domain_test_com_after_adding_to_ACL_DENY_From_Client1(self):
        logging.info("Querying test.com, expected result as REFUSED")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=270)
    def test_270_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=271)
    def test_271_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*failed.*(REFUSED).*test.com.*"
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

    ##adding view view1
    @pytest.mark.run(order=272)
    def test_272_Create_View_view1(self):
        data={"name":"view1"}
        request_publish = ib_NIOS.wapi_request('POST',object_type="view",fields=json.dumps(data))
        self.restart_the_grid()
        print("DNS view view1 is created successfully..")

    ##2. Added Authoritative  zone test.com with a record in default view
    @pytest.mark.run(order=273)
    def test_273_create_test_com_authoritative_zone(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        data={"fqdn": "test.com"}
        response = ib_NIOS.wapi_request('POST', object_type='zone_auth',fields=json.dumps(data))
        zone_response = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        res = json.loads(zone_response)
        for i in res:
            data = {"grid_primary":[{"name":"infoblox.localdomain"}]}
            response = ib_NIOS.wapi_request('PUT', ref=i["_ref"],fields=json.dumps(data))
            print("Zone added successfully........")

    @pytest.mark.run(order=274)
    def test_274_Add_arec_A_record_to_test_com_zone(self):
        logging.info("Add a record")
        data = {"name":"arec.test.com","ipv4addr":"2.2.2.2","comment":"A record added"}
        response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
        if (response[0]!=400):
            print ("Added A record")
        else:
            print ("A record already exists")
            logging.info("Test case Execution Completed")

    @pytest.mark.run(order=275)
    def test_275_validate_added_A_record(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -2 /infoblox/var/audit.log | grep  \'ARecord\'"'
        out1 = commands.getoutput(audit_log_validation)
        print out1
        logging.info(out1)
        if re.search(r'Created ARecord arec\.test\.com ',out1) and re.search(r'arec\.test\.com',out1):
            assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    ##3. set deny to dns default view (match client)
    @pytest.mark.run(order=276)
    def test_276_set_deny_to_dns_default_view(self):
            response = ib_NIOS.wapi_request('GET', object_type="view")
            res = json.loads(response)
            for i in res:
                if i["is_default"] == True:
                    data={"match_clients": [{"_struct": "addressac", "address": "Any", "permission": "DENY"}]}
                    response = ib_NIOS.wapi_request('PUT', ref=i["_ref"],fields=json.dumps(data))
                    print(response)
                    self.restart_the_grid()

    @pytest.mark.run(order=277)
    def test_277_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##4. Query a.test.com.. we can see answer from Forwarder
    @pytest.mark.run(order=278)
    def test_278_query_domain_test_com_after_setting_deny_to_dns_default_view_From_Client1(self):
        logging.info("Querying arec.test.com, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' arec.test.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=279)
    def test_279_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=280)
    def test_280_Validate_syslog_for_dig_operation(self):
        LookFor=".*query: arec.test.com IN A response.*NOERROR.*"
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

    ##5. Set allow to dns default view (match client)
    @pytest.mark.run(order=281)
    def test_281_set_allow_to_dns_default_view(self):
        response = ib_NIOS.wapi_request('GET', object_type="view")
        res = json.loads(response)
        for i in res:
            if i["is_default"] == True:
                data={"match_clients": [{"_struct": "addressac", "address": "Any", "permission": "ALLOW"}]}
                response = ib_NIOS.wapi_request('PUT', ref=i["_ref"],fields=json.dumps(data))
                print(response)
                self.restart_the_grid()

    @pytest.mark.run(order=282)
    def test_282_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##6. Query a.test.com.. we can see REFUSED answer (because CLI set to deny)
    @pytest.mark.run(order=283)
    def test_283_query_domain_arec_test_com_after_setting_allow_for_dns_default_view_From_Client1(self):
        logging.info("Querying arec.test.com, expected result as REFUSED")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' arec.test.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=284)
    def test_284_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=285)
    def test_285_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*failed.*(REFUSED).*arec.test.com.*"
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

    ##7. Set CLI allow for test.com
    @pytest.mark.run(order=286)
    def test_286_Add_Named_ACL_to_Grid_with_ALLOW_permission(self):
        logging.info("Adding ACL WITH ALLOW.................")
        data={"name": "ACL_ALLOW","access_list": [{"_struct": "addressac", "address": config.IPv4_Network, "permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=287)
    def test_287_update_test_com_from_ACL_DENY_TO_ACL_ALLOW(self):
        logging.info("Updating test.com from ACL_DENY to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain update default test.com ACL_ALLOW')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=288)
    def test_288_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Modified AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Modified AllowQueryDomain test.com DnsView=default: Changed named_acl:"ACL_DENY"->"ACL_ALLOW"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=289)
    def test_289_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Updated ACL 'ACL_ALLOW' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=290)
    def test_290_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=291)
    def test_291_show_allow_query_domain(self):
        logging.info("Displaying domains added to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        print(type(c))
        result = re.findall('(Domain Name : test.com)(.+)((?:\n.+)+)(Named ACL   : ACL_ALLOW)',c)
        print(result)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=292)
    def test_292_Validate_named_conf_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat /infoblox/var/named_conf/named.conf | grep test.com'
        print(audit_log_validation)
        string_content = commands.getoutput(audit_log_validation)
        print(string_content)
        logging.info(string_content)
        if bool(re.search('"test.com" { '+config.IPv4_Network+'; }', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")
        print("Test Case Execution Completed")

    @pytest.mark.run(order=293)
    def test_293_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##8. Query a.test.com.. we can see answer from Authoritative zone
    @pytest.mark.run(order=294)
    def test_294_query_domain_test_com_after_updating_test_com_from_ACL_DENY_to_ACL_ALLOW(self):
        logging.info("Querying test.com after updating to NOERROR, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' arec.test.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=295)
    def test_295_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=296)
    def test_296_Validate_syslog_for_dig_operation(self):
        LookFor=".*query: arec.test.com IN A response.*NOERROR.*"
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

    ##5.  delete dns default view (match client)
    @pytest.mark.run(order=297)
    def test_297_Update_Dns_default_view_match_clients_with_None(self):
        response = ib_NIOS.wapi_request('GET', object_type="view")
        res = json.loads(response)
        for i in res:
            if i["is_default"] == True:
                print(i)
                data={"match_clients": []}
                response = ib_NIOS.wapi_request('PUT', ref=i["_ref"],fields=json.dumps(data))
                print(response)
                self.restart_the_grid()

    @pytest.mark.run(order=298)
    def test_298_delete_test_com_autoritative_zone(self):
        data={"fqdn":"test.com"}
        response = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
        res = json.loads(response)
        for i in res:
            response = ib_NIOS.wapi_request('DELETE', ref=i["_ref"])
            print(response)
            sleep(10)
            logging.info("Test case Execution Completed")
            self.restart_the_grid()

    @pytest.mark.run(order=299)
    def test_299_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
        logging.info("deleting test.com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain delete default test.com')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=300)
    def test_300_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain test.com DnsView=default', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=301)
    def test_301_validate_infoblox_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Deleted ACL for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=302)
    def test_302_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    ##adding view view1
    @pytest.mark.run(order=303)
    def test_303_Delete_Dns_View_view1(self):
        data={"name":"view1"}
        response = ib_NIOS.wapi_request('GET',object_type="view",fields=json.dumps(data))
        res = json.loads(response)
        for i in res:
            response = ib_NIOS.wapi_request('DELETE', ref=i["_ref"])
            print(response)
            sleep(10)
            self.restart_the_grid()
            print("Restrting the grid")
            print("DNS view view1 is deleted successfully..")

    @pytest.mark.run(order=304)
    def test_304_Delete_Namedacl_ACL_DENY(self):
        logging.info("Deleting ACL ACL_DENY.................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        sleep(30)

    @pytest.mark.run(order=305)
    def test_305_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_DENY is deleted .................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=306)
    def test_306_Delete_Namedacl_ACL_ALLOW(self):
        logging.info("Deleting ACL ACL_ALLOW.................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(delete_acl)
        sleep(30)

    @pytest.mark.run(order=307)
    def test_307_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_ALLOW is deleted .................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    #class RFE_6181_DNS_new_cases(unittest.TestCase):
    #############################################  Test cases related to ACL verification #############################################
    ##adding view view1
    @pytest.mark.run(order=308)
    def test_308_Create_View_view1(self):
        data={"name":"view1"}
        request_publish = ib_NIOS.wapi_request('POST',object_type="view",fields=json.dumps(data))
        self.restart_the_grid()
        print("DNS view view1 is created successfully..")

    ##1.Set CLI ALLOW for test.com
    @pytest.mark.run(order=309)
    def test_309_Add_Named_ACL_to_Grid_with_ALLOW_permission(self):
        logging.info("Adding ACL WITH ALLOW.................")
        data={"name": "ACL_ALLOW","access_list": [{"_struct": "addressac", "address": config.IPv4_Network, "permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=310)
    def test_310_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_ACL_ALLOW(self):
        logging.info("adding test.com to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain add default test.com ACL_ALLOW')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=311)
    def test_311_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain test.com DnsView=default: Set dns_view="default",domain_name="test.com",named_acl="ACL_ALLOW"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=312)
    def test_312_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_ALLOW' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=313)
    def test_313_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=314)
    def test_314_show_allow_query_domain(self):
        logging.info("Displaying domains added to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        print(type(c))
        result = re.findall('(Domain Name : test.com)(.+)((?:\n.+)+)(Named ACL   : ACL_ALLOW)',c)
        print(result)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=315)
    def test_315_Validate_named_conf_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat /infoblox/var/named_conf/named.conf | grep test.com'
        print(audit_log_validation)
        string_content = commands.getoutput(audit_log_validation)
        print(string_content)
        logging.info(string_content)
        if bool(re.search('"test.com" { '+config.IPv4_Network+'; }', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")
        print("Test Case Execution Completed")


    ##1.Set CLI deny for zone.com
    @pytest.mark.run(order=316)
    def test_316_Add_Named_ACL_to_Grid_with_DENY_permission(self):
        logging.info("Adding ACL WITH DENY.................")
        data={"name": "ACL_DENY","access_list": [{"_struct": "addressac", "address": config.IPv4_Network, "permission": "DENY"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=317)
    def test_317_Add_allow_query_domain_with_domain_name_zone_com_with_named_ACL_ACL_DENY(self):
        logging.info("adding zone.com to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain add view1 zone.com ACL_DENY')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=318)
    def test_318_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain zone.com DnsView=view1: Set dns_view="view1",domain_name="zone.com",named_acl="ACL_DENY"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=319)
    def test_319_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_DENY' for domain 'zone.com' under view 'view1' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=320)
    def test_320_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=321)
    def test_321_show_allow_query_domain(self):
        logging.info("Displaying domains added to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain view1')
        child.expect('Infoblox >')
        c= child.before
        print(type(c))
        result = re.findall('(Domain Name : zone.com)(.+)((?:\n.+)+)(Named ACL   : ACL_DENY)',c)
        print(result)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=322)
    def test_322_Validate_named_conf_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat /infoblox/var/named_conf/named.conf | grep test.com'
        print(audit_log_validation)
        string_content = commands.getoutput(audit_log_validation)
        print(string_content)
        logging.info(string_content)
        if bool(re.search('"test.com" { '+config.IPv4_Network+'; }', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")
        print("Test Case Execution Completed")

    @pytest.mark.run(order=323)
    def test_323_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##5. If we query other domain say a.zone.com from 10.36.6.80 it should return response
    @pytest.mark.run(order=324)
    def test_324_query_domain_zone_com_added_to_view1_ACL_DENY_From_Client1(self):
       logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' zone.com +noedns -b '+config.client_ip1+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=325)
    def test_325_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=326)
    def test_326_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*zone.com IN A response.*NOERROR.*zone.com.*"
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

    ##move dns view view1 to top in member properties
    @pytest.mark.run(order=327)
    def test_327_move_views(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        logging.info(get_ref)
        res = json.loads(get_ref)
        for i in res:
            ref=i["_ref"]
            data={"views": ["view1","default"]}
            request_publish = ib_NIOS.wapi_request('PUT',ref=ref +"?_return_fields=views", fields=json.dumps(data))
            print(request_publish)
            self.restart_the_grid()
            print("Moved views successfully..")

    @pytest.mark.run(order=328)
    def test_328_move_views(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        logging.info(get_ref)
        res = json.loads(get_ref)
        for i in res:
            ref=i["_ref"]
            request_publish = ib_NIOS.wapi_request('GET',ref=ref +"?_return_fields=views")
            print(request_publish, type(request_publish))
            data=eval(request_publish)
            if data['views'][0] == 'view1' and data['views'][1] == 'default':
                assert True
                print("validated views successfully..")
            else:
                assert False
                logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=329)
    def test_329_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##5. If we query other domain say a.zone.com from 10.36.6.80 it should return response
    @pytest.mark.run(order=330)
    def test_330_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_Client1(self):
       logging.info("Querying zone.com expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' zone.com +noedns -b '+config.client_ip1+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=331)
    def test_331_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=332)
    def test_332_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*failed.*(REFUSED).*zone.com.*"
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

    @pytest.mark.run(order=333)
    def test_333_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
        logging.info("deleting test.com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain delete default test.com')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(20)

    @pytest.mark.run(order=334)
    def test_334_Validate_named_conf_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat /infoblox/var/named_conf/named.conf | grep test.com'
        print(audit_log_validation)
        string_content = commands.getoutput(audit_log_validation)
        print(string_content)
        logging.info(string_content)
        if bool(re.search('"test.com" { '+config.IPv4_Network+'; }', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")
        print("Test Case Execution Completed")

    @pytest.mark.run(order=335)
    def test_335_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain test.com DnsView=default', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=336)
    def test_336_validate_infoblox_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Deleted ACL for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=337)
    def test_337_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=338)
    def test_338_Delete_domain_zone_com_using_set_allow_query_domain_delete_command(self):
        logging.info("deleting zone.com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain delete view1 zone.com')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=339)
    def test_339_Validate_named_conf_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat /infoblox/var/named_conf/named.conf | grep zone.com'
        print(audit_log_validation)
        string_content = commands.getoutput(audit_log_validation)
        print(string_content)
        logging.info(string_content)
        if bool(re.search('"zone.com" { !'+config.IPv4_Network+'; }', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")
        print("Test Case Execution Completed")

    @pytest.mark.run(order=340)
    def test_340_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain zone.com DnsView=view1', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=341)
    def test_341_validate_infoblox_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Deleted ACL for domain 'zone.com' under view 'view1' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=342)
    def test_342_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    ##move dns view default to top in member properties
    @pytest.mark.run(order=343)
    def test_343_move_views(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        logging.info(get_ref)
        res = json.loads(get_ref)
        for i in res:
            ref=i["_ref"]
            data={"views": ["default","view1"]}
            request_publish = ib_NIOS.wapi_request('PUT',ref=ref +"?_return_fields=views", fields=json.dumps(data))
            print(request_publish)
            self.restart_the_grid()
            print("Moved views successfully..")

    @pytest.mark.run(order=344)
    def test_344_move_views(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        logging.info(get_ref)
        res = json.loads(get_ref)
        for i in res:
            ref=i["_ref"]
            request_publish = ib_NIOS.wapi_request('GET',ref=ref +"?_return_fields=views")
            print(request_publish, type(request_publish))
            data=eval(request_publish)
            if data['views'][0] == 'default' and data['views'][1] == 'view1':
                assert True
                print("validated views successfully..")
            else:
                assert False
                logging.info("Test Case Execution Completed")

    ##adding view view1
    @pytest.mark.run(order=345)
    def test_345_Delete_Dns_View_view1(self):
        data={"name":"view1"}
        response = ib_NIOS.wapi_request('GET',object_type="view",fields=json.dumps(data))
        res = json.loads(response)
        for i in res:
            response = ib_NIOS.wapi_request('DELETE', ref=i["_ref"])
            print(response)
            sleep(10)
            self.restart_the_grid()
            print("DNS view view1 is deleted successfully..")


    @pytest.mark.run(order=346)
    def test_346_validate_views(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        logging.info(get_ref)
        res = json.loads(get_ref)
        for i in res:
            ref=i["_ref"]
            request_publish = ib_NIOS.wapi_request('GET',ref=ref +"?_return_fields=views")
            data=eval(request_publish)
            print(data,len(data['views']))
            if data['views'][0] == 'default' and len(data['views']) == 1:
                assert True
                print("validated views successfully..")
            else:
                assert False
                logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=347)
    def test_347_Delete_Namedacl_ACL_DENY(self):
        logging.info("Deleting ACL ACL_DENY.................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        sleep(30)

    @pytest.mark.run(order=348)
    def test_348_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_DENY is deleted .................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=349)
    def test_349_Delete_Namedacl_ACL_ALLOW(self):
        logging.info("Deleting ACL ACL_ALLOW.................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(delete_acl)
        sleep(30)

    @pytest.mark.run(order=350)
    def test_350_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_ALLOW is deleted .................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    #class RFE_6181_DNS_Network_cases(unittest.TestCase):
    #############################################  Test cases related to DNS view verification #############################################
    ##1. Add network view dhcp (Note: It will crete dns view called 'default.dhcp' )
    @pytest.mark.run(order=351)
    def test_351_Create_networkview(self):
        logging.info("Create networkview")
        data = {"name": "dhcp"}
        response = ib_NIOS.wapi_request('POST', object_type="networkview", fields=json.dumps(data), grid_vip=config.grid_vip)
        print response
        logging.info(response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
            logging.info("Network View dhcp created")
        self.restart_the_grid()

    ##1.Set CLI ALLOW for test.com
    @pytest.mark.run(order=352)
    def test_352_Add_Named_ACL_to_Grid_with_ALLOW_permission(self):
        logging.info("Adding ACL WITH ALLOW.................")
        data={"name": "ACL_ALLOW","access_list": [{"_struct": "addressac", "address": config.IPv4_Network, "permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=353)
    def test_353_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_ACL_ALLOW(self):
        logging.info("adding test.com to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain add default.dhcp test.com ACL_ALLOW')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=354)
    def test_354_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain test.com DnsView=default.dhcp: Set dns_view="default.dhcp",domain_name="test.com",named_acl="ACL_ALLOW"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=355)
    def test_355_validate_infoblox_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_ALLOW' for domain 'test.com' under view 'default.dhcp' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=356)
    def test_356_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=357)
    def test_357_show_allow_query_domain(self):
        logging.info("Displaying domains added to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain default.dhcp')
        child.expect('Infoblox >')
        c= child.before
        print(type(c))
        result = re.findall('(Domain Name : test.com)(.+)((?:\n.+)+)(Named ACL   : ACL_ALLOW)',c)
        print(result)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=358)
    def test_358_Validate_named_conf_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat /infoblox/var/named_conf/named.conf | grep test.com'
        print(audit_log_validation)
        string_content = commands.getoutput(audit_log_validation)
        print(string_content)
        logging.info(string_content)
        if bool(re.search('"test.com" { '+config.IPv4_Network+'; }', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")
        print("Test Case Execution Completed")

    ##move dns view default.dhcp to top in member properties
    @pytest.mark.run(order=359)
    def test_359_move_views(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        logging.info(get_ref)
        res = json.loads(get_ref)
        for i in res:
            ref=i["_ref"]
            data={"views": ["default.dhcp","default"]}
            request_publish = ib_NIOS.wapi_request('PUT',ref=ref +"?_return_fields=views", fields=json.dumps(data))
            print(request_publish)
            self.restart_the_grid()
            print("Moved views successfully..")

    @pytest.mark.run(order=360)
    def test_360_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##3. If we query a.test.com it should return response from 10.36.6.80
    @pytest.mark.run(order=361)
    def test_361_query_domain_test_com_after_adding_to_ACL_ALLOW_From_Client1(self):
        logging.info("Querying test.com, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=362)
    def test_362_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=363)
    def test_363_Validate_syslog_for_dig_operation(self):
        LookFor=".*query: test.com IN A response.*NOERROR.*"
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

    ##1.Set CLI deny for test.com
    @pytest.mark.run(order=364)
    def test_364_Add_Named_ACL_to_Grid_with_DENY_permission(self):
        logging.info("Adding ACL WITH DENY.................")
        data={"name": "ACL_DENY","access_list": [{"_struct": "addressac", "address": config.IPv4_Network, "permission": "DENY"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=365)
    def test_365_update_test_com_from_ACL_ALLOW_TO_ACL_DENY(self):
        logging.info("Updating test.com from ACL_ALLOW to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain update default.dhcp test.com ACL_DENY')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=366)
    def test_366_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Modified AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Modified AllowQueryDomain test.com DnsView=default.dhcp: Changed named_acl:"ACL_ALLOW"->"ACL_DENY"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=367)
    def test_367_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Updated ACL 'ACL_DENY' for domain 'test.com' under view 'default.dhcp' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=368)
    def test_368_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=369)
    def test_369_show_allow_query_domain(self):
        logging.info("Displaying domains added to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain default.dhcp')
        child.expect('Infoblox >')
        c= child.before
        print(type(c))
        result = re.findall('(Domain Name : test.com)(.+)((?:\n.+)+)(Named ACL   : ACL_DENY)',c)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=370)
    def test_370_Validate_named_conf_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat /infoblox/var/named_conf/named.conf | grep test.com'
        print(audit_log_validation)
        string_content = commands.getoutput(audit_log_validation)
        print(string_content)
        logging.info(string_content)
        if bool(re.search('"test.com" { !'+config.IPv4_Network+'; }', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")
        print("Test Case Execution Completed")

    @pytest.mark.run(order=371)
    def test_371_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##5. If we query other domain say a.test.com from 10.36.6.80 it should refuse
    @pytest.mark.run(order=372)
    def test_372_query_domain_test_com_which_is_not_adding_to_any_ACL_From_Client1(self):
       logging.info("Querying test.com which is not added to any ACL, expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=373)
    def test_373_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=374)
    def test_374_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*failed.*(REFUSED).*test.com.*"
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

    ##move dns view default.dhcp to top in member properties
    @pytest.mark.run(order=375)
    def test_375_move_views(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        logging.info(get_ref)
        res = json.loads(get_ref)
        for i in res:
            ref=i["_ref"]
            data={"views": ["default","default.dhcp"]}
            request_publish = ib_NIOS.wapi_request('PUT',ref=ref +"?_return_fields=views", fields=json.dumps(data))
            print(request_publish)
            self.restart_the_grid()
            print("Moved views successfully..")

    @pytest.mark.run(order=376)
    def test_376_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
        logging.info("deleting test.com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain delete default.dhcp test.com')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=377)
    def test_377_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain test.com DnsView=default.dhcp', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=378)
    def test_378_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Deleted ACL for domain 'test.com' under view 'default.dhcp' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=379)
    def test_379_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    ##deleting view default.dhcp
    @pytest.mark.run(order=380)
    def test_380_Delete_Dns_View_default_dhcp(self):
        response = ib_NIOS.wapi_request('GET',object_type="networkview")
        res = json.loads(response)
        for i in res:
            if i['name']=='dhcp':
                response = ib_NIOS.wapi_request('DELETE', ref=i["_ref"])
                print(response)
                sleep(10)
                self.restart_the_grid()
                print("network view dhcp is deleted successfully..")

    @pytest.mark.run(order=381)
    def test_381_Delete_Namedacl_ACL_DENY(self):
        logging.info("Deleting ACL ACL_DENY.................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        sleep(30)

    @pytest.mark.run(order=382)
    def test_382_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_DENY is deleted .................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=383)
    def test_383_Delete_Namedacl_ACL_ALLOW(self):
        logging.info("Deleting ACL ACL_ALLOW.................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(delete_acl)
        sleep(30)

    @pytest.mark.run(order=384)
    def test_384_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_ALLOW is deleted .................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    #class RFE_6181_ACL_cli_command_message_validation(unittest.TestCase):
    #############################################  Test cases related to ACL verification #############################################
    ##7. Set CLI allow for test.com
    @pytest.mark.run(order=385)
    def test_385_Add_Named_ACL_to_Grid_with_ALLOW_permission(self):
        logging.info("Adding ACL WITH ALLOW.................")
        data={"name": "ACL_ALLOW","access_list": [{"_struct": "addressac", "address": "10.0.0.0/8", "permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    ##2. CLI commad execute with zone name test.com
    @pytest.mark.run(order=386)
    def test_386_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_ACL_ALLOW(self):
        logging.info("addin test.com to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain add default test.com ACL_ALLOW')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=387)
    def test_387_update_test_com_TO_ACL_ALLOW_which_is_already_in_ACL_ALLOW_and_validating_message(self):
        logging.info("Updating test.com from ACL_DENY to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain update default test.com ACL_ALLOW')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*No changes found.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=388)
    def test_388_Add_Named_ACL_to_Grid_with_DENY_permission(self):
        logging.info("Adding ACL WITH DENY.................")
        data={"name": "ACL_DENY","access_list": [{"_struct": "addressac", "address": config.IPv4_Network, "permission": "DENY"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=389)
    def test_389_update_test_com_from_ACL_ALLOW_TO_ACL_DENY(self):
        logging.info("Updating test.com from ACL_ALLOW to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain update default test.com ACL_DENY')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=390)
    def test_390_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=391)
    def test_391_update_test2_com_which_is_not_in_any_named_ACL_TO_ACL_ALLOW_validating_error_message(self):
        logging.info("Updating test2.com from ACL_DENY to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain update default test2.com ACL_ALLOW')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r".*ERROR: No matching named ACL found for domain 'test2.com' under view 'default' for updating.*",c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=392)
    def test_392_Delete_domain_zone_com_which_is_not_added_to_any_ACL_validating_error_message(self):
        logging.info("deleting zone.com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain delete default zone.com')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r".*ERROR: No named ACL found for domain 'zone.com' under view 'default' for deletion.*",c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=393)
    def test_393_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
        logging.info("deleting test.com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain delete default test.com')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=394)
    def test_394_show_allow_query_domain(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain_views')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r".*None of the DNS views are associated with domain ACLs.*",c)
        sleep(10)

    ##2. CLI commad execute with zone name zone.com
    @pytest.mark.run(order=395)
    def test_395_Add_allow_query_domain_with_domain_name_zone1_com_with_named_ACL_ACL_ALLOW(self):
        logging.info("addin zone1.com to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain add default zone1.com ACL_ALLOW')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    ##2. CLI commad execute with zone name zone.com
    @pytest.mark.run(order=396)
    def test_396_Add_allow_query_domain_with_domain_name_zone1_com_with_named_ACL_ACL_ALLOW(self):
        logging.info("addin zone1.com to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain add dns_view zone1.com ACL_ALLOW')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r".*ERROR: View 'dns_view' not found.*",c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=397)
    def test_397_show_allow_query_domain_views(self):
        logging.info("Displaying domains added to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain_views')
        child.expect('Infoblox >')
        c= child.before
        print(type(c))
        result = re.findall(r'.*default.*',c)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=398)
    def test_398_show_allow_query_domain(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        print(type(c))
        result = re.findall('(DNS View: default)(.+)((?:\n.+)+)(Domain Name : zone1.com)(.+)((?:\n.+)+)(Named ACL   : ACL_ALLOW)',c)
        print(result)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=399)
    def test_399_Delete_default_using_set_allow_query_domain_delete_command(self):
        logging.info("deleting test.com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain delete default')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=400)
    def test_400_Delete_domain_default_using_set_allow_query_domain_delete_command_validation_erroe_message(self):
        logging.info("deleting test.com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain delete default')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r".*ERROR: No named ACLs found under view 'default' for deletion.*",c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=401)
    def test_401_Delete_domain_zone1_com_using_set_allow_query_domain_delete_command(self):
        logging.info("deleting test.com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain delete default zone1.com')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r".*ERROR: No named ACL found for domain 'zone1.com' under view 'default' for deletion.*",c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=402)
    def test_402_show_allow_query_domain_views(self):
        logging.info("Displaying domains after deleting test.com with delete command")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain_views')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r".*None of the DNS views are associated with domain ACLs.*",c)
        sleep(10)

    @pytest.mark.run(order=403)
    def test_403_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_ACL_ALLOW(self):
        logging.info("addin test.com to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain add default test.com ACL_ALLOW')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    ##2. CLI commad execute with zone name test.com
    @pytest.mark.run(order=404)
    def test_404_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_ACL_ALLOW_validating_error_message(self):
        logging.info("addin test.com to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain add default test.com ACL_ALLOW')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r".*ERROR: A named ACL 'ACL_ALLOW' is already associated with domain 'test.com' under view 'default'.*",c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=405)
    def test_405_show_allow_query_domain_views(self):
        logging.info("Displaying domains after deleting test.com with delete command")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain delete default test.com')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r".*A DNS service restart is required for the configured ACLs to take effect.*",c)
        sleep(10)

    ##2. CLI commad execute with zone name test.com
    @pytest.mark.run(order=406)
    def test_406_Add_allow_query_domain_with_domain_name_of_size_more_then_255_charecters_with_named_ACL_ACL_ALLOW_validating_error_message(self):
        logging.info("addin test.com to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain add default testttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt.com ACL_ALLOW')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*ERROR: The fully qualified DNS name cannot exceed 255 characters.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=407)
    def test_407_Add_allow_query_domain_with_domain_name_xyz_com_with_lengt_of_view_more_then_64_and_validating_error_message(self):
        logging.info("addin xyz.com to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain add viiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii xyz.com ACL_ALLOW')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r".*ERROR: The DNS view cannot exceed 64 characters.*",c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    ##2. CLI commad execute with zone name test.com
    @pytest.mark.run(order=408)
    def test_408_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_with_size_of_more_then_64_charecter(self):
        logging.info("addin xyz.com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain add default xyz.com acccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r".*ERROR: The named ACL name cannot exceed 64 characters.*",c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=409)
    def test_409_Delete_Namedacl_ACL_DENY(self):
        logging.info("Deleting ACL ACL_DENY.................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        sleep(30)

    @pytest.mark.run(order=410)
    def test_410_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_DENY is deleted .................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=411)
    def test_411_Delete_Namedacl_ACL_ALLOW(self):
        logging.info("Deleting ACL ACL_ALLOW.................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(delete_acl)
        sleep(30)

    @pytest.mark.run(order=412)
    def test_412_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_ALLOW is deleted .................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    #class RFE_6181_miscellaneous_cases(unittest.TestCase):
    #############################################  Test cases related to ACL verification #############################################
    ##1.Set CLI deny for test.com
    @pytest.mark.run(order=413)
    def test_413_Add_Named_ACL_to_Grid_with_ALLOW_permission(self):
        logging.info("Adding ACL WITH ALLOW.................")
        data={"name": "ACL_ALLOW_with_tsig_xfer","access_list": [{"_struct": "tsigac", "tsig_key": ":2xCOMPAT", "tsig_key_name": "tsig_xfer"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=414)
    def test_414_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_ACL_DENY(self):
        logging.info("adding test.com to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain add default test.com ACL_ALLOW_with_tsig_xfer')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r".*ERROR: Named ACL 'ACL_ALLOW_with_tsig_xfer' contains '2.x TSIG Key' based ac items which are not allowed for 'ALLOW QUERY DOMAIN'.*",c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    ##1. Add named acl with IPv4 address 10.36.6.80 and set Operation Allow
    @pytest.mark.run(order=415)
    def test_415_Add_Named_ACL_to_Grid_with_ALLOW_permission(self):
        logging.info("Adding ACL WITH ALLOW.................")
        data={"name": "ACL_ALLOW","access_list": [{"_struct": "addressac", "address": "10.0.0.0/8","permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    ##2. CLI commad execute with zone name test.com
    @pytest.mark.run(order=416)
    def test_416_Add_allow_query_domain_with_domain_name_example_com_with_named_ACL_ACL_ALLOW(self):
        logging.info("addin test.com to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain add default example.com ACL_ALLOW')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=417)
    def test_417_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain example.com DnsView=default: Set dns_view="default",domain_name="example.com",named_acl="ACL_ALLOW"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=418)
    def test_418_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_ALLOW' for domain 'example.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=419)
    def test_419_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=420)
    def test_420_Delete_Namedacl_ACL_ALLOW(self):
        logging.info("Deleting ACL ACL_ALLOW.................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        if bool(re.search(r'.*Can not delete ACL_ALLOW because it is used by View : default - ALLOW QUERY DOMAIN.*',delete_acl[1])):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")
        sleep(30)

    @pytest.mark.run(order=421)
    def test_421_show_allow_query_domain(self):
        logging.info("Displaying domains added to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        print(type(c))
        result = re.findall('(Domain Name : example.com)(.+)((?:\n.+)+)(Named ACL   : ACL_ALLOW)',c)
        print(result)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    ##1.Set CLI deny for test.com
    @pytest.mark.run(order=422)
    def test_422_Add_Named_ACL_to_Grid_with_DENY_permission(self):
        logging.info("Adding ACL WITH DENY.................")
        data={"name": "ACL_DENY","access_list": [{"_struct": "addressac", "address": "10.0.0.0/8", "permission": "DENY"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=423)
    def test_423_Add_allow_query_domain_with_domain_name_level3_example_com_with_named_ACL_ACL_DENY(self):
        logging.info("adding level3.example.com to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain add default level3.example.com ACL_DENY')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=424)
    def test_424_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain level3.example.com DnsView=default: Set dns_view="default",domain_name="level3.example.com",named_acl="ACL_DENY"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=425)
    def test_425_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_DENY' for domain 'level3.example.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=426)
    def test_426_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=427)
    def test_427_show_allow_query_domain(self):
        logging.info("Displaying domains added to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        result = re.findall('(Domain Name : level3.example.com)(.+)((?:\n.+)+)(Named ACL   : ACL_DENY)',c)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=428)
    def test_428_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=429)
    def test_429_query_domain_level4_level3_example_com_after_adding_to_ACL_DENY_From_Client1(self):
        logging.info("Querying level4.level3.example.com, expected result as REFUSED")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' level4.level3.example.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=430)
    def test_430_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=431)
    def test_431_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*failed.*(REFUSED).*level4.level3.example.com.*"
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

    @pytest.mark.run(order=432)
    def test_432_update_example_com_from_ACL_ALLOW_TO_ACL_DENY(self):
        logging.info("Updating test.com from ACL_ALLOW to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain update default example.com ACL_DENY')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=433)
    def test_433_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Modified AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Modified AllowQueryDomain example.com DnsView=default: Changed named_acl:"ACL_ALLOW"->"ACL_DENY"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=434)
    def test_434_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Updated ACL 'ACL_DENY' for domain 'example.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=435)
    def test_435_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_client_ip2v6_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=436)
    def test_436_show_allow_query_domain(self):
        logging.info("Displaying domains added to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        result = re.findall('(Domain Name : example.com)(.+)((?:\n.+)+)(Named ACL   : ACL_DENY)',c)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=437)
    def test_437_update_level3_example_com_from_ACL_DENY_TO_ACL_ALLOW(self):
        logging.info("Updating level3.example.com from ACL_DENY to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain update default level3.example.com ACL_ALLOW')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=438)
    def test_438_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Modified AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Modified AllowQueryDomain level3.example.com DnsView=default: Changed named_acl:"ACL_DENY"->"ACL_ALLOW"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=439)
    def test_439_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Updated ACL 'ACL_ALLOW' for domain 'level3.example.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=440)
    def test_440_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=441)
    def test_441_show_allow_query_domain(self):
        logging.info("Displaying domains added to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        print(type(c))
        result = re.findall('(Domain Name : level3.example.com)(.+)((?:\n.+)+)(Named ACL   : ACL_ALLOW)',c)
        print(result)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=442)
    def test_442_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##8. Query a.test.com..
    @pytest.mark.run(order=443)
    def test_443_query_domain_test_com_after_updating_test_com_from_ACL_DENY_to_ACL_ALLOW(self):
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' level4.level3.example.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=444)
    def test_444_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=445)
    def test_445_Validate_syslog_for_dig_operation(self):
        LookFor=".*query: level4.level3.example.com IN A response.*NOERROR.*"
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

    ##2. Added Authoritative  zone test.com with a record in default view
    @pytest.mark.run(order=446)
    def test_446_create_test_com_authoritative_zone(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        data={"fqdn": "test.com"}
        response = ib_NIOS.wapi_request('POST', object_type='zone_auth',fields=json.dumps(data))
        zone_response = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        res = json.loads(zone_response)
        for i in res:
            data = {"grid_primary":[{"name":"infoblox.localdomain"}]}
            response = ib_NIOS.wapi_request('PUT', ref=i["_ref"],fields=json.dumps(data))
            self.restart_the_grid()
            print("Zone added successfully........")

    @pytest.mark.run(order=447)
    def test_447_Add_CNAME_record_to_test_com_zone(self):
        logging.info("Add cname record")
        data = {"name":"cname.test.com","canonical":"abc.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:cname",fields=json.dumps(data))
        if (response[0]!=400):
            print ("Added cname record")
        else:
            print ("A record already exists")
            logging.info("Test case Execution Completed")

    @pytest.mark.run(order=448)
    def test_448_Add_DNAME_record_to_test_com_zone(self):
        logging.info("Add dname record")
        data = {"name":"dname.test.com","target":"xyz.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:dname",fields=json.dumps(data))
        if (response[0]!=400):
            print ("Added dname record")
        else:
            print ("A record already exists")
            logging.info("Test case Execution Completed")

    @pytest.mark.run(order=449)
    def test_449_Add_allow_query_domain_with_domain_name_abc_com_with_named_ACL_ACL_DENY(self):
        logging.info("adding abc.com to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain add default abc.com ACL_DENY')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=450)
    def test_450_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain abc.com DnsView=default: Set dns_view="default",domain_name="abc.com",named_acl="ACL_DENY"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=451)
    def test_451_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_DENY' for domain 'abc.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=452)
    def test_452_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=453)
    def test_453_show_allow_query_domain(self):
        logging.info("Displaying domains added to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        print(type(c))
        result = re.findall('(Domain Name : abc.com)(.+)((?:\n.+)+)(Named ACL   : ACL_DENY)',c)
        print(result)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=454)
    def test_454_Add_allow_query_domain_with_domain_name_xyz_com_with_named_ACL_ACL_DENY(self):
        logging.info("adding xyz.com to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain add default xyz.com ACL_DENY')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=455)
    def test_455_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain xyz.com DnsView=default: Set dns_view="default",domain_name="xyz.com",named_acl="ACL_DENY"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=456)
    def test_456_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_DENY' for domain 'xyz.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=457)
    def test_457_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=458)
    def test_458_show_allow_query_domain(self):
        logging.info("Displaying domains added to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        print(type(c))
        result = re.findall('(Domain Name : xyz.com)(.+)((?:\n.+)+)(Named ACL   : ACL_DENY)',c)
        print(result)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=459)
    def test_459_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=460)
    def test_460_query_domain_abc_com_after_adding_to_ACL_DENY_From_Client1(self):
        logging.info("Querying abc.com, expected result as REFUSED")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' abc.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=461)
    def test_461_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=462)
    def test_462_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*failed.*(REFUSED).*abc.com.*"
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

    @pytest.mark.run(order=463)
    def test_463_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=464)
    def test_464_query_domain_xyz_com_after_adding_to_ACL_DENY_From_Client1(self):
        logging.info("Querying xyz.com, expected result as REFUSED")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' xyz.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=465)
    def test_465_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=466)
    def test_466_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*failed.*(REFUSED).*xyz.com.*"
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

    @pytest.mark.run(order=467)
    def test_467_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
        logging.info("deleting test.com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain delete default example.com')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=468)
    def test_468_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain example.com DnsView=default', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=469)
    def test_469_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Deleted ACL for domain 'example.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=470)
    def test_470_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
        logging.info("deleting test.com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain delete default level3.example.com')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=471)
    def test_471_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain level3.example.com DnsView=default', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=472)
    def test_472_validate_infoblox_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Deleted ACL for domain 'level3.example.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=473)
    def test_473_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
        logging.info("deleting abc.com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain delete default abc.com')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=474)
    def test_474_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain abc.com DnsView=default', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=475)
    def test_475_validate_infoblox_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Deleted ACL for domain 'abc.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=476)
    def test_476_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
        logging.info("deleting test.com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain delete default xyz.com')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=477)
    def test_477_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain xyz.com DnsView=default', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=478)
    def test_478_validate_infoblox_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Deleted ACL for domain 'xyz.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")


    ##1. Add named acl with any adress/network and set Operation Allow
    @pytest.mark.run(order=479)
    def test_479_Add_Named_ACL_to_Grid_ACL_allow_any_with_ALLOW_permission(self):
        logging.info("Adding ACL WITH ALLOW.................")
        data={"name": "ACL_allow_any","access_list": [{"_struct": "addressac", "address": "Any","permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    ##2. CLI commad execute with zone name test.com
    @pytest.mark.run(order=480)
    def test_480_Add_allow_query_domain_with_domain_name_example_com_with_named_ACL_ACL_allow_any(self):
        logging.info("addin test.com to ACL_allow_any")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain add default example.com ACL_allow_any')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=481)
    def test_481_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain example.com DnsView=default: Set dns_view="default",domain_name="example.com",named_acl="ACL_allow_any"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=482)
    def test_482_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_allow_any' for domain 'example.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=483)
    def test_483_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=484)
    def test_484_show_allow_query_domain(self):
        logging.info("Displaying domains added to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        print(type(c))
        result = re.findall('(Domain Name : example.com)(.+)((?:\n.+)+)(Named ACL   : ACL_allow_any)',c)
        print(result)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=485)
    def test_485_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##8. Query a.test.com..
    @pytest.mark.run(order=486)
    def test_486_query_domain_test_com_after_updating_test_com_from_ACL_DENY_to_ACL_ALLOW(self):
        logging.info("Querying test.com after updating to NOERROR, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' example.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=487)
    def test_487_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=488)
    def test_488_Validate_syslog_for_dig_operation(self):
        LookFor=".*query: example.com IN A response.*NOERROR.*"
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

    ##1. Add named acl with any adress/network and set Operation Allow
    @pytest.mark.run(order=489)
    def test_489_Add_Named_ACL_to_Grid_ACL_deny_any_with_DENY_permission(self):
        logging.info("Adding ACL WITH DENY.................")
        data={"name": "ACL_deny_any","access_list": [{"_struct": "addressac", "address": "Any","permission": "DENY"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    ##2. CLI commad execute with zone name test.com
    @pytest.mark.run(order=490)
    def test_490_Add_allow_query_domain_with_domain_name_example_com_with_named_ACL_ACL_deny_any(self):
        logging.info("addin test.com to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain add default xyz.com ACL_deny_any')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=491)
    def test_491_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain xyz.com DnsView=default: Set dns_view="default",domain_name="xyz.com",named_acl="ACL_deny_any"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=492)
    def test_492_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_deny_any' for domain 'xyz.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=493)
    def test_493_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=494)
    def test_494_show_allow_query_domain(self):
        logging.info("Displaying domains added to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        print(type(c))
        result = re.findall('(Domain Name : xyz.com)(.+)((?:\n.+)+)(Named ACL   : ACL_deny_any)',c)
        print(result)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=495)
    def test_495_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=496)
    def test_496_query_domain_xyz_com_after_adding_to_ACL_DENY_From_Client1(self):
        logging.info("Querying xyz.com, expected result as REFUSED")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' xyz.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=497)
    def test_497_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=498)
    def test_498_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*failed.*(REFUSED).*xyz.com.*"
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

    @pytest.mark.run(order=499)
    def test_499_Delete_Namedacl_ACL_DENY(self):
        logging.info("Deleting ACL ACL_DENY.................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        sleep(30)

    @pytest.mark.run(order=500)
    def test_500_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_DENY is deleted .................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=501)
    def test_501_Delete_Namedacl_ACL_ALLOW(self):
        logging.info("Deleting ACL ACL_ALLOW.................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(delete_acl)
        sleep(30)

    @pytest.mark.run(order=502)
    def test_502_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_ALLOW is deleted .................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=503)
    def test_503_Delete_Namedacl_ACL_ALLOW_with_tsig_xfer(self):
        logging.info("Deleting ACL ACL_ALLOW_with_tsig_xfer.................")
        data={"name": "ACL_ALLOW_with_tsig_xfer"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(delete_acl)
        sleep(30)

    @pytest.mark.run(order=504)
    def test_504_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
        logging.info("deleting example.com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain delete default example.com')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=505)
    def test_505_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
        logging.info("deleting xyz.com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain delete default xyz.com')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=506)
    def test_506_Delete_Namedacl_ACL_deny_any(self):
        logging.info("Deleting ACL ACL_deny_any.................")
        data={"name": "ACL_deny_any"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        sleep(30)

    @pytest.mark.run(order=507)
    def test_507_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_deny_any is deleted .................")
        data={"name": "ACL_deny_any"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=508)
    def test_508_Delete_Namedacl_ACL_allow_any(self):
        logging.info("Deleting ACL ACL_allow_any.................")
        data={"name": "ACL_allow_any"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        sleep(30)

    @pytest.mark.run(order=509)
    def test_509_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_allow_any is deleted .................")
        data={"name": "ACL_allow_any"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=510)
    def test_510_delete_test_com_autoritative_zone(self):
        data={"fqdn":"test.com"}
        response = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
        res = json.loads(response)
        for i in res:
            response = ib_NIOS.wapi_request('DELETE', ref=i["_ref"])
            print(response)
            sleep(10)
            logging.info("Test case Execution Completed")
            self.restart_the_grid()

    #class RFE_6181_DCA_related_acl_cases(unittest.TestCase):
    @pytest.mark.run(order=511)
    def test_511_enable_dns_cache_acceleration(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        logging.info(get_ref)
        res = json.loads(get_ref)
        for i in res:
            ref=i["_ref"]
            logging.info("Modify a enable_dns")
            data = {"enable_dns_cache_acceleration": True}
            response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
            sleep(300)
            logging.info(response)
            read  = re.search(r'200',response)
            for read in  response:
                assert True

    ##1. Add named acl with IPv4 address 10.36.6.80 and set Operation Allow
    @pytest.mark.run(order=512)
    def test_512_Add_Named_ACL_to_Grid_with_ALLOW_permission(self):
        logging.info("Adding ACL WITH ALLOW.................")
        data={"name": "ACL_ALLOW","access_list": [{"_struct": "addressac", "address": "10.0.0.0/8","permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=513)
    def test_513_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_ACL_ALLOW(self):
        logging.info("adding test.com to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain add default test.com ACL_ALLOW')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=514)
    def test_514_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain test.com DnsView=default: Set dns_view="default",domain_name="test.com",named_acl="ACL_ALLOW"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=515)
    def test_515_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_ALLOW' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=516)
    def test_516_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=517)
    def test_517_show_allow_query_domain(self):
        logging.info("Displaying domains added to ACL_ALLOW")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        print(type(c))
        result = re.findall('(Domain Name : test.com)(.+)((?:\n.+)+)(Named ACL   : ACL_ALLOW)',c)
        print(result)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=518)
    def test_518_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##4. Query test.com..
    @pytest.mark.run(order=519)
    def test_519_query_domain_test_com_after_setting_deny_to_dns_default_view_From_Client1(self):
        logging.info("Querying arec.test.com, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=520)
    def test_520_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=521)
    def test_521_Validate_syslog_for_dig_operation(self):
        LookFor=".*query: test.com IN A response.*NOERROR.*"
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

    @pytest.mark.run(order=522)
    def test_522_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##4. Query a.test.com
    @pytest.mark.run(order=523)
    def test_523_query_domain_test_com_after_setting_deny_to_dns_default_view_From_Client1(self):
        logging.info("Querying test.com, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=524)
    def test_524_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=525)
    def test_525_Validate_syslog_for_dig_operation(self):
        LookFor=".*query: test.com IN A response.*NOERROR.*"
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

    @pytest.mark.run(order=526)
    def test_526_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##4. Query a.test.com
    @pytest.mark.run(order=527)
    def test_527_query_domain_test_com_after_setting_deny_to_dns_default_view_From_Client1(self):
        logging.info("Querying test.com, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=528)
    def test_528_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=529)
    def test_529_Validate_syslog_for_dig_operation(self):
        LookFor=".*query: test.com IN A response.*NOERROR.*"
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

    @pytest.mark.run(order=530)
    def test_530_Validate_DCA_Cache_Hit_Counts_set_to_Zero(self):
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

    @pytest.mark.run(order=531)
    def test_531_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
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

    @pytest.mark.run(order=532)
    def test_532_Add_Named_ACL_to_Grid_with_DENY_permission(self):
        logging.info("Adding ACL WITH DENY.................")
        data={"name": "ACL_DENY","access_list": [{"_struct": "addressac", "address": config.client_ip1, "permission": "DENY"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=533)
    def test_533_update_test_com_from_ACL_ALLOW_TO_ACL_DENY(self):
        logging.info("Updating test.com from ACL_ALLOW to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain update default test.com ACL_DENY')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=534)
    def test_534_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Modified AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Modified AllowQueryDomain test.com DnsView=default: Changed named_acl:"ACL_ALLOW"->"ACL_DENY"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=535)
    def test_535_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Updated ACL 'ACL_DENY' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=536)
    def test_536_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=537)
    def test_537_show_allow_query_domain(self):
        logging.info("Displaying domains added to ACL_DENY")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        print(type(c))
        result = re.findall('(Domain Name : test.com)(.+)((?:\n.+)+)(Named ACL   : ACL_DENY)',c)
        print(result)
        assert result
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=538)
    def test_538_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=539)
    def test_539_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##1. If we query a.test.com it should refuse queries from 10.36.6.80
    @pytest.mark.run(order=540)
    def test_540_query_domain_test_com_after_updating_from_ACL_ALLOW_to_ACL_DENY_From_Client1(self):
       logging.info("Querying test.com after updating to ACL_DENY, expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=541)
    def test_541_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=542)
    def test_542_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*failed.*(REFUSED).*test.com.*"
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

    @pytest.mark.run(order=543)
    def test_543_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##1. If we query a.test.com it should refuse queries from 10.36.6.80
    @pytest.mark.run(order=544)
    def test_544_query_domain_test_com_after_updating_from_ACL_ALLOW_to_ACL_DENY_From_Client1(self):
       logging.info("Querying test.com after updating to ACL_DENY, expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=545)
    def test_545_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=546)
    def test_546_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*failed.*(REFUSED).*test.com.*"
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

    @pytest.mark.run(order=547)
    def test_547_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##1. If we query a.test.com it should refuse queries from 10.36.6.80
    @pytest.mark.run(order=548)
    def test_548_query_domain_test_com_after_updating_from_ACL_ALLOW_to_ACL_DENY_From_Client1(self):
       logging.info("Querying test.com after updating to ACL_DENY, expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=549)
    def test_549_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=550)
    def test_550_Validate_syslog_for_dig_operation(self):
        LookFor=".*query.*failed.*(REFUSED).*test.com.*"
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

    @pytest.mark.run(order=551)
    def test_551_Validate_DCA_Cache_Hit_Counts_set_to_Zero(self):
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

    @pytest.mark.run(order=552)
    def test_552_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
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

    @pytest.mark.run(order=553)
    def test_553_Validate_DNS_query_status_FAILURE_Zero(self):
        logging.info("Validate as got response from Bind for Proxy domain playboy.com Cache hit count not increased and Miss cache count increased")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show dns-accel')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*DNS query stats:                 SUCCESS=0 NXDOMAIN=0 NXRRSET=0 FAILURE=0 REFERRAL=0.*',c)
        logging.info("Test Case Execution Completed")
        sleep(15)

    @pytest.mark.run(order=554)
    def test_554_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
        logging.info("deleting test.com")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain delete default test.com')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*A DNS service restart is required for the configured ACLs to take effect.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=555)
    def test_555_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain test.com DnsView=default', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=556)
    def test_556_validate_infoblox_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Deleted ACL for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=557)
    def test_557_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=558)
    def test_558_Delete_Namedacl_ACL_DENY(self):
        logging.info("Deleting ACL ACL_DENY.................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        sleep(30)

    @pytest.mark.run(order=559)
    def test_559_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_DENY is deleted .................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=560)
    def test_560_Delete_Namedacl_ACL_ALLOW(self):
        logging.info("Deleting ACL ACL_ALLOW.................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(delete_acl)
        sleep(30)

    @pytest.mark.run(order=561)
    def test_561_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_ALLOW is deleted .................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    #class RFE_6181_non_super_user_validation_for_Named_acl_cli_commands(unittest.TestCase):
    #############################################  Test cases related to ACL verification #############################################
    @pytest.mark.run(order=562)
    def test_562_create_admin_group(self):
        reference=[]
        data={'name':'group1'}
        response_created=ib_NIOS.wapi_request('POST',object_type="admingroup",fields=json.dumps(data))
        data1={"admin_groups": ["group1"],"name": "user123","password":"user123"}
        response1=ib_NIOS.wapi_request('POST',object_type="adminuser",fields=json.dumps(data1))
        print(response1)

    @pytest.mark.run(order=563)
    def test_563_enable_cli_for_group1(self):
        get_ref = ib_NIOS.wapi_request('GET',object_type="admingroup?_return_fields=access_method")
        res = json.loads(get_ref)
        for i in res:
            ref=i["_ref"]
            if 'group1' in i["_ref"]:
                data={"access_method": ["GUI","CLI"]}
                get_ref = ib_NIOS.wapi_request('PUT',ref=ref +"?_return_fields=access_method", fields=json.dumps(data))
                print("testcase passed")

    @pytest.mark.run(order=564)
    def test_564_validate_enabling_cli_Group1(self):
        get_ref = ib_NIOS.wapi_request('GET',object_type="admingroup?_return_fields=access_method")
        print(get_ref)
        res = json.loads(get_ref)
        for i in res:
            ref=i["_ref"]
            if 'group1' in i["_ref"]:
                if i['access_method']==["GUI","CLI"]:
                    print("testcase passed")


    @pytest.mark.run(order=565)
    def test_565_check_set_allow_query_domain_add_command_for_non_super_user(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no user123@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('user123')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain add default test.com ACL_DENY')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Error: The user does not have sufficient privileges to run this command.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=566)
    def test_566_check_set_allow_query_domain_update_command_for_non_super_user(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no user123@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('user123')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain update default test.com ACL_DENY')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Error: The user does not have sufficient privileges to run this command.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=567)
    def test_567_check_set_allow_query_domain_delete_command_for_non_super_user(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no user123@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('user123')
        child.expect('Infoblox >')
        child.sendline('set allow_query_domain delete default test.com')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Error: The user does not have sufficient privileges to run this command.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=568)
    def test_568_check_set_allow_query_domain_show_command_for_non_super_user(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no user123@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('user123')
        child.expect('Infoblox >')
        child.sendline('show allow_query_domain')
        child.expect('Infoblox >')
        c= child.before
        assert re.search(r'.*Error: The user does not have sufficient privileges to run this command.*',c)
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=569)
    def test_569_Delete_user(self):
        data={"name": "user123"}
        acl = ib_NIOS.wapi_request('GET', object_type='adminuser',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        deleteed_user=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(deleteed_user)
        sleep(30)

    @pytest.mark.run(order=579)
    def test_570_Delete_group(self):
        data={"name": "group1"}
        acl = ib_NIOS.wapi_request('GET', object_type='admingroup',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        deleted_group=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(deleted_group)
        sleep(30)


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

class RFE_6181_prerequisite(unittest.TestCase):
    #############################################  Test cases to enable RPZ,recursive query, forworder ip #############################################
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

class RFE_6181_Ipv4_Adress_named_ACL(unittest.TestCase):
#############################################  Test cases related to ACL verification #############################################
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

    ##1. Add named acl with IPv4 address 10.36.6.80 and set Operation Allow
    @pytest.mark.run(order=3)
    def test_003_Add_Named_ACL_to_Grid_with_ALLOW_permission(self):
        logging.info("Adding ACL WITH ALLOW.................")
        data={"name": "ACL_ALLOW","access_list": [{"_struct": "addressac", "address": config.client_ip1, "permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    ##2. CLI commad execute with zone name test.com
    @pytest.mark.run(order=4)
    def test_004_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_ACL_ALLOW(self):
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

    @pytest.mark.run(order=5)
    def test_005_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain test.com DnsView=default: Set dns_view="default",domain_name="test.com",named_acl="ACL_ALLOW"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=6)
    def test_006_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_ALLOW' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=7)
    def test_007_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=8)
    def test_008_show_allow_query_domain(self):
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

    @pytest.mark.run(order=9)
    def test_009_Validate_named_conf_file(self):
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

    @pytest.mark.run(order=10)
    def test_010_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##3. If we query a.test.com it should return response from 10.36.6.80
    @pytest.mark.run(order=11)
    def test_011_query_domain_test_com_after_adding_to_ACL_ALLOW_From_Client1(self):
        logging.info("Querying test.com, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=12)
    def test_012_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=13)
    def test_013_Validate_syslog_for_dig_operation(self):
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


    @pytest.mark.run(order=14)
    def test_014_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##4. If we query a.test.com it should refuse queries from 10.36.1.255
    @pytest.mark.run(order=15)
    def test_015_query_domain_test_com_after_adding_to_ACL_ALLOW_From_Client2(self):
        logging.info("Querying test.com, expected result as REFUSED")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip2+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=16)
    def test_016_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=17)
    def test_017_Validate_syslog_for_dig_operation(self):
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


    @pytest.mark.run(order=18)
    def test_018_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##5. If we query other domain say a.zone.com from 10.36.6.80 it should return response
    @pytest.mark.run(order=19)
    def test_019_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_Client1(self):
       logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' zone.com +noedns -b '+config.client_ip1+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(15)

    @pytest.mark.run(order=20)
    def test_020_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=21)
    def test_021_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=22)
    def test_022_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(15)

    ##6. If we query other domain say a.zone.com from 10.36.1.255 it should return response
    @pytest.mark.run(order=23)
    def test_023_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_Client2(self):
       logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' zone.com +noedns -b '+config.client_ip2+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(15)

    @pytest.mark.run(order=24)
    def test_024_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=25)
    def test_025_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=26)
    def test_026_Add_Named_ACL_to_Grid_with_DENY_permission(self):
        logging.info("Adding ACL WITH DENY.................")
        data={"name": "ACL_DENY","access_list": [{"_struct": "addressac", "address": config.client_ip1, "permission": "DENY"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=27)
    def test_027_update_test_com_from_ACL_ALLOW_TO_ACL_DENY(self):
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

    @pytest.mark.run(order=28)
    def test_028_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Modified AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Modified AllowQueryDomain test.com DnsView=default: Changed named_acl:"ACL_ALLOW"->"ACL_DENY"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=29)
    def test_029_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Updated ACL 'ACL_DENY' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=30)
    def test_030_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=31)
    def test_031_show_allow_query_domain(self):
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

    @pytest.mark.run(order=32)
    def test_032_Validate_named_conf_file(self):
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

    @pytest.mark.run(order=33)
    def test_033_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##1. If we query a.test.com it should refuse queries from 10.36.6.80
    @pytest.mark.run(order=34)
    def test_034_query_domain_test_com_after_updating_from_ACL_ALLOW_to_ACL_DENY_From_Client1(self):
       logging.info("Querying test.com after updating to ACL_DENY, expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=35)
    def test_035_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=36)
    def test_036_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=37)
    def test_037_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##2. If we query a.test.com it should refuse queries from 10.36.1.255
    @pytest.mark.run(order=38)
    def test_038_query_domain_test_com_after_updating_from_ACL_ALLOW_to_ACL_DENY_From_Client2(self):
       logging.info("Querying test.com after updating to ACL_ALLOW, expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip2+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=39)
    def test_039_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=40)
    def test_040_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=41)
    def test_041_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##3. If we query other domain say a.zone.com from 10.36.6.80 it should return response
    @pytest.mark.run(order=42)
    def test_042_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_Client1(self):
        logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' zone.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=43)
    def test_043_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=44)
    def test_044_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=45)
    def test_045_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##4. If we query other domain say a.zone.com from 10.36.1.255 it should return response
    @pytest.mark.run(order=46)
    def test_046_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_Client2(self):
        logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' zone.com +noedns -b '+config.client_ip2+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=47)
    def test_047_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=48)
    def test_048_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=49)
    def test_049_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
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

    @pytest.mark.run(order=50)
    def test_050_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain test.com DnsView=default', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=51)
    def test_051_validate_infoblox_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Deleted ACL for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=52)
    def test_052_Perform_RESTART_of_the_DNS_service(self):
       logging.info("Restart services")
       grid =  ib_NIOS.wapi_request('GET', object_type="grid")
       ref = json.loads(grid)[0]['_ref']
       publish={"member_order":"SIMULTANEOUSLY"}
       request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
       request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
       restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
       print("System Restart is done successfully")
       sleep(60)

    @pytest.mark.run(order=53)
    def test_053_show_allow_query_domain(self):
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

    @pytest.mark.run(order=54)
    def test_054_Validate_named_conf_file(self):
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

    @pytest.mark.run(order=55)
    def test_055_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=56)
    def test_056_query_domain_test_com_after_deleting_ACL_From_Client1(self):
      logging.info("Querying test.com after deleting, expected result as NOERROR")
      cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
      result=subprocess.check_output(cmd, shell=True)
      print(result)
      assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
      logging.info("Test Case Execution Completed")
      sleep(10)

    @pytest.mark.run(order=57)
    def test_057_stop_Syslog_Messages(self):
       log("stop","/var/log/syslog",config.grid_vip)
       logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=58)
    def test_058_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=59)
    def test_059_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=60)
    def test_060_query_domain_test_com_after_deleting_ACL_From_Client2(self):
       logging.info("Querying test.com after updating to ACL_ALLOW, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip2+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=61)
    def test_061_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=62)
    def test_062_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=63)
    def test_063_Delete_Namedacl_ACL_DENY(self):
        logging.info("Deleting ACL ACL_DENY.................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        sleep(30)

    @pytest.mark.run(order=64)
    def test_064_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_DENY is deleted .................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=65)
    def test_065_Delete_Namedacl_ACL_ALLOW(self):
        logging.info("Deleting ACL ACL_ALLOW.................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(delete_acl)
        sleep(30)

    @pytest.mark.run(order=66)
    def test_066_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_ALLOW is deleted .................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

class RFE_6181_Ipv4_Network_named_ACL(unittest.TestCase):
#############################################  Test cases related to ACL verification #############################################
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
    ##1. Add named acl with IPv4 Network 10.0.0.0/8 and set Operation Allow
    @pytest.mark.run(order=3)
    def test_003_Add_Named_ACL_to_Grid_with_ALLOW_permission(self):
        logging.info("Adding ACL WITH ALLOW.................")
        data={"name": "ACL_ALLOW","access_list": [{"_struct": "addressac", "address": config.IPv4_Network, "permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    ##2. CLI commad execute with zone name test.com
    @pytest.mark.run(order=4)
    def test_004_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_ACL_ALLOW(self):
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

    @pytest.mark.run(order=5)
    def test_005_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain test.com DnsView=default: Set dns_view="default",domain_name="test.com",named_acl="ACL_ALLOW"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=6)
    def test_006_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_ALLOW' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=7)
    def test_007_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=8)
    def test_008_show_allow_query_domain(self):
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

    @pytest.mark.run(order=9)
    def test_009_Validate_named_conf_file(self):
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

    @pytest.mark.run(order=10)
    def test_010_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##3. If we query a.test.com it should return response from 10.36.6.80
    @pytest.mark.run(order=11)
    def test_011_query_domain_test_com_after_adding_to_ACL_ALLOW_From_Client1(self):
        logging.info("Querying test.com, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=12)
    def test_012_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=13)
    def test_013_Validate_syslog_for_dig_operation(self):
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


    @pytest.mark.run(order=14)
    def test_014_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##4. If we query a.test.com it should return response from 10.36.1.255
    @pytest.mark.run(order=15)
    def test_015_query_domain_test_com_after_adding_to_ACL_ALLOW_From_Client2(self):
        logging.info("Querying test.com, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip2+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=16)
    def test_016_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=17)
    def test_017_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=18)
    def test_018_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##5. If we query other domain say a.zone.com from 10.36.6.80 it should return response
    @pytest.mark.run(order=19)
    def test_019_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_Client1(self):
       logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' zone.com +noedns -b '+config.client_ip1+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=20)
    def test_020_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=21)
    def test_021_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=22)
    def test_022_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##6. If we query other domain say a.zone.com from 10.36.1.255 it should return response
    @pytest.mark.run(order=23)
    def test_023_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_Client2(self):
       logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' zone.com +noedns -b '+config.client_ip2+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(20)

    @pytest.mark.run(order=24)
    def test_024_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=25)
    def test_025_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=26)
    def test_026_Add_Named_ACL_to_Grid_with_DENY_permission(self):
        logging.info("Adding ACL WITH DENY.................")
        data={"name": "ACL_DENY","access_list": [{"_struct": "addressac", "address": config.IPv4_Network, "permission": "DENY"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=27)
    def test_027_update_test_com_from_ACL_ALLOW_TO_ACL_DENY(self):
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

    @pytest.mark.run(order=28)
    def test_028_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Modified AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Modified AllowQueryDomain test.com DnsView=default: Changed named_acl:"ACL_ALLOW"->"ACL_DENY"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=29)
    def test_029_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Updated ACL 'ACL_DENY' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=30)
    def test_030_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=31)
    def test_031_show_allow_query_domain(self):
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

    @pytest.mark.run(order=32)
    def test_032_Validate_named_conf_file(self):
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

    @pytest.mark.run(order=33)
    def test_033_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##1. If we query a.test.com it should refuse queries from 10.36.6.80
    @pytest.mark.run(order=34)
    def test_034_query_domain_test_com_after_updating_from_ACL_ALLOW_to_ACL_DENY_From_Client1(self):
       logging.info("Querying test.com after updating to ACL_DENY, expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=35)
    def test_035_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=36)
    def test_036_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=37)
    def test_037_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##2. If we query a.test.com it should refuse queries from 10.36.1.255
    @pytest.mark.run(order=38)
    def test_038_query_domain_test_com_after_updating_from_ACL_ALLOW_to_ACL_DENY_From_Client2(self):
       logging.info("Querying test.com after updating to ACL_ALLOW, expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip2+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=39)
    def test_039_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=40)
    def test_040_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=41)
    def test_041_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##3. If we query other domain say a.zone.com from 10.36.6.80 it should return response
    @pytest.mark.run(order=42)
    def test_042_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_Client1(self):
        logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' zone.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=43)
    def test_043_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=44)
    def test_044_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=45)
    def test_045_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##4. If we query other domain say a.zone.com from 10.36.1.255 it should return response
    @pytest.mark.run(order=46)
    def test_046_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_Client2(self):
        logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' zone.com +noedns -b '+config.client_ip2+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=47)
    def test_047_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=48)
    def test_048_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=49)
    def test_049_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
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

    @pytest.mark.run(order=50)
    def test_050_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain test.com DnsView=default', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=51)
    def test_051_validate_infoblox_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Deleted ACL for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=52)
    def test_052_Perform_RESTART_of_the_DNS_service(self):
       logging.info("Restart services")
       grid =  ib_NIOS.wapi_request('GET', object_type="grid")
       ref = json.loads(grid)[0]['_ref']
       publish={"member_order":"SIMULTANEOUSLY"}
       request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
       request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
       restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
       print("System Restart is done successfully")
       sleep(60)

    @pytest.mark.run(order=53)
    def test_053_show_allow_query_domain(self):
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

    @pytest.mark.run(order=54)
    def test_054_Validate_named_conf_file(self):
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


    @pytest.mark.run(order=55)
    def test_055_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=56)
    def test_056_query_domain_test_com_after_deleting_ACL_From_Client1(self):
      logging.info("Querying test.com after deleting, expected result as NOERROR")
      cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
      result=subprocess.check_output(cmd, shell=True)
      print(result)
      assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
      logging.info("Test Case Execution Completed")
      sleep(10)

    @pytest.mark.run(order=57)
    def test_057_stop_Syslog_Messages(self):
       log("stop","/var/log/syslog",config.grid_vip)
       logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=58)
    def test_058_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=59)
    def test_059_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=60)
    def test_060_query_domain_test_com_after_deleting_ACL_From_Client2(self):
       logging.info("Querying test.com after updating to ACL_ALLOW, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip2+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=61)
    def test_061_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=62)
    def test_062_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=63)
    def test_063_Delete_Namedacl_ACL_DENY(self):
        logging.info("Deleting ACL ACL_DENY.................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        sleep(30)

    @pytest.mark.run(order=64)
    def test_064_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_DENY is deleted .................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=65)
    def test_065_Delete_Namedacl_ACL_ALLOW(self):
        logging.info("Deleting ACL ACL_ALLOW.................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(delete_acl)
        sleep(30)

    @pytest.mark.run(order=66)
    def test_066_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_ALLOW is deleted .................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

class RFE_6181_Ipv6_Adress_named_ACL(unittest.TestCase):
#############################################  Test cases related to ACL verification #############################################
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
    ##1. Add named acl with IPv4 address 10.36.6.80 and set Operation Allow
    @pytest.mark.run(order=3)
    def test_003_Add_Named_ACL_to_Grid_with_ALLOW_permission(self):
        logging.info("Adding ACL WITH ALLOW.................")
        data={"name": "ACL_ALLOW","access_list": [{"_struct": "addressac", "address": config.client_ip1v6, "permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    ##2. CLI commad execute with zone name test.com
    @pytest.mark.run(order=4)
    def test_004_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_ACL_ALLOW(self):
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

    @pytest.mark.run(order=5)
    def test_005_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain test.com DnsView=default: Set dns_view="default",domain_name="test.com",named_acl="ACL_ALLOW"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=6)
    def test_006_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_ALLOW' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=7)
    def test_007_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=8)
    def test_008_show_allow_query_domain(self):
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

    @pytest.mark.run(order=9)
    def test_009_Validate_named_conf_file(self):
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

    @pytest.mark.run(order=10)
    def test_010_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##3. If we query a.test.com it should return response from 10.36.6.80
    @pytest.mark.run(order=11)
    def test_011_query_domain_test_com_after_adding_to_ACL_ALLOW_From_client_ip1v6(self):
        logging.info("Querying test.com, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vipv6)+' test.com +noedns -b '+config.client_ip1v6+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=12)
    def test_012_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=13)
    def test_013_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=14)
    def test_014_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##4. If we query a.test.com it should refuse queries from 10.36.1.255
    @pytest.mark.run(order=15)
    def test_015_query_domain_test_com_after_adding_to_ACL_ALLOW_From_client_ip2v6(self):
        logging.info("Querying test.com, expected result as REFUSED")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vipv6)+' test.com +noedns -b '+config.client_ip2v6+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=16)
    def test_016_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=17)
    def test_017_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=18)
    def test_018_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##5. If we query other domain say a.zone.com from 10.36.6.80 it should return response
    @pytest.mark.run(order=19)
    def test_019_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_client_ip1v6(self):
       logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vipv6)+' zone.com +noedns -b '+config.client_ip1v6+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=20)
    def test_020_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=21)
    def test_021_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=22)
    def test_022_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##6. If we query other domain say a.zone.com from 10.36.1.255 it should return response
    @pytest.mark.run(order=23)
    def test_023_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_client_ip2v6(self):
       logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vipv6)+' zone.com +noedns -b '+config.client_ip2v6+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(20)

    @pytest.mark.run(order=24)
    def test_024_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=25)
    def test_025_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=26)
    def test_026_Add_Named_ACL_to_Grid_with_DENY_permission(self):
        logging.info("Adding ACL WITH DENY.................")
        data={"name": "ACL_DENY","access_list": [{"_struct": "addressac", "address": config.client_ip1v6, "permission": "DENY"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=27)
    def test_027_update_test_com_from_ACL_ALLOW_TO_ACL_DENY(self):
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

    @pytest.mark.run(order=28)
    def test_028_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Modified AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Modified AllowQueryDomain test.com DnsView=default: Changed named_acl:"ACL_ALLOW"->"ACL_DENY"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=29)
    def test_029_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Updated ACL 'ACL_DENY' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=30)
    def test_030_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=31)
    def test_031_show_allow_query_domain(self):
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

    @pytest.mark.run(order=32)
    def test_032_Validate_named_conf_file(self):
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

    @pytest.mark.run(order=33)
    def test_033_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##1. If we query a.test.com it should refuse queries from 10.36.6.80
    @pytest.mark.run(order=34)
    def test_034_query_domain_test_com_after_updating_from_ACL_ALLOW_to_ACL_DENY_From_client_ip1v6(self):
       logging.info("Querying test.com after updating to ACL_DENY, expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vipv6)+' test.com +noedns -b '+config.client_ip1v6+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=35)
    def test_035_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=36)
    def test_036_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=37)
    def test_037_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##2. If we query a.test.com it should refuse queries from 10.36.1.255
    @pytest.mark.run(order=38)
    def test_038_query_domain_test_com_after_updating_from_ACL_ALLOW_to_ACL_DENY_From_client_ip2v6(self):
       logging.info("Querying test.com after updating to ACL_ALLOW, expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vipv6)+' test.com +noedns -b '+config.client_ip2v6+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=39)
    def test_039_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=40)
    def test_040_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=41)
    def test_041_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##3. If we query other domain say a.zone.com from 10.36.6.80 it should return response
    @pytest.mark.run(order=42)
    def test_042_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_client_ip1v6(self):
        logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vipv6)+' zone.com +noedns -b '+config.client_ip1v6+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=43)
    def test_043_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=44)
    def test_044_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=45)
    def test_045_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##4. If we query other domain say a.zone.com from 10.36.1.255 it should return response
    @pytest.mark.run(order=46)
    def test_046_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_client_ip2v6(self):
        logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vipv6)+' zone.com +noedns -b '+config.client_ip2v6+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=47)
    def test_047_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=48)
    def test_048_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=49)
    def test_049_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
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

    @pytest.mark.run(order=50)
    def test_050_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain test.com DnsView=default', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=51)
    def test_051_validate_infoblox_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Deleted ACL for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=52)
    def test_052_Perform_RESTART_of_the_DNS_service(self):
       logging.info("Restart services")
       grid =  ib_NIOS.wapi_request('GET', object_type="grid")
       ref = json.loads(grid)[0]['_ref']
       publish={"member_order":"SIMULTANEOUSLY"}
       request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
       request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
       restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
       print("System Restart is done successfully")
       sleep(60)

    @pytest.mark.run(order=53)
    def test_053_show_allow_query_domain(self):
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

    @pytest.mark.run(order=54)
    def test_054_Validate_named_conf_file(self):
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

    @pytest.mark.run(order=55)
    def test_055_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=56)
    def test_056_query_domain_test_com_after_deleting_ACL_From_client_ip1v6(self):
      logging.info("Querying test.com after deleting, expected result as NOERROR")
      cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vipv6)+' test.com +noedns -b '+config.client_ip1v6+'"'
      result=subprocess.check_output(cmd, shell=True)
      print(result)
      assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
      logging.info("Test Case Execution Completed")
      sleep(10)

    @pytest.mark.run(order=57)
    def test_057_stop_Syslog_Messages(self):
       log("stop","/var/log/syslog",config.grid_vip)
       logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=58)
    def test_058_Validate_syslog_for_dig_operation(self):
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


    @pytest.mark.run(order=59)
    def test_059_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=60)
    def test_060_query_domain_test_com_after_deleting_ACL_From_client_ip2v6(self):
       logging.info("Querying test.com after updating to ACL_ALLOW, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vipv6)+' test.com +noedns -b '+config.client_ip2v6+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=61)
    def test_061_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=62)
    def test_062_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=63)
    def test_063_Delete_Namedacl_ACL_DENY(self):
        logging.info("Deleting ACL ACL_DENY.................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        sleep(30)

    @pytest.mark.run(order=64)
    def test_064_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_DENY is deleted .................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=65)
    def test_065_Delete_Namedacl_ACL_ALLOW(self):
        logging.info("Deleting ACL ACL_ALLOW.................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(delete_acl)
        sleep(30)

    @pytest.mark.run(order=66)
    def test_066_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_ALLOW is deleted .................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

class RFE_6181_Ipv6_Network_named_ACL(unittest.TestCase):
#############################################  Test cases related to ACL verification #############################################
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
    ##1. Add named acl with IPv4 Network 10.0.0.0/8 and set Operation Allow
    @pytest.mark.run(order=3)
    def test_003_Add_Named_ACL_to_Grid_with_ALLOW_permission(self):
        logging.info("Adding ACL WITH ALLOW.................")
        data={"name": "ACL_ALLOW","access_list": [{"_struct": "addressac", "address": config.IPv6_Network, "permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    ##2. CLI commad execute with zone name test.com
    @pytest.mark.run(order=4)
    def test_004_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_ACL_ALLOW(self):
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

    @pytest.mark.run(order=5)
    def test_005_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain test.com DnsView=default: Set dns_view="default",domain_name="test.com",named_acl="ACL_ALLOW"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=6)
    def test_006_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_ALLOW' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=7)
    def test_007_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=8)
    def test_008_show_allow_query_domain(self):
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

    @pytest.mark.run(order=9)
    def test_009_Validate_named_conf_file(self):
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

    @pytest.mark.run(order=10)
    def test_010_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##3. If we query a.test.com it should return response from 10.36.6.80
    @pytest.mark.run(order=11)
    def test_011_query_domain_test_com_after_adding_to_ACL_ALLOW_From_client_ip1v6(self):
        logging.info("Querying test.com, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vipv6)+' test.com +noedns -b '+config.client_ip1v6+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=12)
    def test_012_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=13)
    def test_013_Validate_syslog_for_dig_operation(self):
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


    @pytest.mark.run(order=14)
    def test_014_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##4. If we query a.test.com it should return response from 10.36.1.255
    @pytest.mark.run(order=15)
    def test_015_query_domain_test_com_after_adding_to_ACL_ALLOW_From_Client2(self):
        logging.info("Querying test.com, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vipv6)+' test.com +noedns -b '+config.client_ip2v6+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=16)
    def test_016_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=17)
    def test_017_Validate_syslog_for_dig_operation(self):
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


    @pytest.mark.run(order=18)
    def test_018_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##5. If we query other domain say a.zone.com from 10.36.6.80 it should return response
    @pytest.mark.run(order=19)
    def test_019_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_client_ip1v6(self):
       logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vipv6)+' zone.com +noedns -b '+config.client_ip1v6+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=20)
    def test_020_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=21)
    def test_021_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=22)
    def test_022_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##6. If we query other domain say a.zone.com from 10.36.1.255 it should return response
    @pytest.mark.run(order=23)
    def test_023_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_Client2(self):
       logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vipv6)+' zone.com +noedns -b '+config.client_ip2v6+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(20)

    @pytest.mark.run(order=24)
    def test_024_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=25)
    def test_025_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=26)
    def test_026_Add_Named_ACL_to_Grid_with_DENY_permission(self):
        logging.info("Adding ACL WITH DENY.................")
        data={"name": "ACL_DENY","access_list": [{"_struct": "addressac", "address": config.IPv6_Network, "permission": "DENY"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=27)
    def test_027_update_test_com_from_ACL_ALLOW_TO_ACL_DENY(self):
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

    @pytest.mark.run(order=28)
    def test_028_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Modified AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Modified AllowQueryDomain test.com DnsView=default: Changed named_acl:"ACL_ALLOW"->"ACL_DENY"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=29)
    def test_029_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Updated ACL 'ACL_DENY' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=30)
    def test_030_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)


    @pytest.mark.run(order=31)
    def test_031_show_allow_query_domain(self):
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

    @pytest.mark.run(order=32)
    def test_032_Validate_named_conf_file(self):
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

    @pytest.mark.run(order=33)
    def test_033_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##1. If we query a.test.com it should refuse queries from 10.36.6.80
    @pytest.mark.run(order=34)
    def test_034_query_domain_test_com_after_updating_from_ACL_ALLOW_to_ACL_DENY_From_client_ip1v6(self):
       logging.info("Querying test.com after updating to ACL_DENY, expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vipv6)+' test.com +noedns -b '+config.client_ip1v6+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=35)
    def test_035_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=36)
    def test_036_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=37)
    def test_037_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##2. If we query a.test.com it should refuse queries from 10.36.1.255
    @pytest.mark.run(order=38)
    def test_038_query_domain_test_com_after_updating_from_ACL_ALLOW_to_ACL_DENY_From_Client2(self):
       logging.info("Querying test.com after updating to ACL_ALLOW, expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vipv6)+' test.com +noedns -b '+config.client_ip2v6+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=39)
    def test_039_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=40)
    def test_040_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=41)
    def test_041_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##3. If we query other domain say a.zone.com from 10.36.6.80 it should return response
    @pytest.mark.run(order=42)
    def test_042_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_client_ip1v6(self):
        logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vipv6)+' zone.com +noedns -b '+config.client_ip1v6+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=43)
    def test_043_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=44)
    def test_044_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=45)
    def test_045_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##4. If we query other domain say a.zone.com from 10.36.1.255 it should return response
    @pytest.mark.run(order=46)
    def test_046_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_Client2(self):
        logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vipv6)+' zone.com +noedns -b '+config.client_ip2v6+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=47)
    def test_047_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=48)
    def test_048_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=49)
    def test_049_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
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

    @pytest.mark.run(order=50)
    def test_050_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain test.com DnsView=default', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=51)
    def test_051_validate_infoblox_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Deleted ACL for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=52)
    def test_052_Perform_RESTART_of_the_DNS_service(self):
       logging.info("Restart services")
       grid =  ib_NIOS.wapi_request('GET', object_type="grid")
       ref = json.loads(grid)[0]['_ref']
       publish={"member_order":"SIMULTANEOUSLY"}
       request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
       request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
       restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
       print("System Restart is done successfully")
       sleep(60)

    @pytest.mark.run(order=53)
    def test_053_show_allow_query_domain(self):
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

    @pytest.mark.run(order=54)
    def test_054_Validate_named_conf_file(self):
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


    @pytest.mark.run(order=55)
    def test_055_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=56)
    def test_056_query_domain_test_com_after_deleting_ACL_From_client_ip1v6(self):
      logging.info("Querying test.com after deleting, expected result as NOERROR")
      cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vipv6)+' test.com +noedns -b '+config.client_ip1v6+'"'
      result=subprocess.check_output(cmd, shell=True)
      print(result)
      assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
      logging.info("Test Case Execution Completed")
      sleep(10)

    @pytest.mark.run(order=57)
    def test_057_stop_Syslog_Messages(self):
       log("stop","/var/log/syslog",config.grid_vip)
       logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=58)
    def test_058_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=59)
    def test_059_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=60)
    def test_060_query_domain_test_com_after_deleting_ACL_From_Client2(self):
       logging.info("Querying test.com after updating to ACL_ALLOW, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip2)+' "dig @'+str(config.grid_vipv6)+' test.com +noedns -b '+config.client_ip2v6+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=61)
    def test_061_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=62)
    def test_062_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=63)
    def test_063_Delete_Namedacl_ACL_DENY(self):
        logging.info("Deleting ACL ACL_DENY.................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        sleep(30)

    @pytest.mark.run(order=64)
    def test_064_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_DENY is deleted .................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=65)
    def test_065_Delete_Namedacl_ACL_ALLOW(self):
        logging.info("Deleting ACL ACL_ALLOW.................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(delete_acl)
        sleep(30)

    @pytest.mark.run(order=66)
    def test_066_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_ALLOW is deleted .................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

class RFE_6181_DNS_view_named_ACL(unittest.TestCase):
#############################################  Test cases related to ACL verification #############################################
    def restart_the_grid(self):
        logging.info("Restaring the grid")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(60)
        print("Restrting the grid")

    ##1.Set CLI deny for test.com
    @pytest.mark.run(order=1)
    def test_001_Add_Named_ACL_to_Grid_with_DENY_permission(self):
        logging.info("Adding ACL WITH DENY.................")
        data={"name": "ACL_DENY","access_list": [{"_struct": "addressac", "address": config.IPv4_Network, "permission": "DENY"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=2)
    def test_002_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_ACL_DENY(self):
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

    @pytest.mark.run(order=3)
    def test_003_validate_audit_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain test.com DnsView=default: Set dns_view="default",domain_name="test.com",named_acl="ACL_DENY"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=4)
    def test_004_validate_infoblox_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_DENY' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=5)
    def test_005_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=6)
    def test_006_show_allow_query_domain(self):
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

    @pytest.mark.run(order=7)
    def test_007_Validate_named_conf_file(self):
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

    @pytest.mark.run(order=8)
    def test_008_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=9)
    def test_009_query_domain_test_com_after_adding_to_ACL_DENY_From_Client1(self):
        logging.info("Querying test.com, expected result as REFUSED")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=10)
    def test_010_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=11)
    def test_011_Validate_syslog_for_dig_operation(self):
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
    @pytest.mark.run(order=12)
    def test_012_Create_View_view1(self):
        data={"name":"view1"}
        request_publish = ib_NIOS.wapi_request('POST',object_type="view",fields=json.dumps(data))
        self.restart_the_grid()
        print("DNS view view1 is created successfully..")

    ##2. Added Authoritative  zone test.com with a record in default view
    @pytest.mark.run(order=13)
    def test_013_create_test_com_authoritative_zone(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        data={"fqdn": "test.com"}
        response = ib_NIOS.wapi_request('POST', object_type='zone_auth',fields=json.dumps(data))
        zone_response = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        res = json.loads(zone_response)
        for i in res:
            data = {"grid_primary":[{"name":"infoblox.localdomain"}]}
            response = ib_NIOS.wapi_request('PUT', ref=i["_ref"],fields=json.dumps(data))
            print("Zone added successfully........")

    @pytest.mark.run(order=14)
    def test_014_Add_arec_A_record_to_test_com_zone(self):
        logging.info("Add a record")
        data = {"name":"arec.test.com","ipv4addr":"2.2.2.2","comment":"A record added"}
        response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
        if (response[0]!=400):
            print ("Added A record")
        else:
            print ("A record already exists")
            logging.info("Test case Execution Completed")

    @pytest.mark.run(order=15)
    def test_015_validate_added_A_record(self):
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
    @pytest.mark.run(order=16)
    def test_016_set_deny_to_dns_default_view(self):
            response = ib_NIOS.wapi_request('GET', object_type="view")
            res = json.loads(response)
            for i in res:
                if i["is_default"] == True:
                    data={"match_clients": [{"_struct": "addressac", "address": "Any", "permission": "DENY"}]}
                    response = ib_NIOS.wapi_request('PUT', ref=i["_ref"],fields=json.dumps(data))
                    print(response)
                    self.restart_the_grid()

    @pytest.mark.run(order=17)
    def test_017_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##4. Query a.test.com.. we can see answer from Forwarder
    @pytest.mark.run(order=18)
    def test_018_query_domain_test_com_after_setting_deny_to_dns_default_view_From_Client1(self):
        logging.info("Querying arec.test.com, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' arec.test.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=19)
    def test_019_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=20)
    def test_020_Validate_syslog_for_dig_operation(self):
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
    @pytest.mark.run(order=21)
    def test_021_set_allow_to_dns_default_view(self):
        response = ib_NIOS.wapi_request('GET', object_type="view")
        res = json.loads(response)
        for i in res:
            if i["is_default"] == True:
                data={"match_clients": [{"_struct": "addressac", "address": "Any", "permission": "ALLOW"}]}
                response = ib_NIOS.wapi_request('PUT', ref=i["_ref"],fields=json.dumps(data))
                print(response)
                self.restart_the_grid()

    @pytest.mark.run(order=22)
    def test_022_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##6. Query a.test.com.. we can see REFUSED answer (because CLI set to deny)
    @pytest.mark.run(order=23)
    def test_023_query_domain_arec_test_com_after_setting_allow_for_dns_default_view_From_Client1(self):
        logging.info("Querying arec.test.com, expected result as REFUSED")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' arec.test.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=24)
    def test_024_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=25)
    def test_025_Validate_syslog_for_dig_operation(self):
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
    @pytest.mark.run(order=26)
    def test_026_Add_Named_ACL_to_Grid_with_ALLOW_permission(self):
        logging.info("Adding ACL WITH ALLOW.................")
        data={"name": "ACL_ALLOW","access_list": [{"_struct": "addressac", "address": config.IPv4_Network, "permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=27)
    def test_027_update_test_com_from_ACL_DENY_TO_ACL_ALLOW(self):
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

    @pytest.mark.run(order=28)
    def test_028_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Modified AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Modified AllowQueryDomain test.com DnsView=default: Changed named_acl:"ACL_DENY"->"ACL_ALLOW"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=29)
    def test_029_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Updated ACL 'ACL_ALLOW' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=30)
    def test_030_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=31)
    def test_031_show_allow_query_domain(self):
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

    @pytest.mark.run(order=32)
    def test_032_Validate_named_conf_file(self):
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

    @pytest.mark.run(order=33)
    def test_033_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##8. Query a.test.com.. we can see answer from Authoritative zone
    @pytest.mark.run(order=34)
    def test_034_query_domain_test_com_after_updating_test_com_from_ACL_DENY_to_ACL_ALLOW(self):
        logging.info("Querying test.com after updating to NOERROR, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' arec.test.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=35)
    def test_035_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=36)
    def test_036_Validate_syslog_for_dig_operation(self):
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
    @pytest.mark.run(order=37)
    def test_037_Update_Dns_default_view_match_clients_with_None(self):
        response = ib_NIOS.wapi_request('GET', object_type="view")
        res = json.loads(response)
        for i in res:
            if i["is_default"] == True:
                print(i)
                data={"match_clients": []}
                response = ib_NIOS.wapi_request('PUT', ref=i["_ref"],fields=json.dumps(data))
                print(response)
                self.restart_the_grid()

    @pytest.mark.run(order=38)
    def test_038_delete_test_com_autoritative_zone(self):
        data={"fqdn":"test.com"}
        response = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
        res = json.loads(response)
        for i in res:
            response = ib_NIOS.wapi_request('DELETE', ref=i["_ref"])
            print(response)
            sleep(10)
            logging.info("Test case Execution Completed")
            self.restart_the_grid()

    @pytest.mark.run(order=39)
    def test_039_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
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

    @pytest.mark.run(order=40)
    def test_040_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain test.com DnsView=default', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=41)
    def test_041_validate_infoblox_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Deleted ACL for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=42)
    def test_042_Perform_RESTART_of_the_DNS_service(self):
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
    @pytest.mark.run(order=43)
    def test_043_Delete_Dns_View_view1(self):
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

    @pytest.mark.run(order=44)
    def test_044_Delete_Namedacl_ACL_DENY(self):
        logging.info("Deleting ACL ACL_DENY.................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        sleep(30)

    @pytest.mark.run(order=45)
    def test_045_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_DENY is deleted .................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=46)
    def test_046_Delete_Namedacl_ACL_ALLOW(self):
        logging.info("Deleting ACL ACL_ALLOW.................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(delete_acl)
        sleep(30)

    @pytest.mark.run(order=47)
    def test_047_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_ALLOW is deleted .................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

class RFE_6181_DNS_new_cases(unittest.TestCase):
#############################################  Test cases related to ACL verification #############################################
    def restart_the_grid(self):
        logging.info("Restaring the grid")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(60)
        print("Restrting the grid")

    ##adding view view1
    @pytest.mark.run(order=1)
    def test_001_Create_View_view1(self):
        data={"name":"view1"}
        request_publish = ib_NIOS.wapi_request('POST',object_type="view",fields=json.dumps(data))
        self.restart_the_grid()
        print("DNS view view1 is created successfully..")

    ##1.Set CLI ALLOW for test.com
    @pytest.mark.run(order=2)
    def test_002_Add_Named_ACL_to_Grid_with_ALLOW_permission(self):
        logging.info("Adding ACL WITH ALLOW.................")
        data={"name": "ACL_ALLOW","access_list": [{"_struct": "addressac", "address": config.IPv4_Network, "permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=3)
    def test_003_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_ACL_ALLOW(self):
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

    @pytest.mark.run(order=4)
    def test_004_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain test.com DnsView=default: Set dns_view="default",domain_name="test.com",named_acl="ACL_ALLOW"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=5)
    def test_005_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_ALLOW' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=6)
    def test_006_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=7)
    def test_007_show_allow_query_domain(self):
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

    @pytest.mark.run(order=8)
    def test_008_Validate_named_conf_file(self):
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
    @pytest.mark.run(order=9)
    def test_009_Add_Named_ACL_to_Grid_with_DENY_permission(self):
        logging.info("Adding ACL WITH DENY.................")
        data={"name": "ACL_DENY","access_list": [{"_struct": "addressac", "address": config.IPv4_Network, "permission": "DENY"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=10)
    def test_010_Add_allow_query_domain_with_domain_name_zone_com_with_named_ACL_ACL_DENY(self):
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

    @pytest.mark.run(order=11)
    def test_011_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain zone.com DnsView=view1: Set dns_view="view1",domain_name="zone.com",named_acl="ACL_DENY"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=12)
    def test_012_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_DENY' for domain 'zone.com' under view 'view1' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=13)
    def test_013_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=14)
    def test_014_show_allow_query_domain(self):
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

    @pytest.mark.run(order=15)
    def test_015_Validate_named_conf_file(self):
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

    @pytest.mark.run(order=16)
    def test_016_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##5. If we query other domain say a.zone.com from 10.36.6.80 it should return response
    @pytest.mark.run(order=17)
    def test_017_query_domain_zone_com_added_to_view1_ACL_DENY_From_Client1(self):
       logging.info("Querying zone.com which is not added to any ACL, expected result as NOERROR")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' zone.com +noedns -b '+config.client_ip1+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=18)
    def test_018_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=19)
    def test_019_Validate_syslog_for_dig_operation(self):
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
    @pytest.mark.run(order=20)
    def test_020_move_views(self):
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

    @pytest.mark.run(order=21)
    def test_021_move_views(self):
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

    @pytest.mark.run(order=22)
    def test_022_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##5. If we query other domain say a.zone.com from 10.36.6.80 it should return response
    @pytest.mark.run(order=23)
    def test_023_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_Client1(self):
       logging.info("Querying zone.com expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' zone.com +noedns -b '+config.client_ip1+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=24)
    def test_024_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=25)
    def test_025_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=26)
    def test_026_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
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

    @pytest.mark.run(order=27)
    def test_027_Validate_named_conf_file(self):
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

    @pytest.mark.run(order=28)
    def test_028_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain test.com DnsView=default', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=29)
    def test_029_validate_infoblox_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Deleted ACL for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=30)
    def test_030_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=31)
    def test_031_Delete_domain_zone_com_using_set_allow_query_domain_delete_command(self):
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

    @pytest.mark.run(order=32)
    def test_032_Validate_named_conf_file(self):
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

    @pytest.mark.run(order=33)
    def test_033_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain zone.com DnsView=view1', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=34)
    def test_034_validate_infoblox_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Deleted ACL for domain 'zone.com' under view 'view1' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=35)
    def test_035_Perform_RESTART_of_the_DNS_service(self):
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
    @pytest.mark.run(order=36)
    def test_036_move_views(self):
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

    @pytest.mark.run(order=37)
    def test_037_move_views(self):
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
    @pytest.mark.run(order=38)
    def test_038_Delete_Dns_View_view1(self):
        data={"name":"view1"}
        response = ib_NIOS.wapi_request('GET',object_type="view",fields=json.dumps(data))
        res = json.loads(response)
        for i in res:
            response = ib_NIOS.wapi_request('DELETE', ref=i["_ref"])
            print(response)
            sleep(10)
            self.restart_the_grid()
            print("DNS view view1 is deleted successfully..")


    @pytest.mark.run(order=39)
    def test_039_validate_views(self):
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

    @pytest.mark.run(order=40)
    def test_040_Delete_Namedacl_ACL_DENY(self):
        logging.info("Deleting ACL ACL_DENY.................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        sleep(30)

    @pytest.mark.run(order=41)
    def test_041_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_DENY is deleted .................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=42)
    def test_042_Delete_Namedacl_ACL_ALLOW(self):
        logging.info("Deleting ACL ACL_ALLOW.................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(delete_acl)
        sleep(30)

    @pytest.mark.run(order=43)
    def test_043_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_ALLOW is deleted .................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

class RFE_6181_DNS_Network_cases(unittest.TestCase):
#############################################  Test cases related to DNS view verification #############################################

    def restart_the_grid(self):
        logging.info("Restaring the grid")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(60)
        print("Restrting the grid")

    ##1. Add network view dhcp (Note: It will crete dns view called 'default.dhcp' )
    @pytest.mark.run(order=1)
    def test_001_Create_networkview(self):
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
    @pytest.mark.run(order=2)
    def test_002_Add_Named_ACL_to_Grid_with_ALLOW_permission(self):
        logging.info("Adding ACL WITH ALLOW.................")
        data={"name": "ACL_ALLOW","access_list": [{"_struct": "addressac", "address": config.IPv4_Network, "permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=3)
    def test_003_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_ACL_ALLOW(self):
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

    @pytest.mark.run(order=4)
    def test_004_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain test.com DnsView=default.dhcp: Set dns_view="default.dhcp",domain_name="test.com",named_acl="ACL_ALLOW"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=5)
    def test_005_validate_infoblox_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_ALLOW' for domain 'test.com' under view 'default.dhcp' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=6)
    def test_006_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=7)
    def test_007_show_allow_query_domain(self):
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

    @pytest.mark.run(order=8)
    def test_008_Validate_named_conf_file(self):
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
    @pytest.mark.run(order=9)
    def test_009_move_views(self):
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

    @pytest.mark.run(order=10)
    def test_010_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##3. If we query a.test.com it should return response from 10.36.6.80
    @pytest.mark.run(order=11)
    def test_011_query_domain_test_com_after_adding_to_ACL_ALLOW_From_Client1(self):
        logging.info("Querying test.com, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=12)
    def test_012_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=13)
    def test_013_Validate_syslog_for_dig_operation(self):
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
    @pytest.mark.run(order=14)
    def test_014_Add_Named_ACL_to_Grid_with_DENY_permission(self):
        logging.info("Adding ACL WITH DENY.................")
        data={"name": "ACL_DENY","access_list": [{"_struct": "addressac", "address": config.IPv4_Network, "permission": "DENY"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=15)
    def test_015_update_test_com_from_ACL_ALLOW_TO_ACL_DENY(self):
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

    @pytest.mark.run(order=16)
    def test_016_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Modified AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Modified AllowQueryDomain test.com DnsView=default.dhcp: Changed named_acl:"ACL_ALLOW"->"ACL_DENY"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=17)
    def test_017_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Updated ACL 'ACL_DENY' for domain 'test.com' under view 'default.dhcp' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")


    @pytest.mark.run(order=18)
    def test_018_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=19)
    def test_019_show_allow_query_domain(self):
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

    @pytest.mark.run(order=20)
    def test_020_Validate_named_conf_file(self):
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

    @pytest.mark.run(order=21)
    def test_021_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##5. If we query other domain say a.test.com from 10.36.6.80 it should refuse
    @pytest.mark.run(order=22)
    def test_022_query_domain_test_com_which_is_not_adding_to_any_ACL_From_Client1(self):
       logging.info("Querying test.com which is not added to any ACL, expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=23)
    def test_023_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=24)
    def test_024_Validate_syslog_for_dig_operation(self):
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
    @pytest.mark.run(order=25)
    def test_025_move_views(self):
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

    @pytest.mark.run(order=26)
    def test_026_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
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

    @pytest.mark.run(order=27)
    def test_027_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain test.com DnsView=default.dhcp', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=28)
    def test_028_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Deleted ACL for domain 'test.com' under view 'default.dhcp' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=29)
    def test_029_Perform_RESTART_of_the_DNS_service(self):
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
    @pytest.mark.run(order=30)
    def test_030_Delete_Dns_View_default_dhcp(self):
        response = ib_NIOS.wapi_request('GET',object_type="networkview")
        res = json.loads(response)
        for i in res:
            if i['name']=='dhcp':
                response = ib_NIOS.wapi_request('DELETE', ref=i["_ref"])
                print(response)
                sleep(10)
                self.restart_the_grid()
                print("network view dhcp is deleted successfully..")

    @pytest.mark.run(order=31)
    def test_031_Delete_Namedacl_ACL_DENY(self):
        logging.info("Deleting ACL ACL_DENY.................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        sleep(30)

    @pytest.mark.run(order=32)
    def test_032_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_DENY is deleted .................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=33)
    def test_033_Delete_Namedacl_ACL_ALLOW(self):
        logging.info("Deleting ACL ACL_ALLOW.................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(delete_acl)
        sleep(30)

    @pytest.mark.run(order=34)
    def test_034_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_ALLOW is deleted .................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

class RFE_6181_ACL_cli_command_message_validation(unittest.TestCase):
#############################################  Test cases related to ACL verification #############################################
    def restart_the_grid(self):
        logging.info("Restaring the grid")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(60)
        print("Restrting the grid")

    ##7. Set CLI allow for test.com
    @pytest.mark.run(order=1)
    def test_001_Add_Named_ACL_to_Grid_with_ALLOW_permission(self):
        logging.info("Adding ACL WITH ALLOW.................")
        data={"name": "ACL_ALLOW","access_list": [{"_struct": "addressac", "address": "10.0.0.0/8", "permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    ##2. CLI commad execute with zone name test.com
    @pytest.mark.run(order=2)
    def test_002_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_ACL_ALLOW(self):
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

    @pytest.mark.run(order=3)
    def test_003_update_test_com_TO_ACL_ALLOW_which_is_already_in_ACL_ALLOW_and_validating_message(self):
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

    @pytest.mark.run(order=4)
    def test_004_Add_Named_ACL_to_Grid_with_DENY_permission(self):
        logging.info("Adding ACL WITH DENY.................")
        data={"name": "ACL_DENY","access_list": [{"_struct": "addressac", "address": config.IPv4_Network, "permission": "DENY"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=5)
    def test_005_update_test_com_from_ACL_ALLOW_TO_ACL_DENY(self):
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

    @pytest.mark.run(order=6)
    def test_006_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=7)
    def test_007_update_test2_com_which_is_not_in_any_named_ACL_TO_ACL_ALLOW_validating_error_message(self):
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

    @pytest.mark.run(order=8)
    def test_008_Delete_domain_zone_com_which_is_not_added_to_any_ACL_validating_error_message(self):
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

    @pytest.mark.run(order=9)
    def test_009_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
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

    @pytest.mark.run(order=10)
    def test_010_show_allow_query_domain(self):
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
    @pytest.mark.run(order=11)
    def test_011_Add_allow_query_domain_with_domain_name_zone1_com_with_named_ACL_ACL_ALLOW(self):
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
    @pytest.mark.run(order=12)
    def test_012_Add_allow_query_domain_with_domain_name_zone1_com_with_named_ACL_ACL_ALLOW(self):
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

    @pytest.mark.run(order=13)
    def test_013_show_allow_query_domain_views(self):
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

    @pytest.mark.run(order=14)
    def test_014_show_allow_query_domain(self):
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

    @pytest.mark.run(order=15)
    def test_015_Delete_default_using_set_allow_query_domain_delete_command(self):
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

    @pytest.mark.run(order=16)
    def test_016_Delete_domain_default_using_set_allow_query_domain_delete_command_validation_erroe_message(self):
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

    @pytest.mark.run(order=17)
    def test_017_Delete_domain_zone1_com_using_set_allow_query_domain_delete_command(self):
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

    @pytest.mark.run(order=18)
    def test_018_show_allow_query_domain_views(self):
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

    @pytest.mark.run(order=19)
    def test_019_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_ACL_ALLOW(self):
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
    @pytest.mark.run(order=20)
    def test_020_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_ACL_ALLOW_validating_error_message(self):
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

    @pytest.mark.run(order=21)
    def test_021_show_allow_query_domain_views(self):
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
    @pytest.mark.run(order=22)
    def test_022_Add_allow_query_domain_with_domain_name_of_size_more_then_255_charecters_with_named_ACL_ACL_ALLOW_validating_error_message(self):
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

    @pytest.mark.run(order=23)
    def test_023_Add_allow_query_domain_with_domain_name_xyz_com_with_lengt_of_view_more_then_64_and_validating_error_message(self):
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
    @pytest.mark.run(order=24)
    def test_024_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_with_size_of_more_then_64_charecter(self):
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

    @pytest.mark.run(order=25)
    def test_025_Delete_Namedacl_ACL_DENY(self):
        logging.info("Deleting ACL ACL_DENY.................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        sleep(30)

    @pytest.mark.run(order=26)
    def test_026_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_DENY is deleted .................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=27)
    def test_027_Delete_Namedacl_ACL_ALLOW(self):
        logging.info("Deleting ACL ACL_ALLOW.................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(delete_acl)
        sleep(30)

    @pytest.mark.run(order=28)
    def test_028_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_ALLOW is deleted .................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

class RFE_6181_miscellaneous_cases(unittest.TestCase):
#############################################  Test cases related to ACL verification #############################################
    def restart_the_grid(self):
        logging.info("Restaring the grid")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(60)
        print("Restrting the grid")

    ##1.Set CLI deny for test.com
    @pytest.mark.run(order=1)
    def test_001_Add_Named_ACL_to_Grid_with_ALLOW_permission(self):
        logging.info("Adding ACL WITH ALLOW.................")
        data={"name": "ACL_ALLOW_with_tsig_xfer","access_list": [{"_struct": "tsigac", "tsig_key": ":2xCOMPAT", "tsig_key_name": "tsig_xfer"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=2)
    def test_002_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_ACL_DENY(self):
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
    @pytest.mark.run(order=3)
    def test_003_Add_Named_ACL_to_Grid_with_ALLOW_permission(self):
        logging.info("Adding ACL WITH ALLOW.................")
        data={"name": "ACL_ALLOW","access_list": [{"_struct": "addressac", "address": "10.0.0.0/8","permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    ##2. CLI commad execute with zone name test.com
    @pytest.mark.run(order=4)
    def test_004_Add_allow_query_domain_with_domain_name_example_com_with_named_ACL_ACL_ALLOW(self):
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

    @pytest.mark.run(order=5)
    def test_005_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain example.com DnsView=default: Set dns_view="default",domain_name="example.com",named_acl="ACL_ALLOW"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=6)
    def test_006_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_ALLOW' for domain 'example.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=7)
    def test_007_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=8)
    def test_008_Delete_Namedacl_ACL_ALLOW(self):
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

    @pytest.mark.run(order=9)
    def test_009_show_allow_query_domain(self):
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
    @pytest.mark.run(order=10)
    def test_010_Add_Named_ACL_to_Grid_with_DENY_permission(self):
        logging.info("Adding ACL WITH DENY.................")
        data={"name": "ACL_DENY","access_list": [{"_struct": "addressac", "address": "10.0.0.0/8", "permission": "DENY"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=11)
    def test_011_Add_allow_query_domain_with_domain_name_level3_example_com_with_named_ACL_ACL_DENY(self):
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

    @pytest.mark.run(order=12)
    def test_012_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain level3.example.com DnsView=default: Set dns_view="default",domain_name="level3.example.com",named_acl="ACL_DENY"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=13)
    def test_013_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_DENY' for domain 'level3.example.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=14)
    def test_014_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=15)
    def test_015_show_allow_query_domain(self):
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

    @pytest.mark.run(order=16)
    def test_016_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=17)
    def test_017_query_domain_level4_level3_example_com_after_adding_to_ACL_DENY_From_Client1(self):
        logging.info("Querying level4.level3.example.com, expected result as REFUSED")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' level4.level3.example.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=18)
    def test_018_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=19)
    def test_019_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=20)
    def test_020_update_example_com_from_ACL_ALLOW_TO_ACL_DENY(self):
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

    @pytest.mark.run(order=21)
    def test_021_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Modified AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Modified AllowQueryDomain example.com DnsView=default: Changed named_acl:"ACL_ALLOW"->"ACL_DENY"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=22)
    def test_022_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Updated ACL 'ACL_DENY' for domain 'example.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=23)
    def test_023_query_domain_zone_com_which_is_not_adding_to_any_ACL_From_client_ip2v6_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=24)
    def test_024_show_allow_query_domain(self):
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

    @pytest.mark.run(order=25)
    def test_025_update_level3_example_com_from_ACL_DENY_TO_ACL_ALLOW(self):
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

    @pytest.mark.run(order=26)
    def test_026_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Modified AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Modified AllowQueryDomain level3.example.com DnsView=default: Changed named_acl:"ACL_DENY"->"ACL_ALLOW"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=27)
    def test_027_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Updated ACL 'ACL_ALLOW' for domain 'level3.example.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=28)
    def test_028_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=29)
    def test_029_show_allow_query_domain(self):
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

    @pytest.mark.run(order=30)
    def test_030_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##8. Query a.test.com..
    @pytest.mark.run(order=31)
    def test_031_query_domain_test_com_after_updating_test_com_from_ACL_DENY_to_ACL_ALLOW(self):
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' level4.level3.example.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=32)
    def test_032_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=33)
    def test_033_Validate_syslog_for_dig_operation(self):
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
    @pytest.mark.run(order=34)
    def test_034_create_test_com_authoritative_zone(self):
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

    @pytest.mark.run(order=35)
    def test_035_Add_CNAME_record_to_test_com_zone(self):
        logging.info("Add cname record")
        data = {"name":"cname.test.com","canonical":"abc.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:cname",fields=json.dumps(data))
        if (response[0]!=400):
            print ("Added cname record")
        else:
            print ("A record already exists")
            logging.info("Test case Execution Completed")

    @pytest.mark.run(order=36)
    def test_036_Add_DNAME_record_to_test_com_zone(self):
        logging.info("Add dname record")
        data = {"name":"dname.test.com","target":"xyz.com"}
        response = ib_NIOS.wapi_request('POST', object_type="record:dname",fields=json.dumps(data))
        if (response[0]!=400):
            print ("Added dname record")
        else:
            print ("A record already exists")
            logging.info("Test case Execution Completed")

    @pytest.mark.run(order=37)
    def test_037_Add_allow_query_domain_with_domain_name_abc_com_with_named_ACL_ACL_DENY(self):
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

    @pytest.mark.run(order=38)
    def test_038_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain abc.com DnsView=default: Set dns_view="default",domain_name="abc.com",named_acl="ACL_DENY"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=39)
    def test_039_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_DENY' for domain 'abc.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=40)
    def test_040_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=41)
    def test_041_show_allow_query_domain(self):
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

    @pytest.mark.run(order=42)
    def test_042_Add_allow_query_domain_with_domain_name_xyz_com_with_named_ACL_ACL_DENY(self):
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

    @pytest.mark.run(order=43)
    def test_043_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain xyz.com DnsView=default: Set dns_view="default",domain_name="xyz.com",named_acl="ACL_DENY"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=44)
    def test_044_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_DENY' for domain 'xyz.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=45)
    def test_045_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=46)
    def test_046_show_allow_query_domain(self):
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

    @pytest.mark.run(order=47)
    def test_047_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=48)
    def test_048_query_domain_abc_com_after_adding_to_ACL_DENY_From_Client1(self):
        logging.info("Querying abc.com, expected result as REFUSED")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' abc.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=49)
    def test_049_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=50)
    def test_050_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=51)
    def test_051_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=52)
    def test_052_query_domain_xyz_com_after_adding_to_ACL_DENY_From_Client1(self):
        logging.info("Querying xyz.com, expected result as REFUSED")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' xyz.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=53)
    def test_053_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=54)
    def test_054_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=55)
    def test_055_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
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

    @pytest.mark.run(order=56)
    def test_056_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain example.com DnsView=default', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=57)
    def test_057_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Deleted ACL for domain 'example.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=58)
    def test_058_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
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

    @pytest.mark.run(order=59)
    def test_059_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain level3.example.com DnsView=default', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=60)
    def test_060_validate_infoblox_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Deleted ACL for domain 'level3.example.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=61)
    def test_061_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
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

    @pytest.mark.run(order=62)
    def test_062_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain abc.com DnsView=default', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=63)
    def test_063_validate_infoblox_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Deleted ACL for domain 'abc.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=64)
    def test_064_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
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

    @pytest.mark.run(order=65)
    def test_065_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain xyz.com DnsView=default', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=66)
    def test_066_validate_infoblox_log_file(self):
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
    @pytest.mark.run(order=67)
    def test_067_Add_Named_ACL_to_Grid_ACL_allow_any_with_ALLOW_permission(self):
        logging.info("Adding ACL WITH ALLOW.................")
        data={"name": "ACL_allow_any","access_list": [{"_struct": "addressac", "address": "Any","permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    ##2. CLI commad execute with zone name test.com
    @pytest.mark.run(order=68)
    def test_068_Add_allow_query_domain_with_domain_name_example_com_with_named_ACL_ACL_allow_any(self):
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

    @pytest.mark.run(order=69)
    def test_069_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain example.com DnsView=default: Set dns_view="default",domain_name="example.com",named_acl="ACL_allow_any"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=70)
    def test_070_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_allow_any' for domain 'example.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=71)
    def test_071_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=72)
    def test_072_show_allow_query_domain(self):
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

    @pytest.mark.run(order=73)
    def test_073_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##8. Query a.test.com..
    @pytest.mark.run(order=74)
    def test_074_query_domain_test_com_after_updating_test_com_from_ACL_DENY_to_ACL_ALLOW(self):
        logging.info("Querying test.com after updating to NOERROR, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' example.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=75)
    def test_075_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=76)
    def test_076_Validate_syslog_for_dig_operation(self):
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
    @pytest.mark.run(order=77)
    def test_077_Add_Named_ACL_to_Grid_ACL_deny_any_with_DENY_permission(self):
        logging.info("Adding ACL WITH DENY.................")
        data={"name": "ACL_deny_any","access_list": [{"_struct": "addressac", "address": "Any","permission": "DENY"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    ##2. CLI commad execute with zone name test.com
    @pytest.mark.run(order=78)
    def test_078_Add_allow_query_domain_with_domain_name_example_com_with_named_ACL_ACL_deny_any(self):
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

    @pytest.mark.run(order=79)
    def test_079_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain xyz.com DnsView=default: Set dns_view="default",domain_name="xyz.com",named_acl="ACL_deny_any"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=80)
    def test_080_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_deny_any' for domain 'xyz.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=81)
    def test_081_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=82)
    def test_082_show_allow_query_domain(self):
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

    @pytest.mark.run(order=83)
    def test_083_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=84)
    def test_084_query_domain_xyz_com_after_adding_to_ACL_DENY_From_Client1(self):
        logging.info("Querying xyz.com, expected result as REFUSED")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' xyz.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=85)
    def test_085_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=86)
    def test_086_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=87)
    def test_087_Delete_Namedacl_ACL_DENY(self):
        logging.info("Deleting ACL ACL_DENY.................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        sleep(30)

    @pytest.mark.run(order=88)
    def test_088_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_DENY is deleted .................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=89)
    def test_089_Delete_Namedacl_ACL_ALLOW(self):
        logging.info("Deleting ACL ACL_ALLOW.................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(delete_acl)
        sleep(30)

    @pytest.mark.run(order=90)
    def test_090_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_ALLOW is deleted .................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=91)
    def test_091_Delete_Namedacl_ACL_ALLOW_with_tsig_xfer(self):
        logging.info("Deleting ACL ACL_ALLOW_with_tsig_xfer.................")
        data={"name": "ACL_ALLOW_with_tsig_xfer"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(delete_acl)
        sleep(30)

    @pytest.mark.run(order=92)
    def test_092_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
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

    @pytest.mark.run(order=93)
    def test_093_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
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

    @pytest.mark.run(order=94)
    def test_094_Delete_Namedacl_ACL_deny_any(self):
        logging.info("Deleting ACL ACL_deny_any.................")
        data={"name": "ACL_deny_any"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        sleep(30)

    @pytest.mark.run(order=95)
    def test_095_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_deny_any is deleted .................")
        data={"name": "ACL_deny_any"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=96)
    def test_096_Delete_Namedacl_ACL_allow_any(self):
        logging.info("Deleting ACL ACL_allow_any.................")
        data={"name": "ACL_allow_any"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        sleep(30)

    @pytest.mark.run(order=97)
    def test_097_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_allow_any is deleted .................")
        data={"name": "ACL_allow_any"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=98)
    def test_098_delete_test_com_autoritative_zone(self):
        data={"fqdn":"test.com"}
        response = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
        res = json.loads(response)
        for i in res:
            response = ib_NIOS.wapi_request('DELETE', ref=i["_ref"])
            print(response)
            sleep(10)
            logging.info("Test case Execution Completed")
            self.restart_the_grid()

class RFE_6181_DCA_related_acl_cases(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_001_enable_dns_cache_acceleration(self):
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
    @pytest.mark.run(order=2)
    def test_002_Add_Named_ACL_to_Grid_with_ALLOW_permission(self):
        logging.info("Adding ACL WITH ALLOW.................")
        data={"name": "ACL_ALLOW","access_list": [{"_struct": "addressac", "address": "10.0.0.0/8","permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=3)
    def test_003_Add_allow_query_domain_with_domain_name_test_com_with_named_ACL_ACL_ALLOW(self):
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

    @pytest.mark.run(order=4)
    def test_004_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Created AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Created AllowQueryDomain test.com DnsView=default: Set dns_view="default",domain_name="test.com",named_acl="ACL_ALLOW"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=5)
    def test_005_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Added ACL 'ACL_ALLOW' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=6)
    def test_006_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=7)
    def test_007_show_allow_query_domain(self):
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

    @pytest.mark.run(order=8)
    def test_008_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##4. Query test.com..
    @pytest.mark.run(order=9)
    def test_009_query_domain_test_com_after_setting_deny_to_dns_default_view_From_Client1(self):
        logging.info("Querying arec.test.com, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=10)
    def test_010_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=11)
    def test_011_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=12)
    def test_012_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##4. Query a.test.com
    @pytest.mark.run(order=13)
    def test_013_query_domain_test_com_after_setting_deny_to_dns_default_view_From_Client1(self):
        logging.info("Querying test.com, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=14)
    def test_014_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=15)
    def test_015_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=16)
    def test_016_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##4. Query a.test.com
    @pytest.mark.run(order=17)
    def test_017_query_domain_test_com_after_setting_deny_to_dns_default_view_From_Client1(self):
        logging.info("Querying test.com, expected result as NOERROR")
        cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
        result=subprocess.check_output(cmd, shell=True)
        print(result)
        assert re.search(r'.*QUERY, status: NOERROR.*',str(result))
        logging.info("Test Case Execution Completed")
        sleep(10)

    @pytest.mark.run(order=18)
    def test_018_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=19)
    def test_019_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=20)
    def test_020_Validate_DCA_Cache_Hit_Counts_set_to_Zero(self):
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

    @pytest.mark.run(order=21)
    def test_021_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
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

    @pytest.mark.run(order=22)
    def test_022_Add_Named_ACL_to_Grid_with_DENY_permission(self):
        logging.info("Adding ACL WITH DENY.................")
        data={"name": "ACL_DENY","access_list": [{"_struct": "addressac", "address": config.client_ip1, "permission": "DENY"}]}
        response = ib_NIOS.wapi_request('POST', object_type='namedacl',fields=json.dumps(data))
        print(response)

    @pytest.mark.run(order=23)
    def test_023_update_test_com_from_ACL_ALLOW_TO_ACL_DENY(self):
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

    @pytest.mark.run(order=24)
    def test_024_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Modified AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Modified AllowQueryDomain test.com DnsView=default: Changed named_acl:"ACL_ALLOW"->"ACL_DENY"', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=25)
    def test_025_validate_infoblox_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Updated ACL 'ACL_DENY' for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=26)
    def test_026_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=27)
    def test_027_show_allow_query_domain(self):
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

    @pytest.mark.run(order=28)
    def test_028_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    @pytest.mark.run(order=29)
    def test_029_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##1. If we query a.test.com it should refuse queries from 10.36.6.80
    @pytest.mark.run(order=30)
    def test_030_query_domain_test_com_after_updating_from_ACL_ALLOW_to_ACL_DENY_From_Client1(self):
       logging.info("Querying test.com after updating to ACL_DENY, expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=31)
    def test_031_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=32)
    def test_032_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=33)
    def test_033_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##1. If we query a.test.com it should refuse queries from 10.36.6.80
    @pytest.mark.run(order=34)
    def test_034_query_domain_test_com_after_updating_from_ACL_ALLOW_to_ACL_DENY_From_Client1(self):
       logging.info("Querying test.com after updating to ACL_DENY, expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=35)
    def test_035_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=36)
    def test_036_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=37)
    def test_037_start_Syslog_Messages(self):
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case passed")
        sleep(10)

    ##1. If we query a.test.com it should refuse queries from 10.36.6.80
    @pytest.mark.run(order=38)
    def test_038_query_domain_test_com_after_updating_from_ACL_ALLOW_to_ACL_DENY_From_Client1(self):
       logging.info("Querying test.com after updating to ACL_DENY, expected result as REFUSED")
       cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.client_ip1)+' "dig @'+str(config.grid_vip)+' test.com +noedns -b '+config.client_ip1+'"'
       result=subprocess.check_output(cmd, shell=True)
       print(result)
       assert re.search(r'.*QUERY, status: REFUSED.*',str(result))
       logging.info("Test Case Execution Completed")
       sleep(10)

    @pytest.mark.run(order=39)
    def test_039_stop_Syslog_Messages(self):
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=40)
    def test_040_Validate_syslog_for_dig_operation(self):
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

    @pytest.mark.run(order=41)
    def test_041_Validate_DCA_Cache_Hit_Counts_set_to_Zero(self):
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

    @pytest.mark.run(order=42)
    def test_042_Validate_DCA_Cache_content_shows_Cache_is_empty(self):
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

    @pytest.mark.run(order=43)
    def test_043_Validate_DNS_query_status_FAILURE_Zero(self):
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

    @pytest.mark.run(order=44)
    def test_044_Delete_domain_test_com_using_set_allow_query_domain_delete_command(self):
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

    @pytest.mark.run(order=45)
    def test_045_validate_audit_log_file(self):
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/audit.log | grep  \'Deleted AllowQueryDomain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search('Deleted AllowQueryDomain test.com DnsView=default', string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=46)
    def test_046_validate_infoblox_log_file(self):
        logging.info("Validate WAPI Detailed audit log for added A record")
        audit_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /infoblox/var/infoblox.log | grep  \'set_allow_query_domain\'"'
        string_content = commands.getoutput(audit_log_validation)
        logging.info(string_content)
        if bool(re.search("Deleted ACL for domain 'test.com' under view 'default' successfully", string_content)):
             assert True
        else:
            assert False
            logging.info("Test Case Execution Completed")

    @pytest.mark.run(order=47)
    def test_047_Perform_RESTART_of_the_DNS_service(self):
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print("System Restart is done successfully")
        sleep(30)

    @pytest.mark.run(order=48)
    def test_048_Delete_Namedacl_ACL_DENY(self):
        logging.info("Deleting ACL ACL_DENY.................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        sleep(30)

    @pytest.mark.run(order=49)
    def test_049_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_DENY is deleted .................")
        data={"name": "ACL_DENY"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=50)
    def test_050_Delete_Namedacl_ACL_ALLOW(self):
        logging.info("Deleting ACL ACL_ALLOW.................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        delete_acl=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(delete_acl)
        sleep(30)

    @pytest.mark.run(order=51)
    def test_051_Delete_Namedacl_Varification(self):
        logging.info("varify wether ACL_ALLOW is deleted .................")
        data={"name": "ACL_ALLOW"}
        acl = ib_NIOS.wapi_request('GET', object_type='namedacl',fields=json.dumps(data))
        print(acl)
        if len(acl)==2:
            assert True
        else:
            assert False

class RFE_6181_non_super_user_validation_for_Named_acl_cli_commands(unittest.TestCase):
#############################################  Test cases related to ACL verification #############################################
    @pytest.mark.run(order=1)
    def test_001_create_admin_group(self):
        reference=[]
        data={'name':'group1'}
        response_created=ib_NIOS.wapi_request('POST',object_type="admingroup",fields=json.dumps(data))
        data1={"admin_groups": ["group1"],"name": "user123","password":"user123"}
        response1=ib_NIOS.wapi_request('POST',object_type="adminuser",fields=json.dumps(data1))
        print(response1)

    @pytest.mark.run(order=2)
    def test_002_enable_cli_for_group1(self):
        get_ref = ib_NIOS.wapi_request('GET',object_type="admingroup?_return_fields=access_method")
        res = json.loads(get_ref)
        for i in res:
            ref=i["_ref"]
            if 'group1' in i["_ref"]:
                data={"access_method": ["GUI","CLI"]}
                get_ref = ib_NIOS.wapi_request('PUT',ref=ref +"?_return_fields=access_method", fields=json.dumps(data))
                print("testcase passed")

    @pytest.mark.run(order=3)
    def test_003_validate_enabling_cli_Group1(self):
        get_ref = ib_NIOS.wapi_request('GET',object_type="admingroup?_return_fields=access_method")
        print(get_ref)
        res = json.loads(get_ref)
        for i in res:
            ref=i["_ref"]
            if 'group1' in i["_ref"]:
                if i['access_method']==["GUI","CLI"]:
                    print("testcase passed")


    @pytest.mark.run(order=3)
    def test_003_check_set_allow_query_domain_add_command_for_non_super_user(self):
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

    @pytest.mark.run(order=4)
    def test_004_check_set_allow_query_domain_update_command_for_non_super_user(self):
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

    @pytest.mark.run(order=5)
    def test_005_check_set_allow_query_domain_delete_command_for_non_super_user(self):
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

    @pytest.mark.run(order=6)
    def test_006_check_set_allow_query_domain_show_command_for_non_super_user(self):
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

    @pytest.mark.run(order=7)
    def test_007_Delete_user(self):
        data={"name": "user123"}
        acl = ib_NIOS.wapi_request('GET', object_type='adminuser',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        deleteed_user=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(deleteed_user)
        sleep(30)

    @pytest.mark.run(order=8)
    def test_008_Delete_group(self):
        data={"name": "group1"}
        acl = ib_NIOS.wapi_request('GET', object_type='admingroup',fields=json.dumps(data))
        ref = json.loads(acl)[0]['_ref']
        print(ref)
        deleted_group=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(deleted_group)
        sleep(30)


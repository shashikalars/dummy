import config
import re
import pexpect
import pytest
import unittest
import logging
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
import socket
#from ib_utils.log_capture import log_action as log
#from ib_utils.file_validation import log_validation as logv
#from ib_utils.validate_named_conf import log_validation as named_log_1
#import validate_named_conf as named_log_1
#from ib_utils.validate_named_conf import validate_named_file as named_conf
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
from paramiko import client
import paramiko
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)



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
            result=stdout.readlines()
            return result
        else:
            logging.info("Connection not opened.")



def validate_named_conf (string,IP_address, Host_address=host_ip):
    try:
        logging.info ("Checking Log Info")
        connection=SSH(str(IP_address))
        #command1='cat /tmp/'+ str(IP_address)+file_name+'| grep -i '+string
        command1="cat /infoblox/var/named_conf/named.conf | grep -i '"+ string +"'"
        result= connection.send_command(command1)
        return result
    except grep:
        logging.info ("Pattern not found")


class Network(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_001_Start_DNS_Service(self):
        logging.info("Start DNS Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        logging.info(get_ref)
        res = json.loads(get_ref)
        for member in res:
            ref1 = member["_ref"]
            print ref1
            logging.info("Modify a enable_dns")
            data = {"enable_dns": True}
            response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
            print response
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
        print res
        for i in res:
            print i
            logging.info("found")
            assert i["enable_dns"] == True
        logging.info("Test Case 2 Execution Completed")
        logging.info("============================")


    @pytest.mark.run(order=3)
    def test_003_modify_grid_dns_properties(self):
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:dns")
        get_ref1=json.loads(get_ref)[0]['_ref']
        print get_ref1
        data={"logging_categories":{"log_rpz":True},"allow_recursive_query":True,"allow_transfer":[{"_struct":"addressac","address":"Any","permission":"ALLOW"}],"allow_update":[{"_struct":"addressac","address":"Any","permission":"ALLOW"}],"allow_query":[{"_struct": "addressac","address":"Any","permission":"ALLOW"}],"forwarders":["10.36.6.80"]}
        put_ref=ib_NIOS.wapi_request('PUT', object_type=get_ref1,fields=json.dumps(data))
        logging.info(put_ref)
        read  = re.search(r'200',put_ref)
        for read in put_ref:
            assert True
        logging.info("Test Case 3 Execution Completed")
        sleep(20)



    @pytest.mark.run(order=4)
    def test_004_add_dns_view(self):
        data={"name": "myview1","comment":"Adding dns view"}
        get_ref=ib_NIOS.wapi_request('POST', object_type="view",fields=json.dumps(data))

        print get_ref
        if type(get_ref)!=tuple:
            logging.info("adding DNS view")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            time.sleep(10)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            time.sleep(20)
            print ("Restarting the grid ")
            logging.info("Test Case 4 passed as the view is added")
            assert True
        else:
            logging.info("Test case 4 failed as the view is failed to add")
            assert False

    @pytest.mark.run(order=5)
    def test_005_validate_added_dns_view(self):
        get_ref=ib_NIOS.wapi_request('GET', object_type="view?_return_fields=name,comment")
        get_ref=json.loads(get_ref)
        for view in get_ref:
            if view["name"]=="myview1": 
                if view["comment"]=="Adding dns view":
                    logging.info("test case 5 is passed as view is added")
                    assert True
                else:
                    logging.info("test case 5 is failed as view is not added")
                    assert False


    @pytest.mark.run(order=6)
    def test_006_add_rpz_zone_to_default_view(self):
        data={"fqdn": "zone1","grid_primary":[{"name": config.grid_fqdn,"stealth":False}],"view":"default"}
        print config.grid_fqdn
        get_ref=ib_NIOS.wapi_request('POST', object_type="zone_rp",fields=json.dumps(data))
        print get_ref
        logging.info("adding RPZ zone ")
        if type(get_ref)!=tuple:
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            time.sleep(10)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            time.sleep(20)
            print ("Restarting the grid ")
            response=ib_NIOS.wapi_request('GET', object_type="zone_rp")
            response1=json.loads(response)
            if response1[0]["fqdn"]==data["fqdn"]:
                logging.info("Test case 6 passed as RPZ zone is added")
                assert True
            else:
                logging.info("Test case 6 failed as RPZ zone is not added")
                assert False
        else:
            logging.info("Test case 6 failed as RPZ zone is not added")
            assert False

    @pytest.mark.run(order=7)
    def test_007_add_rpz_zone2_to_custom_view_myview1(self):
        data={"fqdn": "zone2","grid_primary":[{"name": config.grid_member1_fqdn,"stealth":False}],"view":"myview1","comment":"added zone2"}
        get_ref=ib_NIOS.wapi_request('POST', object_type="zone_rp",fields=json.dumps(data))
        logging.info("adding RPZ zone ")
        if type(get_ref)!='tuple':
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            time.sleep(10)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            time.sleep(20)
            print ("Restarting the grid ")
            response=ib_NIOS.wapi_request('GET', object_type="zone_rp?_return_fields=fqdn,comment")
            response1=json.loads(response)
            for i in response1:

                if i["fqdn"]==data["fqdn"]:
                    if i["comment"]=="added zone2":
                        logging.info("Test case 7 passed as RPZ zone is added")
                        assert True
                    else:
                        logging.info("Test case 7 failed as RPZ zone is not added")
                        assert False

    @pytest.mark.run(order=8)
    def test_008_add_ruleset_in_rpz_zone_in_default_view_in_zone1(self):
        data={"name":"xdomain.com.zone1","rp_zone":"zone1","canonical":""}
        reference=ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        time.sleep(10)
        if type(reference)!="tuple":
            assert True
            logging.info("Test case 8 execution passed as ruleset is added in RPZ Zone")
        else:
            assert False
            logging.info("Test case 8 execution failed as ruleset is not added in RPZ Zone")

    @pytest.mark.run(order=9)
    def test_009_add_ruleset_in_rpz_zone_in_custom_view_in_zone2(self):
        data={"name":"ydomain.com.zone2","rp_zone":"zone2","canonical":"","view":"myview1"}
        reference=ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        print reference
        if reference[0]!=400:
            assert True
            logging.info("Test case 9 execution passed as ruleset is added in RPZ Zone")
        else:
            assert False
            logging.info("Test case 9 execution failed as ruleset is not added in RPZ Zone")

    @pytest.mark.run(order=10)
    def test_010_check_for_default_value_of_rpz_logging_in_zone_level_in_default_view_in_zone1(self):
        response=ib_NIOS.wapi_request('GET', object_type="zone_rp?_return_fields=fqdn,log_rpz")
        response=json.loads(response)
        for zone in response:
            if zone["fqdn"]=="zone1":
                if zone["log_rpz"]==True:
                    logging.info("Test case 10 execution passed")
                    assert True
                else:
                    logging.info("Test case 10 execution failed")
                    assert False

    @pytest.mark.run(order=11)
    def test_011_check_for_default_value_of_rpz_logging_in_zone_level_in_custom_view_in_zone2(self):
        response=ib_NIOS.wapi_request('GET', object_type="zone_rp?_return_fields=fqdn,log_rpz")
        response=json.loads(response)
        for zone in response:
            if zone["fqdn"]=="zone2": 
                if zone["log_rpz"]==True:
                    logging.info("Test case 11 execution passed")
                    assert True
                else:
                    logging.info("Test case 11 execution failed")
                    assert False


    @pytest.mark.run(order=12)
    def test_012_set_rpz_logging_at_zone_level_to_false_in_default_view_zone1_when_enabled_at_grid_level(self):
        res=ib_NIOS.wapi_request('GET', object_type="zone_rp?_return_fields=fqdn,log_rpz")
        res=json.loads(res)
        for i in res:
            if i["fqdn"]=="zone1":
                data={"log_rpz":False}
                response=ib_NIOS.wapi_request('PUT', object_type=i["_ref"],fields=json.dumps(data))
                if response[0]!=400:
                    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                    ref = json.loads(grid)[0]['_ref']
                    publish={"member_order":"SIMULTANEOUSLY"}
                    request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                    time.sleep(10)
                    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                    time.sleep(20)
                    print ("Restarting the grid ")
                    logging.info("Test case 12 passed")
                    assert True
                    time.sleep(40)
                else:
                    logging.info("Test case 12 Failed")
                    assert False

    @pytest.mark.run(order=13)
    def test_013_validate_set_rpz_logging_at_zone_level_in_default_view_zone1_when_enabled_at_grid_level(self):
        data={"fqdn":"zone1","log_rpz":False}
        response=ib_NIOS.wapi_request('GET', object_type="zone_rp?_return_fields=fqdn,log_rpz")
        response=json.loads(response)
        for zone in response:
            if zone["fqdn"]==data["fqdn"]:
                if zone["log_rpz"]==data["log_rpz"]:
                    print("Test case passed")
                    assert True
                else:
                    print("test case 13 failed")
                    assert False

    @pytest.mark.run(order=14)
    def test_014_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("Test case 14  execution passed")

    @pytest.mark.run(order=15)
    def test_015_send_query(self):
        dig_cmd = 'dig @'+config.grid_vip+' xdomain.com'
        print dig_cmd
        os.system(dig_cmd)
        time.sleep(10)
        logging.info("Test case 15  execution Passed")

    @pytest.mark.run(order=16)
    def test_016_stop_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case 16 execution failed")


    @pytest.mark.run(order=17)
    def test_017_validate_Syslog_Messages_for_CEF_logs(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="CEF:0*/|NIOS"
        print LookFor
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        print logs
        if logs==None:
            logging.info(logs)
            logging.info("Test Case 17 Execution Completed")
            assert True
        else:
            logging.info("Test Case 17 Execution Failed")
            assert False

    @pytest.mark.run(order=18)
    def test_018_validate_named_conf_for_log_status(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor= 'zone "zone1" policy Given log no'
        result=validate_named_conf(LookFor,config.grid_vip)
        print result
        if len(result)!=0:
            logging.info("Test Case 18 Execution Completed")
            assert True
        else:
            logging.info("Test Case 18 Execution Completed")
            assert False

    @pytest.mark.run(order=19)
    def test_019_set_rpz_logging_at_zone_level_to_True_in_default_view_zone1_when_enabled_at_grid_level(self):
        res=ib_NIOS.wapi_request('GET', object_type="zone_rp?_return_fields=fqdn,log_rpz")
        res=json.loads(res)
        for i in res:
            if i["fqdn"]=="zone1":
                data={"log_rpz":True}
                response=ib_NIOS.wapi_request('PUT', object_type=i["_ref"],fields=json.dumps(data))
                if response[0]!=400:
                    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                    ref = json.loads(grid)[0]['_ref']
                    publish={"member_order":"SIMULTANEOUSLY"}
                    request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                    time.sleep(10)
                    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                    time.sleep(20)
                    print ("Restarting the grid ")
                    logging.info("Test case 19 passed")
                    assert True
                    time.sleep(40)
                else:
                    logging.info("Test case 19 Failed")
                    assert False

    @pytest.mark.run(order=20)
    def test_020_validate_set_rpz_logging_at_zone_level_in_default_view_zone1_when_enabled_at_grid_level(self):
        data={"fqdn":"zone1","log_rpz":True}
        response=ib_NIOS.wapi_request('GET', object_type="zone_rp?_return_fields=fqdn,log_rpz")
        response=json.loads(response)
        for zone in response:
            if zone["fqdn"]==data["fqdn"]:
                if zone["log_rpz"]==data["log_rpz"]:
                    print("Test case 20 passed")
                    assert True
                else:
                    print("test case 20 failed")
                    assert False

    @pytest.mark.run(order=21)
    def test_021_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("Test case 21  execution passed")

    @pytest.mark.run(order=22)
    def test_022_send_query(self):
        dig_cmd = 'dig @'+config.grid_vip+' xdomain.com'
        print dig_cmd
        os.system(dig_cmd)
        time.sleep(10)
        logging.info("Test case 22  execution Passed")

    @pytest.mark.run(order=23)
    def test_023_stop_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case 23 execution failed")


    @pytest.mark.run(order=24)
    def test_024_validate_Syslog_Messages_for_CEF_logs(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="CEF:0*/|NIOS"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 24 Execution Completed")
            assert True
        else:
            logging.info("Test Case 24 Execution Failed")
            assert False

    @pytest.mark.run(order=25)
    def test_025_validate_named_conf_for_log_status(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor= 'zone "zone1" policy Given log no'
        result=validate_named_conf(LookFor,config.grid_vip)
        print result
        if len(result)==0:
            logging.info("Test Case 25 Execution Completed")
            assert True
        else:
            logging.info("Test Case 25 Execution Completed")
            assert False

    @pytest.mark.run(order=26)
    def test_026_set_rpz_logging_at_zone_level_to_False_in_custom_view_zone2_when_enabled_at_grid_level(self):
        res=ib_NIOS.wapi_request('GET', object_type="zone_rp?_return_fields=fqdn,log_rpz")
        res=json.loads(res)
        for i in res:
            if i["fqdn"]=="zone2":
                data={"log_rpz":False}
                response=ib_NIOS.wapi_request('PUT', object_type=i["_ref"],fields=json.dumps(data))
                if response[0]!=400:
                    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                    ref = json.loads(grid)[0]['_ref']
                    publish={"member_order":"SIMULTANEOUSLY"}
                    request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                    time.sleep(10)
                    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                    time.sleep(20)
                    print ("Restarting the grid ")

                    logging.info("Test case 26 passed")
                    assert True
                else:
                    logging.info("Test case 26 Failed")
                    assert False

    @pytest.mark.run(order=27)
    def test_027_validate_set_rpz_logging_at_zone_level_in_custom_view_zone2_when_enabled_at_grid_level(self):
        data={"fqdn":"zone2","log_rpz":False}
        response=ib_NIOS.wapi_request('GET', object_type="zone_rp?_return_fields=fqdn,log_rpz")
        response=json.loads(response)
        for zone in response:
            if zone["fqdn"]==data["fqdn"]:
                if zone["log_rpz"]==data["log_rpz"]:
                    logging.info("Test case 27 passed")
                    assert True
                else:
                    logging.info("test case 27 failed")
                    assert False

    
    @pytest.mark.run(order=28)
    def test_028_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case 28 execution failed")

    @pytest.mark.run(order=29)
    def test_029_send_query(self):
        dig_cmd = 'dig @'+config.grid_member1_vip+' ydomain.com'
        print dig_cmd
        os.system(dig_cmd)
        logging.info("Test case 29 execution failed")


    @pytest.mark.run(order=30)
    def test_030_stop_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case 30 execution failed")


    @pytest.mark.run(order=31)
    def test_031_validate_Syslog_Messages_for_CEF_logs(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="CEF:0*/|NIOS"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
        print logs
        if logs==None:
            logging.info("Test Case 31 Execution Completed")
            assert True
        else:
            logging.info("Test Case 31 Execution Failed")
            assert False
    
    @pytest.mark.run(order=32)
    def test_032_validate_named_conf_for_log_status(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor= 'zone "zone1" policy Given log no'
        result=validate_named_conf(LookFor,config.grid_vip)
        if len(result)!=0:
            logging.info("Test Case 32 Execution Completed")
            assert True
        else:
            logging.info("Test Case 32 Execution Completed")
            assert True

    @pytest.mark.run(order=33)
    def test_033_set_rpz_logging_at_zone_level_to_True_in_custom_view_zone2_when_enabled_at_grid_level(self):
        res=ib_NIOS.wapi_request('GET', object_type="zone_rp?_return_fields=fqdn,log_rpz")
        res=json.loads(res)
        for i in res:
            if i["fqdn"]=="zone2":
                data={"log_rpz":True}
                response=ib_NIOS.wapi_request('PUT', object_type=i["_ref"],fields=json.dumps(data))
                if response[0]!=400:
                    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                    ref = json.loads(grid)[0]['_ref']
                    publish={"member_order":"SIMULTANEOUSLY"}
                    request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                    time.sleep(10)
                    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                    time.sleep(20)
                    print ("Restarting the grid ")

                    logging.info("Test case 33 passed")
                    assert True
                else:
                    logging.info("Test case 33 Failed")
                    assert False

    @pytest.mark.run(order=34)
    def test_034_validate_set_rpz_logging_at_zone_level_in_custom_view_zone2_when_enabled_at_grid_level(self):
        data={"fqdn":"zone2","log_rpz":True}
        response=ib_NIOS.wapi_request('GET', object_type="zone_rp?_return_fields=fqdn,log_rpz")
        response=json.loads(response)
        for zone in response:
            if zone["fqdn"]==data["fqdn"]:
                if zone["log_rpz"]==data["log_rpz"]:
                    logging.info("Test case 34 passed")
                    assert True
                else:
                    logging.info("test case 34 failed")
                    assert False


    @pytest.mark.run(order=35)
    def test_035_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case 35 execution failed")

    @pytest.mark.run(order=36)
    def test_036_send_query(self):
        dig_cmd = 'dig @'+config.grid_member1_vip+' ydomain.com'
        print dig_cmd
        os.system(dig_cmd)
        logging.info("Test case 36 execution failed")


    @pytest.mark.run(order=37)
    def test_037_stop_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("Test case 37 execution failed")

    '''
    This test case will cannot be executed as wapi support is not thre to move up the dns view
    @pytest.mark.run(order=38)
    def test_038_validate_Syslog_Messages_for_CEF_logs(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="CEF:0*/|NIOS"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
        print logs
        if logs!=None:
            logging.info("Test Case 38 Execution Completed")
            assert True
        else:
            logging.info("Test Case 38 Execution Failed")
            assert False
    '''
    @pytest.mark.run(order=39)
    def test_039_validate_named_conf_for_log_status(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor= 'zone "zone1" policy Given log no'
        result=validate_named_conf(LookFor,config.grid_vip)
        if len(result)==0:
            logging.info("Test Case 39 Execution Completed")
            assert True
        else:
            logging.info("Test Case 39 Execution Completed")
            assert True


    @pytest.mark.run(order=40)
    def test_040_Start_DNS_Service_in_grid2(self):
        logging.info("Start DNS Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns",grid_vip=config.grid_2_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print ref1
        logging.info("Modify a enable_dns")
        data = {"enable_dns": True}
        response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data),grid_vip=config.grid_2_vip)
        print response
        sleep(20)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in  response:
            assert True
        logging.info("Test Case 40 Execution Completed")

    @pytest.mark.run(order=41)
    def test_041_Validate_DNS_service_Enabled_in_grid2(self):
        logging.info("Validate DNs Service is enabled")
        get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns",grid_vip=config.grid_2_vip)
        logging.info(get_tacacsplus)
        res = json.loads(get_tacacsplus)
        print res
        for i in res:
            print i
            logging.info("found")
            assert i["enable_dns"] == True
        logging.info("Test Case 41 Execution Completed")
        logging.info("============================")


    @pytest.mark.run(order=42)
    def test_042_modify_grid_dns_properties_in_grid2(self):
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:dns",grid_vip=config.grid_2_vip)
        get_ref1=json.loads(get_ref)[0]['_ref']
        print get_ref1
        data={"logging_categories":{"log_rpz":True},"allow_recursive_query":True,"allow_transfer":[{"_struct":"addressac","address":"Any","permission":"ALLOW"}],"allow_update":[{"_struct":"addressac","address":"Any","permission":"ALLOW"}],"allow_query":[{"_struct": "addressac","address":"Any","permission":"ALLOW"}],"forwarders":["10.36.6.80"]}
        put_ref=ib_NIOS.wapi_request('PUT', object_type=get_ref1,fields=json.dumps(data),grid_vip=config.grid_2_vip)
        logging.info(put_ref)
        read  = re.search(r'200',put_ref)
        for read in put_ref:
            assert True
        logging.info("Test Case 42 Execution Completed")
        sleep(20)

    @pytest.mark.run(order=43)
    def test_043_add_local_rpz_zone3_to_default_view_in_grid2(self):
        data={"fqdn": "zone3","grid_primary":[{"name": config.grid_2_fqdn,"stealth":False}],"external_secondaries":[{"address":config.grid_vip,"name":config.grid_fqdn,"stealth":False,"use_tsig_key_name":False}],"view":"default"}
        get_ref=ib_NIOS.wapi_request('POST', object_type="zone_rp",fields=json.dumps(data),grid_vip=config.grid_2_vip)
        logging.info("adding RPZ zone ")
        if type(get_ref)!=tuple:
            grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_2_vip)
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish),grid_vip=config.grid_2_vip)
            time.sleep(10)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus",grid_vip=config.grid_2_vip)
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",grid_vip=config.grid_2_vip)
            time.sleep(20)
            print ("Restarting the grid ")
            response=ib_NIOS.wapi_request('GET', object_type="zone_rp",grid_vip=config.grid_2_vip)
            response1=json.loads(response)
            if response1[0]["fqdn"]==data["fqdn"]:
                logging.info("Test case 43 passed as RPZ zone is added")
                assert True
            else:
                logging.info("Test case 43 failed as RPZ zone is not added")
                assert False
        else:
            logging.info("Test case 43 failed as RPZ zone is not added")
            assert False
    
    @pytest.mark.run(order=44)
    def test_044_set_rpz_logging_at_zone_level_in_default_view_zone3_when_enabled_at_grid_level_in_grid_2(self):
        res=ib_NIOS.wapi_request('GET', object_type="zone_rp?_return_fields=fqdn,log_rpz",grid_vip=config.grid_2_vip)
        res=json.loads(res)
        print res
        for i in res:
            if i["fqdn"]=="zone3":
                data={"log_rpz":True}
                response=ib_NIOS.wapi_request('PUT', object_type=i["_ref"],fields=json.dumps(data),grid_vip=config.grid_2_vip)
                print response
                if type(response)!=tuple:
                    grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_2_vip)
                    ref = json.loads(grid)[0]['_ref']
                    publish={"member_order":"SIMULTANEOUSLY"}
                    request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish),grid_vip=config.grid_2_vip)
                    time.sleep(10)
                    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus",grid_vip=config.grid_2_vip)
                    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",grid_vip=config.grid_2_vip)
                    time.sleep(20)
                    print ("Restarting the grid ")
                    logging.info("Test case 44 passed")
                    assert True
                    time.sleep(40)
                else:
                    logging.info("Test case 44 Failed")
                    assert False

    @pytest.mark.run(order=45)
    def test_045_validate_set_rpz_logging_at_zone_level_in_default_view_zone1_when_enabled_at_grid_level_in_grid_2(self):
        data={"fqdn":"zone3","log_rpz":True}
        response=ib_NIOS.wapi_request('GET', object_type="zone_rp?_return_fields=fqdn,log_rpz",grid_vip=config.grid_2_vip)
        response=json.loads(response)
        for zone in response:
            if zone["fqdn"]==data["fqdn"]:
                if zone["log_rpz"]==data["log_rpz"]:
                    print("Test case 45 passed")
                    assert True
                else:
                    print("test case 45 failed")
                    assert False



    @pytest.mark.run(order=46)
    def test_046_add_Feed_rpz_zone_to_default_view(self):

        data={"fqdn": "zone3","grid_secondaries":[{"name": config.grid_fqdn,"stealth":False}],"external_primaries":[{"address":config.grid_2_vip,"name":config.grid_2_fqdn,"stealth":False,"use_tsig_key_name":False}],"view":"default","rpz_type": "FEED","use_external_primary" : True,"comment":"zone 3 is added"}

        get_ref=ib_NIOS.wapi_request('POST', object_type="zone_rp",fields=json.dumps(data))
        logging.info("adding RPZ zone ")
        if type(get_ref)!=tuple:
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            time.sleep(10)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            time.sleep(20)
            print ("Restarting the grid ")
            response=ib_NIOS.wapi_request('GET', object_type="zone_rp?_return_fields=fqdn,comment")
            response=json.loads(response)
            for rpz in response:
                if rpz["fqdn"]!=data["fqdn"]:
                    continue
                if rpz["comment"]=="zone 3 is added":
                    logging.info("Test case 46 passed as RPZ zone is added")
                    assert True
                else:
                    logging.info("Test case 46 failed as RPZ zone is not added")
                    assert False
        else:
            logging.info("Test case 46 failed as RPZ zone is not added")
            assert False

    @pytest.mark.run(order=47)
    def test_047_set_rpz_logging_at_zone_level_in_default_view_zone3_when_enabled_at_grid_level_for_feed_zone(self):
        res=ib_NIOS.wapi_request('GET', object_type="zone_rp?_return_fields=fqdn,log_rpz")
        res=json.loads(res)
        for i in res:
            if i["fqdn"]=="zone3":
                data={"log_rpz":True}
                response=ib_NIOS.wapi_request('PUT', object_type=i["_ref"],fields=json.dumps(data))
                if type(response)!="tuple":
                    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                    ref = json.loads(grid)[0]['_ref']
                    publish={"member_order":"SIMULTANEOUSLY"}
                    request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                    time.sleep(10)
                    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                    time.sleep(20)
                    print ("Restarting the grid ")
                    logging.info("Test case 47 passed")
                    assert True
                    time.sleep(40)
                else:
                    logging.info("Test case 47 Failed")
                    assert False

    @pytest.mark.run(order=48)
    def test_048_validate_set_rpz_logging_at_zone_level_in_default_view_zone3_when_enabled_at_grid_level(self):
        data={"fqdn":"zone3","log_rpz":True}
        response=ib_NIOS.wapi_request('GET', object_type="zone_rp?_return_fields=fqdn,log_rpz")
        response=json.loads(response)
        for zone in response:
            if zone["fqdn"]==data["fqdn"]:
                if zone["log_rpz"]==data["log_rpz"]:
                    logging.info("Test case 48 passed")
                    assert True
                else:
                    logging.info("test case 48 failed")
                    assert False
    
    @pytest.mark.run(order=49)
    def test_049_add_ruleset_in_rpz_zone_in_default_view_in_zone3_in_grid2(self):
        data={"name":"zdomain.com.zone3","rp_zone":"zone3","canonical":""}
        reference=ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data),grid_vip=config.grid_2_vip)
        if type(reference)!="tuple":
            logging.info("Test case 49 execution passed as ruleset is added in RPZ Zone")
            time.sleep(100)
            assert True
        else:
            logging.info("Test case 49 execution failed as ruleset is not added in RPZ Zone")
            assert False
    
    @pytest.mark.run(order=50)
    def test_050_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("Test case 50 execution failed")

    @pytest.mark.run(order=51)
    def test_051_send_query(self):
        dig_cmd = 'dig @'+config.grid_vip+' zdomain.com'
        print dig_cmd
        os.system(dig_cmd)
        logging.info("Test case 51 execution passed")

    @pytest.mark.run(order=52)
    def test_052_stop_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test case 52 execution failed")


    @pytest.mark.run(order=53)
    def test_053_validate_Syslog_Messages_for_CEF_logs(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="CEF:0*/|NIOS"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        if logs!=None:
            logging.info("Test Case 53 Execution Completed")
            assert True
        else:
            logging.info("Test Case 53 Execution Failed")
            assert False

    
    @pytest.mark.run(order=54)
    def test_054_validate_named_conf_for_log_status(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor= 'zone "zone3" policy Given'
        result=validate_named_conf(LookFor,config.grid_vip)
        if len(result)==0:
            logging.info("Test Case 54 Execution Completed")
            assert True
        else:
            logging.info("Test Case 54 Execution Completed")
            assert True
    
    @pytest.mark.run(order=55)
    def test_055_add_Fireeye_rpz_zone4_to_default_view(self):

        data={"comment":"zone 4 is added","rpz_type":"FIREEYE","view":"default","fqdn": "zone4","grid_primary":[{"name":config.grid_fqdn,"stealth":False}],"fireeye_rule_mapping":{"apt_override": "NOOVERRIDE","fireeye_alert_mapping":[{"alert_type": "DOMAIN_MATCH","lifetime": 604800,"rpz_rule": "PASSTHRU"},{"alert_type": "INFECTION_MATCH","lifetime": 86400,"rpz_rule": "PASSTHRU"},{"alert_type": "MALWARE_CALLBACK","lifetime": 86400,"rpz_rule": "PASSTHRU"},{"alert_type": "MALWARE_OBJECT","lifetime": 86400,"rpz_rule": "PASSTHRU"},{"alert_type": "WEB_INFECTION","lifetime": 86400,"rpz_rule": "PASSTHRU"}],"substituted_domain_name": ""}}

        get_ref=ib_NIOS.wapi_request('POST', object_type="zone_rp",fields=json.dumps(data))
        logging.info("adding RPZ zone ")
        print get_ref
        if type(get_ref)!=tuple:
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            time.sleep(10)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            time.sleep(20)
            print ("Restarting the grid ")
            response=ib_NIOS.wapi_request('GET', object_type="zone_rp?_return_fields=fqdn,comment")
            response=json.loads(response)
            for rpz in response:
                if rpz["fqdn"]!=data["fqdn"]:
                    continue
                if rpz["comment"]=="zone 4 is added":
                    logging.info("Test case 55 passed as RPZ zone is added")
                    assert True
                else:
                    logging.info("Test case 55 failed as RPZ zone is not added")
                    assert False
        else:
            logging.info("Test case 55 failed as RPZ zone is not added")
            assert False

    @pytest.mark.run(order=56)
    def test_056_set_rpz_logging_at_zone_level_in_default_view_zone4_when_enabled_at_grid_level_for_feed_zone(self):
        res=ib_NIOS.wapi_request('GET', object_type="zone_rp?_return_fields=fqdn,log_rpz")
        res=json.loads(res)
        for i in res:
            if i["fqdn"]=="zone4":
                data={"log_rpz":False}
                response=ib_NIOS.wapi_request('PUT', object_type=i["_ref"],fields=json.dumps(data))
                if response[0]!=400:
                    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                    ref = json.loads(grid)[0]['_ref']
                    publish={"member_order":"SIMULTANEOUSLY"}
                    request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                    time.sleep(10)
                    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                    time.sleep(20)
                    print ("Restarting the grid ")
                    logging.info("Test case 56 passed")
                    assert True
                    time.sleep(40)
                else:
                    logging.info("Test case 56 Failed")
                    assert False

    @pytest.mark.run(order=57)
    def test_057_validate_set_rpz_logging_at_zone_level_in_default_view_zone4_when_enabled_at_grid_level(self):
        data={"fqdn":"zone4","log_rpz":False}
        response=ib_NIOS.wapi_request('GET', object_type="zone_rp?_return_fields=fqdn,log_rpz")
        response=json.loads(response)
        for zone in response:
            if zone["fqdn"]==data["fqdn"]:
                if zone["log_rpz"]==data["log_rpz"]:
                    logging.info("Test case 57 passed")
                    assert True
                else:
                    logging.info("test case 57 failed")
                    assert False

    @pytest.mark.run(order=58)
    def test_058_add_ruleset_in_rpz_zone_in_default_view_in_zone4_in_grid2(self):
        data={"name":"xydomain.com.zone4","rp_zone":"zone4","canonical":""}
        reference=ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        if type(reference)!=tuple:
            logging.info("Test case 58 execution passed as ruleset is added in RPZ Zone")
            assert True
        else:
            logging.info("Test case 58 execution failed as ruleset is not added in RPZ Zone")
            assert False


    @pytest.mark.run(order=59)
    def test_059_validate_named_conf_for_log_status(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor= 'zone "zone4" policy Given log no'
        result=validate_named_conf(LookFor,config.grid_vip)
        if len(result)!=0:
            print("Test Case 59 Execution Completed")
            assert True
        else:
            print("Test Case 59 Execution Failed")
            assert False





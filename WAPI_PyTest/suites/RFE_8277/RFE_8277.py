import re
import config
import pytest
import unittest
import logging
import subprocess
import os,sys
import json
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
import commands
import json, ast
import requests
import time
import subprocess

def get_ref_grid():
    get_ref = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
    logging.info(get_ref)
    res = json.loads(get_ref)
    ref1 = json.loads(get_ref)[0]['_ref']
    display_msg(ref1)
    return ref1

def get_ref_member():
    get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
    logging.info(get_ref)
    res = json.loads(get_ref)
    ref1 = json.loads(get_ref)[0]['_ref']
    display_msg(ref1)
    return ref1

def get_dduq_load():
	cmd = "/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part1/dduq/dduq -i "+ config.grid_vip +" -f 200k"
	returned_value = commands.getoutput(cmd)  # returns the exit code in unix
	print('returned value:', returned_value)


def display_msg(x):
    logging.info(x)
    print(x)
    print("\n")
    
class Network(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_001_add_forwarder_and_recursive(self):
        logging.info("start the ipv4 DNS service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        data={"allow_recursive_query":True,"forwarders":["10.39.16.160"]}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        for read in response:
            assert True

    @pytest.mark.run(order=2)
    def test_002_start_IPv4_DNS_service(self):
        logging.info("start the ipv4 DNS service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print ref1
        data = {"enable_dns": True}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        sleep(20)
        logging.info(response)
        logging.info("============================")
        print response

    @pytest.mark.run(order=3)
    def test_003_Enable_Traffic_Capture_without_passing_time(self):
        display_msg("Enable_Traffic_Capture_without_passing_time")
        ref1=get_ref_grid()
        data = {"automated_traffic_capture_setting":{"traffic_capture_enable": True}}
        status, response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        assert status == 400 and re.search(r"Traffic capture duration must be set", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 3 completed Enable_Traffic_Capture_without_passing_time")
        

    @pytest.mark.run(order=4)
    def test_004_Enable_Traffic_Capture_with_more_than_600s(self):
        display_msg("Enable_Traffic_Capture_with_more_than_600s")
        ref1=get_ref_grid()
        data = {"automated_traffic_capture_setting":{"traffic_capture_enable": True,"duration": 3230,"destination":"FTP", "traffic_capture_directory":"asfg","destination_host": "10.120.21.154","username": "abcde", "password":"abcd"}}
        status, response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        assert re.search(r"Traffic capture duration must be in limits 1-600", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 4  complited: Enable_Traffic_Capture_with_more_than_600s")
        
    @pytest.mark.run(order=5)
    def test_005_Enable_Traffic_Capture_with_FTP_without_username(self):
        display_msg("Enable_Traffic_Capture_with_FTP_without_username")
        ref1=get_ref_grid()
        data = {"automated_traffic_capture_setting":{"traffic_capture_enable": True,"duration": 30,"destination":"FTP", "traffic_capture_directory":"asfg","destination_host": "10.120.21.154","username":"", "password":"abcd"}}
        status, response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        assert re.search(r"A username must be set if destination is FTP", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 5  complited: Enable_Traffic_Capture_with_FTP_without_username")
        

    @pytest.mark.run(order=6)
    def test_006_Enable_Traffic_Capture_with_FTP_without_password(self):
        display_msg("Enable_Traffic_Capture_with_FTP_without_password")
        ref1=get_ref_grid()
        data = {"automated_traffic_capture_setting":{"traffic_capture_enable": True,"duration": 30,"destination":"FTP", "traffic_capture_directory":"asfg","destination_host": "10.120.21.154","username":"abcd","password":""}}
        status, response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        display_msg(response)
        assert re.search(r"A password must be set if destination is FTP", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 6 complited: Enable_Traffic_Capture_with_FTP_without_password")
        
    @pytest.mark.run(order=7)
    def test_007_Enable_Traffic_Capture_with_FTP(self):
        display_msg("Enable_Traffic_Capture_with_FTP")
        ref1=get_ref_grid()
        data = {"automated_traffic_capture_setting":{"traffic_capture_enable": True,"duration": 30,"destination":"FTP", "traffic_capture_directory":"asfg","destination_host": "10.120.21.154","username": "abcde","include_support_bundle": False, "keep_local_copy": False,"password":"abcd"}}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        display_msg(response)
        res =ib_NIOS.wapi_request('GET', object_type=ref1 + "?_return_fields=automated_traffic_capture_setting",grid_vip=config.grid_vip)
        res_json=json.loads(res)
        res_json_tcs = res_json['automated_traffic_capture_setting']
        data_tcs=data['automated_traffic_capture_setting']
        data_tcs.pop("password")
        assert res_json_tcs == data_tcs
        display_msg("=="*50)
        display_msg("TEST 7 complited: Enable_Traffic_Capture_with_FTP")

    @pytest.mark.run(order=8)
    def test_008_Enable_Traffic_Capture_with_SCP_without_username(self):
        display_msg("Enable_Traffic_Capture_with_SCP_without_username")
        ref1=get_ref_grid()
        data = {"automated_traffic_capture_setting":{"traffic_capture_enable": True,"duration": 230,"destination":"SCP", "traffic_capture_directory":"asfg","destination_host": "10.120.21.154","username":"", "password":"abcd"}}
        status, response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        assert re.search(r"A username must be set if destination is SCP", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 8  complited: Enable_Traffic_Capture_with_SCP_without_username")
        

    @pytest.mark.run(order=9)
    def test_009_Enable_Traffic_Capture_with_SCP_without_password(self):
        display_msg("Enable_Traffic_Capture_with_SCP_without_password")
        ref1=get_ref_grid()
        data = {"automated_traffic_capture_setting":{"traffic_capture_enable": True,"duration": 230,"destination":"SCP", "traffic_capture_directory":"asfg","destination_host": "10.120.21.154","username":"abcd","password":""}}
        status, response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        display_msg(response)
        assert re.search(r"A password must be set if destination is SCP", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 9 complited: Enable_Traffic_Capture_with_SCP_without_password")
        
    @pytest.mark.run(order=10)
    def test_010_Enable_Traffic_Capture_with_SCP(self):
        display_msg("Enable_Traffic_Capture_with_SCP")
        ref1=get_ref_grid()
        data = {"automated_traffic_capture_setting":{"traffic_capture_enable": True,"duration": 30,"destination":"SCP", "traffic_capture_directory":"asfg","destination_host": "10.120.21.154","include_support_bundle": False, "keep_local_copy": False,"username": "abcde", "password":"abcd"}}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        display_msg(response)
        res =ib_NIOS.wapi_request('GET', object_type=ref1 + "?_return_fields=automated_traffic_capture_setting",grid_vip=config.grid_vip)
        res_json=json.loads(res)
        res_json_tcs = res_json['automated_traffic_capture_setting']
        data_tcs=data['automated_traffic_capture_setting']
        data_tcs_not_pswd=data_tcs.pop("password")
        assert res_json_tcs== data_tcs
        display_msg("=="*50)
        display_msg("TEST 10 complited: Enable_Traffic_Capture_with_SCP")

    @pytest.mark.run(order=11)
    def test_011_Enable_Cache_Hit_Ratio_Trigger_without_passing_anyvalue(self):
        display_msg("Enable_Cache_Hit_Ratio_Trigger_without_passing_anyvalue")
        ref1=get_ref_grid()
        data = {"traffic_capture_chr_setting":{"chr_trigger_enable": True}}
        status, response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        assert status == 400 and re.search(r"A threshold value must be configured if Cache Hit Ratio trigger is enabled", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 11 completed Enable_Cache_Hit_Ratio_Trigger_without_passing_anyvalue")
        

    @pytest.mark.run(order=12)
    def test_012_Enable_Cache_Hit_Ratio_Trigger_with_reset_value_less_thna_threshold(self):
        display_msg("Enable_Cache_Hit_Ratio_Trigger_with_reset_value_less_thna_threshold")
        ref1=get_ref_grid()
        data = {"traffic_capture_chr_setting":{"chr_trigger_enable": True, "chr_threshold":25,"chr_reset":3, "chr_min_cache_utilization":45 }}
        status, response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        assert re.search(r"must be lesser or equal than reset value ", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 12  complited: Enable_Cache_Hit_Ratio_Trigger_with_reset_value_less_thna_threshold")    


    @pytest.mark.run(order=13)
    def test_013_Enable_Queries_Per_Second_Trigger_without_passing_anyvalue(self):
        display_msg("Enable_Queries_Per_Second_Trigger_without_passing_anyvalue")
        ref1=get_ref_grid()
        data = {"traffic_capture_qps_setting":{"qps_trigger_enable": True}}
        status, response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        assert status == 400 and re.search(r"A threshold value must be configured if Queries Per Second trigger is enabled", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 13 completed Enable_Queries_Per_Second_Trigger_without_passing_anyvalue")
        

    @pytest.mark.run(order=14)
    def test_014_Enable_Queries_Per_Second_Trigger_with_threshold_value_more_than_reset_value(self):
        display_msg("Enable_Queries_Per_Second_Trigger_with_threshold_value_more_than_reset_value")
        ref1=get_ref_grid()
        data = {"traffic_capture_qps_setting":{"qps_trigger_enable": True,"qps_threshold":10000,"qps_reset":1001}}
        status, response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        assert re.search(r"must be lesser or equal than reset value", response)
        for read in response:
            assert True
        display_msg("=="*50)
        display_msg("TEST 14 complited: Enable_Queries_Per_Second_Trigger_with_threshold_value_more_than_reset_value")

    @pytest.mark.run(order=15)    
    def test_015_Enable_Queries_Per_Second_Trigger(self):
        display_msg("Enable_Queries_Per_Second_Trigger")
        ref1=get_ref_grid()
        data = {"traffic_capture_qps_setting":{"qps_trigger_enable": True,"qps_threshold":10000,"qps_reset":10001}}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        display_msg(response)
        res =ib_NIOS.wapi_request('GET', object_type=ref1 + "?_return_fields=traffic_capture_qps_setting",grid_vip=config.grid_vip)
        res_json=json.loads(res)
        res_json_qps = res_json["traffic_capture_qps_setting"]
        data_qps=data["traffic_capture_qps_setting"]
        assert res_json_qps== data_qps
        display_msg("=="*50)
        sleep(80)

    @pytest.mark.run(order=16)
    def test_016_validate_log_for_enable_qps(self):
        display_msg("Validate log for enable qps")
        enable_qps_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat /infoblox/var/infoblox.log | grep "kpi_consider_threshold(): Automated traffic capture triggered by hitting Queries per second threshold: threshold.*, current=.*"'
        out1 = commands.getoutput(enable_qps_validation)
        display_msg(out1)
        assert re.search(r"Automated traffic capture triggered by hitting Queries per second threshold: threshold=.*, current=.*",out1)
        logging.info("Test Case 17 Execution Completed")

    @pytest.mark.run(order=17)
    def test_017_disable_Queries_Per_Second_Trigger(self):
        display_msg("disable_Queries_Per_Second_Trigger")
        ref1=get_ref_grid()
        data = {"traffic_capture_qps_setting":{"qps_trigger_enable":False}}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        display_msg(response)
        res =ib_NIOS.wapi_request('GET', object_type=ref1 + "?_return_fields=traffic_capture_qps_setting",grid_vip=config.grid_vip)
        res_json=json.loads(res)
        res_json_qps = res_json["traffic_capture_qps_setting"]
        data_qps=data["traffic_capture_qps_setting"]
        assert res_json_qps["qps_trigger_enable"]== data_qps["qps_trigger_enable"]
        display_msg("=="*50)

    @pytest.mark.run(order=18)
    def test_018_Enable_Cache_Hit_Ratio_Trigger(self):
        display_msg("Enable_Cache_Hit_Ratio_Trigger")
        ref1=get_ref_grid()
        data = {"traffic_capture_chr_setting":{"chr_trigger_enable": True, "chr_threshold":90,"chr_reset":100, "chr_min_cache_utilization":0 }}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        display_msg(response)
        res =ib_NIOS.wapi_request('GET', object_type=ref1 + "?_return_fields=traffic_capture_chr_setting",grid_vip=config.grid_vip)
        res_json=json.loads(res)
        res_json_chr = res_json["traffic_capture_chr_setting"]
        data_chr=data["traffic_capture_chr_setting"]
        assert res_json_chr== data_chr
        display_msg("=="*50)
        display_msg("TEST 18 complited: Enable_Cache_Hit_Ratio_Trigger")
        sleep(30)

    @pytest.mark.run(order=19)
    def test_019_validate_log_for_chr_traffic_capture(self):
	load=get_dduq_load()
	sleep(30)
	'''
        display_msg("Validate log for_chr_traffic_capture")
        enable_qps_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat /infoblox/var/infoblox.log | grep "kpi_consider_threshold(): Automated traffic capture triggered by hitting Cache Hit Ratio threshold: cache utilization=.*, threshold=.*, current=.*"'
        out1 = commands.getoutput(enable_qps_validation)
        display_msg(out1)
        assert re.search(r"Automated traffic capture triggered by hitting Cache Hit Ratio threshold: cache utilization=.*, threshold=.*, current=.*",out1)
        logging.info("Test Case 20  Execution Completed")
        ref1=get_ref_grid()
        data = {"traffic_capture_chr_setting":{"chr_trigger_enable": False }}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        display_msg(response)
	'''
                                                
    @pytest.mark.run(order=20)
    def test_020_Enable_Traffic_Capture_with_FTP_member_level(self):
        display_msg("Enable_Traffic_Capture_with_FTP")
        ref1=get_ref_member()
        data = {"automated_traffic_capture_setting":{"traffic_capture_enable": True,"duration": 30,"destination":"FTP", "traffic_capture_directory":"asfg","destination_host": "10.120.21.154","username": "abcde","include_support_bundle": False, "keep_local_copy": True,"password":"abcd"}}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        display_msg(response)
        res =ib_NIOS.wapi_request('GET', object_type=ref1 + "?_return_fields=automated_traffic_capture_setting",grid_vip=config.grid_vip)
        res_json=json.loads(res)
        res_json_tcs = res_json['automated_traffic_capture_setting']
        data_tcs=data['automated_traffic_capture_setting']
        data_tcs.pop("password")
        assert res_json_tcs == data_tcs
        display_msg("=="*50)
        grid=ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data))
        logging.info("Wait for 20 sec.,")
        sleep(20)
        display_msg("TEST 21 complited: Enable_Traffic_Capture_with_FTP")
        
    @pytest.mark.run(order=21)
    def test_021_Enable_Queries_Per_Second_Trigger_member_level(self):  
        display_msg("Enable_Queries_Per_Second_Trigger")
        ref1=get_ref_member()
        data = {"traffic_capture_qps_setting":{"qps_trigger_enable": True,"qps_threshold":9800,"qps_reset":10000}}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        display_msg(response)
        res =ib_NIOS.wapi_request('GET', object_type=ref1 + "?_return_fields=traffic_capture_qps_setting",grid_vip=config.grid_vip)
        res_json=json.loads(res)
        res_json_qps = res_json["traffic_capture_qps_setting"]
        data_qps=data["traffic_capture_qps_setting"]
        assert res_json_qps== data_qps
        display_msg("=="*50)
        sleep(80)
        display_msg("TEST 222 complited: Enable_Cache_Hit_Ratio_Trigger")

    @pytest.mark.run(order=22)
    def test_022_validate_log_for_enable_qps_member_level(self):
        display_msg("Validate log for enable qps")
        enable_qps_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat /infoblox/var/infoblox.log | grep "Automated traffic capture triggered by hitting Queries per second threshold: threshold=.*, current=.*"'
        out1 = commands.getoutput(enable_qps_validation)
        display_msg(out1)
        assert re.search(r"Automated traffic capture triggered by hitting Queries per second threshold: threshold=9800, current=.*",out1)
        logging.info("Test Case 17 Execution Completed")

    @pytest.mark.run(order=23)
    def test_023_disable_Queries_Per_Second_Trigger_member_level(self):
        display_msg("disable_Queries_Per_Second_Trigger")
        ref1=get_ref_member()
        data = {"traffic_capture_qps_setting":{"qps_trigger_enable":False}}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        display_msg(response)
        res =ib_NIOS.wapi_request('GET', object_type=ref1 + "?_return_fields=traffic_capture_qps_setting",grid_vip=config.grid_vip)
        res_json=json.loads(res)
        res_json_qps = res_json["traffic_capture_qps_setting"]
        data_qps=data["traffic_capture_qps_setting"]
        assert res_json_qps["qps_trigger_enable"]== data_qps["qps_trigger_enable"]
        display_msg("=="*50)

    @pytest.mark.run(order=24)
    def test_024_Enable_Cache_Hit_Ratio_Trigger_member_level(self):
        display_msg("Enable_Cache_Hit_Ratio_Trigger")
        ref1=get_ref_member()
        data = {"traffic_capture_chr_setting":{"chr_trigger_enable": True, "chr_threshold":91,"chr_reset":100, "chr_min_cache_utilization":0 }}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        display_msg(response)
        res =ib_NIOS.wapi_request('GET', object_type=ref1 + "?_return_fields=traffic_capture_chr_setting",grid_vip=config.grid_vip)
        res_json=json.loads(res)
        res_json_chr = res_json["traffic_capture_chr_setting"]
        data_chr=data["traffic_capture_chr_setting"]
        assert res_json_chr== data_chr
        display_msg("=="*50)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data))
        logging.info("Wait for 20 sec.,")
        sleep(50) 
        display_msg("TEST 24 complited: Enable_Cache_Hit_Ratio_Trigger")

    @pytest.mark.run(order=25)
    def test_025_validate_log_for_chr_traffic_capture_member_level(self):
	load=get_dduq_load()
	sleep(30)
        display_msg("Validate log for_chr_traffic_capture")
        enable_qps_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat  /infoblox/var/infoblox.log | grep "Automated traffic capture triggered by hitting Cache Hit Ratio threshold: cache utilization=.*, threshold=.*, current=.*"'
        out1 = commands.getoutput(enable_qps_validation)
        display_msg(out1)
        assert re.search(r"Automated traffic capture triggered by hitting Cache Hit Ratio threshold: cache utilization=.*, threshold=91, current=.*",out1)
        logging.info("Test Case 25 Execution Completed")
    	    
    
    @pytest.mark.run(order=26)
    def test_026_validate_if_traffic_cap_stored_in_retained_captured(self):
        import paramiko

        output = {}
        output['err'] = []
        output['out'] = []

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(
                        paramiko.AutoAddPolicy())
        client.connect(str(config.grid_vip), username="root")
        cmd = "cd /storage/kpi_traffic_capture_room/;tar -xzvf $(ls -Atr *gz | tail -1)"
        stdin, stdout, stderr = client.exec_command(cmd)
        err = stderr.readlines()
        out = stdout.readlines()

        output['err'] = err
        output['out'] = out

        if not output['err']:
            assert output['out'][0].strip('\n') == "traffic.cap"
        else:
            raise Exception(err)

 
    @pytest.mark.run(order=27)
    def test_027_validate_invalid_argument(self):
        validation_invalid_argument_infoblox = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat  /infoblox/var/infoblox.log   /var/log/syslog | grep "Invalid argument"'     
        out1 = commands.getoutput(validation_invalid_argument_infoblox)
        
        display_msg(out1)
        search = re.search("Invalid argument",out1)
        if search:
            print search.group()
            raise Exception("Invalid argument is present in logs")


    @pytest.mark.run(order=28)
    def test_028_validate_if_traffic_cap_is_readable_OR_not(self):
        import paramiko

        output = {}
        output['err'] = []
        output['out'] = []

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(
                        paramiko.AutoAddPolicy())
        client.connect(str(config.grid_vip), username="root")
        cmd = "cd /storage/kpi_traffic_capture_room/ ; tcpdump -i any -vvvvn -r traffic.cap | grep 'ARP' "
        stdin, stdout, stderr = client.exec_command(cmd)
        err = stderr.readlines()
        out = stdout.readlines()

        #output['err'] = err
        output['out'] = out
	#print err
	#print out
	count=0
        for line in out:
                if re.search(r'.*ARP.*',line):
                        count=count+1
        print count
        if count is 0:
                raise Exception("ARP is not found in traffic cap file")



    @pytest.mark.run(order=29)
    def test_029_validate_log_after_disabling_the_QPS(self):
        display_msg("Validate log after disabling the QPS")
        enable_qps_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' cat  /infoblox/var/infoblox.log | grep "Automated traffic capture triggered off due to configuration change"'
        out1 = commands.getoutput(enable_qps_validation)
        display_msg(out1)
        assert re.search(r"Automated traffic capture triggered off due to configuration change",out1)
        logging.info("Test Case 29 Execution Completed")
	

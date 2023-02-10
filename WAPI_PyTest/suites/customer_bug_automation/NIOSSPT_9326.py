__author__ = "Aditya G"
__email__  = "adityag@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master + Member                                                             #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415),DTC                                  #
########################################################################################


import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
import commands
import json, ast
import time
import getpass
import sys
import pexpect
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv


logging.basicConfig(filename='niosspt9326.log', filemode='w', level=logging.DEBUG)


class NIOSSPT_9326(unittest.TestCase):
    @pytest.mark.order(order=1)
    def test001_create_zone(self):
        logging.info("Creating zone abc.com")
        data={"fqdn":"abc.com","view":"default","grid_primary":[{"name": config.grid_fqdn,"stealth": False}],"grid_secondaries": [{"name": config.grid_member1_fqdn,"stealth": False,"grid_replicate": True,"enable_preferred_primaries": False,"preferred_primaries": []}]}
        zone_ref=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        logging.info(zone_ref)
        if bool(re.match("\"zone_auth*.",str(zone_ref))):
            logging.info("abc.com created succesfully")
            logging.info("Restart services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            sleep(20)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            sleep(20)

        else:
            raise Exception("abc.com creation unsuccessful")

    @pytest.mark.order(order=2)
    def test002_dtc_server1(self):
        logging.info("Creating dtc server1")
        data={"host": config.grid_vip,"monitors": [{"host": config.grid_vip,"monitor": "dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"}],"name": "server1"}
        server1_ref=ib_NIOS.wapi_request('POST',object_type='dtc:server',fields=json.dumps(data))
        logging.info(server1_ref)
        if bool(re.match("\"dtc:server*.",str(server1_ref))):
            logging.info("dtc server1 created succesfully")
	else:
            raise Exception("dtc server1 creation unsuccessful")

    @pytest.mark.order(order=3)
    def test003_dtc_server2(self):
        logging.info("Creating dtc server2")
        data={"host": config.grid_member1_vip,"monitors": [{"host": config.grid_member1_vip,"monitor": "dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"}],"name": "server2"}
        server2_ref=ib_NIOS.wapi_request('POST',object_type='dtc:server',fields=json.dumps(data))
        logging.info(server2_ref)
        if bool(re.match("\"dtc:server*.",str(server2_ref))):
            logging.info("dtc server2 created succesfully")
	else:
            raise Exception("dtc server2 creation unsuccessful")

    @pytest.mark.order(order=4)
    def test004_dtc_pool(self):
        logging.info("Creating dtc pool")
        server=ib_NIOS.wapi_request('GET',object_type='dtc:server')
        server1=json.loads(server)[0]['_ref']
        server2=json.loads(server)[1]['_ref']
        data={"name": "pool","lb_preferred_method": "ROUND_ROBIN","monitors": ["dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"],"servers": [{"ratio": 1,"server": server1},{"ratio": 1,"server": server2}]}
        pool_ref=ib_NIOS.wapi_request('POST',object_type='dtc:pool',fields=json.dumps(data))
        logging.info(pool_ref)
        if bool(re.match("\"dtc:pool*.",str(pool_ref))):
            logging.info("pool created succesfully")
	else:
            raise Exception("pool creation unsuccessful")


    @pytest.mark.order(order=5)
    def test005_dtc_lbdn(self):
        logging.info("Creating lbdn")
        sleep(10)
        zone=ib_NIOS.wapi_request('GET',object_type='zone_auth', params="?fqdn=abc.com")
        print(zone)
        zone_ref=json.loads(zone)[0]['_ref']
        pool=ib_NIOS.wapi_request('GET',object_type='dtc:pool')
        pool_ref=json.loads(pool)[0]['_ref']
        data={"name": "lbdn1","lb_method": "ROUND_ROBIN","patterns": ["b2.abc.com"],"auth_zones": [zone_ref],"pools": [{"pool": pool_ref,"ratio": 1}]}
        lbdn_ref=ib_NIOS.wapi_request('POST',object_type='dtc:lbdn',fields=json.dumps(data))
        print(lbdn_ref)
        logging.info(lbdn_ref)
        if bool(re.match("\"dtc:lbdn*.",str(lbdn_ref))):
            logging.info("lbdn created succesfully")
            logging.info("Restart services")
	    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
    	    ref = json.loads(grid)[0]['_ref']
    	    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    	    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
    	    sleep(20)
	    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
            ref = json.loads(grid)[0]['_ref']
            data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_member1_vip)
            sleep(20)
	else:
            raise Exception("lbdn creation unsuccessful")
    @pytest.mark.run(order=6)
    def test006_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 6 passed")
    

    @pytest.mark.order(order=7)
    def test007_verify_round_robin(self):
        logging.info("Verifying round robin")
        sleep(20)
        ip='@'+config.grid_vip
        validation1=config.grid_vip
        validation2=config.grid_member1_vip
        output=subprocess.check_output(['dig',ip,'b2.abc.com','in','a'])
        logging.info(output)
        if validation1 in output:
            logging.info("Validation1 successful")
            sleep(5)
        else:
            raise Exception("Incorrect dig output")
        output2=subprocess.check_output(['dig',ip,'b2.abc.com','in','a'])
        logging.info(output2)
        if validation2 in output2:
            logging.info("Validation2successful")
        else:
            raise Exception("Incorrect dig output")
        logging.info("Round robin validation succesfull")

    @pytest.mark.run(order=8)
    def test008_stop_Syslog_Messages_logs(self):
	sleep(20)
        logging.info("Starting Syslog Messages Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        log("stop","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 8 passed")

    @pytest.mark.run(order=9)
    def test009_validate_var_log_Messages_for_master(self):
        logging.info("Validating Sylog Messages Logs")
        validate_msg = "IN A "+config.grid_vip
        logs=logv(validate_msg,"/var/log/syslog",config.grid_vip)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 9 Execution Completed")
            assert True
        else:
            logging.info("Test Case 9 Execution Failed")
            assert False
    
    @pytest.mark.run(order=9)
    def test010_validate_sys_log_Messages_for_member(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="IN A "+config.grid_member1_vip
	print LookFor
	logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 10 Execution Completed")
            assert True
        else:
            logging.info("Test Case 10 Execution Failed")
            assert False


    @pytest.mark.order(order=11)
    def test011_test_cleanup(self):
        logging.info("Starting cleanup")

        lbdn=ib_NIOS.wapi_request('GET',object_type='dtc:lbdn')
        lbdn_ref=json.loads(lbdn)[0]['_ref']
        del_lbdn=ib_NIOS.wapi_request('DELETE',ref=lbdn_ref)

        pool=ib_NIOS.wapi_request('GET',object_type='dtc:pool')
        pool_ref=json.loads(pool)[0]['_ref']
        del_pool=ib_NIOS.wapi_request('DELETE',ref=pool_ref)

        server=ib_NIOS.wapi_request('GET',object_type='dtc:server')
        server1=json.loads(server)[0]['_ref']
        server2=json.loads(server)[1]['_ref']
        del_server2=ib_NIOS.wapi_request('DELETE',ref=server2)
        del_server1=ib_NIOS.wapi_request('DELETE',ref=server1)

        zone=ib_NIOS.wapi_request('GET',object_type='zone_auth', params="?fqdn=abc.com")
        zone_ref=json.loads(zone)[0]['_ref']
        del_zone=ib_NIOS.wapi_request('DELETE',ref=zone_ref)


        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(5)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(5)





















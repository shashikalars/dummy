__author__ = "Aditya G"
__email__  = "adityag@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master + Reporting                                                          #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415),RPZ                                  #
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
import ib_utils.common_utilities as ib_TOKEN
from time import sleep
import commands
import json, ast
import time
import getpass
import sys
import pexpect


logging.basicConfig(filename='niosspt9255.log', filemode='w', level=logging.DEBUG)
client1="10.36.198.7"
client2="10.36.198.8"
user_client1="root"
user_client2="root"


class NIOSSPT_9255(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test001_enable_logging_and_recursive_query(self):
        logging.info("Fetching the reference of grid dns properties")
        ref_grid_dns = ib_NIOS.wapi_request('GET',object_type="grid:dns")
        logging.info(ref_grid_dns)
        ref_gd=json.loads(ref_grid_dns)[0]['_ref']
        logging.info("Enabling recursive queries and logging for rpz")
        data={"allow_recursive_query": True,"logging_categories": {"log_rpz": True,"log_queries": True,"log_responses": True}}
        ref_changed_properties = ib_NIOS.wapi_request('PUT',ref=ref_gd,fields=json.dumps(data),grid_vip=config.grid_vip)
        logging.info(ref_changed_properties)
        if bool(re.match("\"grid:dns*.",str(ref_changed_properties))):
            logging.info("Properties changed successfully")
        else:
            raise Exception("Unable to enable the recursive queries and logging for rpz")


    @pytest.mark.run(order=2)
    def test002_create_rpz_zone(self):
        logging.info("Creating a rpz zone")
        data={"fqdn": "rpz.com","view": "default","grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        rpz_zone_ref=ib_NIOS.wapi_request('POST',fields=json.dumps(data),object_type="zone_rp")
        logging.info(rpz_zone_ref)
        if bool(re.match("\"zone_rp*.",str(rpz_zone_ref))):
            logging.info("Zone created successfully")
            logging.info("Restart services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            sleep(5)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            sleep(5)
        else:
            raise Exception("RPZ zone creation failed")


    @pytest.mark.run(order=3)
    def test003_add_block_domain(self):
        logging.info("Creating block domain")
        logging.info("Creating block domain yahoo.com")
        data={"name": "yahoo.com.rpz.com","view": "default","canonical": "","rp_zone": "rpz.com"}
        ref_bd_1=ib_NIOS.wapi_request('POST',fields=json.dumps(data),object_type="record:rpz:cname")
        logging.info(ref_bd_1)
        if bool(re.match("\"record:rpz:cname*.",str(ref_bd_1))):
            logging.info("bd yahoo.com created successfully")
        else:
            raise Exception("bd creation unsuccessful")
        logging.info("Creating block domain abc.com")
        data={"name": "abc.com.rpz.com","view": "default","canonical": "","rp_zone": "rpz.com"}
        ref_bd_2=ib_NIOS.wapi_request('POST',fields=json.dumps(data),object_type="record:rpz:cname")
        logging.info(ref_bd_2)
        if bool(re.match("\"record:rpz:cname*.",str(ref_bd_2))):
            logging.info("bd abc.com created successfully")
            logging.info("Restart services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            sleep(5)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            sleep(5)
        else:
            raise Exception("bd creation unsuccessful")

    @pytest.mark.run(order=4)
    def test004_hit_rpz_rules_from_different_clients(self):
        logging.info("Entering client 1")
        c=pexpect.spawn('ssh -o StrictHostKeyChecking=no %s@%s' % (user_client1,client1))
        c.expect("password: ",timeout=30)
        c.sendline("infoblox")
        c.expect(["~\]# ","~\]$ "])
        c.sendline("dig @"+config.grid_vip+" yahoo.com")
        sleep(2)
        c.expect(["~\]# ","~\]$ "])
        c.sendline("dig @"+config.grid_vip+" abc.com")
        sleep(2)
        c.close()
        logging.info("Entering client 2")
        c=pexpect.spawn('ssh -o StrictHostKeyChecking=no %s@%s' % (user_client2,client2))
        c.expect("password: ",timeout=30)
        c.sendline("infoblox")
        c.expect(["~\]# ","~\]\$ "])
        c.sendline("dig @"+config.grid_vip+" yahoo.com")
        sleep(2)
        c.expect(["~\]# ","~\]\$ "])
        c.sendline("dig @"+config.grid_vip+" abc.com")
        sleep(2)
        c.close()

    @pytest.mark.run(order=5)
    def test005_verify_log_messages_for_CEF_log(self):
	logging.info("Fetching current working directory")
	path= os.getcwd()
        logging.info("Logging into grid to collect logs")
        c=pexpect.spawn('ssh -o StrictHostKeyChecking=no root@%s' % (config.grid_vip))
        c.expect("bash-5.0# ")
        #c.sendline("zgrep -w \"CEF\"  /var/log/syslog > log_cef_niosspt_9255.txt")
        c.sendline("strings /var/log/syslog | grep \"CEF\" > log_cef_niosspt_9255.txt")
        c.expect("bash-5.0# ")
        c.sendline("scp -o StrictHostKeyChecking=no log_cef_niosspt_9255.txt "+config.client_user+"@"+config.client_ip+":"+path)
        c.expect("password: ")
        c.sendline("infoblox")
        c.expect("bash-5.0# ")
        c.close()
        f=open("log_cef_niosspt_9255.txt","r")
        a=f.readlines()
        f.close()
        count=0
        logging.info("Searching cef log for abc.com with client1 ip")
        for i in range(len(a)):
            if ("src=10.36.198.7" in a[i] and ("dst="+config.grid_vip) in a[i] and "RPZ-QNAME|NXDOMAIN" in a[i] and "qtype=A msg=\"rpz QNAME NXDOMAIN rewrite abc.com [A] via abc.com.rpz.com\"" in a[i] ):
                count=1
                break
        if count==1:
            logging.info("Client 1 ip verified successfully")
        else:
            raise Exception("Unable to find abc.com cef logs for the client1 ip")
        count=0
        logging.info("Searching cef log for yahoo.com with client 2 ip")
        for i in range(len(a)):
            if ("src=10.36.198.7" in a[i] and ("dst="+config.grid_vip) in a[i] and "RPZ-QNAME|NXDOMAIN" in a[i] and "qtype=A msg=\"rpz QNAME NXDOMAIN rewrite yahoo.com [A] via yahoo.com.rpz.com\"" in a[i] ):
                count=1
                break
        if count==1:
            logging.info("Client 1 ip verified successfully")
        else:
            raise Exception("Unable to find yahoo.com cef logs for the client1 ip")

        count=0
        logging.info("Searching cef log for abc.com with client2 ip")
        for i in range(len(a)):
            if ("src=10.36.198.8" in a[i] and ("dst="+config.grid_vip) in a[i] and "RPZ-QNAME|NXDOMAIN" in a[i] and "qtype=A msg=\"rpz QNAME NXDOMAIN rewrite abc.com [A] via abc.com.rpz.com\"" in a[i] ):
                count=1
                break
        if count==1:
            logging.info("Client 2 ip verified successfully")
        else:
            raise Exception("Unable to find abc.com cef logs for the client2 ip")

        count=0
        logging.info("Searching cef log for yahoo.com with client2 ip")
        for i in range(len(a)):
            if ("src=10.36.198.8" in a[i] and ("dst="+config.grid_vip) in a[i] and "RPZ-QNAME|NXDOMAIN" in a[i] and "qtype=A msg=\"rpz QNAME NXDOMAIN rewrite yahoo.com [A] via yahoo.com.rpz.com\"" in a[i] ):
                count=1
                break
        if count==1:
            logging.info("Client 2 ip verified successfully")
        else:
            raise Exception("Unable to find yahoo.com cef logs for the client2 ip")


    @pytest.mark.run(order=6)
    def test006_test_cleanup(self):
        logging.info("Starting Cleanup")
        logging.info("Get RPZ reference")
        ref_rpz_zone = ib_NIOS.wapi_request('GET',object_type="zone_rp")
        logging.info(ref_rpz_zone)
        ref_rpz=json.loads(ref_rpz_zone)[0]['_ref']
        logging.info("Deleteing RPZ zone")
        ref_del_rpz= ib_NIOS.wapi_request('DELETE',ref=ref_rpz)
        if bool(re.match("\"zone_rp*.",str(ref_del_rpz))):
            logging.info("rpz zone deletion successfull")
            logging.info("Restart services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            sleep(5)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            sleep(5)

        else:
            raise Exception("rpz zone deletion unsuccessful")






















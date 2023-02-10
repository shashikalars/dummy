__author__ = "Aditya G"
__email__  = "adityag@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master + Member                                                             #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415)                                      #
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
import paramiko


logging.basicConfig(filename='niosspt8863.log', filemode='w', level=logging.DEBUG)

class NIOSSPT_8863(unittest.TestCase):
    @pytest.mark.order(order=1)
    def test001_create_zone_add_records_and_sign_zone(self):
        logging.info("------Creating zone------")
        data = {"fqdn": "zone8863.com","grid_primary": [{"name": config.grid_fqdn,"stealth": False}],"grid_secondaries": [{"enable_preferred_primaries": False,"grid_replicate": True,"lead": False,"name": config.grid_member1_fqdn,"preferred_primaries": [],"stealth": False}]}
        zone_ref = ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        logging.info(zone_ref)
        if bool(re.match("\"zone_auth*.",str(zone_ref))):
            logging.info("abc.com created succesfully")
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
            raise Exception("Zone creation unsuccessful")
        logging.info("------Creating A record------")
        data = {"name": "arecord.zone8863.com","view": "default","ipv4addr": "10.0.0.1"}
        arecord_ref = ib_NIOS.wapi_request('POST',object_type='record:a',fields=json.dumps(data))
        logging.info(arecord_ref)
        if bool(re.match("\"record:a*.",str(arecord_ref))):
            logging.info("A record creation successfull")
        else:
            raise Exception("A record creation unsuccessfull")
        logging.info("------Creating NS record------")
        data = {"name": "zone8863.com","nameserver": "zone8863.com","view": "default","addresses": [{"address": "10.0.0.2","auto_create_ptr": True}]}
        nsrecord_ref = ib_NIOS.wapi_request('POST',object_type='record:ns',fields=json.dumps(data))
        if bool(re.match("\"record:ns*.",str(nsrecord_ref))):
            logging.info("NS record creation successfull")
            sleep(10)
        else:
            raise Exception("NS record creation unsuccessfull")
        logging.info("------Signing the zone zone8863.com------")
        print str(zone_ref)
        sleep(5)
        signzone_ref = ib_NIOS.wapi_request('POST', ref=str(zone_ref[1:-1]), params='?_function=dnssec_operation', fields=json.dumps({"operation":"SIGN"}))
        logging.info(signzone_ref)
        if bool(re.match("{}",str(signzone_ref))):
            logging.info("Zone signed successfully")
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
            raise Exception("Zone signing unsuccessfull")

    @pytest.mark.order(order=2)
    def test002_add_resolver(self):
        logging.info("------Adding resolver------")
        logging.info("Fetching grid reference")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
        grid_ref = json.loads(get_ref)[0]['_ref']
        logging.info(grid_ref)
        data = {"dns_resolver_setting":{"resolvers":["127.0.0.1","10.102.3.10"],"search_domains": []}}
        resolver_ref = ib_NIOS.wapi_request('PUT', ref=grid_ref, fields=json.dumps(data))
        logging.info(resolver_ref)
        if bool(re.match("\"grid*.",str(resolver_ref))):
            logging.info("Resolver added successfully")
        else:
            raise Exception("DNS resolver update failed")

    @pytest.mark.order(order=3)
    def test003_start_log_capture(self):
        logging.info("------Starting log capture------")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(config.grid_vip, port=22, username = "root", password = "infoblox")
        stdin, stdout, stderr = ssh.exec_command("nohup tail -f /var/log/syslog /infoblox/var/infoblox.log > log_automation.txt &")
        stdin.write("\n")
        stdin.flush()
        stdin.write("\n")
        stdin.flush()
        output = stdout.readlines
        logging.info(output)
        if 'error' in str(output):
            raise Exception("Unable to start log capture")
        elif 'ERROR' in str(output):
            raise Exception("Unable to start log capture")
        else:
            logging.info("------Log capture started------")
            ssh.close()


    @pytest.mark.order(order=4)
    def test004_enable_dns_integrity_check(self):
        logging.info("------Enabling dns integrity check------")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
        zone_ref = json.loads(get_ref)[0]['_ref']
        logging.info(zone_ref)
        data = {"dns_integrity_enable": True,"dns_integrity_frequency": 900,"dns_integrity_member": config.grid_fqdn,"dns_integrity_verbose_logging": True}
        dns_integrity_ref = ib_NIOS.wapi_request('PUT', ref=zone_ref, fields=json.dumps(data))
        logging.info(dns_integrity_ref)
        if bool(re.match("\"zone_auth*.",str(dns_integrity_ref))):
            logging.info("DNS integrity check enabled successfully")
            sleep(300)
        else:
            raise Exception("Enabling DNS integrity check failed")

    @pytest.mark.order(order=5)
    def test005_stop_log_capture(self):
        logging.info("------Stopping log capture------")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(config.grid_vip, port=22, username = "root", password = "infoblox")
        stdin, stdout, stderr = ssh.exec_command("pkill tail")
        stdin.write("\n")
        stdin.flush()
        stdin.write("\n")
        stdin.flush()
        output = stdout.readlines
        logging.info(output)
        if 'error' in str(output):
            raise Exception("Unable to stop log capture")
        elif 'ERROR' in str(output):
            raise Exception("Unable to stop log capture")
        else:
            logging.info("------Log capture stopped------")
            ssh.close()

    @pytest.mark.order(order=6)
    def test006_copy_log_file_and_validate(self):
        logging.info("------Starting transfer of file from the grid------")
        cmd = ['scp','-o','StrictHostKeyChecking=no','root@'+config.grid_vip+':/root/log_automation.txt','.']
        output = subprocess.call(cmd)
        if output==0:
            logging.info("File transfer successfull")
        else:
            raise Exception("File transfer failed")
        sleep(5)
        with open('log_automation.txt') as f:
            if "WARNING discrepancy found" in f.read():
                logging.info("Discrepancy found")
                logging.info("_____ATTACHING_____LOG______HERE________")
                logging.info("-----------------------------------------------------------")
                logging.info("-----------------------------------------------------------")
                logging.info("-----------------------------------------------------------")
                logging.info("-----------------------------------------------------------")
                logging.info(f.read())
                logging.info("-----------------------------------------------------------")
                logging.info("-----------------------------------------------------------")
                logging.info("-----------------------------------------------------------")
                logging.info("-----------------------------------------------------------")
                raise Exception("Warning found please verify the log")
            else:
                logging.info("No warning message found")
                print "Execution successfull"

    @pytest.mark.order(order=7)
    def test007_cleanup(self):
        logging.info("Starting cleanup")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth")
        zone_ref = json.loads(get_ref)[0]['_ref']
        zone_delete=ib_NIOS.wapi_request('DELETE', ref=zone_ref)
        if bool(re.match("\"zone_auth*.",str(zone_delete))):
            logging.info("Zone deleted succesfully")
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
            raise Exception("Zone deletion unsuccessful")

















        





        


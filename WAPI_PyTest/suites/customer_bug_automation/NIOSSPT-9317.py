__author__ = "Aditya G"
__email__  = "adityag@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master + Member                                                             #
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
from time import sleep
import commands
import json, ast
import time
import getpass
import sys
import pexpect
import paramiko


logging.basicConfig(filename='niosspt9317.log', filemode='w', level=logging.DEBUG)


class NIOSSPT_9317(unittest.TestCase):
    @pytest.mark.order(order=1)
    def test001_enable_dns_service(self):
        logging.info("Enabling DNS service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"enable_dns": True}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        sleep(10)
        logging.info(response)
        if bool(re.match("\"member:dns*.",str(response))):
            logging.info("DNS service enabled successfully")
        else:
            raise Exception("Enable DNS service unsuccessful")

        sleep(10)


    @pytest.mark.order(order=2)
    def test002_add_rpz_zone(self):
        logging.info("Adding a rpz zone")
        data={"fqdn": "rpz1.com","grid_primary": [{"name": config.grid_fqdn,"stealth": False}],"rpz_policy": "GIVEN","view": "default"}
        rpz_zone_ref=ib_NIOS.wapi_request('POST',object_type="zone_rp",fields=json.dumps(data))
        logging.info(rpz_zone_ref)
        if bool(re.match("\"zone_rp*.",str(rpz_zone_ref))):
            logging.info("RPZ zone creation successful")
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
            raise Exception("RPZ zone creation unsuccessful")

    @pytest.mark.order(order=3)
    def test003_create_zone(self):
        logging.info("Creating zone abcd.com")
        data={"fqdn":"abcd.com","view":"default","grid_primary":[{"name": config.grid_fqdn,"stealth": False}],"grid_secondaries": [{"name":config.grid_member1_fqdn,"stealth": False,"grid_replicate": True,"enable_preferred_primaries": False,"preferred_primaries": []}]}
        zone_ref=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        logging.info(zone_ref)
        if bool(re.match("\"zone_auth*.",str(zone_ref))):
            logging.info("abcd.com created succesfully")
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
            raise Exception("abcd.com creation unsuccessful")


    @pytest.mark.order(order=4)
    def test004_dtc_server1(self):
        logging.info("Creating dtc server1")
        data={"host": config.grid_vip,"monitors": [{"host": config.grid_vip,"monitor": "dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"}],"name": "server1"}
        server1_ref=ib_NIOS.wapi_request('POST',object_type='dtc:server',fields=json.dumps(data))
        logging.info(server1_ref)
        if bool(re.match("\"dtc:server*.",str(server1_ref))):
            logging.info("dtc server1 created succesfully")
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
            raise Exception("dtc server1 creation unsuccessful")

    @pytest.mark.order(order=5)
    def test005_dtc_server2(self):
        logging.info("Creating dtc server2")
        data={"host": config.grid_member1_vip,"monitors": [{"host": config.grid_member1_vip,"monitor": "dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"}],"name": "server2"}
        server2_ref=ib_NIOS.wapi_request('POST',object_type='dtc:server',fields=json.dumps(data))
        logging.info(server2_ref)
        if bool(re.match("\"dtc:server*.",str(server2_ref))):
            logging.info("dtc server2 created succesfully")
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
            raise Exception("dtc server2 creation unsuccessful")

    @pytest.mark.order(order=6)
    def test006_dtc_pool(self):
        logging.info("Creating dtc pool")
        server=ib_NIOS.wapi_request('GET',object_type='dtc:server')
        server1=json.loads(server)[0]['_ref']
        server2=json.loads(server)[1]['_ref']
        data={"name": "pool","lb_preferred_method": "ROUND_ROBIN","servers": [{"ratio": 1,"server": server1},{"ratio": 1,"server": server2}]}
        pool_ref=ib_NIOS.wapi_request('POST',object_type='dtc:pool',fields=json.dumps(data))
        logging.info(pool_ref)
        if bool(re.match("\"dtc:pool*.",str(pool_ref))):
            logging.info("pool created succesfully")
            logging.info("Restart services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            sleep(10)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            sleep(10)

        else:
            raise Exception("pool creation unsuccessful")

    @pytest.mark.order(order=7)
    def test007_dtc_lbdn(self):
        logging.info("Creating lbdn")
        zone=ib_NIOS.wapi_request('GET',object_type='zone_auth', params="?fqdn=abcd.com")
        print(zone)
        zone_ref=json.loads(zone)[0]['_ref']
        pool=ib_NIOS.wapi_request('GET',object_type='dtc:pool')
        pool_ref=json.loads(pool)[0]['_ref']
        data={"name": "lbdn1","lb_method": "ROUND_ROBIN","patterns": ["b2.abcd.com"],"auth_zones": [zone_ref],"pools": [{"pool": pool_ref,"ratio": 1}]}
        lbdn_ref=ib_NIOS.wapi_request('POST',object_type='dtc:lbdn',fields=json.dumps(data))
        logging.info(lbdn_ref)
        if bool(re.match("\"dtc:lbdn*.",str(lbdn_ref))):
            logging.info("lbdn created succesfully")
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
            raise Exception("lbdn creation unsuccessful")

    @pytest.mark.order(order=8)
    def test008_verify_round_robin(self):
        logging.info("Verifying round robin")
        sleep(35)
        ip='@'+config.grid_vip
        #validation1="b2.abcd.com.             28800   IN      A       "+config.grid_vip
        #validation2="b2.abcd.com.             28800   IN      A       "+config.grid_member1_vip
        validation1=config.grid_vip
        validation2=config.grid_member1_vip
        output=subprocess.check_output(['dig',ip,'b2.abcd.com','in','a'])
        logging.info(output)
        if validation1 in output:
            logging.info("Validation1 successful")
            sleep(5)
        else:
            raise Exception("Incorrect dig output")
        output2=subprocess.check_output(['dig',ip,'b2.abcd.com','in','a'])
        logging.info(output2)
        if validation2 in output2:
            logging.info("Validation2successful")
        else:
            raise Exception("Incorrect dig output")
        logging.info("Round robin validation succesfull")


    @pytest.mark.order(order=9)
    def test009_restart_services_multiple_times(self):
        logging.info("Restarting services multipletimes")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(5)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(2)
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(2)
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(10)

    @pytest.mark.order(order=10)
    def test010_check_for_core_file_generation(self):
        logging.info("Checking for core file generation")
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_system_host_keys()
        ssh.connect(config.grid_vip,username="root")
        stdin,stdout,stderr = ssh.exec_command('cd /storage/cores; ls -ltr')
        output=stdout.readlines()
        if "core.named" in output:
            raise Exception("Core file generated")
        else:
            logging.info("Core file not generated")

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

        zone=ib_NIOS.wapi_request('GET',object_type='zone_auth', params="?fqdn=abcd.com")
        zone_ref=json.loads(zone)[0]['_ref']
        del_zone=ib_NIOS.wapi_request('DELETE',ref=zone_ref)

        rpz_zone=ib_NIOS.wapi_request('GET',object_type='zone_rp')
        rpz_zone_ref=json.loads(rpz_zone)[0]['_ref']
        del_rpz_zone=ib_NIOS.wapi_request('DELETE',ref=rpz_zone_ref)


        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(5)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(5)









   







        


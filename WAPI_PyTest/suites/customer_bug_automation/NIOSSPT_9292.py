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


logging.basicConfig(filename='niosspt9292.log', filemode='w', level=logging.DEBUG)


class NIOSSPT_9292(unittest.TestCase):
    @pytest.mark.order(order=1)
    def test001_create_zone(self):
        """
        Create zone abc.com
        """
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
            sleep(5)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            sleep(5)

        else:
            raise Exception("abc.com creation unsuccessful")

    @pytest.mark.order(order=2)
    def test002_validate_zone(self):
        """
        Validate created zone abc.com
        """
        logging.info("Validating zone abc.com")
        zone_ref=ib_NIOS.wapi_request('GET',object_type='zone_auth')
        logging.info(zone_ref)
        flag = False
        for ref in json.loads(zone_ref):
            if ref["fqdn"] == "abc.com":
                flag = True
                break
        if not flag:
            raise Exception("abc.com validation unsuccessful")

    @pytest.mark.order(order=3)
    def test003_dtc_server1(self):
        """
        Create DTC server
        "monitor": "dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"
        """
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

    @pytest.mark.order(order=3)
    def test003_dtc_server2(self):
        """
        Create DTC server 
        "monitor": "dtc:monitor:icmp/ZG5zLmlkbnNfbW9uaXRvcl9pY21wJGljbXA:icmp"
        """
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

    @pytest.mark.order(order=4)
    def test004_dtc_pool(self):
        """
        Create DTC pool
        """
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
            sleep(5)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            sleep(5)

        else:
            raise Exception("pool creation unsuccessful")


    @pytest.mark.order(order=5)
    def test005_dtc_lbdn(self):
        """"
        Create DTC lbdn
        """
        logging.info("Creating lbdn")
        zone=ib_NIOS.wapi_request('GET',object_type='zone_auth', params="?fqdn=abc.com")
        zone_ref=json.loads(zone)[0]['_ref']
        pool=ib_NIOS.wapi_request('GET',object_type='dtc:pool')
        pool_ref=json.loads(pool)[0]['_ref']
        data={"name": "lbdn1","lb_method": "ROUND_ROBIN","patterns": ["b2.abc.com"],"auth_zones": [zone_ref],"pools": [{"pool": pool_ref,"ratio": 1}]}
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

    @pytest.mark.order(order=6)
    def test006_verify_round_robin(self):
        """
        Verify round robin
        """
        logging.info("Verifying round robin")
        sleep(40)
        ip='@'+config.grid_vip
        #validation1="b2.abc.com.             28800   IN      A       "+config.grid_vip
        #validation2="b2.abc.com.             28800   IN      A       "+config.grid_member1_vip
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

    @pytest.mark.order(order=7)
    def test007_test_cleanup(self):
        """
        Test case clean-up
        """

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





















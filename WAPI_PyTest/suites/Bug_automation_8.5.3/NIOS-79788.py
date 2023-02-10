#!/usr/bin/env python
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. SA configuration                                                      #
#  2. License : Grid                                                        #
#############################################################################

import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import sys
import json
import commands
import json, ast
import requests
from time import sleep as sleep
import ib_utils.ib_NIOS as ib_NIOS
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv


class NIOS_79788(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_add_offline_member_to_grid(self):
               
        for i in range(1,5):
            
            data = {"config_addr_type": "IPV4",
                    "host_name": "member"+str(i)+".localdomain",
                    "platform": "VNIOS",
                    "service_type_configuration": "ALL_V6",
                    "vip_setting": {"address": "10.35.111."+str(i),
                                "gateway": "10.35.0.1",
                                "primary": True,
                                "subnet_mask": "255.255.0.0"}}
            response = ib_NIOS.wapi_request('POST',object_type="member",fields=json.dumps(data))
            print(response)
            if type(response) == tuple:
                print("Failure: Add offline member")
                assert False
        print("Sucess: added offline member to grid")

            
    @pytest.mark.run(order=2)
    def test_001_make_changes_in_member_property_and_check_logs(self):
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member?_return_fields=vip_setting", grid_vip=config.grid_vip)
        
        for row in json.loads(get_ref):
            if row['vip_setting']['address']=="10.35.111.9":
                data = {"vip_setting":{"address":"10.35.111.8"}}
                response = ib_NIOS.wapi_request('PUT',ref=row['_ref'],fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
            	if type(response) == tuple:
                	print("Failure: Not able to make any chnages in member property")
                	assert False
        print("Sucess: Able to make any chnages in member property")


        sleep(5)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        lookfor = ["vpn_master_vnode_vpn_ip_address.*chmod failed for /infoblox/var/vpn_addrs/.*","vpn_set_replica_vpn_address.*chmod failed for /infoblox/var/vpn_addrs/.*"]
        flag=0
        for look in lookfor:
            result = logv(look, '/infoblox/var/infoblox.log', config.grid_vip)
            if not result:
                flag=flag+1
        if flag==2:
            print("Sucess: Validate infoblox log message after made changes in offline member property")
            assert True
        else:
            print("Failure: Validate infoblox log message after made changes in offline member property")
            assert False



    @pytest.mark.run(order=3)
    def test_002_cleanup(self):
        print("Clean up all created objects")

        get_ref = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            
            if 'member1.localdomain' in ref['_ref'] or 'member2.localdomain' in ref['_ref'] or 'member3.localdomain' in ref['_ref'] or 'member4.localdomain' in ref['_ref'] :

                response = ib_NIOS.wapi_request('DELETE',ref=ref['_ref'])
                print(response)
                if type(response) == tuple:
                    print("Failure: Offline member did not deleted ")
                    assert False




import os
import re
import config
import pytest
import unittest
import logging
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
from subprocess import Popen, PIPE
import pexpect
import paramiko

#config.grid_vip="10.35.204.9"
get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
for ref in json.loads(get_ref):
    data = {"use_lan_ipv6_port": True}
    response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data))

grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
ref = json.loads(grid)[0]['_ref']
data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)



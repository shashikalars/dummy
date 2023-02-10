import config
import pytest
import unittest
import logging
import json
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.dig_utility
from time import sleep
import time

# adding this function for the purpose of integration

ref=ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
ref=json.loads(ref)[0]['_ref']
data={"use_mgmt_port":True}
ref1=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data), grid_vip=config.grid_vip)
logging.info (ref1)

# Restart Services
grid =  ib_NIOS.wapi_request('GET', object_type="grid")
ref = json.loads(grid)[0]['_ref']
request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
sleep(60)


ref=ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
ref=json.loads(ref)[1]['_ref']
data={"use_mgmt_port":True}
ref1=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data), grid_vip=config.grid_vip)
logging.info (ref1)

# Restart Services
grid =  ib_NIOS.wapi_request('GET', object_type="grid")
ref = json.loads(grid)[0]['_ref']
request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
sleep(60)

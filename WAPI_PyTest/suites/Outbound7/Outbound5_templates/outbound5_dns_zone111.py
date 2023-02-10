import os
import json
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
import commands
import json, ast
import requests
import time
import pexpect
import getpass
import sys
import config


class Outbound(unittest.TestCase):

def test_001_create_auth_zone():
    print ("Check here about your data:",config.grid_zone1)
    print (config.grid_vip)
    print config.grid_zone1
    #print config.grid_zone1
    data={"fqdn":config.grid_zone1,"grid_primary":[{"name": config.grid_fqdn2}],"allow_transfer": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}],"allow_query": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}],"allow_update": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}]}
    print data
    response1=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data),grid_vip= config.grid_vip2)
    response1=json.loads(response1)
    print ("Restart services")
    print ("Associated Zone with Primary GRID :",response1)
    grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip= config.grid_vip2)
    ref = json.loads(grid)[0]['_ref']
    publish={"member_order":"SIMULTANEOUSLY"}
    request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
    time.sleep(10)
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",grid_vip= config.grid_vip2)
    time.sleep(20)
    print ("Restarting the grid ")
    return response1

def test_002_check_auth_zone():
    a=config.grid_vip
    print a
    response=ib_NIOS.wapi_request('GET',object_type='zone_auth?fqdn='+config.grid_zone1)
    if response =='[]':
        print ("Zone not present,adding the zone")
        data={"fqdn": config.grid_zone1 ,"grid_primary":[{"name":config.grid_fqdn}],"allow_transfer":[{"_struct": "addressac","address": "Any","permission": "ALLOW"}],"allow_query": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}],"allow_update": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}]}
        response2=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        print response2
        print type(response2)
        response2=json.loads(response2)
        print("Copying the records")
        print ("Restart services")
        print ("Associated Zone with Primary GRID :",response2)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        time.sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        time.sleep(20)
        print ("Restarting the grid ")
        data1={"import_from": config.grid_vip2}
        response2=ib_NIOS.wapi_request('PUT',object_type=response2,fields=json.dumps(data1))
        return response2
    else:
        print("Zone present already copying records")
        data1={"import_from": config.grid_vip2}
        res=json.loads(response)[0]['_ref']
        response2=ib_NIOS.wapi_request('PUT',object_type=res,fields=json.dumps(data1))
        print response2
        #response2=json.loads(response2)
        return response2

create_auth_zone()
check_auth_zone()


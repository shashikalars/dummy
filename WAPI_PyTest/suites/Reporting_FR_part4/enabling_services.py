import re
#import pdb
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
import commands
import json, ast
import requests
from time import sleep as sleep
import pexpect
import paramiko
import time
import sys
from paramiko import client
#from logger import logger
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results


"""
TEST Steps:
      1.  Input/Preparaiton      : Create a network, Range and request leases
      2.  Search                 : Search with Default Filter
      3.  Validation             : Validating Search result against input data
"""



def start_subscriber_collection_services_for_added_site(member):
    for mem in member:
        get_ref=ib_NIOS.wapi_request('GET', object_type='member:parentalcontrol?name='+mem)
        get_ref=json.loads(get_ref)
        ref=get_ref[0]["_ref"]
        print ref
        logging.info(ref)
        data={"enable_service":True}
        reference=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
        logging.info(reference)
        print reference
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        time.sleep(1)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        time.sleep(20)
        for mem in member:
            get_ref=ib_NIOS.wapi_request('GET', object_type='member:parentalcontrol?name='+mem)
            get_ref=json.loads(get_ref)
            if get_ref[0]["enable_service"]==True:
                return True
                print("subscriber service is started in "+mem)
            else:
                return None
                print("Not able to start subscriber service "+mem)
        time.sleep(40)

def mem_ref_string_pc(hostname):
    response = ib_NIOS.wapi_request('GET', object_type="member:parentalcontrol")
    logging.info(response)
    #print(response)
    if type(response)!=tuple:
        ref1 = json.loads(response)
        for key in ref1:
            if key.get('name') == hostname:
                mem_ref = key.get('_ref')
                break
    else:
        print("Failed to get member ref string")
        mem_ref = "NIL"

    return mem_ref

def change_default_route():
    ref=ib_NIOS.wapi_request('GET', object_type="grid")
    print("#############",ref)
    ref=json.loads(ref)[0]['_ref']
    #data={"enable_gui_api_for_lan_vip":"true","dns_resolver_setting": {"resolvers": ["10.0.2.35"]}}
    data={"dns_resolver_setting": {"resolvers": [config.resolver_ip]}}
    ref1=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
    child.logfile=sys.stdout
    child.expect('-bash-5.0#')
    child.sendline('ip route del default via 10.35.0.1 dev eth1 table main')
    child.expect('-bash-5.0#')
    child.sendline('ip route add default via 10.36.0.1 dev eth0 table main')
    child.sendline('exit')
    child.expect(pexpect.EOF)
    time.sleep(20)

def enable_mgmt_port_for_dns():
    ref=ib_NIOS.wapi_request('GET', object_type="member:dns")
    ref=json.loads(ref)[0]['_ref']
    data={"use_mgmt_port":True}
    ref1=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
    logging.info (ref1)
    time.sleep(120)

def enable_GUI_and_API_access_through_LAN_and_MGMT():
    ref=ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.Master1_MGMT_IP)
    logging.info (ref)
    ref=json.loads(ref)[0]['_ref']
    logging.info(ref)
    data={"enable_gui_api_for_lan_vip":True}
    ref1=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data),grid_vip=config.Master1_MGMT_IP)
    logging.info (ref1)
    time.sleep(120)


def stop_subscriber_collection_services_for_added_site(member):#config.grid_fqdn
    get_ref=ib_NIOS.wapi_request('GET', object_type='member:parentalcontrol?name='+member)
    get_ref=json.loads(get_ref)
    ref=get_ref[0]["_ref"]
    logging.info(ref)
    data={"enable_service":False}
    reference=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
    logging.info(reference)
    grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    ref = json.loads(grid)[0]['_ref']
    publish={"member_order":"SIMULTANEOUSLY"}
    request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
    time.sleep(1)
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    get_ref=ib_NIOS.wapi_request('GET', object_type='member:parentalcontrol?name='+member)
    get_ref=json.loads(get_ref)
    if get_ref[0]["enable_service"]==False:
        logging.info ("Test case passed")
        time.sleep(40)
        logging.info ("subscriber service is stopped")
        return get_ref[0]["enable_service"]
    else:
        logging.info("Not able to stop subscriber service")
        return None



class  Query_Count_details_by_subscriber_id(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_001_start_DCA_service(self):
        logging.info("starting DCA service in the Grid member...\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        logging.info(get_ref)
        print get_ref
        res = json.loads(get_ref)
        print res
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"enable_dns": True,"enable_dns_cache_acceleration": True}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        print response
        sleep(10)
        print (response)
        sleep(30)
        print("DCA service started in the Grid member")


    @pytest.mark.run(order=2)
    def test_002_start_Threat_Analysis_service(self):
        logging.info("starting TA service in the Grid member...\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatanalytics", grid_vip=config.grid_vip)
        logging.info(get_ref)
        print get_ref
        res = json.loads(get_ref)
        print res
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"enable_service": True}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        print response
        sleep(10)
        print (response)
        sleep(30)
        print("Threat analysis service started in the Grid member")


    @pytest.mark.run(order=3)
    def test_003_start_TAXII_service(self):
        logging.info("starting TAXII service in the Grid member...\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="taxii", grid_vip=config.grid_vip)
        logging.info(get_ref)
        print get_ref
        res = json.loads(get_ref)
        print res
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"enable_service": True}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
        print response
        sleep(10)
        print (response)
        sleep(30)
        print("TAXII service started in the Grid member")


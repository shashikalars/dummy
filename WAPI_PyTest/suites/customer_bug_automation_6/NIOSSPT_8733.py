__author__ = "Ashwini C M, Chetan Kumar PG"
__email__  = "cma@infoblox.com, cpg@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master                                                                      #
#  2. Licenses : DNS, DHCP, Grid, NIOS(IB-V1415), TP License(Both)                     #
#  3. MGMT interface                                                                   #
########################################################################################
import os
import re
import csv
import config
import pytest
import unittest
import logging
import json
import shlex
import pexpect
import paramiko
from time import sleep
from subprocess import Popen,PIPE
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as  ib_TOKEN
from ib_utils.log_capture import log_action as log
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_8733.log" ,level=logging.DEBUG,filemode='w')

def restart_services(grid=config.grid_vip):
    """
    Restart Services
    """
    display_msg("Restart services")
    get_ref =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=grid)
    ref = json.loads(get_ref)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data),grid_vip=grid)
    sleep(30)

def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

def validate_syslog(lookfor, logfile, grid=config.grid_vip):
    """
    Validate captured log
    Using this function because log_validation.py in ib_utils is not correct.
    """
    display_msg("Validate captured log")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(grid, username='root', pkey = mykey)
    file_name='_'.join(logfile.split('/'))
    file = '/root/dump/'+ str(grid)+file_name+'.log'
    display_msg("cat "+file+" | grep -i \""+lookfor+"\"")
    stdin, stdout, stderr = client.exec_command("cat "+file+" | grep -i '"+lookfor+"'")
    result=stdout.read()
    display_msg(result)
    client.close()
    if result:
        return True
    return False

class RFE_8733(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_001_enable_dns_service(self):
        """
        Enable DNS service.
        Enable DNS service on MGMT interface.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Enable DNS service")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns')
        display_msg(get_ref)
        data = {"enable_dns":True,"use_mgmt_port":True}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Enable DNS Service")
            assert False
        restart_services()
        ref=ib_NIOS.wapi_request('GET', object_type="member:dns")
        ref=json.loads(ref)[0]['_ref']
        data={"use_mgmt_port":True}
        ref1=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
        display_msg(ref1)
        sleep(120)
        display_msg("-----------Test Case 1 Execution Completed------------")
            
    @pytest.mark.run(order=2)
    def test_002_enable_threat_protection_service(self):
        """
        Enable Threat Protection service.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        logging.info("Enable the threat protection service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        display_msg(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps({"enable_service": True}))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Enable threat protection service")
            assert False
        restart_services()
        
        display_msg("-----------Test Case 2 Execution Completed------------")

    @pytest.mark.run(order=3)
    def test_003_enable_automatic_download(self):
        """
        Enable auto download in threat protection service.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 3 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        logging.info("Enable automatic download")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatprotection")
        display_msg(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps({"enable_auto_download": True}))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Enable automatic download in threat protection service")
            assert False
        restart_services()
        display_msg("sleep 30 seconds for threat protection rules to download")
        sleep(30)
        
        display_msg("-----------Test Case 3 Execution Completed------------")

    @pytest.mark.run(order=4)
    def test_004_create_auth_forward_mapping_zone(self):
        """
        Create an auth zone with name niosspt_8733.com.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 4 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Create a DNS auth zone niosspt_8733.com")
        data = {"fqdn": "niosspt_8733.com",
                "view":"default",
                "grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type="zone_auth",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Create a DNS auth zone niosspt_8733.com")
            assert False
        restart_services()

        display_msg("-----------Test Case 4 Execution Completed------------")

    @pytest.mark.run(order=5)
    def test_005_add_cds_record(self):
        """
        Add CDS record (unknown record).
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 5 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Add unknown record of type CDS")
        data = {"name": "cds.niosspt_8733.com",
                "record_type": "CDS",
                "subfield_values": [{"field_value":"100",
                                     "field_type": "S",
                                     "include_length": "NONE"},
                                    {"field_value":"0",
                                     "field_type": "S",
                                     "include_length": "NONE"},
                                    {"field_value":"200",
                                     "field_type": "S",
                                     "include_length": "NONE"},
                                    {"field_value":"123456789abcdef67890123456789abcdef67890",
                                     "field_type": "X",
                                     "include_length": "8_BIT"}],
                "view": "default",
                "extattrs":{"IB Discovery Owned":{"value":"100"},
                            "Site":{"value":"200"}}}
        response = ib_NIOS.wapi_request('POST',object_type="record:unknown",fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Add unknown record of type CDS")
            assert False
        
        display_msg("-----------Test Case 5 Execution Completed------------")

    @pytest.mark.run(order=6)
    def test_006_perform_dig_query_for_cds_record(self):
        """
        Perform dig query for CDS record (unknown record).
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 6 Execution Started           |")
        display_msg("----------------------------------------------------")
        
        display_msg("Perform dig query for the added CDS record")
        display_msg("Start capturing /var/log/nessages")
        log("start","/var/log/nessages",config.grid_vip)
        display_msg("dig @"+config.grid_vip+" cds.niosspt_8733.com IN CDS +tcp +retry=0 +timeout=1")
        output = os.popen("dig @"+config.grid_vip+" cds.niosspt_8733.com IN CDS +tcp +retry=0 +timeout=1").read()
        output = output.split('\n')
        answer = False
        pattern = False
        for line in output:
            display_msg(line)
        match_line = "cds.niosspt_8733.com.\s+\d+\s+IN\s+CDS\s+.*"
        for line in output:
            if answer and not pattern:
                match = re.match(match_line, line)
                if match:
                    pattern = True
                    break
            if 'ANSWER SECTION' in line:
                answer = True
        if not answer or not pattern:
            display_msg("Failure: Perform dig query")
            assert False

        lookfor = "'CEF:0\|Infoblox\|NIOS Threat'"
        result = validate_syslog(lookfor, '/var/log/nessages', config.grid_vip)
        display_msg("Stop capturing /var/log/syslog")
        log("stop","/var/log/syslog",config.grid_vip)
        if result:
            display_msg("Failure: "+lookfor+" found in /var/log/nessages")
            assert False

        display_msg("-----------Test Case 6 Execution Completed------------")

    @pytest.mark.run(order=-1)
    def test_cleanup(self):
        """
        cleanup method: Delete all the objects created from this script.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|          Test Case cleanup Started           |")
        display_msg("------------------------------------------------")
        
        display_msg("Delete auth zone niosspt_8733.com")
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth')
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if ref['fqdn'] == 'niosspt_8733.com':
                response = ib_NIOS.wapi_request('DELETE', ref = ref['_ref'])
                display_msg(response)
                if type(response) == tuple:
                    display_msg("Failure: Delete auth zone niosspt_8733.com")
                    assert False
                break
        
        display_msg("Disable threat protection service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        display_msg(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps({"enable_service": False}))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Disable threat protection service")
            assert False
        restart_services()

        display_msg("-----------Test Case cleanup Completed------------")

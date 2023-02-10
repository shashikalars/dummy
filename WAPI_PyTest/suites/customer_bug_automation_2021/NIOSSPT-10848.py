#!/usr/bin/env python
__author__ = "Shivasai Bandaru"
__email__  = "sbandaru@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Stand Alone Grid                                                                 #
#  2. Licenses : DNS, DHCP, Grid                                                       #
########################################################################################

import os
import re
import paramiko
import config
import pytest
import unittest
import logging
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_10848.log" ,level=logging.DEBUG,filemode='w')



def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

def get_engineBoots():
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data="cat /var/lib/net-snmp/snmpd.conf | grep engineBoots"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        engineBoots = re.findall('\d\d',stdout)
        return engineBoots
    

class NIOSSPT_10848(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_000_setup(self):
        """
        Creating snmpv3 user and adding the user in grid snmp setting 
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case setup Started            |")
        display_msg("------------------------------------------------")
        data={"name":"NIOSSPT","authentication_protocol":"MD5","privacy_protocol":"DES","privacy_password":"Infoblox@123","authentication_password":"Infoblox@123"}
        response = ib_NIOS.wapi_request('POST',object_type="snmpuser",fields=json.dumps(data))
        print(response)
        response = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        userref = json.loads(response)[0]['_ref']
        userref = userref.encode('ascii', 'ignore')
        print(userref)
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        getref=json.loads(get_ref)[0]['_ref']
        print(getref)
        data={"snmp_setting":{"snmpv3_queries_enable": True,"snmpv3_queries_users": [{"user": userref}],"snmpv3_traps_enable": True,"trap_receivers": [{"address": "10.36.198.1","user":userref}]}}
        response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            assert False
        else:
            assert True
    
    @pytest.mark.run(order=2)
    def test_001_check_engineBoots_after_reboot(self):
        """
        check snmp engineBoots before reboot
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")
        engineBoots_before = get_engineBoots()[0]
        engineBoots_before = int(engineBoots_before)
        print(engineBoots_before)
        
        os.system("/import/tools/lab/bin/reboot_system -H " + config.vmid )
        sleep(300)
     	engineBoots_after = get_engineBoots()[0]
        engineBoots_after = int(engineBoots_after)
        print(engineBoots_after)
        if engineBoots_after - engineBoots_before == 2:
            assert True
        else:
            assert False
        display_msg("-----------Test Case 1 Execution Completed------------")

    @pytest.mark.run(order=3)
    def test_002_check_engineBoots_after_pkill(self):
        """
        check engineBoots value after killing snmp services
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")
        engineBoots_before = get_engineBoots()[0]
        engineBoots_before = int(engineBoots_before)
        print(engineBoots_before)
        
        client = paramiko.SSHClient()
    	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    	privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    	mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    	client.connect(config.grid_vip, username='root', pkey = mykey)
        data="pkill -x snmpd"
        stdin, stdout, stderr = client.exec_command(data)
        sleep(90)
        engineBoots_after = get_engineBoots()[0]
        engineBoots_after = int(engineBoots_after)
        print(engineBoots_after)
        
        if engineBoots_after - engineBoots_before == 1:
            assert True
        else:
            assert False
            
        
    @pytest.mark.run(order=4)
    def test_003_check_engineBoots_after_stop_snmp(self):
        """
        check engineBoots value after stop snmp services
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 3 Execution Started           |")
        display_msg("----------------------------------------------------")
        engineBoots_before = get_engineBoots()[0]
        engineBoots_before = int(engineBoots_before)
        print(engineBoots_before)
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        getref=json.loads(get_ref)[0]['_ref']
        print(getref)
        data={"snmp_setting":{"snmpv3_queries_enable": False,"snmpv3_traps_enable": False}}
        response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
        print(response)
        sleep(90)
        engineBoots_after = get_engineBoots()[0]
        engineBoots_after = int(engineBoots_after)
        print(engineBoots_after)
        if engineBoots_after - engineBoots_before == 1:
            assert True
        else:
            assert False

    @pytest.mark.run(order=5)
    def test_004_check_engineBoots_after_start_snmp(self):
        """
        check engineBoots value after starting snmp services
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 4 Execution Started           |")
        display_msg("----------------------------------------------------")
        engineBoots_before = get_engineBoots()[0]
        engineBoots_before = int(engineBoots_before)
        print(engineBoots_before)
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        getref=json.loads(get_ref)[0]['_ref']
        print(getref)
        response = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        userref = json.loads(response)[0]['_ref']
        userref = userref.encode('ascii', 'ignore')
        data={"snmp_setting":{"snmpv3_queries_enable": True,"snmpv3_queries_users": [{"user": userref}],"snmpv3_traps_enable": True,"trap_receivers": [{"address": "10.36.198.1","user":userref}]}}
        response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
        print(response)
        sleep(90)
        engineBoots_after = get_engineBoots()[0]
        engineBoots_after = int(engineBoots_after)
        print(engineBoots_after)
        if engineBoots_after - engineBoots_before == 2:
            assert True
        else:
            assert False

    @pytest.mark.run(order=6)
    def test_005_check_engineBoots_after_stop_snmp(self):
        """
        check engineBoots value after stop snmp services
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 5 Execution Started           |")
        display_msg("----------------------------------------------------")
        engineBoots_before = get_engineBoots()[0]
        engineBoots_before = int(engineBoots_before)
        print(engineBoots_before)
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        getref=json.loads(get_ref)[0]['_ref']
        print(getref)
        data={"snmp_setting":{"snmpv3_queries_enable": False,"snmpv3_traps_enable": False}}
        response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
        print(response)
        sleep(90)
        engineBoots_after = get_engineBoots()[0]
        engineBoots_after = int(engineBoots_after)
        print(engineBoots_after)
        if engineBoots_after - engineBoots_before == 1:
            assert True
        else:
            assert False
    
    @pytest.mark.run(order=-1)
    def test_cleanup(self):
        """
        cleanup method: Delete all the objects created and changes made from this script.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|          Test Case cleanup Started           |")
        display_msg("------------------------------------------------")
        display_msg("Reverting back the Grid to its original state")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        getref=json.loads(get_ref)[0]['_ref']
        print(getref)
        data={"snmp_setting":{"snmpv3_queries_enable": False,"snmpv3_traps_enable": False}}
        response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
        print(response)
        response = ib_NIOS.wapi_request('GET',object_type="snmpuser")
        userref = json.loads(response)[0]['_ref']
        userref = userref.encode('ascii', 'ignore')
        response = ib_NIOS.wapi_request('DELETE',ref=userref)
        if type(response) == tuple: 
            assert False
        else:
            assert True       
        display_msg("-----------Test Case cleanup Completed------------")

        
        
        
        
        
        
        

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
# import requests
import time
import sys
import pexpect
import ib_utils.log_capture
from paramiko import client
import paramiko
import shlex
from subprocess import Popen, PIPE
from ib_utils.log_capture import log_action as log
from ib_utils.log_validation import log_validation as logv
from ib_utils.common_utilities import generate_token_from_file

# site_data={"blocking_ipv4_vip1": "2.4.5.6","nas_gateways":[{"ip_address": "10.36.0.151", "name": "nas1", "shared_secret":"testing123"}],"maximum_subscribers": 898989,
#          "members": [{"name": str(config.grid_fqdn)}],"msps":[{"ip_address": "10.196.128.13"}],"name": "site1","nas_port": 1813,"spms": [{"ip_address": "10.12.11.11"}]}

site_data = {"name": "site1", "blocking_ipv4_vip1": "1.1.1.1", "blocking_ipv4_vip2": "2.2.2.2",
             "blocking_ipv6_vip1": "22::55", "blocking_ipv6_vip2": "2::11",
             "spms": [{"ip_address": "9.9.9.9"}], "msps": [{"ip_address": "10.196.6.95"}],
             "nas_gateways": [{"ip_address": "10.36.0.151", "name": "nas1", "shared_secret": "testing123"}],
             "members": [{"name": config.grid_fqdn}]}
#subscriber_properties_data = {"enable_parental_control": True, "cat_acctname": "InfoBlox",
#                              "cat_password": "CSg\@vBz!rx7A",
#                              "category_url": "https://pitchers.rulespace.com/ufsupdate/web.pl",
#                              "proxy_url": "http://10.196.9.113:8001", "proxy_username": "client",
#                              "proxy_password": "infoblox",
#                              "pc_zone_name": "parental_control", "ident": "pkFu-yhrf-qPOV-s5BU",
#                              "cat_update_frequency": 24}

subscriber_properties_data = {"enable_parental_control": True, "cat_acctname": "infoblox_sdk",
                               "cat_password": "LinWmRRDX0q",
                               "category_url": "https://dl.zvelo.com/",
                               "proxy_url": "http://10.196.9.113:8001", "proxy_username": "client",
                               "proxy_password": "infoblox",
                               "pc_zone_name": "parental_control","cat_update_frequency": 24}

def start_syslog(logfile):
    """
    Start log capture
    """
    print("Start capturing " + logfile)
    log("start", logfile, config.grid_vip)


def stop_syslog(logfile):
    """
    Stop log capture
    """
    print("Stop capturing " + logfile)
    log("stop", logfile, config.grid_vip)


def validate_syslog(logfile, lookfor):
    """
    Validate captured log
    """
    print("Validate captured log")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(config.grid_vip, username='root', pkey=mykey)
    file_name = '_'.join(logfile.split('/'))
    file = '/root/dump/' + str(config.grid_vip) + file_name + '.log'
    print("cat " + file + " | grep -i '" + lookfor + "'")
    stdin, stdout, stderr = client.exec_command("cat " + file + " | grep -i '" + lookfor + "'")
    result = stdout.read()
    print(result)
    client.close()
    if result:
        return True
    return False


class SSH:
    client = None

    def __init__(self, address, port=22, key=None):
        # print ("connecting to server \n : ", address)
        self.client = client.SSHClient()
        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        # os.system('ssh-keygen -p -m PEM -f ~/.ssh/id_rsa')
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        # print ("mykey here :",mykey)
        self.client.connect(address, port=22, timeout=0.3, username='root', pkey=mykey)

    def send_command(self, command):
        if (self.client):
            stdin, stdout, stderr = self.client.exec_command(command)
            result = stdout.read()
            print(result)
            error = stderr.read()
            print(error)
            return result
        else:
            print("Connection not opened.")


def restart_services():
    """
    Restart Services
    """
    print("Restart services")
    grid = ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.master0mgmt)
    ref = json.loads(grid)[0]['_ref']
    data = {"member_order": "SIMULTANEOUSLY", "restart_option": "FORCE_RESTART", "service_option": "ALL"}
    restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=restartservices", fields=json.dumps(data),grid_vip=config.master0mgmt)
    sleep(10)


def show_subscriber_secure_data():
    logging.info(" show subscriber_secure_data")
    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@' + config.grid_vip)
    child.logfile = sys.stdout
    child.expect('password:')
    child.sendline('infoblox')
    child.expect('Infoblox >')
    child.sendline('show subscriber_secure_data')
    child.expect('>')
    output = child.before
    child.sendline('exit')
    return output


class Network(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_001_enable_parental_control_feature(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 1  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        """
        setup method: Used for configuring pre-required configs.
        """
        print("------------------------------------------------")
        print("|           Test Case setup Started            |")
        print("------------------------------------------------")

        '''Add MGMT ip route'''
        cmd1 = "ip route del default via 10.35.0.1 dev eth1 table main"
        cmd2 = "ip route add default via 10.36.0.1 dev eth0 table main"
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey=mykey)
        stdin, stdout, stderr = client.exec_command(cmd1)
        stdin1, stdout1, stderr1 = client.exec_command(cmd2)
        result = stdout.read()
        print(result)
        result1 = stdout1.read()
        print(result1)
        client.close()
        sleep(120)
        print("------------------------------------------------")
        print("|           Enabling Parental Control feature now         |")
        print("------------------------------------------------")
        print("Enabling Parental Control Services under subscriber services properties \n")
        subscriber_site_ref = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber",grid_vip=config.master0mgmt)
        print("reference of subscriber_site", subscriber_site_ref)
        ref = json.loads(subscriber_site_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(subscriber_properties_data),grid_vip=config.master0mgmt)
        print("Response of newly added data ", json.loads(response))
        ref1 = ref + "?_return_fields=enable_parental_control,proxy_url,proxy_username,proxy_password,category_url,cat_acctname,cat_password,cat_update_frequency,pc_zone_name"
        check_data = ib_NIOS.wapi_request('GET', object_type=ref1,grid_vip=config.master0mgmt)
        check_data = json.loads(check_data)
        check_data.pop('_ref')
        print("Validating data before comparing it with data provided for Put operation", check_data)
        print("Validating original data before comparing it with data got after Put operation",
              subscriber_properties_data)
        if (check_data == subscriber_properties_data):
            assert True
            print(" Test case 1 passed ")
        else:
            assert False

    @pytest.mark.run(order=2)
    def test_002_add_site_under_subscriber_site(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 2  Started Executing                      ####")
        print("###############################################################################")
        sleep(20)
	get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns',grid_vip=config.master0mgmt)
	data = {"dns_query_source_interface":"ANY","use_mgmt_port":True,"use_mgmt_ipv6_port":True}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data),grid_vip=config.master0mgmt)
        print(response)
        print("adding subscriber site under subscriber site \n ")
        site_data_new = {"blocking_ipv4_vip1": "2.4.5.6", "maximum_subscribers": 898989,"msps": [{"ip_address": "10.196.128.13"}], "name": "mysite1", "nas_port": 1813,"spms": [{"ip_address": "10.12.11.11"}]}
        subscriber_site_ref = ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(site_data),grid_vip=config.master0mgmt)
        # subscriber_site_ref=json.dumps(subscriber_site_ref)
        print(subscriber_site_ref)
        subscriber_site_ref = json.loads(subscriber_site_ref)
        print(subscriber_site_ref)
        ref1 = subscriber_site_ref + "?_return_fields=blocking_ipv4_vip1,maximum_subscribers,members,name,nas_port,msps,spms,nas_gateways"
        print(ref1)
        check_data = ib_NIOS.wapi_request('GET', object_type=ref1,grid_vip=config.master0mgmt)
        print(check_data)
        check_data = json.loads(check_data)
        check_data.pop('_ref')
        check_data.pop('members')
        check_data.pop('nas_gateways')
        check_data = json.dumps(check_data)
        check_data = json.loads(check_data)
        site_data_new = json.dumps(site_data_new)
        site_data_new = json.loads(site_data_new)
        print("Validating data before comparing it with data provided for Put operation", check_data)
        print("Data sent to update ", site_data_new)
        if (check_data != site_data_new):
            assert True
            print(" Test case 2 passed ")
        else:
            assert False

    @pytest.mark.run(order=3)
    def test_003_modifying_in_grid_dns_properties(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 3  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        grid_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns",grid_vip=config.master0mgmt)
        grid_ref = json.loads(grid_ref)
        grid_dns_ref = grid_ref[0]['_ref']
        fields = grid_dns_ref + "?_return_fields=allow_query,allow_update,forwarders,logging_categories,allow_recursive_query"
        grid_fields_data = ib_NIOS.wapi_request('GET', object_type=fields,grid_vip=config.master0mgmt)
        print("before editing grid : dns properties", grid_fields_data)
        data = {"allow_query": [], "allow_recursive_query": True, "allow_update": [], "forwarders": [config.forwarder],
                "logging_categories": {"log_client": False, "log_config": False, "log_database": False,
                                       "log_dnssec": False, "log_dtc_gslb": False, "log_dtc_health": False,
                                       "log_general": False, "log_lame_servers": False, "log_network": False,
                                       "log_notify": False, "log_queries": False, "log_query_rewrite": False,
                                       "log_rate_limit": False, "log_resolver": False, "log_responses": True,
                                       "log_rpz": True, "log_security": False, "log_update": True,
                                       "log_update_security": False, "log_xfer_in": False, "log_xfer_out": False}}
        condition = ib_NIOS.wapi_request('PUT', ref=grid_dns_ref, fields=json.dumps(data),grid_vip=config.master0mgmt)
        print(condition)
        grid = ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.master0mgmt)
        ref = json.loads(grid)[0]['_ref']
        publish = {"member_order": "SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=publish_changes",
                                               fields=json.dumps(publish),grid_vip=config.master0mgmt)
        time.sleep(1)
        request_restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=requestrestartservicestatus",grid_vip=config.master0mgmt)
        restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=restartservices",grid_vip=config.master0mgmt)
        time.sleep(1)
        grid_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns",grid_vip=config.master0mgmt)
        grid_ref = json.loads(grid_ref)
        grid_dns_ref = grid_ref[0]['_ref']
        new_fields = grid_dns_ref + "?_return_fields=allow_query,allow_update,forwarders,logging_categories,allow_recursive_query"
        new_grid_fields_data = ib_NIOS.wapi_request('GET', object_type=new_fields,grid_vip=config.master0mgmt)
        print("data data performed from GET operation after Modifying from GET operation after Modifying",
              new_grid_fields_data)
        print("data obtained from GET operation before Modifying", grid_fields_data)
        if (grid_fields_data != new_grid_fields_data):
            assert True
            print("Successfully Modified GRID DNS Properties ")
        else:
            assert False
            print("unable to Modify GRID_DNS Properties ")

    @pytest.mark.run(order=4)
    def test_004_start_IPv4_DHCP_DCA_ENABLE_RPZ_LOGGING_and_service(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 4  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        logging.info("start the ipv4 service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.master0mgmt)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        ref1 = ref1 + "?_return_fields=enable_dhcp"
        print("==========================", ref1)
        member_dhcp_data = ib_NIOS.wapi_request('GET', object_type=ref1,grid_vip=config.master0mgmt)
        print("---------------------------", member_dhcp_data)
        data = {"enable_dhcp": True}
        response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data), grid_vip=config.master0mgmt)
        print(response)
        grid = ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.master0mgmt)
        ref = json.loads(grid)[0]['_ref']
        publish = {"member_order": "SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=publish_changes",
                                               fields=json.dumps(publish),grid_vip=config.master0mgmt)
        time.sleep(1)
        request_restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=requestrestartservicestatus",grid_vip=config.master0mgmt)
        restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=restartservices",grid_vip=config.master0mgmt)
        time.sleep(1)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.master0mgmt)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        ref1 = ref1 + "?_return_fields=enable_dhcp"
        print("==========================", ref1)
        new_member_dhcp_data = ib_NIOS.wapi_request('GET', object_type=ref1,grid_vip=config.master0mgmt)
        new_member_dhcp_data = json.loads(new_member_dhcp_data)
        if (new_member_dhcp_data["enable_dhcp"] == data["enable_dhcp"]):
            assert True
            print("Successfully Modified GRID DNS Properties ")
            print("Test Case 04 Execution Completed")
        else:
            assert False
            print("unable to Modify GRID_DNS Properties ")
            print("Test Case 04 Execution Failed")
        restart_services()
        sleep(60)
        print("------------------------------------------------")
        print("|           Test Case for IPV4 DNS Service Started            |")
        print("------------------------------------------------")
        logging.info("start the ipv4 DNS service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.master0mgmt)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"allow_recursive_query": True, "forwarders": [config.forwarder]}
        response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data),grid_vip=config.master0mgmt)
        for read in response:
            assert True
        print("------------------------------------------------")
        print("|           Test Case for DCA Service Enabling Started            |")
        print("------------------------------------------------")
        logging.info("Start DCA Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns",grid_vip=config.master0mgmt)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print(ref1)
        restart_services()
        sleep(60)
        logging.info("Modify a enable_dns")
        data = {"enable_dns_cache_acceleration": True}
        response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data),grid_vip=config.master0mgmt)

        sleep(60)
        print("------------------------------------------------")
        print("|           Test Case  Started for Enabling Recursive Query and Forwarders           |")
        print("------------------------------------------------")
        print("############################Enabling Recursive Query and Adding Forwarders ###########################")
        logging.info("start the ipv4 DNS service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.master0mgmt)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"allow_recursive_query": True, "forwarders": [config.forwarder]}
        response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data),grid_vip=config.master0mgmt)
        for read in response:
            assert True
        restart_services()
        sleep(60)
        print("------------------------------------------------")
        print("|           Test Case setup for Enabling Logging Categories started            |")
        print("------------------------------------------------")
        print("############################Enabling Logging Categories ###########################")
        logging.info("start the ipv4 DNS service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.master0mgmt)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"allow_recursive_query": True,
                "logging_categories": {"log_rpz": True, "log_queries": True, "log_responses": True}}
        response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data),grid_vip=config.master0mgmt)
        for read in response:
            assert True
        restart_services()
        sleep(60)
        logging.info("start the ipv4 DNS service")
        print("------------------------------------------------")
        print("|           Test Case setup Started for Adding Resolvers            |")
        print("------------------------------------------------")
        print("############################ Adding Resolvers ###########################")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.master0mgmt)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        data = {"dns_resolver_setting": {"resolvers": ["127.0.0.1", config.resolver]}}
        response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data),grid_vip=config.master0mgmt)
        for read in response:
            assert True
        sleep(60)

    @pytest.mark.run(order=5)
    def test_005_start_subscriber_services_and_symantec_data_download(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 5  Started Executing                      ####")
        print("###############################################################################")
        '''Update Interim Accounting Interval'''
        sleep(5)
        print("Update Interim Accounting Interval to 60min")
        get_ref = ib_NIOS.wapi_request('GET', object_type='parentalcontrol:subscriber',grid_vip=config.master0mgmt)
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps({"interim_accounting_interval":60}),grid_vip=config.master0mgmt)
        if type(response) == tuple:
            if response2[0]==400 or response2[0]==401:
                display_msg("Failure: Updating Interim Accounting Interval to 60min")
                assert False
        sleep(10)
        print("------------------------enabling subscriber collection services------------------------------")
        subscriber_services = ib_NIOS.wapi_request('GET', object_type="member:parentalcontrol",grid_vip=config.master0mgmt)
        subscriber_services = json.loads(subscriber_services)
        print(subscriber_services)
        print("__________________________________")
        subscriber_ref = subscriber_services[0]['_ref']
        data = {"enable_service": True}
        enable_subscriber_ref = ib_NIOS.wapi_request('PUT', ref=subscriber_ref, fields=json.dumps(data),grid_vip=config.master0mgmt)
        print(enable_subscriber_ref)
        com = json.loads(enable_subscriber_ref) + "?_return_fields=enable_service"
        print(com)
        new_member_ref = ib_NIOS.wapi_request('GET', object_type=com,grid_vip=config.master0mgmt)
        new_member_ref = json.loads(new_member_ref)
        if (new_member_ref["enable_service"] == data["enable_service"]):
            assert True
            print("Subscriber Collection Service Enabled : Test case 05 passed")
        else:
            assert False
        ########################Symantec Downloading Data ##########################
    #    print("------------------------------------------------")
    #    print("|           Test Case setup Started  for Symantec Data Download          |")
    #    print("------------------------------------------------")
    #     '''Start capturing ufsclient logs'''
	# """
	# sleep_interval = 600
    #     count = 0
    #     while True:
    #         if count > 6:
    #             display_msg("Failure: Failed to start Subscriber Collection Service")
    #             stop_syslog('/storage/symantec/log/ufclient.log')
    #             assert False
    #             break
	#     else:
	# 	cmd1 = "cat /storage/symantec/log/ufclient.log |  grep -i "'*** ufclient completed ***'""
	# 	print (cmd1)
	# 	client = paramiko.SSHClient()
	# 	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	# 	privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
	# 	mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
	# 	client.connect(config.grid_vip, username='root', pkey=mykey)
	# 	stdin, stdout, stderr = client.exec_command(cmd1)
	# 	#stdin1, stdout1, stderr1 = client.exec_command(cmd2)
	# 	result = stdout.read()
	# 	print (result)
	# 	if result :
	# 		display_msg("Subscriber Collection Service Started")
	# 		break
	# 		count=+1
	# 		sleep(sleep_interval)
					
					
    #         #if not validate_syslog("/storage/symantec/log/ufclient.log", "*** ufclient completed ***"):
    #         #    sleep(sleep_interval)
    #     """         
    #    start_syslog('/storage/symantec/log/ufclient.log')
    #    print("Sleep for 3600 seconds for the Subscriber collection service to start")
    #    sleep(3600)
	
    #    '''Validate the ufsclient logs for the succesful starting of subscriber collection service'''
    #    if not validate_syslog("/storage/symantec/log/ufclient.log", "*** ufclient completed ***"):
    #        print("Failure: Subscriber Collection Service is not started")
    #        stop_syslog('/storage/symantec/log/ufclient.log')
    #        assert False
    #    print("Subscriber Collection Service Started")

    #    '''Stop capturing ufsclient logs'''
    #    stop_syslog('/storage/symantec/log/ufclient.log')

    @pytest.mark.run(order=6)
    def test_006_start_IPv4_DNS_service(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 6  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        logging.info("start the ipv4 DNS service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.master0mgmt)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print(ref1)
        data = {"enable_dns": True}
        response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data), grid_vip=config.master0mgmt)
        sleep(20)
        logging.info(response)
        com = json.loads(response) + "?_return_fields=enable_dns"
        print(com)
        new_member_ref = ib_NIOS.wapi_request('GET', object_type=com,grid_vip=config.master0mgmt)
        new_member_ref = json.loads(new_member_ref)
        if (new_member_ref["enable_dns"] == data["enable_dns"]):
            assert True
            print("DNS Service Enabled : Test case 06 passed")
        else:
            assert False
            print("errored out while enabling DNS service : Test Case 06 Execution Failed")

    @pytest.mark.run(order=7)
    def test_007_create_IPv4_network_without_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 7  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        logging.info(
            "Create an ipv4 network default network view and with out Extensible attributes of Subscriber services")
        # data = {"network": "10.0.0.0/8","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}]}
        network_data = {"network": "20.0.0.0/8",
                        "members": [{"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                        "extattrs": {"IB Discovery Owned": {"value": "ib"}}}
        response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(network_data),grid_vip=config.master0mgmt)
        print(response)
        read = re.search(r'201', response)
        for read in response:
            assert True
        print("Created the ipv4network 20.0.0.0/8 in default view")
        logging.info("Restart DHCP Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.master0mgmt)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order": "SIMULTANEOUSLY", "restart_option": "FORCE_RESTART", "service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=restartservices",
                                               fields=json.dumps(data),grid_vip=config.master0mgmt)
        logging.info("Wait for 15 sec.,")
        sleep(15)
        new_data = ib_NIOS.wapi_request('GET', object_type="network",grid_vip=config.master0mgmt)
        new_data = json.loads(new_data)
        print("result of adding ipv4 network", new_data)
        sleep(20)  # wait for 20 secs for the member to get started
        if (new_data[0]['network'] == network_data['network']):
            assert True
            print("Test Case 07 Execution Completed")
        else:
            assert False
            print("Test Case 07 Execution Failed")

    @pytest.mark.run(order=8)
    def test_008_validate_added_ipv4_network_without_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 8  Started Executing                      ####")
        print("###############################################################################")
        print("Test case to validate IPV4 network added without EA ")
        sleep(10)
        data = show_subscriber_secure_data()
        result = re.search("20.0.0.0", data)
        if (result == None):
            assert True
            print("Test case 08 passed")
        else:
            assert False
            print("Test case 08 failed")

    @pytest.mark.run(order=9)
    def test_009_create_IPv6_network_without_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 9  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        print("Create an ipv6 network default network view and with out Extensible attributes of Subscriber services")
        # data = {"network": "10.0.0.0/8","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vivi p}]}
        network_data = {"network": "2620:10a:6000:2500::/64", "network_view": "default",
                        "members": [{"ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                        "extattrs": {"IB Discovery Owned": {"value": "ib"}}}
        response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(network_data),
                                        grid_vip=config.master0mgmt)
        print(response)
        read = re.search(r'201', response)
        for read in response:
            assert True
        print("Created the ipv6network with given data in default view")
        logging.info("Restart DHCP Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.master0mgmt)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order": "SIMULTANEOUSLY", "restart_option": "FORCE_RESTART", "service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=restartservices",
                                               fields=json.dumps(data), grid_vip=config.master0mgmt)
        logging.info("Wait for 20 sec.,")
        new_data = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.master0mgmt)
        new_data = json.loads(new_data)[0]['network'].encode('utf-8')
        sleep(20)  # wait for 20 secs for the member to get started
        # print ("-------------------------------",new_data)
        # print ("******************************",network_data['network'])
        # print ("type:",type(new_data.encode('utf-8')))
        # print ("hype:",type(network_data['network']))
        if (new_data == network_data['network']):
            assert True
            print("Test Case 09 Execution Completed")
        else:
            assert False
            print("Test Case 09 Execution Failed")

    @pytest.mark.run(order=10)
    def test_010_validate_added_ipv6_network_without_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 10  Started Executing                      ####")
        print("###############################################################################")
        print("Test case to validate IPV6 network added ")
        sleep(10)
        data = show_subscriber_secure_data()
        result = re.search("2620:10a:6000:2500::", data)
        if (result == None):
            assert True
            print("Test case 10 passed")
        else:
            assert False
            print("Test case 10 failed")

    @pytest.mark.run(order=11)
    def test_011_create_IPv4_Range_without_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 11 Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        logging.info("Create an IPv4 range in defaultnetwork view")
        network_data = {"network": "20.0.0.0/8", "start_addr": "20.0.0.10", "end_addr": "20.0.0.100",
                        "network_view": "default", "member": {"_struct": "dhcpmember"}}
        response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(network_data),
                                        grid_vip=config.master0mgmt)
        print(response)
        read = re.search(r'201', response)
        for read in response:
            assert True
        print("Created the ipv4 prefix range with bits 8  in default view")
        logging.info("Restart DHCP Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.master0mgmt)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order": "SIMULTANEOUSLY", "restart_option": "FORCE_RESTART", "service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=restartservices",
                                               fields=json.dumps(data), grid_vip=config.master0mgmt)
        logging.info("Wait for 20 sec.,")
        new_data = ib_NIOS.wapi_request('GET', object_type="range", grid_vip=config.master0mgmt)
        new_data = json.loads(new_data)
        sleep(20)  # wait for 20 secs for the member to get started
        if (new_data[0]['network'] == network_data['network']):
            assert True
            print("Test Case 11 Execution Completed")
        else:
            assert False
            print("Test Case 11 Execution Failed")

    @pytest.mark.run(order=12)
    def test_012_validate_added_IPV4_range_without_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 12  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        res = range(10, 15)
        for i in res:
            print("Test case to validate IPV6 network added ")
            data = show_subscriber_secure_data()
            result = re.search("20.0.0." + str(i), data)
        if (result == None):
            assert True
            print("Test case 12 passed")
        else:
            assert False
            print("Test case 12 failed")

    @pytest.mark.run(order=13)
    def test_013_create_IPv6_Range_without_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 13  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        logging.info("Create an IPv4 range in defaultnetwork view")
        network_data = {"network": "2620:10a:6000:2500::/64", "start_addr": "2620:10a:6000:2500::10",
                        "end_addr": "2620:10a:6000:2500::100", "network_view": "default",
                        "member": {"_struct": "dhcpmember"}}
        response = ib_NIOS.wapi_request('POST', object_type="ipv6range", fields=json.dumps(network_data),
                                        grid_vip=config.master0mgmt)
        print(response)
        read = re.search(r'201', response)
        for read in response:
            assert True
        print("Created the ipv6 prefix range with bits 8  in default view")
        logging.info("Restart DHCP Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.master0mgmt)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order": "SIMULTANEOUSLY", "restart_option": "FORCE_RESTART", "service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=restartservices",
                                               fields=json.dumps(data), grid_vip=config.master0mgmt)
        new_data = ib_NIOS.wapi_request('GET', object_type="ipv6range", grid_vip=config.master0mgmt)
        new_data = json.loads(new_data)
        logging.info("Wait for 20 sec.,")
        sleep(20)  # wait for 20 secs for the member to get started
        if (new_data[0]['network'] == network_data['network']):
            assert True
            print("Test Case 13 Execution Completed")
        else:
            assert False
            print("Test Case 13 Execution Failed")

    @pytest.mark.run(order=14)
    def test_014_validate_added_IPV6_range_without_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 14  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        res = range(10, 12)
        for i in res:
            print("Test case to validate IPV6 network added ")
            data = show_subscriber_secure_data()
            result = re.search("2620:10a:6000:2500::" + str(i), data)
            print(result)
            if (result == None):
                assert True
                print("Test case 14 passed")
            else:
                assert False
                print("Test case 14 failed")

    @pytest.mark.run(order=15)
    def test_015_add_IPV4fixed_address_without_subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 15  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("Create an IPv4 fixed address in defaultnetwork view")
        network_data = {"ipv4addr": "20.0.0.1", "network_view": "default", "mac": "11:11:11:11:11:11",
                        "extattrs": {"IB Discovery Owned": {"value": "ib2"}}}
        response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(network_data),
                                        grid_vip=config.master0mgmt)
        print(response)
        read = re.search(r'201', response)
        for read in response:
            assert True
        print("Created the ipv4 fixed address in default view")
        logging.info("Restart DHCP Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.master0mgmt)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order": "SIMULTANEOUSLY", "restart_option": "FORCE_RESTART", "service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=restartservices",
                                               fields=json.dumps(data), grid_vip=config.master0mgmt)
        new_data = ib_NIOS.wapi_request('GET', object_type="fixedaddress", grid_vip=config.master0mgmt)
        new_data = json.loads(new_data)
        logging.info("Wait for 20 sec.,")
        sleep(20)  # wait for 20 secs for the member to get started
        print(new_data[0])
        if (new_data[0]['ipv4addr'] == network_data['ipv4addr']):
            assert True
            print("Test Case 15 Execution Completed")
        else:
            assert False
            print("Test Case 15 Execution Failed")

    @pytest.mark.run(order=16)
    def test_016_validate_added_IPV4_fixedaddress_without_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 16  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        print("Test case to validate IPV4 fixed address added ")
        data = show_subscriber_secure_data()
        result = re.search("20.0.0.22", data)
        print(result)
        if (result == None):
            assert True
            print("Test case 16 passed")
        else:
            assert False
            print("Test case 16 failed")

    @pytest.mark.run(order=17)
    def test_017_add_IPV6fixed_address_without_subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 17  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("Create an IPv6 fixed in defaultnetwork view")
        network_data = {"ipv6addr": "2620:10a:6000:2500:230:48ff:fed5:d928", "network_view": "default",
                        "duid": "11:12:11:13:11:14", "extattrs": {"IB Discovery Owned": {"value": "ipv6"}}}
        response = ib_NIOS.wapi_request('POST', object_type="ipv6fixedaddress", fields=json.dumps(network_data),
                                        grid_vip=config.master0mgmt)
        print(response)
        read = re.search(r'201', response)
        for read in response:
            assert True
        print("Created the ipv4 prefix range with bits 8  in default view")
        logging.info("Restart DHCP Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.master0mgmt)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order": "SIMULTANEOUSLY", "restart_option": "FORCE_RESTART", "service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=restartservices",
                                               fields=json.dumps(data), grid_vip=config.master0mgmt)
        new_data = ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress", grid_vip=config.master0mgmt)
        new_data = json.loads(new_data)
        print('===================', new_data)
        logging.info("Wait for 20 sec.,")
        sleep(20)  # wait for 20 secs for the member to get started
        if (new_data[0]['ipv6addr'] == network_data['ipv6addr']):
            assert True
            print("Test Case 17 Execution Completed")
        else:
            assert False
            print("Test Case 17 Execution Failed")

    @pytest.mark.run(order=18)
    def test_018_validate_added_IPV6_fixedaddress_without_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 18  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        print("Test case to validate IPV6 fixed address added ")
        data = show_subscriber_secure_data()
        print(data)
        result = re.search("2620:10a:6000:2500:230:48ff:fed5:d928", data)
        print(result)
        if (result == None):
            assert True
            print("Test case 18 passed")
        else:
            assert False
            print("Test case 18 failed")

    @pytest.mark.run(order=19)
    def test_019_add_reservation_address_without_subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                Test Case 19  Started Executing                        ####")
        print("###############################################################################")
        sleep(5)
        print("Adding Reservation Address without Subscriber Services")
        print("test case Pending since bug raised for Reservation Address WAPI Object : NIOS-71006")

    @pytest.mark.run(order=20)
    def test_020_delete_subscriber_records_without_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 20  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        list1 = ['ipv6network', 'network']
        for i in list1:
            reference = get_ref = ib_NIOS.wapi_request('GET', object_type=str(i),grid_vip=config.master0mgmt)
            if reference != "[]":
                reference = json.loads(reference)
                print(reference)
                for ref in reference:
                    get_ref = ref["_ref"]
                    reference = get_ref = ib_NIOS.wapi_request('DELETE', object_type=get_ref,grid_vip=config.master0mgmt)
                    print(reference)
                    sleep(5)
                    data = {"member_order": "SIMULTANEOUSLY", "restart_option": "FORCE_RESTART",
                            "service_option": "ALL"}
                    request_restart = ib_NIOS.wapi_request('POST', object_type=reference + "?_function=restartservices",
                                                           fields=json.dumps(data), grid_vip=config.master0mgmt)
                    sleep(5)
                    if type(reference) != tuple:
                        print("Test case 20 execution passed")
                        assert True
                    else:
                        print("Test case 20 execution failed")
                        assert False
            else:
                print("No records to delete")
                assert True

    @pytest.mark.run(order=21)
    def test_021_create_IPv4_network_with_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 21  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        logging.info(
            "Create an ipv4 network default network view and with Extensible attributes of Subscriber services")
        # data = {"network": "10.0.0.0/8","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.master01lan1v4}]}
	get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.master0mgmt)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        data={"allow_recursive_query":True,"forwarders":[config.forwarder]}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.master0mgmt)
        network_data = {"network": "10.0.0.0/8",
                        "members": [{"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                        "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                     "IB Discovery Owned": {"value": "ib"},
                                     "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                     "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                     "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                     "Site": {"value": "site"}, "State": {"value": "state"},
                                     "Subscriber-Secure-Policy": {"value": "ff"}, "User-Name": {"value": "user123"},
                                     "VLAN": {"value": "vlan"}, "White-List": {"value": "bbc.com"},
                                     "Black-List": {"value": "facebook.com"}}}
        print(":::::::::::::::::::::", network_data)
        response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(network_data),
                                        grid_vip=config.master0mgmt)
        print(response)
        read = re.search(r'201', response)
        for read in response:
            assert True
        print("Created the ipv4network 10.0.0.0/8 in default view")
        logging.info("Restart DHCP Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.master0mgmt)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order": "SIMULTANEOUSLY", "restart_option": "FORCE_RESTART", "service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=restartservices",
                                               fields=json.dumps(data), grid_vip=config.master0mgmt)
        # print ("result of adding ipv4 network",new_data)
        sleep(20)  # wait for 20 secs for the member to get started
        logging.info("Wait for 20 sec.,")
        new_data = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.master0mgmt)
        new_data = json.loads(new_data)
        sleep(2)
        if (new_data[0]['network'] == network_data['network']):
            assert True
            print("Test Case 21 Execution Completed")
        else:
            assert False
            print("Test Case 21 Execution Failed")

    @pytest.mark.run(order=22)
    def test_022_validate_added_ipv4_network_with_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 22  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        print("Test case to validate IPV4 network added ")
        data = show_subscriber_secure_data()
        result = re.search("10.0.0.0", data)
        if (result != None):
            assert True
            print("Test case 22 passed")
        else:
            assert False
            print("Test case 22 failed")

    @pytest.mark.run(order=23)
    def test_023_query_parental_control_domain_playboy_com_ipv4(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 23  Started Executing                      ####")
        print("###############################################################################")
        sleep(20)
        print("This test performs dig by logging in to Client IP")
        query_list = ['playboy.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.grid_vip + " " + str(record) + " +noedns -b 10.36.0.151"
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
	flag=False
	for line in output:
	    print (line)
        #print(output)
	    if "connection timed out; no servers could be reached" in line:
	    	assert False
	    if site_data['blocking_ipv4_vip1'] in line:
		flag=True
		break
	if not flag:
		assert False

    @pytest.mark.run(order=24)
    def test_024_query_parental_control_domain_facebook_com_ipv4(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 24  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        print("This test performs dig by logging in to Client IP and checks for Blacklist DOmain in DIG output")
        query_list = ['facebook.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.grid_vip + " " + str(record) + " +noedns -b 10.36.0.151"
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        sleep(5)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        log_out = commands.getoutput(sys_log_validation)
        print(log_out)
	flag=False
        for line in output:
            print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
            if site_data['blocking_ipv4_vip1'] in line:
                flag=True
                break
        if not flag:
                assert False


    @pytest.mark.run(order=25)
    def test_025_query_parental_control_domain_beer_com_ipv4(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 25  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        print("This test performs dig by logging in to Client IP")
        query_list = ['beer.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.grid_vip + " " + str(record) + " +noedns -b 10.36.0.151"
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        print(output)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        out1 = commands.getoutput(sys_log_validation)
        print(out1)
	flag=False
        assert re.search(r'.*10.*196.*', out1)
	for line in output:
            print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
            if "10.196." in line:
                flag=True
                break
        if not flag:
                assert False


    @pytest.mark.run(order=26)
    def test_026_query_parental_control_domain_playboy_com_ipv4(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 26  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        print("This test performs dig by logging in to Client IP")
        query_list = ['playboy.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.grid_vip + " " + str(record) + " +noedns -b 10.36.0.151"
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        print(output)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        out1 = commands.getoutput(sys_log_validation)
        print(out1)
        logging.info(out1)
        assert re.search(site_data['blocking_ipv4_vip1'], out1)
	flag=False
	for line in output:
            print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
            if site_data['blocking_ipv4_vip1'] in line:
                flag=True
                break
        if not flag:
                assert False

    @pytest.mark.run(order=27)
    def test_027_query_parental_control_domain_cnn_com_ipv4(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 27  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        print("This test performs dig by logging in to Client IP")
        query_list = ['cnn.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.grid_vip + " " + str(record) + " +noedns -b 10.36.0.151"
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        print(output)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        out1 = commands.getoutput(sys_log_validation)
        print(out1)
        logging.info(out1)
        assert re.search(r'.*10.*196.*', out1)
	flag=False
        for line in output:
            print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
            if "10.196." in line:
                flag=True
                break
        if not flag:
                assert False


    @pytest.mark.run(order=28)
    def test_028_query_parental_control_domain_nxdomain_com_ipv4(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 28  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        print("This test performs dig by logging in to Client IP")
        query_list = ['rpz7']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.grid_vip + " " + str(record) + " +noedns -b 10.36.0.151"
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        print(output)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        out1 = commands.getoutput(sys_log_validation)
        print(out1)
        logging.info(out1)
	flag=False
        for line in output:
            print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
            if "NOERROR" in line:
                flag=True
                break
        if not flag:
                assert False


    @pytest.mark.run(order=29)
    def test_029_query_parental_control_domain_cnn_com_username_ipv4(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 29  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        print("This test performs dig by logging in to Client IP")
        query_list = ['cnn.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.grid_vip + " " + str(record) + " +noedns -b 10.36.0.151"
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        print(output)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        out1 = commands.getoutput(sys_log_validation)
        print(out1)
        logging.info(out1)
        assert re.search(r'.*10.*', out1)
	flag=False
        for line in output:
            print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
            if "10.196" in line:
                flag=True
                break
        if not flag:
                assert False

    @pytest.mark.run(order=30)
    def test_030_query_parental_control_domain_bbc_com_ipv4(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 30  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        print("This test performs dig by logging in to Client IP")
        query_list = ['bbc.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.grid_vip + " " + str(record) + " +noedns -b 10.36.0.151"
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        print(output)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        out1 = commands.getoutput(sys_log_validation)
        print(out1)
        logging.info(out1)
        assert re.search(".*10.*", out1)
	flag=False
        for line in output:
            print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
            if "NOERROR" in line:
                flag=True
                break
        if not flag:
                assert False

    @pytest.mark.run(order=31)
    def test_031_create_IPv4_Range_with_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 31  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        try:
            logging.info("Create an IPv4 range in defaultnetwork view")
            network_data = {"network": "10.0.0.0/8", "start_addr": "10.0.0.10", "end_addr": "20.0.0.100",
                            "network_view": "default", "member": {"_struct": "dhcpmember",
                                                                  "extattrs": {"IB Discovery Owned": {"value": "ib2"},
                                                                               "PC-Category-Policy": {
                                                                                   "value": "00000000000000000000000000000001"},
                                                                               "Parental-Control-Policy": {
                                                                                   "value": "00000000000000000000000000020040"},
                                                                               "Proxy-All": {"value": "True"},
                                                                               "Site": {"value": "site2"},
                                                                               "Subscriber-Secure-Policy": {
                                                                                   "value": "ff"},
                                                                               "User-Name": {"value": "user2"},
                                                                               "White-List": {"value": "qa2.com"},
                                                                               "Black-List": {
                                                                                   "value": "facebook.com"}}}}
            response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(network_data),
                                            grid_vip=config.master0mgmt)
            print(response)
            read = re.search(r'201', response)
            for read in response:
                assert False
            print("Created the ipv4 prefix range with bits 8  in default view , where EA is not Supported for range ")
        except TypeError:
            assert True
            print(
                "Unable to create EA with subscriber values for Range , since it has no support : Test 27 Negative scenario passed")

    @pytest.mark.run(order=32)
    def test_032_validate_added_IPV4_range_with_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 32  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        res = range(11, 12)
        for i in res:
            print("Test case to validate IPV4 network added ")
            data = show_subscriber_secure_data()
            result = re.findall("10.0.0." + str(i), data)
            print("+++++++++++++++++++++++++++", str(result))
            if (result == []):
                assert True
                print("Test case 32 passed")
            else:
                assert False
                print("Test case 32 failed")


    @pytest.mark.run(order=33)
    def test_033_create_IPv6_network_with_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 33  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        logging.info(
            "Create an ipv6 network default network view and with Extensible attributes of Subscriber services")
        # data = {"network": "10.0.0.0/8","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vivi p}]}
        network_data = {"network": "2001:550:40a:2500::/64", "network_view": "default",
                        "members": [{"ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                        "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                     "IB Discovery Owned": {"value": "ib"},
                                     "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                     "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                     "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                     "Site": {"value": "site"}, "State": {"value": "state"},
                                     "Subscriber-Secure-Policy": {"value": "ff"}, "User-Name": {"value": "user123"},
                                     "VLAN": {"value": "vlan"}, "White-List": {"value": "bbc.com"},
                                     "Black-List": {"value": "facebook.com"}}}
        # 2620:10a:6000:2500::/64
        response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(network_data),
                                        grid_vip=config.master0mgmt)
        print(response)
        read = re.search(r'201', response)
        for read in response:
            assert True
        print("Created the ipv6network with given data in default view")
        logging.info("Restart DHCP Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.master0mgmt)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order": "SIMULTANEOUSLY", "restart_option": "FORCE_RESTART", "service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=restartservices",
                                               fields=json.dumps(data), grid_vip=config.master0mgmt)
        logging.info("Wait for 20 sec.,")
        sleep(20)  # wait for 20 secs for the member to get started
        new_data = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.master0mgmt)
        new_data = json.loads(new_data)[0]['network'].encode('utf-8')
        print(new_data)
        if (new_data == network_data['network']):
            assert True
            print("Test Case 33 Execution Completed")
        else:
            assert False
            print("Test Case 33 Execution Failed")

    @pytest.mark.run(order=34)
    def test_034_validate_added_ipv6_network_with_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 34  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        print("Test case to validate IPV6 network added ")
        data = show_subscriber_secure_data()
        result = re.search("2001:550:40a:2500::", data)
        if (result != None):
            assert True
            print("Test case 34 passed")
        else:
            assert False
            print("Test case 34 failed")


    @pytest.mark.run(order=35)
    def test_035_query_parental_control_domain_playboy_com_ipv6(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 35  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("This test performs dig by logging in to Client IP")
        query_list = ['playboy.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.master0mgmtv6 + " " + str(record) + " +noedns "
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
	flag=False
	for line in output:
            print ("This is line " + line)
            print("This is site_data " + site_data['blocking_ipv4_vip1'])
            if "connection timed out; no servers could be reached" in line:
                assert False
            if site_data['blocking_ipv4_vip1'] in line:
                flag=True
                break
        if not flag:
                assert False

    @pytest.mark.run(order=36)
    def test_036_query_parental_control_domain_facebook_com_ipv6(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 36  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("This test performs dig by logging in to Client IP and checks for Blacklist DOmain in DIG output")
        query_list = ['facebook.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.master0mgmtv6 + " " + str(record) + " +noedns " 
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        print(output)
        sleep(5)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        log_out = commands.getoutput(sys_log_validation)
        print(log_out)
	flag=False
        for line in output:
            print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
            if site_data['blocking_ipv4_vip1'] in line:
                flag=True
                break
        if not flag:
                assert False


    @pytest.mark.run(order=37)
    def test_037_query_parental_control_domain_beer_com_ipv6(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 37  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("This test performs dig by logging in to Client IP")
        query_list = ['beer.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.master0mgmtv6 + " " + str(record) + " +noedns "
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        print(output)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
	out1 = commands.getoutput(sys_log_validation)
        print(out1)
	flag=False
        #assert re.search(r'.*10.*196.*', out1)
	for line in output:
            print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
            if "SERVFAIL" in line:
                flag=True
                break
        if not flag:
                assert False

    @pytest.mark.run(order=38)
    def test_038_query_parental_control_domain_playboy_com_ipv6(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 38  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("This test performs dig by logging in to Client IP")
        query_list = ['playboy.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.master0mgmtv6 + " " + str(record) + " +noedns "
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        print(output)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        out1 = commands.getoutput(sys_log_validation)
	print(out1)
        logging.info(out1)
        assert re.search(site_data['blocking_ipv4_vip1'], out1)
	flag=False
	for line in output:
            print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
            if site_data['blocking_ipv4_vip1'] in line:
                flag=True
                break
        if not flag:
                assert False


    @pytest.mark.run(order=39)
    def test_039_query_parental_control_domain_cnn_com_ipv6(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 39  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("This test performs dig by logging in to Client IP")
        query_list = ['cnn.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.master0mgmtv6 + " " + str(record) + " +noedns "
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        #print(output)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        out1 = commands.getoutput(sys_log_validation)
	print (out1)
        #assert re.search(r'.*101.*', out1)
	flag=False
        for line in output:
	    #print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
                break

    @pytest.mark.run(order=40)
    def test_040_query_parental_control_domain_nxdomain_com_ipv6(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 40  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("This test performs dig by logging in to Client IP")
        query_list = ['rpz7']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.master0mgmtv6 + " " + str(record) + " +noedns "
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        print(output)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        out1 = commands.getoutput(sys_log_validation)
        print(out1)
        logging.info(out1)
	flag=False
        for line in output:
            print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
		break


    @pytest.mark.run(order=41)
    def test_041_query_parental_control_domain_cnn_com_username_ipv6(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 41  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("This test performs dig by logging in to Client IP")
        query_list = ['cnn.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.master0mgmtv6 + " " + str(record) + " +noedns "
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        print(output)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        out1 = commands.getoutput(sys_log_validation)
        print(out1)
        logging.info(out1)
        assert re.search(r'.*user*', out1)
	flag=False
        for line in output:
            #print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False

    @pytest.mark.run(order=42)
    def test_042_query_parental_control_domain_bbc_com_ipv6(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 42  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("This test performs dig by logging in to Client IP")
        query_list = ['bbc.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.master0mgmtv6 + " " + str(record) + " +noedns "
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        print(output)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        out1 = commands.getoutput(sys_log_validation)
        print(out1)
        logging.info(out1)
	flag=False
        for line in output:
            print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
            if "bbc" in line:
                flag=True
                break
        if not flag:
                assert False



    @pytest.mark.run(order=43)
    def test_043_create_IPv6_Range_with_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 43  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        try:
            logging.info("Create an IPv6 range in defaultnetwork view")
            network_data = {"network": "2001:550:40a:2500::/64", "start_addr": "2001:550:40a:2500::10",
                            "end_addr": "2001:550:40a:2500::100", "network_view": "default",
                            "member": {"_struct": "dhcpmember", "extattrs": {"IB Discovery Owned": {"value": "ib2"},
                                                                             "PC-Category-Policy": {
                                                                                 "value": "00000000000000000000000000000001"},
                                                                             "Parental-Control-Policy": {
                                                                                 "value": "00000000000000000000000000020040"},
                                                                             "Proxy-All": {"value": "True"},
                                                                             "Site": {"value": "site2"},
                                                                             "Subscriber-Secure-Policy": {
                                                                                 "value": "ff"},
                                                                             "User-Name": {"value": "user2"},
                                                                             "White-List": {"value": "bbc.com"},
                                                                             "Black-List": {"value": "facebook.com"}}}}
            response = ib_NIOS.wapi_request('POST', object_type="ipv6range", fields=json.dumps(network_data),
                                            grid_vip=config.master0mgmt)
            print(response)
            read = re.search(r'201', response)
            for read in response:
                assert False
            print("Created the ipv4 prefix range with bits 8  in default view , where EA is not Supported for range ")
        except TypeError:
            assert True
            print(
                "Unable to create EA with subscriber values for Range , since it has no support : Test 43 Negative scenario passed")

    @pytest.mark.run(order=44)
    def test_044_validate_added_IPV6_range_with_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 44  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        print("Test case to validate IPV6 network added ")
        data = show_subscriber_secure_data()
        sleep(10)
        print("LookFor : ", "2001:550:40a:2500::" )
        result = re.findall("2001:550:40a:2500::" , data)
        print("++++++++++++++++++++++++++++", result)
        if (result != []):
            assert True
            print("Test case 44 passed")
        else:
            assert False
            print("Test case 44 failed")

    @pytest.mark.run(order=45)
    def test_045_add_IPV4fixed_address_with_subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 45  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("Create an IPv4 fixed address in defaultnetwork view")
        network_data = {"ipv4addr": "10.36.0.151", "network_view": "default", "mac": "11:11:11:11:11:11",
                        "extattrs": {"IB Discovery Owned": {"value": "ib2"},
                                     "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                     "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                     "Proxy-All": {"value": "True"}, "Site": {"value": "site2"},
                                     "Subscriber-Secure-Policy": {"value": "ff"}, "User-Name": {"value": "user2"},
                                     "White-List": {"value": "bbc.com"}, "Black-List": {"value": "facebook.com"}}}
        response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(network_data),
                                        grid_vip=config.master0mgmt)
        print(response)
        read = re.search(r'201', response)
        for read in response:
            assert True
        print("Created the ipv4 fixed address in default view")
        logging.info("Restart DHCP Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.master0mgmt)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order": "SIMULTANEOUSLY", "restart_option": "FORCE_RESTART", "service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=restartservices",
                                               fields=json.dumps(data), grid_vip=config.master0mgmt)
        new_data = ib_NIOS.wapi_request('GET', object_type="fixedaddress", grid_vip=config.master0mgmt)
        new_data = json.loads(new_data)
        logging.info("Wait for 20 sec.,")
        sleep(20)  # wait for 20 secs for the member to get started
        print(new_data[0])
        if (new_data[0]['ipv4addr'] == network_data['ipv4addr']):
            assert True
            print("Test Case 45 Execution Completed")
        else:
            assert False
            print("Test Case 45 Execution Failed")

    @pytest.mark.run(order=46)
    def test_046_validate_added_IPV4_fixedaddress_with_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 46  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("Test case to validate IPV4 fixed address added ")
        data = show_subscriber_secure_data()
        result = re.match(".*10.36.0.151.*", data)
        if (result == None):
            assert True
            print("Test case 46 passed")
        else:
            assert False
            print("Test case 46 failed")

    @pytest.mark.run(order=47)
    def test_047_query_parental_control_domain_playboy_com_ipv4(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 47  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("This test performs dig by logging in to Client IP")
        query_list = ['playboy.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.grid_vip + " " + str(record) + " +noedns -b 10.36.0.151"
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
	flag=False
	for line in output:
	    print (line)
        #print(output)
	    if "connection timed out; no servers could be reached" in line:
	    	assert False
	    if site_data['blocking_ipv4_vip1'] in line:
		flag=True
		break
	if not flag:
		assert False

    @pytest.mark.run(order=48)
    def test_048_query_parental_control_domain_facebook_com_ipv4(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 48  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("This test performs dig by logging in to Client IP and checks for Blacklist DOmain in DIG output")
        query_list = ['facebook.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.grid_vip + " " + str(record) + " +noedns -b 10.36.0.151"
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        print(output)
        sleep(5)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        out1 = commands.getoutput(sys_log_validation)
        print(out1)
	flag=False
        for line in output:
            print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
            if site_data['blocking_ipv4_vip1'] in line:
                flag=True
                break
        if not flag:
                assert False

    @pytest.mark.run(order=49)
    def test_049_query_parental_control_domain_beer_com_ipv4(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 49  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("This test performs dig by logging in to Client IP")
        query_list = ['beer.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.grid_vip + " " + str(record) + " +noedns -b 10.36.0.151"
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        #print(output)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        out1 = commands.getoutput(sys_log_validation)
        print(out1)
        logging.info(out1)
	flag=False
	for line in output:
            print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
            if "NOERROR" in line:
                flag=True
                break
        if not flag:
                assert False	

    @pytest.mark.run(order=50)
    def test_050_query_parental_control_domain_playboy_com_ipv4(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 50  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("This test performs dig by logging in to Client IP")
        query_list = ['playboy.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.grid_vip + " " + str(record) + " +noedns -b 10.36.0.151"
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        print(output)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        out1 = commands.getoutput(sys_log_validation)
	assert re.search(site_data['blocking_ipv4_vip1'], out1)
	flag=False
	for line in output:
            print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
            if site_data['blocking_ipv4_vip1'] in line:
                flag=True
                break
        if not flag:
                assert False

    @pytest.mark.run(order=51)
    def test_051_query_parental_control_domain_cnn_com_ipv4(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 51  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("This test performs dig by logging in to Client IP")
        query_list = ['cnn.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.grid_vip + " " + str(record) + " +noedns -b 10.36.0.151"
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        print(output)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        out1 = commands.getoutput(sys_log_validation)
        print(out1)
        logging.info(out1)
	flag=False
        for line in output:
            print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
            if "NOERROR" in line:
                flag=True
                break
        if not flag:
                assert False

    @pytest.mark.run(order=52)
    def test_052_query_parental_control_domain_nxdomain_com_ipv4(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 52  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("This test performs dig by logging in to Client IP")
        query_list = ['rpz7']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.grid_vip + " " + str(record) + " +noedns -b 10.36.0.151"
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        print(output)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        out1 = commands.getoutput(sys_log_validation)
        print(out1)
        logging.info(out1)
	flag=False
        for line in output:
            print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
            if "NOERROR" in line:
                flag=True
                break
        if not flag:
                assert False

    @pytest.mark.run(order=53)
    def test_053_query_parental_control_domain_cnn_com_username_ipv4(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 53  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("This test performs dig by logging in to Client IP")
        query_list = ['cnn.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.grid_vip + " " + str(record) + " +noedns -b 10.36.0.151"
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        print(output)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        out1 = commands.getoutput(sys_log_validation)
        print(out1)
        logging.info(out1)
	assert re.search(r'.*user2*', out1)
	flag=False
        for line in output:
            print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
            if "NOERROR" in line:
                flag=True
                break
        if not flag:
                assert False

    @pytest.mark.run(order=54)
    def test_054_query_parental_control_domain_bbc_com_ipv4(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 54  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("This test performs dig by logging in to Client IP")
        query_list = ['bbc.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.grid_vip + " " + str(record) + " +noedns -b 10.36.0.151"
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        print(output)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        out1 = commands.getoutput(sys_log_validation)
        print(out1)
        logging.info(out1)
	assert re.search(".*10.*", out1)
	flag=False
        for line in output:
            print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
            if "NOERROR" in line:
                flag=True
                break
        if not flag:
                assert False

    @pytest.mark.run(order=55)
    def test_055_add_IPV6fixed_address_with_subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 55  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("Create an IPv6 fixed in defaultnetwork view")
        network_data = {"ipv6addr": "2001:550:40a:2500:230:48ff:fed5:d928", "network_view": "default",
                        "duid": "11:12:11:13:11:14", "extattrs": {"IB Discovery Owned": {"value": "ibv6"},
                                                                  "PC-Category-Policy": {
                                                                      "value": "00000000000000000000000000000001"},
                                                                  "Parental-Control-Policy": {
                                                                      "value": "00000000000000000000000000020040"},
                                                                  "Proxy-All": {"value": "True"},
                                                                  "Site": {"value": "sitev6"},
                                                                  "Subscriber-Secure-Policy": {"value": "ff"},
                                                                  "User-Name": {"value": "user123"},
                                                                  "White-List": {"value": "bbc.com"},
                                                                  "Black-List": {"value": "facebook.com"}}}
        response = ib_NIOS.wapi_request('POST', object_type="ipv6fixedaddress", fields=json.dumps(network_data),
                                        grid_vip=config.master0mgmt)
        print(response)
        read = re.search(r'201', response)
        for read in response:
            assert True
        print("Created the ipv4 prefix range with bits 8  in default view")
        logging.info("Restart DHCP Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.master0mgmt)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order": "SIMULTANEOUSLY", "restart_option": "FORCE_RESTART", "service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=restartservices",
                                               fields=json.dumps(data), grid_vip=config.master0mgmt)
        new_data = ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress", grid_vip=config.master0mgmt)
        new_data = json.loads(new_data)
        print('===================', new_data)
        logging.info("Wait for 20 sec.,")
        sleep(20)  # wait for 20 secs for the member to get started
        if (new_data[0]['ipv6addr'] == network_data['ipv6addr']):
            assert True
            print("Test Case 55 Execution Completed")
        else:
            assert False
            print("Test Case 55 Execution Failed")

    @pytest.mark.run(order=56)
    def test_056_validate_added_IPV6_fixedaddress_with_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 56  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("Test case to validate IPV6 fixed address added ")
        data = show_subscriber_secure_data()
        result = re.match(".*2001:550:40a:2500:230:48ff:fed5:d928.*", data)
        if (result == None):
            assert True
            print("Test case 56 passed")
        else:
            assert False
            print("Test case 56 failed")



    @pytest.mark.run(order=57)
    def test_057_query_parental_control_domain_playboy_com_ipv6(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 57  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("This test performs dig by logging in to Client IP")
        query_list = ['playboy.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.master0mgmtv6 + " " + str(record) + " +noedns "
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        flag=False
        for line in output:
            print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
            if site_data['blocking_ipv4_vip1'] in line:
                flag=True
                break
        if not flag:
                assert False


    @pytest.mark.run(order=58)
    def test_058_query_parental_control_domain_facebook_com_ipv6(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 58  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("This test performs dig by logging in to Client IP and checks for Blacklist DOmain in DIG output")
        query_list = ['facebook.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.master0mgmtv6 + " " + str(record) + " +noedns "
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        print(output)
        sleep(5)
	sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        log_out = commands.getoutput(sys_log_validation)
        print(log_out)
        flag=False
        for line in output:
            print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
            if site_data['blocking_ipv4_vip1'] in line:
                flag=True
                break
        if not flag:
                assert False

    @pytest.mark.run(order=59)
    def test_059_query_parental_control_domain_beer_com_ipv6(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 59  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("This test performs dig by logging in to Client IP")
        query_list = ['beer.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.master0mgmtv6 + " " + str(record) + " +noedns "
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        print(output)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        out1 = commands.getoutput(sys_log_validation)
        print(out1)
        logging.info(out1)
	flag=False
        #assert re.search(r'.*10.*196.*', out1)
        for line in output:
            print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
            if "SERVFAIL" in line:
                flag=True
                break
        if not flag:
                assert False


    @pytest.mark.run(order=60)
    def test_060_query_parental_control_domain_playboy_com_ipv6(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 60  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("This test performs dig by logging in to Client IP")
        query_list = ['playboy.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.master0mgmtv6 + " " + str(record) + " +noedns "
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        print(output)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        out1 = commands.getoutput(sys_log_validation)
        print(out1)
        logging.info(out1)
        assert re.search(site_data['blocking_ipv4_vip1'], out1)
	assert re.search(site_data['blocking_ipv4_vip1'], out1)
        flag=False
        for line in output:
            print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
            if site_data['blocking_ipv4_vip1'] in line:
                flag=True
                break
        if not flag:
                assert False

    @pytest.mark.run(order=61)
    def test_061_query_parental_control_domain_cnn_com_ipv6(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 61  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("This test performs dig by logging in to Client IP")
        query_list = ['cnn.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.master0mgmtv6 + " " + str(record) + " +noedns "
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        print(output)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        out1 = commands.getoutput(sys_log_validation)
	print (out1)
 	flag=False
        for line in output:
            #print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
                break

    @pytest.mark.run(order=62)
    def test_062_query_parental_control_domain_nxdomain_com_ipv6(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 62  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("This test performs dig by logging in to Client IP")
        query_list = ['rpz7']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.master0mgmtv6 + " " + str(record) + " +noedns "
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        print(output)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        out1 = commands.getoutput(sys_log_validation)
        print(out1)
        logging.info(out1)
        flag=False
        for line in output:
            print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
                break

    @pytest.mark.run(order=63)
    def test_063_query_parental_control_domain_cnn_com_username_ipv6(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 63  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("This test performs dig by logging in to Client IP")
        query_list = ['cnn.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.master0mgmtv6 + " " + str(record) + " +noedns "
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        print(output)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        out1 = commands.getoutput(sys_log_validation)
        print(out1)
        logging.info(out1)
        assert re.search(r'.*user*', out1)
        flag=False
        for line in output:
            #print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False


    @pytest.mark.run(order=64)
    def test_064_query_parental_control_domain_bbc_com_ipv6(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 64  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("This test performs dig by logging in to Client IP")
        query_list = ['bbc.com']
        args = "sshpass ssh -T -o StrictHostKeyChecking=no root@10.36.0.151"
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for record in query_list:
            dig_command = 'dig @' + config.master0mgmtv6 + " " + str(record) + " +noedns "
            child.stdin.write(dig_command + '\n')
        child.stdin.write("exit")
        output = child.communicate()
        print(output)
        sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str(
            config.grid_vip) + ' " tail -20 /var/log/syslog"'
        out1 = commands.getoutput(sys_log_validation)
        print(out1)
        logging.info(out1)
	flag=False
        for line in output:
            print (line)
            if "connection timed out; no servers could be reached" in line:
                assert False
            if "bbc" in line:
                flag=True
                break
        if not flag:
                assert False

    @pytest.mark.run(order=65)
    def test_065_add_reservation_address_with_subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 65  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("Adding Reservation Address without Subscriber Services")
        print("test case Pending since bug raised for Reservation Address WAPI Object : NIOS-71006")

    @pytest.mark.run(order=66)
    def test_066_modify_IPv4_network_with_invalid_PCCP_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 66  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("Modifying PC-Category Policy value with Invalid values : Negative test Case")
        try:
            original_data = {"network": "10.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "bbc.com"}, "Black-List": {"value": "facebook.com"}}}
            data_before_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                            grid_vip=config.master0mgmt)
            ref = json.loads(data_before_modification)[0]['_ref']
            modified_data = {"network": "20.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "qwertyuiopasdf"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "qa.com"}, "Black-List": {"value": "facebook.com"}}}
            modified_response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(modified_data),grid_vip=config.master0mgmt)
            sleep(10)
            data_after_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                           grid_vip=config.master0mgmt)
            print(data_after_modification)
            if (data_before_modification == data_after_modification):
                assert True
                print("Able to modify the PC-Category Policy value with Invalid values: Test case 66 Passed")
            else:
                assert False
                print(
                    "Able to modify the PC-Category Policy value with Invalid values, Check it Manually to cross verify: Test case 66 Failed")
        except TypeError:
            print("Unable to modify the PC-Category Policy value with Invalid values : Test case 66 Passed")

    @pytest.mark.run(order=67)
    def test_067_modify_IPv4_network_with_invalid_PCP_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 67  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("Modifying Parental-Category Policy value with Invalid values : Negative test Case")
        try:
            original_data = {"network": "10.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "bbc.com"}, "Black-List": {"value": "facebook.com"}}}
            data_before_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                            grid_vip=config.master0mgmt)
            ref = json.loads(data_before_modification)[0]['_ref']
            modified_data = {"network": "20.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "qwertyabcdef"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "qa.com"}, "Black-List": {"value": "facebook.com"}}}
            modified_response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(modified_data),grid_vip=config.master0mgmt)
            sleep(10)
            data_after_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                           grid_vip=config.master0mgmt)
            print(data_after_modification)
            if (data_before_modification == data_after_modification):
                assert True
                print("Able to modify the PC-Category Policy value with Invalid values: Test case 67 Passed")
            else:
                assert False
                print(
                    "Able to modify the PC-Category Policy value with Invalid values, Check it Manually to cross verify: Test case 67 Failed")
        except TypeError:
            print("Unable to modify the Parental-Category Policy value with Invalid values : Test case 67 Passed")

    @pytest.mark.run(order=68)
    def test_068_modify_IPv4_network_with_invalid_Proxyall_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 68  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("Modifying Parental-Category Policy value with Invalid values : Negative test Case")
        try:
            original_data = {"network": "10.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "bbc.com"}, "Black-List": {"value": "facebook.com"}}}
            data_before_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                            grid_vip=config.master0mgmt)
            ref = json.loads(data_before_modification)[0]['_ref']
            modified_data = {"network": "20.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "Infoblox"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "qa.com"}, "Black-List": {"value": "facebook.com"}}}
            modified_response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(modified_data),grid_vip=config.master0mgmt)
            sleep(10)
            data_after_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                           grid_vip=config.master0mgmt)
            print(data_after_modification)
            if (data_before_modification == data_after_modification):
                assert True
                print("Able to modify the PC-Category Policy value with Invalid values: Test case 68 Passed")
            else:
                assert False
                print(
                    "Able to modify the PC-Category Policy value with Invalid values, Check it Manually to cross verify: Test case 68 Failed")
        except TypeError:
            print(
                "Able to modify the Proxy All value with Invalid values,try manually and verify it : Test case 68 Failed")

    @pytest.mark.run(order=69)
    def test_069_modify_IPv4_network_with_invalid_subscriber_secure_policy_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 69  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("Modifying subscriber secure policy value with Invalid values : Negative test Case")
        try:
            original_data = {"network": "10.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "bbc.com"}, "Black-List": {"value": "facebook.com"}}}
            data_before_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                            grid_vip=config.master0mgmt)
            ref = json.loads(data_before_modification)[0]['_ref']
            modified_data = {"network": "20.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {
                                              "value": "qwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwerty"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "qa.com"}, "Black-List": {"value": "facebook.com"}}}
            modified_response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(modified_data),grid_vip=config.master0mgmt)
            sleep(10)
            data_after_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                           grid_vip=config.master0mgmt)
            print(data_after_modification)
            if (data_before_modification == data_after_modification):
                assert True
                print("Able to modify the PC-Category Policy value with Invalid values: Test case 69 Passed")
            else:
                assert False
                print(
                    "Able to modify the PC-Category Policy value with Invalid values, Check it Manually to cross verify: Test case 69 Failed")
        except TypeError:
            print("Unable to modify the subscriber secure policy value with Invalid value : Test case 69 Passed")

    @pytest.mark.run(order=70)
    def test_070_modify_IPv4_network_with_invalid_user_name_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 70  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("Modifying User Name value with Invalid values : Negative test Case")
        try:
            original_data = {"network": "10.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "bbc.com"}, "Black-List": {"value": "facebook.com"}}}
            data_before_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                            grid_vip=config.master0mgmt)
            ref = json.loads(data_before_modification)[0]['_ref']
            modified_data = {"network": "20.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"}, "User-Name": {
                                     "value": "qwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwertyqwerty"},
                                          "VLAN": {"value": "vlan"}, "White-List": {"value": "qa.com"},
                                          "Black-List": {"value": "facebook.com"}}}
            modified_response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(modified_data),grid_vip=config.master0mgmt)
            sleep(10)
            data_after_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                           grid_vip=config.master0mgmt)
            print(data_after_modification)
            if (data_before_modification == data_after_modification):
                assert True
                print("Able to modify the PC-Category Policy value with Invalid values: Test case 70 Passed")
            else:
                assert False
                print(
                    "Able to modify the PC-Category Policy value with Invalid values, Check it Manually to cross verify: Test case 70 Failed")
        except TypeError:
            print("Unable to modify the User Name value with Invalid values : Test case 70 Passed")

    @pytest.mark.run(order=71)
    def test_071_modify_IPv4_network_with_invalid_whitelist_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 71  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("Modifying whitelist value with Invalid values : Negative test Case")
        try:
            original_data = {"network": "10.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "bbc.com"}, "Black-List": {"value": "facebook.com"}}}
            data_before_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                            grid_vip=config.master0mgmt)
            ref = json.loads(data_before_modification)[0]['_ref']
            modified_data = {"network": "20.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": ""}, "Black-List": {"value": "facebook.com"}}}
            modified_response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(modified_data),grid_vip=config.master0mgmt)
            sleep(10)
            data_after_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                           grid_vip=config.master0mgmt)
            print(data_after_modification)
            if (data_before_modification == data_after_modification):
                assert True
                print("Able to modify the PC-Category Policy value with Invalid values: Test case 71 Passed")
            else:
                assert False
                print(
                    "Able to modify the PC-Category Policy value with Invalid values, Check it Manually to cross verify: Test case 71 Failed")
        except TypeError:
            print("Unable to modify the whitelist value with Invalid values : Test case 71 Passed")

    @pytest.mark.run(order=72)
    def test_072_modify_IPv4_network_with_invalid_Black_List_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 72  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("Modifying BlackList value with Invalid values : Negative test Case")
        try:
            original_data = {"network": "10.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "bbc.com"}, "Black-List": {"value": "facebook.com"}}}
            data_before_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                            grid_vip=config.master0mgmt)
	    print ("data_before_modification")
            ref = json.loads(data_before_modification)[0]['_ref']
            modified_data = {"network": "20.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "qa.com"}, "Black-List": {"value": ""}}}
            modified_response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(modified_data),grid_vip=config.master0mgmt)
            sleep(10)
            data_after_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                           grid_vip=config.master0mgmt)
            print(data_after_modification)
            if (data_before_modification == data_after_modification):
                assert True
                print("Able to modify the PC-Category Policy value with Invalid values: Test case 72 Passed")
            else:
                assert False
                print(
                    "Able to modify the PC-Category Policy value with Invalid values, Check it Manually to cross verify: Test case 72 Failed")
        except TypeError:
            print("Unable to modify the Black_List value with Invalid values : Test case 72 Passed")

    @pytest.mark.run(order=73)
    def test_073_modify_IPv4_network_with_valid_PCCP_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 73  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("Modifying PC-Category Policy value with valid values : Negative test Case")
        try:
            original_data = {"network": "10.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "bbc.com"}, "Black-List": {"value": "facebook.com"}}}
            data_before_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                            grid_vip=config.master0mgmt)
            ref = json.loads(data_before_modification)[0]['_ref']
            modified_data = {"network": "10.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000002"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "qa.com"}, "Black-List": {"value": "facebook.com"}}}
            modified_response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(modified_data),grid_vip=config.master0mgmt)
            sleep(10)
            data_after_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                           grid_vip=config.master0mgmt)
            print(data_after_modification)
            if (data_before_modification != data_after_modification):
                assert True
                print("Able to modify the PC-Category Policy value with valid values: Test case 73 Passed")
            else:
                assert False
                print(
                    "Able to modify the PC-Category Policy value with valid values, Check it Manually to cross verify: Test case 73 Failed")
        except TypeError:
            print("Unable to modify the PC-Category Policy value with valid values : Test case 73 Passed")

    @pytest.mark.run(order=74)
    def test_074_modify_IPv4_network_with_valid_PCP_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 74  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("Modifying Parental-Category Policy value with valid values : Negative test Case")
        try:
            original_data = {"network": "10.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "bbc.com"}, "Black-List": {"value": "facebook.com"}}}
            data_before_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                            grid_vip=config.master0mgmt)
            ref = json.loads(data_before_modification)[0]['_ref']
            modified_data = {"network": "10.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000022040"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "qa.com"}, "Black-List": {"value": "facebook.com"}}}
            modified_response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(modified_data),grid_vip=config.master0mgmt)
            sleep(10)
            data_after_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                           grid_vip=config.master0mgmt)
            print(data_after_modification)
            if (data_before_modification != data_after_modification):
                assert True
                print("Able to modify the PC-Category Policy value with Invalid values: Test case 74 Passed")
            else:
                assert False
                print(
                    "Able to modify the PC-Category Policy value with valid values, Check it Manually to cross verify: Test case 74 Failed")
        except TypeError:
            print("Unable to modify the Parental-Category Policy value with valid values : Test case 74 Passed")

    @pytest.mark.run(order=75)
    def test_075_modify_IPv4_network_with_valid_Proxyall_Subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 75  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("Modifying Parental-Category Policy value with valid values : Negative test Case")
        try:
            original_data = {"network": "10.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "bbc.com"}, "Black-List": {"value": "facebook.com"}}}
            data_before_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                            grid_vip=config.master0mgmt)
            ref = json.loads(data_before_modification)[0]['_ref']
            modified_data = {"network": "10.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "False"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "qa.com"}, "Black-List": {"value": "facebook.com"}}}
            modified_response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(modified_data),grid_vip=config.master0mgmt)
            sleep(10)
            data_after_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                           grid_vip=config.master0mgmt)
            print(data_after_modification)
            if (data_before_modification != data_after_modification):
                assert True
                print("Able to modify the PC-Category Policy value with valid values: Test case 75 Passed")
            else:
                assert False
                print(
                    "Able to modify the PC-Category Policy value with Invalid values, Check it Manually to cross verify: Test case 75 Failed")
        except TypeError:
            print(
                "UnAble to modify the Proxy All value with valid values,try manually and verify it : Test case 75 Failed")

    @pytest.mark.run(order=76)
    def test_076_modify_IPv4_network_with_valid_subscriber_secure_policy_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 76  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("Modifying subscriber secure policy value with valid values : Negative test Case")
        try:
            original_data = {"network": "10.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "bbc.com"}, "Black-List": {"value": "facebook.com"}}}
            data_before_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                            grid_vip=config.master0mgmt)
            ref = json.loads(data_before_modification)[0]['_ref']
            modified_data = {"network": "10.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ffff"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "qa.com"}, "Black-List": {"value": "facebook.com"}}}
            modified_response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(modified_data),grid_vip=config.master0mgmt)
            sleep(10)
            data_after_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                           grid_vip=config.master0mgmt)
            print(data_after_modification)
            if (data_before_modification != data_after_modification):
                assert True
                print("Able to modify the PC-Category Policy value with valid values: Test case 76 Passed")
            else:
                assert False
                print(
                    "Able to modify the PC-Category Policy value with valid values, Check it Manually to cross verify: Test case 76 Failed")
        except TypeError:
            print("Unable to modify the subscriber secure policy value with valid value : Test case 76 Passed")

    @pytest.mark.run(order=77)
    def test_077_modify_IPv4_network_with_valid_user_name_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 77  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("Modifying User Name value with valid values : Negative test Case")
        try:
            original_data = {"network": "10.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "bbc.com"}, "Black-List": {"value": "facebook.com"}}}
            data_before_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                            grid_vip=config.master0mgmt)
            ref = json.loads(data_before_modification)[0]['_ref']
            modified_data = {"network": "10.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"},
                                          "User-Name": {"value": "infoblox_user"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "qa.com"}, "Black-List": {"value": "facebook.com"}}}
            modified_response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(modified_data),grid_vip=config.master0mgmt)
            sleep(10)
            data_after_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                           grid_vip=config.master0mgmt)
            print(data_after_modification)
            if (data_before_modification != data_after_modification):
                assert True
                print("Able to modify the PC-Category Policy value with valid values: Test case 77 Passed")
            else:
                assert False
                print(
                    "Able to modify the PC-Category Policy value with valid values, Check it Manually to cross verify: Test case 77 Failed")
        except TypeError:
            print("Unable to modify the User Name value with valid values : Test case 77 Passed")

    @pytest.mark.run(order=78)
    def test_078_modify_IPv4_network_with_valid_whitelist_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 78  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("Modifying whitelist value with valid values : Negative test Case")
        try:
            original_data = {"network": "10.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "bbc.com"}, "Black-List": {"value": "facebook.com"}}}
            data_before_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                            grid_vip=config.master0mgmt)
            ref = json.loads(data_before_modification)[0]['_ref']
            modified_data = {"network": "10.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "ib.com"}, "Black-List": {"value": "facebook.com"}}}
            modified_response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(modified_data),grid_vip=config.master0mgmt)
            sleep(10)
            data_after_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                           grid_vip=config.master0mgmt)
            print(data_after_modification)
            if (data_before_modification != data_after_modification):
                assert True
                print("Able to modify the PC-Category Policy value with valid values: Test case 78 Passed")
            else:
                assert False
                print(
                    "Able to modify the PC-Category Policy value with valid values, Check it Manually to cross verify: Test case 78 Failed")
        except TypeError:
            print("Unable to modify the whitelist value with valid values : Test case 78 Passed")

    @pytest.mark.run(order=79)
    def test_079_modify_IPv4_network_with_valid_Black_List_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 78  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("Modifying BlackList value with valid values : Negative test Case")
        try:
            original_data = {"network": "10.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "bbc.com"}, "Black-List": {"value": "facebook.com"}}}
            data_before_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                            grid_vip=config.master0mgmt)
            ref = json.loads(data_before_modification)[0]['_ref']
            modified_data = {"network": "10.0.0.0/8", "members": [
                {"_struct": "dhcpmember", "ipv4addr": config.master01lan1v4, "name": config.grid_fqdn}],
                             "extattrs": {"Building": {"value": "building"}, "Country": {"value": "country"},
                                          "IB Discovery Owned": {"value": "ib"},
                                          "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                          "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                          "Proxy-All": {"value": "True"}, "Region": {"value": "region"},
                                          "Site": {"value": "site"}, "State": {"value": "state"},
                                          "Subscriber-Secure-Policy": {"value": "ff"},
                                          "User-Name": {"value": "user123"}, "VLAN": {"value": "vlan"},
                                          "White-List": {"value": "qa.com"}, "Black-List": {"value": "googley.com"}}}
            modified_response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(modified_data),grid_vip=config.master0mgmt)
            sleep(10)
            data_after_modification = ib_NIOS.wapi_request('GET', object_type="network?_return_fields=extattrs",
                                                           grid_vip=config.master0mgmt)
            print(data_after_modification)
            if (data_before_modification != data_after_modification):
                assert True
                print("Able to modify the PC-Category Policy value with valid values: Test case 78 Passed")
            else:
                assert False
                print(
                    "Able to modify the PC-Category Policy value with valid values, Check it Manually to cross verify: Test case 78 Failed")
        except TypeError:
            print("Unable to modify the Black_List value with valid values : Test case 78 Passed")

    @pytest.mark.run(order=80)
    def test_080_disable_IPv4_network(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 79  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("Disable the IPV4 network, it should not show in Subscriber services data ")
        try:
            network_ref = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.master0mgmt)
            print("{{{{{{{{{{{{{{{{{{{{{{{{", network_ref)
            ref = json.loads(network_ref)[0]['_ref']
            before_disabling_network = ib_NIOS.wapi_request('GET', object_type=ref + "?_return_fields=disable",
                                                            grid_vip=config.master0mgmt)
            sleep(5)
            data = {"disable": True}
            modified_data = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data),grid_vip=config.master0mgmt)
            sleep(20)
            after_modification_network = ib_NIOS.wapi_request('GET', object_type="network", grid_vip=config.master0mgmt)
            ref = json.loads(after_modification_network)[0]['_ref']
            after_disabling_network = ib_NIOS.wapi_request('GET', object_type=ref + "?_return_fields=disable",
                                                           grid_vip=config.master0mgmt)
            if (before_disabling_network != after_disabling_network):
                assert True
                print("Sucessfully Disabled IPV4 network : test case 79 Passed")
            else:
                assert False
                print("Sucessfully Disabled IPV4 network : test case 79 Failed")
        except TypeError:
            assert False

    @pytest.mark.run(order=81)
    def test_081_check_in_console_for_disable_IPv4_network(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 80  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        sleep(10)
        print("Test case to validate IPV4 fixed address disabled ")
        data = show_subscriber_secure_data()
        result = re.findall(".*20.0.0.22.*", data)
        if (result == []):
            assert True
            print("Test case 80 passed")
        else:
            assert False
            print("Test case 80 failed")

    @pytest.mark.run(order=82)
    def test_082_disable_IPv6_network(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 81  Started Executing                      ####")
        print("###############################################################################")
        print("Disable the IPV6 network, it should not show in Subscriber services data ")
        try:
            network_ref = ib_NIOS.wapi_request('GET', object_type="ipv6network", grid_vip=config.master0mgmt)
            ref = json.loads(network_ref)[0]['_ref']
            before_disabling_network = ib_NIOS.wapi_request('GET', object_type=ref + "?_return_fields=disable",
                                                            grid_vip=config.master0mgmt)
            sleep(5)
            data = {"disable": True}
            modified_data = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data),grid_vip=config.master0mgmt)
            sleep(20)
            after_modification_network = ib_NIOS.wapi_request('GET', object_type="ipv6network",
                                                              grid_vip=config.master0mgmt)
            ref = json.loads(after_modification_network)[0]['_ref']
            after_disabling_network = ib_NIOS.wapi_request('GET', object_type=ref + "?_return_fields=disable",
                                                           grid_vip=config.master0mgmt)
            if (before_disabling_network != after_disabling_network):
                assert True
                print("Sucessfully Disabled IPV4 network : test case 81 Passed")
            else:
                assert False
                print("Sucessfully Disabled IPV4 network : test case 81 Failed")
        except TypeError:
            assert False

    @pytest.mark.run(order=83)
    def test_083_check_in_console_for_disable_IPv6_network(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 82  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        print("Test case to validate IPV6 fixed address disabled ")
        data = show_subscriber_secure_data()
        result = re.findall(".*2630:10a:6000:2500::/64*", data)
        if (result == []):
            assert True
            print("Test case 82 passed")
        else:
            assert False
            print("Test case 82 failed")

    @pytest.mark.run(order=84)
    def test_084_delete_subscriber_records_with_Subscriber_EA_ipv4(self):
        ############Records should  get deleted since networks still have EA in them################
        sleep(10)
        print("Deleting network after Subscriber site deleted ")
        network_details = ib_NIOS.wapi_request('GET', object_type="network",grid_vip=config.master0mgmt)
        network_details = json.loads(network_details)
        print("::::::::::::::", network_details)
        # print (type(network_details))
        for ref in network_details:
            ref_link = ref['_ref']
            delete_network = ib_NIOS.wapi_request('DELETE', object_type=ref_link,grid_vip=config.master0mgmt)
        sleep(5)
        network_details_after_deletion = ib_NIOS.wapi_request('GET', object_type="network",grid_vip=config.master0mgmt)
        network_details_after_deletion = json.loads(network_details_after_deletion)
        print("network_details_after_deletion", network_details_after_deletion)
        if (network_details != network_details_after_deletion):
            print("IPV4 Network delete successfully : test case 83 Failed")
            assert True
        else:
            print("IPV4 Network delete successfully : test case 83 passed")
            assert False

    @pytest.mark.run(order=85)
    def test_085_delete_subscriber_records_with_Subscriber_EA_IPV6(self):
        ############Records should  get deleted since networks still have EA in them################
        sleep(10)
        print("Deleting network after Subscriber site deleted ")
        network_details = ib_NIOS.wapi_request('GET', object_type="ipv6network",grid_vip=config.master0mgmt)
        network_details = json.loads(network_details)
        print("::::::::::::::", network_details)
        # print (type(network_details))
        for ref in network_details:
            ref_link = ref['_ref']
            delete_network = ib_NIOS.wapi_request('DELETE', object_type=ref_link,grid_vip=config.master0mgmt)
        sleep(5)
        network_details_after_deletion = ib_NIOS.wapi_request('GET', object_type="ipv6network",grid_vip=config.master0mgmt)
        network_details_after_deletion = json.loads(network_details_after_deletion)
        print("network_details_after_deletion", network_details_after_deletion)
        if (network_details != network_details_after_deletion):
            print("IPV6 Network delete successfully : test case 84 Failed")
            assert True
        else:
            print("IPV6 Network delete successfully : test case 84 passed")
            assert False

    @pytest.mark.run(order=86)
    def test_086_start_Syslog_Messages_logs(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 85  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        logging.info("Starting Syslog Messages Logs")
        log("start", "/infoblox/var/infoblox", config.master0mgmt)
        logging.info("test case 85 passed")
        sleep(5)

    @pytest.mark.run(order=87)
    def test_087_import_subscriber_records_through_csv(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 86  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        logging.info("Upload DHCP Network with Subscriber Services records using csv file")
        # dir_name = "/import/qaddi/rkarjagi/API_Automation/WAPI_PyTest/suites/RFE-8538"
        dir_name = os.getcwd()
        base_file = "RFE_8538.csv"
        text_file_path = dir_name + '/' + base_file
        text = open(text_file_path, "r")
        text = ''.join([i for i in text]).replace("FQDN", config.grid_fqdn)
	print (text)
        data_file_path = str(dir_name) + '/' + "RFE_8538_output.csv"
        data = open(data_file_path, "w")
        data.writelines(text)
        data.close()
        base_filename = "RFE_8538_output.csv"
        sleep(5)
        token = generate_token_from_file(dir_name, base_filename)
        data = {"token": token, "action": "START", "doimport": True, "on_error": "CONTINUE",
                "update_method": "OVERRIDE"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),
                                        params="?_function=csv_import",grid_vip=config.master0mgmt)
        response = json.loads(response)
        time.sleep(30)
        get_ref = ib_NIOS.wapi_request('GET', object_type="csvimporttask",grid_vip=config.master0mgmt)
        get_ref = json.loads(get_ref)
        for ref in get_ref:
            if response["csv_import_task"]["import_id"] == ref["import_id"]:
                print(ref["lines_failed"])
                if ref["lines_failed"] > 0:
                    data = {"import_id": ref["import_id"]}
                    response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),
                                                    params="?_function=csv_error_log",grid_vip=config.master0mgmt)
                    response = json.loads(response)
                    response = response["url"].split("/")
                    req_id = response[4]
                    filename = response[5]
                    command = os.system(
                        'scp -pr root@' + config.grid_vip + ':/tmp/http_direct_file_io/' + req_id + '/' + filename + ' /tmp')
                    print(command)
                    print("Test case execution Failed csv import was unsuccessfull with invalid AVP's")
                    assert True
                else:
                    print(ref["status"])
                    print(ref["lines_failed"])
                    if ref["status"] == "COMPLETED" and ref["lines_failed"] == 0:
                        print("Test case 86 execution passed")
                        assert True
                    else:
                        print("Test case 86 execution Failed")
                        assert False

    @pytest.mark.run(order=88)
    def test_088_validate_Infoblox_Messages_for_Data_repo(self):
        logging.info("Restart DHCP Services")
        sleep(5)
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.master0mgmt)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order": "SIMULTANEOUSLY", "restart_option": "FORCE_RESTART", "service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=restartservices",
                                               fields=json.dumps(data), grid_vip=config.master0mgmt)
        print("Test Case 87 Passed ")

    @pytest.mark.run(order=89)
    def test_089_stop_Infoblox_Messages_Logs(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 88  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        logging.info("Stopping Syslog Logs")
        log("stop", "/infoblox/var/infoblox", config.master0mgmt)
        print("Test Case 88 Execution Completed")

    @pytest.mark.run(order=90)
    def test_090_validate_Infoblox_Messages_for_Data_repo(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 89  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        logging.info("Validating Sylog Messages Logs")
        # LookFor="imc"
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey=mykey)
        cmd = "cat /root/dump/" + str(config.master0mgmt) + "_infoblox_var_infoblox.log"
        stdin, stdout, stderr = client.exec_command(cmd + "| grep -i 'imc_open_data_repo_connection(): connected'")
        result = stdout.read()
        if not result:
            assert True
            logging.info("Test Case 89 Execution Failed")
        client.close()

    @pytest.mark.run(order=91)
    def test_091_import_subscriber_records_through_csv_Invalid_data(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 90  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        logging.info("Upload DHCP Network with Subscriber Services records using csv file")
        # dir_name = "/import/qaddi/rkarjagi/API_Automation/WAPI_PyTest/suites/RFE-8538"
        dir_name = os.getcwd()
        base_file = "RFE_8538_invalid_data.csv"
        text_data_file = str(dir_name) + '/' + "RFE_8538_output_invalid_data.csv"
        print("text_data_file")
        text = open(base_file, "r")
        text = ''.join([i for i in text]).replace("FQDN", config.grid_fqdn)
        data = open(text_data_file, "w")
        data.writelines(text)
        data.close()
        base_filename = "RFE_8538_output_invalid_data.csv"
        sleep(5)
        token = generate_token_from_file(dir_name, base_filename)
        data = {"token": token, "action": "START", "doimport": True, "on_error": "CONTINUE",
                "update_method": "OVERRIDE"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),
                                        params="?_function=csv_import",grid_vip=config.master0mgmt)
        response = json.loads(response)
        time.sleep(30)
        print(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::", response)
        get_ref = ib_NIOS.wapi_request('GET', object_type="csvimporttask",grid_vip=config.master0mgmt)
        get_ref = json.loads(get_ref)
        for ref in get_ref:
            if response["csv_import_task"]["import_id"] == ref["import_id"]:
                print(ref["lines_failed"])
                if ref["lines_failed"] > 0:
                    data = {"import_id": ref["import_id"]}
                    response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),
                                                    params="?_function=csv_error_log",grid_vip=config.master0mgmt)
                    response = json.loads(response)
                    response = response["url"].split("/")
                    req_id = response[4]
                    filename = response[5]
                    command = os.system(
                        'scp -pr root@' + config.master0mgmt + ':/tmp/http_direct_file_io/' + req_id + '/' + filename + ' /tmp')
                    print(command)
                    print("Test case execution Failed csv import was unsuccessfull with invalid AVP's")
                    assert True
                else:
                    print(ref["status"])
                    print(ref["lines_failed"])
                    if ref["status"] == "COMPLETED" and ref["lines_failed"] == 0:
                        print("Test case 90 execution passed")
                        assert True
                    else:
                        print("Test case 90 execution Failed")
                        assert False

    @pytest.mark.run(order=92)
    def test_092_CSV_import_SS_disabled(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 91  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("Trying to import CSV file when subscriber services is disabled,it should throw exception")
        subscriber_site_ref = ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",
                                                   fields=json.dumps(site_data),grid_vip=config.master0mgmt)
        print("Site deleted, stopping subscriber services now")
        print("------------------------Disbaling subscriber collection services------------------------------")
        subscriber_services = ib_NIOS.wapi_request('GET', object_type="member:parentalcontrol",grid_vip=config.master0mgmt)
        subscriber_services = json.loads(subscriber_services)
        print(subscriber_services)
        print("__________________________________")
        subscriber_ref = subscriber_services[0]['_ref']
        data = {"enable_service": False}
        enable_subscriber_ref = ib_NIOS.wapi_request('PUT', ref=subscriber_ref, fields=json.dumps(data),grid_vip=config.master0mgmt)
        print(enable_subscriber_ref)
        com = json.loads(enable_subscriber_ref) + "?_return_fields=enable_service"
        print(com)
        new_member_ref = ib_NIOS.wapi_request('GET', object_type=com,grid_vip=config.master0mgmt)
        new_member_ref = json.loads(new_member_ref)
        if (new_member_ref["enable_service"] == data["enable_service"]):
            assert True
            print("Subscriber Collection Service Disabled : Test case 91 passed")
        else:
            assert False
            print("errored out while Disabling Subscriber Collection service : Test case 91 Failed")

    @pytest.mark.run(order=93)
    def test_093_deleting_subscriber_site_after_disabling_SS(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 92  Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("deleting subscriber site ")
        site_ref = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite",grid_vip=config.master0mgmt)
        site_ref = json.loads(site_ref)
        site_ref = site_ref[0]['_ref']
        delete = ib_NIOS.wapi_request('DELETE', object_type=site_ref,grid_vip=config.master0mgmt)
        site_ref_new = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite",grid_vip=config.master0mgmt)
        if (site_ref_new == '[]'):
            print("Successfully deleted subscriber site : Test case 092 passed")
            assert True
        else:
            print("Unable to delete subscriber site : test case 092 failed")
            assert False

    @pytest.mark.run(order=94)
    def test_094_delete_network(self):
        ########able to delete network by updating its EA#############
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 93  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        print("Deleting network after Subscriber site deleted ")
        network_details = ib_NIOS.wapi_request('GET', object_type="network",grid_vip=config.master0mgmt)
        network_details = json.loads(network_details)
        print("::::::::::::::", network_details)
        # print (type(network_details))
        for ref in network_details:
            ref_link = ref['_ref']
            delete_network = ib_NIOS.wapi_request('DELETE', object_type=ref_link,grid_vip=config.master0mgmt)
        sleep(5)
        network_details_after_deletion = ib_NIOS.wapi_request('GET', object_type="network",grid_vip=config.master0mgmt)
        network_details_after_deletion = json.loads(network_details_after_deletion)
        print("network_details_after_deletion", network_details_after_deletion)
        if (network_details == network_details_after_deletion):
            print("Network delete successfully : test case 93 Passed")
            assert True
        else:
            print("Network delete successfully : test case 93 Failed")
            assert False

    @pytest.mark.run(order=95)
    def test_095_import_subscriber_records_through_csv_after_deleting_site_network(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 94  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        logging.info("Upload DHCP Network with Subscriber Services records using csv file")
        # dir_name = "/import/qaddi/rkarjagi/API_Automation/WAPI_PyTest/suites/RFE-8538"
        dir_name = os.getcwd()
        # base_filename = "RFE_8538.csv"
        # dir_name = "/import/qaddi/rkarjagi/API_Automation/WAPI_PyTest/suites/RFE-8538"
        base_file = "RFE_8538.csv"
        text = open(str(dir_name) + '/' + str(base_file), "r")
        text = ''.join([i for i in text]).replace("FQDN", config.grid_fqdn)
        data_file_path = str(dir_name) + '/' + "RFE_8538_output_latest.csv"
        data = open(data_file_path, "w")
        data.writelines(text)
        data.close()
        base_filename = "RFE_8538_output_latest.csv"
        sleep(5)
        token = generate_token_from_file(dir_name, base_filename)
        data = {"token": token, "action": "START", "doimport": True, "on_error": "CONTINUE",
                "update_method": "OVERRIDE"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),
                                        params="?_function=csv_import",grid_vip=config.master0mgmt)
        response = json.loads(response)
        time.sleep(30)
        # data={"action":"START","file_name":"arun.csv","on_error":"STOP","operation":"CREATE","separator":"COMMA"}
        get_ref = ib_NIOS.wapi_request('GET', object_type="csvimporttask",grid_vip=config.master0mgmt)
        get_ref = json.loads(get_ref)
        for ref in get_ref:
            if response["csv_import_task"]["import_id"] == ref["import_id"]:
                print(ref["lines_failed"])
                if ref["lines_failed"] == 0:
                    print(
                        "Test case execution Passed, csv import was successfull in case of Site not present and Subscriber services are not running")
                    assert False
                else:
                    data = {"import_id": ref["import_id"]}
                    response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),
                                                    params="?_function=csv_error_log",grid_vip=config.master0mgmt)
                    response = json.loads(response)
                    response = response["url"].split("/")
                    req_id = response[4]
                    filename = response[5]
                    command = os.system(
                        'scp -pr root@' + config.grid_vip + ':/tmp/http_direct_file_io/' + req_id + '/' + filename + ' /tmp')
                    print(command)
                    assert True
                    print(
                        "Test 94 case Passed , Negative validation for subscriber services and site details after deletion of both ")

    @pytest.mark.run(order=96)
    def test_096_add_site_under_subscriber_site(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 95  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        print("adding subscriber site under subscriber site \n ")
        site_data_new = {"blocking_ipv4_vip1": "2.4.5.6", "maximum_subscribers": 898989,
                         "msps": [{"ip_address": "10.196.128.13"}], "name": "mysite1", "nas_port": 1813,
                         "spms": [{"ip_address": "10.12.11.11"}]}
        subscriber_site_ref = ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",
                                                   fields=json.dumps(site_data),grid_vip=config.master0mgmt)
        # subscriber_site_ref=json.dumps(subscriber_site_ref)
        subscriber_site_ref = json.loads(subscriber_site_ref)
        print(subscriber_site_ref)
        ref1 = subscriber_site_ref + "?_return_fields=blocking_ipv4_vip1,maximum_subscribers,members,name,nas_port,msps,spms,nas_gateways"
        print(ref1)
        check_data = ib_NIOS.wapi_request('GET', object_type=ref1,grid_vip=config.master0mgmt)
        print(check_data)
        check_data = json.loads(check_data)
        check_data.pop('_ref')
        check_data.pop('members')
        check_data.pop('nas_gateways')
        check_data = json.dumps(check_data)
        check_data = json.loads(check_data)
        site_data_new = json.dumps(site_data_new)
        site_data_new = json.loads(site_data_new)
        print("Validating data before comparing it with data provided for Put operation", check_data)
        print("Data sent to update ", site_data_new)
        if (check_data != site_data_new):
            assert True
            print(" Test case 95 passed ")
        else:
            assert False
            print("Test Case 95 Failed")

    @pytest.mark.run(order=97)
    def test_097_start_subscriber_services(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 96  Started Executing                      ####")
        print("###############################################################################")
        sleep(10)
        print("------------------------enabling subscriber collection services------------------------------")
        subscriber_services = ib_NIOS.wapi_request('GET', object_type="member:parentalcontrol",grid_vip=config.master0mgmt)
        subscriber_services = json.loads(subscriber_services)
        print(subscriber_services)
        print("__________________________________")
        subscriber_ref = subscriber_services[0]['_ref']
        data = {"enable_service": True}
        enable_subscriber_ref = ib_NIOS.wapi_request('PUT', ref=subscriber_ref, fields=json.dumps(data),grid_vip=config.master0mgmt)
        print(enable_subscriber_ref)
        sleep(10)
        ####################Restarting the services now ################################
        grid = ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.master0mgmt)
        ref = json.loads(grid)[0]['_ref']
        publish = {"member_order": "SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=publish_changes",
                                               fields=json.dumps(publish),grid_vip=config.master0mgmt)
        time.sleep(1)
        request_restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=requestrestartservicestatus",grid_vip=config.master0mgmt)
        restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=restartservices",grid_vip=config.master0mgmt)
        time.sleep(5)
        com = json.loads(enable_subscriber_ref) + "?_return_fields=enable_service"
        print(com)
        new_member_ref = ib_NIOS.wapi_request('GET', object_type=com,grid_vip=config.master0mgmt)
        new_member_ref = json.loads(new_member_ref)
        if (new_member_ref["enable_service"] == data["enable_service"]):
            assert True
            print("Subscriber Collection Service Enabled : Test case 96 passed")
        else:
            assert False
            print("errored out while enabling Subscriber Collection service ")

    @pytest.mark.run(order=98)
    def test_098_add_IPV4fixed_address_with_subscriber_EA(self):
        print("\n")
        print("###############################################################################")
        print("####                   Test Case 97 Started Executing                      ####")
        print("###############################################################################")
        sleep(5)
        print("Create an IPv4 fixed address in defaultnetwork view")
        network_data = {"ipv4addr": "20.0.0.22", "network_view": "default", "mac": "11:11:11:11:11:11",
                        "extattrs": {"IB Discovery Owned": {"value": "ib2"},
                                     "PC-Category-Policy": {"value": "00000000000000000000000000000001"},
                                     "Parental-Control-Policy": {"value": "00000000000000000000000000020040"},
                                     "Proxy-All": {"value": "True"}, "Site": {"value": "site2"},
                                     "Subscriber-Secure-Policy": {"value": "ff"}, "User-Name": {"value": "user2"},
                                     "White-List": {"value": "qa2.com"}, "Black-List": {"value": "facebook.com"}}}
        response = ib_NIOS.wapi_request('POST', object_type="fixedaddress", fields=json.dumps(network_data),
                                        grid_vip=config.master0mgmt)
        print(response)
        read = re.search(r'201', response)
        for read in response:
            assert True
        print("Created the ipv4 fixed address in default view")
        logging.info("Restart DHCP Services")
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.master0mgmt)
        ref = json.loads(grid)[0]['_ref']
        data = {"member_order": "SIMULTANEOUSLY", "restart_option": "FORCE_RESTART", "service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=restartservices",
                                               fields=json.dumps(data), grid_vip=config.master0mgmt)
        new_data = ib_NIOS.wapi_request('GET', object_type="fixedaddress", grid_vip=config.master0mgmt)
        new_data = json.loads(new_data)
        logging.info("Wait for 20 sec.,")
        sleep(20)  # wait for 20 secs for the member to get started
        print(new_data[0])
        if (new_data[0]['ipv4addr'] == network_data['ipv4addr']):
            assert True
            print("Test Case 97 Execution Completed")
        else:
            assert False
            print("Test Case 97 Execution Failed")

    @pytest.mark.run(order=99)
    def test_099_export_site_data(self):
        try:
            print("\n")
            print("###############################################################################")
            print("####                   Test Case 98  Started Executing                      ####")
            print("###############################################################################")
            sleep(10)
            data1 = {"site": "site1"}
            data = {"_separator": "COMMA", "_object": "parentalcontrol:subscriberrecord", "site": "site1"}
            create_file = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),
                                               params="?_function=csv_export",grid_vip=config.master0mgmt)
            # print(create_file)
            read = re.search(r'400', create_file)
            for read in create_file:
                assert True
            res = json.loads(create_file)
            token = json.loads(create_file)['token']
            url = json.loads(create_file)['url']
            logging.info(create_file)
            cmd = 'curl -k1 -u admin:infoblox -H "Content-type:application/force-download" -O %s' % (url)
            result = subprocess.check_output(cmd, shell=True)
            print(result)
            command1 = "cat Subscriberrecords.csv | grep -F '10.36.0.151,N/A,N/A,32' "
            if command1 != None:
                print("Exported site data successfully")
                return command1
            else:
                print("Exporting site data failed")
                return None
            cmd = 'rm Subscriberrecords.csv'
            command2 = subprocess.check_output(cmd, shell=True)
        except TypeError:
            assert True






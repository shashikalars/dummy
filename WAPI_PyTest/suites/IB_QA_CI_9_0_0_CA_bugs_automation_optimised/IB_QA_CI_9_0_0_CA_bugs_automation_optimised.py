#!/usr/bin/env python
# -*- coding: utf-8 -*- 
__author__ = "Arun J R"
__email__  = "aramaiah@infoblox.com"

##################################################################################
#  Grid Set up required:                                                         #
#  1. Standalone HA Master with Grid Member                                      #
#  3. Licenses : DNS, Grid, DTC, NIOS(IB_1415)                                   #
##################################################################################


import re
import sys
import config
import pytest
import unittest
import logging
import os
import os.path
from os.path import join
import subprocess
import shlex
import json
import time
from time import sleep
import commands
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
import ib_utils.log_capture as log_capture
#from ib_utils.start_stop_logs import log_action as log
#from ib_utils.file_content_validation import log_validation as logv

from ib_utils.log_capture import log_action as log
from ib_utils.log_validation import log_validation as logv
from time import sleep
from scp import SCPClient
from subprocess import Popen, PIPE

import pexpect
import paramiko
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="9_0_0_CA_Regression_bugs.log" ,level=logging.INFO,filemode='w')

def is_grid_alive(grid=config.grid_vip):
    """
    Checks whether the grid is reachable
    """
    ping = os.popen("ping -c 2 "+grid).read()
    display_msg(ping)
    if "0 received" in ping:
        return False
    else:
        return True

def remove_known_hosts_file():
    """
    Removes known_hosts file.
    This is to avoid host key expiration issues.
    """
    client_username = os.popen('whoami').read().strip('\n')
    cmd = "rm -rf /home/"+client_username+"/.ssh/known_hosts"
    ret_code = os.system(cmd)
    if ret_code == 0:
        display_msg("Cleared known hosts file")
    else:
        display_msg("Couldnt clear known hosts file")

def generate_token_from_file(filepath, filename,grid=config.grid_vip):
    dir_name=filepath
    base_filename=filename
    filename= os.path.join(dir_name, base_filename)
    data = {"filename":base_filename}
    create_file = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadinit",grid_vip=grid)
    logging.info(create_file)
    res = json.loads(create_file)
    token = json.loads(create_file)['token']
    url = json.loads(create_file)['url']
    print create_file
    print res
    print token
    print url
    os.system('curl -k1 -u admin:infoblox -F name=%s -F filedata=@%s %s'%(filename,filename,url))
    filename="/"+filename
    return token

def get_conf_file(file, grid=config.grid_vip):
    '''
    Returns conf file in list formatt
    '''
    remove_known_hosts_file()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(grid, username='root', pkey = mykey)
    display_msg("cat /infoblox/var/quagga/"+file)
    stdin, stdout, stderr = client.exec_command("cat /infoblox/var/quagga/"+file)
    conf_file = []
    for line in stdout.readlines():
        line = line.encode('ascii','ignore')
        conf_file.append(line)
    client.close()
    return conf_file

def map_remote_user_to_the_group(group='admin-group'):
    display_msg("Selecting remote user to be mapped to the group "+group)
    response = ib_NIOS.wapi_request("GET",object_type="authpolicy")
    auth_policy_ref = json.loads(response)[0]['_ref']
    data={"default_group": group}
    response = ib_NIOS.wapi_request('PUT', ref=auth_policy_ref, fields=json.dumps(data), grid_vip=config.grid_vip)
    display_msg(response)
    if bool(re.match("\"authpolicy*.",str(response))):
        display_msg("Selected '"+group+"' for remote user mapping successfully")
        assert True
    else:
        display_msg("Selecting '"+group+"' for remote user mapping failed")
        assert False

def print_and_log(arg=""):
	print(arg)
	logging.info(arg)

def check_pingable_ips_for_dtc_server_configuration(ip_range):
    global Server_ip
    Server_ip = []
    for i in range(1, 8):
        out = ip_range + str(i)
        response = os.system("ping -c 1 " + out)
        if (response == 0):
            pingstatus = "Network Active"
            Server_ip.append(out)
        else:
            pass
    return Server_ip

def send_dig_query(record,rr_type,grid=config.grid1_master_vip,options=''):
    '''
    Send dig query to the grid and returns the output
    '''
    cmd = "dig @"+grid+" "+record+" IN "+rr_type+" "+options
    display_msg("Send dig query")
    output = os.popen(cmd).read()
    display_msg(output)
    output = output.split('\n')
    output = [x for x in output if x]
    return output

def parse_get_lab_info(ipv4):
    """
    ipv4    : ipv4 address of the machine
    Returns : Dictionary containing lab unit info
    """
    h_info = os.popen("identify_lab_unit "+ipv4).read()
    hostname = h_info.split(' ')[-1][:-2]
    display_msg(hostname)
    info = os.popen("get_lab_info -H "+hostname).read()
    info_list = info.split('\n')
    info_list = list(filter(None, info_list))
    info_dict = {}
    for x in info_list:
        info_dict[x.split('=')[0]] = x.split('=')[1]
    display_msg(info_dict)
    return info_dict

def getting_ref_of_the_dtc_health_monitors(dtc_health_object_name):
    get_ref = ib_NIOS.wapi_request('GET', object_type=dtc_health_object_name)
    print_and_log(get_ref)
    res = json.loads(get_ref)
    health_monitor_ref = res[0]['_ref']
    return health_monitor_ref


def restart_the_grid_Services():
    grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
    ref = json.loads(grid)[0]['_ref']
    data = {"mode": "SIMULTANEOUS", "restart_option": "FORCE_RESTART", "services": ["DNS"]}
    request_restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=restartservices", fields=json.dumps(data), grid_vip=config.grid_vip)
    sleep(60)

def restart_the_grid2_Services():
    grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid2_master_vip)
    ref = json.loads(grid)[0]['_ref']
    data = {"mode": "SIMULTANEOUS", "restart_option": "FORCE_RESTART", "services": ["DNS"]}
    request_restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=restartservices", fields=json.dumps(data), grid_vip=config.grid2_master_vip)
    sleep(60)

def Perform_Dig_queires(ip):
    output = os.popen("dig @" + ip + " a.dtc.com in a +short").read()
    Server_That_Responded = output.strip(" ").split("\n")[0]
    return Server_That_Responded

def check_dtc_server_health_status():
    response = ib_NIOS.wapi_request('GET', object_type="dtc:server", params="?_return_fields=health")
    response = json.loads(response)
    print_and_log(response)
    server_health = response[0]['health']['availability']
    print_and_log(server_health)
    return server_health


def dtc_object_failback_disable_options(data):
    response = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data), params="?_function=dtc_object_disable")
    print_and_log(response)
    output = json.loads(response)
    output = output['failback_status']
    return output


def dtc_object_failback_disable_options_with_workflow(data, username, password):
    response = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data), params="?_function=dtc_object_disable", user=username,password=password)
    print_and_log(response)
    output = json.loads(response)
    output = output['failback_status']
    return output


def check_dtc_object_health_status(obj):
    response = ib_NIOS.wapi_request('GET', object_type=obj, params="?_return_fields=health")
    response = json.loads(response)
    print_and_log(response)
    output = []
    for i in response:
        dtc_obj_health = i['health']['availability']
        print_and_log(dtc_obj_health)
        output.append(dtc_obj_health)
    print_and_log(output)
    return output


def dtc_object_failback_status(data):
    response = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data), params="?_function=dtc_get_object_grid_state")
    response = json.loads(response)
    output = response['enabled_on']
    return output

def dtc_object_failback_enable_options(data):
    response = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data),params="?_function=dtc_object_enable")
    print_and_log(response)
    output = json.loads(response)
    output = output['failback_status']
    return output


def dtc_object_failback_enable_options_with_workflow(data, username, password):
    response = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data),params="?_function=dtc_object_enable", user=username, password=password)
    print_and_log(response)
    output = json.loads(response)
    output = output['failback_status']
    return output


def validate_the_partial_health_update_error_logs(ip):
    LookFor1 = "'Received unexpected PARTIAL health update message from healthd, second part of the message is missing'"
    LookFor2 = "'general failure'"
    LookFor3 = "'Failed to replying PARTIAL health update'"
    log("stop", "/infoblox/var/infoblox.log", ip)
    try:
        logs = logv(LookFor1, "/infoblox/var/infoblox.log", ip)
        logs = logv(LookFor2, "/infoblox/var/infoblox.log", ip)
        logs = logv(LookFor3, "/infoblox/var/infoblox.log", ip)
    except Exception as e:
        print_and_log(e)
        print_and_log(" Error message is not seen in the logs ")
        assert True
    else:
        print_and_log(" Error message is seen in the logs ")
        assert False


def rebuild_services():
    print_and_log("******** Rebuild Services **********")
    log("start", "/var/log/syslog", config.grid_vip)
    request_restart = ib_NIOS.wapi_request('POST', object_type="dtc?_function=generate_ea_topology_db")
    print_and_log(request_restart)
    if request_restart == '{}':
        print_and_log("Success: Rebuild Service")
        assert True
    else:
        print_and_log("Failure: Rebuild Service")
        assert False
    sleep(60)
    LookFor = "'Topology EA DB Generator has finished: OK'"
    log("stop", "/var/log/syslog", config.grid_vip)
    logs = logv(LookFor, "/var/log/syslog", config.grid_vip)
    print_and_log("Success: validate Rebuild has completed successfully")


def disable_the_DTC_objects_using_checkbox(obj, obj_name, disable_val):
    response = ib_NIOS.wapi_request('GET', object_type=obj, params='?name='+obj_name)
    response = json.loads(response)
    print_and_log(response)
    ref_server = response[0]['_ref']
    data = {"disable": disable_val}
    output = ib_NIOS.wapi_request('PUT', object_type=ref_server, fields=json.dumps(data))
    print_and_log(output)
    return output


def check_the_DTC_objects_state(obj, obj_name):
    data = {"name": obj_name}
    print_and_log(data)
    response = ib_NIOS.wapi_request('GET', object_type=obj, params='?_return_fields=health', fields=json.dumps(data))
    response = json.loads(response)
    print_and_log(response)
    status = response[0]['health']['availability']
    print_and_log(status)
    return status


def Drop_and_Accept_the_DTC_Servers_on_DTC_members(ip, server_ip, action):
    try:
        add_server = "iptables -I INPUT -s " +server_ip+ " -j "+action
        print_and_log(add_server)
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@' + ip)
        child.logfile = sys.stdout
        child.expect('#')
        child.sendline(add_server)
        child.expect('#')
        child.close()
    except Exception as e:
        print_and_log(e)
        print_and_log("Error while executing the iptables command")
        assert False


def display_msg(x="", is_dict=False):
    """
    This function prints and logs data 'x'.
    is_dict : If this parameter is True, then print the data in easy to read format.
    """
    logging.info(x)
    if is_dict:
        print(json.dumps(x, sort_keys=False, indent=4))
    else:
        print(x)


def is_grid_alive(grid=config.grid_vip):
    """
    Checks whether the grid is reachable
    """
    ping = os.popen("ping -c 2 " + grid).read()
    display_msg(ping)
    if "0 received" in ping:
        return False
    else:
        return True


def remove_known_hosts_file():
    """
    Removes known_hosts file.
    This is to avoid host key expiration issues.
    """
    client_username = os.popen('whoami').read().strip('\n')
    cmd = "rm -rf /home/" + client_username + "/.ssh/known_hosts"
    ret_code = os.system(cmd)
    if ret_code == 0:
        display_msg("Cleared known hosts file")
    else:
        display_msg("Couldnt clear known hosts file")


def restart_services(grid=config.grid_vip, service=['ALL']):
    """
    Restart Services
    """
    display_msg()
    display_msg("+----------------------------------------------+")
    display_msg("|           Restart Services                   |")
    display_msg("+----------------------------------------------+")
    get_ref = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=grid)
    ref = json.loads(get_ref)[0]['_ref']
    data = {"mode": "SIMULTANEOUS", "restart_option": "FORCE_RESTART", "services": service}
    restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=restartservices", fields=json.dumps(data),
                                   grid_vip=grid)
    if restart != '{}':
        display_msg(restart)
        display_msg("FAIL: Restart services failed, Please debug above error message for root cause")
        assert False
    sleep(20)


def generate_token_from_file(filepath, filename, grid=config.grid_vip):
    dir_name = filepath
    base_filename = filename
    filename = os.path.join(dir_name, base_filename)
    data = {"filename": base_filename}
    create_file = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data), params="?_function=uploadinit", grid_vip=grid)
    logging.info(create_file)
    res = json.loads(create_file)
    token = json.loads(create_file)['token']
    url = json.loads(create_file)['url']
    print(create_file)
    print(res)
    print(token)
    print(url)
    os.system('curl -k1 -u admin:infoblox -F name=%s -F filedata=@%s %s' % (filename, filename, url))
    filename = "/" + filename
    return token


def get_conf_file(file, grid=config.grid_vip):
    '''
    Returns conf file in list formatt
    '''
    remove_known_hosts_file()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(grid, username='root', pkey=mykey)
    display_msg("cat /infoblox/var/quagga/" + file)
    stdin, stdout, stderr = client.exec_command("cat /infoblox/var/quagga/" + file)
    conf_file = []
    for line in stdout.readlines():
        line = line.encode('ascii', 'ignore')
        conf_file.append(line)
    client.close()
    return conf_file


def send_dig_query(record, rr_type, grid=config.grid_vip, options=''):
    '''
    Send dig query to the grid and returns the output
    '''
    cmd = "dig @" + grid + " " + record + " IN " + rr_type + " " + options
    display_msg("Send dig query")
    output = os.popen(cmd).read()
    display_msg(output)
    output = output.split('\n')
    output = [x for x in output if x]
    return output

def dns_restart_services():
    print("\n============================================\n")
    print("DNS Restart Services")
    print("\n============================================\n")

    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
    ref = json.loads(grid)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
    sleep(10)

def map_remote_user_to_the_group(group='admin-group'):
    display_msg("Selecting remote user to be mapped to the group "+group)
    response = ib_NIOS.wapi_request("GET",object_type="authpolicy")
    auth_policy_ref = json.loads(response)[0]['_ref']
    data={"default_group": group}
    response = ib_NIOS.wapi_request('PUT', ref=auth_policy_ref, fields=json.dumps(data), grid_vip=config.grid_vip)
    display_msg(response)
    if bool(re.match("\"authpolicy*.",str(response))):
        display_msg("Selected '"+group+"' for remote user mapping successfully")
        assert True
    else:
        display_msg("Selecting '"+group+"' for remote user mapping failed")
        assert False

def clean_up_supportbundle_files_on_the_client(username, ip, path, pw):
    try:
        print_and_log("Deleting the support bundle file from the scp server")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=pw)
        cmd = "rm "+path
        print_and_log(cmd)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read()
        print_and_log(output)
        ssh.close()
    except Exception as e:
        ssh.close()
        print_and_log(e)
        print_and_log(" Error while deleting the file ")
        assert False

def perform_set_transfer_supportbundle_cli_command(ip, cli_cmd):
    try:
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@' + ip)
        child.logfile = sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline(cli_cmd)
        child.expect(':')
        child.sendline('y')
        sleep(180)
        child.expect('successfully' )
        output = child.before
        child.close()
    except Exception as e:
        child.close()
        print("Error while executing the CLI command")
        print(e)
        assert False
    return output

def perform_show_firmware_cli_command(ip, cli_cmd):
    try:
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@' + ip)
        child.logfile = sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline(cli_cmd)
        child.expect('Infoblox >')
        output = child.before
        child.close()
    except Exception as e:
        child.close()
        print("Error while executing the CLI command")
        print(e)
        assert False
    return output

def IPv4_records_validation(grid=config.grid1_master_vip):
    record_name = re.search('Added new forward map from(.*)by server ',log_validation)
    record_name = record_name.group(0)
    def Convert(string):
            li = list(string.split(" "))
            return li
    str1 = Convert(record_name)
    record_name = str1[5]
    print(record_name)
    sleep(10)
    A_record = ib_NIOS.wapi_request('GET', object_type="record:a?name="+record_name, grid_vip=config.grid1_master_vip)
    print(A_record)
    TXT_record = ib_NIOS.wapi_request('GET', object_type="record:txt?name="+record_name,grid_vip=config.grid1_master_vip)
    print(TXT_record)
    if record_name in A_record and record_name in TXT_record:
            assert True
            print(record_name+" added in A and TXT records ")
    else:
            print(record_name+" not added in A and TXT records ")
            assert False

def check_status(ip):
    ping_cmd= 'ping -c 3 '+str(ip)
    print ping_cmd
    for i in range(3):
        result_ping= os.system(ping_cmd)
    	if result_ping == 0:
	    print("product restarted successfully")
	    return True
	else:
	    sleep(120)
    else:
	print("product is still restarting")
	return False

def check_able_to_login_appliances(ip):

    for i in range(5):
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+ip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.close()
            print("\n************Appliances is Working************\n ")
            sleep(120)
            assert True
            break

        except Exception as e:
            child.close()
            print(e)
            sleep(120)
            continue

            print("Failure: Appliances did not comeup(vm didn't comeup)")

            assert False


def prepration():
    print("Adding core and memory to flex members")

    subprocess.check_output("reboot_system -H "+config.grid1_member1_id+" -a poweroff -c "+config.owner,shell=True)
    subprocess.check_output("reboot_system -H "+config.grid1_member2_id+" -a poweroff -c "+config.owner,shell=True)

    subprocess.check_output("vm_specs -H "+config.grid1_member1_id+" -C 8 -M 32 -c "+config.owner,shell=True)
    subprocess.check_output("vm_specs -H "+config.grid1_member2_id+" -C 8 -M 32 -c "+config.owner,shell=True)

    subprocess.check_output("reboot_system -H "+config.grid1_member1_id+" -a poweron -c "+config.owner,shell=True)
    subprocess.check_output("reboot_system -H "+config.grid1_member2_id+" -a poweron -c "+config.owner,shell=True)

    sleep(400)


class dtc_bug_automation_9_0(unittest.TestCase):


    @pytest.mark.run(order=1)
    def test_001_NIOS_87856_enable_dns_on_the_gird_and_member(self):
        prepration()
        print_and_log("*********** Enabling the DNS on the Grid and member ************")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        print_and_log(get_ref)
        res = json.loads(get_ref)
        for i in res:
            data = {"enable_dns": True}
            print_and_log(data)
            response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
            print_and_log(response)
        print_and_log("*********** Test Case 1 Execution Completed ************")


    @pytest.mark.run(order=2)
    def test_002_NIOS_87856_Validate_DNS_service_Enabled(self):
        print_and_log("************ Validate DNS Service is enabled **************")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
        res = json.loads(get_ref)
        print_and_log(res)
        for i in res:
            print_and_log(i)
            if i["enable_dns"] == True:
                print_and_log("DNS is enabled on the Grid")
                assert True
            else:
                print_and_log("DNS is not enabled on the Grid")
                assert False
        print_and_log("*********** Test Case 2 Execution Completed ************")

    @pytest.mark.run(order=3)
    def test_003_NIOS_87856_create_AuthZone(self):
        print_and_log("************ Create auth Zone dtc.com *************")
        global zones
        zones = ["dtc.com", "dtc1.com"]
        for i in zones:
            data = {"fqdn": i, "grid_primary": [{"name": config.grid1_master_fqdn, "stealth": False}, {"name": config.grid1_member1_fqdn, "stealth": False}]}
            response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
            print_and_log(response)
            assert re.search(i, response)
        print_and_log("Restart DNS Services")
        restart_the_grid_Services()
        print_and_log("*********** Test Case 3 Execution Completed ************")

    @pytest.mark.run(order=4)
    def test_004_NIOS_87856_Validate_AuthZones(self):
        print_and_log("************ Validate the Zone dtc.com *************")
        for i in zones:
            response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn="+i, grid_vip=config.grid1_master_vip)
            print_and_log(response)
            response = json.loads(response)
            output = response[0]['fqdn']
            if output == zones[0] or output == zones[1]:
                print_and_log("Auth zone "+output+" created sucessfully")
                assert True
            else:
                print_and_log(" Error while validating the auth zone")
                assert False
        print_and_log("********** Test Case 4 Execution Completed ***********")

    @pytest.mark.run(order=5)
    def test_005_NIOS_87856_Create_a_record_for_the_zone_which_is_not_associated_to_DTC_LBDN(self):
        print_and_log("************** Create a record for the zone which is not associated to DTC LBDN ***************")
        global dtc_server_ips
        dtc_server_ips = check_pingable_ips_for_dtc_server_configuration(config.ip_range)
        print_and_log(dtc_server_ips)
        data = {"name": "server1."+zones[1],"ipv4addr": dtc_server_ips[0], "ttl": 60}
        print_and_log(data)
        response = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(data))
        print_and_log(response)
        assert re.search(r'record:a', response)
        print_and_log("********** Test Case 5 Execution Completed ***********")

    @pytest.mark.run(order=6)
    def test_006_NIOS_87856_Validate_the_a_record_created_and_ttl_configured(self):
        print_and_log("************** Validate the a record created and ttl configured **************")
        global record_name
        response = ib_NIOS.wapi_request('GET', object_type="record:a")
        output = json.loads(response)
        print_and_log(output)
        record_ref = output[0]['_ref']
        record_name = output[0]['name']
        print_and_log(record_ref)
        print_and_log(record_name)
        response1 = ib_NIOS.wapi_request('GET', object_type=record_ref, params="?_return_fields=ttl")
        response1 = json.loads(response1)
        ttl = response1['ttl']
        print_and_log(ttl)
        if record_name == "server1."+zones[1] and ttl == 60:
            print_and_log("A record "+record_name+" is configured with ttl value of "+str(ttl))
            assert True
        else:
            print_and_log("Error while validating the record name and ttl value")
            assert False
        print_and_log("********** Test Case 6 Execution Completed ***********")

    @pytest.mark.run(order=7)
    def test_007_NIOS_87856_configure_two_dtc_servers(self):
        print_and_log("************ Configure 2 dtc servers ***************")
        global server_name
        server_name = ["server1", "server2", "server3", "server4"]
        server_obj = {server_name[0]: record_name, server_name[1]: dtc_server_ips[1]}
        for i, j in server_obj.items():
            data = {"name": i, "host": j}
            response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
            print_and_log(response)
            assert re.search("dtc:server", response)
        print_and_log("*********** Test Case 7 Execution Completed ************")

    @pytest.mark.run(order=8)
    def test_008_NIOS_87856_validate_the_dtc_servers_created(self):
        print_and_log(" ************ Validate the dtc servers created *************** ")
        for i in server_name[:2]:
            servers = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name=' + i)
            servers = json.loads(servers)
            dtc_server_name = servers[0]['name']
            if dtc_server_name == "server1":
                print_and_log("DTC server " + dtc_server_name + " created successfully")
                assert True
            elif dtc_server_name == "server2":
                print_and_log("DTC server " + dtc_server_name + " created successfully")
                assert True
            else:
                print_and_log("Error while validating the DTC servers")
                assert False
        print_and_log("*********** Test Case 8 Execution Completed ************")

    @pytest.mark.run(order=9)
    def test_009_NIOS_87856_Create_the_DTC_Pool_1_and_Assign_the_Server_members_server1_and_server2(self):
        print_and_log(" ************ Create the DTC pool and Assign the Server members *************** ")
        server_ref = []
        for i in server_name[:2]:
            response_servers = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name=' + i)
            response_servers = json.loads(response_servers)
            ref = response_servers[0]['_ref']
            server_ref.append(ref)
        health_monitor_ref = getting_ref_of_the_dtc_health_monitors("dtc:monitor:icmp")
        print_and_log(health_monitor_ref)
        data = {"name": "pool1", "lb_preferred_method": "GLOBAL_AVAILABILITY",
                "servers": [{"ratio": 1, "server": str(server_ref[0])}, {"ratio": 1, "server": str(server_ref[1])}],
                "monitors": [str(health_monitor_ref)]}
        res = ib_NIOS.wapi_request('POST', object_type='dtc:pool', fields=json.dumps(data))
        print_and_log(res)
        assert re.search("dtc:pool", res)
        print_and_log(" ************ Test Case 9 Execution Completed *************** ")

    @pytest.mark.run(order=10)
    def test_010_NIOS_87856_validate_the_dtc_pool_1_created(self):
        print_and_log(" ************ Validate the dtc pool 1 created *************** ")
        response_servers = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response_servers = json.loads(response_servers)
        print_and_log(response_servers)
        dtc_pool_name = response_servers[0]['name']
        if dtc_pool_name == "pool1":
            print_and_log("DTC Pool " + dtc_pool_name + " is created successfully")
            assert True
        else:
            print_and_log(" Error while validating the DTC Pool created")
            assert False
        print_and_log(" ************ Test Case 10 Execution Completed *************** ")

    @pytest.mark.run(order=11)
    def test_011_NIOS_87856_Create_the_DTC_LBDN1(self):
        print_and_log(" ************ Create the DTC LBDN1 ************ ")
        print_and_log("Getting ref of auth zone dtc.com")
        response = ib_NIOS.wapi_request('GET', object_type='zone_auth', params='?fqdn=dtc.com')
        response = json.loads(response)
        ref_zone = response[0]['_ref']
        print_and_log(ref_zone)
        print_and_log("********** Getting the ref of pool ************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response = json.loads(response)
        ref_pool = response[0]['_ref']
        print_and_log(ref_pool)
        print_and_log("********** Creating the lbdn by post request ************")
        data = {"auth_zones": [ref_zone], "name": "DTC_LBDN_1", "lb_method": "ROUND_ROBIN",
                "patterns": ["*.dtc.com"], "pools": [{"ratio": 1, "pool": ref_pool}]}
        print_and_log(data)
        response = ib_NIOS.wapi_request('POST', object_type='dtc:lbdn', fields=json.dumps(data))
        response = json.loads(response)
        print_and_log("Validation of lbdn creation")
        assert re.search(r'dtc:lbdn', response)
        print_and_log("******** Restart the DNS service *********")
        restart_the_grid_Services()
        print_and_log(" ************ Test Case 11 Execution Completed *************** ")

    @pytest.mark.run(order=12)
    def test_012_NIOS_87856_Validate_the_DTC_LBDN1(self):
        print_and_log(" ************ Validate the DTC LBDN1 ************ ")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        ref_lbdn = response[0]['_ref']
        print_and_log(ref_lbdn)
        dtc_lbdn_name = response[0]['name']
        print_and_log(dtc_lbdn_name)
        if dtc_lbdn_name == "DTC_LBDN_1":
            print_and_log("DTC LBDN " + dtc_lbdn_name + " configured successfully")
            assert True
        else:
            print_and_log("Validation for the DTC LBDN 1 failed")
            assert False
        print_and_log(" ************ Test Case 12 Execution Completed *************** ")

    @pytest.mark.run(order=13)
    def test_013_NIOS_87856_Perform_the_dig_command_and_verify_the_response_is_from_dtc_Server1(self):
        print_and_log("********** Perform the dig command and verify the response on Grid master ************")
        Server_That_Responded = Perform_Dig_queires(config.grid1_master_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == record_name+".":
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("********** Perform the dig command and verify the response on Grid member ************")
        Server_That_Responded = Perform_Dig_queires(config.grid1_member1_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == record_name+".":
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("********* Test Case 13 Execution Completed *************")


    @pytest.mark.run(order=14)
    def test_014_NIOS_87856_modify_a_record_ip_to_non_pingable_ip(self):
        print_and_log("************* modify a record ip to non pingable ip **************")
        response = ib_NIOS.wapi_request('GET', object_type="record:a")
        output = json.loads(response)
        print_and_log(output)
        record_ref = output[0]['_ref']
        print_and_log(record_ref)
        data = {"ipv4addr": "1.1.1.1"}
        response1 = ib_NIOS.wapi_request('PUT', object_type=record_ref, fields=json.dumps(data))
        print_and_log(response1)
        assert re.search(r'record:a', response1)
        print_and_log("*********** Test Case 14 Execution Completed *************")

    @pytest.mark.run(order=15)
    def test_015_NIOS_87856_Validate_the_a_record_ip_which_is_modified(self):
        print_and_log("************** Validate the a record ip which is modified **************")
        response = ib_NIOS.wapi_request('GET', object_type="record:a")
        output = json.loads(response)
        print_and_log(output)
        record_ip = output[0]['ipv4addr']
        print_and_log(record_ip)
        if record_ip == "1.1.1.1":
            print_and_log("A record " + record_ip + " is configured successfully")
            assert True
        else:
            print_and_log("Error while validating the record ip")
            assert False
        print_and_log("********** Test Case 15 Execution Completed ***********")

    @pytest.mark.run(order=16)
    def test_016_NIOS_87856_Check_if_the_dig_quereies_only_from_Server1_after_60_seconds(self):
        print_and_log("************ Check if the dig queries only from Server1 after 60 seconds *************")
        flag = False
        for i in range(0,80):
            Server_That_Responded = Perform_Dig_queires(config.grid1_master_vip)
            print_and_log(Server_That_Responded)
            if Server_That_Responded != record_name+".":
                print_and_log("Itteration "+str(i)+" : Server " + Server_That_Responded + " responded for the query")
                flag = True
                break
            else:
                print_and_log("Itteration "+str(i)+" : Still We see DTC server responding to DTC quereies")
                sleep(1)
                continue
        if flag == True:
            print_and_log("DTC server stopped responding to queries")
            assert True
        else:
            print_and_log("DTC server continued to respond to the queries")
            assert False
        sleep(20)
        print_and_log("********** Test Case 16 Execution Completed ***********")

    @pytest.mark.run(order=17)
    def test_017_NIOS_87856_Check_the_status_of_DTC_Server1(self):
        print_and_log("************* Check the status of DTC Server1  *************")
        flag = False
        for i in range(1,10):
            health_status = check_dtc_server_health_status()
            if health_status == "RED":
                print_and_log("Server health status is in "+health_status+ " color")
                flag=True
                break
            else:
                print_and_log("Server health status is not in Error state")
                sleep(1)
                continue
        if flag == True:
            print_and_log("Server health status is updated correctly")
            assert True
        else:
            print_and_log("Server health status is not updated correctly")
            assert False
        print_and_log("********** Test Case 17 Execution Completed ***********")

    @pytest.mark.run(order=18)
    def test_018_NIOS_87856_Add_the_host_record_for_the_auth_zone_which_is_not_associated_to_DTC_LBDN(self):
        print_and_log("************ Add the host record for the auth zone which is not associated to DTC LBDN **************")
        data = {"name": "host."+zones[1], "ipv4addrs": [{"ipv4addr": dtc_server_ips[2], "configure_for_dhcp": False}], "ttl": 60}
        response = ib_NIOS.wapi_request('POST', object_type="record:host", fields=json.dumps(data))
        print_and_log(response)
        assert re.search(r'record:host', response)
        print_and_log("********** Test Case 18 Execution Completed ***********")

    @pytest.mark.run(order=19)
    def test_019_NIOS_87856_Validate_the_host_record_created(self):
        print_and_log("************ Validate the host record created **************")
        response = ib_NIOS.wapi_request('GET', object_type="record:host")
        response = json.loads(response)
        print_and_log(response)
        host_record_name = response[0]['name']
        print_and_log(host_record_name)
        if host_record_name == "host."+zones[1]:
            print_and_log("Host record "+host_record_name+" created successfully")
            assert True
        else:
            print_and_log("Host record validation failed")
            assert False
        print_and_log("********** Test Case 19 Execution Completed ***********")

    @pytest.mark.run(order=20)
    def test_020_NIOS_87856_Add_the_host_record_to_the_DTC_server_1(self):
        print_and_log("************* Add the host record to the DTC server 1 **************")
        response = ib_NIOS.wapi_request('GET', object_type="dtc:server", params="?name="+server_name[0])
        response = json.loads(response)
        print_and_log(response)
        server_ref = response[0]['_ref']
        print_and_log(server_ref)
        data = {"name": "host", "host": "host."+zones[1]}
        response1 = ib_NIOS.wapi_request('PUT', object_type=server_ref, fields=json.dumps(data))
        print_and_log(response1)
        assert re.search(r'dtc:server', response1)
        restart_the_grid_Services()
        print_and_log("********** Test Case 19 Execution Completed ***********")

    @pytest.mark.run(order=21)
    def test_021_NIOS_87856_validate_the_modified_dtc_server(self):
        print_and_log(" ************ Validate the dtc server modfied *************** ")
        servers = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name=host')
        servers = json.loads(servers)
        dtc_server_name = servers[0]['name']
        if dtc_server_name == "host":
            print_and_log("DTC server " + dtc_server_name + " modified successfully")
            assert True
        else:
            print_and_log("Error while validating the DTC servers")
            assert False
        sleep(20)
        print_and_log("*********** Test Case 21 Execution Completed ************")

    @pytest.mark.run(order=22)
    def test_022_NIOS_87856_Check_the_status_of_DTC_Server1(self):
        print_and_log("************* Check the status of DTC Server1  *************")
        flag = False
        for i in range(1, 10):
            health_status = check_dtc_server_health_status()
            if health_status == "GREEN":
                print_and_log("Server health status is in " + health_status + " color")
                flag = True
                break
            else:
                print_and_log("Server health status is not in RUNNING state")
                sleep(1)
                continue
        if flag == True:
            print_and_log("Server health status is updated correctly")
            assert True
        else:
            print_and_log("Server health status is not updated correctly")
            assert False
        print_and_log("********** Test Case 22 Execution Completed ***********")

    @pytest.mark.run(order=23)
    def test_023_NIOS_87856_Perform_the_dig_command_and_verify_the_response_is_from_dtc_Server1(self):
        print_and_log("********** Perform the dig command and verify the response on Grid master ************")
        Server_That_Responded = Perform_Dig_queires(config.grid1_master_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == "host."+zones[1]+".":
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("********** Perform the dig command and verify the response on Grid member ************")
        Server_That_Responded = Perform_Dig_queires(config.grid1_member1_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == "host."+zones[1]+".":
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("********* Test Case 23 Execution Completed *************")

    @pytest.mark.run(order=24)
    def test_024_NIOS_87856_modify_host_record_ip_to_non_pingable_ip(self):
        print_and_log("************* modify host record ip to non pingable ip **************")
        response = ib_NIOS.wapi_request('GET', object_type="record:host")
        output = json.loads(response)
        print_and_log(output)
        record_ref = output[0]['_ref']
        print_and_log(record_ref)
        data = {"ipv4addrs": [{"ipv4addr": "1.1.1.1"}]}
        response1 = ib_NIOS.wapi_request('PUT', object_type=record_ref, fields=json.dumps(data))
        print_and_log(response1)
        assert re.search(r'record:host', response1)
        print_and_log("*********** Test Case 24 Execution Completed *************")

    @pytest.mark.run(order=25)
    def test_025_NIOS_87856_Validate_the_a_record_ip_which_is_modified(self):
        print_and_log("************** Validate the a record ip which is modified **************")
        response = ib_NIOS.wapi_request('GET', object_type="record:host")
        response = json.loads(response)
        output = print_and_log(response)
        host_record_ip = response[0]['ipv4addrs'][0]['ipv4addr']
        print_and_log(host_record_ip)
        if host_record_ip == "1.1.1.1":
            print_and_log("Host record ip is modified to " + host_record_ip + " successfully")
            assert True
        else:
            print_and_log("Error while validating the host record ip")
            assert False
        print_and_log("********** Test Case 25 Execution Completed ***********")

    @pytest.mark.run(order=26)
    def test_026_NIOS_87856_Check_if_the_dig_quereies_only_from_Server1_after_60_seconds(self):
        print_and_log("************ Check if the dig queries only from Server1 after 60 seconds *************")
        flag = False
        for i in range(0, 80):
            Server_That_Responded = Perform_Dig_queires(config.grid1_master_vip)
            print_and_log(Server_That_Responded)
            if Server_That_Responded != "host."+zones[1]+".":
                print_and_log("Itteration " + str(i) + " : Server " + Server_That_Responded + " responded for the query")
                flag = True
                break
            else:
                print_and_log("Itteration " + str(i) + " : Still We see DTC server responding to DTC queries")
                sleep(1)
                continue
        if flag == True:
            print_and_log("DTC server stopped responding to queries")
            assert True
        else:
            print_and_log("DTC server continued to respond to the queries")
            assert False
        sleep(20)
        print_and_log("********** Test Case 26 Execution Completed ***********")

    @pytest.mark.run(order=27)
    def test_027_NIOS_87856_Check_the_status_of_DTC_Server1(self):
        print_and_log("************* Check the status of DTC Server1  *************")
        flag = False
        for i in range(1, 10):
            health_status = check_dtc_server_health_status()
            if health_status == "RED":
                print_and_log("Server health status is in " + health_status + " color")
                flag = True
                break
            else:
                print_and_log("Server health status is not in ERROR state")
                sleep(1)
                continue
        if flag == True:
            print_and_log("Server health status is updated correctly")
            assert True
        else:
            print_and_log("Server health status is not updated correctly")
            assert False
        print_and_log("********** Test Case 27 Execution Completed ***********")

    @pytest.mark.run(order=28)
    def test_028_NIOS_87856_Create_aaaa_record_for_the_zone_which_is_not_associated_to_DTC_LBDN(self):
        print_and_log("************** Create aaaa record for the zone which is not associated to DTC LBDN ***************")
        data = {"name": "ipv6a." + zones[1], "ipv6addr": config.grid1_member1_ipv6, "ttl": 60}
        print_and_log(data)
        response = ib_NIOS.wapi_request('POST', object_type="record:aaaa", fields=json.dumps(data))
        print_and_log(response)
        assert re.search(r'record:aaaa', response)
        print_and_log("********** Test Case 28 Execution Completed ***********")

    @pytest.mark.run(order=29)
    def test_029_NIOS_87856_Validate_the_aaaa_record_created_and_ttl_configured(self):
        print_and_log("************** Validate the aaaa record created and ttl configured **************")
        response = ib_NIOS.wapi_request('GET', object_type="record:aaaa")
        output = json.loads(response)
        print_and_log(output)
        record_ref = output[0]['_ref']
        record_name = output[0]['name']
        print_and_log(record_ref)
        print_and_log(record_name)
        response1 = ib_NIOS.wapi_request('GET', object_type=record_ref, params="?_return_fields=ttl")
        response1 = json.loads(response1)
        ttl = response1['ttl']
        print_and_log(ttl)
        if record_name == "ipv6a." + zones[1] and ttl == 60:
            print_and_log("AAAA record " + record_name + " is configured with ttl value of " + str(ttl))
            assert True
        else:
            print_and_log("Error while validating the AAAA record name and ttl value")
            assert False
        print_and_log("********** Test Case 29 Execution Completed ***********")

    @pytest.mark.run(order=30)
    def test_030_NIOS_87856_Add_the_aaaa_record_to_the_DTC_server_1(self):
        print_and_log("************* Add the aaaa record to the DTC server 1 **************")
        response = ib_NIOS.wapi_request('GET', object_type="dtc:server", params="?name=host")
        response = json.loads(response)
        print_and_log(response)
        server_ref = response[0]['_ref']
        print_and_log(server_ref)
        data = {"name": "ipv6a", "host": "ipv6a." + zones[1]}
        response1 = ib_NIOS.wapi_request('PUT', object_type=server_ref, fields=json.dumps(data))
        print_and_log(response1)
        assert re.search(r'dtc:server', response1)
        restart_the_grid_Services()
        print_and_log("********** Test Case 30 Execution Completed ***********")

    @pytest.mark.run(order=31)
    def test_031_NIOS_87856_validate_the_modified_dtc_server(self):
        print_and_log(" ************ Validate the dtc server modfied *************** ")
        servers = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name=ipv6a')
        servers = json.loads(servers)
        dtc_server_name = servers[0]['name']
        if dtc_server_name == "ipv6a":
            print_and_log("DTC server " + dtc_server_name + " modified successfully")
            assert True
        else:
            print_and_log("Error while validating the DTC servers")
            assert False
        sleep(10)
        print_and_log("*********** Test Case 31 Execution Completed ************")

    @pytest.mark.run(order=32)
    def test_032_NIOS_87856_Check_the_status_of_DTC_Server1(self):
        print_and_log("************* Check the status of DTC Server1  *************")
        flag = False
        for i in range(1, 10):
            health_status = check_dtc_server_health_status()
            if health_status == "GREEN":
                print_and_log("Server health status is in " + health_status + " color")
                flag = True
                break
            else:
                print_and_log("Server health status is not in RUNNING state")
                sleep(1)
                continue
        if flag == True:
            print_and_log("Server health status is updated correctly")
            assert True
        else:
            print_and_log("Server health status is not updated correctly")
            assert False
        print_and_log("********** Test Case 32 Execution Completed ***********")

    @pytest.mark.run(order=33)
    def test_033_NIOS_87856_Perform_the_dig_command_and_verify_the_response_is_from_dtc_Server1(self):
        print_and_log("********** Perform the dig command and verify the response on Grid master ************")
        Server_That_Responded = Perform_Dig_queires(config.grid1_master_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == "ipv6a." + zones[1] + ".":
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("********** Perform the dig command and verify the response on Grid member ************")
        Server_That_Responded = Perform_Dig_queires(config.grid1_member1_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == "ipv6a." + zones[1] + ".":
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("********* Test Case 33 Execution Completed *************")

    @pytest.mark.run(order=34)
    def test_034_NIOS_87856_modify_aaaa_record_ip_to_non_pingable_ip(self):
        print_and_log("************* modify aaaa record ip to non pingable ip **************")
        response = ib_NIOS.wapi_request('GET', object_type="record:aaaa")
        output = json.loads(response)
        print_and_log(output)
        record_ref = output[0]['_ref']
        print_and_log(record_ref)
        data = {"ipv6addr": "a::b"}
        response1 = ib_NIOS.wapi_request('PUT', object_type=record_ref, fields=json.dumps(data))
        print_and_log(response1)
        assert re.search(r'record:aaaa', response1)
        print_and_log("*********** Test Case 34 Execution Completed *************")

    @pytest.mark.run(order=35)
    def test_035_NIOS_87856_Validate_the_aaaa_record_ip_which_is_modified(self):
        print_and_log("************** Validate the aaaa record ip which is modified **************")
        response = ib_NIOS.wapi_request('GET', object_type="record:aaaa")
        response = json.loads(response)
        print_and_log(response)
        aaaa_record_ip = response[0]['ipv6addr']
        print_and_log(aaaa_record_ip)
        if aaaa_record_ip == "a::b":
            print_and_log("aaaa record ip is modified to" + aaaa_record_ip + " successfully")
            assert True
        else:
            print_and_log("Error while validating the aaaa record ip")
            assert False
        print_and_log("********** Test Case 35 Execution Completed ***********")

    @pytest.mark.run(order=36)
    def test_036_NIOS_87856_Check_if_the_dig_quereies_only_from_Server1_after_60_seconds(self):
        print_and_log("************ Check if the dig queries only from Server1 after 60 seconds *************")
        flag = False
        for i in range(0, 80):
            Server_That_Responded = Perform_Dig_queires(config.grid1_master_vip)
            print_and_log(Server_That_Responded)
            if Server_That_Responded != "ipv6a." + zones[1] + ".":
                print_and_log("Itteration " + str(i) + " : Server " + Server_That_Responded + " responded for the query")
                flag = True
                break
            else:
                print_and_log("Itteration " + str(i) + " : Still We see DTC server responding to DTC queries")
                sleep(1)
                continue
        if flag == True:
            print_and_log("DTC server stopped responding to queries")
            assert True
        else:
            print_and_log("DTC server continued to respond to the queries")
            assert False
        sleep(20)
        print_and_log("********** Test Case 36 Execution Completed ***********")

    @pytest.mark.run(order=37)
    def test_037_NIOS_87856_Check_the_status_of_DTC_Server1(self):
        print_and_log("************* Check the status of DTC Server1  *************")
        flag = False
        for i in range(1, 10):
            health_status = check_dtc_server_health_status()
            if health_status == "RED":
                print_and_log("Server health status is in " + health_status + " color")
                flag = True
                break
            else:
                print_and_log("Server health status is not in ERROR state")
                sleep(1)
                continue
        if flag == True:
            print_and_log("Server health status is updated correctly")
            assert True
        else:
            print_and_log("Server health status is not updated correctly")
            assert False
        print_and_log("********** Test Case 37 Execution Completed ***********")

    @pytest.mark.run(order=38)
    def test_038_NIOS_86457_Add_the_pingable_ip_to_the_DTC_server_1(self):
        print_and_log("************* Add the aaaa record to the DTC server 1 **************")
        response = ib_NIOS.wapi_request('GET', object_type="dtc:server", params="?name=ipv6a")
        response = json.loads(response)
        print_and_log(response)
        server_ref = response[0]['_ref']
        print_and_log(server_ref)
        data = {"name": "server1", "host": dtc_server_ips[0]}
        response1 = ib_NIOS.wapi_request('PUT', object_type=server_ref, fields=json.dumps(data))
        print_and_log(response1)
        assert re.search(r'dtc:server', response1)
        restart_the_grid_Services()
        print_and_log("********** Test Case 38 Execution Completed ***********")

    @pytest.mark.run(order=39)
    def test_039_NIOS_86457_validate_the_modified_dtc_server(self):
        print_and_log(" ************ Validate the dtc server modfied *************** ")
        servers = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name=server1')
        servers = json.loads(servers)
        print_and_log(servers)
        dtc_server_name = servers[0]['name']
        if dtc_server_name == server_name[0]:
            print_and_log("DTC server " + dtc_server_name + " modified successfully")
            assert True
        else:
            print_and_log("Error while validating the DTC servers")
            assert False
        sleep(10)
        print_and_log("*********** Test Case 39 Execution Completed ************")

    @pytest.mark.run(order=40)
    def test_040_NIOS_86457_Create_the_DTC_Pool_2_and_Assign_the_Server_members_server1_and_server2(self):
        print_and_log(" ************ Create the DTC pool 2 and Assign the Server members *************** ")
        server_ref = []
        for i in server_name[:2]:
            response_servers = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name=' + i)
            response_servers = json.loads(response_servers)
            ref = response_servers[0]['_ref']
            server_ref.append(ref)
        health_monitor_ref = getting_ref_of_the_dtc_health_monitors("dtc:monitor:icmp")
        print_and_log(health_monitor_ref)
        data = {"name": "pool2", "lb_preferred_method": "GLOBAL_AVAILABILITY",
                "servers": [{"ratio": 1, "server": str(server_ref[0])}, {"ratio": 1, "server": str(server_ref[1])}],
                "monitors": [str(health_monitor_ref)]}
        res = ib_NIOS.wapi_request('POST', object_type='dtc:pool', fields=json.dumps(data))
        print_and_log(res)
        assert re.search("dtc:pool", res)
        print_and_log(" ************ Test Case 40 Execution Completed *************** ")

    @pytest.mark.run(order=41)
    def test_041_NIOS_86457_validate_the_dtc_pool_2_created(self):
        print_and_log(" ************ Validate the dtc pool 2 created *************** ")
        response_servers = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool2')
        response_servers = json.loads(response_servers)
        print_and_log(response_servers)
        dtc_pool_name = response_servers[0]['name']
        if dtc_pool_name == "pool2":
            print_and_log("DTC Pool " + dtc_pool_name + " is created successfully")
            assert True
        else:
            print_and_log(" Error while validating the DTC Pool created")
            assert False
        print_and_log(" ************ Test Case 41 Execution Completed *************** ")

    @pytest.mark.run(order=42)
    def test_042_NIOS_86457_Add_Pool2_to_DTC_LBDN_1(self):
        print_and_log(" ************ Add Pool2 to DTC LBDN 1 ************ ")
        print_and_log("Getting ref of DTC_LBDN_1")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        ref = response[0]['_ref']
        print_and_log(ref)
        print_and_log("********** Getting the ref of pool ************")
        pool_name = ["pool1", "pool2"]
        pool_ref = []
        for i in pool_name:
            response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name='+i)
            response = json.loads(response)
            ref_pool = response[0]['_ref']
            pool_ref.append(ref_pool)
        print_and_log(pool_ref)
        print_and_log("********** Modify the lbdn by adding pool 2 ************")
        data = {"pools": [{"ratio": 1, "pool": pool_ref[0]}, {"ratio": 1, "pool": pool_ref[1]}]}
        print_and_log(data)
        response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
        response = json.loads(response)
        print_and_log("Validation of lbdn creation")
        assert re.search(r'dtc:lbdn', response)
        print_and_log("******** Restart the DNS service *********")
        restart_the_grid_Services()
        print_and_log(" ************ Test Case 42 Execution Completed *************** ")

    @pytest.mark.run(order=43)
    def test_043_NIOS_86457_Validate_the_DTC_LBDN1(self):
        print_and_log(" ************ Validate the DTC LBDN1 ************ ")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn')
        response = json.loads(response)
        ref_lbdn = response[0]['_ref']
        print_and_log(ref_lbdn)
        response = ib_NIOS.wapi_request('GET', object_type=ref_lbdn, params="?_return_fields=pools")
        response = json.loads(response)
        pool_name = response['pools'][1]['pool'].split(':')[2]
        print_and_log(pool_name)
        if pool_name == "pool2":
            print_and_log(pool_name+" is added to the DTC LBDN 1")
            assert True
        else:
            print_and_log("Validation for the pool 2 for DTC LBDN 1 failed")
            assert False
        print_and_log(" ************ Test Case 43 Execution Completed *************** ")

    @pytest.mark.run(order=44)
    def test_044_NIOS_86457_Disable_the_Pool_2_With_Disable_until_Manual_Enable_option(self):
        print_and_log("*********** Disable the Pool 2 With Disable until Manual Enable option *************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool2')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10,
                "disable_on": [config.grid1_master_fqdn, config.grid1_member1_fqdn],
                "disable_timeframe": "UNTIL_MANUAL_ENABLING", "dtc_object": ref_pool, "specific_time_disable": 60}
        output = dtc_object_failback_disable_options(data)
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC Pool object disabled successfully")
            assert True
        else:
            print_and_log("DTC Pool object is not Disabled")
            assert False
        print_and_log("************* Test Case 44 Execution Completed ***************")

    @pytest.mark.run(order=45)
    def test_045_NIOS_86457_Add_Consolidated_health_monitors_to_pool2_with_Full_health_communication_option_checked(self):
        print_and_log("*********** Add Consolidated health monitors to pool2 with Full health communication option checked ************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool2')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        health_monitor_ref = getting_ref_of_the_dtc_health_monitors("dtc:monitor:icmp")
        print_and_log(health_monitor_ref)
        data = {"consolidated_monitors": [{"availability": "ANY", "full_health_communication": True, "members": [config.grid1_master_fqdn], "monitor": health_monitor_ref}]}
        response1 = ib_NIOS.wapi_request('PUT', object_type=ref_pool, fields=json.dumps(data))
        print_and_log(response1)
        assert re.search(r'dtc:pool', response1)
        restart_the_grid_Services()
        print_and_log("************* Test Case 45 Execution Completed ***************")

    @pytest.mark.run(order=46)
    def test_046_NIOS_86457_Validate_Consolidated_health_monitors_added_to_pool2_with_Full_health_communication_option_checked(self):
        print_and_log("************** Validate Consolidated health monitors added to pool2 with Full health communication option checked **************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool2')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        response1 = ib_NIOS.wapi_request('GET', object_type=ref_pool, params="?_return_fields=consolidated_monitors")
        response1 = json.loads(response1)
        print_and_log(response1)
        availability = response1['consolidated_monitors'][0]['availability']
        full_health_communication = response1['consolidated_monitors'][0]['full_health_communication']
        members = response1['consolidated_monitors'][0]['members'][0]
        print_and_log(availability)
        print_and_log(full_health_communication)
        print_and_log(members)
        if availability == "ANY" and full_health_communication == True and members == config.grid1_master_fqdn:
            print_and_log("Consolidated monitors with availability "+availability+" and full health communication is set to TRUE with selected member "+members)
            assert True
        else:
            print_and_log("Validation for consolidated monitors failed for pool2")
            assert False
        print_and_log("************* Test Case 46 Execution Completed ***************")

    @pytest.mark.run(order=47)
    def test_047_NIOS_86457_configure_two_dtc_servers_server3_and_server4(self):
        print_and_log("************ Configure 2 dtc servers server3 and server4 ***************")
        server_obj = {server_name[2]: dtc_server_ips[3], server_name[3]: dtc_server_ips[4]}
        for i, j in server_obj.items():
            data = {"name": i, "host": j}
            response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
            print_and_log(response)
            assert re.search("dtc:server", response)
        restart_the_grid_Services()
        print_and_log("*********** Test Case 47 Execution Completed ************")

    @pytest.mark.run(order=48)
    def test_048_NIOS_86457_validate_the_dtc_servers_server3_and_server4(self):
        print_and_log(" ************ Validate the dtc servers server3 and server4 created *************** ")
        for i in server_name[2:]:
            servers = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name=' + i)
            servers = json.loads(servers)
            dtc_server_name = servers[0]['name']
            if dtc_server_name == "server3":
                print_and_log("DTC server " + dtc_server_name + " created successfully")
                assert True
            elif dtc_server_name == "server4":
                print_and_log("DTC server " + dtc_server_name + " created successfully")
                assert True
            else:
                print_and_log("Error while validating the DTC servers")
                assert False
        print_and_log("*********** Test Case 48 Execution Completed ************")

    @pytest.mark.run(order=49)
    def test_049_NIOS_86457_modify_pool2_and_configure_Server3_and_Server4(self):
        print_and_log(" ************ Modify pool2 and configure Server3 and Server4 *************** ")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool2')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        server_ref = []
        for i in server_name[2:]:
            response_servers = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name=' + i)
            response_servers = json.loads(response_servers)
            ref = response_servers[0]['_ref']
            server_ref.append(ref)
        data = {"servers": [{"ratio": 1, "server": server_ref[0]}, {"ratio": 1, "server": server_ref[1]}]}
        res = ib_NIOS.wapi_request('PUT', object_type=ref_pool, fields=json.dumps(data))
        print_and_log(res)
        assert re.search("dtc:pool", res)
        restart_the_grid_Services()
        print_and_log(" ************ Test Case 49 Execution Completed *************** ")

    @pytest.mark.run(order=50)
    def test_050_NIOS_86457_Validate_the_Server3_and_Server4_added_to_Pool2(self):
        print_and_log(" ************ Validate the Server3 and Server4 added to Pool2  ************ ")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params="?name=pool2")
        response = json.loads(response)
        ref_pool = response[0]['_ref']
        print_and_log(ref_pool)
        response1 = ib_NIOS.wapi_request('GET', object_type=ref_pool, params="?_return_fields=servers")
        response1 = json.loads(response1)
        print_and_log(response1)
        server_name_3 = response1['servers'][0]['server'].split(':')[2]
        server_name_4 = response1['servers'][1]['server'].split(':')[2]
        print_and_log(server_name_3)
        print_and_log(server_name_4)
        if server_name_3 == "server3" and server_name_4 == "server4":
            print_and_log("Servers "+server_name_3+" and "+server_name_4+ " Added successfully")
            assert True
        else:
            print_and_log("Validation for the servers server3 and server4 in pool2 failed")
            assert False
        print_and_log(" ************ Test Case 50 Execution Completed *************** ")

    @pytest.mark.run(order=51)
    def test_051_NIOS_86457_Check_the_status_of_all_DTC_Objects(self):
        print_and_log("************* Check the status of DTC Objects *************")
        server_health_status = check_dtc_object_health_status("dtc:server")
        pool_health_status = check_dtc_object_health_status("dtc:pool")
        lbdn_health_status = check_dtc_object_health_status("dtc:lbdn")
        failure_states = ["NONE", "UNKNOWN", "ERROR"]
        if server_health_status not in failure_states and pool_health_status not in failure_states and lbdn_health_status not in failure_states:
            print_and_log("Server health status is not in None or Unknown or Error state")
            assert True
        else:
            print_and_log("Server health status is in Error or None or Unknwon state")
            assert False
        print_and_log("********** Test Case 51 Execution Completed ***********")

    @pytest.mark.run(order=52)
    def test_052_NIOS_86457_Enable_the_Pool_2_with_Manual_Enable_option(self):
        print_and_log("*********** Enable the Pool 2 With Manual Enable option *************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool2')
        response = json.loads(response)
        ref_pool = response[0]['_ref']
        data = {"enable_on": [config.grid1_master_fqdn, config.grid1_member1_fqdn], "dtc_object": ref_pool}
        output = dtc_object_failback_enable_options(data)
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC Pool 2 object Enabled successfully")
            assert True
        else:
            print_and_log("DTC Pool 2 object is not enabled")
            assert False
        print_and_log("*********** Test Case 52 Execution Completed *************")


    @pytest.mark.run(order=53)
    def test_053_NIOS_86726_Disable_the_Pool_2_With_Disable_until_Manual_Enable_option(self):
        print_and_log("*********** Disable the Pool 2 With Disable until Manual Enable option *************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool2')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10,
                "disable_on": [config.grid1_master_fqdn, config.grid1_member1_fqdn],
                "disable_timeframe": "UNTIL_MANUAL_ENABLING", "dtc_object": ref_pool, "specific_time_disable": 60}
        output = dtc_object_failback_disable_options(data)
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC Pool object disabled successfully")
            assert True
        else:
            print_and_log("DTC Pool object is not Disabled")
            assert False
        print_and_log("************* Test Case 53 Execution Completed ***************")

    @pytest.mark.run(order=54)
    def test_054_NIOS_86726_Uncheck_the_full_health_communication_option_in_consolidated_monitors_under_pool2(self):
        print_and_log("*********** Uncheck the full health communication option in consolidated monitors under pool2 ************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool2')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        health_monitor_ref = getting_ref_of_the_dtc_health_monitors("dtc:monitor:icmp")
        print_and_log(health_monitor_ref)
        data = {"consolidated_monitors": [{"availability": "ANY", "full_health_communication": False, "members": [config.grid1_master_fqdn], "monitor": health_monitor_ref}]}
        response1 = ib_NIOS.wapi_request('PUT', object_type=ref_pool, fields=json.dumps(data))
        print_and_log(response1)
        assert re.search(r'dtc:pool', response1)
        restart_the_grid_Services()
        print_and_log("************* Test Case 54 Execution Completed ***************")

    @pytest.mark.run(order=55)
    def test_055_NIOS_86726_Verify_the_Full_health_communication_box_is_unchecked_in_consolidated_health_monitors(self):
        print_and_log("************** Verify the Full health communication box is unchecked in consolidated health monitors **************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool2')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        response1 = ib_NIOS.wapi_request('GET', object_type=ref_pool, params="?_return_fields=consolidated_monitors")
        response1 = json.loads(response1)
        print_and_log(response1)
        full_health_communication = response1['consolidated_monitors'][0]['full_health_communication']
        print_and_log(full_health_communication)
        if full_health_communication == False :
            print_and_log("Consolidated monitors with full health communication set to False")
            assert True
        else:
            print_and_log("Validation for consolidated monitors failed for pool2")
            assert False
        print_and_log("************* Test Case 55 Execution Completed ***************")

    @pytest.mark.run(order=56)
    def test_056_NIOS_86726_Enable_Pool2_with_Manual_enable_option(self):
        print_and_log("*********** Enable the Pool 2 With Manual Enable option *************")
        log("start", "/infoblox/var/infoblox.log", config.grid_vip)
        log("start", "/infoblox/var/infoblox.log", config.grid1_member1_vip)
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool2')
        response = json.loads(response)
        ref_pool = response[0]['_ref']
        data = {"enable_on": [config.grid1_master_fqdn, config.grid1_member1_fqdn], "dtc_object": ref_pool}
        output = dtc_object_failback_enable_options(data)
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC Pool 2 object Enabled successfully")
            assert True
        else:
            print_and_log("DTC Pool 2 object is not enabled")
            assert False
        print_and_log("*********** Test Case 56 Execution Completed *************")

    @pytest.mark.run(order=57)
    def test_057_NIOS_86726_Verify_If_there_are_no_Partial_Health_update_Error_messages_in_grid_master_infoblox_log(self):
        print_and_log("************** Verify If there are no Partial Health update Error messages in grid master infoblox log ***************")
        validate_the_partial_health_update_error_logs(config.grid_vip)
        print_and_log("*********** Test Case 57 Execution Completed ************")

    @pytest.mark.run(order=58)
    def test_058_NIOS_86726_Verify_If_there_are_no_Partial_Health_update_Error_messages_in_grid_member_infoblox_log(self):
        print_and_log("************** Verify If there are no Partial Health update Error messages in grid member infoblox log ***************")
        validate_the_partial_health_update_error_logs(config.grid1_member1_vip)
        print_and_log("*********** Test Case 58 Execution Completed ************")

    @pytest.mark.run(order=59)
    def test_059_NIOS_86726_Disable_the_Pool_2_With_Disable_until_DNS_Restart_option(self):
        print_and_log("*********** Disable the Pool 2 With Disable until DNS restart option *************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool2')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10,
                "disable_on": [config.grid1_master_fqdn, config.grid1_member1_fqdn],
                "disable_timeframe": "UNTIL_DNS_RESTART", "dtc_object": ref_pool, "specific_time_disable": 60}
        output = dtc_object_failback_disable_options(data)
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC Pool object disabled successfully")
            assert True
        else:
            print_and_log("DTC Pool object is not Disabled")
            assert False
        print_and_log("************* Test Case 59 Execution Completed ***************")

    @pytest.mark.run(order=60)
    def test_060_NIOS_86726_Enable_Pool2_with_Manual_enable_option(self):
        print_and_log("*********** Enable the Pool 2 With Manual Enable option *************")
        log("start", "/infoblox/var/infoblox.log", config.grid_vip)
        log("start", "/infoblox/var/infoblox.log", config.grid1_member1_vip)
        restart_the_grid_Services()
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool2')
        response = json.loads(response)
        ref_pool = response[0]['_ref']
        data = {"dtc_object": ref_pool}
        output = dtc_object_failback_status(data)
        print_and_log(output)
        if config.grid1_master_fqdn in output and config.grid1_member1_fqdn in output:
            print_and_log("DTC Pool 2 object is enabled")
            assert True
        else:
            print_and_log("DTC Pool 2 object is not enabled")
            assert False
        print_and_log("*********** Test Case 60 Execution Completed *************")

    @pytest.mark.run(order=61)
    def test_061_NIOS_86726_Verify_If_there_are_no_Partial_Health_update_Error_messages_in_grid_master_infoblox_log(self):
        print_and_log("************** Verify If there are no Partial Health update Error messages in grid master infoblox log ***************")
        validate_the_partial_health_update_error_logs(config.grid_vip)
        print_and_log("*********** Test Case 61 Execution Completed ************")

    @pytest.mark.run(order=62)
    def test_062_NIOS_86726_Verify_If_there_are_no_Partial_Health_update_Error_messages_in_grid_member_infoblox_log(self):
        print_and_log("************** Verify If there are no Partial Health update Error messages in grid member infoblox log ***************")
        validate_the_partial_health_update_error_logs(config.grid1_member1_vip)
        print_and_log("*********** Test Case 62 Execution Completed ************")

    @pytest.mark.run(order=63)
    def test_063_NIOS_86726_Disable_the_Pool2_With_Disable_until_Specified_time(self):
        print_and_log("*********** Disable the Pool2 With Disable until Specified time *************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool2')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10,
                "disable_on": [config.grid1_master_fqdn, config.grid1_member1_fqdn],
                "disable_timeframe": "FOR_SPECIFIED_TIME", "dtc_object": ref_pool, "specific_time_disable": 300}
        output = dtc_object_failback_disable_options(data)
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC Pool 2 object disabled successfully")
            assert True
        else:
            print_and_log("DTC Pool 2 object is not Disabled")
            assert False
        print_and_log("Test Case 63 Execution Completed")

    @pytest.mark.run(order=64)
    def test_064_NIOS_86726_wait_for_300_seconds_and_validate_the_pool_status(self):
        print_and_log("*********** Wait for 300 seconds and validate the pool status ***********")
        log("start", "/infoblox/var/infoblox.log", config.grid_vip)
        log("start", "/infoblox/var/infoblox.log", config.grid1_member1_vip)
        sleep(300)
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool2')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        data = {"dtc_object": ref_pool}
        output = dtc_object_failback_status(data)
        print_and_log(output)
        if config.grid1_master_fqdn in output and config.grid1_member1_fqdn in output:
            print_and_log("DTC Pool 2 object is enabled")
            assert True
        else:
            print_and_log("DTC Pool 2 object is not enabled")
            assert False
        print_and_log("Test Case 64 Execution Completed")

    @pytest.mark.run(order=65)
    def test_065_NIOS_86726_Verify_If_there_are_no_Partial_Health_update_Error_messages_in_grid_master_infoblox_log(self):
        print_and_log("************** Verify If there are no Partial Health update Error messages in grid master infoblox log ***************")
        validate_the_partial_health_update_error_logs(config.grid_vip)
        print_and_log("*********** Test Case 65 Execution Completed ************")

    @pytest.mark.run(order=66)
    def test_066_NIOS_86726_Verify_If_there_are_no_Partial_Health_update_Error_messages_in_grid_member_infoblox_log(self):
        print_and_log("************** Verify If there are no Partial Health update Error messages in grid member infoblox log ***************")
        validate_the_partial_health_update_error_logs(config.grid1_member1_vip)
        print_and_log("*********** Test Case 66 Execution Completed ************")

    @pytest.mark.run(order=67)
    def test_067_NIOS_86141_Check_the_status_of_DTC_pool(self):
        print_and_log("************* Check the status of DTC Pool *************")
        pool_health_status = check_dtc_object_health_status("dtc:pool")
        failure_states = ["NONE", "UNKNOWN", "ERROR"]
        if pool_health_status not in failure_states:
            print_and_log("Pool health status is not in None or Unknown or Error state")
            assert True
        else:
            print_and_log("Pool health status is in Error or None or Unknown state")
            assert False
        print_and_log("********** Test Case 67 Execution Completed ***********")

    @pytest.mark.run(order=68)
    def test_068_NIOS_86691_Modify_the_Pool_1_and_add_two_health_monitors_and_add_Availability_requirements_to_at_least_1(self):
        print_and_log("*********** Modify the Pool 1 and add two health monitors and add Availability requirements to at least 1 *************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        icmp_health_ref = getting_ref_of_the_dtc_health_monitors("dtc:monitor:icmp")
        snmp_health_ref = getting_ref_of_the_dtc_health_monitors("dtc:monitor:http")
        data = {"monitors": [icmp_health_ref, snmp_health_ref], "availability": "QUORUM", "quorum": 1}
        response1 = ib_NIOS.wapi_request('PUT', object_type=ref_pool, fields=json.dumps(data))
        print_and_log(response1)
        assert re.search(r'dtc:pool', response1)
        restart_the_grid_Services()
        print_and_log("********** Test Case 68 Execution Completed ***********")

    @pytest.mark.run(order=69)
    def test_069_NIOS_86691_Validate_the_Pool_1_health_monitors_and_Availability_requirements_set_to_at_least_1(self):
        print_and_log("************** Validate the Pool 1 health monitors and Availability requirements set to at least 1 ****************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        icmp_health_ref = getting_ref_of_the_dtc_health_monitors("dtc:monitor:icmp")
        snmp_health_ref = getting_ref_of_the_dtc_health_monitors("dtc:monitor:http")
        response1 = ib_NIOS.wapi_request('GET', object_type=ref_pool, params='?_return_fields=monitors')
        response1 = json.loads(response1)
        print_and_log(response1)
        monitors = response1['monitors']
        response2 = ib_NIOS.wapi_request('GET', object_type=ref_pool, params='?_return_fields=quorum')
        response2 = json.loads(response2)
        print_and_log(response2)
        quorum = response2['quorum']
        response3 = ib_NIOS.wapi_request('GET', object_type=ref_pool, params='?_return_fields=availability')
        response3 = json.loads(response3)
        print_and_log(response3)
        availability = response3['availability']
        if "icmp" in monitors and "http" in monitors and quorum == 1 and availability == "QUORUM":
            print_and_log("2 Health monitors are configured with avaialability set to at least 1")
            assert True
        else:
            print_and_log("Validation of pool1 failed ")
            assert False
        print_and_log("********** Test Case 69 Execution Completed ***********")

    @pytest.mark.run(order=70)
    def test_070_NIOS_86691_Check_the_status_of_Server_Objects(self):
        print_and_log("************* Check the status of DTC Server Objects *************")
        sleep(60)
        server_health_status = check_dtc_object_health_status("dtc:server")
        for i in server_health_status:
            print_and_log(i)
            if i == "GREEN":
                print_and_log("Server object status is in "+i+" state")
                assert True
            else:
                print_and_log("Server object status is not in running state")
                assert False
        print_and_log("********** Test Case 70 Execution Completed ***********")

    @pytest.mark.run(order=71)
    def test_071_NIOS_86691_Perform_the_dig_command_and_verify_the_response_is_from_dtc_Server1(self):
        print_and_log("********** Perform the dig command and verify the response on Grid master ************")
        Server_That_Responded = Perform_Dig_queires(config.grid1_master_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[0]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("********** Perform the dig command and verify the response on Grid member ************")
        Server_That_Responded = Perform_Dig_queires(config.grid1_member1_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[0]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("********* Test Case 71 Execution Completed *************")

    @pytest.mark.run(order=72)
    def test_072_NIOS_86418_Modify_the_Pool_1_add_Availability_requirements_to_any(self):
        print_and_log("*********** Modify the Pool 1 add Availability requirements to any *************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        data = {"availability": "ANY"}
        response1 = ib_NIOS.wapi_request('PUT', object_type=ref_pool, fields=json.dumps(data))
        print_and_log(response1)
        assert re.search(r'dtc:pool', response1)
        restart_the_grid_Services()
        print_and_log("********** Test Case 73 Execution Completed ***********")

    @pytest.mark.run(order=73)
    def test_073_NIOS_86418_Validate_the_Pool_1_Availability_requirements_set_to_any(self):
        print_and_log("************** Validate the Pool 1 Availability requirements set to any ****************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        response3 = ib_NIOS.wapi_request('GET', object_type=ref_pool, params='?_return_fields=availability')
        response3 = json.loads(response3)
        print_and_log(response3)
        availability = response3['availability']
        if availability == "ANY":
            print_and_log("2 Health monitors are configured with avaialability set to ANY")
            assert True
        else:
            print_and_log("Validation of pool1 failed ")
            assert False
        print_and_log("********** Test Case 73 Execution Completed ***********")

    @pytest.mark.run(order=74)
    def test_074_NIOS_86418_Check_the_status_of_Server_Objects(self):
        print_and_log("************* Check the status of DTC Server Objects *************")
        sleep(60)
        server_health_status = check_dtc_object_health_status("dtc:server")
        for i in server_health_status:
            print_and_log(i)
            if i == "GREEN":
                print_and_log("Server object status is in " + i + " state")
                assert True
            else:
                print_and_log("Server object status is not in running state")
                assert False
        print_and_log("********** Test Case 74 Execution Completed ***********")

    @pytest.mark.run(order=75)
    def test_075_NIOS_86418_Perform_the_dig_command_and_verify_the_response_is_from_dtc_Server1(self):
        print_and_log("********** Perform the dig command and verify the response on Grid master ************")
        Server_That_Responded = Perform_Dig_queires(config.grid1_master_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[0]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("********** Perform the dig command and verify the response on Grid member ************")
        Server_That_Responded = Perform_Dig_queires(config.grid1_member1_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[0]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("********* Test Case 75 Execution Completed *************")

    @pytest.mark.run(order=76)
    def test_076_NIOS_86418_Modify_the_Pool_1_add_Availability_requirements_to_ALL_and_add_one_health_monitor(self):
        print_and_log("*********** Modify the Pool 1 add Availability requirements to ALL and add one health monitor *************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        icmp_health_ref = getting_ref_of_the_dtc_health_monitors("dtc:monitor:icmp")
        data = {"monitors": [icmp_health_ref], "availability": "ALL"}
        response1 = ib_NIOS.wapi_request('PUT', object_type=ref_pool, fields=json.dumps(data))
        print_and_log(response1)
        assert re.search(r'dtc:pool', response1)
        restart_the_grid_Services()
        print_and_log("********** Test Case 76 Execution Completed ***********")

    @pytest.mark.run(order=77)
    def test_077_NIOS_86418_Validate_the_Pool_1_Availability_requirements_set_to_all(self):
        print_and_log("************** Validate the Pool 1 Availability requirements set to all ****************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        response3 = ib_NIOS.wapi_request('GET', object_type=ref_pool, params='?_return_fields=availability')
        response3 = json.loads(response3)
        print_and_log(response3)
        availability = response3['availability']
        if availability == "ALL":
            print_and_log("Pool1 avaialability is set to ANY")
            assert True
        else:
            print_and_log("Validation of pool1 failed ")
            assert False
        print_and_log("********** Test Case 77 Execution Completed ***********")


    @pytest.mark.run(order=78)
    def test_078_NIOS_86195_Configure_the_topology_rule_with_subnet_rule_pool_as_destination(self):
        print_and_log("************* Configure the topology rule with subnet rule pool as destination **************")
        pool_name = ["pool1", "pool2"]
        pool_ref = []
        for i in pool_name:
            response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name='+i)
            response = json.loads(response)
            print_and_log(response)
            ref_pool = response[0]['_ref']
            pool_ref.append(ref_pool)
        print_and_log(pool_ref)
        data = {"name": "dtc_topology_1", "rules": [{"sources": [{"source_op": "IS", "source_type": "SUBNET", "source_value": "10.0.0.0/8"}],"dest_type": "POOL", "destination_link": pool_ref[0]}, {"sources": [{"source_op": "IS", "source_type": "SUBNET", "source_value": "20.0.0.0/8"}],"dest_type": "POOL", "destination_link": pool_ref[1]}]}
        response = ib_NIOS.wapi_request('POST', object_type='dtc:topology', fields=json.dumps(data))
        print_and_log(response)
        assert re.search(r'dtc:topology', response)
        print_and_log("********** Test Case 78 Execution Completed ***********")

    @pytest.mark.run(order=79)
    def test_079_NIOS_86195_Validate_the_topology_rule_with_subnet_rule_pool_as_destination(self):
        print_and_log("************* Validate the topology rule with subnet rule pool as destination **************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:topology', params='?name=dtc_topology_1')
        response = json.loads(response)
        print_and_log(response)
        topo_name = response[0]['name']
        print_and_log(topo_name)
        if topo_name == "dtc_topology_1":
            print_and_log("Topo rule "+topo_name+" configured successfully")
            assert True
        else:
            print_and_log("Validation for Topo rule configured successfully")
            assert False
        print_and_log("********** Test Case 79 Execution Completed ***********")

    @pytest.mark.run(order=80)
    def test_080_NIOS_86195_Add_the_topo_rule_to_the_LBDN(self):
        print_and_log("*********** Add the topo rule to the LBDN *************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:topology', params='?name=dtc_topology_1')
        response = json.loads(response)
        print_and_log(response)
        ref_topo = response[0]['_ref']
        print_and_log("********** Get refrence of DTC LBDN ************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        print_and_log(response)
        ref_lbdn = response[0]['_ref']
        data = {"lb_method": "TOPOLOGY", "topology": ref_topo}
        response1 = ib_NIOS.wapi_request('PUT', object_type=ref_lbdn, fields=json.dumps(data))
        print_and_log(response1)
        assert re.search(r'dtc:lbdn', response1)
        restart_the_grid_Services()
        print_and_log("********** Test Case 80 Execution Completed ***********")

    @pytest.mark.run(order=81)
    def test_081_NIOS_86195_Validate_the_topo_rule_added_to_LBDN(self):
        print_and_log("************** Validate the topo rule added to LBDN ***************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        print_and_log(response)
        ref_lbdn = response[0]['_ref']
        response1 = ib_NIOS.wapi_request('GET', object_type=ref_lbdn, params='?_return_fields=lb_method')
        response1 = json.loads(response1)
        print_and_log(response1)
        lb_method = response1['lb_method']
        response2 = ib_NIOS.wapi_request('GET', object_type=ref_lbdn, params='?_return_fields=topology')
        response2 = json.loads(response2)
        print_and_log(response2)
        topo_name = response2['topology'].split(':')[2]
        if lb_method == "TOPOLOGY" and topo_name == "dtc_topology_1":
            print_and_log("Load balancing method "+lb_method+" is configured with topology rule"+topo_name)
            assert True
        else:
            print_and_log("Validation for the LBDN failed")
            assert False
        print_and_log("********** Test Case 81 Execution Completed ***********")

    @pytest.mark.run(order=82)
    def test_082_NIOS_86195_Delete_the_pool2_from_the_LBDN_Pool_members(self):
        print_and_log("************* Delete the pool2 from the LBDN Pool members *************")
        print_and_log("Getting ref of DTC_LBDN_1")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        ref = response[0]['_ref']
        print_and_log(ref)
        print_and_log("********** Getting the ref of pool ************")
        pool_name = ["pool1", "pool2"]
        pool_ref = []
        for i in pool_name:
            response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=' + i)
            response = json.loads(response)
            ref_pool = response[0]['_ref']
            pool_ref.append(ref_pool)
        print_and_log(pool_ref)
        print_and_log("********** Delete the pool2 in pool members ************")
        data = {"pools": [{"ratio": 1, "pool": pool_ref[0]}]}
        print_and_log(data)
        response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
        print_and_log(response)
        print_and_log("Validation of lbdn creation")
        assert re.search(r'dtc:lbdn', response)
        print_and_log("******** Restart the DNS service *********")
        restart_the_grid_Services()
        print_and_log(" ************ Test Case 82 Execution Completed *************** ")

    @pytest.mark.run(order=83)
    def test_083_NIOS_86195_Validate_If_Pool2_is_deleted_from_LBDN_Pool_members(self):
        print_and_log(" ************ Validate the DTC LBDN1 ************ ")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn')
        response = json.loads(response)
        ref_lbdn = response[0]['_ref']
        print_and_log(ref_lbdn)
        response = ib_NIOS.wapi_request('GET', object_type=ref_lbdn, params="?_return_fields=pools")
        response = json.loads(response)
        pool_name = response['pools'][0]['pool'].split(':')[2]
        print_and_log(pool_name)
        if pool_name != "pool2":
            print_and_log("Pool 2 is deleted from LBDN pool members")
            assert True
        else:
            print_and_log("Validation for the pool 2 for DTC LBDN 1 failed")
            assert False
        print_and_log(" ************ Test Case 83 Execution Completed *************** ")

    @pytest.mark.run(order=84)
    def test_084_NIOS_86195_Validate_If_Pool2_status_is_running_after_deleting_from_LBDN_Pool_members(self):
        print_and_log("*********** Validate If Pool2 status is running after deleting from LBDN Pool members ***********")
        output = check_dtc_object_health_status('dtc:pool')
        print_and_log(output)
        failure_states = ["NONE", "UNKNOWN", "ERROR"]
        if output not in failure_states:
            print_and_log("Pool health status is not in None or Unknown or Error state")
            assert True
        else:
            print_and_log("Pool health status is in Error or None or Unknown state")
            assert False
        print_and_log("********** Test Case 84 Execution Completed ***********")




    @pytest.mark.run(order=85)
    def test_085_NIOS_86195_Configure_the_topology_rule_with_Geo_ip_rule_pool_as_destination(self):
        print_and_log("************* Configure the topology rule with Geo ip rule pool as destination **************")
        pool_name = ["pool1", "pool2"]
        pool_ref = []
        for i in pool_name:
            response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=' + i)
            response = json.loads(response)
            print_and_log(response)
            ref_pool = response[0]['_ref']
            pool_ref.append(ref_pool)
        print_and_log(pool_ref)
        data = {"name": "geo_ip_rule", "rules": [
            {"sources": [{
            "source_op": "IS",
            "source_type": "CITY",
            "source_value": "Bengaluru"
        },
        {
            "source_op": "IS",
            "source_type": "SUBDIVISION",
            "source_value": "Karnataka"
        },
        {
            "source_op": "IS",
            "source_type": "COUNTRY",
            "source_value": "India"
        },
        {
            "source_op": "IS",
            "source_type": "CONTINENT",
            "source_value": "Asia"
        }],
             "dest_type": "POOL", "destination_link": pool_ref[0]},
            {"sources": [{
            "source_op": "IS",
            "source_type": "CONTINENT",
            "source_value": "Asia"
        },
        {
            "source_op": "IS",
            "source_type": "SUBDIVISION",
            "source_value": "Karnataka"
        },
        {
            "source_op": "IS",
            "source_type": "CITY",
            "source_value": "Kunigal"
        },
        {
            "source_op": "IS",
            "source_type": "COUNTRY",
            "source_value": "India"
        }],
             "dest_type": "POOL", "destination_link": pool_ref[1]}]}
        print_and_log(data)
        response = ib_NIOS.wapi_request('POST', object_type='dtc:topology', fields=json.dumps(data))
        print_and_log(response)
        assert re.search(r'dtc:topology', response)
        print_and_log("********** Test Case 85 Execution Completed ***********")

    @pytest.mark.run(order=86)
    def test_086_NIOS_86195_Validate_the_topology_rule_with_geo_ip_rule_pool_as_destination(self):
        print_and_log("************* Validate the topology rule with geo ip rule pool as destination **************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:topology', params='?name=geo_ip_rule')
        response = json.loads(response)
        print_and_log(response)
        topo_name = response[0]['name']
        print_and_log(topo_name)
        if topo_name == "geo_ip_rule":
            print_and_log("Topo rule " + topo_name + " configured successfully")
            assert True
        else:
            print_and_log("Validation for Topo rule configured successfully")
            assert False
        print_and_log("********** Test Case 86 Execution Completed ***********")



    @pytest.mark.run(order=87)
    def test_087_NIOS_86195_Add_the_geo_topo_rule_to_the_LBDN(self):
        print_and_log("*********** Add the geo topo rule to the LBDN *************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:topology', params='?name=geo_ip_rule')
        response = json.loads(response)
        print_and_log(response)
        ref_topo = response[0]['_ref']
        print_and_log("********** Get refrence of DTC LBDN ************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        print_and_log(response)
        ref_lbdn = response[0]['_ref']
        data = {"lb_method": "TOPOLOGY", "topology": ref_topo}
        response1 = ib_NIOS.wapi_request('PUT', object_type=ref_lbdn, fields=json.dumps(data))
        print_and_log(response1)
        assert re.search(r'dtc:lbdn', response1)
        restart_the_grid_Services()
        print_and_log("********** Test Case 87 Execution Completed ***********")

    @pytest.mark.run(order=88)
    def test_088_NIOS_86195_Validate_the_goe_topo_rule_added_to_LBDN(self):
        print_and_log("************** Validate the geo topo rule added to LBDN ***************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        print_and_log(response)
        ref_lbdn = response[0]['_ref']
        response1 = ib_NIOS.wapi_request('GET', object_type=ref_lbdn, params='?_return_fields=lb_method')
        response1 = json.loads(response1)
        print_and_log(response1)
        lb_method = response1['lb_method']
        response2 = ib_NIOS.wapi_request('GET', object_type=ref_lbdn, params='?_return_fields=topology')
        response2 = json.loads(response2)
        print_and_log(response2)
        topo_name = response2['topology'].split(':')[2]
        if lb_method == "TOPOLOGY" and topo_name == "geo_ip_rule":
            print_and_log("Load balancing method " + lb_method + " is configured with topology rule" + topo_name)
            assert True
        else:
            print_and_log("Validation for the LBDN failed")
            assert False
        print_and_log("********** Test Case 88 Execution Completed ***********")

    @pytest.mark.run(order=89)
    def test_089_NIOS_86195_Validate_If_Pool2_status_is_running_after_deleting_from_LBDN_Pool_members(self):
        print_and_log("*********** Validate If Pool2 status is running after deleting from LBDN Pool members ***********")
        output = check_dtc_object_health_status('dtc:pool')
        print_and_log(output)
        failure_states = ["NONE", "UNKNOWN", "ERROR"]
        if output not in failure_states:
            print_and_log("Pool health status is not in None or Unknown or Error state")
            assert True
        else:
            print_and_log("Pool health status is in Error or None or Unknown state")
            assert False
        print_and_log("********** Test Case 89 Execution Completed ***********")

    @pytest.mark.run(order=90)
    def test_090_NIOS_86896_Create_Custom_Extensible_Attribute_required_for_topo_rule(self):
        print_and_log("******** Creation of Custom Externsible Attribute with Type String for topo rule **********")
        data = {"name": "EA_string", "type": "STRING"}
        response = ib_NIOS.wapi_request('POST', object_type='extensibleattributedef', fields=json.dumps(data))
        print_and_log(response)
        assert re.search(r'EA_string', response)
        print_and_log("********** Test Case 90 Execution Completed ***********")



    @pytest.mark.run(order=91)
    def test_091_NIOS_86896_Validation_of_Custom_Extensible_Attribute_that_is_created(self):
        print_and_log("************ Validation of Custom Extensible Attribute that is created *************")
        response = ib_NIOS.wapi_request('GET', object_type='extensibleattributedef', params='?name=EA_string')
        response = json.loads(response)
        ref_name = response[0]['name']
        ref_type = response[0]['type']
        if ref_name == "EA_string" and ref_type == "STRING":
            print_and_log("Custom EA " + ref_name + " with type " + ref_type + " is configured successfully")
            assert True
        else:
            print_and_log("Validation for Custom Extensible attribute")
            assert False
        print_and_log("********** Test Case 91 Execution Completed ***********")

    @pytest.mark.run(order=92)
    def test_092_NIOS_86896_Assign_the_Custom_EA_EA_string_in_Grid_Properties_Traffic_Control(self):
        print_and_log("********** Assign the Custom EA EA_string in Grid Properties Traffic Conftrol w************")
        response = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        response = json.loads(response)
        ref = response[0]['_ref']
        data = {"dtc_topology_ea_list": ["EA_string"]}
        response1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
        print_and_log(response1)
        assert re.search(r'grid:dns', response1)
        rebuild_services()
        # validate Custom EA
        print_and_log("************ Test Case 92 Execution completed *************")

    @pytest.mark.run(order=93)
    def test_093_NIOS_86896_Validation_of_the_Custom_EA_EA_string_in_Grid_Properties_Traffic_Control(self):
        print_and_log("********** Validation of the Custom EA EA_string in Grid Properties TrafficControl ***********")
        response = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        response = json.loads(response)
        ref = response[0]['_ref']
        response = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=dtc_topology_ea_list')
        response = json.loads(response)
        out = response['dtc_topology_ea_list'][0]
        print_and_log(out)
        if out == "EA_string":
            print_and_log(" Custome EA " + out + " configured in Grid DNS properties")
            assert True
        else:
            print_and_log(" Error while Validating the Custom EA in Grid DNS properties")
            assert False
        print_and_log("************ Test Case 93 Execution completed *************")



    @pytest.mark.run(order=94)
    def test_094_NIOS_86896_ADD_Two_IPV4_Networks(self):
        print_and_log("******** Add Two IPV4 Network *********")
        data = {"network": config.ipv4network1, "extattrs": {"EA_string": {"value": "network2"}}}
        response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data))
        print_and_log(response)
        assert re.search(r'network', response)
        data = {"network": config.ipv4network2, "extattrs": {"EA_string": {"value": "network1"}}}
        response1 = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data))
        assert re.search(r'network', response1)
        print_and_log(response1)
        rebuild_services()
        print_and_log("************ Test Case 94 Execution completed *************")

    @pytest.mark.run(order=95)
    def test_095_NIOS_86896_Validation_of_IPV4_Network(self):
        print_and_log("********* Validation of IPV4 Network ***********")
        networks = [config.ipv4network1, config.ipv4network2]
        network_name = []
        for i in networks:
            response = ib_NIOS.wapi_request('GET', object_type="network", params='?network=' + i)
            response = json.loads(response)
            print_and_log(response)
            net_name = response[0]['network']
            network_name.append(net_name)
        print_and_log(network_name)
        if network_name == networks:
            print_and_log("IPV4 Networks are created successfully")
            assert True
        else:
            print_and_log("Error while validating the IPV4 network")
            assert False
        print_and_log("Test Case 95 Execution completed")



    @pytest.mark.run(order=96)
    def test_096_NIOS_86896_Create_the_DTC_topology_Rule_with_extensible_rule_with_pool_as_Destination(self):
        print_and_log("********* Create the DTC topology Rule with extensible rule with pool as Destination ***********")
        pool_list = ["pool1", "pool2"]
        pool_ref = []
        for i in pool_list:
            response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=' + i)
            response_servers = json.loads(response)
            ref = response_servers[0]['_ref']
            pool_ref.append(ref)
        print_and_log(pool_ref)
        data = {"name": "ea-rule1", "rules": [{"sources": [{"source_op": "IS", "source_type": "EA0", "source_value": "network1"}], "dest_type": "POOL","destination_link": pool_ref[0]}, {"sources": [{"source_op": "IS", "source_type": "EA0", "source_value": "network2"}], "dest_type": "POOL", "destination_link": pool_ref[1]}]}
        print_and_log(data)
        response = ib_NIOS.wapi_request('POST', object_type='dtc:topology', fields=json.dumps(data))
        print_and_log(response)
        assert re.search(r'dtc:topology', response)
        print_and_log("********* Test Case 96 Execution completed ***********")



    @pytest.mark.run(order=97)
    def test_097_NIOS_86896_Validate_the_topology_rule_with_extensible_attribute_rule_pool_as_destination(self):
        print_and_log("************* Validate the topology rule with extensible attribute rule pool as destination **************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:topology', params='?name=ea-rule1')
        response = json.loads(response)
        print_and_log(response)
        topo_name = response[0]['name']
        print_and_log(topo_name)
        if topo_name == "ea-rule1":
            print_and_log("Topo rule " + topo_name + " configured successfully")
            assert True
        else:
            print_and_log("Validation for Topo rule configured successfully")
            assert False
        print_and_log("********** Test Case 97 Execution Completed ***********")



    @pytest.mark.run(order=98)
    def test_098_NIOS_86896_Add_the_geo_topo_rule_to_the_LBDN(self):
        print_and_log("*********** Add the geo topo rule to the LBDN *************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:topology', params='?name=geo_ip_rule')
        response = json.loads(response)
        print_and_log(response)
        ref_topo = response[0]['_ref']
        print_and_log("********** Get refrence of DTC LBDN ************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        print_and_log(response)
        ref_lbdn = response[0]['_ref']
        data = {"lb_method": "TOPOLOGY", "topology": ref_topo}
        response1 = ib_NIOS.wapi_request('PUT', object_type=ref_lbdn, fields=json.dumps(data))
        print_and_log(response1)
        assert re.search(r'dtc:lbdn', response1)
        restart_the_grid_Services()
        print_and_log("********** Test Case 98 Execution Completed ***********")



    @pytest.mark.run(order=99)
    def test_099_NIOS_86896_Validate_the_topo_rule_added_to_LBDN(self):
        print_and_log("************** Validate the topo rule added to LBDN ***************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        print_and_log(response)
        ref_lbdn = response[0]['_ref']
        response1 = ib_NIOS.wapi_request('GET', object_type=ref_lbdn, params='?_return_fields=lb_method')
        response1 = json.loads(response1)
        print_and_log(response1)
        lb_method = response1['lb_method']
        response2 = ib_NIOS.wapi_request('GET', object_type=ref_lbdn, params='?_return_fields=topology')
        response2 = json.loads(response2)
        print_and_log(response2)
        topo_name = response2['topology'].split(':')[2]
        if lb_method == "TOPOLOGY" and topo_name == "geo_ip_rule":
            print_and_log("Load balancing method " + lb_method + " is configured with topology rule" + topo_name)
            assert True
        else:
            print_and_log("Validation for the LBDN failed")
            assert False
        print_and_log("********** Test Case 99 Execution Completed ***********")



    @pytest.mark.run(order=100)
    def test_100_NIOS_86896_Validate_If_Pool2_status_is_running_after_deleting_from_LBDN_Pool_members(self):
        print_and_log("*********** Validate If Pool2 status is running after deleting from LBDN Pool members ***********")
        output = check_dtc_object_health_status('dtc:pool')
        print_and_log(output)
        failure_states = ["NONE", "UNKNOWN", "ERROR"]
        if output not in failure_states:
            print_and_log("Pool health status is not in None or Unknown or Error state")
            assert True
        else:
            print_and_log("Pool health status is in Error or None or Unknown state")
            assert False
        print_and_log("********** Test Case 100 Execution Completed ***********")

    @pytest.mark.run(order=101)
    def test_101_NIOS_86896_Disconnect_Grid_member_from_Grid_Master(self):
        print_and_log("************* Disconnect Grid member from Grid Master ***************")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@' + config.grid1_member1_vip)
            child.logfile = sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline("set vpn_comm block")
            child.expect('successfully.')
            output = child.before
            print_and_log(output)
            child.close()
        except Exception as e:
            child.close()
            print("Error while executing the CLI command")
            print(e)
            assert False
        sleep(60)
        print_and_log("*********** Test Case 101 Execution Completed ************")

    @pytest.mark.run(order=102)
    def test_102_NIOS_86896_Verify_if_the_member_node_is_offline(self):
        print_and_log("************* Verify if the member node is offline **************")
        response = ib_NIOS.wapi_request('GET', object_type='member')
        response = json.loads(response)
        print_and_log(response)
        ref_member = response[1]['_ref']
        response1 = ib_NIOS.wapi_request('GET', object_type=ref_member, params='?_return_fields=node_info')
        response1 = json.loads(response1)
        print_and_log(response1)
        member_status = response1['node_info'][0]['service_status'][0]['description']
        print_and_log(member_status)
        if member_status == "Offline":
            print_and_log("Member node status is "+member_status)
            assert True
        else:
            print_and_log("Member node status is not offline")
            assert False
        print_and_log("*********** Test Case 102 Execution Completed ************")

    @pytest.mark.run(order=103)
    def test_103_NIOS_86896_Verify_the_error_logs_in_the_Infoblox_log_when_rebuild_request_is_sent_for_the_offline_node(self):
        print_and_log("************* Verify the error logs in the Infoblox log when rebuild request is sent for the offline node *************")
        print_and_log("******** Rebuild Services **********")
        log("start", "/infoblox/var/infoblox.log", config.grid_vip)
        request_restart = ib_NIOS.wapi_request('POST', object_type="dtc?_function=generate_ea_topology_db")
        print_and_log(request_restart)
        if request_restart == '{}':
            print_and_log("Success: Rebuild Service")
            assert True
        else:
            print_and_log("Failure: Rebuild Service")
            assert False
        sleep(60)
        LookFor1 = "'util_import_maxmind_db_file(): Not connected'"
        LookFor2 = "'initiate_maxmind_db_replication(): Unable to replicate MaxMind DB to a physical node. Node id:'"
        try:
            logs = logv(LookFor1, "/infoblox/var/infoblox.log", config.grid_vip)
            logs = logv(LookFor2, "/infoblox/var/infoblox.log", config.grid_vip)
        except Exception as e:
            print_and_log(e)
            print_and_log(" Error message is not seen in the logs ")
            assert True
            log("stop", "/infoblox/var/infoblox.log", config.grid_vip)
        else:
            print_and_log(" Error message is seen in the logs ")
            assert False
            log("stop", "/infoblox/var/infoblox.log", config.grid_vip)
        print_and_log("*********** Test Case 103 Execution Completed ************")



    @pytest.mark.run(order=104)
    def test_104_NIOS_86896_Connect_Grid_member_to_Grid_Master(self):
        print_and_log("************* Connect Grid member to Grid Master ***************")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@' + config.grid1_member1_vip)
            child.logfile = sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline("set vpn_comm unblock")
            child.expect('successfully.')
            output = child.before
            print_and_log(output)
            child.close()
        except Exception as e:
            child.close()
            print("Error while executing the CLI command")
            print(e)
            assert False
        sleep(60)
        print_and_log("*********** Test Case 101 Execution Completed ************")



    @pytest.mark.run(order=105)
    def test_105_NIOS_86896_Verify_if_the_member_node_is_online(self):
        print_and_log("************* Verify if the member node is online **************")
        response = ib_NIOS.wapi_request('GET', object_type='member')
        response = json.loads(response)
        print_and_log(response)
        ref_member = response[1]['_ref']
        response1 = ib_NIOS.wapi_request('GET', object_type=ref_member, params='?_return_fields=node_info')
        response1 = json.loads(response1)
        print_and_log(response1)
        member_status = response1['node_info'][0]['service_status'][0]['description']
        print_and_log(member_status)
        if member_status == "Running":
            print_and_log("Member node status is " + member_status)
            assert True
        else:
            print_and_log("Member node status is offline")
            assert False
        sleep(60)
        print_and_log("*********** Test Case 105 Execution Completed ************")



    @pytest.mark.run(order=106)
    def test_106_NIOS_87124_Disable_the_DTC_Server_With_Disable_untill_Manual_enable(self):
        print_and_log("*************** Disable the DTC Server With Disable untill Manual enable ****************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name=server1')
        response = json.loads(response)
        print_and_log(response)
        ref_server = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10, "disable_on": [config.grid1_master_fqdn], "disable_timeframe": "UNTIL_MANUAL_ENABLING", "dtc_object": ref_server, "specific_time_disable": 60}
        output = dtc_object_failback_disable_options(data)
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC Server object disabled successfully")
            assert True
        else:
            print_and_log("DTC Server object is not Disabled")
            assert False
        sleep(10)
        print_and_log("************* Test Case 106 Execution Completed ***************")



    @pytest.mark.run(order=107)
    def test_107_NIOS_87124_Check_the_status_of_Server1_and_validate_if_the_status_is_Requires_Manual_Enabling(self):
        print_and_log("************* Check the status of Server1 and validate if the status is Requires Manual Enabling **************")
        out = check_the_DTC_objects_state('dtc:server', "server1")
        print_and_log(out)
        if out == 'WHITE':
            print_and_log("DTC server status is " + status)
            assert True
        else:
            print_and_log("DTC server status is not None")
            assert False
        print_and_log("************* Test Case 107 Execution Completed ***************")



    @pytest.mark.run(order=108)
    def test_108_NIOS_87124_Disable_the_DTC_Server_using_Checkbox_option(self):
        print_and_log("*********** Disable the DTC Server using Checkbox option *************")
        out = disable_the_DTC_objects_using_checkbox('dtc:server', "server1", True)
        print_and_log(out)
        assert re.search(r'dtc:server', out)
        restart_the_grid_Services()
        print_and_log("************* Test Case 108 Execution Completed ***************")



    @pytest.mark.run(order=109)
    def test_109_NIOS_87124_Check_the_status_of_Server1_and_validate_if_the_status_is_NONE(self):
        print_and_log("************* Check the status of Server1 and validate if the status is NONE **************")
        out = check_the_DTC_objects_state('dtc:server', "server1")
        print_and_log(out)
        if out == 'NONE':
            print_and_log("DTC server status is "+status)
            assert True
        else:
            print_and_log("DTC server status is not None")
            assert False
        print_and_log("************* Test Case 109 Execution Completed ***************")

    @pytest.mark.run(order=110)
    def test_110_NIOS_87124_Enable_the_DTC_Server_using_Checkbox_option(self):
        print_and_log("*********** Enable the DTC Server using Checkbox option *************")
        out = disable_the_DTC_objects_using_checkbox('dtc:server', "server1", False)
        print_and_log(out)
        assert re.search(r'dtc:server', out)
        restart_the_grid_Services()
        print_and_log("************* Test Case 110 Execution Completed ***************")



    @pytest.mark.run(order=111)
    def test_111_NIOS_87124_Check_the_status_of_Server1_and_validate_if_the_status_is_Requires_Manual_Enabling(self):
        print_and_log("************* Check the status of Server1 and validate if the status is Requires Manual Enabling **************")
        out = check_the_DTC_objects_state('dtc:server', "server1")
        print_and_log(out)
        if out == 'WHITE':
            print_and_log("DTC server status is " + status)
            assert True
        else:
            print_and_log("DTC server status is not None")
            assert False
        print_and_log("************* Test Case 111 Execution Completed ***************")


    @pytest.mark.run(order=112)
    def test_112_NIOS_87124_Enable_the_Server_1_with_Manual_Enable_option(self):
        print_and_log("*********** Enable the server1 With Manual Enable option *************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name=server1')
        response = json.loads(response)
        ref_server = response[0]['_ref']
        data = {"enable_on": [config.grid1_master_fqdn], "dtc_object": ref_server}
        output = dtc_object_failback_enable_options(data)
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC Server 1 object Enabled successfully")
            assert True
        else:
            print_and_log("DTC Server 1 object is not enabled")
            assert False
        print_and_log("*********** Test Case 112 Execution Completed *************")


    @pytest.mark.run(order=113)
    def test_113_NIOS_87124_Disable_the_DTC_Server_With_Disable_untill_DNS_Restart(self):
        print_and_log("*************** Disable the DTC Server With Disable untill DNS Restart ****************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name=server1')
        response = json.loads(response)
        print_and_log(response)
        ref_server = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10,
                "disable_on": [config.grid1_master_fqdn], "disable_timeframe": "UNTIL_DNS_RESTART",
                "dtc_object": ref_server, "specific_time_disable": 60}
        output = dtc_object_failback_disable_options(data)
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC Server object disabled successfully")
            assert True
        else:
            print_and_log("DTC Server object is not Disabled")
            assert False
        print_and_log("************* Test Case 113 Execution Completed ***************")

    @pytest.mark.run(order=114)
    def test_114_NIOS_87124_Check_the_status_of_Server1_and_validate_if_the_status_is_Disable_UNTIL_DNS_RESTART(self):
        print_and_log("************* Check the status of Server1 and validate if the status is Disable UNTIL DNS RESTART **************")
        out = check_the_DTC_objects_state('dtc:server', "server1")
        print_and_log(out)
        if out == 'DARKGRAY':
            print_and_log("DTC server status is " + status)
            assert True
        else:
            print_and_log("DTC server status is not None")
            assert False
        print_and_log("************* Test Case 114 Execution Completed ***************")


    @pytest.mark.run(order=115)
    def test_115_NIOS_87124_Disable_the_DTC_Server_using_Checkbox_option(self):
        print_and_log("*********** Disable the DTC Server using Checkbox option *************")
        out = disable_the_DTC_objects_using_checkbox('dtc:server', "server1", True)
        print_and_log(out)
        assert re.search(r'dtc:server', out)
        restart_the_grid_Services()
        print_and_log("************* Test Case 115 Execution Completed ***************")


    @pytest.mark.run(order=116)
    def test_116_NIOS_87124_Check_the_status_of_Server1_and_validate_if_the_status_is_NONE(self):
        print_and_log("************* Check the status of Server1 and validate if the status is NONE **************")
        out = check_the_DTC_objects_state('dtc:server', "server1")
        print_and_log(out)
        if out == 'NONE':
            print_and_log("DTC server status is " + status)
            assert True
        else:
            print_and_log("DTC server status is not None")
            assert False
        print_and_log("************* Test Case 116 Execution Completed ***************")

    @pytest.mark.run(order=117)
    def test_117_NIOS_87124_Enable_the_DTC_Server_using_Checkbox_option(self):
        print_and_log("*********** Enable the DTC Server using Checkbox option *************")
        out = disable_the_DTC_objects_using_checkbox('dtc:server', "server1", False)
        print_and_log(out)
        assert re.search(r'dtc:server', out)
        restart_the_grid_Services()
        print_and_log("************* Test Case 117 Execution Completed ***************")

    @pytest.mark.run(order=118)
    def test_118_NIOS_87124_Check_the_status_of_Server1_and_validate_if_the_status_is_Running(self):
        print_and_log("************* Check the status of Server1 and validate if the status is Running **************")
        out = check_the_DTC_objects_state('dtc:server', "server1")
        print_and_log(out)
        if out == 'GREEN':
            print_and_log("DTC server status is " + status)
            assert True
        else:
            print_and_log("DTC server status is not None")
            assert False
        print_and_log("************* Test Case 118 Execution Completed ***************")


    @pytest.mark.run(order=119)
    def test_119_NIOS_87124_Disable_the_DTC_Server_With_Disable_untill_Specified_time(self):
        print_and_log("*************** Disable the DTC Server With Disable untill Specified time ****************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name=server1')
        response = json.loads(response)
        print_and_log(response)
        ref_server = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10,
                "disable_on": [config.grid1_master_fqdn], "disable_timeframe": "FOR_SPECIFIED_TIME",
                "dtc_object": ref_server, "specific_time_disable": 300}
        output = dtc_object_failback_disable_options(data)
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC Server object disabled successfully")
            assert True
        else:
            print_and_log("DTC Server object is not Disabled")
            assert False
        print_and_log("************* Test Case 119 Execution Completed ***************")



    @pytest.mark.run(order=120)
    def test_120_NIOS_87124_Check_the_status_of_Server1_and_validate_if_the_status_is_Disable_untill_Specified_time(self):
        print_and_log("************* Check the status of Server1 and validate if the status is Disable untill Specified time **************")
        out = check_the_DTC_objects_state('dtc:server', "server1")
        print_and_log(out)
        if out == 'DARKGRAY':
            print_and_log("DTC server status is " + status)
            assert True
        else:
            print_and_log("DTC server status is not None")
            assert False
        print_and_log("************* Test Case 120 Execution Completed ***************")



    @pytest.mark.run(order=121)
    def test_121_NIOS_87124_Disable_the_DTC_Server_using_Checkbox_option(self):
        print_and_log("*********** Disable the DTC Server using Checkbox option *************")
        out = disable_the_DTC_objects_using_checkbox('dtc:server', "server1", True)
        print_and_log(out)
        assert re.search(r'dtc:server', out)
        restart_the_grid_Services()
        print_and_log("************* Test Case 121 Execution Completed ***************")



    @pytest.mark.run(order=122)
    def test_122_NIOS_87124_Check_the_status_of_Server1_and_validate_if_the_status_is_NONE(self):
        print_and_log("************* Check the status of Server1 and validate if the status is NONE **************")
        out = check_the_DTC_objects_state('dtc:server', "server1")
        print_and_log(out)
        if out == 'NONE':
            print_and_log("DTC server status is " + status)
            assert True
        else:
            print_and_log("DTC server status is not None")
            assert False
        print_and_log("************* Test Case 122 Execution Completed ***************")


    @pytest.mark.run(order=123)
    def test_123_NIOS_87124_Enable_the_DTC_Server_using_Checkbox_option(self):
        print_and_log("*********** Enable the DTC Server using Checkbox option *************")
        out = disable_the_DTC_objects_using_checkbox('dtc:server', "server1", False)
        print_and_log(out)
        assert re.search(r'dtc:server', out)
        restart_the_grid_Services()
        print_and_log("************* Test Case 123 Execution Completed ***************")

    @pytest.mark.run(order=124)
    def test_124_NIOS_87124_Verify_if_DTC_Server_is_enabled_after_300_seconds(self):
        print_and_log("*********** Verify if DTC Server is enabled after 300 seconds *************")
        sleep(300)
        response = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name=server1')
        response = json.loads(response)
        ref_server = response[0]['_ref']
        data = {"dtc_object": ref_server}
        output = dtc_object_failback_status(data)
        print_and_log(output)
        if config.grid1_master_fqdn in output:
            print_and_log("DTC Server object is enabled")
            assert True
        else:
            print_and_log("DTC Server object is not enabled")
            assert False
        print_and_log("*********** Test Case 124 Execution Completed *************")


    #DTCPool
    @pytest.mark.run(order=125)
    def test_125_NIOS_87124_Disable_the_DTC_Pool1_With_Disable_untill_Manual_enable(self):
        print_and_log("*************** Disable the DTC Server With Disable untill Manual enable ****************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10,
                "disable_on": [config.grid1_master_fqdn], "disable_timeframe": "UNTIL_MANUAL_ENABLING",
                "dtc_object": ref_pool, "specific_time_disable": 60}
        output = dtc_object_failback_disable_options(data)
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC Server object disabled successfully")
            assert True
        else:
            print_and_log("DTC Server object is not Disabled")
            assert False
        print_and_log("************* Test Case 125 Execution Completed ***************")

    @pytest.mark.run(order=126)
    def test_126_NIOS_87124_Check_the_status_of_Pool1_and_validate_if_the_status_is_Requires_Manual_Enabling(self):
        print_and_log("************* Check the status of Pool1 and validate if the status is Requires Manual Enabling **************")
        out = check_the_DTC_objects_state('dtc:pool', "pool1")
        print_and_log(out)
        if out == 'WHITE':
            print_and_log("DTC Pool status is " + status)
            assert True
        else:
            print_and_log("DTC Pool status is not None")
            assert False
        print_and_log("************* Test Case 126 Execution Completed ***************")

    @pytest.mark.run(order=127)
    def test_127_NIOS_87124_Disable_the_DTC_Pool_using_Checkbox_option(self):
        print_and_log("*********** Disable the DTC Pool using Checkbox option *************")
        out = disable_the_DTC_objects_using_checkbox('dtc:pool', "Pool1", True)
        print_and_log(out)
        assert re.search(r'dtc:pool', out)
        restart_the_grid_Services()
        print_and_log("************* Test Case 127 Execution Completed ***************")

    @pytest.mark.run(order=128)
    def test_128_NIOS_87124_Check_the_status_of_Server1_and_validate_if_the_status_is_NONE(self):
        print_and_log("************* Check the status of Pool1 and validate if the status is NONE **************")
        out = check_the_DTC_objects_state('dtc:pool', "pool1")
        print_and_log(out)
        if out == 'NONE':
            print_and_log("DTC server status is " + status)
            assert True
        else:
            print_and_log("DTC server status is not None")
            assert False
        print_and_log("************* Test Case 128 Execution Completed ***************")

    @pytest.mark.run(order=129)
    def test_129_NIOS_87124_Enable_the_DTC_Pool1_using_Checkbox_option(self):
        print_and_log("*********** Enable the DTC Pool using Checkbox option *************")
        out = disable_the_DTC_objects_using_checkbox('dtc:pool', "pool1", False)
        print_and_log(out)
        assert re.search(r'dtc:pool', out)
        restart_the_grid_Services()
        print_and_log("************* Test Case 129 Execution Completed ***************")

    @pytest.mark.run(order=130)
    def test_130_NIOS_87124_Check_the_status_of_Pool1_and_validate_if_the_status_is_Requires_Manual_Enabling(self):
        print_and_log("************* Check the status of Pool1 and validate if the status is Requires Manual Enabling **************")
        out = check_the_DTC_objects_state('dtc:pool', "pool1")
        print_and_log(out)
        if out == 'WHITE':
            print_and_log("DTC pool status is " + status)
            assert True
        else:
            print_and_log("DTC pool status is not None")
            assert False
        print_and_log("************* Test Case 130 Execution Completed ***************")

    @pytest.mark.run(order=131)
    def test_131_NIOS_87124_Enable_the_Pool_1_with_Manual_Enable_option(self):
        print_and_log("*********** Enable the pool1 With Manual Enable option *************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response = json.loads(response)
        ref_server = response[0]['_ref']
        data = {"enable_on": [config.grid1_master_fqdn], "dtc_object": ref_server}
        output = dtc_object_failback_enable_options(data)
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC pool 1 object Enabled successfully")
            assert True
        else:
            print_and_log("DTC pool 1 object is not enabled")
            assert False
        print_and_log("*********** Test Case 131 Execution Completed *************")

    @pytest.mark.run(order=132)
    def test_132_NIOS_87124_Disable_the_DTC_Server_With_Disable_untill_DNS_Restart(self):
        print_and_log("*************** Disable the DTC pool With Disable untill DNS Restart ****************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10,
                "disable_on": [config.grid1_master_fqdn], "disable_timeframe": "UNTIL_DNS_RESTART",
                "dtc_object": ref_pool, "specific_time_disable": 60}
        output = dtc_object_failback_disable_options(data)
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC Pool object disabled successfully")
            assert True
        else:
            print_and_log("DTC Pool object is not Disabled")
            assert False
        print_and_log("************* Test Case 132 Execution Completed ***************")

    @pytest.mark.run(order=133)
    def test_133_NIOS_87124_Check_the_status_of_Pool1_and_validate_if_the_status_is_Disable_UNTIL_DNS_RESTART(self):
        print_and_log("************* Check the status of Pool1 and validate if the status is Disable UNTIL DNS RESTART **************")
        out = check_the_DTC_objects_state('dtc:pool', "pool1")
        print_and_log(out)
        if out == 'DARKGRAY':
            print_and_log("DTC pool status is " + status)
            assert True
        else:
            print_and_log("DTC pool status is not None")
            assert False
        print_and_log("************* Test Case 133 Execution Completed ***************")

    @pytest.mark.run(order=134)
    def test_134_NIOS_87124_Disable_the_DTC_Pool_using_Checkbox_option(self):
        print_and_log("*********** Disable the DTC Pool using Checkbox option *************")
        out = disable_the_DTC_objects_using_checkbox('dtc:pool', "pool1", True)
        print_and_log(out)
        assert re.search(r'dtc:pool', out)
        restart_the_grid_Services()
        print_and_log("************* Test Case 134 Execution Completed ***************")

    @pytest.mark.run(order=135)
    def test_135_NIOS_87124_Check_the_status_of_Pool1_and_validate_if_the_status_is_NONE(self):
        print_and_log("************* Check the status of Pool1 and validate if the status is NONE **************")
        out = check_the_DTC_objects_state('dtc:pool', "pool1")
        print_and_log(out)
        if out == 'NONE':
            print_and_log("DTC pool status is " + status)
            assert True
        else:
            print_and_log("DTC pool status is not None")
            assert False
        print_and_log("************* Test Case 135 Execution Completed ***************")

    @pytest.mark.run(order=136)
    def test_136_NIOS_87124_Enable_the_DTC_Pool_using_Checkbox_option(self):
        print_and_log("*********** Enable the DTC Pool using Checkbox option *************")
        out = disable_the_DTC_objects_using_checkbox('dtc:pool', "server1", False)
        print_and_log(out)
        assert re.search(r'dtc:pool', out)
        restart_the_grid_Services()
        print_and_log("************* Test Case 136 Execution Completed ***************")

    @pytest.mark.run(order=137)
    def test_137_NIOS_87124_Check_the_status_of_Pool1_and_validate_if_the_status_is_Running(self):
        print_and_log("************* Check the status of Pool1 and validate if the status is Running **************")
        out = check_the_DTC_objects_state('dtc:pool', "pool1")
        print_and_log(out)
        if out == 'GREEN':
            print_and_log("DTC pool status is " + status)
            assert True
        else:
            print_and_log("DTC pool status is not None")
            assert False
        print_and_log("************* Test Case 137 Execution Completed ***************")

    @pytest.mark.run(order=138)
    def test_138_NIOS_87124_Disable_the_DTC_Pool1_With_Disable_untill_Specified_time(self):
        print_and_log("*************** Disable the DTC Pool1 With Disable untill Specified time ****************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10,
                "disable_on": [config.grid1_master_fqdn], "disable_timeframe": "FOR_SPECIFIED_TIME",
                "dtc_object": ref_pool, "specific_time_disable": 300}
        output = dtc_object_failback_disable_options(data)
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC Pool object disabled successfully")
            assert True
        else:
            print_and_log("DTC Pool object is not Disabled")
            assert False
        print_and_log("************* Test Case 138 Execution Completed ***************")

    @pytest.mark.run(order=139)
    def test_139_NIOS_87124_Check_the_status_of_Pool1_and_validate_if_the_status_is_Disable_untill_Specified_time(self):
        print_and_log("************* Check the status of Pool1 and validate if the status is Disable untill Specified time **************")
        out = check_the_DTC_objects_state('dtc:pool', "pool1")
        print_and_log(out)
        if out == 'DARKGRAY':
            print_and_log("DTC pool status is " + status)
            assert True
        else:
            print_and_log("DTC pool status is not None")
            assert False
        print_and_log("************* Test Case 139 Execution Completed ***************")

    @pytest.mark.run(order=140)
    def test_140_NIOS_87124_Disable_the_DTC_Pool_using_Checkbox_option(self):
        print_and_log("*********** Disable the DTC Pool using Checkbox option *************")
        out = disable_the_DTC_objects_using_checkbox('dtc:pool', "pool1", True)
        print_and_log(out)
        assert re.search(r'dtc:pool', out)
        restart_the_grid_Services()
        print_and_log("************* Test Case 140 Execution Completed ***************")

    @pytest.mark.run(order=141)
    def test_141_NIOS_87124_Check_the_status_of_Pool1_and_validate_if_the_status_is_NONE(self):
        print_and_log("************* Check the status of Pool1 and validate if the status is NONE **************")
        out = check_the_DTC_objects_state('dtc:pool', "pool1")
        print_and_log(out)
        if out == 'NONE':
            print_and_log("DTC server status is " + status)
            assert True
        else:
            print_and_log("DTC server status is not None")
            assert False
        print_and_log("************* Test Case 141 Execution Completed ***************")

    @pytest.mark.run(order=142)
    def test_142_NIOS_87124_Enable_the_DTC_Pool_using_Checkbox_option(self):
        print_and_log("*********** Enable the DTC Pool using Checkbox option *************")
        out = disable_the_DTC_objects_using_checkbox('dtc:pool', "pool1", False)
        print_and_log(out)
        assert re.search(r'dtc:pool', out)
        restart_the_grid_Services()
        print_and_log("************* Test Case 142 Execution Completed ***************")

    @pytest.mark.run(order=143)
    def test_143_NIOS_87124_Verify_if_DTC_Pool_is_enabled_after_300_seconds(self):
        print_and_log("*********** Verify if DTC Pool is enabled after 300 seconds *************")
        sleep(300)
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response = json.loads(response)
        ref_pool = response[0]['_ref']
        data = {"dtc_object": ref_pool}
        output = dtc_object_failback_status(data)
        print_and_log(output)
        if config.grid1_master_fqdn in output:
            print_and_log("DTC Pool object is enabled")
            assert True
        else:
            print_and_log("DTC Pool object is not enabled")
            assert False
        print_and_log("*********** Test Case 143 Execution Completed *************")

    # DTC LBDN
    @pytest.mark.run(order=144)
    def test_144_NIOS_87124_Disable_the_DTC_LBDN_With_Disable_untill_Manual_enable(self):
        print_and_log("*************** Disable the DTC LBDN With Disable untill Manual enable ****************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        print_and_log(response)
        ref_lbdn = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10,
                "disable_on": [config.grid1_master_fqdn], "disable_timeframe": "UNTIL_MANUAL_ENABLING",
                "dtc_object": ref_lbdn, "specific_time_disable": 60}
        output = dtc_object_failback_disable_options(data)
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC LBDN object disabled successfully")
            assert True
        else:
            print_and_log("DTC LBDN object is not Disabled")
            assert False
        print_and_log("************* Test Case 144 Execution Completed ***************")

    @pytest.mark.run(order=145)
    def test_145_NIOS_87124_Check_the_status_of_LBDN_and_validate_if_the_status_is_Requires_Manual_Enabling(self):
        print_and_log("************* Check the status of LBDN and validate if the status is Requires Manual Enabling **************")
        out = check_the_DTC_objects_state('dtc:lbdn', "DTC_LBDN_1")
        print_and_log(out)
        if out == 'WHITE':
            print_and_log("DTC LBDN status is " + status)
            assert True
        else:
            print_and_log("DTC LBDN status is not None")
            assert False
        print_and_log("************* Test Case 145 Execution Completed ***************")

    @pytest.mark.run(order=146)
    def test_146_NIOS_87124_Disable_the_DTC_LBDN_using_Checkbox_option(self):
        print_and_log("*********** Disable the DTC LBDN using Checkbox option *************")
        out = disable_the_DTC_objects_using_checkbox('dtc:lbdn', "server1", True)
        print_and_log(out)
        assert re.search(r'dtc:lbdn', out)
        restart_the_grid_Services()
        print_and_log("************* Test Case 146 Execution Completed ***************")

    @pytest.mark.run(order=147)
    def test_147_NIOS_87124_Check_the_status_of_LBDN_and_validate_if_the_status_is_NONE(self):
        print_and_log("************* Check the status of LBDN and validate if the status is NONE **************")
        out = check_the_DTC_objects_state('dtc:lbdn', "DTC_LBDN_1")
        print_and_log(out)
        if out == 'NONE':
            print_and_log("DTC LBDN status is " + status)
            assert True
        else:
            print_and_log("DTC LBDN status is not None")
            assert False
        print_and_log("************* Test Case 147 Execution Completed ***************")

    @pytest.mark.run(order=148)
    def test_148_NIOS_87124_Enable_the_DTC_LBDN_using_Checkbox_option(self):
        print_and_log("*********** Enable the DTC LBDN using Checkbox option *************")
        out = disable_the_DTC_objects_using_checkbox('dtc:lbdn', "DTC_LBDN_1", False)
        print_and_log(out)
        assert re.search(r'dtc:lbdn', out)
        restart_the_grid_Services()
        print_and_log("************* Test Case 148 Execution Completed ***************")

    @pytest.mark.run(order=149)
    def test_149_NIOS_87124_Check_the_status_of_LBDN_and_validate_if_the_status_is_Requires_Manual_Enabling(self):
        print_and_log("************* Check the status of LBDN and validate if the status is Requires Manual Enabling **************")
        out = check_the_DTC_objects_state('dtc:lbdn', "DTC_LBDN_1")
        print_and_log(out)
        if out == 'WHITE':
            print_and_log("DTC LBDN status is " + status)
            assert True
        else:
            print_and_log("DTC LBDN status is not None")
            assert False
        print_and_log("************* Test Case 149 Execution Completed ***************")

    @pytest.mark.run(order=150)
    def test_150_NIOS_87124_Enable_the_LBDN_with_Manual_Enable_option(self):
        print_and_log("*********** Enable the LBDN With Manual Enable option *************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        ref_lbdn = response[0]['_ref']
        data = {"enable_on": [config.grid1_master_fqdn], "dtc_object": ref_lbdn}
        output = dtc_object_failback_enable_options(data)
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC LBDN object Enabled successfully")
            assert True
        else:
            print_and_log("DTC LBDN object is not enabled")
            assert False
        print_and_log("*********** Test Case 150 Execution Completed *************")

    @pytest.mark.run(order=151)
    def test_151_NIOS_87124_Disable_the_DTC_LBDN_With_Disable_untill_DNS_Restart(self):
        print_and_log("*************** Disable the DTC LBDN With Disable untill DNS Restart ****************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        print_and_log(response)
        ref_lbdn = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10,
                "disable_on": [config.grid1_master_fqdn], "disable_timeframe": "UNTIL_DNS_RESTART",
                "dtc_object": ref_lbdn, "specific_time_disable": 60}
        output = dtc_object_failback_disable_options(data)
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC LBDN object disabled successfully")
            assert True
        else:
            print_and_log("DTC LBDN object is not Disabled")
            assert False
        print_and_log("************* Test Case 151 Execution Completed ***************")

    @pytest.mark.run(order=152)
    def test_152_NIOS_87124_Check_the_status_of_LBDN_and_validate_if_the_status_is_Disable_UNTIL_DNS_RESTART(self):
        print_and_log("************* Check the status of LBDN and validate if the status is Disable UNTIL DNS RESTART **************")
        out = check_the_DTC_objects_state('dtc:lbdn', "DTC_LBDN_1")
        print_and_log(out)
        if out == 'DARKGRAY':
            print_and_log("DTC LBDN status is " + status)
            assert True
        else:
            print_and_log("DTC LBDN status is not None")
            assert False
        print_and_log("************* Test Case 152 Execution Completed ***************")

    @pytest.mark.run(order=153)
    def test_153_NIOS_87124_Disable_the_DTC_LBDN_using_Checkbox_option(self):
        print_and_log("*********** Disable the DTC LBDN using Checkbox option *************")
        out = disable_the_DTC_objects_using_checkbox('dtc:lbdn', "DTC_LBDN_1", True)
        print_and_log(out)
        assert re.search(r'dtc:lbdn', out)
        restart_the_grid_Services()
        print_and_log("************* Test Case 153 Execution Completed ***************")

    @pytest.mark.run(order=154)
    def test_154_NIOS_87124_Check_the_status_of_LBDN_and_validate_if_the_status_is_NONE(self):
        print_and_log("************* Check the status of LBDN and validate if the status is NONE **************")
        out = check_the_DTC_objects_state('dtc:lbdn', "DTC_LBDN_1")
        print_and_log(out)
        if out == 'NONE':
            print_and_log("DTC LBDN status is " + status)
            assert True
        else:
            print_and_log("DTC LBDN status is not None")
            assert False
        print_and_log("************* Test Case 154 Execution Completed ***************")

    @pytest.mark.run(order=155)
    def test_155_NIOS_87124_Enable_the_DTC_LBDN_using_Checkbox_option(self):
        print_and_log("*********** Enable the DTC LBDN using Checkbox option *************")
        out = disable_the_DTC_objects_using_checkbox('dtc:lbdn', "DTC_LBDN_1", False)
        print_and_log(out)
        assert re.search(r'dtc:lbdn', out)
        restart_the_grid_Services()
        print_and_log("************* Test Case 155 Execution Completed ***************")

    @pytest.mark.run(order=156)
    def test_156_NIOS_87124_Check_the_status_of_LBDN_and_validate_if_the_status_is_Running(self):
        print_and_log("************* Check the status of LBDN and validate if the status is Running **************")
        out = check_the_DTC_objects_state('dtc:lbdn', "DTC_LBDN_1")
        print_and_log(out)
        if out == 'GREEN':
            print_and_log("DTC LBDN status is " + status)
            assert True
        else:
            print_and_log("DTC LBDN status is not None")
            assert False
        print_and_log("************* Test Case 156 Execution Completed ***************")

    @pytest.mark.run(order=157)
    def test_157_NIOS_87124_Disable_the_DTC_LBDN_With_Disable_untill_Specified_time(self):
        print_and_log("*************** Disable the DTC LBDN With Disable untill Specified time ****************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        print_and_log(response)
        ref_lbdn = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10,
                "disable_on": [config.grid1_master_fqdn], "disable_timeframe": "FOR_SPECIFIED_TIME",
                "dtc_object": ref_lbdn, "specific_time_disable": 300}
        output = dtc_object_failback_disable_options(data)
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC LBDN object disabled successfully")
            assert True
        else:
            print_and_log("DTC LBDN object is not Disabled")
            assert False
        print_and_log("************* Test Case 157 Execution Completed ***************")

    @pytest.mark.run(order=158)
    def test_158_NIOS_87124_Check_the_status_of_LBDN_and_validate_if_the_status_is_Disable_untill_Specified_time(self):
        print_and_log("************* Check the status of LBDN and validate if the status is Disable untill Specified time **************")
        out = check_the_DTC_objects_state('dtc:lbdn', "DTC_LBDN_1")
        print_and_log(out)
        if out == 'DARKGRAY':
            print_and_log("DTC LBDN status is " + status)
            assert True
        else:
            print_and_log("DTC LBDN status is not None")
            assert False
        print_and_log("************* Test Case 158 Execution Completed ***************")

    @pytest.mark.run(order=159)
    def test_159_NIOS_87124_Disable_the_DTC_LBDN_using_Checkbox_option(self):
        print_and_log("*********** Disable the DTC LBDN using Checkbox option *************")
        out = disable_the_DTC_objects_using_checkbox('dtc:lbdn', "DTC_LBDN_1", True)
        print_and_log(out)
        assert re.search(r'dtc:lbdn', out)
        restart_the_grid_Services()
        print_and_log("************* Test Case 159 Execution Completed ***************")

    @pytest.mark.run(order=160)
    def test_160_NIOS_87124_Check_the_status_of_LBDN_and_validate_if_the_status_is_NONE(self):
        print_and_log("************* Check the status of LBDN and validate if the status is NONE **************")
        out = check_the_DTC_objects_state('dtc:lbdn', "DTC_LBDN_1")
        print_and_log(out)
        if out == 'NONE':
            print_and_log("DTC LBDN status is " + status)
            assert True
        else:
            print_and_log("DTC LBDN status is not None")
            assert False
        print_and_log("************* Test Case 160 Execution Completed ***************")

    @pytest.mark.run(order=161)
    def test_161_NIOS_87124_Enable_the_DTC_LBDN_using_Checkbox_option(self):
        print_and_log("*********** Enable the DTC LBDN using Checkbox option *************")
        out = disable_the_DTC_objects_using_checkbox('dtc:lbdn', "DTC_LBDN_1", False)
        print_and_log(out)
        assert re.search(r'dtc:lbdn', out)
        restart_the_grid_Services()
        print_and_log("************* Test Case 161 Execution Completed ***************")



    @pytest.mark.run(order=162)
    def test_162_NIOS_87124_Verify_if_DTC_LBDN_is_enabled_after_300_seconds(self):
        print_and_log("*********** Verify if DTC LBDN is enabled after 300 seconds *************")
        sleep(300)
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        ref_lbdn = response[0]['_ref']
        data = {"dtc_object": ref_lbdn}
        output = dtc_object_failback_status(data)
        print_and_log(output)
        if config.grid1_master_fqdn in output:
            print_and_log("DTC LBDN object is enabled")
            assert True
        else:
            print_and_log("DTC LBDN object is not enabled")
            assert False
        print_and_log("*********** Test Case 162 Execution Completed *************")

    @pytest.mark.run(order=163)
    def test_163_NIOS_86471_Disconnect_Grid_member_from_Grid_Master(self):
        print_and_log("************* Disconnect Grid member from Grid Master ***************")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@' + config.grid1_member1_vip)
            child.logfile = sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline("set vpn_comm block")
            child.expect('successfully.')
            output = child.before
            print_and_log(output)
            child.close()
        except Exception as e:
            child.close()
            print("Error while executing the CLI command")
            print(e)
            assert False
        sleep(60)
        print_and_log("*********** Test Case 163 Execution Completed ************")

    @pytest.mark.run(order=164)
    def test_164_NIOS_86896_Verify_if_the_member_node_is_offline(self):
        print_and_log("************* Verify if the member node is offline **************")
        response = ib_NIOS.wapi_request('GET', object_type='member')
        response = json.loads(response)
        print_and_log(response)
        ref_member = response[1]['_ref']
        response1 = ib_NIOS.wapi_request('GET', object_type=ref_member, params='?_return_fields=node_info')
        response1 = json.loads(response1)
        print_and_log(response1)
        member_status = response1['node_info'][0]['service_status'][0]['description']
        print_and_log(member_status)
        if member_status == "Offline":
            print_and_log("Member node status is " + member_status)
            assert True
        else:
            print_and_log("Member node status is not offline")
            assert False
        print_and_log("*********** Test Case 164 Execution Completed ************")

    @pytest.mark.run(order=165)
    def test_165_NIOS_87124_Disable_the_DTC_Server_With_Disable_untill_Manual_enable_on_offline_member(self):
        print_and_log("*************** Disable the DTC Server With Disable untill Manual enable on offline member ****************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name=server1')
        response = json.loads(response)
        print_and_log(response)
        ref_server = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10, "disable_on": [config.grid1_member1_fqdn], "disable_timeframe": "UNTIL_MANUAL_ENABLING", "dtc_object": ref_server, "specific_time_disable": 60}
        output = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data), params="?_function=dtc_object_disable")
        #output = json.loads(response)
        print_and_log(output)
        if type(output) == tuple:
            out = output[1]
            out = json.loads(out)
            print_and_log(out)
            error_message = out['text']
            print_and_log(error_message)
            expected_error_message = "A DTC object cannot be enabled or disabled on an offline grid member '"+ config.grid1_member1_fqdn +"'"
            if error_message in expected_error_message:
                print_and_log("Expected Error message is seen")
                assert True
            else:
                print_and_log("Expected Error message is not seen")
                assert False
        else:
            print_and_log(output)
            print_and_log(" Able to Disable the Offline DTC member")
            assert False
        print_and_log("************* Test Case 165 Execution Completed ***************")

    @pytest.mark.run(order=166)
    def test_166_NIOS_87124_Disable_the_DTC_Server_With_Disable_untill_DNS_Restart_on_offline_member(self):
        print_and_log("*************** Disable the DTC Server With Disable untill DNS Restart on offline member ****************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name=server1')
        response = json.loads(response)
        print_and_log(response)
        ref_server = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10, "disable_on": [config.grid1_member1_fqdn], "disable_timeframe": "UNTIL_DNS_RESTART", "dtc_object": ref_server, "specific_time_disable": 60}
        output = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data),
                                        params="?_function=dtc_object_disable")
        #output = json.loads(response)
        print_and_log(output)
        if type(output) == tuple:
            out = output[1]
            out = json.loads(out)
            print_and_log(out)
            error_message = out['text']
            print_and_log(error_message)
            expected_error_message = "A DTC object cannot be enabled or disabled on an offline grid member '" + config.grid1_member1_fqdn + "'"
            if error_message in expected_error_message:
                print_and_log("Expected Error message is seen")
                assert True
            else:
                print_and_log("Expected Error message is not seen")
                assert False
        else:
            print_and_log(output)
            print_and_log(" Able to Disable the Offline DTC member")
            assert False
        print_and_log("************* Test Case 166 Execution Completed ***************")

    @pytest.mark.run(order=167)
    def test_167_NIOS_87124_Disable_the_DTC_Server_With_Disable_untill_Specified_time_on_offline_member(self):
        print_and_log("*************** Disable the DTC Server With Disable untill specififed time on offline member ****************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name=server1')
        response = json.loads(response)
        print_and_log(response)
        ref_server = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10, "disable_on": [config.grid1_member1_fqdn], "disable_timeframe": "FOR_SPECIFIED_TIME", "dtc_object": ref_server, "specific_time_disable": 300}
        output = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data),
                                        params="?_function=dtc_object_disable")
        #output = json.loads(response)
        print_and_log(output)
        if type(output) == tuple:
            out = output[1]
            out = json.loads(out)
            print_and_log(out)
            error_message = out['text']
            print_and_log(error_message)
            expected_error_message = "A DTC object cannot be enabled or disabled on an offline grid member '" + config.grid1_member1_fqdn + "'"
            if error_message in expected_error_message:
                print_and_log("Expected Error message is seen")
                assert True
            else:
                print_and_log("Expected Error message is not seen")
                assert False
        else:
            print_and_log(output)
            print_and_log(" Able to Disable the Offline DTC member")
            assert False
        print_and_log("************* Test Case 167 Execution Completed ***************")

    @pytest.mark.run(order=168)
    def test_168_NIOS_87124_Connect_Grid_member_to_Grid_Master(self):
        print_and_log("************* Connect Grid member to Grid Master ***************")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@' + config.grid1_member1_vip)
            child.logfile = sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline("set vpn_comm unblock")
            child.expect('successfully.')
            output = child.before
            print_and_log(output)
            child.close()
        except Exception as e:
            child.close()
            print("Error while executing the CLI command")
            print(e)
            assert False
        sleep(60)
        print_and_log("*********** Test Case 168 Execution Completed ************")

    @pytest.mark.run(order=169)
    def test_169_NIOS_87124_Verify_if_the_member_node_is_online(self):
        print_and_log("************* Verify if the member node is online **************")
        response = ib_NIOS.wapi_request('GET', object_type='member')
        response = json.loads(response)
        print_and_log(response)
        ref_member = response[1]['_ref']
        response1 = ib_NIOS.wapi_request('GET', object_type=ref_member, params='?_return_fields=node_info')
        response1 = json.loads(response1)
        print_and_log(response1)
        member_status = response1['node_info'][0]['service_status'][0]['description']
        print_and_log(member_status)
        if member_status == "Running":
            print_and_log("Member node status is " + member_status)
            assert True
        else:
            print_and_log("Member node status is offline")
            assert False
        sleep(60)
        print_and_log("*********** Test Case 169 Execution Completed ************")

    @pytest.mark.run(order=170)
    def test_170_NIOS_85838_Add_the_pool1_and_Pool2_to_the_LBDN_Pool_members_and_configure_Source_IP_hash_as_LB_method(self):
        print_and_log("************* Add the pool1 and pool2 to the LBDN Pool members and configure Source IP hash as LB method *************")
        print_and_log("Getting ref of DTC_LBDN_1")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        ref = response[0]['_ref']
        print_and_log(ref)
        print_and_log("********** Getting the ref of pool ************")
        pool_name = ["pool1", "pool2"]
        pool_ref = []
        for i in pool_name:
            response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=' + i)
            response = json.loads(response)
            ref_pool = response[0]['_ref']
            pool_ref.append(ref_pool)
        print_and_log(pool_ref)
        print_and_log("********** Delete the pool2 in pool members ************")
        data = {"pools": [{"ratio": 1, "pool": pool_ref[0]}, {"ratio": 1, "pool": pool_ref[1]}], "lb_method": "SOURCE_IP_HASH"}
        print_and_log(data)
        response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
        print_and_log(response)
        print_and_log("Validation of lbdn creation")
        assert re.search(r'dtc:lbdn', response)
        print_and_log("******** Restart the DNS service *********")
        restart_the_grid_Services()
        print_and_log(" ************ Test Case 170 Execution Completed *************** ")

    @pytest.mark.run(order=171)
    def test_171_NIOS_85838_Validate_the_LB_method_Source_IP_hash_added_to_LBDN(self):
        print_and_log("************** Validate the LB method Source IP hash added to LBDN ***************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        print_and_log(response)
        ref_lbdn = response[0]['_ref']
        response1 = ib_NIOS.wapi_request('GET', object_type=ref_lbdn, params='?_return_fields=lb_method')
        response1 = json.loads(response1)
        print_and_log(response1)
        lb_method = response1['lb_method']
        if lb_method == "SOURCE_IP_HASH":
            print_and_log("Load balancing method " + lb_method + " is configured")
            assert True
        else:
            print_and_log("Validation for the LBDN failed")
            assert False
        print_and_log("********** Test Case 171 Execution Completed ***********")

    @pytest.mark.run(order=172)
    def test_172_NIOS_85838_Perform_the_dig_command_and_verify_the_response_is_from_dtc_Server1(self):
        print_and_log("********** Perform the dig command and verify the response on Grid master ************")
        Server_That_Responded = Perform_Dig_queires(config.grid1_master_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[0]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("********** Perform the dig command and verify the response on Grid member ************")
        Server_That_Responded = Perform_Dig_queires(config.grid1_member1_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[0]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("********* Test Case 172 Execution Completed *************")


    @pytest.mark.run(order=173)
    def test_173_NIOS_85838_Drop_the_DTC_Servers_On_DTC_members(self):
        print_and_log("************* Drop the DTC Servers On DTC members ************")
        print_and_log("Drop the Server1 on Grid Master")
        Drop_and_Accept_the_DTC_Servers_on_DTC_members(config.grid_vip, dtc_server_ips[0], "DROP")
        print_and_log("Drop the Server2 on Grid Member")
        Drop_and_Accept_the_DTC_Servers_on_DTC_members(config.grid1_member1_vip, dtc_server_ips[1], "DROP")
        sleep(30)
        print_and_log("********* Test Case 173 Execution Completed *************")



    @pytest.mark.run(order=174)
    def test_174_NIOS_85838_Enable_the_Auto_consolidated_monitors_on_pool1(self):
        print_and_log("************ Enable the Auto consolidated monitors on pool1 ************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        data = {"auto_consolidated_monitors": True}
        response1 = ib_NIOS.wapi_request('PUT', object_type=ref_pool, fields=json.dumps(data))
        print_and_log(response1)
        assert re.search(r'dtc:pool', response1)
        restart_the_grid_Services()
        print_and_log("********* Test Case 174 Execution Completed *************")



    @pytest.mark.run(order=175)
    def test_175_NIOS_85838_Validate_the_Auto_consolidated_monitors_on_pool1(self):
        print_and_log("************ Validate the Auto consolidated monitors on pool1 ************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        response1 = ib_NIOS.wapi_request('GET', object_type=ref_pool, params='?_return_fields=auto_consolidated_monitors')
        response1 = json.loads(response1)
        print_and_log(response1)
        auto_consolidated_monitors = response1['auto_consolidated_monitors']
        if auto_consolidated_monitors == True:
            print_and_log("Auto consolidated monitors are set to TRUE")
            assert True
        else:
            print_and_log("Auto consolidated monitors are set to FALSE")
            assert False
        print_and_log("********* Test Case 175 Execution Completed *************")



    @pytest.mark.run(order=176)
    def test_176_NIOS_85838_Validate_the_DTC_Health_status_of_Pool_and_LBDN_after_600_seconds(self):
        print_and_log("********** Validate the DTC Health status of Pool and LBDN after 600 seconds **********")
        sleep(600)
        print_and_log("checking status of DTC Pool")
        out = check_the_DTC_objects_state("dtc:pool", "pool1")
        print_and_log(out)
        print_and_log("checking status of DTC LBDN")
        out1 = check_the_DTC_objects_state("dtc:lbdn", "DTC_LBDN_1")
        print_and_log(out1)
        if out == "ERROR" and out1 == "WARNING":
            print_and_log("DTC Pool status is"+out+" and DTC LBDN status is"+out1)
            assert True
        else:
            print_and_log("Error while validating the DTC pool and lBDN status")
            assert False
        print_and_log("********* Test Case 176 Execution Completed *************")

    @pytest.mark.run(order=177)
    def test_177_NIOS_85838_Disable_the_Auto_consolidated_monitors_on_pool1(self):
        print_and_log("************ Disable the Auto consolidated monitors on pool1 ************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        data = {"auto_consolidated_monitors": False}
        response1 = ib_NIOS.wapi_request('PUT', object_type=ref_pool, fields=json.dumps(data))
        print_and_log(response1)
        assert re.search(r'dtc:pool', response1)
        restart_the_grid_Services()
        print_and_log("********* Test Case 177 Execution Completed *************")

    @pytest.mark.run(order=178)
    def test_178_NIOS_85838_Validate_the_Auto_consolidated_monitors_on_pool1(self):
        print_and_log("************ Validate the Auto consolidated monitors on pool1 ************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        response1 = ib_NIOS.wapi_request('GET', object_type=ref_pool,
                                         params='?_return_fields=auto_consolidated_monitors')
        response1 = json.loads(response1)
        print_and_log(response1)
        auto_consolidated_monitors = response1['auto_consolidated_monitors']
        if auto_consolidated_monitors == False:
            print_and_log("Auto consolidated monitors are set to FALSE")
            assert True
        else:
            print_and_log("Auto consolidated monitors are set to TRUE")
            assert False
        print_and_log("********* Test Case 178 Execution Completed *************")



    @pytest.mark.run(order=179)
    def test_179_NIOS_85838_Accept_the_DTC_Servers_On_DTC_members(self):
        print_and_log("************* Accept the DTC Servers On DTC members ************")
        print_and_log("Accept the Server1 on Grid Master")
        Drop_and_Accept_the_DTC_Servers_on_DTC_members(config.grid_vip, dtc_server_ips[0], "ACCEPT")
        print_and_log("Accept the Server2 on Grid Member")
        Drop_and_Accept_the_DTC_Servers_on_DTC_members(config.grid1_member1_vip, dtc_server_ips[1], "ACCEPT")
        sleep(30)
        print_and_log("********* Test Case 179 Execution Completed *************")

    @pytest.mark.run(order=180)
    def test_180_NIOS_85838_Delete_the_Zone_and_pattern_in_the_LBDN(self):
        print_and_log("************* Delete the Zone and pattern in the LBDN *************")
        print_and_log("Getting ref of DTC_LBDN_1")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        ref = response[0]['_ref']
        print_and_log(ref)
        data = {"auth_zones": [], "patterns": []}
        print_and_log(data)
        response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
        print_and_log(response)
        print_and_log("Validation of lbdn creation")
        assert re.search(r'dtc:lbdn', response)
        print_and_log("******** Restart the DNS service *********")
        restart_the_grid_Services()
        print_and_log(" ************ Test Case 180 Execution Completed *************** ")

    @pytest.mark.run(order=181)
    def test_181_NIOS_85838_Validate_if_Zone_and_pattern_is_deleted_in_the_LBDN(self):
        print_and_log("************* Validate if Zone and pattern is deleted in the LBDN *************")
        print_and_log("Getting ref of DTC_LBDN_1")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        ref = response[0]['_ref']
        print_and_log(ref)
        response1 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=auth_zones')
        print_and_log(response1)
        response1 = json.loads(response1)
        auth_zones = response1['auth_zones']
        response2 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=patterns')
        response2 = json.loads(response2)
        print_and_log(response2)
        patterns = response1['patterns']
        if auth_zones == [] and patterns == []:
            print_and_log("Auth zone and patterns are deleted in the LBDN")
            assert True
        else:
            print_and_log("Validation for the LBDN failed")
            assert False
        print_and_log(" ************ Test Case 181 Execution Completed *************** ")

    @pytest.mark.run(order=182)
    def test_182_NIOS_85813_Disable_the_DTC_Server_With_ALl_Disable_Methods_when_in_None_state(self):
        print_and_log("*************** Disable DTC Server With All Disable Methods when in None state ****************")
        disable_states = ["UNTIL_MANUAL_ENABLING", "UNTIL_DNS_RESTART", "FOR_SPECIFIED_TIME"]
        response = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name=server1')
        response = json.loads(response)
        print_and_log(response)
        ref_server = response[0]['_ref']
        for i in disable_states:
            data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10,
                "disable_on": [config.grid1_master_fqdn], "disable_timeframe": i, "dtc_object": ref_server,
                "specific_time_disable": 60}
            print_and_log(data)
            output = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data),params="?_function=dtc_object_disable")
            print_and_log(output)
            if type(output) == tuple:
                out = output[1]
                out = json.loads(out)
                print_and_log(out)
                error_message = out['text']
                print_and_log(error_message)
                expected_error_message = "The DTC object 'server1' cannot be enabled/disabled since there are no associated enabled LBDN's"
                if error_message in expected_error_message:
                    print_and_log("Expected Error message is seen")
                    assert True
                else:
                    print_and_log("Expected Error message is not seen")
                    assert False
            else:
                print_and_log(output)
                print_and_log("Able to Disable the DTC Server Object when in None state")
                assert False
        print_and_log("************* Test Case 182 Execution Completed ***************")

    @pytest.mark.run(order=183)
    def test_183_NIOS_85813_Disable_the_DTC_Pool_With_ALl_Disable_Methods_when_in_None_state(self):
        print_and_log("*************** Disable DTC Pool With All Disable Methods when in None state ****************")
        disable_states = ["UNTIL_MANUAL_ENABLING", "UNTIL_DNS_RESTART", "FOR_SPECIFIED_TIME"]
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        for i in disable_states:
            data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10,
                    "disable_on": [config.grid1_master_fqdn], "disable_timeframe": i, "dtc_object": ref_pool,
                    "specific_time_disable": 60}
            print_and_log(data)
            output = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data),
                                          params="?_function=dtc_object_disable")
            print_and_log(output)
            if type(output) == tuple:
                out = output[1]
                out = json.loads(out)
                print_and_log(out)
                error_message = out['text']
                print_and_log(error_message)
                expected_error_message = "The DTC object 'pool1' cannot be enabled/disabled since there are no associated enabled LBDN's"
                if error_message in expected_error_message:
                    print_and_log("Expected Error message is seen")
                    assert True
                else:
                    print_and_log("Expected Error message is not seen")
                    assert False
            else:
                print_and_log(output)
                print_and_log("Able to Disable the DTC Pool Object when in None state")
                assert False
        print_and_log("************* Test Case 183 Execution Completed ***************")

    @pytest.mark.run(order=184)
    def test_184_NIOS_85813_Disable_the_DTC_LBDN_With_ALl_Disable_Methods_when_in_None_state(self):
        print_and_log("*************** Disable DTC LBDN With All Disable Methods when in None state ****************")
        disable_states = ["UNTIL_MANUAL_ENABLING", "UNTIL_DNS_RESTART", "FOR_SPECIFIED_TIME"]
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        print_and_log(response)
        ref_lbdn = response[0]['_ref']
        for i in disable_states:
            data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10,
                    "disable_on": [config.grid1_master_fqdn], "disable_timeframe": i, "dtc_object": ref_lbdn,
                    "specific_time_disable": 60}
            print_and_log(data)
            output = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data),
                                          params="?_function=dtc_object_disable")
            print_and_log(output)
            if type(output) == tuple:
                out = output[1]
                out = json.loads(out)
                print_and_log(out)
                error_message = out['text']
                print_and_log(error_message)
                expected_error_message = "The DTC object 'DTC_LBDN_1' cannot be enabled/disabled since there are no associated zones"
                if error_message in expected_error_message:
                    print_and_log("Expected Error message is seen")
                    assert True
                else:
                    print_and_log("Expected Error message is not seen")
                    assert False
            else:
                print_and_log(output)
                print_and_log("Able to Disable the DTC LBDN Object when in None state")
                assert False
        print_and_log("************* Test Case 184 Execution Completed ***************")

    @pytest.mark.run(order=185)
    def test_185_NIOS_85813_Add_the_Zone_and_pattern_in_the_LBDN_DTC_LBDN1(self):
        print_and_log(" ************ Add the Zone and pattern in the LBDN DTC LBDN1 ************ ")
        print_and_log("Getting ref of auth zone dtc.com")
        response = ib_NIOS.wapi_request('GET', object_type='zone_auth', params='?fqdn=dtc.com')
        response = json.loads(response)
        ref_zone = response[0]['_ref']
        print_and_log(ref_zone)
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        ref_lbdn = response[0]['_ref']
        print_and_log(ref_lbdn)
        print_and_log("********** Creating the lbdn by post request ************")
        data = {"auth_zones": [ref_zone], "patterns": ["*.dtc.com"]}
        print_and_log(data)
        response = ib_NIOS.wapi_request('PUT', object_type=ref_lbdn, fields=json.dumps(data))
        response = json.loads(response)
        print_and_log("Validation of lbdn creation")
        assert re.search(r'dtc:lbdn', response)
        print_and_log("******** Restart the DNS service *********")
        restart_the_grid_Services()
        print_and_log(" ************ Test Case 185 Execution Completed *************** ")




    @pytest.mark.run(order=186)
    def test_186_NIOS_85838_Validate_if_Zone_and_pattern_is_added_in_the_LBDN(self):
        print_and_log("************* Validate if Zone and pattern is added in the LBDN *************")
        print_and_log("Getting ref of DTC_LBDN_1")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        ref = response[0]['_ref']
        print_and_log(ref)
        response1 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=auth_zones')
        print_and_log(response1)
        response1 = json.loads(response1)
        auth_zones = response1['auth_zones'][0].split(':')[1].split('/')[0]
        response2 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=patterns')
        print_and_log(response2)
        response2 = json.loads(response2)
        patterns = response1['patterns']
        if auth_zones == "dtc.com" and patterns == "*.dtc.com":
            print_and_log("Auth zone and patterns are added in the LBDN")
            assert True
        else:
            print_and_log("Validation for the LBDN failed")
            assert False
        print_and_log(" ************ Test Case 186 Execution Completed *************** ")

    @pytest.mark.run(order=187)
    def test_187_NIOS_86538_Enable_Master_candidate_option_on_the_Grid_Member(self):
        print_and_log("********* Enable Master candidate option on the Grid Member ***********")
        response = ib_NIOS.wapi_request('GET', object_type="member")
        response = json.loads(response)
        print_and_log(response)
        ref = response[1]['_ref']
        data = {"master_candidate": True}
        response1 = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
        print_and_log(response1)
        assert re.search(r'member', response1)
        sleep(120)
        print_and_log("Test Case 187 Execution Completed")

    @pytest.mark.run(order=188)
    def test_188_NIOS_86538_Validate_if_Master_candidate_option_is_enalbed_in_the_Grid_Member(self):
        print_and_log("********** Validate if Master candidate option is enalbed in the Grid Member ***********")
        response = ib_NIOS.wapi_request('GET', object_type="member")
        response = json.loads(response)
        print_and_log(response)
        ref = response[1]['_ref']
        response1 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=master_candidate')
        response1 = json.loads(response1)
        print_and_log(response1)
        ref_master_candidate = response1['master_candidate']
        if ref_master_candidate == True:
            print_and_log("Master Candidate option is enabled in Grid member")
            assert True
        else:
            print_and_log("Master Candidate option is not enabled in Grid member")
            assert False
        print_and_log("Test Case 188 Execution Completed")

    @pytest.mark.run(order=189)
    def test_189_NIOS_86538_Add_Consolidated_health_monitors_to_pool1_with_Full_health_communication_option_checked(self):
        print_and_log("*********** Add Consolidated health monitors to pool1 with Full health communication option checked ************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        health_monitor_ref = getting_ref_of_the_dtc_health_monitors("dtc:monitor:icmp")
        print_and_log(health_monitor_ref)
        data = {"consolidated_monitors": [
            {"availability": "ANY", "full_health_communication": True, "members": [config.grid1_master_fqdn],
             "monitor": health_monitor_ref}]}
        response1 = ib_NIOS.wapi_request('PUT', object_type=ref_pool, fields=json.dumps(data))
        print_and_log(response1)
        assert re.search(r'dtc:pool', response1)
        restart_the_grid_Services()
        print_and_log("************* Test Case 189 Execution Completed ***************")

    @pytest.mark.run(order=190)
    def test_190_NIOS_86538_Validate_Consolidated_health_monitors_added_to_pool1_with_Full_health_communication_option_checked(self):
        print_and_log("************** Validate Consolidated health monitors added to pool1 with Full health communication option checked **************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        response1 = ib_NIOS.wapi_request('GET', object_type=ref_pool, params="?_return_fields=consolidated_monitors")
        response1 = json.loads(response1)
        print_and_log(response1)
        availability = response1['consolidated_monitors'][0]['availability']
        full_health_communication = response1['consolidated_monitors'][0]['full_health_communication']
        members = response1['consolidated_monitors'][0]['members'][0]
        print_and_log(availability)
        print_and_log(full_health_communication)
        print_and_log(members)
        if availability == "ANY" and full_health_communication == True and members == config.grid1_master_fqdn:
            print_and_log(
                "Consolidated monitors with availability " + availability + " and full health communication is set to TRUE with selected member " + members)
            assert True
        else:
            print_and_log("Validation for consolidated monitors failed for pool1")
            assert False
        print_and_log("************* Test Case 190 Execution Completed ***************")

    @pytest.mark.run(order=191)
    def test_191_NIOS_86538_Disable_the_DTC_Server_With_Disable_untill_Manual_enable(self):
        print_and_log("*************** Disable the DTC Server With Disable untill Manual enable ****************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name=server1')
        response = json.loads(response)
        print_and_log(response)
        ref_server = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10,
                "disable_on": [config.grid1_master_fqdn, config.grid1_member1_fqdn], "disable_timeframe": "UNTIL_MANUAL_ENABLING",
                "dtc_object": ref_server, "specific_time_disable": 60}
        output = dtc_object_failback_disable_options(data)
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC Server object disabled successfully")
            assert True
        else:
            print_and_log("DTC Server object is not Disabled")
            assert False
        print_and_log("************* Test Case 191 Execution Completed ***************")

    @pytest.mark.run(order=192)
    def test_192_NIOS_86538_Check_the_status_of_Server1_and_validate_if_the_status_is_Requires_Manual_Enabling(self):
        print_and_log("************* Check the status of Server1 and validate if the status is Requires Manual Enabling **************")
        out = check_the_DTC_objects_state('dtc:server', "server1")
        print_and_log(out)
        if out == 'WHITE':
            print_and_log("DTC server status is " + status)
            assert True
        else:
            print_and_log("DTC server status is not None")
            assert False
        print_and_log("************* Test Case 192 Execution Completed ***************")

    @pytest.mark.run(order=193)
    def test_193_NIOS_86538_Verify_the_error_logs_in_the_Infoblox_log_consolidate_monitors_are_configured_in_pool1(self):
        print_and_log("************* Verify the error logs in the Infoblox log consolidate monitors are configured in pool1 *************")
        log("start", "/infoblox/var/infoblox.log", config.grid_vip)
        sleep(300)
        LookFor1 = "'Consolidated Monitor: RabbitMQ: Error while sending message to Grid Member with ID'"
        try:
            logs = logv(LookFor1, "/infoblox/var/infoblox.log", config.grid_vip)
        except Exception as e:
            print_and_log(e)
            print_and_log(" Error message is not seen in the logs ")
            assert True
            log("stop", "/infoblox/var/infoblox.log", config.grid_vip)
        else:
            print_and_log(" Error message is seen in the logs ")
            assert False
            log("stop", "/infoblox/var/infoblox.log", config.grid_vip)
        print_and_log("*********** Test Case 193 Execution Completed ************")

    @pytest.mark.run(order=194)
    def test_194_NIOS_86538_Enable_the_Server_1_with_Manual_Enable_option(self):
        print_and_log("*********** Enable the server1 With Manual Enable option *************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name=server1')
        response = json.loads(response)
        ref_server = response[0]['_ref']
        data = {"enable_on": [config.grid1_master_fqdn, config.grid1_member1_fqdn], "dtc_object": ref_server}
        output = dtc_object_failback_enable_options(data)
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC Server 1 object Enabled successfully")
            assert True
        else:
            print_and_log("DTC Server 1 object is not enabled")
            assert False
        print_and_log("*********** Test Case 194 Execution Completed *************")


    @pytest.mark.run(order=195)
    def test_195_NIOS_86538_Check_the_status_of_Server1_and_validate_if_the_status_is_Running(self):
        print_and_log("************* Check the status of Server1 and validate if the status is Running **************")
        out = check_the_DTC_objects_state('dtc:server', "server1")
        print_and_log(out)
        if out == 'GREEN':
            print_and_log("DTC server status is " + status)
            assert True
        else:
            print_and_log("DTC server status is not WHITE")
            assert False
        print_and_log("************* Test Case 195 Execution Completed ***************")

    @pytest.mark.run(order=196)
    def test_196_NIOS_86538_Remove_Consolidated_health_monitors_from_pool1(self):
        print_and_log("*********** Remove Consolidated health monitors from pool1 ************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        data = {"consolidated_monitors": []}
        response1 = ib_NIOS.wapi_request('PUT', object_type=ref_pool, fields=json.dumps(data))
        print_and_log(response1)
        assert re.search(r'dtc:pool', response1)
        restart_the_grid_Services()
        print_and_log("************* Test Case 196 Execution Completed ***************")

    @pytest.mark.run(order=197)
    def test_197_NIOS_86538_Validate_Consolidated_health_monitors_added_to_pool1_with_Full_health_communication_option_checked(self):
        print_and_log("************** Validate Consolidated health monitors added to pool1 with Full health communication option checked **************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        response1 = ib_NIOS.wapi_request('GET', object_type=ref_pool, params="?_return_fields=consolidated_monitors")
        response1 = json.loads(response1)
        print_and_log(response1)
        consolidated_monitors = response1['consolidated_monitors']
        print_and_log(consolidated_monitors)
        if consolidated_monitors == []:
            print_and_log("Consolidated monitors are removed in the pool1")
            assert True
        else:
            print_and_log("Validation for consolidated monitors failed for pool1")
            assert False
        print_and_log("************* Test Case 197 Execution Completed ***************")

    @pytest.mark.run(order=198)
    def test_198_NIOS_86444_Create_admin_group_for_submitter(self):
        print_and_log("********** Create A new admin group for submitter **********")
        data = {"access_method": ["GUI", "API"], "name": "group_sub"}
        response = ib_NIOS.wapi_request('POST', object_type="admingroup", fields=json.dumps(data))
        print_and_log(response)
        assert re.search(r'admingroup', response)
        print_and_log("************ Test Case 198 Execution Completed *************")

    @pytest.mark.run(order=199)
    def test_199_NIOS_86444_Create_admin_group_for_approver(self):
        print_and_log("********** Create A new admin group for approver ************")
        data = {"access_method": ["GUI", "API"], "name": "group_app"}
        response = ib_NIOS.wapi_request('POST', object_type="admingroup", fields=json.dumps(data))
        print_and_log(response)
        assert re.search(r'admingroup', response)
        print_and_log("*********** Test Case 199 Execution Completed *************")

    @pytest.mark.run(order=200)
    def test_200_NIOS_86444_Validate_the_admin_group_created_for_submitter_and_approver(self):
        print_and_log("************* Validate the admin group created for submitter and approver *************")
        response = ib_NIOS.wapi_request('GET', object_type="admingroup")
        name_list = json.loads(response)
        print_and_log(name_list)
        expected_out = ["group_sub", "group_app"]
        actual_out = []
        for i in name_list:
            grp = i['name']
            actual_out.append(grp)
        print_and_log(actual_out)
        for i in expected_out:
            if i in actual_out:
                print_and_log("Admin group "+str(i)+" is present in "+str(actual_out))
                assert True
            else:
                print_and_log("Validation for admin group failed")
                assert False
        print_and_log("********** Test Case 200 Execution Completed *************")

    @pytest.mark.run(order=201)
    def test_201_NIOS_86444_Create_admin_user_for_submitter(self):
        print_and_log("********** Create A new admin user for submitter **********")
        data = {"admin_groups": ["group_sub"], "comment": "NIOS_86444", "name": "user_sub", "password": "infoblox"}
        response = ib_NIOS.wapi_request('POST', object_type="adminuser", fields=json.dumps(data))
        print_and_log(response)
        assert re.search(r'adminuser', response)
        print_and_log("************ Test Case 201 Execution Completed *************")

    @pytest.mark.run(order=202)
    def test_202_NIOS_86444_Create_admin_user_for_approver(self):
        print_and_log("********** Create A new admin user for approver **********")
        data = {"admin_groups": ["group_app"], "comment": "NIOS_86444", "name": "user_app", "password": "infoblox"}
        response = ib_NIOS.wapi_request('POST', object_type="adminuser", fields=json.dumps(data))
        print_and_log(response)
        assert re.search(r'adminuser', response)
        print_and_log("************ Test Case 202 Execution Completed *************")

    @pytest.mark.run(order=203)
    def test_203_NIOS_86444_Validate_the_admin_user_created_for_submitter_and_approver(self):
        print_and_log("************* Validate the admin user created for submitter and approver *************")
        response = ib_NIOS.wapi_request('GET', object_type="adminuser")
        print_and_log(response)
        name_list = json.loads(response)
        print_and_log(name_list)
        expected_out = ["user_sub", "user_app"]
        actual_out = []
        for i in name_list:
            grp = i['name']
            actual_out.append(grp)
        print_and_log(actual_out)
        for i in expected_out:
            if i in actual_out:
                print_and_log("Admin user " + str(i) + " is present in " + str(actual_out))
                assert True
            else:
                print_and_log("Validation for admin user failed")
                assert False
        print_and_log("********** Test Case 203 Execution Completed *************")

    @pytest.mark.run(order=204)
    def test_204_NIOS_86444_Create_Admin_Group_permission_as_Read_Write_for_resource_type_DTC_and_DNS_Grid_properties_in_submitter_group(self):
        print_and_log("************ Create Admin Group permission as Read Write for resource type DTC and DNS Grid properties in submitter group *************")
        resource_type = ["IDNS_CERTIFICATE", "IDNS_GEO_IP", "IDNS_LBDN", "IDNS_LBDN_RECORD", "IDNS_MONITOR", "IDNS_POOL", "IDNS_SERVER", "IDNS_TOPOLOGY"]
        print_and_log(resource_type)
        for i in resource_type:
            data = {"group": "group_sub", "permission": "WRITE", "resource_type": i}
            response = ib_NIOS.wapi_request('POST', object_type="permission", fields=json.dumps(data))
            print_and_log(response)
            assert re.search(r'permission', response)
        print_and_log("********** Test Case 204 Execution Completed *************")

    @pytest.mark.run(order=205)
    def test_205_NIOS_86444_Create_Admin_Group_permission_as_Read_Write_for_resource_type_is_DNS_Grid_properties_in_approver_group(self):
        print_and_log("************ Create Admin Group permission as Read Write for resource type is Grid properties in approver group *************")
        resource_type = ["IDNS_CERTIFICATE", "IDNS_GEO_IP", "IDNS_LBDN", "IDNS_LBDN_RECORD", "IDNS_MONITOR","IDNS_POOL", "IDNS_SERVER", "IDNS_TOPOLOGY"]
        print_and_log(resource_type)
        for i in resource_type:
            data = {"group": "group_app", "permission": "WRITE", "resource_type": i}
            response = ib_NIOS.wapi_request('POST', object_type="permission", fields=json.dumps(data))
            print_and_log(response)
            assert re.search(r'permission', response)
        print_and_log("********** Test Case 205 Execution Completed *************")

    @pytest.mark.run(order=206)
    def test_206_NIOS_86444_Validate_if_Admin_Group_permission_as_Read_Write_for_resource_type_is_DTC_and_Grid_DNS_properties_in_submitter_group(self):
        print_and_log("*********** Validate if Admin Group permission as Read Write for resource type is DTC and Grid DNS properties in submitter group ***********")
        resource_type = ["IDNS_CERTIFICATE", "IDNS_GEO_IP", "IDNS_LBDN", "IDNS_LBDN_RECORD", "IDNS_MONITOR", "IDNS_POOL", "IDNS_SERVER", "IDNS_TOPOLOGY"]
        response = ib_NIOS.wapi_request('GET', object_type="permission", params='?group=group_sub')
        print_and_log(response)
        response = json.loads(response)
        output = []
        for i in response:
            output.append(i['resource_type'])
        print_and_log(output)
        if output == resource_type:
            print_and_log("Resource Type has Read write Permissions for DTC and Grid DNS properties")
            assert True
        else:
            print_and_log("Validation for Resource Type is failed")
            assert False
        print_and_log("********** Test Case 206 Execution Completed *************")

    @pytest.mark.run(order=207)
    def test_207_NIOS_86444_Validate_if_Admin_Group_permission_as_Read_Write_for_resource_type_is_DTC_and_Grid_DNS_properties_in_approver_group(self):
        print_and_log("*********** Validate if Admin Group permission as Read Write for resource type is DTC and Grid DNS properties in approver group ***********")
        resource_type = ["IDNS_CERTIFICATE", "IDNS_GEO_IP", "IDNS_LBDN", "IDNS_LBDN_RECORD", "IDNS_MONITOR", "IDNS_POOL", "IDNS_SERVER", "IDNS_TOPOLOGY"]
        response = ib_NIOS.wapi_request('GET', object_type="permission", params='?group=group_app')
        print_and_log(response)
        response = json.loads(response)
        output = []
        for i in response:
            output.append(i['resource_type'])
        print_and_log(output)
        if output == resource_type:
            print_and_log("Resource Type has Read write Permissions for DTC and Grid DNS properties")
            assert True
        else:
            print_and_log("Validation for Resource Type is failed")
            assert False
        print_and_log("********** Test Case 207 Execution Completed *************")

    @pytest.mark.run(order=208)
    def test_208_NIOS_86444_Create_the_Approval_and_Submitter_workflow(self):
        print_and_log("********** Create the Approval and Submitter workflow **********")
        data = {"approval_group": "group_app", "submitter_group": "group_sub"}
        response = ib_NIOS.wapi_request('POST', object_type="approvalworkflow", fields=json.dumps(data))
        print_and_log(response)
        assert re.search(r'approvalworkflow', response)
        print_and_log("********** Test Case 208 Execution Completed *************")

    @pytest.mark.run(order=209)
    def test_209_NIOS_86444_Validate_if_the_Approval_and_Submitter_workflow_is_created(self):
        print_and_log("*********** Validate if the Approval and Submitter workflow is created ************")
        response = ib_NIOS.wapi_request('GET', object_type="approvalworkflow")
        response = json.loads(response)
        approval_group = response[0]['approval_group']
        submitter_group = response[0]['submitter_group']
        if approval_group == "group_app" and submitter_group == "group_sub":
            print_and_log("New Workflow is created with approval group "+approval_group+" and submitter group "+submitter_group)
            assert True
        else:
            print_and_log("Validation for workflow failed")
            assert False
        print_and_log("********** Test Case 209 Execution Completed *************")

    @pytest.mark.run(order=210)
    def test_210_NIOS_86444_Disable_the_DTC_server_with_Disable_untill_manual_enable_with_approval_user(self):
        print_and_log("*********** Disable the DTC server with Disable untill manual enable with approval user ***********")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name=server1')
        response = json.loads(response)
        print_and_log(response)
        ref_server = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10,
                "disable_on": [config.grid1_master_fqdn], "disable_timeframe": "UNTIL_MANUAL_ENABLING",
                "dtc_object": ref_server, "specific_time_disable": 60}
        output = dtc_object_failback_disable_options_with_workflow(data, "user_app", "infoblox")
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC Server object disabled successfully")
            assert True
        else:
            print_and_log("DTC Server object is not Disabled")
            assert False
        print_and_log("************* Test Case 210 Execution Completed ***************")

    @pytest.mark.run(order=211)
    def test_211_NIOS_86444_Enable_the_DTC_Server_using_with_Manual_enable(self):
        print_and_log("*********** Enable the DTC Server using Manual enable with approval user *************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name=server1')
        response = json.loads(response)
        ref_server = response[0]['_ref']
        data = {"enable_on": [config.grid1_master_fqdn], "dtc_object": ref_server}
        output = dtc_object_failback_enable_options_with_workflow(data, "user_app", "infoblox")
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC Server 1 object Enabled successfully")
            assert True
        else:
            print_and_log("DTC Server 1 object is not enabled")
            assert False
        print_and_log("************* Test Case 211 Execution Completed ***************")

    @pytest.mark.run(order=212)
    def test_212_NIOS_86444_Disable_the_DTC_pool_with_Disable_untill_manual_enable_with_approval_user(self):
        print_and_log("*********** Disable the DTC pool with Disable untill manual enable with approval user ***********")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10,
                "disable_on": [config.grid1_master_fqdn], "disable_timeframe": "UNTIL_MANUAL_ENABLING",
                "dtc_object": ref_pool, "specific_time_disable": 60}
        output = dtc_object_failback_disable_options_with_workflow(data, "user_app", "infoblox")
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC pool object disabled successfully")
            assert True
        else:
            print_and_log("DTC pool object is not Disabled")
            assert False
        print_and_log("************* Test Case 212 Execution Completed ***************")

    @pytest.mark.run(order=213)
    def test_213_NIOS_86444_Enable_the_DTC_pool_using_with_Manual_enable_with_approval_user(self):
        print_and_log("*********** Enable the DTC pool using Manual enable with approval user *************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response = json.loads(response)
        ref_pool = response[0]['_ref']
        data = {"enable_on": [config.grid1_master_fqdn], "dtc_object": ref_pool}
        output = dtc_object_failback_enable_options_with_workflow(data, "user_app", "infoblox")
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC pool 1 object Enabled successfully")
            assert True
        else:
            print_and_log("DTC pool 1 object is not enabled")
            assert False
        print_and_log("************* Test Case 213 Execution Completed ***************")

    @pytest.mark.run(order=214)
    def test_214_NIOS_86444_Disable_the_DTC_lbdn_with_Disable_untill_manual_enable_with_approval_user_with_approval_user(self):
        print_and_log("*********** Disable the DTC lbdn with Disable untill manual enable with approval user ***********")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        print_and_log(response)
        ref_lbdn = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10,
                "disable_on": [config.grid1_master_fqdn], "disable_timeframe": "UNTIL_MANUAL_ENABLING",
                "dtc_object": ref_lbdn, "specific_time_disable": 60}
        output = dtc_object_failback_disable_options_with_workflow(data, "user_app", "infoblox")
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC LBDN object disabled successfully")
            assert True
        else:
            print_and_log("DTC LBDN object is not Disabled")
            assert False
        print_and_log("************* Test Case 214 Execution Completed ***************")

    @pytest.mark.run(order=215)
    def test_215_NIOS_86444_Enable_the_DTC_lbdn_using_with_Manual_enable_with_approval_user(self):
        print_and_log("*********** Enable the DTC lbdn using Manual enable with approval user *************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        ref_lbdn = response[0]['_ref']
        data = {"enable_on": [config.grid1_master_fqdn], "dtc_object": ref_lbdn}
        output = dtc_object_failback_enable_options_with_workflow(data, "user_app", "infoblox")
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC LBDN 1 object Enabled successfully")
            assert True
        else:
            print_and_log("DTC LBDN 1 object is not enabled")
            assert False
        print_and_log("************* Test Case 215 Execution Completed ***************")

    @pytest.mark.run(order=216)
    def test_216_NIOS_86444_Disable_the_DTC_server_with_Disable_untill_manual_enable_with_submitter_user(self):
        print_and_log("*********** Disable the DTC server with Disable untill manual enable with submitter user ***********")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name=server1')
        response = json.loads(response)
        print_and_log(response)
        ref_server = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10,
                "disable_on": [config.grid1_master_fqdn], "disable_timeframe": "UNTIL_MANUAL_ENABLING",
                "dtc_object": ref_server, "specific_time_disable": 60}
        output = dtc_object_failback_disable_options_with_workflow(data, "user_sub", "infoblox")
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC Server object disabled successfully")
            assert True
        else:
            print_and_log("DTC Server object is not Disabled")
            assert False
        print_and_log("************* Test Case 216 Execution Completed ***************")

    @pytest.mark.run(order=217)
    def test_217_NIOS_86444_Enable_the_DTC_Server_using_with_Manual_enable_with_submitter_user(self):
        print_and_log("*********** Enable the DTC Server using Manual enable with submitter user *************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name=server1')
        response = json.loads(response)
        ref_server = response[0]['_ref']
        data = {"enable_on": [config.grid1_master_fqdn], "dtc_object": ref_server}
        output = dtc_object_failback_enable_options_with_workflow(data, "user_sub", "infoblox")
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC Server 1 object Enabled successfully")
            assert True
        else:
            print_and_log("DTC Server 1 object is not enabled")
            assert False
        print_and_log("************* Test Case 217 Execution Completed ***************")

    @pytest.mark.run(order=218)
    def test_218_NIOS_86444_Disable_the_DTC_pool_with_Disable_untill_manual_enable_with_submitter_user(self):
        print_and_log("*********** Disable the DTC pool with Disable untill manual enable with submitter user ***********")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response = json.loads(response)
        print_and_log(response)
        ref_pool = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10,
                "disable_on": [config.grid1_master_fqdn], "disable_timeframe": "UNTIL_MANUAL_ENABLING",
                "dtc_object": ref_pool, "specific_time_disable": 60}
        output = dtc_object_failback_disable_options_with_workflow(data, "user_sub", "infoblox")
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC pool object disabled successfully")
            assert True
        else:
            print_and_log("DTC pool object is not Disabled")
            assert False
        print_and_log("************* Test Case 218 Execution Completed ***************")

    @pytest.mark.run(order=219)
    def test_219_NIOS_86444_Enable_the_DTC_pool_using_with_Manual_enable_with_submitter_user(self):
        print_and_log("*********** Enable the DTC pool using Manual enable with submitter user *************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response = json.loads(response)
        ref_pool = response[0]['_ref']
        data = {"enable_on": [config.grid1_master_fqdn], "dtc_object": ref_pool}
        output = dtc_object_failback_enable_options_with_workflow(data, "user_sub", "infoblox")
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC pool 1 object Enabled successfully")
            assert True
        else:
            print_and_log("DTC pool 1 object is not enabled")
            assert False
        print_and_log("************* Test Case 219 Execution Completed ***************")

    @pytest.mark.run(order=220)
    def test_220_NIOS_86444_Disable_the_DTC_lbdn_with_Disable_untill_manual_enable_with_approval_user_with_submitter_user(self):
        print_and_log("*********** Disable the DTC lbdn with Disable untill manual enable with submitter user ***********")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        print_and_log(response)
        ref_lbdn = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10,
                "disable_on": [config.grid1_master_fqdn], "disable_timeframe": "UNTIL_MANUAL_ENABLING",
                "dtc_object": ref_lbdn, "specific_time_disable": 60}
        output = dtc_object_failback_disable_options_with_workflow(data, "user_sub", "infoblox")
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC LBDN object disabled successfully")
            assert True
        else:
            print_and_log("DTC LBDN object is not Disabled")
            assert False
        print_and_log("************* Test Case 220 Execution Completed ***************")

    @pytest.mark.run(order=221)
    def test_221_NIOS_86444_Enable_the_DTC_lbdn_using_with_Manual_enable_with_submitter_user(self):
        print_and_log("*********** Enable the DTC lbdn using Manual enable with submitter user *************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        ref_lbdn = response[0]['_ref']
        data = {"enable_on": [config.grid1_master_fqdn], "dtc_object": ref_lbdn}
        output = dtc_object_failback_enable_options_with_workflow(data, "user_sub", "infoblox")
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC LBDN 1 object Enabled successfully")
            assert True
        else:
            print_and_log("DTC LBDN 1 object is not enabled")
            assert False
        print_and_log("************* Test Case 221 Execution Completed ***************")


    #chetan
    @pytest.mark.run(order=222)
    def test_222_NIOS_81110_Start_DNS_service(self):
        """
        Start DNS service on all members.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 222 Started                |")
        display_msg("+----------------------------------------------+")

        display_msg("Enable DNS service")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns')
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'],
                                            fields=json.dumps({"enable_dns": True, "use_lan_ipv6_port": True}))
            if type(response) == tuple:
                display_msg("FAIL: Enable DNS Service")
                assert False
        display_msg("PASS: DNS Service enabled")
        sleep(3)

        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        dns_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=enable_dns')
        display_msg(dns_ref)
        if 'true' in dns_ref:
            display_msg("PASS: DNS service vaidation")
        else:
            display_msg("FAIL: DNS service vaidation")
            assert False

        display_msg("---------Test Case 222 Execution Completed----------")

    # NIOS-81110
    @pytest.mark.run(order=223)
    def test_223_NIOS_81110_Validate_named_service_start(self):
        """
        Validate named service started without any issue.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 223 Started                |")
        display_msg("+----------------------------------------------+")

        display_msg("ps ax | grep named")
        remove_known_hosts_file()
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey=mykey)
        stdin, stdout, stderr = client.exec_command("ps ax | grep named")
        output = []
        flag = False
        flag2 = False
        for line in stdout.readlines():
            display_msg(line)
            output.append(line)
            if 'named.conf' in line:
                flag = True
            if 'grep' in line:
                flag2 = True
        client.close()
        if not flag or not flag2 or len(output) > 3:
            display_msg("named not started or other scripts hung.")
            assert False

        display_msg("---------Test Case 223 Execution Completed----------")

    # NIOS-81110
    @pytest.mark.run(order=224)
    def test_224_NIOS_81110_Stop_DNS_service(self):
        """
        Stop DNS service on all members.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 224 Started                |")
        display_msg("+----------------------------------------------+")

        display_msg("Disable DNS service")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns')
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps({"enable_dns": False}))
            display_msg(response)
            if type(response) == tuple:
                display_msg("FAIL: Disable DNS Service")
                assert False
        display_msg("PASS: DNS Service disabled")
        sleep(3)

        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        dns_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=enable_dns')
        display_msg(dns_ref)
        if 'false' in dns_ref:
            display_msg("PASS: DNS service vaidation")
        else:
            display_msg("FAIL: DNS service vaidation")
            assert False

        display_msg("---------Test Case 224 Execution Completed----------")

    # NIOS-81110
    @pytest.mark.run(order=225)
    def test_225_NIOS_81110_Validate_named_service_stop(self):
        """
        Validate named service stopped without any issue.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 225 Started                |")
        display_msg("+----------------------------------------------+")
        sleep(30)
        remove_known_hosts_file()
        display_msg("ps ax | grep named")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey=mykey)
        stdin, stdout, stderr = client.exec_command("ps ax | grep named")
        for line in stdout.readlines():
            display_msg(line)
            if 'named.conf' in line:
                display_msg("named service not stopped.")
                client.close()
                assert False
        client.close()
        display_msg("named service is stopped correctly")

        display_msg("---------Test Case 225 Execution Completed----------")

    # NIOS-81156
    @pytest.mark.run(order=226)
    def test_226_NIOS_81156_Start_DNS_service(self):
        """
        Start DNS service on all members.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 226 Started                |")
        display_msg("+----------------------------------------------+")

        # Start log capture
        display_msg("Starting infoblox log capture")
        log("start", "/infoblox/var/infoblox.log", config.grid_vip)

        display_msg("Enable DNS service")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member:dns')
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'],
                                            fields=json.dumps({"enable_dns": True, "use_lan_ipv6_port": True}))
            if type(response) == tuple:
                display_msg("FAIL: Enable DNS Service")
                assert False
        display_msg("PASS: DNS Service enabled")
        sleep(3)

        # stop log capture
        display_msg("Stop log capture")
        log("stop", "/infoblox/var/infoblox.log", config.grid_vip)

        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        dns_ref = ib_NIOS.wapi_request('GET', object_type='member:dns?_return_fields=enable_dns')
        display_msg(dns_ref)
        if 'true' in dns_ref:
            display_msg("PASS: DNS service vaidation")
        else:
            display_msg("FAIL: DNS service vaidation")
            assert False

        # validate captured log
        display_msg("Validate log for deprecated configuration warnings and Internal Error")
        try:
            logv("'is obsolete and should be removed'", "/infoblox/var/infoblox.log", config.grid_vip)
            display_msg("FAIL: Above warning messages are seen")
            assert False
        except Exception as E:
            if 'returned non-zero exit status 1' in str(E):
                display_msg("PASS: Deprecated configuration warnings not seen")
                assert True
            else:
                display_msg(E)
                assert False
        try:
            logv("'Internal Error'", "/infoblox/var/infoblox.log", config.grid_vip)
            display_msg("FAIL: Internal Error is seen")
            assert False
        except Exception as E:
            if 'returned non-zero exit status 1' in str(E):
                display_msg("PASS: Internal Error not seen")
                assert True
            else:
                display_msg(E)
                assert False

        display_msg("---------Test Case 226 Execution Completed----------")

    # NIOS-82950
    @pytest.mark.run(order=227)
    def test_227_NIOS_82950_add_auth_zone(self):
        """
        Add an authoritative zone.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 227 Started                |")
        display_msg("+----------------------------------------------+")

        display_msg("Add an authoritative zone test.com")
        data = {"fqdn": "test.com",
                "view": "default",
                "grid_primary": [{"name": config.grid1_master_fqdn, "stealth": False}],
                "grid_secondaries": [{"name": config.grid1_member1_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: Create Authorative FMZ")
            assert False
        restart_services()
        display_msg("PASS: Authoritative zone test.com is added")

        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test.com")
        display_msg(get_ref)
        if 'test.com' in get_ref:
            display_msg("PASS: Zone test.com found")
        else:
            display_msg("FAIL: Zone test.com not found")
            assert False

        display_msg("---------Test Case 227 Execution Completed----------")

    # NIOS-81110
    @pytest.mark.run(order=228)
    def test_228_NIOS_81110_Validate_named_service_restart(self):
        """
        Validate named service re-started without any issue.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 228 Started                |")
        display_msg("+----------------------------------------------+")

        display_msg("ps ax | grep named")
        remove_known_hosts_file()
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey=mykey)
        stdin, stdout, stderr = client.exec_command("ps ax | grep named")
        output = []
        flag = False
        flag2 = False
        for line in stdout.readlines():
            display_msg(line)
            output.append(line)
            if 'named.conf' in line:
                flag = True
            if 'grep' in line:
                flag2 = True
        client.close()
        if not flag or not flag2 or len(output) > 3:
            display_msg("named not started or other scripts hung.")
            assert False

        display_msg("---------Test Case 228 Execution Completed----------")

    # NIOS-82950
    @pytest.mark.run(order=229)
    def test_229_NIOS_82950_add_a_record(self):
        """
        Add a record in the test.com zone.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 229 Started                |")
        display_msg("+----------------------------------------------+")

        display_msg("Add a record a.test.com")
        data = {"name": "a.test.com",
                "ipv4addr": "10.1.1.1"
                }
        response = ib_NIOS.wapi_request('POST', object_type='record:a', fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Add a record a.test.com")
            assert False
        display_msg("PASS: a record a.test.com added")

        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:a?name=a.test.com")
        display_msg(get_ref)
        if 'a.test.com' in get_ref:
            display_msg("PASS: A record a.test.com found")
        else:
            display_msg("FAIL: A record a.test.com not found")
            assert False

        display_msg("---------Test Case 229 Execution Completed----------")

    # NIOS-82950
    @pytest.mark.run(order=230)
    def test_230_NIOS_82950_add_host_record(self):
        """
        Add host record in the test.com zone.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 230 Started                |")
        display_msg("+----------------------------------------------+")

        display_msg("Add host record a.test.com")
        data = {"name": "a.test.com",
                "ipv4addrs": [{"ipv4addr": "10.1.1.2"}]
                }
        response = ib_NIOS.wapi_request('POST', object_type='record:host', fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Add host record a.test.com")
            assert False
        display_msg("PASS: host record a.test.com added")

        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:host?name=a.test.com")
        display_msg(get_ref)
        if 'a.test.com' in get_ref:
            display_msg("PASS: Host record a.test.com found")
        else:
            display_msg("FAIL: Host record a.test.com not found")
            assert False

        display_msg("---------Test Case 230 Execution Completed----------")

    # NIOS-82913
    @pytest.mark.run(order=231)
    def test_231_NIOS_82913_add_few_more_a_records(self):
        """
        Add few more a records with same as existing in the test.com zone.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 231 Started               |")
        display_msg("+----------------------------------------------+")

        display_msg("Add few a records with name a.test.com")
        data1 = {"name": "a.test.com",
                 "ipv4addr": "10.1.1.3"
                 }
        data2 = {"name": "a.test.com",
                 "ipv4addr": "10.1.1.4"
                 }
        data3 = {"name": "a.test.com",
                 "ipv4addr": "10.1.1.5"
                 }
        response1 = ib_NIOS.wapi_request('POST', object_type='record:a', fields=json.dumps(data1))
        response2 = ib_NIOS.wapi_request('POST', object_type='record:a', fields=json.dumps(data2))
        response3 = ib_NIOS.wapi_request('POST', object_type='record:a', fields=json.dumps(data3))
        display_msg(response1)
        display_msg(response2)
        display_msg(response3)
        if type(response1) == tuple or type(response2) == tuple or type(response3) == tuple:
            display_msg("Failure: Add few a records with name a.test.com")
            assert False
        display_msg("PASS: few a records with name a.test.com added")

        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:a?name=a.test.com")
        display_msg(get_ref)
        if 'a.test.com' in get_ref:
            display_msg("PASS: A record a.test.com found")
        else:
            display_msg("FAIL: A record a.test.com not found")
            assert False

        display_msg("---------Test Case 231 Execution Completed---------")

    # NIOS-82913
    @pytest.mark.run(order=232)
    def test_232_NIOS_82913_Enable_DNS64(self):
        """
        Enable DNS64 with default DNS64 group.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 232 Started               |")
        display_msg("+----------------------------------------------+")

        display_msg("Get Grid DNS Properties ref")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns?_return_fields=enable_dns64")
        display_msg(get_ref)
        display_msg("Enable DNS64")
        data = {"enable_dns64": True, "dns64_groups": ["default"]}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: Enable DNS64")
            assert False
        display_msg("PASS: Enable DNS64")
        restart_services()

        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns?_return_fields=enable_dns64")
        display_msg(get_ref)
        if 'true' in get_ref:
            display_msg("PASS: DNS64 Enabled")
        else:
            display_msg("FAIL: DNS64 is still disabled")
            assert False

        display_msg("---------Test Case 232 Execution Completed---------")

    # NIOS-82913
    @pytest.mark.run(order=233)
    def test_233_NIOS_82913_Validate_RR_Set_Order_for_A_records(self):
        """
        Send dig query to the A records and validate the rr set order.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 233 Started               |")
        display_msg("+----------------------------------------------+")

        display_msg("Send multiple queries to A records")
        output1 = send_dig_query("a.test.com", "A", options="+short")
        output2 = send_dig_query("a.test.com", "A", options="+short")
        output3 = send_dig_query("a.test.com", "A", options="+short")
        output4 = send_dig_query("a.test.com", "A", options="+short")
        if output1 == output2 == output3 == output4:
            display_msg("FAIL: RR set is in fixed order.")
            assert False
        display_msg("PASS: RR set is in round robin order.")

        display_msg("---------Test Case 233 Execution Completed---------")

    # NIOS-82913
    @pytest.mark.run(order=234)
    def test_234_NIOS_82913_Validate_RR_Set_Order_for_AAAA_records(self):
        """
        Send dig query to the AAAA records and validate the rr set order.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 234 Started               |")
        display_msg("+----------------------------------------------+")

        display_msg("Send multiple queries to AAAA records")
        output1 = send_dig_query("a.test.com", "AAAA", options="+short")
        output2 = send_dig_query("a.test.com", "AAAA", options="+short")
        output3 = send_dig_query("a.test.com", "AAAA", options="+short")
        output4 = send_dig_query("a.test.com", "AAAA", options="+short")
        if output1 == output2 == output3 == output4:
            display_msg("FAIL: RR set is in fixed order.")
            assert False
        display_msg("PASS: RR set is in round robin order.")

        display_msg("---------Test Case 234 Execution Completed---------")

    # NIOS-86743,NIOS-82149
    @pytest.mark.run(order=235)
    def test_235_NIOS_86743_NIOS_82149_DNSSEC_Sign_zone(self):
        """
        DNSSEC Sign the zone test.com.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 235 Started               |")
        display_msg("+----------------------------------------------+")

        display_msg("Perform DNSSEC Sign on test.com")
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth?fqdn=test.com')
        display_msg(get_ref)
        data = {"operation": "SIGN"}
        response = ib_NIOS.wapi_request('POST', ref=json.loads(get_ref)[0]['_ref'] + '?_function=dnssec_operation',
                                        fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: DNSSEC Sign")
            assert False
        display_msg("PASS: DNSSEC Sign")
        restart_services()

        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth?_return_fields=is_dnssec_signed')
        display_msg(get_ref)
        if 'true' in get_ref:
            display_msg("PASS: Zone successfully Signed")
        else:
            display_msg("FAIL: Zone Sign unsuccessfull")
            assert False

        display_msg("---------Test Case 235 Execution Completed---------")

    # NIOS-86743
    @pytest.mark.run(order=236)
    def test_236_NIOS_86743_Modify_KSK_ZSK_Algorithm(self):
        """
        Update KSK and ZSK Algorithm with different value.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 237 Started               |")
        display_msg("+----------------------------------------------+")

        display_msg("Modify KSK and ZSK Algorithm")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=dnssec_key_params')
        display_msg(get_ref)
        data = {"dnssec_key_params": {"ksk_algorithms": [{"algorithm": "ECDSAP256SHA256", "size": 256}],
                                      "zsk_algorithms": [{"algorithm": "ECDSAP256SHA256", "size": 256}]}}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: Modify KSK and ZSK Algorithm")
            assert False
        display_msg("PASS: Modified KSK and ZSK Algorithm")
        restart_services()

        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=dnssec_key_params')
        display_msg(get_ref)
        if 'ECDSAP256SHA256' in get_ref:
            display_msg("PASS: Validation of KSK and ZSK Algorithm")
        else:
            display_msg("FAIL: Validation of KSK and ZSK Algorithm")
            assert False

        display_msg("---------Test Case 236 Execution Completed---------")

    # NIOS-86743
    @pytest.mark.run(order=237)
    def test_237_NIOS_86743_Apply_Algorithm_changes(self):
        """
        Apply alogorithm changes.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 238 Started               |")
        display_msg("+----------------------------------------------+")

        # Start log capture
        display_msg("Starting infoblox log capture")
        log("start", "/var/log/syslog.log", config.grid_vip)

        display_msg("Apply algorithm changes")
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth?fqdn=test.com')
        display_msg(get_ref)
        data = {"operation": "RESIGN"}
        response = ib_NIOS.wapi_request('POST', ref=json.loads(get_ref)[0]['_ref'] + '?_function=dnssec_operation',
                                        fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: DNSSEC ReSign")
            assert False
        display_msg("PASS: DNSSEC ReSign")
        restart_services()

        sleep(600)

        # stop log capture
        display_msg("Stop log capture")
        log("stop", "/var/log/syslog.log", config.grid_vip)

        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")

        # validate captured log
        display_msg("Validate log for failure")
        try:
            logv("'cannot be resigned'", "/var/log/syslog.log", config.grid_vip)
            logv("'No private keys found'", "/var/log/syslog.log", config.grid_vip)
            display_msg("FAIL: Above failure messages are seen")
            assert False
        except Exception as E:
            if 'returned non-zero exit status 1' in str(E):
                display_msg("PASS: Failure messages are not seen")
                assert True
            else:
                display_msg(E)
                assert False

        # Validate Sign
        get_ref = ib_NIOS.wapi_request('GET', object_type='zone_auth?_return_fields=is_dnssec_signed')
        display_msg(get_ref)
        if 'true' in get_ref:
            display_msg("PASS: Zone successfully Resigned")
        else:
            display_msg("FAIL: Zone Resign unsuccessfull")
            assert False

        display_msg("---------Test Case 237 Execution Completed---------")

    # NIOS-82461
    @pytest.mark.run(order=238)
    def test_238_NIOS_82461_add_auth_zone(self):
        """
        Add an authoritative zone test1.com.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 239 Started               |")
        display_msg("+----------------------------------------------+")

        display_msg("Add an authoritative zone test1.com")
        data = {"fqdn": "test1.com",
                "view": "default",
                "grid_primary": [{"name": config.grid1_master_fqdn, "stealth": False}],
                "grid_secondaries": [{"name": config.grid1_member1_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: Create Authorative FMZ")
            assert False
        restart_services()
        display_msg("PASS: Authoritative zone test1.com is added")

        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test1.com")
        display_msg(get_ref)
        if 'test1.com' in get_ref:
            display_msg("PASS: Zone test1.com found")
        else:
            display_msg("FAIL: Zone test1.com not found")
            assert False

        display_msg("---------Test Case 238 Execution Completed---------")

    # NIOS-82461
    @pytest.mark.run(order=239)
    def test_239_NIOS_82461_add_wild_card_a_records(self):
        """
        Add 200 wild card A records in the test1.com zone.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 240 Started               |")
        display_msg("+----------------------------------------------+")

        display_msg("Add 200 wild card a records *.test1.com")
        for i in range(1, 200):
            data = {"name": "*.test1.com",
                    "ipv4addr": "10.1.1." + str(i)
                    }
            response = ib_NIOS.wapi_request('POST', object_type='record:a', fields=json.dumps(data))
            display_msg(response)
            if type(response) == tuple:
                display_msg("Failure: Add a record *.test1.com")
                assert False
            display_msg("PASS: a record *.test1.com added with ip address " + "10.1.1." + str(i))

        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:a?name=*.test1.com")
        display_msg(get_ref)
        if '*.test1.com' in get_ref:
            display_msg("PASS: A record *.test1.com found")
        else:
            display_msg("FAIL: A record *.test1.com not found")
            assert False

        display_msg("---------Test Case 239 Execution Completed---------")

    # NIOS-82461
    @pytest.mark.run(order=240)
    def test_240_NIOS_82461_Modify_EDNS0_Buffer_size_and_UDP_Buffer_size(self):
        """
        Update EDNS(0) Buffer size and UDP Buffer size to 4096.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 241 Started               |")
        display_msg("+----------------------------------------------+")

        display_msg("Modify EDNS(0) Buffer Size and UDP Buffer Size to 4096")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=edns_udp_size,max_udp_size')
        display_msg(get_ref)
        data = {"edns_udp_size": 4096, "max_udp_size": 4096}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: Modify EDNS(0) Buffer Size and UDP Buffer Size to 4096")
            assert False
        display_msg("PASS: Modified EDNS(0) Buffer Size and UDP Buffer Size to 4096")
        restart_services()

        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns?_return_fields=edns_udp_size,max_udp_size')
        display_msg(get_ref)
        if '4096' in get_ref:
            display_msg("PASS: Validation of updated EDNS(0) Buffer Size and UDP Buffer Size")
        else:
            display_msg("FAIL: Validation of updated EDNS(0) Buffer Size and UDP Buffer Size")
            assert False

        display_msg("---------Test Case 240 Execution Completed---------")

    # NIOS-82461
    @pytest.mark.run(order=241)
    def test_241_NIOS_82461_Perform_EDNS_Query(self):
        """
        Perform EDNS Query and validate that the response is not truncated.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 242 Started               |")
        display_msg("+----------------------------------------------+")

        display_msg("Perform EDNS Query")
        output = send_dig_query("abc.test1.com", "A", options="+edns")
        if "trucated" in output:
            display_msg("FAIL: EDNS Query Output is truncated")
            assert False
        display_msg("PASS: EDNS Query output is not truncated")

        display_msg("---------Test Case 241 Execution Completed---------")

    # NIOS-85205
    @pytest.mark.run(order=242)
    def test_242_NIOS_85205_add_rpz_zone(self):
        """
        Add an RPZ zone rpz.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 243 Started               |")
        display_msg("+----------------------------------------------+")

        display_msg("Add an Response Policy Zone rpz")
        data = {"fqdn": "rpz",
                "grid_primary": [{"name": config.grid1_master_fqdn, "stealth": False}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_rp", fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: Response Policy Zone creation")
            assert False
        display_msg("PASS: Response Policy Zone 'rpz' is added")
        restart_services()

        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_rp?fqdn=rpz")
        display_msg(get_ref)
        if 'rpz' in get_ref:
            display_msg("PASS: Zone rpz found")
        else:
            display_msg("FAIL: Zone rpz not found")
            assert False

        display_msg("---------Test Case 242 Execution Completed---------")

    # NIOS-85205
    @pytest.mark.run(order=243)
    def test_243_NIOS_85205_add_rpz_passthru_rule(self):
        """
        Add an RPZ Passthru rule under the Response Policy Zone 'rpz'.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 244 Started               |")
        display_msg("+----------------------------------------------+")

        display_msg("Add RPZ Passthru rule under Response Policy Zone 'rpz'")
        data = {"canonical": "a.test1.com",
                "name": "a.test1.com.rpz",
                "rp_zone": "rpz"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname", fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: RPZ Passthru rule is not added")
            assert False
        display_msg("PASS: RPZ Passthru rule is added")

        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname?name=a.test1.com.rpz")
        display_msg(get_ref)
        get_ref = json.loads(get_ref)[0]
        if get_ref["canonical"] == get_ref["name"].strip(".rpz"):
            display_msg("PASS: RPZ Passthru rule found")
        else:
            display_msg("FAIL: RPZ Passthru rule missing")
            assert False

        display_msg("---------Test Case 243 Execution Completed---------")

    # NIOS-85205
    @pytest.mark.run(order=244)
    def test_244_NIOS_85205_add_rpz_no_data_rule(self):
        """
        Add an RPZ No Data rule under the Response Policy Zone 'rpz'.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 244 Started               |")
        display_msg("+----------------------------------------------+")

        display_msg("Add RPZ No Data rule under Response Policy Zone 'rpz'")
        data = {"canonical": "*",
                "name": "b.test1.com.rpz",
                "rp_zone": "rpz"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname", fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: RPZ No Data rule is not added")
            assert False
        display_msg("PASS: RPZ No Data rule is added")

        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname?name=b.test1.com.rpz")
        display_msg(get_ref)
        get_ref = json.loads(get_ref)[0]
        if get_ref["canonical"] == "*" and get_ref["name"] == "b.test1.com.rpz":
            display_msg("PASS: RPZ No Data rule found")
        else:
            display_msg("FAIL: RPZ No Data rule missing")
            assert False

        display_msg("---------Test Case 244 Execution Completed---------")

    # NIOS-85205
    @pytest.mark.run(order=245)
    def test_245_NIOS_85205_add_rpz_no_such_domain_rule(self):
        """
        Add an RPZ No Such Domain rule under the Response Policy Zone 'rpz'.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 245 Started               |")
        display_msg("+----------------------------------------------+")

        display_msg("Add RPZ No Such Domain rule under Response Policy Zone 'rpz'")
        data = {"canonical": "",
                "name": "c.test1.com.rpz",
                "rp_zone": "rpz"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname", fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: RPZ No Such Domain rule is not added")
            assert False
        display_msg("PASS: RPZ No Such Domain rule is added")

        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname?name=c.test1.com.rpz")
        display_msg(get_ref)
        get_ref = json.loads(get_ref)[0]
        if get_ref["canonical"] == "" and get_ref["name"] == "c.test1.com.rpz":
            display_msg("PASS: RPZ No Such Domain rule found")
        else:
            display_msg("FAIL: RPZ No Such Domain rule missing")
            assert False

        display_msg("---------Test Case 245 Execution Completed---------")

    # NIOS-85205
    @pytest.mark.run(order=246)
    def test_246_NIOS_85205_add_rpz_substitute_domain_name_rule(self):
        """
        Add an RPZ Substitute Domain Name rule under the Response Policy Zone 'rpz'.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 246 Started               |")
        display_msg("+----------------------------------------------+")

        display_msg("Add RPZ Substitute Domain Name rule under Response Policy Zone 'rpz'")
        data = {"canonical": "e.test1.com",
                "name": "d.test1.com.rpz",
                "rp_zone": "rpz"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:cname", fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: RPZ Substitute Domain Name rule is not added")
            assert False
        display_msg("PASS: RPZ Substitute Domain Name rule is added")

        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:cname?name=d.test1.com.rpz")
        display_msg(get_ref)
        get_ref = json.loads(get_ref)[0]
        if get_ref["canonical"] == "e.test1.com" and get_ref["name"] == "d.test1.com.rpz":
            display_msg("PASS: RPZ Substitute Domain Name rule found")
        else:
            display_msg("FAIL: RPZ Substitute Domain Name rule missing")
            assert False

        display_msg("---------Test Case 246 Execution Completed---------")

    # NIOS-85205
    @pytest.mark.run(order=247)
    def test_247_NIOS_85205_add_rpz_substitute_record_rule(self):
        """
        Add an RPZ Substitute A Record rule under the Response Policy Zone 'rpz'.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 247 Started               |")
        display_msg("+----------------------------------------------+")

        display_msg("Add RPZ Substitute A Record rule under Response Policy Zone 'rpz'")
        data = {"ipv4addr": "100.100.100.100",
                "name": "f.test1.com.rpz",
                "rp_zone": "rpz"}
        response = ib_NIOS.wapi_request('POST', object_type="record:rpz:a", fields=json.dumps(data))
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: RPZ Substitute A Record rule is not added")
            assert False
        display_msg("PASS: RPZ Substitute A Record rule is added")

        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        get_ref = ib_NIOS.wapi_request('GET', object_type="record:rpz:a?name=f.test1.com.rpz")
        display_msg(get_ref)
        get_ref = json.loads(get_ref)[0]
        if get_ref["ipv4addr"] == "100.100.100.100" and get_ref["name"] == "f.test1.com.rpz":
            display_msg("PASS: RPZ Substitute A Record rule found")
        else:
            display_msg("FAIL: RPZ Substitute A Record rule missing")
            assert False

        display_msg("---------Test Case 247 Execution Completed---------")

    @pytest.mark.run(order=248)
    def test_248_NIOS_81534_Enable_Recursion_on_Grid1(self):
        print_and_log("************** Enable Recursion on Grid1 ***************")
        data = {"allow_recursive_query": True}
        res = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        print_and_log(res)
        res = json.loads(res)
        ref = res[0]['_ref']
        response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
        print_and_log(response)
        assert re.search(r'grid:dns', response)
        print_and_log("Restart DNS Services")
        restart_the_grid_Services()
        print_and_log("*********** Test Case 248 Execution Completed ************")

    @pytest.mark.run(order=249)
    def test_249_NIOS_81534_Verify_the_Recursion_enabled_on_Grid1(self):
        print_and_log("*********** Verify the Recursion enabled on Grid1 ***********")
        res = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        print_and_log(res)
        res = json.loads(res)
        ref = res[0]['_ref']
        response = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=allow_recursive_query')
        print_and_log(response)
        response = json.loads(response)
        allow_recursive_query = response['allow_recursive_query']
        if allow_recursive_query == True:
            print_and_log("Recursion query is enabled")
            assert True
        else:
            print_and_log("Recursion query is disabled")
            assert False
        print_and_log("*********** Test Case 249 Execution Completed ************")

    # NIOS-85205
    @pytest.mark.run(order=250)
    def test_250_NIOS_85205_query_to_match_passthru_RPZ_rule(self):
        """
        Send dig query to match Passthru RPZ Rule
        Validate SOA record is not present in the Additional section.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 250 Started               |")
        display_msg("+----------------------------------------------+")

        display_msg("Send dig query to match Passthru RPZ Rule")
        output = send_dig_query("a.test1.com", "A", options="+additional")
        output = str(output)
        if "NOERROR" in output and "ANSWER SECTION" in output:
            display_msg("PASS: Passthru RPZ rule is hit")
            if "SOA" in output:
                display_msg("FAIL: SOA Record is seen in additional section")
                assert False
            else:
                display_msg("PASS: SOA Record is not seen in additional section")
                assert True
        else:
            display_msg("FAIL: Passthru RPZ Rule is not hit")
            assert False
        display_msg("---------Test Case 250 Execution Completed---------")

    # NIOS-85205
    @pytest.mark.run(order=251)
    def test_251_NIOS_85205_query_to_match_no_data_RPZ_rule(self):

        """
        Send dig query to match No Data RPZ Rule
        Validate SOA record is not present in the Additional section.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 251 Started               |")
        display_msg("+----------------------------------------------+")

        display_msg("Send dig query to match No Data RPZ Rule")
        output = send_dig_query("b.test1.com", "A", options="+additional")
        output = str(output)
        if "NOERROR" in output and "ANSWER SECTION" not in output:
            display_msg("PASS: No Data RPZ rule is hit")
            if "SOA" in output:
                display_msg("FAIL: SOA Record is seen in additional section")
                assert False
            else:
                display_msg("PASS: SOA Record is not seen in additional section")
                assert True
        else:
            display_msg("FAIL: No Data RPZ Rule is not hit")
            assert False

        display_msg("---------Test Case 251 Execution Completed---------")

    # NIOS-85205
    @pytest.mark.run(order=252)
    def test_252_NIOS_85205_query_to_match_no_such_domain_RPZ_rule(self):
        """
        Send dig query to match No Such Domain RPZ Rule
        Validate SOA record is not present in the Additional section.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 252 Started               |")
        display_msg("+----------------------------------------------+")

        display_msg("Send dig query to match No Such Domain RPZ Rule")
        output = send_dig_query("c.test1.com", "A", options="+additional")
        output = str(output)
        if "NXDOMAIN" in output and "ANSWER SECTION" not in output:
            display_msg("PASS: No Such Domain RPZ rule is hit")
            if "SOA" in output:
                display_msg("FAIL: SOA Record is seen in additional section")
                assert False
            else:
                display_msg("PASS: SOA Record is not seen in additional section")
                assert True
        else:
            display_msg("FAIL: No Such Domain RPZ Rule is not hit")
            assert False

        display_msg("---------Test Case 252 Execution Completed---------")

    # NIOS-85205
    @pytest.mark.run(order=253)
    def test_253_NIOS_85205_query_to_match_substitute_domain_name_RPZ_rule(self):
        """
        Send dig query to match Substitute Domain Name RPZ Rule
        Validate SOA record is not present in the Additional section.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 253 Started               |")
        display_msg("+----------------------------------------------+")

        display_msg("Send dig query to match Substitute Domain Name RPZ Rule")
        output = send_dig_query("d.test1.com", "A", options="+additional")
        output = str(output)
        if "NOERROR" in output and "ANSWER SECTION" in output and "e.test1.com" in output:
            display_msg("PASS: Substitute Domain Name RPZ rule is hit")
            if "SOA" in output:
                display_msg("FAIL: SOA Record is seen in additional section")
                assert False
            else:
                display_msg("PASS: SOA Record is not seen in additional section")
                assert True
        else:
            display_msg("FAIL: Substitute Domain Name RPZ Rule is not hit")
            assert False

        display_msg("---------Test Case 253 Execution Completed---------")

    # NIOS-85205
    @pytest.mark.run(order=254)
    def test_254_NIOS_85205_query_to_match_substitute_record_RPZ_rule(self):
        """
        Send dig query to match Substitute A Record RPZ Rule
        Validate SOA record is not present in the Additional section.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case 254 Started               |")
        display_msg("+----------------------------------------------+")

        display_msg("Send dig query to match Substitute A Record RPZ Rule")
        output = send_dig_query("f.test1.com", "A", options="+additional")
        output = str(output)
        if "NOERROR" in output and "ANSWER SECTION" in output and "100.100.100.100" in output:
            display_msg("PASS: Substitute A Record RPZ rule is hit")
            if "SOA" in output:
                display_msg("FAIL: SOA Record is seen in additional section")
                assert False
            else:
                display_msg("PASS: SOA Record is not seen in additional section")
                assert True
        else:
            display_msg("FAIL: Substitute A Record RPZ Rule is not hit")
            assert False

        display_msg("---------Test Case 254 Execution Completed---------")

	display_msg("Delete the auth zone")
        response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=test.com", grid_vip=config.grid_vip)
        display_msg(response)
        ref = json.loads(response)[0]['_ref']
        del_ref = ib_NIOS.wapi_request('DELETE', object_type = ref)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_msg("FAILURE: Deleting zone failed.")
            assert False
        else:
            dns_restart_services()
            display_msg("Auth zone deletion successful")
            assert True
    #Arun J R
    @pytest.mark.run(order=255)
    def test_255_NIOS_81534_enable_dns_on_the_gird2(self):
        print_and_log("*********** Enabling the DNS on the Grid 2 ***********")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid2_master_vip)
        print_and_log(get_ref)
        res = json.loads(get_ref)
        data = {"enable_dns": True}
        print_and_log(data)
        response = ib_NIOS.wapi_request('PUT', ref=res[0]['_ref'], fields=json.dumps(data), grid_vip=config.grid2_master_vip)
        print_and_log(response)
        print_and_log("*********** Test Case 255 Execution Completed ************")

    @pytest.mark.run(order=256)
    def test_256_NIOS_81534_Validate_DNS_service_Enabled_on_Grid2(self):
        print_and_log("************ Validate DNS Service is enabled on Grid2 **************")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", params="?_return_fields=enable_dns", grid_vip=config.grid2_master_vip)
        res = json.loads(get_ref)
        print_and_log(res)
        if res[0]["enable_dns"] == True:
            print_and_log("DNS is enabled on the Grid 2")
            assert True
        else:
            print_and_log("DNS is not enabled on the Grid 2")
            assert False
        print_and_log("*********** Test Case 256 Execution Completed ************")


    @pytest.mark.run(order=257)
    def test_257_NIOS_81534_create_AuthZone_on_Grid2(self):
        print_and_log("************ Create auth Zone new.com on Grid2 *************")
        data = {"fqdn": "new.com", "grid_primary": [{"name": config.grid2_master_fqdn, "stealth": False}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data),
                                        grid_vip=config.grid2_master_vip)
        print_and_log(response)
        assert re.search(r'zone_auth', response)
        print_and_log("Restart DNS Services")
        restart_the_grid2_Services()
        print_and_log("*********** Test Case 257 Execution Completed ************")

    @pytest.mark.run(order=258)
    def test_258_NIOS_81534_Validate_the_AuthZone_Created_on_Grid2(self):
        print_and_log("************ Validate the AuthZone Created on Grid2 ***********")
        response = ib_NIOS.wapi_request('GET', object_type="zone_auth", params='?fqdn=new.com',
                                        grid_vip=config.grid2_master_vip)
        print_and_log(response)
        res = json.loads(response)
        fqdn = res[0]['fqdn']
        if fqdn == "new.com":
            print_and_log("Auth zone " + fqdn + " is configured successfully")
            assert True
        else:
            print_and_log("Validation failed for Auth zone new.com")
            assert False
        print_and_log("*********** Test Case 258 Execution Completed ************")

    @pytest.mark.run(order=259)
    def test_259_NIOS_81534_Create_A_record_for_the_auth_zone_created_on_Grid2(self):
        print_and_log("********** Create A record for the auth zone created on Grid2 **********")
        data = {"name": "arec.new.com", "ipv4addr": "1.1.1.1"}
        print_and_log(data)
        response = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(data), grid_vip=config.grid2_master_vip)
        print_and_log(response)
        assert re.search(r'record:a', response)
        print_and_log("********** Test Case 259 Execution Completed ***********")

    @pytest.mark.run(order=260)
    def test_260_NIOS_81534_Validate_A_record_for_the_auth_zone_created_on_Grid2(self):
        print_and_log("********** Validate A record for the auth zone created on Grid2 **********")
        response = ib_NIOS.wapi_request('GET', object_type="record:a", grid_vip=config.grid2_master_vip)
        output = json.loads(response)
        print_and_log(output)
        record_name = output[0]['name']
        if record_name == "arec.new.com":
            print_and_log("A record " + record_name + " is configured successfully")
            assert True
        else:
            print_and_log("Validation failed for A record arec.new.com")
            assert False
        print_and_log("********** Test Case 260 Execution Completed ***********")

    @pytest.mark.run(order=261)
    def test_261_NIOS_81534_Enable_Queries_and_responses_under_logging_on_Grid1(self):
        print_and_log("************** Enable Queries and responses under logging on Grid1 ***************")
        data = {"logging_categories": {"log_queries": True, "log_responses": True}}
        res = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        print_and_log(res)
        res = json.loads(res)
        ref = res[0]['_ref']
        response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
        print_and_log(response)
        assert re.search(r'grid:dns', response)
        print_and_log("Restart DNS Services")
        restart_the_grid_Services()
        print_and_log("*********** Test Case 261 Execution Completed ************")

    @pytest.mark.run(order=262)
    def test_262_NIOS_81534_Validate_Queries_and_responses_enabled_under_logging_on_Grid1(self):
        print_and_log("********** Validate Queries and responses enabled under logging on Grid1 **********")
        res = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        print_and_log(res)
        res = json.loads(res)
        ref = res[0]['_ref']
        response = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=logging_categories')
        print_and_log(response)
        response = json.loads(response)
        queries = response['logging_categories']['log_queries']
        responses = response['logging_categories']['log_responses']
        if queries == True and responses == True:
            print_and_log("Queries and Responses set to True under Logging")
            assert True
        else:
            print_and_log("Validation failed for logging")
            assert False
        print_and_log("*********** Test Case 262 Execution Completed ************")

    @pytest.mark.run(order=263)
    def test_263_NIOS_81534_Create_the_NX_DOMAIN_Ruleset_on_Grid1(self):
        print_and_log("********** Create the NX DOMAIN Ruleset on Grid1 **********")
        data = {"disabled": False, "name": "nxd_rule1", "type": "NXDOMAIN",
                "nxdomain_rules": [{"action": "MODIFY", "pattern": "arec.new.com"}]}
        request = ib_NIOS.wapi_request('POST', object_type="ruleset", fields=json.dumps(data))
        print_and_log(request)
        assert re.search(r'ruleset', request)
        print_and_log("*********** Test Case 263 Execution Completed ************")

    @pytest.mark.run(order=264)
    def test_264_NIOS_81534_Validate_the_NX_DOMAIN_Ruleset_on_Grid1(self):
        print_and_log("************ Validate the NX DOMAIN Ruleset on Grid1 **************")
        response = ib_NIOS.wapi_request('GET', object_type="ruleset")
        print_and_log(response)
        response = json.loads(response)
        ruleset_ref = response[0]['_ref']
        ruleset_name = response[0]['name']
        response1 = ib_NIOS.wapi_request('GET', object_type=ruleset_ref, params='?_return_fields=nxdomain_rules')
        print_and_log(response1)
        response1 = json.loads(response1)
        action = response1['nxdomain_rules'][0]['action']
        pattern = response1['nxdomain_rules'][0]['pattern']
        if ruleset_name == "nxd_rule1" and action == "MODIFY" and pattern == "arec.new.com":
            print_and_log(
                "NX DOMAIN ruleset " + ruleset_name + " is configured with action " + action + " and pattern " + pattern)
            assert True
        else:
            print_and_log("Validation for NX DOMAIN ruleset failed")
            assert False
        print_and_log("*********** Test Case 264 Execution Completed ************")

    @pytest.mark.run(order=265)
    def test_265_NIOS_81534_Add_the_Grid2_IP_As_the_Forwarder_IP_in_Grid1(self):
        print_and_log("*********** Add_the_Grid2_IP_As_the_Forwarder_IP_in_Grid1 ***********")
        data = {"forwarders": [config.grid2_master_vip]}
        res = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        print_and_log(res)
        res = json.loads(res)
        ref = res[0]['_ref']
        response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
        print_and_log(response)
        assert re.search(r'grid:dns', response)
        print_and_log("Restart DNS Services")
        restart_the_grid_Services()
        print_and_log("*********** Test Case 265 Execution Completed ************")

    @pytest.mark.run(order=266)
    def test_266_NIOS_81534_Verify_if_Grid2_IP_is_configured_as_Forwarder_IP_on_Grid1(self):
        print_and_log("*********** Verify if Grid2 IP is configured as Forwarder IP on Grid1 ***********")
        res = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        print_and_log(res)
        res = json.loads(res)
        ref = res[0]['_ref']
        response = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=forwarders')
        print_and_log(response)
        response = json.loads(response)
        forwarders = response['forwarders'][0]
        if forwarders == config.grid2_master_vip:
            print_and_log("Grid 2 IP " + forwarders + " is configured as Forwarder ip in Grid 2")
            assert True
        else:
            print_and_log("Validation of Forwarder IP Failed")
            assert False
        print_and_log("*********** Test Case 266 Execution Completed ************")

    @pytest.mark.run(order=267)
    def test_267_NIOS_81534_Enable_the_NXDOMAIN_redirection_for_created_ruleset_and_configure_ipv4_address(self):
        print_and_log("*********** Enable the NXDOMAIN redirection for created ruleset and configure ipv4 address ***********")
        data = {"nxdomain_redirect": True, "nxdomain_rulesets": ["nxd_rule1"],
                "nxdomain_redirect_addresses": ["11.11.11.11"]}
        res = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        print_and_log(res)
        res = json.loads(res)
        ref = res[0]['_ref']
        response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
        print_and_log(response)
        assert re.search(r'grid:dns', response)
        print_and_log("Restart DNS Services")
        restart_the_grid_Services()
        print_and_log("*********** Test Case 267 Execution Completed ************")

    @pytest.mark.run(order=268)
    def test_268_NIOS_81534_Verify_if_the_NXDOMAIN_redirection_is_enabled_for_created_ruleset_and_configure_ipv4_address(self):
        print_and_log("*********** Verify if the NXDOMAIN redirection is enabled for created ruleset and configure ipv4 address  ***********")
        res = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        print_and_log(res)
        res = json.loads(res)
        ref = res[0]['_ref']
        response = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=nxdomain_redirect')
        print_and_log(response)
        response = json.loads(response)
        nxdomain_redirect = response['nxdomain_redirect']
        response1 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=nxdomain_rulesets')
        print_and_log(response1)
        response1 = json.loads(response1)
        nxdomain_rulesets = response1['nxdomain_rulesets'][0]
        response2 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=nxdomain_redirect_addresses')
        print_and_log(response2)
        response2 = json.loads(response2)
        nxdomain_redirect_addresses = response2['nxdomain_redirect_addresses'][0]
        if nxdomain_redirect == True and nxdomain_rulesets == "nxd_rule1" and nxdomain_redirect_addresses == "11.11.11.11":
            print_and_log(
                "NXDOMAIN redirection for the ruleset is set to True with ruleset " + nxdomain_rulesets + " with IPV4 address " + nxdomain_redirect_addresses)
            assert True
        else:
            print_and_log("Validation failed for Re-direction of NXdomain")
            assert False
        print_and_log("*********** Test Case 268 Execution Completed ************")

    @pytest.mark.run(order=269)
    def test_269_NIOS_81534_Run_the_Dig_command_with_incorrect_domain_name_and_expect_response_from_the_redirection_IP(self):
        print_and_log("************* Run the Dig command with incorrect domain name and expect response from the redirection IP *************")
        output = os.popen("dig @" + config.grid_vip + " arec1.new.com in a").read()
        out = output.split("\n")
        flag = False
        for i in out:
            match = re.match("arec1.new.com.\s+\d+\s+IN\s+A\s+11.11.11.11", i)
            print_and_log(i)
            if match:
                print_and_log(" Match found ")
                flag = True
                break
        if flag == True:
            print_and_log("NXDOMAIN Re-directional IP responded to the query")
            assert True
        else:
            print_and_log("Dig command failed")
            assert False
        print_and_log("************ Test Case 269 Execution Completed **************")

    @pytest.mark.run(order=270)
    def test_270_NIOS_81534_Run_the_Dig_command_with_correct_domain_name_and_expect_response_from_A_record_IP(self):
        print_and_log("************* Run the Dig command with correct domain name and expect response from A record IP *************")
        output = os.popen("dig @" + config.grid_vip + " arec.new.com in a").read()
        out = output.split("\n")
        flag = False
        for i in out:
            match = re.match("arec.new.com.\s+\d+\s+IN\s+A\s+1.1.1.1", i)
            print_and_log(i)
            if match:
                print_and_log(" Match found ")
                flag = True
                break
        if flag == True:
            print_and_log("A Record responded to the query")
            assert True
        else:
            print_and_log("Dig command failed")
            assert False
        print_and_log("************ Test Case 270 Execution Completed **************")

    @pytest.mark.run(order=281)
    def test_281_NIOS_81534_Modify_the_Action_to_PASS_in_NXDOMAIN_ruleset_on_Grid1(self):
        print_and_log("********** Modify the Action to PASS in NXDOMAIN ruleset on Grid1 **********")
        response = ib_NIOS.wapi_request('GET', object_type="ruleset")
        print_and_log(response)
        response = json.loads(response)
        ruleset_ref = response[0]['_ref']
        data = {"nxdomain_rules": [{"action": "PASS", "pattern": "arec.new.com"}]}
        request = ib_NIOS.wapi_request('PUT', object_type=ruleset_ref, fields=json.dumps(data))
        print_and_log(request)
        assert re.search(r'ruleset', request)
        restart_the_grid_Services()
        print_and_log("*********** Test Case 281 Execution Completed ************")

    @pytest.mark.run(order=282)
    def test_282_NIOS_81534_Validate_the_NX_DOMAIN_Ruleset_Action_set_to_PASS_on_Grid1(self):
        print_and_log("************ Validate the NX DOMAIN Ruleset action set to PASS on Grid1 **************")
        response = ib_NIOS.wapi_request('GET', object_type="ruleset")
        print_and_log(response)
        response = json.loads(response)
        ruleset_ref = response[0]['_ref']
        ruleset_name = response[0]['name']
        response1 = ib_NIOS.wapi_request('GET', object_type=ruleset_ref, params='?_return_fields=nxdomain_rules')
        print_and_log(response1)
        response1 = json.loads(response1)
        action = response1['nxdomain_rules'][0]['action']
        if action == "PASS":
            print_and_log("NX DOMAIN ruleset " + ruleset_name + " is configured with action " + action)
            assert True
        else:
            print_and_log("Validation for NX DOMAIN ruleset failed")
            assert False
        print_and_log("*********** Test Case 282 Execution Completed ************")

    @pytest.mark.run(order=283)
    def test_283_NIOS_81534_Run_the_Dig_command_with_incorrect_domain_name_and_Action_set_to_PASS_and_expect_response_from_the_redirection_IP(self):
        print_and_log("************* Run the Dig command with incorrect domain name and action set to pass expect response from the redirection IP *************")
        output = os.popen("dig @" + config.grid_vip + " arec1.new.com in a").read()
        out = output.split("\n")
        flag = False
        for i in out:
            match = re.match("arec1.new.com.\s+\d+\s+IN\s+A\s+11.11.11.11", i)
            print_and_log(i)
            if match:
                print_and_log(" Match found ")
                flag = True
                break
        if flag == True:
            print_and_log("NXDOMAIN Re-directional IP responded to the query")
            assert True
        else:
            print_and_log("Dig command failed")
            assert False
        print_and_log("************ Test Case 283 Execution Completed **************")

    @pytest.mark.run(order=284)
    def test_284_NIOS_81534_Modify_the_Action_to_REDIRECT_in_NXDOMAIN_ruleset_on_Grid1(self):
        print_and_log("********** Modify the Action to REDIRECT in NXDOMAIN ruleset on Grid1 **********")
        response = ib_NIOS.wapi_request('GET', object_type="ruleset")
        print_and_log(response)
        response = json.loads(response)
        ruleset_ref = response[0]['_ref']
        data = {"nxdomain_rules": [{"action": "REDIRECT", "pattern": "arec.new.com"}]}
        request = ib_NIOS.wapi_request('PUT', object_type=ruleset_ref, fields=json.dumps(data))
        print_and_log(request)
        assert re.search(r'ruleset', request)
        restart_the_grid_Services()
        print_and_log("*********** Test Case 284 Execution Completed ************")

    @pytest.mark.run(order=285)
    def test_285_NIOS_81534_Validate_the_NX_DOMAIN_Ruleset_Action_set_to_PASS_on_Grid1(self):
        print_and_log("************ Validate the NX DOMAIN Ruleset action set to PASS on Grid1 **************")
        response = ib_NIOS.wapi_request('GET', object_type="ruleset")
        print_and_log(response)
        response = json.loads(response)
        ruleset_ref = response[0]['_ref']
        ruleset_name = response[0]['name']
        response1 = ib_NIOS.wapi_request('GET', object_type=ruleset_ref, params='?_return_fields=nxdomain_rules')
        print_and_log(response1)
        response1 = json.loads(response1)
        action = response1['nxdomain_rules'][0]['action']
        if action == "REDIRECT":
            print_and_log("NX DOMAIN ruleset " + ruleset_name + " is configured with action " + action)
            assert True
        else:
            print_and_log("Validation for NX DOMAIN ruleset failed")
            assert False
        print_and_log("*********** Test Case 285 Execution Completed ************")

    @pytest.mark.run(order=286)
    def test_286_NIOS_81534_Run_the_Dig_command_with_incorrect_domain_name_and_Action_set_to_REDIRECT_and_expect_response_from_the_redirection_IP(self):
        print_and_log("************* Run the Dig command with incorrect domain name and action set to REDIRECT expect response from the redirection IP *************")
        output = os.popen("dig @" + config.grid_vip + " arec1.new.com in a").read()
        out = output.split("\n")
        flag = False
        for i in out:
            match = re.match("arec1.new.com.\s+\d+\s+IN\s+A\s+11.11.11.11", i)
            print_and_log(i)
            if match:
                print_and_log(" Match found ")
                flag = True
                break
        if flag == True:
            print_and_log("NXDOMAIN Re-directional IP responded to the query")
            assert True
        else:
            print_and_log("Dig command failed")
            assert False
        print_and_log("************ Test Case 286 Execution Completed **************")


    @pytest.mark.run(order=287)
    def test_287_NIOS_81298_Create_the_Stub_Zone(self):
        print_and_log("************** Create the stub Zone ***************")
        data = {"fqdn": "stubzone1.com", "stub_from": [{"address": config.grid2_master_vip, "name": config.grid2_master_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_stub", fields=json.dumps(data))
        print_and_log(response)
        assert re.search(r'zone_stub', response)
        restart_the_grid_Services()
        print_and_log("*********** Test Case 287 Execution Completed ************")

    @pytest.mark.run(order=289)
    def test_289_NIOS_81298_Validate_the_Stub_zone_created(self):
        print_and_log("*********** Validate the Stub zone created ************")
        response = ib_NIOS.wapi_request('GET', object_type="zone_stub", params='?fqdn=stubzone1.com')
        print_and_log(response)
        response = json.loads(response)
        fqdn = response[0]['fqdn']
        master = response[0]['stub_from'][0]['address']
        if fqdn == "stubzone1.com" and master == config.grid2_master_vip:
            print_and_log("Stub zone " + fqdn + " is configured successfully with master " + master)
            assert True
        else:
            print_and_log("Validation for Stub zone failed")
            assert False
        print_and_log("*********** Test Case 289 Execution Completed ************")

    @pytest.mark.run(order=290)
    def test_290_NIOS_81298_Modify_the_Master_IP_in_the_Stub_zone_and_expect_no_error_in_infoblox_log(self):
        print_and_log("********** Modify the Master IP in the Stub zone and expect no error in infoblox log **********")
        log("start", "/infoblox/var/infoblox.log", config.grid_vip)
        res = ib_NIOS.wapi_request('GET', object_type="zone_stub", params='?fqdn=stubzone1.com')
        print_and_log(res)
        response = json.loads(res)
        ref = response[0]['_ref']
        data = {"stub_from": [{"address": "11.11.11.11", "name": config.grid2_master_fqdn}]}
        response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
        print_and_log(response)
        assert re.search(r'zone_stub', response)
        restart_the_grid_Services()
        try:
            LookFor = "Error in parsing SOA file for zone 'stubzone1.com.'"
            log("stop", "/infoblox/var/infoblox.log", config.grid_vip)
            logs = logv(LookFor, "/infoblox/var/infoblox.log", config.grid_vip)
        except Exception as e:
            print_and_log(e)
            print_and_log(" Error message is not seen in the logs ")
            assert True
        else:
            print_and_log(" Error message is seen in the logs ")
            assert False
        print_and_log("*********** Test Case 290 Execution Completed ************")

    @pytest.mark.run(order=291)
    def test_291_NIOS_81298_Enable_the_Fixed_RR_sets_and_configure_fqdns(self):
        print_and_log("************* Enable the Fixed RR sets and configure fqdns *************")
        data = {"enable_fixed_rrset_order_fqdns": True,
                "fixed_rrset_order_fqdns": [{"fqdn": "a.new.com", "record_type": "A"},
                                            {"fqdn": "c.new.com", "record_type": "A"},
                                            {"fqdn": "b.new.com", "record_type": "BOTH"}]}
        res = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        print_and_log(res)
        res = json.loads(res)
        ref = res[0]['_ref']
        response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
        print_and_log(response)
        assert re.search(r'grid:dns', response)
        print_and_log("Restart DNS Services")
        restart_the_grid_Services()
        print_and_log("*********** Test Case 291 Execution Completed ************")

    @pytest.mark.run(order=292)
    def test_292_NIOS_81298_Verify_if_the_Fixed_RR_Sets_option_is_enabled_with_fqdns_configured(self):
        print_and_log("*********** Verify if the Fixed RR Sets option is enabled with fqdns configured  ***********")
        res = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        print_and_log(res)
        res = json.loads(res)
        ref = res[0]['_ref']
        response = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=enable_fixed_rrset_order_fqdns')
        print_and_log(response)
        response = json.loads(response)
        enable_fixed_rrset_order_fqdns = response['enable_fixed_rrset_order_fqdns']
        response1 = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=fixed_rrset_order_fqdns')
        print_and_log(response1)
        response1 = json.loads(response1)
        fixed_rrset_order_fqdns = response1['fixed_rrset_order_fqdns']
        expected_output = [{"fqdn": "a.new.com", "record_type": "A"}, {"fqdn": "c.new.com", "record_type": "A"},
                           {"fqdn": "b.new.com", "record_type": "BOTH"}]
        if enable_fixed_rrset_order_fqdns == True and fixed_rrset_order_fqdns == expected_output:
            print_and_log("Fixed RR sets options is enabled and fqdns are configured successfully")
            assert True
        else:
            print_and_log("Validation failed for RR sets option and fqdns")
            assert False
        print_and_log("*********** Test Case 292 Execution Completed ************")

    @pytest.mark.run(order=293)
    def test_293_NIOS_81298_Configure_set_of_a_records_in_the_Grid2(self):
        print_and_log("*********** Configure set of a records in the Grid2 ************")
        record_ip = ["1.1.1.1", "2.2.2.2", "3.3.3.3"]
        for i in record_ip:
            data = {"name": "a.new.com", "ipv4addr": i}
            print_and_log(data)
            response = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(data),
                                            grid_vip=config.grid2_master_vip)
            print_and_log(response)
            assert re.search(r'record:a', response)
        record_ip_2 = ["4.4.4.4", "5.5.5.5", "6.6.6.6"]
        for i in record_ip_2:
            data = {"name": "d.new.com", "ipv4addr": i}
            print_and_log(data)
            response = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(data),
                                            grid_vip=config.grid2_master_vip)
            print_and_log(response)
            assert re.search(r'record:a', response)
        print_and_log("*********** Test Case 293 Execution Completed ************")

    @pytest.mark.run(order=294)
    def test_294_NIOS_81298_Validate_the_a_records_created_in_the_Grid2(self):
        print_and_log("*********** Validate the a records created in the Grid2 ************")
        response = ib_NIOS.wapi_request('GET', object_type="record:a", grid_vip=config.grid2_master_vip)
        print_and_log(response)
        record = json.loads(response)
        name = []
        for i in record:
            name.append(i['name'])
        print_and_log(name)
        if "a.new.com" in name and "d.new.com" in name:
            print_and_log("a.new.com and d.new.com records are present")
            assert True
        else:
            print_and_log("Validation failed for a records")
            assert False
        print_and_log("*********** Test Case 294 Execution Completed ************")

    @pytest.mark.run(order=295)
    def test_295_NIOS_81298_Run_the_Dig_commands_with_domain_which_are_defined_in_rr_set_defined_fqdns_and_response_should_be_in_fixed_order(self):
        print_and_log("*********** Run the Dig commands with domain which are defined in rr set defined fqdns and response should be in fixed order ***********")
        output1 = []
        output2 = []
        output3 = []
        output = os.popen("dig @" + config.grid_vip + " a.new.com in a +short").read()
        dig_out = output.split("\n")
        for i in dig_out:
            print_and_log(i)
            output1.append(i)
        output1 = list(filter(None, output1))
        print_and_log(output1)
        output = os.popen("dig @" + config.grid_vip + " a.new.com in a +short").read()
        dig_out2 = output.split("\n")
        for i in dig_out2:
            print_and_log(i)
            output2.append(i)
        output2 = list(filter(None, output2))
        print_and_log(output2)
        output = os.popen("dig @" + config.grid_vip + " a.new.com in a +short").read()
        dig_out3 = output.split("\n")
        for i in dig_out3:
            print_and_log(i)
            output3.append(i)
        output3 = list(filter(None, output3))
        print_and_log(output3)
        if output1 == output2 and output2 == output3 and output3 == output1:
            print_and_log("Response for the RR set fqdns are in Fixed order")
            assert True
        else:
            print_and_log("Responses for the RR set fqdns are not in Fixed order")
            assert False
        print_and_log("*********** Test Case 295 Execution Completed ************")

    @pytest.mark.run(order=296)
    def test_296_NIOS_81298_Run_the_Dig_commands_with_domain_which_are_not_defined_in_rr_set_defined_fqdns_and_response_should_be_in_round_robin_order(self):
        print_and_log("*********** Run the Dig commands with domain which are not defined in rr set defined fqdns and response should be in round robin order ***********")
        output1 = []
        output2 = []
        output3 = []
        output = os.popen("dig @" + config.grid_vip + " d.new.com in a +short").read()
        dig_out = output.split("\n")
        for i in dig_out:
            print_and_log(i)
            output1.append(i)
        output1 = list(filter(None, output1))
        print_and_log(output1)
        output = os.popen("dig @" + config.grid_vip + " d.new.com in a +short").read()
        dig_out2 = output.split("\n")
        for i in dig_out2:
            print_and_log(i)
            output2.append(i)
        output2 = list(filter(None, output2))
        print_and_log(output2)
        output = os.popen("dig @" + config.grid_vip + " d.new.com in a +short").read()
        dig_out3 = output.split("\n")
        for i in dig_out3:
            print_and_log(i)
            output3.append(i)
        output3 = list(filter(None, output3))
        print_and_log(output3)
        if output1 != output2 and output2 != output3 and output3 != output1:
            print_and_log("Response for the RR set fqdns are in Round Robin order")
            assert True
        else:
            print_and_log("Responses for the RR set fqdns are not in Round Robin order")
            assert False
        print_and_log("*********** Test Case 296 Execution Completed ************")

    @pytest.mark.run(order=297)
    def test_297_NIOS_81298_Add_the_sort_list_in_the_Grid1(self):
        print_and_log("************* Add the sort list in the Grid1 *************")
        data = {"sortlist": [{"address": config.client_ip, "match_list": ["1.1.1.1", "2.2.2.2", "3.3.3.3"]}]}
        res = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        print_and_log(res)
        res = json.loads(res)
        ref = res[0]['_ref']
        response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
        print_and_log(response)
        assert re.search(r'grid:dns', response)
        print_and_log("Restart DNS Services")
        restart_the_grid_Services()
        print_and_log("*********** Test Case 297 Execution Completed ************")

    @pytest.mark.run(order=298)
    def test_298_NIOS_81298_Verify_if_the_sort_list_is_configured(self):
        print_and_log("*********** Verify if the sort list is configured  ***********")
        res = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        print_and_log(res)
        res = json.loads(res)
        ref = res[0]['_ref']
        response = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=sortlist')
        print_and_log(response)
        response = json.loads(response)
        output = []
        list = response['sortlist'][0]['match_list']
        for i in list:
            output.append(i)
        print_and_log(output)
        address = response['sortlist'][0]['address']
        sort_list = ["1.1.1.1", "2.2.2.2", "3.3.3.3"]
        if output == sort_list and address == config.client_ip:
            print_and_log("Sort list Ip address are validated")
            assert True
        else:
            print_and_log("Sort list validation failed")
            assert False
        print_and_log("*********** Test Case 298 Execution Completed ************")

    @pytest.mark.run(order=299)
    def test_299_NIOS_81298_Run_the_Dig_commands_with_domain_which_are_defined_in_rr_set_defined_fqdns_and_response_should_be_in_fixed_order_and_same_as_in_sort_list(self):
        print_and_log("*********** Run the Dig commands with domain which are defined in rr set defined fqdns and response should be in fixed order and same as in sort list ***********")
        output1 = []
        output2 = []
        output3 = []
        expected_output = ["1.1.1.1", "2.2.2.2", "3.3.3.3"]
        output = os.popen("dig @" + config.grid_vip + " a.new.com in a +short").read()
        dig_out = output.split("\n")
        for i in dig_out:
            print_and_log(i)
            output1.append(i)
        output1 = list(filter(None, output1))
        print_and_log(output1)
        output = os.popen("dig @" + config.grid_vip + " a.new.com in a +short").read()
        dig_out2 = output.split("\n")
        for i in dig_out2:
            print_and_log(i)
            output2.append(i)
        output2 = list(filter(None, output2))
        print_and_log(output2)
        output = os.popen("dig @" + config.grid_vip + " a.new.com in a +short").read()
        dig_out3 = output.split("\n")
        for i in dig_out3:
            print_and_log(i)
            output3.append(i)
        output3 = list(filter(None, output3))
        print_and_log(output3)
        if output1 == expected_output and output2 == expected_output and output3 == expected_output:
            print_and_log("Response for the RR set fqdns are in Fixed order and same as sort list")
            assert True
        else:
            print_and_log("Responses for the RR set fqdns are not in Fixed order and not same as in sort list")
            assert False
        print_and_log("*********** Test Case 299 Execution Completed ************")

    @pytest.mark.run(order=300)
    def test_300_NIOS_81298_Modify_the_sort_list_in_the_Grid1(self):
        print_and_log("************* Modify the sort list in the Grid1 *************")
        data = {"sortlist": [{"address": config.client_ip, "match_list": ["4.4.4.4", "5.5.5.5", "6.6.6.6"]}]}
        res = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        print_and_log(res)
        res = json.loads(res)
        ref = res[0]['_ref']
        response = ib_NIOS.wapi_request('PUT', object_type=ref, fields=json.dumps(data))
        print_and_log(response)
        assert re.search(r'grid:dns', response)
        print_and_log("Restart DNS Services")
        restart_the_grid_Services()
        print_and_log("*********** Test Case 300 Execution Completed ************")

    @pytest.mark.run(order=301)
    def test_301_NIOS_81298_Verify_if_the_sort_list_is_modified_to_new_ips(self):
        print_and_log("*********** Verify if the sort list is modified to new ips  ***********")
        res = ib_NIOS.wapi_request('GET', object_type="grid:dns")
        print_and_log(res)
        res = json.loads(res)
        ref = res[0]['_ref']
        response = ib_NIOS.wapi_request('GET', object_type=ref, params='?_return_fields=sortlist')
        print_and_log(response)
        response = json.loads(response)
        output = []
        list = response['sortlist'][0]['match_list']
        for i in list:
            output.append(i)
        print_and_log(output)
        address = response['sortlist'][0]['address']
        sort_list = ["4.4.4.4", "5.5.5.5", "6.6.6.6"]
        if output == sort_list and address == config.client_ip:
            print_and_log("Sort list Ip address are validated")
            assert True
        else:
            print_and_log("Sort list validation failed")
            assert False
        print_and_log("*********** Test Case 301 Execution Completed ************")

    @pytest.mark.run(order=302)
    def test_302_NIOS_81298_Run_the_Dig_commands_with_domain_which_are_not_defined_in_rr_set_defined_fqdns_and_response_should_be_in_fixed_order_and_same_as_in_sort_list(self):
        print_and_log("*********** Run the Dig commands with domain which are not defined in rr set defined fqdns and response should be in fixed order and same as in sort list ***********")
        output1 = []
        output2 = []
        output3 = []
        expected_output = ["4.4.4.4", "5.5.5.5", "6.6.6.6"]
        output = os.popen("dig @" + config.grid_vip + " d.new.com in a +short").read()
        dig_out = output.split("\n")
        for i in dig_out:
            print_and_log(i)
            output1.append(i)
        output1 = list(filter(None, output1))
        print_and_log(output1)
        output = os.popen("dig @" + config.grid_vip + " d.new.com in a +short").read()
        dig_out2 = output.split("\n")
        for i in dig_out2:
            print_and_log(i)
            output2.append(i)
        output2 = list(filter(None, output2))
        print_and_log(output2)
        output = os.popen("dig @" + config.grid_vip + " d.new.com in a +short").read()
        dig_out3 = output.split("\n")
        for i in dig_out3:
            print_and_log(i)
            output3.append(i)
        output3 = list(filter(None, output3))
        print_and_log(output3)
        if output1 == expected_output and output2 == expected_output and output3 == expected_output:
            print_and_log("Response for the RR set fqdns which are are not in Fixed order and same as sort list")
            assert True
        else:
            print_and_log("Responses for the RR set fqdns are not in Fixed order and not same as in sort list")
            assert False
        print_and_log("*********** Test Case 302 Execution Completed ************")

    @pytest.mark.run(order=303)
    def test_303_NIOS_84672_Create_an_auth_zone(self):
        display_msg("Create auth zone")

        data = {"fqdn":"infoblox.com","view":"default","grid_primary":[{"name":config.grid1_master_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_msg("FAILURE: Create authoratative zone.")
            assert False
        else:
            display_msg("\n--------------------------------------------------------\n")
            display_msg("Validating Authoratative zone - infoblox.com")
            display_msg("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=infoblox.com", grid_vip=config.grid_vip)
            response=json.loads(response)[0]
            display_msg(response)

            if 'infoblox.com' in response['_ref']:
                display_msg(response["_ref"])
                display_msg("SUCCESS: Authoratative Zone 'infoblox.com' was created!")
                dns_restart_services()
                assert True
            else:
                display_msg("FAILURE: Authoratative Zone 'infoblox.com' creation failed")
                assert False

    
    @pytest.mark.run(order=304)
    def test_304_NIOS_84672_Add_A_record_to_the_auth_zone(self):
        display_msg("Add A record to the auth zone")

        data = {"ipv4addr": "1.2.3.4",
            "name": "a.infoblox.com",
            "view": "default"}
        response = ib_NIOS.wapi_request('POST', object_type="record:a", fields=json.dumps(data))
        display_msg(response)
        if response[0]==400 or response[0]==401 or response[0]==402:
    
            assert False
        else:

            assert True


    @pytest.mark.run(order=305)
    def test_305_NIOS_84672_Perform_dig_query_on_the_A_record_from_the_grid(self):
        display_msg("Perform dig query on the A records from the grid")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip,timeout=300)
        child.expect("bash-5.0#")
        child.sendline("dig @"+config.grid1_master_vip+" a.infoblox.com IN A")
        child.expect("bash-5.0#")
        output = child.before
        print(output)
        child.close()
        if('1.2.3.4' in output):
            display_msg("Dig query successfull")
            assert True
        else:
            display_msg("Dig query failed")
            assert False

    @pytest.mark.run(order=306)
    def test_306_NIOS_84672_Validate_if_core_files_were_generated_after_dig_operation(self):
        display_msg("Validate if cores were generated after the dig operation")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip,timeout=300)
        child.expect("bash-5.0#")
        child.sendline("ls -ltr /storage/cores")
        child.expect("bash-5.0#")
        output = child.before
        print(output)
        child.close()
        if('core.dig' in output):
            display_msg("Core files have been generated")
            assert False
        else:
            display_msg("Core file have not been generated")
            assert True

    @pytest.mark.run(order=307)
    def test_307_NIOS_84694_81654_Perform_nsupdate_from_the_grid(self):
        display_msg("Perform nspdate from the grid")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip,timeout=300)
        child.expect("bash-5.0#")
        child.sendline("nsupdate")
        child.expect(">")
        child.sendline("quit")
        child.expect("bash-5.0#")
        output = child.before
        print(output)
        child.close()
        if('error' in output):
            display_msg("ns update unsuccessfull")
            assert False
        else:
            display_msg("ns update successfull")
            assert True

    @pytest.mark.run(order=308)
    def test_308_NIOS_84694_81654_Validate_if_core_files_were_generated_after_nsupdate_operation(self):
        display_msg("Validate if cores were generated after the nsupdate operation")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip,timeout=300)
        child.expect("bash-5.0#")
        child.sendline("ls -ltr /storage/cores")
        child.expect("bash-5.0#")
        output = child.before
        print(output)
        child.close()
        if('core.nsupdate' in output):
            display_msg("Core files have been generated")
            assert False
        else:
            display_msg("Core file have not been generated")
            assert True

    @pytest.mark.run(order=309)
    def test_309_NIOS_83213_Add_ALIAS_Record_of_type_A_record(self):
        display_msg("Add ALIAS record of type A record")
        data = {"name": "alias.infoblox.com","target_name": "a.infoblox.com","target_type": "A","view": "default"}
        response = ib_NIOS.wapi_request('POST', object_type = "record:alias",fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_msg("ALIAS record creation failed")
            assert False
        else:
            display_msg("ALIAS record creation successfull")
            assert True

    @pytest.mark.run(order=310)
    def test_310_NIOS_83213_Perform_dig_operation_on_the_ALIAS_record(self):
        display_msg("Perform dig operation on the ALIAS record")
        try:
            output = subprocess.check_output(['dig','@'+config.grid1_master_vip,'alias.infoblox.com','IN','A'])
        except subprocess.CalledProcessError as e:
            display_msg("Error encountered while executing dig query")
            display_msg(e)
            assert False
        else:
            display_msg(output)
            if '1.2.3.4' in output:
                display_msg("Dig operation successfull")
                assert True
            else:
                display_msg("Dig operation was unsuccessfull")
                assert False

    @pytest.mark.run(order=311)
    def test_311_NIOS_83213_Validate_if_core_files_were_generated_after_dig_operation(self):
        display_msg("Validate if cores were generated after the dig operation")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip,timeout=300)
        child.expect("bash-5.0#")
        child.sendline("ls -ltr /storage/cores")
        child.expect("bash-5.0#")
        output = child.before
        print(output)
        child.close()
        if('core.isc-net-0000' in output):
            display_msg("Core files have been generated")
            assert False
        else:
            display_msg("Core file have not been generated")
            assert True


    @pytest.mark.run(order=312)
    def test_312_NIOS_82043_Set_return_minimal_responses_to_false_on_member_dns(self):
        display_msg("Set 'return minimal responses' to False in member DNS properties")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if ref["ipv4addr"] == config.grid1_master_vip:
                member_dns_ref = ref['_ref']
                break
        data = {"minimal_resp":False}
        response = ib_NIOS.wapi_request('PUT', object_type=member_dns_ref,fields=json.dumps(data))
        display_msg(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_msg("Unable to set 'Return minimal response' to False")
            assert False
        else:
            display_msg("'Return minimal response' set to False")
            dns_restart_services()
            assert True

    @pytest.mark.run(order=313)
    def test_313_NIOS_82043_Perform_dig_query_and_check_if_additional_sections_are_returned_in_the_response(self):
        display_msg("Perform dig query and check if additional sections are returned in the response")
        try:
            output = subprocess.check_output(['dig','@'+config.grid1_master_vip,'a.infoblox.com','IN','A'])
        except subprocess.CalledProcessError as e:
            display_msg("Error encountered while executing dig query")
            display_msg(e)
            assert False
        else:
            display_msg(output)
            count = 0
            if ';; AUTHORITY SECTION:' in output:
                count +=1 
                display_msg("Authority section present under the response")
            
            if ';; ADDITIONAL SECTION:' in output:
                count +=1
                display_msg("Additional section present under the response")

            if count == 2:
                display_msg("The dig repsonse did not return minimal response as expected")
                assert True
            else:
                display_msg("The dig response returned minimal response, when the 'Return minimal response' has been set to False")
                assert False

        
    @pytest.mark.run(order=314)
    def test_314_NIOS_82043_Set_return_minimal_responses_to_true_on_member_dns(self):
        display_msg("Set 'return minimal responses' to True in member DNS properties")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        display_msg(get_ref)
        for ref in json.loads(get_ref):
            if ref["ipv4addr"] == config.grid1_master_vip:
                member_dns_ref = ref['_ref']
                break
        data = {"minimal_resp":True}
        response = ib_NIOS.wapi_request('PUT', object_type=member_dns_ref,fields=json.dumps(data))
        display_msg(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_msg("Unable to set 'Return minimal response' to True")
            assert False
        else:
            display_msg("'Return minimal response' set to True")
            dns_restart_services()
            assert True

#"""
#Below testcases have been coded from 7th Dec 2022
#"""

    @pytest.mark.run(order=315)
    def test_315_NIOS_85705_Check_if_temporary_failure_in_name_resolution_logs_are_observerd_in_infoblox_logs(self):
        display_msg("Check if 'Temporary failure in name resolution' logs are observed in infoblox.log")
        display_msg("Starting log capture on infoblox.log")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        display_msg("Sleep for 2min for log capture")
        sleep(120)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        display_msg("Log capture complete")
        display_msg("Check if error logs are seen")
        if logv(".*Temporary failure in name resolution.*","/infoblox/var/infoblox.log",config.grid_vip) :
            display_msg("'Temporary failure in name resolution' logs are observed in infoblox.log")
            assert False
        else:
            display_msg("'Temporary failure in name resolution' logs are not observed in infoblox.log")
            assert True

    @pytest.mark.run(order=316)
    def test_316_NIOS_87645_create_an_auth_zone(self):
        display_msg("Create an Auth zone")

        data = {"fqdn":"nios87645.com","view":"default","grid_primary":[{"name":config.grid1_master_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_msg("FAILURE: Create authoratative zone.")
            assert False
        else:
            dns_restart_services()
            display_msg("\n--------------------------------------------------------\n")
            display_msg("Validating Authoratative zone - nios87645.com")
            display_msg("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=nios87645.com", grid_vip=config.grid_vip)
            response=json.loads(response)[0]
            display_msg(response)

            if 'nios87645.com' in response['_ref']:
                display_msg(response["_ref"])
                display_msg("SUCCESS: Authoratative Zone 'nios87645.com' was created!")
                dns_restart_services()
                assert True
            else:
                display_msg("FAILURE: Authoratative Zone 'nios87645.com' creation failed")
                assert False

    
    @pytest.mark.run(order=317)
    def test_317_NIOS_87645_Export_the_zone_data_in_csv_format(self):
        display_msg("Export the zone data in CSV format")
        data={"_separator":"COMMA","_object": "zone_auth"}
        create_file = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=csv_export")
        display_msg(create_file)
        res = json.loads(create_file)
        token = json.loads(create_file)['token']
        url = json.loads(create_file)['url']
        display_msg("Create the fileop function to dowload the csv file to the specified url")
        cmd='curl -k1 -u admin:infoblox -H "Content-type:application/force-download" -O %s'%(url)
        result = subprocess.check_output(cmd, shell=True)
        display_msg(result)

    @pytest.mark.run(order=318)
    def test_318_NIOS_87645_Verify_if_the_csv_file_has_been_downloaded(self):
        display_msg("Verify if the csv file has been downloaded")
        try:
            output = subprocess.check_output(["ls","-l"])
        except subprocess.CalledProcessError as e:
            display_msg("Exception encountered when trying to execute the command. Check the error below")
            display_msg(e)
            assert False
        else:
            display_msg(output)
            if 'Authzones.csv' in output:
                display_msg("CSV export successfull")
                assert True
            else:
                display_msg("CSV export unsuccessful")
                assert False

    @pytest.mark.run(order=319)
    def test_319_NIOS_87645_Delete_the_auth_zone(self):
        display_msg("Delete the auth zone")
        response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=nios87645.com", grid_vip=config.grid_vip)
        display_msg(response)
        ref = json.loads(response)[0]['_ref']
        del_ref = ib_NIOS.wapi_request('DELETE', object_type = ref)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_msg("FAILURE: Deleting zone failed.")
            assert False
        else:
            dns_restart_services()
            display_msg("Auth zone deletion successful")
            assert True

    @pytest.mark.run(order=320)
    def test_320_NIOS_87645_Import_the_exported_csv_file_and_check_if_no_errors_are_observed(self):
        display_msg("Import the exported CSV file and check if no errors are observed")
        dir_name = os.getcwd()
        base_filename = "Authzones.csv"
        token = common_util.generate_token_from_file(dir_name, base_filename)
        display_msg(token)
        data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
        response=json.loads(response)
        display_msg(response)
        sleep(10)
        data={"action":"START","file_name":base_filename,"on_error":"CONTINUE","operation":"CREATE","separator":"COMMA"}
        get_ref=ib_NIOS.wapi_request('GET', object_type="csvimporttask")
        display_msg(get_ref)
        get_ref=json.loads(get_ref)
        for ref in get_ref:
            if response["csv_import_task"]["import_id"]==ref["import_id"]:
                if ref["lines_failed"]==0:
                    logging.info("CSV import successful")
                    dns_restart_services()
                    assert True
                else:
                    display_msg("CSV import unsuccessful")
                    assert False

    @pytest.mark.run(order=321)
    def test_321_NIOS_87645_Delete_the_zone_and_csv_file(slef):
        display_msg("Delete the zone and csv file")
        count = 0
        display_msg("Delete the auth zone")
        response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=nios87645.com", grid_vip=config.grid_vip)
        display_msg(response)
        ref = json.loads(response)[0]['_ref']
        del_ref = ib_NIOS.wapi_request('DELETE', object_type = ref)
        display_msg(del_ref)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_msg("FAILURE: Deleting zone failed.")
        else:
            dns_restart_services()
            display_msg("Auth zone deletion successful")
            count += 1

        display_msg("Delete the exported csv file")
        path = os.getcwd() + "/Authzones.csv"
        try:
            subprocess.check_output(['rm','-rf',path])
        except subprocess.CalledProcessError as e:
            display_msg("Error encountered while deleting the csv file. Check below for more details")
            display_msg(e)
        else:
            display_msg("CSV file deleted successfully")
            count += 1

        if count == 2:
            display_msg("Cleanup successful")
            assert True
        else:
            display_msg("Cleanup unsuccessful")
            assert False

    
    @pytest.mark.run(order=322)
    def test_322_NIOS_83043_Set_the_KSK_and_ZSK_algo_to_ECDSAP256SHA256_in_DNSSEC_properties(self):
        display_msg("Set the KSK and ZSK algo to ECDSAP256SHA256 in DNSSEC properties")
        data = {"dnssec_key_params": {"ksk_algorithms":[{"algorithm": "ECDSAP256SHA256","size": 256}],"zsk_algorithms":[{"algorithm": "ECDSAP256SHA256","size": 256}]}}
        response = ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.grid_vip)
        display_msg(response)
        grid_dns_ref = json.loads(response)[0]["_ref"]
        response = ib_NIOS.wapi_request('PUT', object_type=grid_dns_ref,fields=json.dumps(data))
        display_msg(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_msg("Unable to change the KSK and ZSK algo to ECDSAP256SHA256")
            assert False
        else:
            display_msg("KSK and ZSK algo changed to ECDSAP256SHA256")
            dns_restart_services()
            assert True

        
    @pytest.mark.run(order=323)
    def test_323_NIOS_83043_Verify_KSK_and_ZSK_algo_set_to_ECDSAP256SHA256_in_DNSSEC_properties(self):
        display_msg("Verify KSK and ZSK algo set to ECDSAP256SHA256 in DNSSEC properties")
        response = ib_NIOS.wapi_request('GET', object_type="grid:dns?_return_fields=dnssec_key_params", grid_vip=config.grid_vip)
        display_msg(response)
        response = json.loads(response)
        if (response[0]["dnssec_key_params"]["ksk_algorithms"][0]["algorithm"] == "ECDSAP256SHA256" and response[0]["dnssec_key_params"]["zsk_algorithms"][0]["algorithm"] == "ECDSAP256SHA256") :
            display_msg("ECDSAP256SHA256 algorithm present")
            assert True
        else:
            display_msg("ECDSAP256SHA256 algorithm not present")
            assert False


    @pytest.mark.run(order=324)
    def test_324_NIOS_83043_Set_the_KSK_and_ZSK_algo_to_ECDSAP384SHA384_in_DNSSEC_properties(self):
        display_msg("Set the KSK and ZSK algo to ECDSAP384SHA384 in DNSSEC properties")
        data = {"dnssec_key_params": {"ksk_algorithms":[{"algorithm": "ECDSAP384SHA384","size": 256}],"zsk_algorithms":[{"algorithm": "ECDSAP384SHA384","size": 256}]}}
        response = ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.grid_vip)
        display_msg(response)
        grid_dns_ref = json.loads(response)[0]["_ref"]
        response = ib_NIOS.wapi_request('PUT', object_type=grid_dns_ref,fields=json.dumps(data))
        display_msg(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_msg("Unable to change the KSK and ZSK algo to ECDSAP384SHA384")
            assert False
        else:
            display_msg("KSK and ZSK algo changed to ECDSAP384SHA384")
            dns_restart_services()
            assert True

        
    @pytest.mark.run(order=325)
    def test_325_NIOS_83043_Verify_KSK_and_ZSK_algo_set_to_ECDSAP384SHA384_in_DNSSEC_properties(self):
        display_msg("Verify KSK and ZSK algo set to ECDSAP384SHA384 in DNSSEC properties")
        response = ib_NIOS.wapi_request('GET', object_type="grid:dns?_return_fields=dnssec_key_params", grid_vip=config.grid_vip)
        display_msg(response)
        response = json.loads(response)
        if (response[0]["dnssec_key_params"]["ksk_algorithms"][0]["algorithm"] == "ECDSAP384SHA384" and response[0]["dnssec_key_params"]["zsk_algorithms"][0]["algorithm"] == "ECDSAP384SHA384") :
            display_msg("ECDSAP384SHA384 algorithm present")
            assert True
        else:
            display_msg("ECDSAP384SHA384 algorithm not present")
            assert False

    @pytest.mark.run(order=326)
    def test_326_NIOS_83711_Check_if_we_are_not_able_to_select_RSA_MD5_algo_with_NSEC(self):
        display_msg("Check if we are not able to select RSA\MD5 algo with NSEC")
        data = {"dnssec_key_params": {"next_secure_type": "NSEC","ksk_algorithms":[{"algorithm": "RSAMD5","size": 1024}]}}
        response = ib_NIOS.wapi_request('GET', object_type="grid:dns?_return_fields=dnssec_key_params", grid_vip=config.grid_vip)
        display_msg(response)
        grid_dns_ref = json.loads(response)[0]['_ref']
        response = ib_NIOS.wapi_request('PUT', object_type=grid_dns_ref,fields=json.dumps(data))
        display_msg(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_msg("Unable to set the RSA/MD5 algo as expected")
            assert True
        else:
            display_msg("RSA/MD5 algo has been set, which is not the correct behaviour")
            assert False

    @pytest.mark.run(order=327)
    def test_327_NIOS_87135_Add_an_auth_zone(self):
        display_msg("Create an Auth zone")

        data = {"fqdn":"nios87135.com","view":"default","grid_primary":[{"name":config.grid1_master_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_msg("FAILURE: Create authoratative zone.")
            assert False
        else:
            dns_restart_services()
            display_msg("\n--------------------------------------------------------\n")
            display_msg("Validating Authoratative zone - nios87135.com")
            display_msg("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=nios87135.com", grid_vip=config.grid_vip)
            response=json.loads(response)[0]
            display_msg(response)

            if 'nios87135.com' in response['_ref']:
                display_msg(response["_ref"])
                display_msg("SUCCESS: Authoratative Zone 'nios87135.com' was created!")
                dns_restart_services()
                assert True
            else:
                display_msg("FAILURE: Authoratative Zone 'nios87135.com' creation failed")
                assert False

    @pytest.mark.run(order=328)
    def test_328_NIOS_87135_Sign_the_zone_nios87135_com(self):
        display_msg("Sign the zone nios87135.com")
        zone_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=nios87135.com", grid_vip=config.grid_vip)
        display_msg(zone_ref)
        zone_ref = json.loads(zone_ref)[0]['_ref']
        data={"buffer":"KSK","operation":"SIGN"}
        response = ib_NIOS.wapi_request('POST', object_type=zone_ref,fields=json.dumps(data),params="?_function=dnssec_operation")
        display_msg(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_msg("FAILURE: Failed to sign the zone nios87135.com.")
            assert False
        else:
            display_msg("Zone nios87135.com signed successfully")
            dns_restart_services()
            assert True

    @pytest.mark.run(order=329)
    def test_329_NIOS_87135_Validate_if_zone_signing_was_successful(self):
        display_msg("Verify if zone signing was successful")
        zone_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=nios87135.com", grid_vip=config.grid_vip)
        display_msg(zone_ref)
        zone_ref = json.loads(zone_ref)[0]['_ref']
        data = {"fqdn":"nios87135.com"}
        response = ib_NIOS.wapi_request('GET', object_type= zone_ref + "?_return_fields=is_dnssec_signed",fields=json.dumps(data))
        display_msg(response)
        if json.loads(response)["is_dnssec_signed"] == True:
            display_msg("Zone signing verification successful")
            assert True
        else:
            display_msg("Zone signing verification failed")
            assert False

    @pytest.mark.run(order=330)
    def test_330_NIOS_87315_Change_the_NSEC3_salt_length_of_the_zone_nios87315(self):
        display_msg("Change the NSEC3 salt length of zone nios87315.com")
        zone_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=nios87135.com", grid_vip=config.grid_vip)
        for zone in json.loads(zone_ref):
            if 'nios87135.com' in zone['_ref']:
                display_msg(zone)
                zone_ref = zone['_ref']
                break
        data = {"dnssec_key_params":{"nsec3_salt_min_length": 2,"nsec3_salt_max_length": 14}}
        response = ib_NIOS.wapi_request('PUT', object_type=zone_ref,fields=json.dumps(data))
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_msg("Error encountered while changing NSEC3 salt length")
            assert False
        else:
            display_msg("NSEC3 salt length change successfull, proceeding with DNS restart")
            dns_restart_services()
            display_msg("DNS service restart successfull")
            assert True

    @pytest.mark.run(order=331)
    def test_331_NIOS_87315_Verify_the_NSEC3_salt_length_change(self):
        display_msg("Change the NSEC3 salt length of zone nios87315.com")
        zone_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?_return_fields=dnssec_key_params", grid_vip=config.grid_vip)
        for zone in json.loads(zone_ref):
            if 'nios87135.com' in zone['_ref']:
                display_msg(zone)
                zone_ref = zone
                break
        if zone_ref["dnssec_key_params"]["nsec3_salt_min_length"] == 2 and zone_ref["dnssec_key_params"]["nsec3_salt_max_length"] == 14:
            display_msg("Changing NSEC3 salt length successful")
            assert True
        else:
            display_msg("NSEC3 salt length change failed")
            assert False

    @pytest.mark.run(order=332)
    def test_332_NIOS_87315_Delete_the_auth_zone(self):
        response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=nios87135.com", grid_vip=config.grid_vip)
        display_msg(response)
        ref = json.loads(response)[0]['_ref']
        del_ref = ib_NIOS.wapi_request('DELETE', object_type = ref)
        display_msg(del_ref)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_msg("FAILURE: Deleting zone failed.")
            assert False
        else:
            dns_restart_services()
            display_msg("Auth zone deletion successful")
            assert True

    @pytest.mark.run(order=333)
    def test_333_NIOS_86900_Add_auth_zone(self):
        display_msg("Create an Auth zone")

        data = {"fqdn":"nios86900.com","view":"default","grid_primary":[{"name":config.grid1_master_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_msg("FAILURE: Create authoratative zone.")
            assert False
        else:
            dns_restart_services()
            display_msg("\n--------------------------------------------------------\n")
            display_msg("Validating Authoratative zone - nios86900.com")
            display_msg("\n--------------------------------------------------------\n")

            response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=nios86900.com", grid_vip=config.grid_vip)
            response=json.loads(response)[0]
            display_msg(response)

            if 'nios86900.com' in response['_ref']:
                display_msg(response["_ref"])
                display_msg("SUCCESS: Authoratative Zone 'nios86900.com' was created!")
                dns_restart_services()
                assert True
            else:
                display_msg("FAILURE: Authoratative Zone 'nios86900.com' creation failed")
                assert False

    @pytest.mark.run(order=334)
    def test_334_NIOS_86900_Add_RR_of_type_APL_and_check_no_error_logs_are_observed(self):
        display_msg("Add RR of type APL and check no error logs are observed")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        data={"name": "apl.nios86900.com","record_type": "APL","subfield_values": [{"field_type": "P","field_value": "1:224.0.0.0/4 2:ff00::/8","include_length": "NONE"}],"view": "default"}
        response = ib_NIOS.wapi_request('POST', object_type="record:unknown",fields=json.dumps(data))
        display_msg(response)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_msg("Error encountered while trying to add APL record")
            assert False
        sleep(10)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        count = 0
        if logv(".*ERROR com.infoblox.widget.dialog.function.FunctionImpl:126 - inheritance invocation target exception.*","/infoblox/var/infoblox.log",config.grid_vip):
            count +=1
            display_msg("Encountered error ERROR com.infoblox.widget.dialog.function.FunctionImpl:126 - inheritance invocation target exception")  

        if logv(".*Missing: record_rdata_hash.*","/infoblox/var/infoblox.log",config.grid_vip):
            count +=1
            display_msg("Encountered error Missing: record_rdata_hash")

        if count == 0:
            display_msg("No error logs encountered while adding APL record")
            assert True
        else:
            assert False

    @pytest.mark.run(order=335)
    def test_335_NIOS_86900_Delete_the_auth_zone(self):
        response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=nios86900.com", grid_vip=config.grid_vip)
        display_msg(response)
        ref = json.loads(response)[0]['_ref']
        del_ref = ib_NIOS.wapi_request('DELETE', object_type = ref)
        display_msg(del_ref)
        if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
            display_msg("FAILURE: Deleting zone failed.")
            assert False
        else:
            dns_restart_services()
            display_msg("Auth zone deletion successful")
            assert True


    @pytest.mark.run(order=336)
    def test_336_NIOS_86741_Executing_CLI_command__rotate_log_syslog(self):
        display_msg("\n========================================================\n")
        display_msg("Executing CLI command 'rotate log syslog'")
        display_msg("\n========================================================\n")

        try:
            child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect("password:")
            child.sendline("infoblox")
            child.expect("Infoblox >")
            child.sendline("rotate log syslog")
            child.expect("The selected log file has been rotated to syslog.0.gz")
            child.expect("Infoblox >")
            print("SUCCESS: ")
            assert True

        except Exception as e:
            print(e)
            child.close()
            print("FAILURE: ")
            assert False

        finally:
            child.close()

    # Login as root and check if /var/log/syslog is present

    @pytest.mark.run(order=337)
    def test_337_NIOS_86741_Checking_for_syslog(self):
        display_msg("\n========================================================\n")
        display_msg("Logging in as root and checking if syslog folder is peresent ")
        display_msg("\n========================================================\n")

        try:
            child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect(".*#")
            child.sendline("ls -ltr /var/log/syslog* > output.txt")
            child.expect(".*#")
            os.system("sshpass -p 'infoblox' scp -pr root@"+config.grid_vip+":output.txt .")
            
            with open('output.txt') as file:
                output=file.readlines()
                print(type(output))
                if '/var/log/syslog\n' in output[-1]:
                    print("SUCCESS: ")
                    assert True
                else:
                    print("FAILURE: ")
                    assert False

        except Exception as e:
            print(e)
            child.close()
            print("FAILURE: ")
            assert False

        finally:
            child.close()

    # Clean Up

    @pytest.mark.run(order=338)
    def test_338_NIOS_86741_cleanup(self):
        display_msg("\n============================================\n")
        display_msg("CLEANUP: Reverting back to original setup...")
        display_msg("\n============================================\n")

        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect(".*#")
        child.sendline("rm -rf output.txt")
        child.expect(".*#")
        os.system("rm -rf output.txt")

    ###################### NIOS_86540 ###################################
    # Login as admin and execute CLI command 'rotate log syslog'

    @pytest.mark.run(order=339)
    def test_339_NIOS_86540_Stop_DHCP_service_on_members(self):
        
        display_msg("\n========================================================\n")
        display_msg("Stop DHCP service on members")
        display_msg("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties?_return_fields=enable_dhcp", grid_vip=config.grid_vip)
        res = json.loads(get_ref)
        for i in res:
            data = {"enable_dhcp": False}
            response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties?_return_fields=enable_dhcp", grid_vip=config.grid_vip)
            display_msg(get_ref)

            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    display_msg("FAILURE: Couldnt stop DHCP service on one or more members")
                    assert False
                break
            else:
                display_msg("SUCCESS: DHCP service stopped on all members")
                assert True
                break

    @pytest.mark.run(order=340)
    def test_340_NIOS_86540_Start_DNS_service_on_members(self):
        display_msg("\n========================================================\n")
        display_msg("Start DNS service on members")
        display_msg("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=enable_dns", grid_vip=config.grid_vip)
        res = json.loads(get_ref)
        for i in res:
            if config.grid1_member1_fqdn in i['_ref'] or config.grid1_member2_fqdn in i['_ref']:
                data = {"enable_dns": True}
                response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=enable_dns", grid_vip=config.grid_vip)
                display_msg(get_ref)

                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        display_msg("FAILURE: Couldnt start DNS service on one or more members")
                        assert False
                    break
                else:
                    display_msg("SUCCESS: DNS service started on all members")
                    assert True
                    break
            
            else:
                continue
      
        
        
    @pytest.mark.run(order=341)
    def test_341_NIOS_86540_Start_DCS_service_on_members(self):
        display_msg("\n========================================================\n")
        display_msg("Start DCA service on members")
        display_msg("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=enable_dns_cache_acceleration", grid_vip=config.grid_vip)
        res = json.loads(get_ref)
        for i in res:
            if config.grid1_member1_fqdn in i['_ref'] or config.grid1_member2_fqdn in i['_ref']:
                data = {"enable_dns_cache_acceleration": True}
                response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=enable_dns_cache_acceleration", grid_vip=config.grid_vip)
                display_msg(get_ref)

                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        display_msg("FAILURE: Couldnt start DCA service on one or more members")
                        assert False
                    break
                else:
                    display_msg("SUCCESS: DCA service started on all members")
                    assert True
                    break
            
            else:
                continue


    @pytest.mark.run(order=342)
    def test_342_NIOS_86540_Start_TP_service_on_members(self):
        display_msg("\n========================================================\n")
        display_msg("Start TP service on members")
        display_msg("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection?_return_fields=enable_service", grid_vip=config.grid_vip)
        res = json.loads(get_ref)
        for i in res:
            if config.grid1_member1_fqdn in i['_ref'] or config.grid1_member2_fqdn in i['_ref']:
                data = {"enable_service": True}
                response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection?_return_fields=enable_service", grid_vip=config.grid_vip)
                display_msg(get_ref)

                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        display_msg("FAILURE: Couldnt start TP service on one or more members")
                        assert False
                    break
                else:
                    display_msg("SUCCESS: TP service started on all members")
                    assert True
                    break
            
            else:
                continue


    @pytest.mark.run(order=343)
    def test_343_NIOS_86540_Enable_Parental_control_and_add_site_with_members(self):
        display_msg("\n========================================================\n")
        display_msg("Enable Parental control and add a site with members")
        display_msg("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber?_return_fields=enable_parental_control", grid_vip=config.grid_vip)
        res = json.loads(get_ref)[0]

        data = {"enable_parental_control": True, "cat_acctname": "vvk", "cat_update_frequency": 24, "category_url": "https://dl.zvelo.com/", "pc_zone_name": "vvk"}
        response = ib_NIOS.wapi_request('PUT', ref=res['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
        get_ref = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscriber?_return_fields=enable_parental_control", grid_vip=config.grid_vip)
        display_msg(get_ref)

        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("FAILURE: Could not enable Parental control")
                assert False
            
        else:
            display_msg("SUCCESS: Parental control enabled successfully\n")

        
        ### Adding site with members ###
        data = {"name": "vvk_site", "members":[{"name":config.grid1_member1_fqdn},{"name":config.grid1_member2_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        get_ref = ib_NIOS.wapi_request('GET', object_type="parentalcontrol:subscribersite?_return_fields=members,name", grid_vip=config.grid_vip)
        display_msg(get_ref)

        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                display_msg("FAILURE: Could not add Parental control site")
                assert False
            
        else:
            display_msg("SUCCESS: Parental control site added successfully with members")
            assert True
          
    @pytest.mark.run(order=344)
    def test_344_NIOS_86540_Restarting_services(self):
        display_msg("\n========================================================\n")
        display_msg("Restarting Services...")
        display_msg("\n========================================================\n")

        grid = ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(35)
        display_msg("Restart completed successfully")

    @pytest.mark.run(order=345)
    def test_345_NIOS_86540_Validating_synopsis_for__set_subscriber_secure_data(self):
        display_msg("\n========================================================\n")
        display_msg("Executing CLI command 'set subscriber_secure_data' and validating 'Synopsis' for 'set subscriber_secure_data'")
        display_msg("\n========================================================\n")

        try:
            child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid1_member1_vip)
            child.logfile=sys.stdout
            child.expect("password:")
            child.sendline("infoblox")
            child.expect("Infoblox >")
            child.sendline("set subscriber_secure_data ?")
            child.expect("Infoblox >")
            output=child.before
            
            wrong_synopsis = "set subscriber_secure_data bypass <on|off> [grid | site <\"site-name\">]"
            wrong_description = "Use \"set subscriber_secure_data bypass <on|off> [grid | site <\"site-name\">]\" to configure bypass subscriber service policies on entire grid, all members of the given site or local member only"
            
            correct_synopsis = "set subscriber_secure_data bypass <on|off>"
            correct_description = "Use \"set subscriber_secure_data bypass <on | off>\" to configure bypass subscriber service policies on the given member"
            
            if (wrong_synopsis in output) or (wrong_description in output):
                print("FAILURE: Something went wrong...please check and reopen the bug.")
                assert False
                
            elif (correct_synopsis in output) and (correct_description in output):
                print("SUCCESS: Synopsis and description for 'subscriber_secure_data bypass' is correct.")
                assert True

        except Exception as e:
            print(e)
            child.close()
            print("FAILURE: Something went wrong...please check and reopen the bug.")
            assert False

        finally:
            child.close()

    @pytest.mark.run(order=346)
    def test_346_NIOS_86540_Validating_synopsis_for__set_subscriber_secure_data_bypass(self):
        display_msg("\n========================================================\n")
        display_msg("Executing CLI command 'show subscriber_secure_data' and validating 'Synopsis' for 'show subscriber_secure_data bypass'")
        display_msg("\n========================================================\n")

        try:
            child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid1_member1_vip)
            child.logfile=sys.stdout
            child.expect("password:")
            child.sendline("infoblox")
            child.expect("Infoblox >")
            child.sendline("set subscriber_secure_data ?")
            child.expect("Infoblox >")
            output=child.before
            
            wrong_synopsis = "show subscriber_secure_data bypass [grid | site] [\"site-name\"]"
            wrong_description = "EX: show subscriber_secure_data bypass site \"Site1\""
            
            correct_synopsis = "show subscriber_secure_data bypass"
            correct_description = "EX: show subscriber_secure_data bypass"
            
            if (wrong_synopsis in output) or (wrong_description in output):
                print("FAILURE: Something went wrong...please check and reopen the bug.")
                assert False
                
            elif (correct_synopsis in output) and (correct_description in output):
                print("SUCCESS: Synopsis and description for 'subscriber_secure_data bypass' is correct.")
                assert True

        except Exception as e:
            print(e)
            child.close()
            print("FAILURE: Something went wrong...please check and reopen the bug.")
            assert False

        finally:
            child.close()

    @pytest.mark.run(order=348)
    def test_348_NIOS_87882_Create_EA_zone_Ipv4Nw_EAInheritance_Enabled(self):
        display_msg("Create EA attribute with zone and ipv4 nw with EA_Inheritance enabled")
        data = {"name": "st1", "type": "STRING","max": 10,"min": 1,"flags": "I","allowed_object_types": [ "BaseZone","Network"]}
        post_ref = ib_NIOS.wapi_request('POST', object_type="extensibleattributedef",  fields=json.dumps(data),grid_vip=config.grid_vip)
        display_msg(post_ref)
        if type(post_ref)== tuple:
            display_msg("Creating EA attribute failed")
            assert False
        else:
            display_msg("Creation of EA Attribute success")
            assert True


    @pytest.mark.run(order=349)
    def test_349_NIOS_87882_Create_Auth_zone_with_EA_Attribute_Enabled(self):
        display_msg("Create auth_zone with EA  Attribute enabled")
        data={"extattrs": {"st1": {"value": "15"}},"fqdn": "test2.com","grid_primary": [{"name":"config.grid_fqdn"}]}
        post_ref = ib_NIOS.wapi_request('POST', object_type="zone_auth",  fields=json.dumps(data),grid_vip=config.grid_vip)
        display_msg(post_ref)
        if type(post_ref)== tuple:
            display_msg("Creating auth_zone  with EA Attribute enabled failed")
            assert False
        else:
            display_msg("Creating auth_zone  with EA Attribute enabled success")
            assert True
    
    @pytest.mark.run(order=350)
    def test_350_test_NIOS_82456_Create_authzone_Unknown_record_type_TYPE65535_withSubfields(self):
       # display_msg("Create Unknwon record TYPE65535 with subfields")
       # data= {"name": "p3.com"}
        display_msg("Create auth zone")

        data = {"fqdn":"p3.com","view":"default","grid_primary":[{"name":config.grid1_master_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        if type(response)== tuple:
            display_msg("Creating auth_zone Failed")
            assert False
        else:
            display_msg("Creating auth_zone  Success")
            dns_restart_services()
            assert True
    @pytest.mark.run(order=351)
    def test_351_test_NIOS_82456_Create_authzone_Unknown_record_type_TYPE65535_withSubfields(self):
        display_msg("Create Unknwon record TYPE65535 with subfields")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        data={"name": "uk1.p3.com","record_type": "TYPE65535","subfield_values": [ {"field_type": "H","field_value": "1100","include_length": "8_BIT"},{"field_type": "X","field_value": "abcd","include_length":"8_BIT"},{"field_type": "S","field_value": "12","include_length": "NONE"},{"field_type": "I","field_value": "12","include_length": "NONE"},{"field_type": "6","field_value": "1234::1","include_length": "NONE"}]}
        response=ib_NIOS.wapi_request('POST', object_type="record:unknown", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        if type(response)== tuple:
            display_msg("Creating Unknown record with TYPE65535  Failed")
            assert False
        else:
            display_msg("Creating Unknown record with TYPE65535  Success")
            assert True

    @pytest.mark.run(order=352)
    def test_352_test_NIOS_82456_Validate_Infoblox_log_for_errors(self):
        display_msg("Validate Infoblox.log for errors ")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log1=logv(".*Required Value(s) Missing: record_rdata_hash.*","/infoblox/var/infoblox.log",config.grid_vip)
        if log1 :
            display_msg("Error log message found")
            assert False
        else:
            display_msg("No Error logs found")
            assert True 
    

    @pytest.mark.run(order=353)
    def test_353_test_NIOS_84643_enable_dns(self):
          logging.info("starting DNS service")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
          logging.info(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print (ref1)
          data = {"enable_dns": True}
          response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
          sleep(5)
          logging.info(response)
          print (response)
          print("Successfully started DNS service")
    
    @pytest.mark.run(order=354)
    def test_354_test_NIOS_84643_Create_Auth_zone(self):
        display_msg("Create auth zone with member assignment")

        data = {"fqdn":"test_nx1.com","view":"default","grid_primary":[{"name":config.grid1_master_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth",  fields=json.dumps(data),grid_vip=config.grid_vip)
        display_msg(response)
        if response[0]==400 or response[0]==401 or response[0]==402:

            assert False
        else:

            assert True

    

    @pytest.mark.run(order=355)
    def test_355_NIOS_84643_Validate_Zone_Signing(self):
        display_msg("Validate Zone Signing")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
        res=json.loads(get_ref)
        display_msg(res)
        sleep(5)
        for zone  in res:
            if  zone['fqdn']=='test_nx1.com':
                zone_auth_ref=zone['_ref']
        signzone_ref = ib_NIOS.wapi_request('POST', ref=str(zone_auth_ref), params='?_function=dnssec_operation', fields=json.dumps({"operation":"SIGN"}))
        logging.info(signzone_ref)
        if bool(re.match("{}",str(signzone_ref))):
            logging.info("Zone signed successfully")
            dns_restart_services()
        else:
            raise Exception("Zone signing unsuccessfull")

    
    @pytest.mark.run(order=356)
    def test_356_NIOS_84643_Validate_if_core_files_were_generated_after_zone_signing_operation(self):
        display_msg("Validate if cores were generated after the dig operation")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip,timeout=300)
        child.expect("bash-5.0#")
        child.sendline("ls -ltr /storage/cores")
        child.expect("bash-5.0#")
        output = child.before
        print(output)
        child.close()
        if('core.dnssec-signzone.SIGABRT' in output):
            display_msg("Core files have been generated")
            assert False
        else:
            display_msg("Core file have not been generated")
            assert True

    @pytest.mark.run(order=357)
    def test_357_test_NIOS_84008_enable_dns(self):
          logging.info("starting DNS service")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
          logging.info(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print (ref1)
          data = {"enable_dns": True}
          response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
          sleep(5)
          logging.info(response)
          print (response)
          print("Successfully started DNS service")


    @pytest.mark.run(order=358)
    def test_358_test_NIOS_84008_Create_Auth_zone(self):
        display_msg("Create auth zone with member assignment")

        data = {"fqdn":"test_nx2.com","view":"default","grid_primary":[{"name":config.grid1_master_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth",  fields=json.dumps(data),grid_vip=config.grid_vip)
        display_msg(response)
        if response[0]==400 or response[0]==401 or response[0]==402:

            assert False
        else:

            assert True


    @pytest.mark.run(order=359)
    def test_359_NIOS_84008_Validate_Zone_Signing(self):
        display_msg("Validate Zone Signing")
        log("start","/var/log/syslog",config.grid_vip)
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
        res=json.loads(get_ref)
        display_msg(res)
        sleep(5)
        for zone  in res:
            if  zone['fqdn']=='test_nx2.com':
                zone_auth_ref=zone['_ref']
        signzone_ref = ib_NIOS.wapi_request('POST', ref=str(zone_auth_ref), params='?_function=dnssec_operation', fields=json.dumps({"operation":"SIGN"}))
        logging.info(signzone_ref)
        if bool(re.match("{}",str(signzone_ref))):
            logging.info("Zone signed successfully")
            dns_restart_services()
        else:
            raise Exception("Zone signing unsuccessfull")



    @pytest.mark.run(order=360)
    def test_360_test_NIOS_84008_Validate_sys_log_for_errors(self):
        display_msg("Validate var/log/syslog for errors ")
        log("stop","/var/log/syslog",config.grid_vip)
        log1=logv("malformed transaction: serial number did not increase apply_txn_zrq_items:dns_journal_write_transaction -> unexpected error ","/var/log/syslog",config.grid_vip)
        if log1 :
            display_msg("Error log message found")
            assert False
        else:
            display_msg("No Error logs found")
            assert True


    @pytest.mark.run(order=361)
    def test_361_test_NIOS_84008_enable_dns(self):
          logging.info("starting DNS service")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
          logging.info(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print (ref1)
          data = {"enable_dns": True}
          response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
          sleep(5)
          logging.info(response)
          print (response)
          print("Successfully started DNS service")


    @pytest.mark.run(order=362)
    def test_362_test_NIOS_84008_Create_Auth_zone_with_Member_asGrid_Primary(self):
        display_msg("Create auth zone with member as Grid Primary")

        data = {"fqdn":"test_nx3.com","view":"default","grid_primary":[{"name":config.grid1_member1_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth",  fields=json.dumps(data),grid_vip=config.grid_vip)
        display_msg(response)
        if response[0]==400 or response[0]==401 or response[0]==402:

            assert False
        else:

            assert True


    @pytest.mark.run(order=363)
    def test_363_NIOS_84008_Validate_Zone_Signing_With_Member_asGridPrimary(self):
        display_msg("Validate Zone Signing with Member as Grid Primary")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
        res=json.loads(get_ref)
        display_msg(res)
        sleep(5)
        for zone  in res:
            if  zone['fqdn']=='test_nx3.com':
                zone_auth_ref=zone['_ref']
        signzone_ref = ib_NIOS.wapi_request('POST', ref=str(zone_auth_ref), params='?_function=dnssec_operation', fields=json.dumps({"operation":"SIGN"}))
        logging.info(signzone_ref)
        if bool(re.match("{}",str(signzone_ref))):
            logging.info("Zone signed successfully")
            dns_restart_services()
        else:
            raise Exception("Zone signing unsuccessfull")

    @pytest.mark.run(order=364)
    def test_364_test_NIOS_84008_enable_dns(self):
          logging.info("starting DNS service")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
          logging.info(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print (ref1)
          data = {"enable_dns": True}
          response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
          sleep(5)
          logging.info(response)
          print (response)
          print("Successfully started DNS service")


    @pytest.mark.run(order=365)
    def test_365_test_NIOS_84008_Create_Auth_zone_with_Master_asGrid_Primary_and_Member_asGridSecondary(self):
        display_msg("Create auth zone with master as Grid Primary and Member as grid secondary")

        data = {"fqdn":"test_nx4.com","view":"default","grid_primary":[{"name":config.grid1_master_fqdn}],"grid_secondaries":[{"name":config.grid1_member1_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth",  fields=json.dumps(data),grid_vip=config.grid_vip)
        display_msg(response)
        if response[0]==400 or response[0]==401 or response[0]==402:

            assert False
        else:

            assert True

    @pytest.mark.run(order=366)
    def test_366_NIOS_84008_Validate_Zone_Signing_With_Master_asGridPrimary_and_Member_as_Grid_Secondary(self):
        display_msg("Validate Zone Signing with Master as Grid Primary and Member as Grid Secondary")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
        res=json.loads(get_ref)
        display_msg(res)
        sleep(5)
        for zone  in res:
            if  zone['fqdn']=='test_nx4.com':
                zone_auth_ref=zone['_ref']
        signzone_ref = ib_NIOS.wapi_request('POST', ref=str(zone_auth_ref), params='?_function=dnssec_operation', fields=json.dumps({"operation":"SIGN"}))
        logging.info(signzone_ref)
        if bool(re.match("{}",str(signzone_ref))):
            logging.info("Zone signed successfully")
            dns_restart_services()
        else:
            raise Exception("Zone signing unsuccessfull")


    @pytest.mark.run(order=367)
    def test_367_test_NIOS_83040_enable_dns(self):
          logging.info("starting DNS service")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
          logging.info(get_ref)
          res = json.loads(get_ref)
          for ref in res:
             if config.grid1_master_fqdn==ref['host_name']:
                    ref1 = json.loads(get_ref)[0]['_ref']
                    data = {"enable_dns": True}
                    response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                    sleep(5)
                    logging.info(response)
                    print (response)
                    print("Successfully started DNS service")
             elif config.grid1_member1_fqdn==ref['host_name']:
                    ref2 = json.loads(get_ref)[1]['_ref']
                    print (ref2)
                    data = {"enable_dns": True}
                    response = ib_NIOS.wapi_request('PUT',ref=ref2,fields=json.dumps(data), grid_vip=config.grid_vip)
                    sleep(5)
                    logging.info(response)
                    print (response)
                    print("Successfully started DNS service")


    @pytest.mark.run(order=368)
    def test_368_test_NIOS_83040_Create_Auth_zone_with_Member_asGrid_Primary_and_Master_asGridSecondary(self):
        display_msg("Create auth zone with member as Grid Primary and Master as Grid Secondary")

        data = {"fqdn":"test_nx5.com","view":"default","grid_primary":[{"name":config.grid1_member1_fqdn}],"grid_secondaries":[{"name":config.grid1_master_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth",  fields=json.dumps(data),grid_vip=config.grid_vip)
        display_msg(response)
        if response[0]==400 or response[0]==401 or response[0]==402:

            assert False
        else:
            assert True


    @pytest.mark.run(order=369)
    def test_369_NIOS_NIOS_83040_Validate_Zone_Signing_With_Member_asGridPrimary_and_GridMasterr_as_Grid_Secondary(self):
        display_msg("Validate Zone Signing with Member as Grid Primary and Master as Grid Secondary")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
        res=json.loads(get_ref)
        display_msg(res)
        sleep(5)
        for zone  in res:
            if  zone['fqdn']=='test_nx5.com':
                zone_auth_ref=zone['_ref']
        signzone_ref = ib_NIOS.wapi_request('POST', ref=str(zone_auth_ref), params='?_function=dnssec_operation', fields=json.dumps({"operation":"SIGN"}))
        logging.info(signzone_ref)
        if bool(re.match("{}",str(signzone_ref))):
            logging.info("Zone signed successfully")
            dns_restart_services()
        else:
            raise Exception("Zone signing unsuccessfull")


    @pytest.mark.run(order=370)
    def test_370_test_NIOS_83040_Validate_Infoblox_log_for_errors(self):
        display_msg("Validate Infoblox.log for errors ")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log1=logv("TypeError: ord() expected string of length 1, but int found","/infoblox/var/infoblox.log",config.grid_vip)
        if log1 :
            display_msg("Error log message found")
            assert False
        else:
            display_msg("No Error logs found")
            assert True


    @pytest.mark.run(order=371)
    def test_371_test_NIOS_82452_Create_authzone_Unknown_record_type_NULL_withSubfields(self):
        display_msg("Create auth zone")

        data = {"fqdn":"test_nx6.com","view":"default","grid_primary":[{"name":config.grid1_master_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        if type(response)== tuple:
            display_msg("Creating auth_zone Failed")
            assert False
        else:
            display_msg("Creating auth_zone  Success")
            dns_restart_services()
            assert True



    @pytest.mark.run(order=372)
    def test_372_test_NIOS_82452_Create_authzone_Unknown_record_type_NULL_withSubfields(self):
       # display_msg("Create Unknwon record TYPE65535 with subfields")
       # data= {"name": "p3.com"}
        display_msg("Create auth zone")

        data = {"fqdn":"p3.com","view":"default","grid_primary":[{"name":config.grid1_master_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        if type(response)== tuple:
            display_msg("Creating auth_zone Failed")
            assert False
        else:
            display_msg("Creating auth_zone  Success")
            dns_restart_services()
            assert True



    @pytest.mark.run(order=373)
    def test_373_test_NIOS_82452_Create_authzone_Unknown_record_type_TYPE65535_withSubfields(self):
        display_msg("Create Unknwon record TYPENULL with subfields")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        data={"name": "uk1.p3.com","record_type": "NULL","subfield_values":[{"field_type": "H","field_value": "1100","include_length": "8_BIT"},{"field_type": "X","field_value": "abcd","include_length": "8_BIT"},{"field_type": "S","field_value": "12","include_length": "NONE"},{"field_type": "I","field_value":"234","include_length": "NONE"},{"field_type": "4","field_value": "1.2.3.4","include_length": "NONE"},{"field_type": "B","field_value": "1","include_length": "NONE"},{"field_type": "N","field_value": "a.com","include_length": "NONE"},{"field_type": "T","field_value": "sss","include_length": "8_BIT"},{"field_type": "6","field_value": "1234::1","include_length": "NONE"}]}
        response=ib_NIOS.wapi_request('POST', object_type="record:unknown", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        if type(response)== tuple:
            display_msg("Creating Unknown record with TYPENULL  Failed")
            assert False
        else:
            display_msg("Creating Unknown record with TYPENULL  Success")
            assert True




    @pytest.mark.run(order=374)
    def test_374_test_NIOS_82452_Validate_Infoblox_log_for_errors(self):
        display_msg("Validate Infoblox.log for errors ")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log1=logv(".*Required Value(s) Missing: record_rdata_hash.*","/infoblox/var/infoblox.log",config.grid_vip)
        if log1 :
            display_msg("Error log message found")
            assert False
        else:
            display_msg("No Error logs found")
            assert True



    @pytest.mark.run(order=375)
    def test_375_test_NIOS_82227_enable_dns(self):
          logging.info("starting DNS service")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
          logging.info(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          print (ref1)
          data = {"enable_dns": True}
          response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
          sleep(5)
          logging.info(response)
          print (response)
          print("Successfully started DNS service")


    @pytest.mark.run(order=376)
    def test_376_test_NIOS_82227_Create_Auth_zone(self):
        display_msg("Create auth zone with member assignment")

        data = {"fqdn":"test.com","view":"default","grid_primary":[{"name":config.grid1_master_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth",  fields=json.dumps(data),grid_vip=config.grid_vip)
        display_msg(response)
        if response[0]==400 or response[0]==401 or response[0]==402:

            assert False
        else:

            assert True

    @pytest.mark.run(order=377)
    def test_377_NIOS_82227_ZoneSigning(self):
        display_msg("Validate Zone Signing")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
        res=json.loads(get_ref)
        display_msg(res)
        sleep(5)
        for zone  in res:
            if  zone['fqdn']=='test_nx7.com':
                zone_auth_ref=zone['_ref']
        signzone_ref = ib_NIOS.wapi_request('POST', ref=str(zone_auth_ref), params='?_function=dnssec_operation', fields=json.dumps({"operation":"SIGN"}))
        logging.info(signzone_ref)
        if bool(re.match("{}",str(signzone_ref))):
            logging.info("Zone Signing is  success")
            dns_restart_services()
        else:
            raise Exception("Zone Signing  is  unsuccessful")


    @pytest.mark.run(order=378)
    def test_378_NIOS_82227_ROLLOVER_ZSK_(self):
                logging.info("ROLLOVER_ZSK for the signed zone")
                data = {"fqdn":"test_nx7.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"operation":"ROLLOVER_ZSK"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                print("Rollover ZSK for signed zone is completed`")
                dns_restart_services()

   
    @pytest.mark.run(order=379)
    def test_379_NIOS_82227_ZoneSigning(self):
        display_msg("Validate Zone Signing")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
        res=json.loads(get_ref)
        display_msg(res)
        sleep(5)
        for zone  in res:
            if  zone['fqdn']=='test_nx7.com':
                zone_auth_ref=zone['_ref']
        signzone_ref = ib_NIOS.wapi_request('POST', ref=str(zone_auth_ref), params='?_function=dnssec_operation', fields=json.dumps({"operation":"SIGN"}))
        logging.info(signzone_ref)
        if bool(re.match("{}",str(signzone_ref))):
            logging.info("Zone Signing is  success")
            dns_restart_services()
        else:
            raise Exception("Zone Signing  is  unsuccessful")



    @pytest.mark.run(order=380)
    def test_380_NIOS_81826_Change_grid_dns(self):
                logging.info("Change grid:dns properties  Allow Updates to allow any")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.grid_vip)
                res=json.loads(get_ref)
                print ("###########",res[0]['_ref'])
                data={"allow_update": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}]}
                response = ib_NIOS.wapi_request('PUT', object_type=res[0]['_ref'],fields=json.dumps(data))
                print(response)
                for read in response:
                        assert True
                print("Grid:DNS Properties Allow updates is set to Allow Any")
                dns_restart_services()


    @pytest.mark.run(order=381)
    def test_381_test_NIOS_81826__Create_authzone(self):
        display_msg("Create auth zone")

        data = {"fqdn":"test_nx7.com","view":"default","grid_primary":[{"name":config.grid1_master_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        if type(response)== tuple:
            display_msg("Creating auth_zone Failed")
            assert False
        else:
            display_msg("Creating auth_zone  Success")
            dns_restart_services()

    @pytest.mark.run(order=382)
    def test_382_NIOS_81826_Create_NSUpdate_RR_Record(self):
        log("start","/var/log/syslog",config.grid_vip)
        display_msg("Create  RR Record through ns update")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip,timeout=300)
        child.expect("bash-5.0#")
        child.sendline("nsupdate")
        child.sendline("server "+config.grid_vip)
        child.sendline("update add test_nx7.com 111 A 5.5.5.5")
        child.sendline("send")
        child.sendline("quit")
        child.expect("bash-5.0#")
        output = child.before
        print(output)
        child.close()
        if('-' in output):
            display_msg("Record creation is success through nsupdate")
            assert True
        else:
            display_msg("Record creation is failed through nsupdate")
            assert False


    @pytest.mark.run(order=383)
    def test_383_NIOS_81826_Validate_sys_log_for_errors(self):
        display_msg("Validate var/log/syslog for errors ")
        log("stop","/var/log/syslog",config.grid_vip)
        log1=logv("test_nx7.com IN SOA - "+config.grid_vip + "ajith.test.com IN SOA response: NXDOMAIN +A","/var/log/syslog",config.grid_vip)
        if log1 :
            display_msg("Error log message found")
            assert False
        else:
            display_msg("No Error logs found")
            assert True



    @pytest.mark.run(order=384)
    def test_384_test_NIOS_81823_Create_Auth_zone_Import_Records_from_grid2_to_grid1_enable_Zone_Transfer(self):
        display_msg("Create auth zone with member assignment")

        data = {"fqdn":"test_nx7.com","view":"default","grid_primary":[{"name":config.grid1_master_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth",  fields=json.dumps(data),grid_vip=config.grid_vip)
        display_msg(response)
        if response[0]==400 or response[0]==401 or response[0]==402:

            assert False
        else:

            assert True


    @pytest.mark.run(order=385)
    def test_385_NIOS_81823_Import_Records_from_grid2_to_grid1_enable_Zone_Transfer(self):
                logging.info("Change grid:dns properties  Zone Transfer to allow any")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.grid_vip)
                res=json.loads(get_ref)
                print ("###########",res[0]['_ref'])
                data={"allow_transfer": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}]}
                response = ib_NIOS.wapi_request('PUT', object_type=res[0]['_ref'],fields=json.dumps(data))
                print(response)
                for read in response:
                        assert True
                print("Grid:DNS Properties Allow transfer is set to Allow Any")
                dns_restart_services()


    @pytest.mark.run(order=386)
    def test_386_NIOS_81823_ImportRecords_From_grid2_to_grid1(self):
                log("start","/var/log/syslog",config.grid_vip)
                logging.info("Copying records from grid2 to grid1")
                data={"import_from": config.grid2_master_vip}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
                response=json.loads(get_ref)
                for res in response:
                    if res['fqdn']=="test_nx7.com":
                        ref_zone=res['_ref']
                res=json.loads(get_ref)
                print ("###########",ref_zone)
                response2 = ib_NIOS.wapi_request('PUT', object_type=ref_zone,fields=json.dumps(data))
                print(response2)
                for read in response:
                        assert True
                print("Import Grid Records success from grid2 to grid1")
                dns_restart_services()


    @pytest.mark.run(order=387)
    def test_387_NIOS_81823_Validate_sys_log_for_errors(self):
        display_msg("Validate var/log/syslog for errors ")
        log("stop","/var/log/syslog",config.grid_vip)
        log1=logv("ssindex.c:9274 __xxx_get_any_rr_by_zone_and_name_internal(): not found ssindex.c:9413 __xxx_get_any_rr_by_zone_and_display_name(): not found","/var/log/syslog",config.grid_vip)
        if log1 :
            display_msg("Error log message found")
            assert False
        else:
            display_msg("No Error logs found")
            assert True



    @pytest.mark.run(order=388)
    def test_388_test_NIOS_81656_Create_Auth_zone_Import_Records_from_grid2_to_grid1_enable_Zone_Transfer(self):
        display_msg("Create auth zone with member assignment")

        data = {"fqdn":"test_nx8.com","view":"default","grid_primary":[{"name":config.grid1_master_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth",  fields=json.dumps(data),grid_vip=config.grid_vip)
        display_msg(response)
        if response[0]==400 or response[0]==401 or response[0]==402:

            assert False
        else:

            assert True

    
    @pytest.mark.run(order=389)
    def test_389_NIOS_81656_Import_Records_from_grid2_to_grid1_enable_Zone_Transfer(self):
                logging.info("Change grid:dns properties  Zone Transfer to allow any")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.grid_vip)
                res=json.loads(get_ref)
                print ("###########",res[0]['_ref'])
                data={"allow_transfer": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}]}
                response = ib_NIOS.wapi_request('PUT', object_type=res[0]['_ref'],fields=json.dumps(data))
                print(response)
                for read in response:
                        assert True
                print("Grid:DNS Properties Allow transfer is set to Allow Any")
                dns_restart_services()
    
    @pytest.mark.run(order=390)
    def test_390_NIOS_81656_ImportRecords_From_grid2_to_grid1(self):
                log("start","/infoblox/var/infoblox.log",config.grid_vip)
                logging.info("Copying records from grid2 to grid1")
                data={"import_from": config.grid2_master_vip}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
                response=json.loads(get_ref)
                for res in response:
                    if res['fqdn']=="test_nx7.com":
                        ref_zone=res['_ref']
                res=json.loads(get_ref)
                print ("###########",ref_zone)
                response2 = ib_NIOS.wapi_request('PUT', object_type=ref_zone,fields=json.dumps(data))
                print(response2)
                for read in response:
                        assert True
                print("Import Grid Records success from grid2 to grid1")
                dns_restart_services()

    
    @pytest.mark.run(order=391)
    def test_391_NIOS_81656_Validate_sys_log_for_errors(self):
        display_msg("Validate /infoblox/var/infoblox.log  for errors ")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log1=logv("core.isc-worker0001.SIGABRT.395014","/infoblox/var/infoblox.log",config.grid_vip)
        if log1 :
            display_msg("Error log message found")
            assert False
        else:
            display_msg("No Error logs found")
            assert True


    @pytest.mark.run(order=392)
    def test_392_Enable_recursion_Queries_and_start_DNS_service(self):

        display_msg("**********************************************")
        display_msg("*              Testcase 02                   *")
        display_msg("**********************************************")
        display_msg("-------Start DNS service-------")

        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        display_msg("Member DNS reference")
        display_msg(get_ref)
        member_dns_ref = json.loads(get_ref)[0]['_ref']
        data = {"enable_dns": True}
        response = ib_NIOS.wapi_request('PUT', ref=member_dns_ref, fields=json.dumps(data))
        display_msg("Enable DNS, request response")
        if bool(re.match("\"member:dns*.",str(response))):
            display_msg("DNS service started successfully")
            sleep(20)
            assert True
        else:
            display_msg("Starting DNS service failed")
            assert False
        display_msg("-------Enabling recursion and queries on Grid DNS-------")

        display_msg("Fetch Grid DNS reference")
        get_grid_dns_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        display_msg("Grid DNS reference is given below")
        display_msg(get_grid_dns_ref)
        grid_dns_ref = json.loads(get_grid_dns_ref)[0]['_ref']
        data = {"allow_recursive_query": True,"logging_categories":{"log_queries": True}}
        response = ib_NIOS.wapi_request('PUT', ref=grid_dns_ref, fields=json.dumps(data))
        display_msg("Response for enable recursion on Grid DNS")
        display_msg(response)
        if bool(re.match("\"grid:dns*.",str(response))):
            display_msg("Recursion enabled and queries enabled successfully")
            dns_restart_services()
            assert True
        else:
            display_msg("Enabling recursion on the grid failed")
            assert False


    @pytest.mark.run(order=393)
    def test_393_NIOS_81257_add_fwd_zone_with_forwarder(self):
          print("Creating fwd zone")
          log("start","/var/log/syslog",config.grid_vip)
          forward_zone={"fqdn":"fwd1.com","forward_to":[{"address":config.grid2_master_vip,"name":config.grid2_master_fqdn}]}
          response = ib_NIOS.wapi_request('POST', object_type="zone_forward", fields=json.dumps(forward_zone))
          print(response)
          if response[0]==400 or response[0]==401 or response[0]==402:
           assert False
           dns_restart_services()
          else:

            assert True
          print ("Added Forward Zones as expected")
          zones=ib_NIOS.wapi_request('GET', object_type="zone_forward")
          print (zones)


    @pytest.mark.run(order=394)
    def test_394_NIOS_81257_Validate_sys_log_for_errors(self):
        display_msg("Validate var/log/syslog for errors ")
        log("stop","/var/log/syslog",config.grid_vip)
        log1=logv("exceeded max queries resolving","/var/log/syslog",config.grid_vip)
        if log1 :
            display_msg("Error log message found")
            assert False
        else:
            display_msg("No Error logs found")
            assert True


    @pytest.mark.run(order=395)
    def test_395_test_NIOS_81255_Create_authzone(self):
        display_msg("Create auth zone")

        data = {"fqdn":"p4.com","view":"default","grid_primary":[{"name":config.grid1_master_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        if type(response)== tuple:
            display_msg("Creating auth_zone Failed")
            assert False
        else:
            display_msg("Creating auth_zone  Success")
            dns_restart_services()
            assert True

    

    @pytest.mark.run(order=396)
    def test_396_NIOS_81255_Perform_dig_query_and_check_if_Recursion_Cache_View_Recursion_Client_Quota_exists(self):
        log("start","/var/log/syslog",config.grid_vip)
        display_msg("Perform dig query on the p4.com from the grid")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip,timeout=300)
        child.expect("bash-5.0#")
        child.sendline("dig @"+config.grid_vip+" p4.com")
        child.expect("bash-5.0#")
        output = child.before
        print(output)
        child.close()
        if('p4.com' in output):
            display_msg("Dig query successfull")
            assert True
        else:
            display_msg("Dig query failed")
            assert False


    @pytest.mark.run(order=397)
    def test_397_NIOS_81255_Validate_sys_log_for_errors(self):
        sleep(300)
        display_msg("Validate var/log/syslog for errors ")
        log("stop","/var/log/syslog",config.grid_vip)
        log1=logv("Recursion cache view Recursion client quota:","/var/log/syslog",config.grid_vip)
        if log1 :
            display_msg("Error log message found")
            assert False
        else:
            display_msg("No Error logs found")
            assert True


    @pytest.mark.run(order=398)
    def test_398_81254_Enable_recursion_Queries_Response_filter_aaaa_and_start_DNS_service(self):

        display_msg("-------Start DNS service-------")

        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        display_msg("Member DNS reference")
        display_msg(get_ref)
        member_dns_ref = json.loads(get_ref)[0]['_ref']
        data = {"enable_dns": True}
        response = ib_NIOS.wapi_request('PUT', ref=member_dns_ref, fields=json.dumps(data))
        display_msg("Enable DNS, request response")
        if bool(re.match("\"member:dns*.",str(response))):
            display_msg("DNS service started successfully")
            sleep(20)
            assert True
        else:
            display_msg("Starting DNS service failed")
            assert False
        display_msg("-------Enabling recursion,queries responses and filter_aaaa on grid:dns------")

        display_msg("Fetch Grid DNS reference")
        get_grid_dns_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
        display_msg("Grid DNS reference is given below")
        display_msg(get_grid_dns_ref)
        grid_dns_ref = json.loads(get_grid_dns_ref)[0]['_ref']
        data = {"allow_recursive_query": True,"logging_categories":{"log_queries": True,'log_responses': True} ,"filter_aaaa": "YES","forwarders":[config.grid2_master_vip]}
        response = ib_NIOS.wapi_request('PUT', ref=grid_dns_ref, fields=json.dumps(data))
        display_msg("Response for enable recursion  ,queries,responses and filter_aaaa on Grid DNS")
        display_msg(response)
        if bool(re.match("\"grid:dns*.",str(response))):
            display_msg("Recursion,queries,responses and filter_aaaa enabled  and forwarder added successfully")
            dns_restart_services()
            assert True
        else:
            display_msg("ecursion,queries,responses and filter_aaaa not enabled  and forwarder failed")
            assert False



    @pytest.mark.run(order=399)
    def test_399_test_NIOS_81254_Create_Auth_zone(self):
        display_msg("Create auth zone with member assignment")

        data = {"fqdn":"b1.com","view":"default","grid_primary":[{"name":config.grid1_master_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth",  fields=json.dumps(data),grid_vip=config.grid_vip)
        display_msg(response)
        if response[0]==400 or response[0]==401 or response[0]==402:

            assert False
        else:
            assert True
            dns_restart_services()


    @pytest.mark.run(order=400)
    def test_400_NIOS_81254_Perform_dig_query_on_the_grid(self):
        log("start","/var/log/syslog",config.grid_vip)
        display_msg("Perform dig query to test AAAA filtering ")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip,timeout=300)
        child.expect("bash-5.0#")
        child.sendline("dig @"+config.grid_vip+" b1.com aaaa")
        child.expect("bash-5.0#")
        output = child.before
        print(output)
        child.close()
        if('b1.com' in output):
            display_msg("Dig query successfull")
            assert True
        else:
            display_msg("Dig query failed")
            assert False


    @pytest.mark.run(order=401)
    def test_401_NIOS_81254_Validate_sys_log_for_errors(self):
        display_msg("Validate var/log/syslog for errors ")
        log("stop","/var/log/syslog",config.grid_vip)
        log1=logv("b1.com IN AAAA","/var/log/syslog",config.grid_vip)
        if log1 :
            display_msg("Error logs found")
            assert False
        else:
            display_msg("No Error logs found")
            assert True


    @pytest.mark.run(order=402)
    def test_402_NIOS_80612_add_the_DNS_DHCP_NIOS_Grid_license(member):
        
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set temp_license')
        child.expect(':')
        child.sendline('1')
        child.expect(':')
        child.sendline('y')
        child.expect(':')
        child.sendline('y')
        child.sendline('y')
        child.expect('Infoblox >')
        child.sendline('set temp_license')
        child.expect(':')
        child.sendline('2')
        child.expect(':')
        child.sendline('y')
        child.expect(': ')
        child.sendline('y')
        child.sendline('y')
        child.sendline('y')
        child.expect('Infoblox >')
        child.sendline('set temp_license')
        child.expect(':')
        child.sendline('7')
        child.expect(':')
        child.sendline('y')
        child.expect(':')
        child.sendline('y')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        sleep(150)
        
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set temp_license')
        child.expect(':')
        child.sendline('4')
        child.expect(':')
        child.sendline('y')
        child.expect(':')
        child.sendline('y')
        child.expect('Infoblox >')
        c= child.before
        sleep(150)
        
        
    @pytest.mark.run(order=403)
    def test_403_NIOS_80612_Create_Auth_zone(self):
        display_msg("Create auth zone with member assignment")

        data = {"fqdn":"nbc.com","view":"default","grid_primary":[{"name":config.grid1_master_fqdn}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth",  fields=json.dumps(data),grid_vip=config.grid_vip)
        display_msg(response)
        if response[0]==400 or response[0]==401 or response[0]==402:

            assert False
        else:

            assert True


    @pytest.mark.run(order=404)
    def test_404_NIOS_80612_Add_Network_10_0_0_0_24_with_members_assignment_in_default_network_view(self):
        print("\n***************************************************")
        print("* TC : 122 - Add network 10.0.0.0/24 with members assignment in default network view *")
        print("*****************************************************")
        data = {"network": "10.0.0.0/24","network_view": "default","members":[{"_struct": "dhcpmember","ipv4addr":config.grid_vip}]}
        #data = {"network": "10.0.0.0/24","network_view": "default","members": [{"_struct": "dhcpmember","ipv4addr": config.grid_master_vip}]}
        response = ib_NIOS.wapi_request('POST', object_type='network', fields=json.dumps(data))
        print(response)
        if bool(re.match("\"network*.*10.0.0.0",str(response))):
                print("Network 10.0.0.0/24 creation successful")
        sleep(5)


    @pytest.mark.run(order=405)
    def test_405_NIOS_80612_Download_Grid_Master_support_bundle(self):
                log("start","/var/log/syslog",config.grid_vip)
                logging.info("Download Grid Master Support Bundle")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('set transfer_supportbundle scp '+config.client_ip+' root infoblox dest /tmp/support_bundle_master.gz core_files')
                child.expect(':')
                child.sendline('y')
                sleep(100)
                child.expect('Infoblox >')
                response=child.before
                assert re.search(r'supportBundle is uploaded to scp server.* successfully',response)

    @pytest.mark.run(order=406)
    def test_406_NIOS_80612__Validate_sys_log_for_errors(self):
        display_msg("Validate var/log/syslog for errors ")
        log("stop","/var/log/syslog",config.grid_vip)
        log1=logv("/bin/tar:","/var/log/syslog",config.grid_vip)
        if log1 :
            display_msg("Error log message found")
            assert False
        else:
            display_msg("No Error logs found")
            assert True

    @pytest.mark.run(order=407)
    def test_407_NIOS_86559_Start_the_infoblox_logs_and_perform_upgrade_reset_status_command_in_CLI_and_stop_the_infoblox_logs(self):
        log("start","/infoblox/var/infoblox.log",config.grid1_member1_vip)
	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid1_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('>')
        child.sendline('set upgrade reset_status')
        child.expect(':')
        child.sendline('y')
        child.expect('>')
        sleep(10)
        log("stop","/infoblox/var/infoblox.log",config.grid1_member1_vip)
	    
    @pytest.mark.run(order=408)
    def test_408_NIOS_86559_Validate_input_output_and_cleaning_up_errors_infoblox_Logs(self):
        LookFor1="i/o error"
        logs1=logv(LookFor1,"/infoblox/var/infoblox.log",config.grid1_member1_vip)
        print("logs1 --> ",logs1)
	LookFor2="Error occurred while cleaning up grid upgrade status"
        logs2=logv(LookFor2,"/infoblox/var/infoblox.log",config.grid1_member1_vip)
        print("logs2 --> ",logs2)
        if logs1==None and logs2==None:
            assert True
        else:
            assert False
	sleep(05)
  
    @pytest.mark.run(order=409)
    def test_409_NIOS_86559_Validate_No_such_file_or_directory_logs_in_infoblox_Logs(self):
        LookFor1="Error occurred: No such file or directory"
        logs1=logv(LookFor1,"/infoblox/var/infoblox.log",config.grid1_member1_vip)
        print("logs1 --> ",logs1)
        LookFor2="Starting 'set upgrade reset_status'"
        logs2=logv(LookFor2,"/infoblox/var/infoblox.log",config.grid1_member1_vip)
        print("logs2 --> ",logs2)
	LookFor3="Successfully reset upgrade status"
        logs3=logv(LookFor3,"/infoblox/var/infoblox.log",config.grid1_member1_vip)
        print("logs3 --> ",logs3)
	if logs1==None and logs2==None and logs3==None:
	    assert False
	else:
	    assert True
	sleep(05)
        
    @pytest.mark.run(order=410)
    def test_410_NIOS_87521_Test_Killing_the_transfer_support_bundle_with_ctrl_Command(self):
        logging.info("Validating killing the transfer support bundle with ctrl command")
	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('>')
        child.sendline('set transfer_supportbundle scp '+config.client_ip+' root '+config.password+' dest '+config.scp_dest_path)
        child.expect(':')
        child.sendline('\x03')
        child.expect('Please press enter to proceed')
        output1 = child.before
        print("output1 is --> ",output1)
        value1 = re.search('Ctrl commands(.*)are invalid inputs', output1)
        value1 = value1.group(0)
        print("string is present",value1)
        child.sendline('\r')
        child.expect(':')
        child.sendline('y')
        sleep(30)
        child.expect('>')
        output2 = child.before
        print("output2 is --> ",output2)
        value2 = "supportBundle is uploaded to scp server "+config.client_ip+" successfully"
        if value2 in output2:
            assert True
        else:
            assert False
        sleep(05)
        
    @pytest.mark.run(order=411)
    def test_411_NIOS_81938_Reboot_the_subgrid(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid1_member1_vip)
        child.logfile=sys.stdout
        child.expect('password')
	child.sendline('infoblox')
        child.expect('>')
        child.sendline('reboot')
        child.expect(":")
	child.sendline('y')
	child.sendline('exit')
        sleep(300)
        
    @pytest.mark.run(order=412)
    def test_test_412_NIOS_81938_Check_sub_grid_availability_after_performing_reboot_on_sub_grid(self):
	for i in range(30):
	    ping = os.popen("for i in range{1..3} ; do ping -c 4 -w 10 "+config.grid1_member1_vip+" ; done").read()
            print(ping)
            if "0 received" not in ping:
              	print(config.grid1_member1_vip+" is pinging ")
                break
            else:
                print(config.grid1_member1_vip+" is not pinging, Going to sleep for 60 seconds ")
                print("\n")
                sleep(60)
	    print("\n")
    
    @pytest.mark.run(order=413)
    def test_test_413_NIOS_81938_Validate_cloud_init_logs_in_syslog(self):
        logging.info("Validating cloud init logs in syslog")
        log("start","/var/log/syslog",config.grid1_member1_vip)
        sleep(300)
        log("stop","/var/log/syslog",config.grid1_member1_vip)
        LookFor1="WARNING Daemon cloud-init does not appear to be running"
        LookFor2="INFO Daemon Waiting for cloud-init to copy ovf-env.xml"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid1_member1_vip)
        print("logs1 --> ",logs1)
        logs2=logv(LookFor2,"/var/log/syslog",config.grid1_member1_vip)
        print("logs2 --> ",logs2)
        if logs1==None and logs2==None:
            assert True
        else:
            assert False
       

    @pytest.mark.run(order=414)
    def test_414_NIOS_87317_start_ipv4_DHCP_service(self):
	logging.info("start ipv4 DHCP service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties")
        response = json.loads(get_ref)
        print(response)
        for i in response:
            data = {"enable_dhcp": True}
            get_ref1 = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
            print("get_ref1",get_ref1)
        response1 = re.search(r'200',get_ref1)
        for response1 in get_ref1:
            assert True
        sleep(30)
        print("ipv4 DHCP service started")

	@pytest.mark.run(order=415)
	def test_415_NIOS_87317_create_ipv4_network(self):
	    data = {"network": "10.0.0.0/24","network_view": "default","members": [{"_struct": "dhcpmember", "ipv4addr": config.grid1_master_vip,"name": config.grid1_master_fqdn}]}
	    get_ref = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data))
	    print("ref is",get_ref)	
	    print(type(get_ref))
	    if re.search("network.*10.0.0.0/24", get_ref):
		print("creation of ipv4 network is successful")
		assert True
	    else:
		print("creation ipv4 network is not successful")
		assert False
	    print("Restart DHCP services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid1_master_vip)
            ref = json.loads(grid)[0]['_ref']
            data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid1_master_vip)
            sleep(20)

	@pytest.mark.run(order=416)
	def test_416_NIOS_87317_validate_addition_of_ipv4_network(self):
	    get_ref = ib_NIOS.wapi_request('GET', object_type="network")
	    ref = json.loads(get_ref)
	    ref1 = json.loads(get_ref)[0]['_ref']
	    print(ref1)
	    output = ib_NIOS.wapi_request('GET',object_type="network",ref=ref1,params="?_inheritance=True&_return_fields=network",grid_vip=config.grid1_master_vip)
            output = json.loads(output)
	    print("output is",output)
	    if output["network"] == "10.0.0.0/24":
		assert True
	    else:
		assert False

	@pytest.mark.run(order=417)
	def test_417_NIOS_87317_create_shared_network_and_validate_logs_for_error_messages(self):
	    get_ref = ib_NIOS.wapi_request('GET',object_type="network")
	    ref = json.loads(get_ref)
	    ref = json.loads(get_ref)[0]['_ref']
	    print(ref)
	    log("start","/infoblox/var/infoblox.log",config.grid1_master_vip)
	    data = {"name": "ipv4_shared_network","network_view": "default","networks": [{"_ref": ref}]}
	    get_ref1 =ib_NIOS.wapi_request('POST', object_type="sharednetwork", fields=json.dumps(data))
	    print(get_ref1)
	    sleep(30)
	    log("stop","/infoblox/var/infoblox.log",config.grid1_master_vip)
	    if re.search("sharednetwork.*ipv4_shared_network",get_ref1):
		print("addition of network to shared network is successful")
       	    else:
		print("addition of network to shared network is not successful")
	    data = "IbapServerInternalErrorException"
	    logs = logv(data,"/infoblox/var/infoblox.log",config.grid1_master_vip)
	    print("logs are",logs)
	    if logs == None:
		print("ipv4 shared network created successfully without error")
		assert True
	    else:
		print("erro while creating ipv4 shared network")
		assert False

    @pytest.mark.run(order=418)
    def test_418_NIOS_86695_create_custom_DHCP_option_space(self):
        logging.info("create custom dhcp option space")
        data = {"name": "DHCP65"}
        response = ib_NIOS.wapi_request('POST',object_type="dhcpoptionspace",fields=json.dumps(data))
        print(response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        sleep(10)
        print("created dhcp option space successfully")


    @pytest.mark.run(order=419)
    def test_419_NIOS_86695_create_DHCP_option_definition_and_validate_error_message(self):
        logging.info("create dhcp option definition and validate error message")
        log("start","/infoblox/var/infoblox.log",config.grid1_master_vip)
        data = {"code":21,"name":"policy-filter","space":"DHCP65","type":"array of ip-address pair"}
        response = ib_NIOS.wapi_request('POST', object_type="dhcpoptiondefinition", fields=json.dumps(data))
        sleep(30)
        log("stop","/infoblox/var/infoblox.log",config.grid1_master_vip)
        res0 = str(response[0])
        print(res0)
        res1 = (response[1])
        print("res11 is",res1)
        if type(response) == tuple:
            if ("The custom option of \'array of ip-address pair\' data type is not allowed" in res1) and ("400" in res0):
                print("Not allowed to create dhcpoptionspace with type : array of ip-address pair")
                assert True
            else:
                print("allowed to create dhcpoptionspace with type : array of ip-address pair")
                assert False
        sleep(30)
        data = "Unable to start DHCPv4 service because no valid configuration files are available"
        logs = logv(data,"/infoblox/var/infoblox.log",config.grid1_master_vip)
        print(logs)
        if logs == None:
            print("validated DHCP service is running in logs")
            assert True
        else:
            print("validated DHCP service is not running in logs")
            assert False

    @pytest.mark.run(order=420)
    def test_420_NIOS_86695_validate_DHCP_service_is_running(self):
        logging.info("validate DHCP service is running")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", params="?_return_fields=enable_dhcp")
        response = json.loads(get_ref)
        print("response is",response)
        for i in response:
            if (i["enable_dhcp"]) == True:
                print("dhcp service is running")
                assert True
            else:
                print("dhcp service is not running")
                assert False

    @pytest.mark.run(order=421)
    def test_421_NIOS_86545_start_DNS_service(self):
        logging.info("start the ipv4 DNS service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        print(get_ref)
        res = json.loads(get_ref)
        for i in res:
            print("Enabling DNS IPV4 service")
            data = {"enable_dns": True}
            response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
            print response
            read  = re.search(r'200',response)
            for read in  response:
                assert True
        sleep(30)


    @pytest.mark.run(order=422)
    def test_422_NIOS_86545_create_ipv4_network(self):
        logging.info("create ipv4 network")
        data = {"network": "20.0.0.0/24","network_view": "default","members": [{"_struct": "dhcpmember", "ipv4addr": config.grid1_master_vip,"name": config.grid1_master_fqdn}]}
        get_ref = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data))
        print("ref is",get_ref)
        print(type(get_ref))
        if re.search("network.*20.0.0.0/24", get_ref):
            print("creation of ipv4 network is successful")
            assert True
        else:
            print("creation ipv4 network is not successful")
            assert False

    @pytest.mark.run(order=423)
    def test_423_NIOS_86545_Add_range_to_network_20_0_0_0_24_and_assign_GM(self):
        logging.info("add range to created network 20.0.0.0/24 and assign GM")
        data = {"network":"20.0.0.0/24","start_addr":"20.0.0.1","end_addr":"20.0.0.50","network_view": "default","member": {"_struct": "dhcpmember","ipv4addr": config.grid1_master_vip},"name": "Range1"}
        response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(data), grid_vip=config.grid1_master_vip)
        print(response)
        print(type(response))
        if re.search("range.*20.0.0.1/20.0.0.50",response):
            print("added range successfully")
            assert True
        else:
            print("range addition is unsuccessful")
            assert False

    @pytest.mark.run(order=424)
    def test_424_NIOS_86545_create_auth_zone_in_default_network_view(self):
        logging.info("create auth zone in default network view")
        data = {"fqdn":"test.com","view":"default","grid_primary":[{"name": config.grid1_master_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        print(response)
        print(type(response))
        if re.search("zone_auth.*test.com",response):
            print("auth zone test.com created successfully")
            assert True
        else:
            print("auth zone not created")
            assert False

    @pytest.mark.run(order=425)
    def test_425_NIOS_86545_Enable_IPv4_DDNS_Updates_in_grid_DHCP_properties(self):
        logging.info("enable ipv4 ddns updatea in grid dhcp properties")
        response = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid1_master_vip)
        print(response)
        get_ref = json.loads(response)[0]['_ref']
        print(get_ref)
        data = {"options":[{"name":"domain-name","value":"test.com"}],"enable_ddns":True,"ddns_domainname":"test1.com","ddns_generate_hostname": True}
        response2 = ib_NIOS.wapi_request('PUT',ref=get_ref,fields=json.dumps(data), grid_vip=config.grid1_master_vip)
        print("response2",response2)
        output = re.search(r'200',response2)
        for output in  response2:
            assert True
        sleep(10)

    @pytest.mark.run(order=426)
    def test_426_NIOS_86545_Enable_Allow_Updates_in_grid_DNS_properties(self):
        logging.info("enable allow updates in grid dns properties")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.grid1_master_vip)
        print(get_ref)
        get_ref = json.loads(get_ref)[0]['_ref']
        data = {"allow_update":[{"_struct":"addressac","address":"Any","permission": "ALLOW"}]}
        response = ib_NIOS.wapi_request('PUT',ref=get_ref,fields=json.dumps(data), grid_vip=config.grid1_master_vip)
        print(response)
        output = re.search(r'200',response)
        for output in  response:
            assert True
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid1_master_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid1_master_vip)
        sleep(30)

    @pytest.mark.run(order=427)
    def test_427_NIOS_86545_Request_IPv4_lease_capture_syslogs_validate_DNS_NS1_used_for_ddns_updates_in_syslogs_and_added_records(self):
        logging.info("request ipv4 lease")
        log("start","/var/log/syslog",config.grid1_master_vip)
        sleep(05)
        global log_validation
        for i in range(10):
            dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid1_master_vip)+' -n 1 -x l=20.0.0.0'
            print(dras_cmd)
            dras_cmd = os.system(dras_cmd)
            sleep(02)
            print("output is ",dras_cmd)
            if dras_cmd == 0:
                print("Got the lease")
                break
            else:
                print("Didn't get the lease and continuing for lease")
        sleep(110)
        log("stop","/var/log/syslog",config.grid1_master_vip)
        LookFor = 'by server'
        log_validation = logv(LookFor,"/var/log/syslog",config.grid1_master_vip)
        print(log_validation)
        data = ['Added new forward map from.*by server']
        for i in data:
            result = re.search(i,log_validation)
            if result == None:
                assert False
            else:
                assert True
        IPv4_records_validation()

    @pytest.mark.run(order=428)
    def test_428_NIOS_86545_disable_ddns_configured_zone(self):
        logging.info("disable ddns configured zone")
        response = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties", grid_vip=config.grid1_master_vip)
        print("response",response)
        get_ref = json.loads(response)[0]['_ref']
        print(get_ref)
        data =  {"ddns_domainname": ""}
        response1 = ib_NIOS.wapi_request('PUT',ref=get_ref, fields=json.dumps(data))
        print("response1",response1)

    @pytest.mark.run(order=429)
    def test_429_NIOS_86545_Request_IPv4_lease(self):
        logging.info("request ipv4 lease")
        for i in range(20):
            dras_cmd = 'sudo /import/tools/qa/tools/dras/./dras -i '+str(config.grid1_master_vip)+' -n 1 -x l=20.0.0.0'
            print(dras_cmd)
            dras_cmd = os.system(dras_cmd)
            sleep(02)
            print("output is ",dras_cmd)
            if dras_cmd == 0:
                print("Got the lease")
                break
            else:
                print("Didn't get the lease and continuing for lease")
        sleep(60)

    @pytest.mark.run(order=430)
    def test_430_NIOS_86545_validate_named_SIGQUIT_cores_files(self):
        logging.info("validate named.SIGQUIT core files")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid1_master_vip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("ls -ltr  /storage/cores")
        child.expect('#')
        output = child.before
        if "core.named.SIGQUIT" in output:
            print("cores are getting generated")
            assert False
        else:
            print("cores are not generated")
            assert True

    
    #86222
    @pytest.mark.run(order=431)
    def test_431_NIOS_86222_Check_if_LDAP_service_is_up_and_running_on_the_authentication_server_else_start_the_service(self):
        display_msg("Checking if the LDAP service is up and running on the authentication server, else, start the service")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.auth_server,timeout=300)
        except pexpect.TIMEOUT:
            display_msg("Unable to connect to the auth server, please check connectivity to the auth server")
            assert False
        else:
            child.expect("password:")
            child.sendline(config.auth_server_pass)
            child.expect(" ~]#")
            child.sendline("ps ax|grep slapd")
            output = child.before
            child.expect(" ~]#")
            output = child.before
            print(output)
            output = re.sub(r'\x1b\[([0-9,A-Z]{1,2}(;[0-9]{1,2})?(;[0-9]{3})?)?[m|K]?', '', output)
            print(output.split())
            if '/usr/sbin/slapd' in output:
                display_msg("LDAP service is running on the auth server")
                child.close()
                assert True
            else:
                display_msg("LDAP service is not running on the auth server, proceeding further to start the LDAP service")
                try:
                    child.sendline("systemctl start slapd")
                except pexpect.ExceptionPexpect as error:
                    display_msg("Unable to start ldap service")
                    display_msg(error)
                    assert False
                else:
                    sleep(20)
                    child.expect(" ~]#")
                    child.sendline("service slapd status --no-pager")
                    output = child.before
                    child.expect(" ~]#")
                    output = child.before
                    print(output)
                    if 'active (running)' in output:
                        display_msg("LDAP service running successfully")
                        child.close()
                        assert True
                    else:
                        display_msg("LDAP service status is not active, please check the below output and debug")
                        display_msg(output)
                        child.close()
                        assert False


    @pytest.mark.run(order=432)
    def test_432_NIOS_86222_Add_DNS_resolver(self):
        logging.info("Add DNS resolver")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
        grid_ref = json.loads(get_ref)[0]['_ref']
        data = {"dns_resolver_setting":{"resolvers":[config.resolver],"search_domains": []}}
        resolver_ref = ib_NIOS.wapi_request('PUT', ref=grid_ref, fields=json.dumps(data))
        logging.info(resolver_ref)
        if bool(re.match("\"grid*.",str(resolver_ref))):
            logging.info("Resolver added successfully")
        else:
            raise Exception("DNS resolver update failed")

    @pytest.mark.run(order=433)
    def test_433_NIOS_86222_Upload_LDAP_CA_cert(self):
        dir_name="certificate/"
        base_filename="ldap_ca_cert.pem"
        token = common_util.generate_token_from_file(dir_name,base_filename)
        print(token)
        data = {"token": token, "certificate_usage":"EAP_CA"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadcertificate")
        print(response)

    @pytest.mark.run(order=434)
    def test_434_NIOS_86222_Configure_LDAP_server_details_in_the_grid(self):
        display_msg("Configuring LDAP server details in the grid")
        data={
                "name": "ldap",
                "servers": [
                {
                    "address": config.auth_server,
                    "version": "V3",
                    "base_dn": "dc=ldapserver,dc=local",
                    "authentication_type": "ANONYMOUS",
                    "encryption": "NONE",
                    "port": 389,
                    }],
                "ldap_group_authentication_type": "GROUP_ATTRIBUTE",
                "search_scope": "SUBTREE",
                "ldap_user_attribute": "uid",
                "timeout": 5,
                "retries":5,
                "recovery_interval":30
            }

        response = ib_NIOS.wapi_request('POST', object_type="ldap_auth_service",fields=json.dumps(data))
        display_msg(response)
        if bool(re.match("\"ldap_auth_service*.",str(response))):
            display_msg("LDAP service configured sucessfully")
            assert True
        else:
            display_msg("LDAP service configuration failed")
            assert False

    @pytest.mark.run(order=435)
    def test_435_NIOS_86222_Add_LDAP_to_the_Authentiation_Policy_list(self):
        display_msg("Adding LDAP to the authentication policy")

        display_msg("Fetch Authentication policy ref")
        response = ib_NIOS.wapi_request('GET',object_type='authpolicy')
        auth_policy_ref = json.loads(response)[0]['_ref']
        display_msg("Authentication Policy ref: "+auth_policy_ref)

        display_msg("Fetch local user ref")
        response = ib_NIOS.wapi_request('GET',object_type='authpolicy?_return_fields=auth_services')
        local_user_ref = json.loads(response)[0]['auth_services'][0]
        display_msg("Local user ref: "+local_user_ref)



        display_msg("Fetch LDAP server ref")
        response = ib_NIOS.wapi_request('GET', object_type="ldap_auth_service")
        ldap_ref = json.loads(response)[0]['_ref']
        display_msg("LDAP server ref : "+ldap_ref)

        display_msg("Add Local and LDAP to the authentiation policy list")
        data={"auth_services":[local_user_ref,ldap_ref]}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=auth_policy_ref)
        display_msg(response)
        if bool(re.match("\"authpolicy*.",str(response))):
            display_msg("Local and LDAP added to the authentiation policy list successfully")
            sleep(10)
            assert True
        else:
            display_msg("Local and  LDAP addition to the authentiation policy list failed")
            assert False


    @pytest.mark.run(order=436)
    def test_436_NIOS_86222_Assign_remote_users_admin_group_as_superuser(self):
        map_remote_user_to_the_group()


    @pytest.mark.run(order=437)
    def test_437_NIOS_86222_Login_to_the_grid_using_LDAP_credentials_and_execute_cli_command(self):
        display_msg("Logging into the grid using LDAP credentials via CLI")
        display_msg("Starting log capture")
        log("start","/var/log/syslog",config.grid_vip)
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/infoblox/var/audit.log",config.grid_vip)
        sleep(10)
        display_msg("Logging into the grid")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+config.ldap_username+'@'+config.grid_vip,timeout=300)
        except pexpect.TIMEOUT:
            display_msg("Unable to connect to the grid, please check connectivity to the grid")
            assert False
        else:
            child.expect("password:")
            child.sendline(config.ldap_password)
            child.expect("Infoblox >")
            child.sendline("show status")
            child.expect("Infoblox >")
            output = child.before
            child.close()
            if 'Hostname:       '+config.grid_fqdn in output:
                display_msg("The user was  able to execute command as a super user")
                assert True
            else:
                display_msg("The user was not able to execute command as a super user")
                assert False

    @pytest.mark.run(order=438)
    def test_438_NIOS_86222_Verify_logs_for_LDAP_user_login_as_superuser(self):
        display_msg("Verify logs for LDAP user login as superuser")
        sleep(20)
        display_msg("Stopping log capture")

        log("stop","/var/log/syslog",config.grid_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/infoblox/var/audit.log",config.grid_vip)

        count=0
        display_msg("Verifying syslog for the authentication logs")
        validate = logv(".*info LDAP authentication succeeded for user "+config.ldap_username+".*","/var/log/syslog",config.grid_vip)
        if validate != None:
            count +=1
            display_msg("Syslog verification successfull")
        else:
             display_msg("Syslog verification unsuccessfull")

        display_msg("Verifying infoblox.log for the authentication logs")
        validate = logv("LDAP Authentication Succeeded for user '"+config.ldap_username+"'.*","/infoblox/var/infoblox.log",config.grid_vip)
        if validate != None:
            count +=1
            display_msg("infoblox.log verification successfull")
        else:
             display_msg("infoblox.log verification unsuccessfull")


        display_msg("Verifying audit.log for the authentication logs")
        validate = logv(".*"+config.ldap_username+".*auth=LDAP.*","/infoblox/var/audit.log",config.grid_vip)
        if validate != None:
            count +=1
            display_msg("Audit.log verification successfull")
        else:
             display_msg("Audit.log verification unsuccessfull")

        if count ==3:
            display_msg("All log verifications successful")
            assert True
        else:
            display("Log verification failed, check above logs for the failures")
            assert False



    @pytest.mark.run(order=439)
    def test_439_NIOS_86222_Remove_LDAP_from_the_Authentiation_Policy_list(self):
        display_msg("Remove LDAP service from the authentication policy")

        display_msg("Fetch Authentication policy ref")
        response = ib_NIOS.wapi_request('GET',object_type='authpolicy')
        auth_policy_ref = json.loads(response)[0]['_ref']
        display_msg("Authentication Policy ref: "+auth_policy_ref)

        display_msg("Fetch local user ref")
        response = ib_NIOS.wapi_request('GET',object_type='authpolicy?_return_fields=auth_services')
        local_user_ref = json.loads(response)[0]['auth_services'][0]
        display_msg("Local user ref: "+local_user_ref)

        display_msg("Fetch LDAP server ref")
        response = ib_NIOS.wapi_request('GET', object_type="ldap_auth_service")
        ldap_ref = json.loads(response)[0]['_ref']
        display_msg("LDAP server ref : "+ldap_ref)

        display_msg("Remove LDAP from the authentiation policy list")
        data={"auth_services":[local_user_ref]}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=auth_policy_ref)
        display_msg(response)
        if bool(re.match("\"authpolicy*.",str(response))):
            display_msg("LDAP removed from the authentication policy list successfully")
            sleep(10)
            assert True
        else:
            display_msg("LDAP removal from the authentication policy list failed")
            assert False


    @pytest.mark.run(order=440)
    def test_440_NIOS_86222_Change_the_LDAP_settings_to_use_SSL_login_with_fqdn_as_ip_address(self):
        logging.info("Change the LDAP settings to use LDAP SSL login with fqdn as ip address")
        response = ib_NIOS.wapi_request("GET",object_type="ldap_auth_service")
        ref = json.loads(response)[0]['_ref']
        print(ref)
        #data={'ldap_group_authentication_type':'GROUP_ATTRIBUTE',"servers":[{"address":"10.197.38.101","base_dn":"ou=People,dc=ldapserver,dc=local"}],"search_scope": "ONELEVEL"}
        data={
                "name": "ldap",
                "servers": [
                {
                    "address": config.auth_server,
                    "version": "V3",
                    "base_dn": "dc=ldapserver,dc=local",
                    "authentication_type": "AUTHENTICATED",
                    "bind_user_dn": "cn=admin,dc=ldapserver,dc=local",
                    "bind_password": config.ldap_password,
                    "encryption": "SSL",
                    "port": 636,
                    }],
                "ldap_group_authentication_type": "GROUP_ATTRIBUTE",
                "search_scope": "SUBTREE",
                "ldap_user_attribute": "uid",
                "timeout": 5,
                "retries":5,
                "recovery_interval":30
            }
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if bool(re.match("\"ldap_auth_service*.",str(response))):
            display_msg("LDAP service configuration changes sucessfull")
            assert True
        else:
            display_msg("LDAP service configuration changes failed")
            assert False



    @pytest.mark.run(order=441)
    def test_442_NIOS_86222_Add_LDAP_to_the_Authentiation_Policy_list(self):
        display_msg("Adding LDAP to the authentication policy")

        display_msg("Fetch Authentication policy ref")
        response = ib_NIOS.wapi_request('GET',object_type='authpolicy')
        auth_policy_ref = json.loads(response)[0]['_ref']
        display_msg("Authentication Policy ref: "+auth_policy_ref)

        display_msg("Fetch local user ref")
        response = ib_NIOS.wapi_request('GET',object_type='authpolicy?_return_fields=auth_services')
        local_user_ref = json.loads(response)[0]['auth_services'][0]
        display_msg("Local user ref: "+local_user_ref)



        display_msg("Fetch LDAP server ref")
        response = ib_NIOS.wapi_request('GET', object_type="ldap_auth_service")
        ldap_ref = json.loads(response)[0]['_ref']
        display_msg("LDAP server ref : "+ldap_ref)

        display_msg("Add Local and LDAP to the authentiation policy list")
        data={"auth_services":[local_user_ref,ldap_ref]}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=auth_policy_ref)
        display_msg(response)
        if bool(re.match("\"authpolicy*.",str(response))):
            display_msg("Local and LDAP added to the authentiation policy list successfully")
            sleep(10)
            assert True
        else:
            display_msg("Local and  LDAP addition to the authentiation policy list failed")
            assert False

    @pytest.mark.run(order=442)
    def test_442_NIOS_86222_Try_logging_in_with_LDAP_credentials_using_CLI_negative_case(self):

        display_msg("Logging into the grid using LDAP credentials via CLI(negative case)")
        display_msg("Starting log capture")
        log("start","/var/log/syslog",config.grid_vip)
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        sleep(10)
        display_msg("Logging into the grid")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+config.ldap_username+'@'+config.grid_vip,timeout=300)
        except pexpect.TIMEOUT:
            display_msg("Unable to connect to the grid, please check connectivity to the grid")
            assert False
        else:
            child.expect("password:")
            child.sendline(config.ldap_password)
            child.expect("password:")
            output = child.before
            child.close()
            if 'Permission denied, please try again' in output:
                display_msg("The user was unable to login as expected")
                assert True
            else:
                display_msg("The user was able to login with LDAP SSL configured and hostname is IP instead of FQDN, which is a bug")
                assert False

    @pytest.mark.run(order=443)
    def test_443_NIOS_86222_Verify_logs_for_LDAP_user_login_as_superuser(self):
        display_msg("Verify logs for LDAP user failed login")
        sleep(20)
        display_msg("Stopping log capture")

        log("stop","/var/log/syslog",config.grid_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)

        count=0
        display_msg("Verifying syslog for the authentication logs")
        validate = logv(".*info No authentication methods succeeded for user "+config.ldap_username+".*","/var/log/syslog",config.grid_vip)
        if validate != None:
            count +=1
            display_msg("Syslog verification successfull")
        else:
             display_msg("Syslog verification unsuccessfull")

        display_msg("Verifying infoblox.log for the authentication logs")
        validate = logv("LDAP Authentication Failed for user '"+config.ldap_username+"'.*","/infoblox/var/infoblox.log",config.grid_vip)
        if validate != None:
            count +=1
            display_msg("infoblox.log verification successfull")
        else:
             display_msg("infoblox.log verification unsuccessfull")


        if count ==2:
            display_msg("All log verifications successful")
            assert True
        else:
            display("Log verification failed, check above logs for the failures")
            assert False



    @pytest.mark.run(order=444)
    def test_444_NIOS_86222_Remove_LDAP_from_the_Authentiation_Policy_list(self):
        display_msg("Remove LDAP service from the authentication policy")

        display_msg("Fetch Authentication policy ref")
        response = ib_NIOS.wapi_request('GET',object_type='authpolicy')
        auth_policy_ref = json.loads(response)[0]['_ref']
        display_msg("Authentication Policy ref: "+auth_policy_ref)

        display_msg("Fetch local user ref")
        response = ib_NIOS.wapi_request('GET',object_type='authpolicy?_return_fields=auth_services')
        local_user_ref = json.loads(response)[0]['auth_services'][0]
        display_msg("Local user ref: "+local_user_ref)

        display_msg("Fetch LDAP server ref")
        response = ib_NIOS.wapi_request('GET', object_type="ldap_auth_service")
        ldap_ref = json.loads(response)[0]['_ref']
        display_msg("LDAP server ref : "+ldap_ref)

        display_msg("Remove LDAP from the authentiation policy list")
        data={"auth_services":[local_user_ref]}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=auth_policy_ref)
        display_msg(response)
        if bool(re.match("\"authpolicy*.",str(response))):
            display_msg("LDAP removed from the authentication policy list successfully")
            sleep(10)
            assert True
        else:
            display_msg("LDAP removal from the authentication policy list failed")
            assert False


    @pytest.mark.run(order=445)
    def test_445_NIOS_86222_Change_the_LDAP_settings_to_use_SSL_login_with_fqdn_as_hostname(self):
        logging.info("Change the LDAP settings to use LDAP SSL login with fqdn as ip address")
        response = ib_NIOS.wapi_request("GET",object_type="ldap_auth_service")
        ref = json.loads(response)[0]['_ref']
        print(ref)
        #data={'ldap_group_authentication_type':'GROUP_ATTRIBUTE',"servers":[{"address":"10.197.38.101","base_dn":"ou=People,dc=ldapserver,dc=local"}],"search_scope": "ONELEVEL"}
        data={
                "name": "ldap",
                "servers": [
                {
                    "address": config.auth_server_fqdn,
                    "version": "V3",
                    "base_dn": "dc=ldapserver,dc=local",
                    "authentication_type": "AUTHENTICATED",
                    "bind_user_dn": "cn=admin,dc=ldapserver,dc=local",
                    "bind_password": config.ldap_password,
                    "encryption": "SSL",
                    "port": 636,
                    }],
                "ldap_group_authentication_type": "GROUP_ATTRIBUTE",
                "search_scope": "SUBTREE",
                "ldap_user_attribute": "uid",
                "timeout": 5,
                "retries":5,
                "recovery_interval":30
            }
        response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
        if bool(re.match("\"ldap_auth_service*.",str(response))):
            display_msg("LDAP service configuration changes sucessfull")
            assert True
        else:
            display_msg("LDAP service configuration changes failed")
            assert False



    @pytest.mark.run(order=446)
    def test_446_NIOS_86222_Add_LDAP_to_the_Authentiation_Policy_list(self):
        display_msg("Adding LDAP to the authentication policy")

        display_msg("Fetch Authentication policy ref")
        response = ib_NIOS.wapi_request('GET',object_type='authpolicy')
        auth_policy_ref = json.loads(response)[0]['_ref']
        display_msg("Authentication Policy ref: "+auth_policy_ref)

        display_msg("Fetch local user ref")
        response = ib_NIOS.wapi_request('GET',object_type='authpolicy?_return_fields=auth_services')
        local_user_ref = json.loads(response)[0]['auth_services'][0]
        display_msg("Local user ref: "+local_user_ref)



        display_msg("Fetch LDAP server ref")
        response = ib_NIOS.wapi_request('GET', object_type="ldap_auth_service")
        ldap_ref = json.loads(response)[0]['_ref']
        display_msg("LDAP server ref : "+ldap_ref)

        display_msg("Add Local and LDAP to the authentiation policy list")
        data={"auth_services":[local_user_ref,ldap_ref]}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=auth_policy_ref)
        display_msg(response)
        if bool(re.match("\"authpolicy*.",str(response))):
            display_msg("Local and LDAP added to the authentiation policy list successfully")
            sleep(10)
            assert True
        else:
            display_msg("Local and  LDAP addition to the authentiation policy list failed")
            assert False


    @pytest.mark.run(order=447)
    def test_447_NIOS_86222_Check_if_error_logs_are_observed(self):
        display_msg("Check if error logs are observed")
        print("Starting log capture")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        display_msg("Wait for 3 min for log capture to finish")
        sleep(180)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)

        display_msg("Verifying infoblox.log for the error logs")
        validate = logv(".*Ldap server data not found for key: 0\.ldap\."+config.auth_server+".*","/infoblox/var/infoblox.log",config.grid_vip)
        if validate != None:
            display_msg("Error log encountered")
            assert False
        else:
             display_msg("Error log not encountered")
             assert True

    @pytest.mark.run(order=448)
    def test_448_NIOS_86619_create_a_DNS_view(self):
        
        print("\n========================================================\n")
        print("*********** Create a DNS view  ************")
        print("\n========================================================\n")

        data = {"name":"ಕನ್ನಡ"}
        response = ib_NIOS.wapi_request('POST', object_type="view", fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)

        print(response)
        if type(response) == tuple:           
            if response[0]==200: 
                print("\n Success: DNS view 'ಕನ್ನಡ' was created!") 
                assert True 
            else:
                print("\n Failure: did not created DNS view 'ಕನ್ನಡ'\n")
                assert False
        elif 'view' in response:
            print("\n Success: added Auth server to the member\n")
            assert True 

    @pytest.mark.run(order=449)
    def test_499_NIOS_86619_create_a_DNS_view(self):
        print("\n--------------------------------------------------------\n")
        print("Validating DNS view created")
        print("\n--------------------------------------------------------\n")

        response = ib_NIOS.wapi_request('GET', object_type="view?name=ಕನ್ನಡ", grid_vip=config.grid_vip)
        response=json.loads(response)[0]
        print(response)

        if 'view' in response['_ref']:
            print(response['_ref'])
            print("SUCCESS: DNS view 'ಕನ್ನಡ' was created!")
            assert True
        else:
            print("FAILURE: DNS view 'ಕನ್ನಡ' was NOT created!")
            assert False 
        

    @pytest.mark.run(order=450)
    def test_450_NIOS_86619_perform_rpz_recursive_only(self):

        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        try:
            child.expect ('password.*')
            child.sendline ('infoblox')
            child.expect ('Infoblox >',timeout=60)
            child.sendline('set maintenancemode')
            child.expect("Maintenance Mode > ")
            child.sendline ('set rpz_recursive_only')
            child.expect('Maintenance Mode >')
            print(child.after)
            print(child.before)
            if '.*if zone omitted.* setting will be applied to view level.*' in child.before:
                print('executing "rpz_recursive_only" with DNS view in special characters')
            child.sendline('exit')
            child.close()
        except Exception as e:
            print("Failure: Execute command set rpz_recursive_only")
            print(e)
            child.close()
            assert False
        finally:
            child.close()

    @pytest.mark.run(order=451)
    def test_451_NIOS_86150_Enable_DNS_service_on_both_IPv4_IPv6_LAN_interface(self):
        print("Fetch member dns reference")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            member_ref = ref['_ref']
            data = {"enable_dns":True,"use_lan_ipv6_port":True,"use_lan_port":True}
            response = ib_NIOS.wapi_request('PUT',ref=member_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)
            if bool(re.match("\"member:dns*.",str(response))):
                print("IPv4 and IPv6 DNS interface set for member "+ref['host_name'])
                sleep(5)
            else:
                print("Unable to set IPv4 and IPv6 DNS interface for member "+ref['host_name'])
                assert False
        restart_the_grid_Services()

    @pytest.mark.run(order=452)
    def test_452_NIOS_86150_create_a_zone(self):
        
        print("Create a zone with grid master as grid primary and external secondary with IPv6 address.")
        print(config.grid1_master_fqdn)
        data={"fqdn":"nios_86150_zone.com","view":"default","grid_primary":[{"name":config.grid1_master_fqdn,"stealth": False}],"external_secondaries": [{"address": "2001:550:40a:2400::1","name": "external_second_member","stealth": False,"use_tsig_key_name": False}]}
        response=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        print(response)
        if type(response) == tuple:           
            if response[0]==200: 
                print("Zone nios_86150_zone.com creation successful")
                restart_the_grid_Services()
                assert True
        elif 'zone_auth' in response:
            print("Zone nios_86150_zone.com creation successful")
            restart_the_grid_Services()
            assert True

        else:
            print("Zone nios_86150_zone.com creation unsuccessful")
            print("\n")
            assert False
        

    @pytest.mark.run(order=453)
    def test_453_NIOS_86150_Disable_DNS_service_on_IPv6_LAN_interface(self):
        print("Disable DNS service on IPv6 LAN interface.")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            member_ref = ref['_ref']
            data = {"enable_dns":True,"use_lan_ipv6_port":False}
            response = ib_NIOS.wapi_request('PUT',ref=member_ref,fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)
            if bool(re.match("\"member:dns*.",str(response))):
                print("Disabled IPv6 DNS interface for member "+ref['host_name'])
                sleep(5)
                assert True
            else:
                print("Unable to disable IPv6 DNS interface for member "+ref['host_name'])
                assert False
        sleep(20)

    @pytest.mark.run(order=454)
    def test_454_NIOS_86150_edit_the_zone_and_try_to_click_save_and_close(self):
        print("edit the zone and try to click save & close.")

        zone_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
        #print(zone_ref)
        for zone in json.loads(zone_ref):
            if 'nios_86150_zone.com' in zone['_ref']:
                print(zone['_ref'])
                zone_ref = zone['_ref']
                break
        data={"comment":"save and close","view":"default","grid_primary":[{"name": config.grid1_master_fqdn,"stealth": False}],"external_secondaries": [{"address": "2001:550:40a:2400::1","name": "external_second_member","stealth": False,"use_tsig_key_name": False}]}
        
        response = ib_NIOS.wapi_request('PUT', object_type=zone_ref,fields=json.dumps(data))
        print(response)
        if response[0]==200:
            print("Zone nios_86150_zone.com creation unsuccessful")
            print("\n")
            assert False
        else:
            print("Secondary name servers must use the same protocol (IPv4/IPv6) as their primary name server.")
            assert True


    @pytest.mark.run(order=455)
    def test_455_NIOS_85505_Enable_GSS_TSIG_authentication_of_clients(self):
        data = {"filename":"niosqadns.ktb"}
        create_file = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadinit")
        print(create_file)
        res = json.loads(create_file)
        token = json.loads(create_file)['token']
        url = json.loads(create_file)['url']
        print (create_file)
        print (res)
        print (token)
        print (url)
        grid = ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data = {"token":token}
        request_restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=upload_keytab", fields=json.dumps(data), grid_vip=config.grid1_master_vip)
        #sleep(30)
        print(request_restart)
        os.system("curl -k1 -u admin:infoblox -F name=niosqadns.ktb -F filedata=@niosqadns.ktb 'https://10.35.112.9/http_direct_file_io/req_id-UPLOAD-0123003106538599/niosqadns'")
        #os.system('curl -k1 -u admin:infoblox -F name=%s -F filedata=@%s %s'%(filename,filename,url))
        print("OPen bug: NIOS-89871")
        assert False
        grid_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=config.grid_vip)
        for ref in json.loads(grid_ref):
            grid_ref = ref['_ref']
        print(grid_ref)
        data={
        "gss_tsig_keys": [
            "kerberoskey/ZG5zLmtlcmJlcm9zX2tleSRETlMvbmlvc3FhLmV4YW1wbGUubG9jYWxARVhBTVBMRS5MT0NBTC4zLmFyY2ZvdXItaG1hYy1tZDU:DNS%2Fniosqa.example.local%40EXAMPLE.LOCAL/3/ARCFOUR-HMAC-MD5",
            "kerberoskey/ZG5zLmtlcmJlcm9zX2tleSRETlMvbmlvc3FhLmV4YW1wbGUubG9jYWxARVhBTVBMRS5MT0NBTC4zLmFlczI1Ni1jdHMtaG1hYy1zaGExLTk2:DNS%2Fniosqa.example.local%40EXAMPLE.LOCAL/3/AES256-CTS-HMAC-SHA1-96",
            "kerberoskey/ZG5zLmtlcmJlcm9zX2tleSRETlMvbmlvc3FhLmV4YW1wbGUubG9jYWxARVhBTVBMRS5MT0NBTC4zLmRlcy1jYmMtY3Jj:DNS%2Fniosqa.example.local%40EXAMPLE.LOCAL/3/DES-CBC-CRC",
            "kerberoskey/ZG5zLmtlcmJlcm9zX2tleSRETlMvbmlvc3FhLmV4YW1wbGUubG9jYWxARVhBTVBMRS5MT0NBTC4zLmRlcy1jYmMtbWQ1:DNS%2Fniosqa.example.local%40EXAMPLE.LOCAL/3/DES-CBC-MD5",
            "kerberoskey/ZG5zLmtlcmJlcm9zX2tleSRETlMvbmlvc3FhLmV4YW1wbGUubG9jYWxARVhBTVBMRS5MT0NBTC4zLmFlczEyOC1jdHMtaG1hYy1zaGExLTk2:DNS%2Fniosqa.example.local%40EXAMPLE.LOCAL/3/AES128-CTS-HMAC-SHA1-96"
        ]}
        response=ib_NIOS.wapi_request('PUT',object_type=grid_ref,fields=json.dumps(data))
        print(response)
        if bool(re.match("grid:dns",str(response))):
            print("Enable GSS-TSIG authentication of clients, Upload and assign keys and upload the keytab")
        else:
            print("Can not Enable GSS-TSIG authentication of clients  and upload keytab also failed")
            print("\n")
            assert False
        
    @pytest.mark.run(order=456)
    def test_456_NIOS_85505_Login_to_the_grid_as_admin_user_from_CLI(self):
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('show dns_gss_tsig keytab')
            child.expect('Infoblox >')
            if 'arcfour-hmac-md5' in child.before:
                print("CLI command dns_gss_tsig keytab is working as expected")
                child.close()
                assert True
            else:
                print("CLI command dns_gss_tsig keytab is failed to list output  ")
                print("OPen bug: NIOS-89871")
                assert False
        except Exception as e:
            child.close()
            print(e)      
            print("Failure: There is no DNS keytab file present on this member which is a bug")
            print("OPen bug: NIOS-89871")
            assert False

    @pytest.mark.run(order=457)
    def test_457_NIOS_85384_perform_dns_restart_and_check_dns_status(self):
        restart_the_grid_Services()
        
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('show dns stats')
            #child.expect('Enter .*return.* for next page.*')
            #child.sendline('q')
            child.expect('Infoblox >')
            if 'success' in child.before:
                print("Success: Able to fetch status while DNS restarting")
                child.close()
                assert True
        except Exception as e:
            child.close()
            print(e)      
            print("Failure: could not fetch status while DNS restarting")
            assert False

    @pytest.mark.run(order=458)
    def test_458_NIOS_82460_delete_all_zone(self):
               
        print("Delete the auth zone")
        response = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
        print(response)
        for ref in json.loads(response):
            del_ref = ib_NIOS.wapi_request('DELETE', object_type = ref['_ref'])
            if response[0]==400 or response[0]==401 or response[0]==404 or response[0]==500:
                print("FAILURE: Deleting zone failed.")
                assert False
            else:
                
                print("Auth zone deletion successful")
                assert True
        dns_restart_services()

    @pytest.mark.run(order=459)
    def test_459_NIOS_82460_create_a_zone(self):
        print("Create a zone with grid master as grid primary and external secondary with IPv6 address.")
        data={"fqdn":"p3.com","view":"default","grid_primary":[{"name": config.grid1_master_fqdn,"stealth": False}]}
        test4_ref=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        print(test4_ref)
        if bool(re.match("\"zone_auth*.*p3.com",str(test4_ref))):
            print("Zone p3.com creation successful")
            restart_the_grid_Services()
        else:
            print("Zone p3.com creation unsuccessful")
            print("\n")
            assert False

    #CSV Upload case
    @pytest.mark.run(order=460)
    def test_460_NIOS_82460_Upload_the_unknown_rr_CSV_file(self):
        log("start","/infoblox/var/audit.log",config.grid_vip)
        print("Import the CSV file and check if no errors are observed")
        dir_name = os.getcwd()
        base_filename = "latest_all_unknown_rr_nios_9_0.csv"
        token = common_util.generate_token_from_file(dir_name, base_filename)
        print(token)
        data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
        response=json.loads(response)
        print(response)
        sleep(10)
        data={"action":"START","file_name":base_filename,"on_error":"CONTINUE","operation":"CREATE","separator":"COMMA"}
        get_ref=ib_NIOS.wapi_request('GET', object_type="csvimporttask")
        print(get_ref)
        get_ref=json.loads(get_ref)
        for ref in get_ref:
            if response["csv_import_task"]["import_id"]==ref["import_id"]:
                if ref["lines_failed"]==0:
                    print("CSV import successful")
                    restart_the_grid_Services()
                    assert True
                else:
                    print("CSV import unsuccessful")
                    assert False

        log("stop","/infoblox/var/audit.log",config.grid_vip)
        

    @pytest.mark.run(order=461)
    def test_461_NIOS_82460_verify_logs__after_importing_CSV_unknown_rr_file(self): 
        print("\n======================================")
        print("\n Verify the 'General Database Error' and 'Import error 'logs after importing a csv file\n")
        print("======================================\n")
        LookFor=[".*Import Error.*",".*General Database Error.*"]
        print(LookFor)
        for look in LookFor:
            logs=logv(look,"/infoblox/var/audit.log",config.grid_vip)
            print(logs)
            print('-------------------------')
            if logs:
                print("Failure: Confirmed that there were no error logs to be found")
                assert False 
            else:
                print("Success: Confirmed that there were error logs to be found")
                assert True
            
    @pytest.mark.run(order=462)
    def test_462_NIOS_84739_stop_DCA_service_before_enable(self):
        print("\n========================================================\n")
        print("Stop DCA service on members")
        print("\n========================================================\n")

        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=enable_dns_cache_acceleration", grid_vip=config.grid_vip)
        res = json.loads(get_ref)
        for ref in res:
            
            data = {"enable_dns_cache_acceleration": False}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)
            if type(response) == tuple:
                if response[0]==200:
                    print("SUCCESS: DCA service Stoped grid master")
                    assert True
                    
            elif 'member:dns' in response:
                    print("SUCCESS: DCA service Stoped grid master")
                    assert True
            else:
                print("Failed: Couldnt stop DCA service grid master")
        sleep(60)

    @pytest.mark.run(order=463)
    def test_463_NIOS_84739_start_DCA_and_ADP_service(self):
        print("\n========================================================\n")
        print("Start DCA and ADP service on members")
        print("\n========================================================\n")
        
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=enable_dns_cache_acceleration", grid_vip=config.grid_vip)
        res = json.loads(get_ref)
        for ref in res:
            
            data = {"enable_dns_cache_acceleration": True}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
            print(response)
            if type(response) == tuple:
                if response[0]==200:
                    print("SUCCESS: DCA service Started grid master")
                    assert True
                    
            elif 'member:dns' in response:
                print("SUCCESS: DCA service Started grid master")
                assert True
            else:
                print("FAILURE: Couldnt Start DCA service grid master")
                assert False
        
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        print(get_ref)
        res = json.loads(get_ref)
        for ref in res:
            
            data={"enable_service":True}
            modify_disable_field = ib_NIOS.wapi_request('PUT',object_type=ref['_ref'],fields=json.dumps(data))
            print(modify_disable_field)
            
            check_able_to_login_appliances(config.grid_vip)
            if type(modify_disable_field) == tuple:
                if modify_disable_field[0]==200:
                    print("Success: Enabled TP services on master")
                    assert True
                elif 'member:dns' in modify_disable_field:
                    print("Success: Enabled TP services on master")
                    assert True
                else:
                    print("Failed: enabling TP services")
                    assert False
        sleep(60)

    @pytest.mark.run(order=464)
    def test_464_NIOS_84739_disabling_DCA_service_notice_any_error_log(self):
        print("\n============================================\n")
        print("Disabling DNS cache acceleration services  ")
        print("\n============================================\n")
        log("start","/var/log/syslog",config.grid1_master_vip)
        
        data = {"enable_dns": False,"enable_dns_cache_acceleration": False}
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=enable_dns_cache_acceleration", grid_vip=config.grid_vip)

        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('PUT', object_type=ref['_ref'], fields=json.dumps(data))
            print(response)
            if type(response) == tuple:
                if response[0]==200:
                    print("Success: Stop DCA Service")
                    assert True
                else:
                    print("Failure: did not Stop DCA Service")
                    assert False
            if 'member:dns' in response:
                print("Success: Disabled  DCA service")
                assert True
            else:
                print("Failure: Can not Disabled  DCA service")
                assert False

        sleep(60)
        log("stop","/var/log/syslog",config.grid1_master_vip)
        
        check_able_to_login_appliances(config.grid_vip)

    @pytest.mark.run(order=465)
    def test_465_NIOS_84739_verify_logs__after_importing_CSV_unknown_rr_file(self): 
        print("\n======================================")
        print("\n Verify the 'err Netfpc control' after disable DCA\n")
        print("======================================\n")
        LookFor=".*fp-rte.*err Netfpc control thread.*"
        print(LookFor)
        
        logs=logv(LookFor,"/var/log/syslog",config.grid1_master_vip)
        print(logs)
        print('-------------------------')
        if logs:
            print("Failure: Confirmed that there were no error logs to be found")
            assert False 
        else:
            print("Success: Confirmed that there were error logs to be found")
            assert True
   
    @pytest.mark.run(order=467)
    def test_467_cleanup_create_objects(self):
        response = ib_NIOS.wapi_request('GET', object_type="view?name=ಕನ್ನಡ", grid_vip=config.grid_vip)
        response=json.loads(response)[0]
        print(response)

        if 'view' in response['_ref']:
            del_ref=response['_ref']
            del_r = ib_NIOS.wapi_request('DELETE', object_type = del_ref)
            print(del_r)
            if 'view' in del_r:
                
                print("Custom View deletion successful")
                assert True
            else:
                print("FAILURE: Deleting custom view failed.")
                assert False

        
        print("Delete the auth zone")
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            reff = ref['_ref']
            del_ref = ib_NIOS.wapi_request('DELETE', object_type = reff)
            print(del_ref)
            if 'zone_auth' in del_ref:
                
                print("Auth zone deletion successful")
                assert True
            else:
                print("FAILURE: Deleting zone failed.")
                assert False
        
        restart_the_grid_Services()

    @pytest.mark.run(order=468)
    def test_468_NIOS_85565_start_infoblox_logs(self):
        print("Starting infoblox logs")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)

    @pytest.mark.run(order=469)
    def test_469_NIOS_85565_core_logs_validation(self):
	print("============================================")
        print("  reboot the GM")
        print("============================================")
        try:
	    child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
	    child.expect('password')
	    child.sendline('infoblox')
	    child.expect('Infoblox >')
	    child.sendline('reboot')
	    child.expect(':')
	    child.sendline('y')
	    sleep(120)
	    check_status(config.grid_vip)
        except Exception as error_message:
            print(error_message)
            assert False
        finally:
            child.close()


    @pytest.mark.run(order=470)
    def test_470_NIOS_85565_stop_infoblox_logs_var_logs(self):
        print("Starting infoblox logs")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)

    @pytest.mark.run(order=471)
    def test_471_NIOS_85565_validate_infoblox_log_message_for_cores(self):
        print("Validating Audit and debug log Messages for taking backup on local Computer")
        LookFor="core.splunkd.SIGABRT"
        logfinal = logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logfinal==None:
            print(logfinal)
            assert True
	else:
            print("Core files are observed")
            assert False


    @pytest.mark.run(order=472)
    def test_472_NIOS_85498_validate_infoblox_log_message_for_exit_code_11(self):
        print("Validating infoblox log for NIOS-85498")
        LookFor="Syncing reporting files from GM failed with exit code: 11!"
        logfinal = logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logfinal==None:
	    print(logfinal)
            assert True
	else:
            print("exit code 11 error is still observed")
            assert False

    @pytest.mark.run(order=473)
    def test_473_NIOS_79228_Add_a_Network(self):
        print("Add a network")
        data = {"network": "10.0.0.0/24"}
        response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data))
        print response
        print(response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True

    @pytest.mark.run(order=474)
    def test_474_NIOS_79228_Add_Network_Range(self):
        print("Add range inside Network")
        data = {"name":"range1","start_addr":"10.0.0.2","end_addr": "10.0.0.254","ddns_domainname":"demo.com","disable": False,"comment":"DHCP range comment"}
        response = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(data))
        print response
        print(response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True

    @pytest.mark.run(order=475)
    def test_475_NIOS_79228_start_infoblox_logs(self):
        print("Starting infoblox logs")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)

    @pytest.mark.run(order=476)
    def test_476_NIOS_79228_start_dhcp(self):
        print('Start dhcp service')
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties")
        print(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print("Enable DHCP service")
        data = {"enable_dhcp": True}
        response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
        sleep(40)
        print(response)
        if  response != None:
            print('DHCP service started')
            assert True
        else:
            print('DHCP service not started')
            assert False

    @pytest.mark.run(order=477)
    def test_477_NIOS_79228_stop_infoblox_logs_var_logs(self):
        print("Starting infoblox logs")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
 

    @pytest.mark.run(order=478)
    def test_478_NIOS_79228_validate_infoblox_log_message_for_dhcp_start_message(self):
        print("Validating infoblox log for NIOS-79228")
        LookFor="A DHCP Daemon monitoring failure has occured"
        logfinal = logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logfinal==None:
	    print(logfinal)
            assert True
	else:
            print("dhcp is not starting normally")
            assert False

    #reporting service should not be present
    @pytest.mark.run(order=479)
    def test_479_NIOS_87115_validate_download_support_bundle(self):
        print("validate download support bundle")
	#pdb.set_trace()
        path = os.getcwd()
        print(path)
        print(type(path))
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set transfer_supportbundle scp '+config.client_ip+' root infoblox dest '+path)
            child.expect(':')
            child.sendline("y")
            sleep(50)
            child.expect(".*scp succeeds.*Infoblox >")
            #print(child.before)
            assert True
        except:
            assert False
        finally:
            child.close()


    @pytest.mark.run(order=480)
    def test_480_NIOS_87115_validate_file_after_download_support_bundle(self):
	print("validate files after downloaded from support bundle")
        path = os.getcwd()
        print(path)
        print(type(path))
	cmd='tar -xvzf '+path+'/supportBundle.tar.gz'
        result1 = subprocess.check_output(cmd, shell=True)
	print("\n")
        cmd="ls "+path+"/infoblox/var/diag-infoblox.tar.gz | wc -l"
        result2 = subprocess.check_output(cmd, shell=True)
	print(result2)
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('ls /infoblox/var/diag-infoblox.tar.gz | wc -l')
        child.expect('#')
        result = child.before
        result = result.split(" ")
        print(result)
        error_log=result[-1][-12].strip("\n")
        print(error_log)
        child.close()
        if (int(error_log) == int(result2)):
            assert True
        else:
            assert False


    @pytest.mark.run(order=481)
    def test_481_NIOS_79228_Delete_Created_IPv4_network(self):
        print("\n==============================")
        print("Deleting created IPv4 Network")
        print("================================")
        network = ib_NIOS.wapi_request('GET',object_type="network?network=10.0.0.0/24")
        print(network)
        ref = json.loads(network)[0]['_ref']
        del_network=ib_NIOS.wapi_request('DELETE',object_type=ref)
        print(del_network)

    '''
    # NIOS-81599
    @pytest.mark.run(order=482)
    def test_482_NIOS_81599_Remove_IPv4_interface(self):
        """
        Make the grid2 as IPv6 Only Grid.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case  Started               |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Remove IPv4 interface and enable NIC bonding on Grid2")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member',grid_vip=config.grid2_master_vip)
        display_msg(get_ref)

        get_ref=json.loads(get_ref)
        print(get_ref[0]['_ref'])
        data = {"config_addr_type":"IPV6",
                "lan2_enabled":True,
                "lan2_port_setting":{"nic_failover_enabled":True}}
        response = ib_NIOS.wapi_request('PUT', ref=get_ref[0]['_ref'], fields=json.dumps(data), grid_vip=config.grid2_master_vip)
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: Operation failed")
            assert False
        display_msg("PASS: Grid2 became IPv6 only with NIC bonding enabled")
        sleep(300)
        
        # Validation
        display_msg()
        display_msg("+------------------------------------------+")
        display_msg("|           Validation                     |")
        display_msg("+------------------------------------------+")
        member_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=config_addr_type,lan2_enabled,lan2_port_setting',grid_vip="["+config.grid2_master_ipv6+"]")
        display_msg(member_ref)
        member_ref = json.loads(member_ref)
        if member_ref["config_addr_type"]=="IPV6" and member_ref["lan2_enabled"]==True and member_ref["lan2_port_setting"]["nic_failover_enabled"] == True:
            display_msg("PASS: Interface settings validated")
        else:
            display_msg("FAIL: Interface setting validation failed")
            assert False
        
    # NIOS-81599
    @pytest.mark.run(order=483)
    def test_483_NIOS_81599_Add_MGMT_interface(self):
        """
        Add MGMT interface with IPv4 and IPv6 address.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case Started               |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Adding MGMT interface")
        get_lab_info = parse_get_lab_info(config.grid2_master_vip)
        args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid2_master_ipv6
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        child.stdin.write("set interface mgmt\n")
        child.stdin.write("y\n")
        child.stdin.write(get_lab_info["MGMT_IPADDR"]+"\n")
        child.stdin.write(get_lab_info["MGMT_NETMASK"]+"\n")
        child.stdin.write("\n")
        child.stdin.write("y\n")
        child.stdin.write(get_lab_info["MGMT_IPV6ADDR"]+"\n")
        child.stdin.write("64\n")
        child.stdin.write(get_lab_info["MGMT_V6ROUTER"]+"\n")
        child.stdin.write("n\n")
        child.stdin.write("y\n")
        child.stdin.write("y\n")
        output = child.communicate()
        flag = False
        for line in output:
            display_msg(line)
            if 'The management port settings have been updated' in line:
                flag = True
        if flag:
            display_msg("PASS: MGMT interface added successfully")
        else:
            display_msg("FAIL: Failed to add MGMT interface due to above reason")
            assert False
        
    # NIOS-81599
    @pytest.mark.run(order=484)
    def test_484_NIOS_81599_Validate_DNS_stats(self):
        """
        Validate failure count in DNS stats.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case  Started               |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Validate failure count in DNS stats")
        flag = False
        args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid2_master_ipv6
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        child.stdin.write("show dns stats\n")
        child.stdin.write("q\n")
        output = child.communicate()
        for line in output:
            display_msg(line)
            if 'failure' in line:
                failure_count1 = int(line.split('')[-1].strip())
                flag = True
        
        if flag:
            display_msg("Sleeping for 60 seconds")
            sleep(60)
            display_msg("Validate failure count in DNS stats again")
            flag2 = False
            args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid2_master_ipv6
            args = shlex.split(args)
            child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            child.stdin.write("show dns stats\n")
            child.stdin.write("q\n")
            output = child.communicate()
            for line in output:
                display_msg(line)
                if 'failure' in line:
                    failure_count2 = int(line.split('')[-1].strip())
                    flag2 = True
            
            if flag2:
                if failure_count1 == failure_count2:
                    display_msg("PASS: No increment of failure count in DNS stats")
                else:
                    display_msg("FAIL: Failure count in DNS stats increasing without any queries")
                    assert False
            else:
                display_msg("FAIL: Not able to find failure count in output of 'show dns stats'")
                assert False
        else:
            display_msg("FAIL: Not able to find failure count in output of 'show dns stats'")
            assert False
        
    # NIOS-81599
    @pytest.mark.run(order=485)
    def test_485_NIOS_81599_Add_IPv4_interface_back(self):
        """
        Add IPv4 Interface back to the Grid2.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case  Started               |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Add IPv4 interface and disable NIC bonding on Grid2")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member',grid_vip="["+config.grid2_master_ipv6+"]")
        display_msg(get_ref)
        get_lab_info = parse_get_lab_info(config.grid2_master_vip)
        data = {"config_addr_type":"BOTH",
                "vip_setting":{"address":get_lab_info["LAN_IPADDR"] ,
                               "gateway":get_lab_info["LAN_ROUTER"] ,
                               "subnet_mask":get_lab_info["LAN_NETMASK"]},
                "lan2_enabled":False,
                "lan2_port_setting":{"nic_failover_enabled":False}
                }
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data), grid_vip="["+config.grid_vip_v6+"]")
        display_msg(response)
        if type(response) == tuple:
            display_msg("FAIL: Operation failed")
            assert False
        display_msg("PASS: Reverted Grid2 Interface settings")
        sleep(300)
        
    # NIOS-81599
    @pytest.mark.run(order=486)
    def test_486_NIOS_81599_Remove_MGMT_interface(self):
        """
        Remove MGMT interface added earlier.
        """
        display_msg()
        display_msg("+----------------------------------------------+")
        display_msg("|           Test Case  Started               |")
        display_msg("+----------------------------------------------+")
        
        display_msg("Removing MGMT interface")
        get_lab_info = parse_get_lab_info(config.grid2_master_vip)
        args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid2_master_ipv6
        args = shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        child.stdin.write("set interface mgmt\n")
        child.stdin.write("n\n")
        child.stdin.write("y\n")
        output = child.communicate()
        flag = False
        for line in output:
            display_msg(line)
            if 'Management port has been disabled' in line:
                flag = True
        if flag:
            display_msg("PASS: MGMT interface removed successfully")
        else:
            display_msg("FAIL: Failed to remove MGMT interface due to above reason")
            assert False
        
    '''
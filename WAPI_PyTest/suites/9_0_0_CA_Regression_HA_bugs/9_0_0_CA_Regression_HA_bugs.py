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
#from  ib_utils.log_capture import log_action as log
#from  ib_utils.log_validation import log_validation as logv
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
import pexpect
import paramiko
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="Bug_Automation_9_0.log" ,level=logging.INFO,filemode='w')




def print_and_log(arg=""):
	print(arg)
	logging.info(arg)


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


def Perform_Dig_queires(ip):
    output = os.popen("dig @" + ip + " a.dtc.com in a +short").read()
    Server_That_Responded = output.strip(" ").split("\n")[0]
    return Server_That_Responded


def dtc_object_failback_disable_options(data):
    response = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data), params="?_function=dtc_object_disable")
    print_and_log(response)
    output = json.loads(response)
    output = output['failback_status']
    return output


def dtc_object_failback_enable_options(data):
    response = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data), params="?_function=dtc_object_enable")
    print_and_log(response)
    output = json.loads(response)
    output = output['failback_status']
    return output

def dtc_object_failback_status(data):
    response = ib_NIOS.wapi_request('POST', object_type="dtc", fields=json.dumps(data), params="?_function=dtc_get_object_grid_state")
    response = json.loads(response)
    output = response['enabled_on']
    return output


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

def display_msg(msg):
    print(msg)
    logging.info(msg)

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


class bug_automation_9_0(unittest.TestCase):


    @pytest.mark.run(order=1)
    def test_001_NIOS_86592_enable_dns_on_the_gird_and_member(self):
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
    def test_002_NIOS_86592_Validate_DNS_service_Enabled(self):
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



    #NIOS-86592
    @pytest.mark.run(order=3)
    def test_003_NIOS_86592_Run_the_CLI_Command_show_firware_on_Grid_master(self):
        print_and_log("************* Run the CLI Command show firmware on Grid master ***************")
        log("start", "/infoblox/var/infoblox.log", config.grid_vip)
        output = perform_show_firmware_cli_command(config.grid_vip, "show firmware")
        print_and_log(output)
        LookFor = ".*Can't open /infoblox/var/interface_info/eth0:: No such file or directory.*"
        log("stop", "/infoblox/var/infoblox.log", config.grid_vip)
        try:
            logs = logv(LookFor, "/infoblox/var/infoblox.log", config.grid_vip)
        except subprocess.CalledProcessError:
            print_and_log(" Error message is not seen in the logs ")
            assert True
        else:
            print_and_log(" Error message is seen in the logs ")
            assert False
        print_and_log("*********** Test Case 3 Execution Completed ************")

    @pytest.mark.run(order=4)
    def test_004_NIOS_86592_Run_the_CLI_Command_show_firware_on_Grid_member(self):
        print_and_log("************* Run the CLI Command show firmware on Grid member ***************")
        log("start", "/infoblox/var/infoblox.log", config.grid_member1_vip)
        output = perform_show_firmware_cli_command(config.grid_member1_vip, "show firmware")
        print_and_log(output)
        LookFor = ".*Can't open /infoblox/var/interface_info/eth0:: No such file or directory.*"
        log("stop", "/infoblox/var/infoblox.log", config.grid_member1_vip)
        try:
            logs = logv(LookFor, "/infoblox/var/infoblox.log", config.grid_member1_vip)
        except subprocess.CalledProcessError:
            print_and_log(" Error message is not seen in the logs ")
            assert True
        else:
            print_and_log(" Error message is seen in the logs ")
            assert False
        print_and_log("*********** Test Case 4 Execution Completed ************")



    #NIOS-86469
    @pytest.mark.run(order=5)
    def test_005_NIOS_86469_Run_the_CLI_Command_set_transfer_supportbundle_using_scp_on_Grid_master(self):
        print_and_log("************* Run the CLI Command set transfer supportbundle using scp on Grid master ***************")
        log("start", "/infoblox/var/infoblox.log", config.grid_vip)
        cmd = "set transfer_supportbundle scp "+config.scp_ip+" "+config.scp_username+" "+config.scp_password+" "+"dest "+config.scp_dest_path+" core_files current_logs rotated_logs"
        print_and_log(cmd)
        output = perform_set_transfer_supportbundle_cli_command(config.grid_vip, cmd)
        print_and_log(output)
        LookFor = ".*Can't open /infoblox/var/interface_info/eth0:: No such file or directory.*"
        log("stop", "/infoblox/var/infoblox.log", config.grid_vip)
        clean_up_supportbundle_files_on_the_client(config.scp_username, config.scp_ip, config.scp_dest_path, config.scp_password)
        try:
            logs = logv(LookFor, "/infoblox/var/infoblox.log", config.grid_vip)
        except subprocess.CalledProcessError:
            print_and_log(" Error message is not seen in the logs ")
            assert True
        else:
            print_and_log(" Error message is seen in the logs ")
            assert False
        print_and_log("*********** Test Case 5 Execution Completed ************")

    @pytest.mark.run(order=6)
    def test_006_NIOS_86469_Run_the_CLI_Command_set_transfer_supportbundle_using_scp_on_Grid_member(self):
        print_and_log("************* Run the CLI Command set transfer supportbundle using scp on Grid member ***************")
        log("start", "/infoblox/var/infoblox.log", config.grid_member1_vip)
        cmd = "set transfer_supportbundle scp "+config.scp_ip+" "+config.scp_username+" "+config.scp_password+" "+"dest "+config.scp_dest_path+" core_files current_logs rotated_logs"
        output = perform_set_transfer_supportbundle_cli_command(config.grid_member1_vip, cmd)
        print_and_log(output)
        LookFor = ".*Can't open /infoblox/var/interface_info/eth0:: No such file or directory.*"
        log("stop", "/infoblox/var/infoblox.log", config.grid_member1_vip)
        clean_up_supportbundle_files_on_the_client(config.scp_username, config.scp_ip, config.scp_dest_path, config.scp_password)
        try:
            logs = logv(LookFor, "/infoblox/var/infoblox.log", config.grid_member1_vip)
        except subprocess.CalledProcessError:
            print_and_log(" Error message is not seen in the logs ")
            assert True
        else:
            print_and_log(" Error message is seen in the logs ")
            assert False
        print_and_log("*********** Test Case 6 Execution Completed ************")

    @pytest.mark.run(order=7)
    def test_007_NIOS_86469_Run_the_CLI_Command_set_transfer_supportbundle_using_ftp_on_Grid_master(self):
        print_and_log("************* Run the CLI Command set transfer supportbundle using ftp on Grid master ***************")
        log("start", "/infoblox/var/infoblox.log", config.grid_vip)
        cmd = "set transfer_supportbundle ftp "+config.ftp_ip+" "+config.ftp_username+" "+config.ftp_password+" "+"dest "+config.ftp_dest_path+" core_files current_logs rotated_logs"
        output = perform_set_transfer_supportbundle_cli_command(config.grid_vip, cmd)
        print_and_log(output)
        LookFor = ".*Can't open /infoblox/var/interface_info/eth0:: No such file or directory.*"
        log("stop", "/infoblox/var/infoblox.log", config.grid_vip)
        clean_up_supportbundle_files_on_the_client(config.ftp_username, config.ftp_ip, config.ftp_dest_path+".tar.gz", config.ftp_password)
        try:
            logs = logv(LookFor, "/infoblox/var/infoblox.log", config.grid_vip)
        except subprocess.CalledProcessError:
            print_and_log(" Error message is not seen in the logs ")
            assert True
        else:
            print_and_log(" Error message is seen in the logs ")
            assert False
        print_and_log("*********** Test Case 7 Execution Completed ************")

    @pytest.mark.run(order=8)
    def test_008_NIOS_86469_Run_the_CLI_Command_set_transfer_supportbundle_using_ftp_on_Grid_member(self):
        print_and_log("************* Run the CLI Command set transfer supportbundle using ftp on Grid member ***************")
        log("start", "/infoblox/var/infoblox.log", config.grid_member1_vip)
        cmd = "set transfer_supportbundle ftp "+config.ftp_ip+" "+config.ftp_username+" "+config.ftp_password+" "+"dest "+config.ftp_dest_path+" core_files current_logs rotated_logs"
        output = perform_set_transfer_supportbundle_cli_command(config.grid_member1_vip, cmd)
        print_and_log(output)
        LookFor = ".*Can't open /infoblox/var/interface_info/eth0:: No such file or directory.*"
        log("stop", "/infoblox/var/infoblox.log", config.grid_member1_vip)
        clean_up_supportbundle_files_on_the_client(config.ftp_username, config.ftp_ip, config.ftp_dest_path+".tar.gz", config.ftp_password)
        try:
            logs = logv(LookFor, "/infoblox/var/infoblox.log", config.grid_member1_vip)
        except subprocess.CalledProcessError:
            print_and_log(" Error message is not seen in the logs ")
            assert True
        else:
            print_and_log(" Error message is seen in the logs ")
            assert False
        print_and_log("*********** Test Case 8 Execution Completed ************")

    @pytest.mark.run(order=9)
    def test_009_NIOS_86400_create_AuthZone(self):
        print_and_log("************ Create auth Zone dtc.com *************")
        data = {"fqdn": "dtc.com", "grid_primary": [{"name": config.grid_member_fqdn, "stealth": False}, {"name": config.grid_member1_fqdn, "stealth": False}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
        print_and_log(response)
        assert re.search("dtc.com", response)
        print_and_log("Restart DNS Services")
        restart_the_grid_Services()
        print_and_log("*********** Test Case 9 Execution Completed ************")

    @pytest.mark.run(order=10)
    def test_010_NIOS_86400_Validate_AuthZone(self):
        print_and_log("************ Validate the Zone dtc.com *************")
        response = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=dtc.com", grid_vip=config.grid_vip)
        print_and_log(response)
        if ('"fqdn": "dtc.com"' in response):
            print_and_log("Auth zone Created successfully")
            assert True
        else:
            print_and_log(" Error while validating the auth zone")
            assert False
        print_and_log("********** Test Case 10 Execution Completed ***********")


    #NIOS-86400
    @pytest.mark.run(order=11)
    def test_011_NIOS_86400_configure_two_dtc_servers(self):
        print_and_log("************ Configure 4 dtc servers ***************")
        global server_name
        global dtc_server_ips
        server_name = ["server1", "server2", "server3", "server4"]
        dtc_server_ips = check_pingable_ips_for_dtc_server_configuration(config.ip_range)
        print_and_log(dtc_server_ips)
        server_obj = {server_name[0]: dtc_server_ips[0], server_name[1]: dtc_server_ips[1], server_name[2]: dtc_server_ips[2], server_name[3]: dtc_server_ips[3]}
        for i,j in server_obj.items():
            data = {"name": i, "host": j}
            response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
            print_and_log(response)
            assert re.search("dtc:server", response)
        print_and_log("*********** Test Case 11 Execution Completed ************")

    @pytest.mark.run(order=12)
    def test_012_NIOS_86400_validate_the_dtc_servers_created(self):
        print_and_log(" ************ Validate the dtc servers created *************** ")
        for i in server_name:
            servers = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name='+i)
            servers = json.loads(servers)
            dtc_server_name = servers[0]['name']
            if dtc_server_name == "server1":
                print_and_log("DTC server "+dtc_server_name+" created successfully")
                assert True
            elif dtc_server_name == "server2":
                print_and_log("DTC server " + dtc_server_name + " created successfully")
                assert True
            elif dtc_server_name == "server3":
                print_and_log("DTC server " + dtc_server_name + " created successfully")
                assert True
            elif dtc_server_name == "server4":
                print_and_log("DTC server " + dtc_server_name + " created successfully")
                assert True
            else:
                print_and_log("Error while validating the DTC servers")
                assert False
        print_and_log("*********** Test Case 12 Execution Completed ************")

    @pytest.mark.run(order=13)
    def test_013_NIOS_86400_Create_the_DTC_Pool_1_and_Assign_the_Server_members_server1_and_server2(self):
        print_and_log(" ************ Create the DTC pool and Assign the Server members *************** ")
        server_ref = []
        for i in server_name:
            response_servers = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name=' + i)
            response_servers = json.loads(response_servers)
            ref = response_servers[0]['_ref']
            server_ref.append(ref)
        health_monitor_ref = getting_ref_of_the_dtc_health_monitors("dtc:monitor:icmp")
        print_and_log(health_monitor_ref)
        data = {"name": "pool1", "lb_preferred_method": "ROUND_ROBIN", "servers": [{"ratio": 1, "server": str(server_ref[0])}, {"ratio": 1, "server": str(server_ref[1])}], "monitors": [str(health_monitor_ref)]}
        res = ib_NIOS.wapi_request('POST', object_type='dtc:pool', fields=json.dumps(data))
        print_and_log(res)
        assert re.search("dtc:pool", res)
        print_and_log(" ************ Test Case 13 Execution Completed *************** ")

    @pytest.mark.run(order=14)
    def test_014_NIOS_86400_validate_the_dtc_pool_1_created(self):
        print_and_log(" ************ Validate the dtc pool 1 created *************** ")
        response_servers = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool1')
        response_servers = json.loads(response_servers)
        print_and_log(response_servers)
        dtc_pool_name = response_servers[0]['name']
        if dtc_pool_name == "pool1":
            print_and_log("DTC Pool "+dtc_pool_name+" is created successfully")
            assert True
        else:
            print_and_log(" Error while validating the DTC Pool created")
            assert False
        print_and_log(" ************ Test Case 14 Execution Completed *************** ")

    @pytest.mark.run(order=15)
    def test_015_NIOS_86400_Create_the_DTC_Pool_2_and_Assign_the_Server_members_server3_and_server4(self):
        print_and_log(" ************ Create the DTC pool 2 and Assign the Server members Server 3 and Server 4 *************** ")
        server_ref = []
        for i in server_name:
            response_servers = ib_NIOS.wapi_request('GET', object_type='dtc:server', params='?name=' + i)
            response_servers = json.loads(response_servers)
            ref = response_servers[0]['_ref']
            server_ref.append(ref)
        health_monitor_ref = getting_ref_of_the_dtc_health_monitors("dtc:monitor:icmp")
        print_and_log(health_monitor_ref)
        data = {"name": "pool2", "lb_preferred_method": "ROUND_ROBIN",
                "servers": [{"ratio": 1, "server": str(server_ref[2])}, {"ratio": 1, "server": str(server_ref[3])}],
                "monitors": [str(health_monitor_ref)]}
        res = ib_NIOS.wapi_request('POST', object_type='dtc:pool', fields=json.dumps(data))
        print_and_log(res)
        assert re.search("dtc:pool", res)
        print_and_log(" ************ Test Case 15 Execution Completed *************** ")

    @pytest.mark.run(order=16)
    def test_016_NIOS_86400_validate_the_dtc_pool_2_created(self):
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
        print_and_log(" ************ Test Case 16 Execution Completed *************** ")

    @pytest.mark.run(order=17)
    def test_017_NIOS_86400_Create_the_LBDN1_with_priority_value_set_to_1(self):
        print_and_log(" ************ Create the DTC LBDN1 with priority value set to 1 ************ ")
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
        data = {"auth_zones": [ref_zone], "name": "DTC_LBDN_1", "priority": 1,"lb_method": "ROUND_ROBIN", "patterns": ["*.dtc.com"], "pools": [{"ratio": 1, "pool": ref_pool}]}
        print_and_log(data)
        response = ib_NIOS.wapi_request('POST', object_type='dtc:lbdn', fields=json.dumps(data))
        response = json.loads(response)
        print_and_log("Validation of lbdn creation")
        assert re.search(r'dtc:lbdn', response)
        print_and_log("******** Restart the DNS service *********")
        restart_the_grid_Services()
        print_and_log(" ************ Test Case 17 Execution Completed *************** ")

    @pytest.mark.run(order=18)
    def test_018_NIOS_86400_Validate_the_DTC_LBDN1_with_priority_value_set_to_1(self):
        print_and_log(" ************ Validate the DTC LBDN1 with priority value set to 1 ************ ")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        ref_lbdn = response[0]['_ref']
        print_and_log(ref_lbdn)
        dtc_lbdn_name = response[0]['name']
        print_and_log(dtc_lbdn_name)
        response = ib_NIOS.wapi_request('GET', object_type=ref_lbdn, params='?_return_fields=priority')
        response = json.loads(response)
        lbdn_priority = response['priority']
        print_and_log(lbdn_priority)
        if dtc_lbdn_name == "DTC_LBDN_1" and lbdn_priority == 1:
            print_and_log("DTC LBDN " + dtc_lbdn_name + " with priority " + str(lbdn_priority) + " configured successfully")
            assert True
        else:
            print_and_log("Validation for the DTC LBDN 1 failed")
            assert False
        print_and_log(" ************ Test Case 18 Execution Completed *************** ")

    @pytest.mark.run(order=19)
    def test_019_NIOS_86400_Perform_the_dig_command_and_verify_the_response_is_from_dtc_Server1(self):
        print_and_log("********** Perform the dig command and verify the response on Grid master ************")
        Server_That_Responded = Perform_Dig_queires(config.grid_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[0]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("********** Perform the dig command and verify the response on Grid member ************")
        Server_That_Responded = Perform_Dig_queires(config.grid_member1_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[0]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("********* Test Case 19 Execution Completed *************")

    @pytest.mark.run(order=20)
    def test_020_NIOS_86400_Perform_the_dig_command_and_verify_the_response_is_from_dtc_Server2(self):
        print_and_log("********** Perform the dig command and verify the response on Grid master ************")
        Server_That_Responded = Perform_Dig_queires(config.grid_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[1]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("********** Perform the dig command and verify the response on Grid member ************")
        Server_That_Responded = Perform_Dig_queires(config.grid_member1_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[1]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("Test Case 20 Execution Completed")

    @pytest.mark.run(order=21)
    def test_021_NIOS_86400_Create_the_LBDN2_with_priority_value_set_to_2(self):
        print_and_log(" ************ Create the DTC LBDN2 with priority value set to 2 ************ ")
        print_and_log("Getting ref of auth zone dtc.com")
        response = ib_NIOS.wapi_request('GET', object_type='zone_auth', params='?fqdn=dtc.com')
        response = json.loads(response)
        ref_zone = response[0]['_ref']
        print_and_log(ref_zone)
        print_and_log("********** Getting the ref of pool ************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:pool', params='?name=pool2')
        response = json.loads(response)
        ref_pool = response[0]['_ref']
        print_and_log(ref_pool)
        print_and_log("********** Creating the lbdn by post request ************")
        data = {"auth_zones": [ref_zone], "name": "DTC_LBDN_2", "priority": 2, "lb_method": "ROUND_ROBIN", "patterns": ["*.dtc.com"], "pools": [{"ratio": 1, "pool": ref_pool}]}
        print_and_log(data)
        response = ib_NIOS.wapi_request('POST', object_type='dtc:lbdn', fields=json.dumps(data))
        response = json.loads(response)
        print_and_log("Validation of lbdn creation")
        assert re.search(r'dtc:lbdn', response)
        print_and_log("******** Restart the DNS service *********")
        restart_the_grid_Services()
        print_and_log(" ************ Test Case 21 Execution Completed *************** ")

    @pytest.mark.run(order=22)
    def test_022_NIOS_86400_Validate_the_DTC_LBDN2_with_priority_value_set_to_2(self):
        print_and_log(" ************ Validate the DTC LBDN2 with priority value set to 2 ************ ")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_2')
        response = json.loads(response)
        ref_lbdn = response[0]['_ref']
        print_and_log(ref_lbdn)
        dtc_lbdn_name = response[0]['name']
        print_and_log(dtc_lbdn_name)
        response = ib_NIOS.wapi_request('GET', object_type=ref_lbdn, params='?_return_fields=priority')
        response = json.loads(response)
        lbdn_priority = response['priority']
        print_and_log(lbdn_priority)
        if dtc_lbdn_name == "DTC_LBDN_2" and lbdn_priority == 2:
            print_and_log("DTC LBDN "+dtc_lbdn_name+" with priority "+ str(lbdn_priority) +" configured successfully")
            assert True
        else:
            print_and_log("Validation for the DTC LBDN 2 failed")
            assert False
        print_and_log(" ************ Test Case 22 Execution Completed *************** ")

    @pytest.mark.run(order=23)
    def test_023_NIOS_86400_Perform_the_dig_command_and_verify_the_response_is_from_dtc_Server1_after_configuring_the_second_lbdn_on_grid_master(self):
        print_and_log("********** Perform the dig command and verify the response is from dtc Server1 after configuring the second lbdn on grid master ************")
        Server_That_Responded = Perform_Dig_queires(config.grid_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[0]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("********** Perform the dig command and verify the response is from dtc Server1 after configuring the second lbdn on grid member ************")
        Server_That_Responded = Perform_Dig_queires(config.grid_member1_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[0]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("Test Case 23 Execution Completed")

    @pytest.mark.run(order=24)
    def test_024_NIOS_86400_Perform_the_dig_command_and_verify_the_response_is_from_dtc_Server2_after_configuring_the_second_lbdn_on_grid_member(self):
        print_and_log("********** Perform the dig command and verify the response is from dtc Server2 after configuring the second lbdn on grid master ************")
        Server_That_Responded = Perform_Dig_queires(config.grid_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[1]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("********** Perform the dig command and verify the response is from dtc Server2 after configuring the second lbdn on grid member ************")
        Server_That_Responded = Perform_Dig_queires(config.grid_member1_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[1]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("Test Case 24 Execution Completed")

    @pytest.mark.run(order=25)
    def test_025_NIOS_86400_Disable_the_LBDN_1_With_Disable_until_Manual_Enable_option(self):
        print_and_log("*********** Disable the LBDN 1 With Disable until Manual Enable option *************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        ref_lbdn = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10, "disable_on": [config.grid_fqdn, config.grid_member1_fqdn], "disable_timeframe": "UNTIL_MANUAL_ENABLING", "dtc_object": ref_lbdn, "specific_time_disable": 60}
        output = dtc_object_failback_disable_options(data)
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC LBDN object disabled successfully")
            assert True
        else:
            print_and_log("DTC LBDN object is not Disabled")
            assert False
        print_and_log("Test Case 25 Execution Completed")

    @pytest.mark.run(order=26)
    def test_026_NIOS_86400_Perform_the_dig_command_and_verify_the_response_is_from_dtc_Server3(self):
        print_and_log("********** Perform the dig command and verify the response is from DTC server3 on Grid master ************")
        Server_That_Responded = Perform_Dig_queires(config.grid_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[2]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("********** Perform the dig command and verify the response is from DTC server3 on Grid member ************")
        Server_That_Responded = Perform_Dig_queires(config.grid_member1_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[2]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("Test Case 26 Execution Completed")

    @pytest.mark.run(order=27)
    def test_027_NIOS_86400_Perform_the_dig_command_and_verify_the_response_is_from_dtc_Server4(self):
        print_and_log("********** Perform the dig command and verify the response is from DTC server4 on Grid master ************")
        Server_That_Responded = Perform_Dig_queires(config.grid_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[3]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("********** Perform the dig command and verify the response is from DTC server4 on Grid member ************")
        Server_That_Responded = Perform_Dig_queires(config.grid_member1_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[3]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("Test Case 27 Execution Completed")

    @pytest.mark.run(order=28)
    def test_028_NIOS_86400_Enable_the_LBDN_1_with_Manual_Enable_option(self):
        print_and_log("*********** Enable the LBDN 1 With Manual Enable option *************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        ref_lbdn = response[0]['_ref']
        data = {"enable_on": [config.grid_fqdn, config.grid_member1_fqdn], "dtc_object": ref_lbdn}
        output = dtc_object_failback_enable_options(data)
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC LBDN object Enabled successfully")
            assert True
        else:
            print_and_log("DTC LBDN object is not enabled")
            assert False
        print_and_log("Test Case 28 Execution Completed")

    @pytest.mark.run(order=29)
    def test_029_NIOS_86400_Disable_the_LBDN_1_With_Disable_until_DNS_Restart(self):
        print_and_log("*********** Disable the LBDN 1 With Disable until DNS restart *************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        ref_lbdn = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10,
                "disable_on": [config.grid_fqdn, config.grid_member1_fqdn],
                "disable_timeframe": "UNTIL_DNS_RESTART", "dtc_object": ref_lbdn, "specific_time_disable": 60}
        output = dtc_object_failback_disable_options(data)
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC LBDN object disabled successfully")
            assert True
        else:
            print_and_log("DTC LBDN object is not Disabled")
            assert False
        print_and_log("Test Case 29 Execution Completed")

    @pytest.mark.run(order=30)
    def test_030_NIOS_86400_Perform_the_dig_command_and_verify_the_response_is_from_dtc_Server3(self):
        print_and_log("********** Perform the dig command and verify the response is from DTC server3 on Grid master ************")
        Server_That_Responded = Perform_Dig_queires(config.grid_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[2]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("********** Perform the dig command and verify the response is from DTC server3 on Grid member ************")
        Server_That_Responded = Perform_Dig_queires(config.grid_member1_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[2]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("Test Case 30 Execution Completed")

    @pytest.mark.run(order=31)
    def test_031_NIOS_86400_Perform_the_dig_command_and_verify_the_response_is_from_dtc_Server4(self):
        print_and_log("********** Perform the dig command and verify the response is from DTC server4 on Grid master ************")
        Server_That_Responded = Perform_Dig_queires(config.grid_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[3]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("********** Perform the dig command and verify the response is from DTC server4 on Grid member ************")
        Server_That_Responded = Perform_Dig_queires(config.grid_member1_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[3]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("Test Case 31 Execution Completed")

    @pytest.mark.run(order=32)
    def test_032_NIOS_86400_Perform_the_DNS_Restart_and_validate_the_LBDN_status(self):
        print_and_log("*********** Perform the DNS Restart and validate the LBDN status ***********")
        restart_the_grid_Services()
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        ref_lbdn = response[0]['_ref']
        data = {"dtc_object": ref_lbdn}
        output = dtc_object_failback_status(data)
        print_and_log(output)
        if config.grid_fqdn in output and config.grid_member1_fqdn in output:
            print_and_log("DTC LBDN object is enabled")
            assert True
        else:
            print_and_log("DTC LBDN object is not enabled")
            assert False
        print_and_log("Test Case 32 Execution Completed")

    @pytest.mark.run(order=33)
    def test_033_NIOS_86400_Disable_the_LBDN_1_With_Disable_until_Specified_time(self):
        print_and_log("*********** Disable the LBDN 1 With Disable until Specified time *************")
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        ref_lbdn = response[0]['_ref']
        data = {"disable_health_monitoring": False, "delayed_disable": False, "delayed_disable_time": 10,
                "disable_on": [config.grid_fqdn, config.grid_member1_fqdn],
                "disable_timeframe": "FOR_SPECIFIED_TIME", "dtc_object": ref_lbdn, "specific_time_disable": 300}
        output = dtc_object_failback_disable_options(data)
        print_and_log(output)
        if output == "SUCCESS":
            print_and_log("DTC LBDN object disabled successfully")
            assert True
        else:
            print_and_log("DTC LBDN object is not Disabled")
            assert False
        print_and_log("Test Case 33 Execution Completed")

    @pytest.mark.run(order=34)
    def test_034_NIOS_86400_Perform_the_dig_command_and_verify_the_response_is_from_dtc_Server3(self):
        print_and_log("********** Perform the dig command and verify the response is from DTC server3 on Grid master ************")
        Server_That_Responded = Perform_Dig_queires(config.grid_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[2]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("********** Perform the dig command and verify the response is from DTC server3 on Grid member ************")
        Server_That_Responded = Perform_Dig_queires(config.grid_member1_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[2]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("Test Case 34 Execution Completed")

    @pytest.mark.run(order=35)
    def test_035_NIOS_86400_Perform_the_dig_command_and_verify_the_response_is_from_dtc_Server4(self):
        print_and_log("********** Perform the dig command and verify the response is from DTC server4 on Grid master ************")
        Server_That_Responded = Perform_Dig_queires(config.grid_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[3]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("********** Perform the dig command and verify the response is from DTC server4 on Grid member ************")
        Server_That_Responded = Perform_Dig_queires(config.grid_member1_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[3]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("Test Case 35 Execution Completed")

    @pytest.mark.run(order=36)
    def test_036_NIOS_86400_wait_for_300_seconds_and_validate_the_LBDN_status(self):
        print_and_log("*********** Wait for 300 seconds and validate the LBDN status ***********")
        sleep(300)
        response = ib_NIOS.wapi_request('GET', object_type='dtc:lbdn', params='?name=DTC_LBDN_1')
        response = json.loads(response)
        ref_lbdn = response[0]['_ref']
        data = {"dtc_object": ref_lbdn}
        output = dtc_object_failback_status(data)
        print_and_log(output)
        if config.grid_fqdn in output and config.grid_member1_fqdn in output:
            print_and_log("DTC LBDN object is enabled")
            assert True
        else:
            print_and_log("DTC LBDN object is not enabled")
            assert False
        print_and_log("Test Case 36 Execution Completed")



    @pytest.mark.run(order=37)
    def test_037_NIOS_86400_Perform_the_dig_command_on_Grid_master_and_verify_the_response_is_from_dtc_Server1_after_Enabling_the_first_lbdn(self):
        print_and_log("********** Perform the dig command on Grid master and verify the response is from dtc Server1 after enabling the first lbdn ************")
        Server_That_Responded = Perform_Dig_queires(config.grid_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[0]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("*********** Perform the dig command on Grid member and verify the response is from dtc Server1 after enabling the first lbdn ************")
        Server_That_Responded = Perform_Dig_queires(config.grid_member1_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[0]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("Test Case 37 Execution Completed")

    @pytest.mark.run(order=38)
    def test_038_NIOS_86400_Perform_the_dig_command_on_Grid_member_and_verify_the_response_is_from_dtc_Server2_after_Enabling_the_first_lbdn(self):
        print_and_log("********** Perform the dig command on Grid master and verify the response is from dtc Server2 after enabling the first lbdn ************")
        Server_That_Responded = Perform_Dig_queires(config.grid_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[1]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("********** Perform the dig command on Grid member and verify the response is from dtc Server2 after enabling the first lbdn ************")
        Server_That_Responded = Perform_Dig_queires(config.grid_member1_vip)
        print_and_log(Server_That_Responded)
        if Server_That_Responded == dtc_server_ips[1]:
            print_and_log("Server " + Server_That_Responded + " responded for the query")
            assert True
        else:
            print_and_log("Different server responded to the query")
            assert False
        print_and_log("Test Case 38 Execution Completed")



    @pytest.mark.run(order=39)
    def test_039_NIOS_86222_Check_if_LDAP_service_is_up_and_running_on_the_authentication_server_else_start_the_service(self):
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


    @pytest.mark.run(order=40)
    def test_040_NIOS_86222_Add_DNS_resolver(self):
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

    @pytest.mark.run(order=41)
    def test_041_NIOS_86222_Upload_LDAP_CA_cert(self):
        dir_name="certificate/"
        base_filename="ldap_ca_cert.pem"
        token = common_util.generate_token_from_file(dir_name,base_filename)
        print(token)
        data = {"token": token, "certificate_usage":"EAP_CA"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadcertificate")
        print(response)

    @pytest.mark.run(order=42)
    def test_042_NIOS_86222_Configure_LDAP_server_details_in_the_grid(self):
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

    @pytest.mark.run(order=43)
    def test_043_NIOS_86222_Add_LDAP_to_the_Authentiation_Policy_list(self):
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


    @pytest.mark.run(order=44)
    def test_044_NIOS_86222_Assign_remote_users_admin_group_as_superuser(self):
        map_remote_user_to_the_group()


    @pytest.mark.run(order=45)
    def test_045_NIOS_86222_Login_to_the_grid_using_LDAP_credentials_and_execute_cli_command(self):
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

    @pytest.mark.run(order=46)
    def test_046_NIOS_86222_Verify_logs_for_LDAP_user_login_as_superuser(self):
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



    @pytest.mark.run(order=47)
    def test_047_NIOS_86222_Remove_LDAP_from_the_Authentiation_Policy_list(self):
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


    @pytest.mark.run(order=48)
    def test_048_NIOS_86222_Change_the_LDAP_settings_to_use_SSL_login_with_fqdn_as_ip_address(self):
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



    @pytest.mark.run(order=49)
    def test_049_NIOS_86222_Add_LDAP_to_the_Authentiation_Policy_list(self):
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

    @pytest.mark.run(order=50)
    def test_050_NIOS_86222_Try_logging_in_with_LDAP_credentials_using_CLI_negative_case(self):

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

    @pytest.mark.run(order=51)
    def test_051_NIOS_86222_Verify_logs_for_LDAP_user_login_as_superuser(self):
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



    @pytest.mark.run(order=52)
    def test_052_NIOS_86222_Remove_LDAP_from_the_Authentiation_Policy_list(self):
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


    @pytest.mark.run(order=53)
    def test_053_NIOS_86222_Change_the_LDAP_settings_to_use_SSL_login_with_fqdn_as_hostname(self):
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



    @pytest.mark.run(order=54)
    def test_054_NIOS_86222_Add_LDAP_to_the_Authentiation_Policy_list(self):
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

'''
    @pytest.mark.run(order=55)
    def test_055_NIOS_86222_Check_if_error_logs_are_observed(self):
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
'''

__author__ = "Aditya G"
__email__  = "adityag@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. SA Grid Master                                                                   #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1425)                                      #
########################################################################################


import config
import pytest
import unittest
import logging
import json
import os
import re
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as ib_TOKEN
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
from time import sleep
import pexpect
import subprocess

logging.basicConfig(filename='cas.log', filemode='w', level=logging.DEBUG)

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



class CAS(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_001_Check_if_RADIUS_service_is_up_and_running_on_the_authentication_server_else_start_the_service(self):
        display_msg("Checking if the RADIUS service is up and running on the authentication server, else, start the service")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.auth_server,timeout=300)
        except pexpect.TIMEOUT:
            display_msg("Unable to connect to the auth server, please check connectivity to the auth server")
            assert False
        else:
            child.expect("password:")
            child.sendline("infoblox")
            child.expect(" ~]#")
            child.sendline("ps ax|grep radius")
            output = child.before
            child.expect(" ~]#")
            output = child.before
            print(output)
            output = re.sub(r'\x1b\[([0-9,A-Z]{1,2}(;[0-9]{1,2})?(;[0-9]{3})?)?[m|K]?', '', output)
            print(output.split())
            if '/usr/sbin/radiusd' in output:
                display_msg("Radius service is running on the auth server")
                child.close()
                assert True
            else:
                display_msg("Radius service is not running on the auth server, proceeding further to start the radius service")
                try:
                    child.sendline("service radiusd start")
                except pexpect.ExceptionPexpect as error:
                    display_msg("Unable to start radius service")
                    display_msg(error)
                    assert False
                else:
                    sleep(20)
                    child.expect(" ~]#")
                    child.sendline("service radiusd status --no-pager")
                    output = child.before
                    child.expect(" ~]#")
                    output = child.before
                    print(output)
                    if 'active (running)' in output:
                        display_msg("Radius service running successfully")
                        child.close()
                        assert True
                    else:
                        display_msg("Radius service status is not active, please check the below output and debug")
                        display_msg(output)
                        child.close()
                        assert False


    
    @pytest.mark.run(order=2)
    def test_002_Check_if_TACACS_service_is_up_and_running_on_the_authentication_server_else_start_the_service(self):
        display_msg("Checking if the TACACS service is up and running on the authentication server, else, start the service")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.auth_server,timeout=300)
        except pexpect.TIMEOUT:
            display_msg("Unable to connect to the auth server, please check connectivity to the auth server")
            assert False
        else:
            child.expect("password:")
            child.sendline("infoblox")
            child.expect(" ~]#")
            child.sendline("ps ax|grep tac")
            output = child.before
            child.expect(" ~]#")
            output = child.before
            print(output)
            output = re.sub(r'\x1b\[([0-9,A-Z]{1,2}(;[0-9]{1,2})?(;[0-9]{3})?)?[m|K]?', '', output)
            print(output.split())
            if '/usr/bin/tac_plus' in output:
                display_msg("TACACS service is running on the auth server")
                child.close()
                assert True
            else:
                display_msg("TACACS service is not running on the auth server, proceeding further to start the TACACS service")
                try:
                    child.sendline("/usr/bin/tac_plus -C /etc/tac_plus.conf -d 16 -l /root/tacacs.log")
                except pexpect.ExceptionPexpect as error:
                    display_msg("Unable to start TACACS service")
                    display_msg(error)
                    assert False
                else:
                    sleep(20)
                    child.expect(" ~]#")
                    child.sendline("ps ax|grep tac")
                    output = child.before
                    child.expect(" ~]#")
                    output = child.before
                    print(output)
                    output = re.sub(r'\x1b\[([0-9,A-Z]{1,2}(;[0-9]{1,2})?(;[0-9]{3})?)?[m|K]?', '', output)
                    if '/usr/bin/tac_plus' in output:
                        display_msg("TACACS service running successfully")
                        child.close()
                        assert True
                    else:
                        display_msg("TACACS service status is not active, please check the below output and debug")
                        display_msg(output)
                        child.close()
                        assert False



    
    @pytest.mark.run(order=3)
    def test_003_Check_if_LDAP_service_is_up_and_running_on_the_authentication_server_else_start_the_service(self):
        display_msg("Checking if the LDAP service is up and running on the authentication server, else, start the service")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.auth_server,timeout=300)
        except pexpect.TIMEOUT:
            display_msg("Unable to connect to the auth server, please check connectivity to the auth server")
            assert False
        else:
            child.expect("password:")
            child.sendline("infoblox")
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

    @pytest.mark.run(order=4)
    def test_004_Check_if_AD_server_is_reachable(self):
        display_msg("Check if AD server is reachable")
        try:
            subprocess.check_output(["ping", "-c", "5", config.ad_ip])
        except subprocess.CalledProcessError:
            display_msg("AD server is not rechable, contact the lab team to power it on")
            assert False
        else:
            display_msg("AD server is reachable")
            assert True

    

    @pytest.mark.run(order=5)
    def test_005_Create_a_non_super_user_group(self):
        display_msg("Creating a non super user group")
        data={"name":"non-superuser","access_method": ["API","CLI"]}
        response = ib_NIOS.wapi_request('POST',object_type="admingroup",fields=json.dumps(data))
        display_msg(response)
        if bool(re.match("\"admingroup*.",str(response))):
            display_msg("Group 'non-superuser' created successfully")
            assert True
        else:
            display_msg("Group 'non-superuser' creation unsuccessful")
            assert False


    @pytest.mark.run(order=6)
    def test_006_Create_a_group_named_infobloxgroup(self):
        display_msg("Creating a group named 'infobloxgroup'")
        data={"name":"infobloxgroup","superuser":True}
        response = ib_NIOS.wapi_request('POST',object_type="admingroup",fields=json.dumps(data))
        display_msg(response)
        if bool(re.match("\"admingroup*.",str(response))):
            display_msg("Group 'infobloxgroup' created successfully")
            assert True
        else:
            display_msg("Group 'infobloxgroup' creation unsuccessful")
            assert False



    @pytest.mark.run(order=7)
    def test_007_Create_a_group_named_asmgroup(self):
        display_msg("Creating a group named 'asmgroup'")
        data={"name":"asmgroup","superuser":True}
        response = ib_NIOS.wapi_request('POST',object_type="admingroup",fields=json.dumps(data))
        display_msg(response)
        if bool(re.match("\"admingroup*.",str(response))):
            display_msg("Group 'asmgroup' created successfully")
            assert True
        else:
            display_msg("Group 'asmgroup' creation unsuccessful")
            assert False


    @pytest.mark.run(order=8)
    def test_008_Configure_RADIUS_server_details_in_the_grid(self):
        display_msg("Configuring RADIUS server details in the grid")
        data={
                "name": "radius",
                "servers": [
                    {
                        "address": config.auth_server,
                        "auth_port": 1812,
                        "auth_type": "PAP",
                        "shared_secret": "testing123",
                        "use_accounting": False
                    }
                ]
            }
        response = ib_NIOS.wapi_request('POST', object_type="radius:authservice",fields=json.dumps(data))
        display_msg(response)
        if bool(re.match("\"radius:authservice*.",str(response))):
            display_msg("RADIUS service configured sucessfully")
            assert True
        else:
            display_msg("RADIUS service configuration failed")
            assert False

    @pytest.mark.run(order=9)
    def test_009_Configure_TACACS_server_details_in_the_grid(self):
        display_msg("Configuring TACACS server details in the grid")
        data={
                "name": "tacacs",
                "servers": [
                    {
                        "address": config.auth_server,
                        "shared_secret": "testing123"
                    }
                ]
            }
        response = ib_NIOS.wapi_request('POST', object_type="tacacsplus:authservice",fields=json.dumps(data))
        display_msg(response)
        if bool(re.match("\"tacacsplus:authservice*.",str(response))):
            display_msg("TACACS service configured sucessfully")
            assert True
        else:
            display_msg("TACACS service configuration failed")
            assert False



    @pytest.mark.run(order=10)
    def test_010_Configure_LDAP_server_details_in_the_grid(self):
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




    @pytest.mark.run(order=11)
    def test_011_Configure_AD_server_details_in_the_grid(self):
        display_msg("Configuring AD server details in the grid")
        data={
                "name": "adserver",
                "ad_domain": config.ad_domain,
                "domain_controllers": [
                    {
                        "auth_port": 389,
                        "disabled": False,
                        "fqdn_or_ip": config.ad_ip,
                        "encryption": "NONE",
                        "use_mgmt_port": False
                    }
                ]
            }
        response = ib_NIOS.wapi_request('POST', object_type="ad_auth_service",fields=json.dumps(data))
        display_msg(response)
        if bool(re.match("\"ad_auth_service*.",str(response))):
            display_msg("AD service configured sucessfully")
            assert True
        else:
            display_msg("AD service configuration failed")
            assert False


    @pytest.mark.run(order=12)
    def test_012_Add_RADIUS_TACACS_LDAP_AD_to_the_Authentiation_Policy_list(self):
        display_msg("Adding RADIUS, TACACS, LDAP and AD service to the authentication policy")
        
        display_msg("Fetch Authentication policy ref")
        response = ib_NIOS.wapi_request('GET',object_type='authpolicy')
        auth_policy_ref = json.loads(response)[0]['_ref']
        display_msg("Authentication Policy ref: "+auth_policy_ref)
        
        display_msg("Fetch local user ref")
        response = ib_NIOS.wapi_request('GET',object_type='authpolicy?_return_fields=auth_services')
        local_user_ref = json.loads(response)[0]['auth_services'][0]
        display_msg("Local user ref: "+local_user_ref)
        
        display_msg("Fetch RADIUS server ref")
        response = ib_NIOS.wapi_request('GET', object_type="radius:authservice")
        radius_ref = json.loads(response)[0]['_ref']
        display_msg("RADIUS server ref : "+radius_ref)


        display_msg("Fetch TACACS server ref")
        response = ib_NIOS.wapi_request('GET', object_type="tacacsplus:authservice")
        tacacs_ref = json.loads(response)[0]['_ref']
        display_msg("TACACS server ref : "+tacacs_ref)
        

        display_msg("Fetch LDAP server ref")
        response = ib_NIOS.wapi_request('GET', object_type="ldap_auth_service")
        ldap_ref = json.loads(response)[0]['_ref']
        display_msg("LDAP server ref : "+ldap_ref)


        display_msg("Fetch AD server ref")
        response = ib_NIOS.wapi_request('GET', object_type="ad_auth_service")
        ad_ref = json.loads(response)[0]['_ref']
        display_msg("AD server ref : "+ad_ref)


        display_msg("Add Local, RADIUS, TACACS, LDAP and AD server to the authentiation policy list")
        data={"auth_services":[local_user_ref,radius_ref,tacacs_ref,ldap_ref,ad_ref]}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=auth_policy_ref)
        display_msg(response)
        if bool(re.match("\"authpolicy*.",str(response))):
            display_msg("Local, RADIUS, TACACS, LDAP and AD server added to the authentiation policy list successfully")
            sleep(10)
            assert True
        else:
            display_msg("Local, RADIUS, TACACS, LDAP and AD server addition to the authentiation policy list failed")
            assert False



    @pytest.mark.run(order=13)
    def test_013_Assign_remote_users_admin_group_as_superuser(self):
        map_remote_user_to_the_group()

    
    @pytest.mark.run(order=14)
    def test_014_Login_to_the_grid_using_RADIUS_credentials_as_superuser_and_execute_cli_command(self):
        display_msg("Logging into the grid using RADIUS credentials via CLI as a superuser")
        display_msg("Starting log capture")
        log("start","/var/log/syslog",config.grid_vip)
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/infoblox/var/audit.log",config.grid_vip)
        sleep(10)
        display_msg("Logging into the grid")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+config.radius_username+'@'+config.grid_vip,timeout=300)
        except pexpect.TIMEOUT:
            display_msg("Unable to connect to the grid, please check connectivity to the grid")
            assert False
        else:
            child.expect("password:")
            child.sendline(config.radius_password)
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


    @pytest.mark.run(order=15)
    def test_015_Verify_logs_for_RADIUS_user_login_as_superuser(self):
        display_msg("Verify logs for RADIUS user login as superuser")
        sleep(20)
        display_msg("Stopping log capture")

        log("stop","/var/log/syslog",config.grid_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/infoblox/var/audit.log",config.grid_vip)
        
        count=0
        display_msg("Verifying syslog for the authentication logs")
        validate = logv(".*info RADIUS authentication succeeded for user "+config.radius_username+".*","/var/log/syslog",config.grid_vip)
        if validate != None:
            count +=1
            display_msg("Syslog verification successfull")
        else:
             display_msg("Syslog verification unsuccessfull")

        display_msg("Verifying infoblox.log for the authentication logs")
        validate = logv(".*Successfully authenticated NIOS superuser '"+config.radius_username+"'.*","/infoblox/var/infoblox.log",config.grid_vip)
        if validate != None:
            count +=1
            display_msg("infoblox.log verification successfull")
        else:
             display_msg("infoblox.log verification unsuccessfull")


        display_msg("Verifying audit.log for the authentication logs")
        validate = logv(".*"+config.radius_username+".*auth=RADIUS.*","/infoblox/var/audit.log",config.grid_vip)
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



    @pytest.mark.run(order=16)
    def test_016_Assign_remote_users_admin_group_as_non_superuser(self):
        map_remote_user_to_the_group('non-superuser')

    
    @pytest.mark.run(order=17)
    def test_017_Login_to_the_grid_using_RADIUS_credentials_as_non_superuser_and_execute_cli_command(self):
        display_msg("Logging into the grid using RADIUS credentials via CLI as a non-superuser")
        display_msg("Starting log capture")
        log("start","/var/log/syslog",config.grid_vip)
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/infoblox/var/audit.log",config.grid_vip)
        sleep(10)
        display_msg("Logging into the grid")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+config.radius_username+'@'+config.grid_vip,timeout=300)
        except pexpect.TIMEOUT:
            display_msg("Unable to connect to the grid, please check connectivity to the grid")
            assert False
        else:
            child.expect("password:")
            child.sendline(config.radius_password)
            child.expect("Infoblox >")
            child.sendline("show status")
            child.expect("Infoblox >")
            output = child.before
            child.close()
            if 'Error: The user does not have sufficient privileges to run this command' in output:
                display_msg("The user was not able to execute command as a super user")
                assert True
            else:
                display_msg("The user was able to execute command as a super user")
                assert False


    @pytest.mark.run(order=18)
    def test_018_Verify_logs_for_radius_user_login_as_non_superuser(self):
        display_msg("Verify logs for radius user login as non-superuser")
        sleep(20)
        display_msg("Stopping log capture")

        log("stop","/var/log/syslog",config.grid_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/infoblox/var/audit.log",config.grid_vip)
        
        count=0
        display_msg("Verifying syslog for the authentication logs")
        validate = logv(".*info RADIUS authentication succeeded for user "+config.radius_username+".*","/var/log/syslog",config.grid_vip)
        if validate != None:
            count +=1
            display_msg("Syslog verification successfull")
        else:
             display_msg("Syslog verification unsuccessfull")

        display_msg("Verifying infoblox.log for the authentication logs")
        validate = logv(".*Successfully authenticated NIOS superuser '"+config.radius_username+"'.*","/infoblox/var/infoblox.log",config.grid_vip)
        if validate != None:
            count +=1
            display_msg("infoblox.log verification successfull")
        else:
             display_msg("infoblox.log verification unsuccessfull")


        display_msg("Verifying audit.log for the authentication logs")
        validate = logv(".*"+config.radius_username+".*auth=RADIUS.*","/infoblox/var/audit.log",config.grid_vip)
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



    @pytest.mark.run(order=19)
    def test_019_Assign_remote_users_admin_group_as_superuser(self):
        map_remote_user_to_the_group('infobloxgroup')

    
    @pytest.mark.run(order=20)
    def test_020_Login_to_the_grid_using_TACACS_credentials_as_superuser_and_execute_cli_command(self):
        display_msg("Logging into the grid using TACACS credentials via CLI as a superuser")
        display_msg("Starting log capture")
        log("start","/var/log/syslog",config.grid_vip)
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/infoblox/var/audit.log",config.grid_vip)
        sleep(10)
        display_msg("Logging into the grid")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+config.tacacs_username+'@'+config.grid_vip,timeout=300)
        except pexpect.TIMEOUT:
            display_msg("Unable to connect to the grid, please check connectivity to the grid")
            assert False
        else:
            child.expect("password:")
            child.sendline(config.tacacs_password)
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


    @pytest.mark.run(order=21)
    def test_021_Verify_logs_for_TACACS_user_login_as_superuser(self):
        display_msg("Verify logs for TACACS user login as superuser")

        display_msg("Stopping log capture")
        sleep(20)

        log("stop","/var/log/syslog",config.grid_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/infoblox/var/audit.log",config.grid_vip)
        
        count=0
        display_msg("Verifying syslog for the authentication logs")
        validate = logv(".*info TACACS\+ authentication succeeded for user "+config.tacacs_username+".*","/var/log/syslog",config.grid_vip)
        if validate != None:
            count +=1
            display_msg("Syslog verification successfull")
        else:
             display_msg("Syslog verification unsuccessfull")

        display_msg("Verifying infoblox.log for the authentication logs")
        validate = logv(".*Successfully authenticated NIOS superuser '"+config.tacacs_username+"'.*","/infoblox/var/infoblox.log",config.grid_vip)
        if validate != None:
            count +=1
            display_msg("infoblox.log verification successfull")
        else:
             display_msg("infoblox.log verification unsuccessfull")


        display_msg("Verifying audit.log for the authentication logs")
        validate = logv(".*"+config.tacacs_username+".*auth=TACACS+.*","/infoblox/var/audit.log",config.grid_vip)
        if validate != None:
            count +=1
            display_msg("Audit.log verification successfull")
        else:
             display_msg("Audit.log verification unsuccessfull")

        if count ==3:
            display_msg("All log verifications successful")
            assert True
        else:
            display_msg("Log verification failed, check above logs for the failures")
            assert False


    @pytest.mark.run(order=22)
    def test_022_Change_infobloxgroup_from_superuser_to_nonsuperuser_group(self):
        display_msg("Change the infobloxgroup from super user to non superuser")
        display_msg("Fetching infobloxgroup reference")
        response = ib_NIOS.wapi_request("GET",object_type="admingroup")
        group_ref=''
        for ref in json.loads(response):
            if ref['name'] == 'infobloxgroup':
                group_ref = ref['_ref']
                break
        if group_ref == '':
            display_msg("infoblox group not found")
            assert False
        data={"superuser":False,"access_method": ["API","CLI"]}
        display_msg("Changing the infobloxgroup to nonsuperuser group")
        response = ib_NIOS.wapi_request('PUT', ref=group_ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        if bool(re.match("\"admingroup*.",str(response))):
            display_msg("Changed the infobloxgroup from superuser to nonsuperuser group successfully")
            sleep(10)
            assert True
        else:
            display_msg("Changing the infobloxgroup from superuser to nonsuperuser group failed")
            assert False




    @pytest.mark.run(order=23)
    def test_023_Assign_remote_users_admin_group_as_non_superuser(self):
        map_remote_user_to_the_group('infobloxgroup')

    
    @pytest.mark.run(order=24)
    def test_024_Login_to_the_grid_using_TACACS_credentials_as_non_superuser_and_execute_cli_command(self):
        display_msg("Logging into the grid using TACACS credentials via CLI as a non-superuser")
        display_msg("Starting log capture")
        log("start","/var/log/syslog",config.grid_vip)
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/infoblox/var/audit.log",config.grid_vip)
        sleep(10)
        display_msg("Logging into the grid")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+config.tacacs_username+'@'+config.grid_vip,timeout=300)
        except pexpect.TIMEOUT:
            display_msg("Unable to connect to the grid, please check connectivity to the grid")
            assert False
        else:
            child.expect("password:")
            child.sendline(config.tacacs_password)
            child.expect("Infoblox >")
            child.sendline("show status")
            child.expect("Infoblox >")
            output = child.before
            child.close()
            if 'Error: The user does not have sufficient privileges to run this command' in output:
                display_msg("The user was not able to execute command as a super user")
                assert True
            else:
                display_msg("The user was able to execute command as a super user")
                assert False


    @pytest.mark.run(order=25)
    def test_025_Verify_logs_for_TACACS_user_login_as_non_superuser(self):
        display_msg("Verify logs for TACACS user login as non-superuser")
        sleep(20)
        display_msg("Stopping log capture")

        log("stop","/var/log/syslog",config.grid_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/infoblox/var/audit.log",config.grid_vip)
        
        count=0
        display_msg("Verifying syslog for the authentication logs")
        validate = logv(".*info TACACS\+ authentication succeeded for user "+config.tacacs_username+".*","/var/log/syslog",config.grid_vip)
        if validate != None:
            count +=1
            display_msg("Syslog verification successfull")
        else:
             display_msg("Syslog verification unsuccessfull")

        display_msg("Verifying infoblox.log for the authentication logs")
        validate = logv(".*Successfully authenticated NIOS superuser '"+config.tacacs_username+"'.*","/infoblox/var/infoblox.log",config.grid_vip)
        if validate != None:
            count +=1
            display_msg("infoblox.log verification successfull")
        else:
             display_msg("infoblox.log verification unsuccessfull")


        display_msg("Verifying audit.log for the authentication logs")
        validate = logv(".*"+config.tacacs_username+".*auth=TACACS+.*","/infoblox/var/audit.log",config.grid_vip)
        if validate != None:
            count +=1
            display_msg("Audit.log verification successfull")
        else:
             display_msg("Audit.log verification unsuccessfull")

        if count ==3:
            display_msg("All log verifications successful")
            assert True
        else:
            display_msg("Log verification failed, check above logs for the failures")
            assert False



    @pytest.mark.run(order=26)
    def test_026_Assign_remote_users_admin_group_as_superuser(self):
        map_remote_user_to_the_group('asmgroup')
        sleep(5)

    
    @pytest.mark.run(order=27)
    def test_027_Login_to_the_grid_using_AD_credentials_as_superuser_and_execute_cli_command(self):
        display_msg("Logging into the grid using AD credentials via CLI as a superuser")
        display_msg("Starting log capture")
        log("start","/var/log/syslog",config.grid_vip)
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/infoblox/var/audit.log",config.grid_vip)
        sleep(10)
        display_msg("Logging into the grid")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+config.ad_username+'@'+config.grid_vip,timeout=300)
        except pexpect.TIMEOUT:
            display_msg("Unable to connect to the grid, please check connectivity to the grid")
            assert False
        else:
            child.expect("password:")
            child.sendline(config.ad_password)
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


    @pytest.mark.run(order=28)
    def test_028_Verify_logs_for_AD_user_login_as_superuser(self):
        display_msg("Verify logs for AD user login as superuser")

        display_msg("Stopping log capture")
        sleep(20)

        log("stop","/var/log/syslog",config.grid_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/infoblox/var/audit.log",config.grid_vip)
        
        count=0
        display_msg("Verifying syslog for the authentication logs")
        validate = logv(".*info AD authentication succeeded for user "+config.ad_username+".*","/var/log/syslog",config.grid_vip)
        if validate != None:
            count +=1
            display_msg("Syslog verification successfull")
        else:
             display_msg("Syslog verification unsuccessfull")

        display_msg("Verifying infoblox.log for the authentication logs")
        validate = logv(".*"+config.ad_username+".*AD Authentication Succeeded.*","/infoblox/var/infoblox.log",config.grid_vip)
        if validate != None:
            count +=1
            display_msg("infoblox.log verification successfull")
        else:
             display_msg("infoblox.log verification unsuccessfull")


        display_msg("Verifying audit.log for the authentication logs")
        validate = logv(".*"+config.ad_username+".*auth=Active.*Directory.*","/infoblox/var/audit.log",config.grid_vip)
        if validate != None:
            count +=1
            display_msg("Audit.log verification successfull")
        else:
             display_msg("Audit.log verification unsuccessfull")

        if count ==3:
            display_msg("All log verifications successful")
            assert True
        else:
            display_msg("Log verification failed, check above logs for the failures")
            assert False


    @pytest.mark.run(order=29)
    def test_029_Change_asmgroup_from_superuser_to_nonsuperuser_group(self):
        display_msg("Change the asmgroup from super user to non superuser")
        display_msg("Fetching asmgroup reference")
        response = ib_NIOS.wapi_request("GET",object_type="admingroup")
        group_ref=''
        for ref in json.loads(response):
            if ref['name'] == 'asmgroup':
                group_ref = ref['_ref']
                break
        if group_ref == '':
            display_msg("asmgroup not found")
            assert False
        data={"superuser":False,"access_method": ["API","CLI"]}
        display_msg("Changing the asmgroup to nonsuperuser group")
        response = ib_NIOS.wapi_request('PUT', ref=group_ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        display_msg(response)
        if bool(re.match("\"admingroup*.",str(response))):
            display_msg("Changed the asmgroup from superuser to nonsuperuser group successfully")
            assert True
            sleep(10)
        else:
            display_msg("Changing the asmgroup from superuser to nonsuperuser group failed")
            assert False




    @pytest.mark.run(order=30)
    def test_030_Assign_remote_users_admin_group_as_non_superuser(self):
        map_remote_user_to_the_group('asmgroup')

    
    @pytest.mark.run(order=31)
    def test_031_Login_to_the_grid_using_AD_credentials_as_non_superuser_and_execute_cli_command(self):
        display_msg("Logging into the grid using AD credentials via CLI as a non-superuser")
        display_msg("Starting log capture")
        log("start","/var/log/syslog",config.grid_vip)
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        log("start","/infoblox/var/audit.log",config.grid_vip)
        sleep(10)
        display_msg("Logging into the grid")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+config.ad_username+'@'+config.grid_vip,timeout=300)
        except pexpect.TIMEOUT:
            display_msg("Unable to connect to the grid, please check connectivity to the grid")
            assert False
        else:
            child.expect("password:")
            child.sendline(config.ad_password)
            child.expect("Infoblox >")
            child.sendline("show status")
            child.expect("Infoblox >")
            output = child.before
            child.close()
            if 'Error: The user does not have sufficient privileges to run this command' in output:
                display_msg("The user was not able to execute command as a super user")
                assert True
            else:
                display_msg("The user was able to execute command as a super user")
                assert False


    @pytest.mark.run(order=32)
    def test_032_Verify_logs_for_AD_user_login_as_non_superuser(self):
        display_msg("Verify logs for AD user login as non-superuser")
        sleep(20)
        display_msg("Stopping log capture")

        log("stop","/var/log/syslog",config.grid_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        log("stop","/infoblox/var/audit.log",config.grid_vip)
        
        count=0
        display_msg("Verifying syslog for the authentication logs")
        validate = logv(".*info AD authentication succeeded for user "+config.ad_username+".*","/var/log/syslog",config.grid_vip)
        if validate != None:
            count +=1
            display_msg("Syslog verification successfull")
        else:
             display_msg("Syslog verification unsuccessfull")

        display_msg("Verifying infoblox.log for the authentication logs")
        validate = logv(".*"+config.ad_username+".*AD Authentication Succeeded.*","/infoblox/var/infoblox.log",config.grid_vip)
        if validate != None:
            count +=1
            display_msg("infoblox.log verification successfull")
        else:
             display_msg("infoblox.log verification unsuccessfull")


        display_msg("Verifying audit.log for the authentication logs")
        validate = logv(".*"+config.ad_username+".*auth=Active.*Directory.*","/infoblox/var/audit.log",config.grid_vip)
        if validate != None:
            count +=1
            display_msg("Audit.log verification successfull")
        else:
             display_msg("Audit.log verification unsuccessfull")

        if count ==3:
            display_msg("All log verifications successful")
            assert True
        else:
            display_msg("Log verification failed, check above logs for the failures")
            assert False


    @pytest.mark.run(order=33)
    def test_033_Assign_remote_users_admin_group_as_superuser(self):
        map_remote_user_to_the_group()

    
    @pytest.mark.run(order=34)
    def test_034_Login_to_the_grid_using_LDAP_credentials_as_superuser_and_execute_cli_command(self):
        display_msg("Logging into the grid using LDAP credentials via CLI as a superuser")
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


    @pytest.mark.run(order=35)
    def test_035_Verify_logs_for_LDAP_user_login_as_superuser(self):
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



    @pytest.mark.run(order=36)
    def test_036_Assign_remote_users_admin_group_as_non_superuser(self):
        map_remote_user_to_the_group('non-superuser')

    
    @pytest.mark.run(order=37)
    def test_037_Login_to_the_grid_using_LDAP_credentials_as_non_superuser_and_execute_cli_command(self):
        display_msg("Logging into the grid using LDAP credentials via CLI as a non-superuser")
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
            if 'Error: The user does not have sufficient privileges to run this command' in output:
                display_msg("The user was not able to execute command as a super user")
                assert True
            else:
                display_msg("The user was able to execute command as a super user")
                assert False


    @pytest.mark.run(order=38)
    def test_038_Verify_logs_for_LDAP_user_login_as_superuser(self):
        display_msg("Verify logs for LDAP user login as non-superuser")
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














    


  



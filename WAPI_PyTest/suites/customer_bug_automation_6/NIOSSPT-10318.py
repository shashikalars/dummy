#!/usr/bin/env python
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. IB-FLEX configure with Grid                                          #
#  2. License : DCA, ADP                                                    #
#############################################################################

import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import sys
import json
import commands
import json, ast
import requests
from time import sleep as sleep
import pexpect
import paramiko
from paramiko import client
import ib_utils.common_utilities as comm_util
import ib_utils.ib_NIOS as ib_NIOS
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
import fileinput
import shlex
from subprocess import Popen, PIPE

def check_able_to_login_appliances():
    
    for i in range(5):
        try:
            #child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
         
            child.sendline('show version')

            child.expect('>')
            
            if 'Version :' in child.before:
                child.close()
                print("\n************Appliances is Working************\n ")
                sleep(60)
                assert True
                break
            else:
                
                raise(Exception)

        except Exception as e:
            child.close()
            print(e)
            sleep(20)
            continue
            print("Failure")
            
            assert False
            
class NIOSSPT_10318(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_check_status_of_DCA_and_ATP(self):
        print("Enable DCA and ADP license")
        sleep(60)
        print("starting DCA service in the Grid member...\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        print(get_ref)
        print get_ref
        res = json.loads(get_ref)
        print res

        #ref1 = json.loads(get_ref)[0]['_ref']
        for ref1 in json.loads(get_ref):
            data = {"enable_dns": True,"enable_dns_cache_acceleration": True}
            response = ib_NIOS.wapi_request('PUT',ref=ref1['_ref'],fields=json.dumps(data), grid_vip=config.grid_vip)
            print response
        check_able_to_login_appliances()
        print("DCA service started in the Grid member")
        sleep(300) 
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print('Grid restart services')
        sleep(60)
        
        print("start the TP service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        print(get_ref)
        res = json.loads(get_ref)
        #ref1 = json.loads(get_ref)[0]['_ref']
        for ref1 in json.loads(get_ref):
            print (ref1)
            data = {"enable_service": True}
            response = ib_NIOS.wapi_request('PUT',ref=ref1['_ref'],fields=json.dumps(data))
        
            print(response)
        check_able_to_login_appliances()
        
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print('Grid restart services')
        sleep(450)    
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_member1_vip, username='root', pkey = mykey)
        data="cat /infoblox/var/fastpath_status\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        if 'dca_status: running' in stdout and 'atp_status: running' in stdout:
            print("Success : Status of DCA and ATP are rightly updated for fastpath")
            print("Mount the RP")
            data="mount -o remount,rw /"
            stdin, stdout, stderr = client.exec_command(data)
            stdout=stdout.read()
            print(type(stdout))
            client.close()
            assert True

        else:
            print("Failure : Status of DCA and ATP are rightly updated for fastpath")
            client.close()
            assert False

    @pytest.mark.run(order=2)
    def test_001_modify_the_function_add_huge_pages(self):
        print("Copy the file into temp file")
        check_able_to_login_appliances()
        #child=pexpect.spawn("ssh root@"+config.grid_vip,  maxread=4000)
        child=pexpect.spawn("ssh root@"+config.grid_member1_vip,  maxread=4000)

        try:
            #child.expect("Are you sure you want to continue connecting (yes/no)?")
            #child.sendline("yes")
            child.expect("-bash-5.0#",timeout=100)
            #child.expect("-bash-5.0#")
            child.sendline("scp /infoblox/one/bin/fastpath_control root@"+config.client_ip+":/import/qaddi/API_Automation_08_12_20/WAPI_PyTest/suites/customer_bug_automation/fastpath_control")
            child.expect("Are you sure you want to continue connecting (yes/no)?")
            child.sendline("yes")
            child.expect('password:',timeout=100)
            child.sendline("infoblox")
            child.expect("fastpath_control")
            child.expect("-bash-5.0#")
            child.sendline("exit")
            print("\nSuccess: Copy the original file into local")
            child.close()
            assert True

        except Exception as e:
            child.close()
            print (e)
            print("Failure: Copy the original file into local")
            assert False

    @pytest.mark.run(order=3)
    def test_002_replace_content_to_fastpath(self):
        print("Modify add_huge_pages function")
        with open("/import/qaddi/API_Automation_08_12_20/WAPI_PyTest/suites/customer_bug_automation/fastpath_control","r+") as file:
            #print(file.read())
            with open("/import/qaddi/API_Automation_08_12_20/WAPI_PyTest/suites/customer_bug_automation/fastpath_control_temp", "w") as f:
                for line in file.readlines():
                    if 'local fp_huge=$' in line:
                        #print(line.replace())
                        text_to_search="local fp_huge=$((fp_mem / 2))  # number of 2MB hugepages"
                        replacement_text="local fp_huge=1000000000  # number of 2MB hugepages"
                        f.write(line.replace(text_to_search, replacement_text))
                    else:
                        f.write(line)
        
        #child=pexpect.spawn("ssh root@"+config.grid_vip,  maxread=4000)
        child=pexpect.spawn("ssh root@"+config.grid_member1_vip,  maxread=4000)

        try:

            child.expect("-bash-5.0#",timeout=100)
            child.sendline("scp root@"+config.client_ip+":/import/qaddi/API_Automation_08_12_20/WAPI_PyTest/suites/customer_bug_automation/fastpath_control_temp /infoblox/one/bin/fastpath_control")
            child.expect('password:',timeout=100)
            child.sendline("infoblox")
            child.expect("-bash-5.0#")
            child.sendline("exit")
            print("\nSuccess: Copy file to fastpath After modifying it")
            child.close()
            assert True

        except Exception as e:
            child.close()
            print (e)
            print("Failure: copy file to fastpath After modifying it")
            assert False



    @pytest.mark.run(order=4)
    def test_003_Reboot_the_appliance(self):

        print("Reboot the appliance")
        #child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('reboot')
        child.expect('y or n')
        child.sendline('y')
        sleep(30)

        for i in range(1,15):
            sleep(22)
            args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no root@"+config.client_ip
            args=shlex.split(args)
            child1 = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            #data="ping "+config.grid_vip+" -c 2"
            #child1.stdin.write("ping "+config.grid_vip+" -c 2 \n")
            child1.stdin.write("ping "+config.grid_member1_vip+" -c 2 \n")
            flag=0
            output = child1.communicate()
            print(output)
            for res in output:

                if ', 0% packet loss' in res:
                    print("=============0% packet loss===============")
                    flag=1
                    break
                else:
                    continue
            if flag ==1:
                sleep(15)
                break
            else:
                continue
        sleep(90)
        child.close()
        sleep(80)
        check_able_to_login_appliances()

    @pytest.mark.run(order=5)
    def test_004_check_updated_status_of_DCA_and_ATP(self):
        sleep(10)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        #client.connect(config.grid_vip, username='root', pkey = mykey)
        client.connect(config.grid_member1_vip, username='root', pkey = mykey)
        data="cat /infoblox/var/fastpath_status\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        if 'dca_status: failure' in stdout and 'atp_status: failure' in stdout :
            print("Success : Status of DCA and ATP are rightly updated for fastpath")
        else:
            print("Failure : Status of DCA and ATP are rightly updated for fastpath")
            client.close()
            assert False

    @pytest.mark.run(order=6)
    def test_005_check_fp_failure_flag(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        #client.connect(config.grid_vip, username='root', pkey = mykey)
        client.connect(config.grid_member1_vip, username='root', pkey = mykey)
        stdin, stdout, stderr = client.exec_command("ls /infoblox/var/flags")
        result=stdout.read()
        print(len(result))
        print(result)
        if 'fp_failure' in result:
            print("Success: fp_failure flag is part of /infoblox/var/flags directory")
            assert True
        else:
            print("Failue: fp_failure flag is part of /infoblox/var/flags directory")
            assert False
        client.close()

    @pytest.mark.run(order=7)
    def test_006_validate_dns_accel_and_adp(self):
        #args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_vip
        args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_member1_vip
        args=shlex.split(args)
        child1 = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)

        child1.stdin.write("show dns-accel\n")

        output = child1.communicate()
        #print(output)
        for res in output:
            print(res.replace(" ", ""))
            if 'Cache:Enabled' in res.replace(" ", ""):
                print("Success")
                assert False
                break
            else:
                print("Failure")
                assert True

        # args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_vip
        args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_member1_vip
        args=shlex.split(args)
        child1 = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)

        child1.stdin.write("show adp\n")

        output = child1.communicate()
        for res in output:
            print(res.replace(" ", ""))
            if 'ThreatProtection:Enabled' in res.replace(" ", ""):
                print("Success")
                assert False
                break
            else:
                print("Failure")
                assert True

    @pytest.mark.run(order=8)
    def test_007_Revert_back_the_changes(self):
        print("Revert back the changes")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        #client.connect(config.grid_vip, username='root', pkey = mykey)
        client.connect(config.grid_member1_vip, username='root', pkey = mykey)
        data="mount -o remount,rw /"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(type(stdout))
        client.close()
        #child=pexpect.spawn("ssh root@"+config.grid_vip,  maxread=4000)
        child=pexpect.spawn("ssh root@"+config.grid_member1_vip,  maxread=4000)

        try:

            child.expect("-bash-5.0#",timeout=100)
            child.sendline("scp root@"+config.client_ip+":/import/qaddi/API_Automation_08_12_20/WAPI_PyTest/suites/customer_bug_automation/fastpath_control /infoblox/one/bin/fastpath_control")

            child.expect('password:',timeout=100)
            child.sendline("infoblox")
            child.expect("-bash-5.0#")
            child.sendline("exit")
            print("\nSuccess: Revert back the changes")
            child.close()
            assert True

        except Exception as e:
            child.close()
            print (e)
            print("Failure: Revert back the changes")
            assert False


    @pytest.mark.run(order=9)
    def test_008_Validate_continue_to_work_on_reboot(self):
        print("Reboot the appliance")
        #child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('reboot')
        child.expect('y or n')
        child.sendline('y')
        sleep(30)

        for i in range(1,15):
            sleep(22)
            args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no root@"+config.client_ip
            args=shlex.split(args)
            child1 = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            #data="ping "+config.grid_vip+" -c 2"
            #child1.stdin.write("ping "+config.grid_vip+" -c 2 \n")
            child1.stdin.write("ping "+config.grid_member1_vip+" -c 2 \n")
            flag=0
            output = child1.communicate()
            print(output)
            for res in output:

                if ', 0% packet loss' in res:
                    print("=============0% packet loss===============")
                    flag=1
                    break
                else:
                    continue
            if flag ==1:
                sleep(15)
                break
            else:
                continue
        sleep(90)
        child.close()
        sleep(80)
        check_able_to_login_appliances()
        
        
    @pytest.mark.run(order=10)
    def test_009_validate_services_are_updated(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        #client.connect(config.grid_vip, username='root', pkey = mykey)
        client.connect(config.grid_member1_vip, username='root', pkey = mykey)
        data="cat /infoblox/var/fastpath_status\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        if 'dca_status: running' in stdout and 'atp_status: running' in stdout and 'fastpath_status: running' in stdout:
            print("Success : Status of DCA and ATP are rightly updated for fastpath")
            client.close()
            assert True

        else:
            print("Failure : Status of DCA and ATP are rightly updated for fastpath")
            client.close()
            assert False

    @pytest.mark.run(order=11)
    def test_010_validate_dns_accel_and_adp_after_revert(self):
        #args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_vip
        args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_member1_vip
        args=shlex.split(args)
        child1 = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)

        child1.stdin.write("show dns-accel\n")

        output = child1.communicate()
        #print(output)
        for res in output:
            print(res.replace(" ", ""))
            if 'Cache:Enabled' in res.replace(" ", ""):
                print("Success")
                assert True
                break
            else:
                print("Failure")
                assert False

        #args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_vip
        args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_member1_vip
        args=shlex.split(args)
        child1 = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)

        child1.stdin.write("show adp\n")

        output = child1.communicate()
        for res in output:
            print(res.replace(" ", ""))
            if 'ThreatProtection:Enabled' in res.replace(" ", ""):
                print("Success")
                assert True
                break
            else:
                print("Failure")
                assert False


    @pytest.mark.run(order=11)
    def test_011_cleanup(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        print(get_ref)
        print get_ref
        res = json.loads(get_ref)
        print res
        #ref1 = json.loads(get_ref)[0]['_ref']
        for ref1 in json.loads(get_ref):

            data = {"enable_dns": True,"enable_dns_cache_acceleration": False}
            response = ib_NIOS.wapi_request('PUT',ref=ref1['_ref'],fields=json.dumps(data), grid_vip=config.grid_vip)
            print response
        check_able_to_login_appliances()
        print("stop the TP service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        print(get_ref)
        res = json.loads(get_ref)
        #ref1 = json.loads(get_ref)[0]['_ref']
        for ref1 in json.loads(get_ref):

            print (ref1)
            data = {"enable_service": False}
            response = ib_NIOS.wapi_request('PUT',ref=ref1['_ref'],fields=json.dumps(data))

            print(response)
        check_able_to_login_appliances()


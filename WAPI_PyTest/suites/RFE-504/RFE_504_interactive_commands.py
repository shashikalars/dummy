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
import time
import getpass
import sys
import pexpect

user=config.username1
password=config.password1
user1=config.username2
password1=config.password2
logging.basicConfig(filename='ref_int.log', filemode='w', level=logging.DEBUG)


def interactive_commands(command,user,password):
    logging.info("Entering function")
    c=pexpect.spawn('ssh -o StrictHostKeyChecking=no %s@%s' % (user,config.grid_vip))
    c.expect("password: ",timeout=30)
    c.sendline(password)
    c.expect("Infoblox > ",timeout=30)
    c.sendline(command.strip('\"'))
    logging.info("login succesfull")
    i=c.expect(["to run this command\r\nInfoblox > ","\(y or n\):","q to quit: ","0 to abort\)\? ","Gateway/CIDR: ","Grid Master VIP: ","license string: ","IPv4 address.*","Enter \<return\> for next page or q\<return\> to cancel the command\.\r\n","All other changes must be performed in the GUI.\r\nInfoblox > ","The grid currently has 3 member\(s\).\r\nInfoblox > "],timeout=30)
    logging.info("Value of i is "+str(i))
    if i==0:
        print "User doesnt have permission to execute this command\n"
        c.sendline("exit")
        c.close()
        return 0
    elif i==1:
        c.sendline("n")
        j=c.expect(["\(y or n\):","Infoblox > "],timeout=30)
        if j==0:
            c.sendline("n")
            c.expect("Infoblox > ",timeout=30)
            c.sendline("exit")
            return 1
        else:
            c.sendline("exit")
            return 1
    elif i==2:
        c.sendline("q")
        c.sendline("exit")
        return 1
    elif i==3:
        c.sendline("0")
        c.sendline("exit")
        return 1
    elif i==4:
        c.sendline("172.17.0.1/16")
        c.expect("\(y or n\):",timeout=30)
        c.sendline("n")
        c.expect("Infoblox > ",timeout=30)
        c.sendline("exit")
        return 1
    elif i==5:
        c.sendline("1.1.1.1")
        c.expect("\[Default Infoblox\]: ",timeout=30)
        c.sendline()
        c.expect("Enter Grid Shared Secret: ",timeout=30)
        c.sendline("test")
        c.expect("\(y or n\):",timeout=30)
        c.sendline("n")
        c.expect("Infoblox > ",timeout=30)
        c.sendline("exit")
        return 1
    elif i==6:
        c.sendline("ad")
        c.expect("Infoblox > ",timeout=30)
        c.sendline("exit")
        return 1
    elif i==7:
        c.sendline(config.grid_vip)
        c.expect("Enter netmask.*",timeout=30)
        c.sendline("255.255.0.0")
        c.expect("\[Default: 10.35.0.1\]: ",timeout=30)
        c.sendline()
        c.expect("\[Default: Untagged\]: ",timeout=30)
        c.sendline()
        c.expect("\(y or n\):",timeout=30)
        c.sendline("n")
        c.expect("\(y or n\):",timeout=30)
        c.sendline("n")
        c.expect("Infoblox > ",timeout=30)
        c.sendline("exit")
        return 1
    elif i==8:
        c.sendline("q")
        c.expect("Infoblox > ",timeout=30)
        c.sendline("exit")
        return 1
    elif i==9:
        c.sendline("exit")
        return 1
    elif i==10:
        c.sendline("exit")
        return 1
    else:
        c.sendline("exit")
        raise Exception("Unknown error")


def interactive_commands_radius(command,user,password):
    logging.info("Entering function")
    c=pexpect.spawn('ssh -o StrictHostKeyChecking=no %s@%s' % (user,config.grid_vip))
    c.expect("password: ",timeout=30)
    c.sendline(password)
    c.expect("Infoblox > ",timeout=30)
    c.sendline(command.strip('\"'))
    logging.info("login succesfull")
    i=c.expect(["to run this command\r\nInfoblox > ","\(y or n\):","q to quit: ","0 to abort\)\? ","Gateway/CIDR: ","Grid Master VIP: ","license string: ","IPv4 address.*","Enter \<return\> for next page or q\<return\> to cancel the command\.\r\n","All other changes must be performed in the GUI.\r\nInfoblox > ","The grid currently has 3 member\(s\).\r\nInfoblox > "],timeout=30)
    logging.info("Value of i is "+str(i))
    if i==0:
        print "User doesnt have permission to execute this command\n"
        c.sendline("exit")
        c.close()
        return 0
    elif i==1:
        c.sendline("n")
        j=c.expect(["\(y or n\):","Infoblox > "],timeout=30)
        if j==0:
            c.sendline("n")
            c.expect("Infoblox > ",timeout=30)
            c.sendline("exit")
            return 1
        else:
            c.sendline("exit")
            return 1
    elif i==2:
        c.sendline("q")
        c.sendline("exit")
        return 1
    elif i==3:
        c.sendline("0")
        c.sendline("exit")
        return 1
    elif i==4:
        c.sendline("172.17.0.1/16")
        c.expect("\(y or n\):",timeout=30)
        c.sendline("n")
        c.expect("Infoblox > ",timeout=30)
        c.sendline("exit")
        return 1
    elif i==5:
        c.sendline("1.1.1.1")
        c.expect("\[Default Infoblox\]: ",timeout=30)
        c.sendline()
        c.expect("Enter Grid Shared Secret: ",timeout=30)
        c.sendline("test")
        c.expect("\(y or n\):",timeout=30)
        c.sendline("n")
        c.expect("Infoblox > ",timeout=30)
        c.sendline("exit")
        return 1
    elif i==6:
        c.sendline("ad")
        c.expect("Infoblox > ",timeout=30)
        c.sendline("exit")
        return 1
    elif i==7:
        c.sendline(config.grid_vip)
        c.expect("Enter netmask.*",timeout=30)
        c.sendline("255.255.0.0")
        c.expect("\[Default: 10.35.0.1\]: ",timeout=30)
        c.sendline()
        c.expect("\[Default: Untagged\]: ",timeout=30)
        c.sendline()
        c.expect("\(y or n\):",timeout=30)
        c.sendline("n")
        c.expect("\(y or n\):",timeout=30)
        c.sendline("n")
        c.expect("Infoblox > ",timeout=30)
        c.sendline("exit")
        return 1
    elif i==8:
        c.sendline("q")
        c.expect("Infoblox > ",timeout=30)
        c.sendline("exit")
        return 1
    elif i==9:
        c.sendline("exit")
        return 1
    elif i==10:
        c.sendline("exit")
        return 1
    else:
        c.sendline("exit")
        raise Exception("Unknown error")

class Network(unittest.TestCase):
                @pytest.mark.run(order=1)
                def test001_change_privilage(self):
                    res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
                    res = json.loads(res)
                    ref1=res[0]['_ref']
		    data={"admin_set_commands":{"set_clean_mscache":False,"set_disable_gui_one_click_support":False},"admin_show_commands":{"show_log":False,"show_tech_support":False},"cloud_set_commands":{"set_cloud_services_portal_force_refresh":False},"docker_set_commands":{"set_docker_bridge":False},"grid_set_commands":{"set_membership":False,"set_nomastergrid":False,"set_revert_grid":False},"licensing_set_commands":{"set_license":False,"set_temp_license":False},"networking_set_commands":{"set_mld_version_1":False,"set_network":False,"set_remote_console":False},"networking_show_commands":{"show_connections":False,"show_interface":False},"security_set_commands":{"set_apache_https_cert":False,"set_cc_mode":False,"set_fips_mode":False,"set_reporting_cert":False,"set_security":False,"set_session_timeout":False,"set_support_access":False}}
                    response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
                    logging.info(response)
                    time.sleep(15)


    		@pytest.mark.run(order=2)
		def test002_set_clean_mscache_disabled(self):
			command="set clean_mscache"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State disabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")
            
                        output=interactive_commands_radius(command,user1,password1)
                        if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=3)
		def test003_set_disable_gui_disabled(self):
			command="set disable_gui_one_click_support"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State disabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")
                
                        output=interactive_commands_radius(command,user1,password1)
                        if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=4)
		def test004_set_cloud_service_disabled(self):
			command="set cloud_services_portal_force_refresh"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State disabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

                        output=interactive_commands_radius(command,user1,password1)
                        if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

		@pytest.mark.run(order=5)
		def test005_set_docker_bridge_disabled(self):
			command="set docker_bridge"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State disabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

                        output=interactive_commands_radius(command,user1,password1)
                        if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

		@pytest.mark.run(order=6)
		def test006_set_membership_disabled(self):
			command="set membership"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State disabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

                        output=interactive_commands_radius(command,user1,password1)
                        if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")
		@pytest.mark.run(order=7)
		def test007_set_nomastergrid_disabled(self):
			command="set nomastergrid"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State disabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

                        output=interactive_commands_radius(command,user1,password1)
                        if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=8)
		def test008_set_revert_grid_disabled(self):
			command="set revert_grid"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State disabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

                        output=interactive_commands_radius(command,user1,password1)
                        if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

		@pytest.mark.run(order=9)
		def test009_set_license_disabled(self):
			command="set license"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State disabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

                        output=interactive_commands_radius(command,user1,password1)
                        if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

		@pytest.mark.run(order=10)
		def test010_set_temp_license_disabled(self):
			command="set temp_license"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State disabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")
            
                        output=interactive_commands_radius(command,user1,password1)
                        if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

		@pytest.mark.run(order=11)
		def test011_set_mld_disabled(self):
			command="set mld_version_1"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State disabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

                        output=interactive_commands_radius(command,user1,password1)
                        if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=12)
		def test012_set_network_disabled(self):
			command="set network"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State disabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

                        output=interactive_commands_radius(command,user1,password1)
                        if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=13)
		def test013_set_remote_console_disabled(self):
			command="set remote_console"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State disabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

                        output=interactive_commands_radius(command,user1,password1)
                        if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=14)
		def test014_set_apache_disabled(self):
			command="set apache_https_cert"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State disabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

                        output=interactive_commands_radius(command,user1,password1)
                        if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

		@pytest.mark.run(order=15)
		def test015_set_cc_disabled(self):
			command="set cc_mode"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State disabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

                        output=interactive_commands_radius(command,user1,password1)
                        if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

		@pytest.mark.run(order=16)
		def test016_set_fips_disabled(self):
			command="set fips_mode"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State disabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

                        output=interactive_commands_radius(command,user1,password1)
                        if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

		@pytest.mark.run(order=17)
		def test017_set_reporting_cert_disabled(self):
			command="set reporting_cert"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State disabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

                        output=interactive_commands_radius(command,user1,password1)
                        if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=18)
		def test018_set_security_disabled(self):
			command="set security"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State disabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")


                        output=interactive_commands_radius(command,user1,password1)
                        if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

		@pytest.mark.run(order=19)
		def test019_set_timeout_disabled(self):
			command="set session_timeout"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State disabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

                        output=interactive_commands_radius(command,user1,password1)
                        if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=20)
		def test020_set_support_access_disabled(self):
			command="set support_access"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State disabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

                        output=interactive_commands_radius(command,user1,password1)
                        if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=21)
		def test021_set_log_disabled(self):
			command="show log"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State disabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

                        output=interactive_commands_radius(command,user1,password1)
                        if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

		@pytest.mark.run(order=22)
		def test022_set_tech_support_disabled(self):
			command="show tech-support"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State disabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

                        output=interactive_commands_radius(command,user1,password1)
                        if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=23)
		def test023_set_connections_disabled(self):
			command="show connections"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State disabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

                        output=interactive_commands_radius(command,user1,password1)
                        if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=24)
		def test024_set_interface_disabled(self):
			command="show interface"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State disabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")

                        output=interactive_commands_radius(command,user1,password1)
                        if output==0:
				logging.info("User does not have permission to execute command")
			elif output==1:
				logging.info("User has permission to execute command")
				raise Exception("Command executed even though user doesnot have permission")
			else:
				raise Exception("Unknown value returned by the function")


                @pytest.mark.run(order=25)
                def test025_change_privilage(self):
                        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
                        res = json.loads(res)
                        ref1=res[0]['_ref']
                        data={"admin_set_commands":{"set_clean_mscache":True,"set_disable_gui_one_click_support":True},"admin_show_commands":{"show_log":True,"show_tech_support":True},"cloud_set_commands":{"set_cloud_services_portal_force_refresh":True},"docker_set_commands":{"set_docker_bridge":True},"grid_set_commands":{"set_membership":True,"set_nomastergrid":True,"set_revert_grid":True},"licensing_set_commands":{"set_license":True,"set_temp_license":True},"networking_set_commands":{"set_mld_version_1":True,"set_network":True,"set_remote_console":True},"networking_show_commands":{"show_connections":True,"show_interface":True},"security_set_commands":{"set_apache_https_cert":True,"set_cc_mode":True,"set_fips_mode":True,"set_reporting_cert":True,"set_security":True,"set_session_timeout":True,"set_support_access":True}}
                        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
                        logging.info(response)
                        time.sleep(15)




                @pytest.mark.run(order=26)
		def test026_set_clean_mscache_enabled(self):
			command="set clean_mscache"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State enabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")
          
			output=interactive_commands_radius(command,user1,password1)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")



		@pytest.mark.run(order=27)
		def test027_set_disable_gui_enabled(self):
			command="set disable_gui_one_click_support"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State enabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")
                
            		output=interactive_commands_radius(command,user1,password1)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=28)
		def test028_set_cloud_service_enabled(self):
			command="set cloud_services_portal_force_refresh"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State enabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")

			output=interactive_commands_radius(command,user1,password1)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")

		@pytest.mark.run(order=29)
		def test029_set_docker_bridge_enabled(self):
			command="set docker_bridge"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State enabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")
            
                        output=interactive_commands_radius(command,user1,password1)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=30)
		def test030_set_membership_enabled(self):
			command="set membership"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State enabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")
                
                        output=interactive_commands_radius(command,user1,password1)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=31)
		def test031_set_nomastergrid_enabled(self):
			command="set nomastergrid"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State enabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")
            
                        output=interactive_commands_radius(command,user1,password1)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=32)
		def test032_set_revert_grid_enabled(self):
			command="set revert_grid"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State enabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")
            
                        output=interactive_commands_radius(command,user1,password1)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=33)
		def test033_set_license_enabled(self):
			command="set license"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State enabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")
                
                        output=interactive_commands_radius(command,user1,password1)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=34)
		def test034_set_temp_license_enabled(self):
			command="set temp_license"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State enabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")
            
                        output=interactive_commands_radius(command,user1,password1)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=35)
		def test035_set_mld_enabled(self):
			command="set mld_version_1"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State enabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")
            
                        output=interactive_commands_radius(command,user1,password1)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=36)
		def test036_set_network_enabled(self):
			command="set network"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State enabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")
            
                        output=interactive_commands_radius(command,user1,password1)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=37)
		def test037_set_remote_console_enabled(self):
			command="set remote_console"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State enabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")
            
                        output=interactive_commands_radius(command,user1,password1)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=38)
		def test038_set_apache_enabled(self):
			command="set apache_https_cert"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State enabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")
                
                        output=interactive_commands_radius(command,user1,password1)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=39)
		def test039_set_cc_enabled(self):
			command="set cc_mode"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State enabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")
                
                        output=interactive_commands_radius(command,user1,password1)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=40)
		def test040_set_fips_enabled(self):
			command="set fips_mode"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State enabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")
                
                        output=interactive_commands_radius(command,user1,password1)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=41)
		def test041_set_reporting_enabled(self):
			command="set reporting_cert"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State enabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")
                
                        output=interactive_commands_radius(command,user1,password1)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=42)
		def test042_set_security_enabled(self):
			command="set security"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State enabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")
            
                        output=interactive_commands_radius(command,user1,password1)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")



		@pytest.mark.run(order=43)
		def test043_set_timeout_enabled(self):
			command="set session_timeout"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State enabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")
                
                        output=interactive_commands_radius(command,user1,password1)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=44)
		def test044_set_support_access_enabled(self):
			command="set support_access"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State enabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")
                
                        output=interactive_commands_radius(command,user1,password1)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=45)
		def test045_set_log_enabled(self):
			command="show log"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State enabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")
                
                        output=interactive_commands_radius(command,user1,password1)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")



		@pytest.mark.run(order=46)
		def test046_set_tech_support_enabled(self):
			command="show tech-support"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State enabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")
                
                        output=interactive_commands_radius(command,user1,password1)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")



		@pytest.mark.run(order=47)
		def test047_set_connection_enabled(self):
			command="show connections"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State enabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")
                
                        output=interactive_commands_radius(command,user1,password1)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")


		@pytest.mark.run(order=48)
		def test048_set_interface_enabled(self):
			command="show interface"
                        time.sleep(15)
			logging.info ("Executing command "+command)
			logging.info("State enabled")
			output=interactive_commands(command,user,password)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")
                
                        output=interactive_commands_radius(command,user1,password1)
			if output==0:
				logging.info("User does not have permission to execute command")
				raise Exception("Command not executed even though user has permission")
			elif output==1:
				logging.info("User has permission to execute command")
			else:
				raise Exception("Unknown value returned by the function")

#!/usr/bin/env python

__author__ = "Prasad K"
__email__  = "pkondisetty@infoblox.com"
__RFE__    = "PenTest 853 SSH Hardening"
############################################################################################################
#  Grid Set up required:                                                                                   #
#  1. Grid Master with reporting,discovery,HA,IB-V1415 members                                             #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415),Threat Analytics,Security Ecosystem,reporting,discovery  #
############################################################################################################






import re
import sys
import config
import pytest
import unittest
import os
import os.path
from os.path import join
import json
import pexpect
import requests
import urllib3
import commands
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
import paramiko
import time
from datetime import datetime, timedelta
import ipaddress



class PenTest_ssh_hardening(unittest.TestCase):

#####################
## Interface : LAN ##
#####################

        @pytest.mark.run(order=00)
        def test_000_For_validatition_short_the_IPv6_address_and_push_to_config_file(self):
                print("\n============================================\n")
                print(" For validation short the IPv6 address and push to config file ")
                print("\n============================================\n")
		grid_ipv6_mgmt_validation = ipaddress.ip_address(unicode(config.grid_ipv6_mgmt))
		grid_ipv6_mgmt_validation = (str(grid_ipv6_mgmt_validation))
		grid_ipv6_lan1_validation = ipaddress.ip_address(unicode(config.grid_ipv6_lan1))
		grid_ipv6_lan1_validation = (str(grid_ipv6_lan1_validation))
		grid_ipv6_lan2_validation = ipaddress.ip_address(unicode(config.grid_ipv6_lan2))
		grid_ipv6_lan2_validation = (str(grid_ipv6_lan2_validation))
		grid_ipv6_HA_vip_validation= ipaddress.ip_address(unicode(config.grid_ipv6_HA_vip))
		grid_ipv6_HA_vip_validation = (str(grid_ipv6_HA_vip_validation))
		grid_ipv6_HA_Active_validation= ipaddress.ip_address(unicode(config.grid_ipv6_HA_Active))
		grid_ipv6_HA_Active_validation = (str(grid_ipv6_HA_Active_validation))
		grid_ipv6_HA_Passive_validation= ipaddress.ip_address(unicode(config.grid_ipv6_HA_Passive))
		grid_ipv6_HA_Passive_validation = (str(grid_ipv6_HA_Passive_validation))
		#reporting_member_ipv6_validation= ipaddress.ip_address(unicode(config.reporting_member_ipv6))
		#reporting_member_ipv6_validation = (str(reporting_member_ipv6_validation))
		os.system("echo -e 'grid_ipv6_mgmt_validation=\""+grid_ipv6_mgmt_validation+"\"' >> config.py")
		os.system("echo -e 'grid_ipv6_lan1_validation=\""+grid_ipv6_lan1_validation+"\"' >> config.py")
		os.system("echo -e 'grid_ipv6_lan2_validation=\""+grid_ipv6_lan2_validation+"\"' >> config.py")
		os.system("echo -e 'grid_ipv6_HA_vip_validation=\""+grid_ipv6_HA_vip_validation+"\"' >> config.py")
		os.system("echo -e 'grid_ipv6_HA_Active_validation=\""+grid_ipv6_HA_Active_validation+"\"' >> config.py")
		os.system("echo -e 'grid_ipv6_HA_Passive_validation=\""+grid_ipv6_HA_Passive_validation+"\"' >> config.py")
		#os.system("echo -e 'reporting_member_ipv6_validation=\""+reporting_member_ipv6_validation+"\"' >> config.py")
	        reload(config)
        	sleep(05)
		print("Test Case 00 Execution Completed")	



        @pytest.mark.run(order=01)
        def test_001_Validate_ssh_admin_login_and_enabled_remote_console_in_Grid_through_LAN_IP_in_Grid_Master(self):
                print("\n============================================\n")
                print(" Validate ssh admin login and enabled remote console in Grid through LAN IP in Grid Master ")
                print("\n============================================\n")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_lan1)
                        child.logfile=sys.stdout
                        child.expect('password: ')
			child.sendline('infoblox')
			child.expect('Infoblox > ')
                        child.sendline('show remote_console')
                        child.expect('>')
			output = child.before
			output = output.replace("\r\n"," ")
			print("\n")
			print(output)
			print("\n")
			data = 'Current remote console access settings: enabled'
			if data in output:
				assert True
				print("Remote console access is enabled ")
			else:
				assert False
			print("\n")
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 01 Execution Completed")

	
        @pytest.mark.run(order=02)
        def test_002_Validate_ssh_root_login_and_PasswordAuthentication_in_sshd_conf_through_LAN_IP_in_Grid_Master(self):
                print("\n============================================\n")
                print(" Validate ssh root login and PasswordAuthentication in sshd conf through LAN IP in Grid Master ")
                print("\n============================================\n")
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_lan1)
                        child.logfile=sys.stdout
                        child.expect('#')
			child.sendline('grep -e PermitRootLogin -e PasswordAuthentication /storage/etc/sshd_config')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        sleep(05)
                        data = ['PermitRootLogin yes','PasswordAuthentication yes']
                        for i in data:
                                if i in output:
                                        assert True
                                        print(data)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("\n")
                print("Test Case 02 Execution Completed")



        @pytest.mark.run(order=03)
        def test_003_Validate_Listen_Address_in_sshd_conf_file_through_LAN_IP_in_Grid_Master(self):
                print("\n============================================\n")
                print("Validate Listen Address in sshd conf file through LAN IP in Grid Master ")
                print("\n============================================\n")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_lan1)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
			child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
			child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
			sleep(05)
                        output = child.before
			output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
			data = ['ListenAddress '+config.grid_vip,'ListenAddress '+config.grid_lan1,'ListenAddress '+config.grid_lan2,'ListenAddress ['+config.grid_ipv6_lan1_validation+']','ListenAddress ['+config.grid_ipv6_lan2_validation+']','ListenAddress '+config.grid_ipv6_mgmt_validation]
			for i in data:
                        	if i in output:
	                                assert True
        	                        print(i)
                	        else:
                        	        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
		sleep(05)
                print("Test Case 03 Execution Completed")



        @pytest.mark.run(order=04)
        def test_004_Validate_ssh_admin_login_and_enabled_remote_console_in_Grid_through_IPv6_LAN_IP_in_Grid_Master(self):
                print("\n============================================\n")
                print(" Validate ssh admin login and enabled remote console in Grid through LAN IP in Grid Master ")
                print("\n============================================\n")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_ipv6_lan1)
                        child.logfile=sys.stdout
                        child.expect('password: ')
                        child.sendline('infoblox')
                        child.expect('Infoblox > ')
                        child.sendline('show remote_console')
                        child.expect('>')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = 'Current remote console access settings: enabled'
                        if data in output:
                                assert True
                                print("Remote console access is enabled ")
                        else:
                                assert False
                        print("\n")
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
		sleep(05)
                print("Test Case 04 Execution Completed")



        @pytest.mark.run(order=05)
        def test_005_Validate_Listen_Address_in_sshd_conf_file_through_LAN_IP_in_Grid_Master(self):
                print("\n============================================\n")
                print("Validate Listen Address in sshd conf file through LAN IP in Grid Master ")
                print("\n============================================\n")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_ipv6_lan1)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        sleep(05)
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print("\n")
                        #data = ['ListenAddress ['+config.grid_ipv6_lan1+']','ListenAddress ['+config.grid_ipv6_lan2+']','ListenAddress '+config.grid_ipv6_mgmt]
			data=['ListenAddress '+config.grid_vip,'ListenAddress '+config.grid_lan1,'ListenAddress '+config.grid_lan2,'ListenAddress ['+config.grid_ipv6_lan1_validation+']','ListenAddress ['+config.grid_ipv6_lan2_validation+']','ListenAddress '+config.grid_ipv6_mgmt_validation]
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
		sleep(05)
                print("Test Case 05 Execution Completed")



######################
## Interface : LAN2 ##
######################

        @pytest.mark.run(order=06)
        def test_006_Validate_ssh_admin_login_and_enabled_remote_console_in_Grid_through_LAN2_IP_in_Grid_Master(self):
                print("\n============================================\n")
                print(" Validate ssh admin login and enabled remote console in Grid through LAN2 IP in Grid Master ")
                print("\n============================================\n")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_lan2)
                        child.logfile=sys.stdout
                        child.expect('password: ')
                        child.sendline('infoblox')
                        child.expect('Infoblox > ')
                        child.sendline('show remote_console')
                        child.expect('>')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
			sleep(05)
                        data = 'Current remote console access settings: enabled'
                        if data in output:
                                assert True
                                print("Remote console access is enabled ")
                        else:
                                assert False
                        print("\n")
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
		sleep(05)
                print("Test Case 06 Execution Completed")


        @pytest.mark.run(order=07)
        def test_007_Validate_ssh_root_login_and_PasswordAuthentication_in_sshd_conf_through_LAN2_IP_in_Grid_Master(self):
                print("\n============================================\n")
                print(" Validate ssh root login and PasswordAuthentication in sshd conf through LAN2 IP in Grid Master ")
                print("\n============================================\n")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_lan2)
                        child.logfile=sys.stdout
                        child.expect('#')
			sleep(10)
			child.sendline('grep -e PermitRootLogin -e PasswordAuthentication /storage/etc/sshd_config')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        sleep(05)
                        data = ['PermitRootLogin yes','PasswordAuthentication yes']
                        for i in data:
                                if i in output:
                                        assert True
                                        print(data)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("\n")
                print("Test Case 07 Execution Completed")



        @pytest.mark.run(order=108)
        def test_008_Validate_Listen_Address_in_sshd_conf_file_through_LAN2_IP_in_Grid_Master(self):
                print("\n============================================\n")
                print(" Validate Listen Address in sshd conf file through LAN2 IP in Grid Master ")
                print("\n============================================\n")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_lan2)
                        child.logfile=sys.stdout
                        child.expect('#')
			sleep(05)
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        #data = ['ListenAddress '+config.grid_vip,'ListenAddress '+config.grid_lan2,'ListenAddress '+config.grid_lan1]
			data=['ListenAddress '+config.grid_vip,'ListenAddress '+config.grid_lan1,'ListenAddress '+config.grid_lan2,'ListenAddress ['+config.grid_ipv6_lan1_validation+']','ListenAddress ['+config.grid_ipv6_lan2_validation+']','ListenAddress '+config.grid_ipv6_mgmt_validation]
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except  Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
		sleep(60)
                print("Test Case 08 Execution Completed")

        @pytest.mark.run(order=109)
        def test_009_Validate_ssh_admin_login_and_enabled_remote_console_in_Grid_through_IPv6_LAN2_IP_in_Grid_Master(self):
                print("\n============================================\n")
                print(" Validate ssh admin login and enabled remote console in Grid through LAN2 IP in Grid Master ")
                print("\n============================================\n")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_ipv6_lan2)
                        child.logfile=sys.stdout
                        child.expect('password: ')
                        child.sendline('infoblox')
                        child.expect('Infoblox > ')
                        child.sendline('show remote_console')
                        child.expect('>')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = 'Current remote console access settings: enabled'
                        if data in output:
                                assert True
                                print("Remote console access is enabled ")
                        else:
                                assert False
                        print("\n")
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
		sleep(05)
                print("Test Case 09 Execution Completed")

        @pytest.mark.run(order=10)
        def test_010_Validate_Listen_Address_in_sshd_conf_file_through_IPv6_LAN2_IP_in_Grid_Master(self):
                print("\n============================================\n")
                print("Validate Listen Address in sshd conf file through IPv6 LAN2 IP in Grid Master ")
                print("\n============================================\n")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_ipv6_lan2)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        sleep(05)
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print("\n")
                        #data = ['ListenAddress ['+config.grid_ipv6_lan1+']','ListenAddress ['+config.grid_ipv6_lan2+']','ListenAddress '+config.grid_ipv6_mgmt]
			data=['ListenAddress '+config.grid_vip,'ListenAddress '+config.grid_lan1,'ListenAddress '+config.grid_lan2,'ListenAddress ['+config.grid_ipv6_lan1_validation+']','ListenAddress ['+config.grid_ipv6_lan2_validation+']','ListenAddress '+config.grid_ipv6_mgmt_validation]
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
		sleep(05)
                print("Test Case 10 Execution Completed")


###############################
### Interface : MGMT #########
###############################

        @pytest.mark.run(order=11)
        def test_011_Validate_ssh_admin_login_and_enabled_remote_console_in_Grid_through_MGMT_IP_in_Grid_Master(self):
                print("\n============================================\n")
                print(" Validate ssh admin login and enabled remote console in Grid through MGMT IP in Grid Master ")
                print("\n============================================\n")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('password: ')
                        child.sendline('infoblox')
                        child.expect('Infoblox > ')
			sleep(05)
                        child.sendline('show remote_console')
                        child.expect('>')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = 'Current remote console access settings: enabled'
                        if data in output:
                                assert True
                                print("Remote console access is enabled ")
                        else:
                                assert False
                        print("\n")
                except Exception as error_message:
                        print(" Remote console access is not enabled ")
                        assert False
                finally:
                        child.close()
		sleep(05)
                print("Test Case 11 Execution Completed")


        @pytest.mark.run(order=12)
        def test_012_Validate_ssh_root_login_and_PasswordAuthentication_in_sshd_conf_through_MGMT_IP_in_Grid_Master(self):
                print("\n============================================\n")
                print(" Validate ssh root login and PasswordAuthentication in sshd conf through MGMT IP in Grid Master ")
                print("\n============================================\n")
		sleep(10)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
			sleep(05)
			child.sendline('grep -e PermitRootLogin -e PasswordAuthentication /storage/etc/sshd_config')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        sleep(05)
                        data = ['PermitRootLogin yes','PasswordAuthentication yes']
                        for i in data:
                                if i in output:
                                        assert True
                                        print(data)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("\n")
		sleep(05)
                print("Test Case 12 Execution Completed")


        @pytest.mark.run(order=13)
        def test_013_Validate_Listen_Address_in_sshd_conf_file_through_MGMT_IP_in_Grid_Master(self):
                print("\n============================================\n")
                print(" Validate Listen Address in sshd conf file through MGMT IP in Grid Master ")
                print("\n============================================\n")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
			sleep(10)
                        child.logfile=sys.stdout
                        child.expect('#')
			sleep(05)
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        #data = ['ListenAddress '+config.grid_vip,'ListenAddress '+config.grid_lan2,'ListenAddress '+config.grid_MGMT_IP]
			data=['ListenAddress '+config.grid_vip,'ListenAddress '+config.grid_lan1,'ListenAddress '+config.grid_lan2,'ListenAddress ['+config.grid_ipv6_lan1_validation+']','ListenAddress ['+config.grid_ipv6_lan2_validation+']','ListenAddress '+config.grid_ipv6_mgmt_validation]
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
		sleep(05)
                print("Test Case 13 Execution Completed")

        @pytest.mark.run(order=14)
        def test_014_Validate_ssh_admin_login_and_enabled_remote_console_in_Grid_through_IPv6_MGMT_IP_in_Grid_Master(self):
                print("\n============================================\n")
                print(" Validate ssh admin login and enabled remote console in Grid through IPv6 MGMT IP in Grid Master ")
                print("\n============================================\n")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_ipv6_mgmt)
                        child.logfile=sys.stdout
                        child.expect('password: ')
                        child.sendline('infoblox')
                        child.expect('Infoblox > ')
                        child.sendline('show remote_console')
                        child.expect('>')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = 'Current remote console access settings: enabled'
                        if data in output:
                                assert True
                                print("Remote console access is enabled ")
                        else:
                                assert False
                        print("\n")
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
		sleep(60)
                print("Test Case 14 Execution Completed")

        @pytest.mark.run(order=15)
        def test_015_Validate_Listen_Address_in_sshd_conf_file_through_IPv6_MGMT_IP_in_Grid_Master(self):
                print("\n============================================\n")
                print("Validate Listen Address in sshd conf file through IPv6 MGMT IP in Grid Master ")
                print("\n============================================\n")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_ipv6_mgmt)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        sleep(05)
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print("\n")
                        #data = ['ListenAddress ['+config.grid_ipv6_lan1+']','ListenAddress ['+config.grid_ipv6_lan2+']','ListenAddress '+config.grid_ipv6_mgmt]
			data=['ListenAddress '+config.grid_vip,'ListenAddress '+config.grid_lan1,'ListenAddress '+config.grid_lan2,'ListenAddress ['+config.grid_ipv6_lan1_validation+']','ListenAddress ['+config.grid_ipv6_lan2_validation+']','ListenAddress '+config.grid_ipv6_mgmt_validation]
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
		sleep(05)
                print("Test Case 15 Execution Completed")




###################
### HA Scenarios ##
###################

############
## HA VIP ##
############


        @pytest.mark.run(order=16)
        def test_016_Validate_ssh_admin_login_and_enabled_remote_console_in_Grid_through_HA_VIP_in_HA_Member(self):
                print("\n============================================\n")
                print(" Validate ssh admin login and enabled remote console in Grid through HA VIP in HA Member ")
                print("\n============================================\n")
		sleep(10)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_HA_VIP)
                        child.logfile=sys.stdout
                        child.expect('password: ')
                        child.sendline('infoblox')
                        child.expect('Infoblox > ')
                        child.sendline('show remote_console')
                        child.expect('>')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = 'Current remote console access settings: enabled'
                        if data in output:
                                assert True
                                print("Remote console access is enabled ")
                        else:
                                assert False
                        print("\n")
                except Exception as error_message:
                        print(" Remote console access is not enabled ")
                        assert False
                finally:
                        child.close()
		sleep(05)
                print("Test Case 16 Execution Completed")


        @pytest.mark.run(order=17)
        def test_017_Validate_ssh_root_login_and_PasswordAuthentication_and_PermitRootLogin_in_sshd_conf_through_HA_VIP_in_HA_Member(self):
                print("\n============================================\n")
                print(" Validate ssh root login and PasswordAuthentication and PermitRootLogin in sshd conf through HA VIP in HA Member ")
                print("\n============================================\n")
		sleep(10)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_HA_VIP)
                        child.logfile=sys.stdout
                        child.expect('#')
			child.sendline('grep -e PasswordAuthentication -e PermitRootLogin /storage/etc/sshd_config')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ['PermitRootLogin yes','PasswordAuthentication yes']
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
		sleep(05)
                print("\n")
                print("Test Case 17 Execution Completed")


        @pytest.mark.run(order=18)
        def test_018_Validate_Listen_Address_in_sshd_conf_file_through_HA_VIP_in_HA_Member(self):
                print("\n============================================\n")
                print(" Validate Listen Address in sshd conf file through HA VIP in HA Member ")
                print("\n============================================\n")
		sleep(10)
                try:
			child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_HA_ACTIVE)
                        child.logfile=sys.stdout
                        child.expect('password: ')
                        child.sendline('infoblox')
                        child.expect('Infoblox > ')
                        child.sendline('show network')
                        child.expect('>')
                        output = child.before
			sleep(05)
                        output = output.replace("\r\n"," ")
			Active_HA_Local_IP = re.search('HA Local IPv4 Address(.*)Grid Status', output)
			if Active_HA_Local_IP==None:
				assert False
			else:
	                	Active_HA_Local_IP = Active_HA_Local_IP.group(0)
			Active_HA_Local_IP=Active_HA_Local_IP.replace("HA Local IPv4 Address:","").replace("Grid Status","").replace(" ","")
			print("\n")
			print("Active_HA_Local_IP ",Active_HA_Local_IP)
			print("\n")
			sleep(60)
			child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_HA_PASSIVE)
                        child.logfile=sys.stdout
                        child.expect('password: ')
                        child.sendline('infoblox')
                        child.expect('Infoblox > ')
                        child.sendline('show network')
                        child.expect('>')
                        output = child.before
			sleep(05)
                        output = output.replace("\r\n"," ")
                        Passive_HA_Local_IP = re.search('HA Local IPv4 Address(.*)Grid Status', output)
			if Passive_HA_Local_IP==None:
                                assert False
                        else:
                        	Passive_HA_Local_IP = Passive_HA_Local_IP.group(0)
                        Passive_HA_Local_IP = Passive_HA_Local_IP.replace("HA Local IPv4 Address:","").replace("Grid Status","").replace(" ","")
			print("\n")
                        print("Passive_HA_Local_IP ",Passive_HA_Local_IP)
			
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_HA_VIP)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        output = child.before
			sleep(05)
                        output = output.replace("\r\n"," ")
                        data = ['ListenAddress '+config.grid_HA_VIP,'ListenAddress '+config.grid_HA_ACTIVE,'ListenAddress '+Active_HA_Local_IP]
			print("\n")
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
			
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                print("Test Case 18 Execution Completed")


        @pytest.mark.run(order=19)
        def test_019_Validate_ssh_admin_login_and_enabled_remote_console_in_Grid_through_IPv6_HA_VIP_in_Grid_Master(self):
                print("\n============================================\n")
                print(" Validate ssh admin login and enabled remote console in Grid through IPv6 HA VIP in Grid Master ")
                print("\n============================================\n")
		sleep(100)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_ipv6_HA_vip)
                        child.logfile=sys.stdout
                        child.expect('password: ')
                        child.sendline('infoblox')
                        child.expect('Infoblox > ')
                        child.sendline('show remote_console')
                        child.expect('>')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = 'Current remote console access settings: enabled'
                        if data in output:
                                assert True
                                print("Remote console access is enabled ")
                        else:
                                assert False
                        print("\n")
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 19 Execution Completed")

        @pytest.mark.run(order=20)
        def test_020_Validate_Listen_Address_in_sshd_conf_file_through_IPv6_HA_VIP_in_Grid_Master(self):
                print("\n============================================\n")
                print("Validate Listen Address in sshd conf file through IPv6 HA VIP in Grid Master ")
                print("\n============================================\n")
		sleep(10)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_ipv6_HA_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        sleep(05)
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print("\n")
                        data = ['ListenAddress ['+config.grid_ipv6_HA_vip_validation+']','ListenAddress ['+config.grid_ipv6_HA_Active_validation+']']
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                print("Test Case 20 Execution Completed")


###############
## HA Active ##
###############


        @pytest.mark.run(order=21)
        def test_021_Validate_ssh_admin_login_and_enabled_remote_console_in_HA_Member_through_HA_Active_IP(self):
                print("\n============================================\n")
                print(" Validate ssh admin login and enabled remote console in HA Member through HA Active ")
                print("\n============================================\n")
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_HA_ACTIVE)
                        child.logfile=sys.stdout
                        child.expect('password: ')
                        child.sendline('infoblox')
                        child.expect('Infoblox > ')
                        child.sendline('show remote_console')
                        child.expect('>')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = 'Current remote console access settings: enabled'
                        if data in output:
                                assert True
                                print("Remote console access is enabled ")
                        else:
                                assert False
                        print("\n")
                except Exception as error_message:
                        print(" Remote console access is not enabled ")
                        assert False
                finally:
                        child.close()
                print("Test Case 21 Execution Completed")


        @pytest.mark.run(order=22)
        def test_022_Validate_ssh_root_login_and_PasswordAuthentication_and_PermitRootLogin_in_HA_Member_through_HA_Active_IP(self):
                print("\n============================================\n")
                print(" Validate ssh root login and PasswordAuthentication and PermitRootLogin in HA Member through HA Active IP ")
                print("\n============================================\n")
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_HA_ACTIVE)
                        child.logfile=sys.stdout
                        child.expect('#')
			sleep(05)
                        child.sendline('grep -e PasswordAuthentication -e PermitRootLogin /storage/etc/sshd_config')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ['PermitRootLogin yes','PasswordAuthentication yes']
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                print("Test Case 22 Execution Completed")


        @pytest.mark.run(order=23)
        def test_023_Validate_Listen_Address_in_sshd_conf_file_in_HA_Member_through_HA_Active_IP(self):
                print("\n============================================\n")
                print(" Validate Listen Address in sshd conf file in HA Member through HA Active IP ")
                print("\n============================================\n")
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_HA_ACTIVE)
                        child.logfile=sys.stdout
                        child.expect('password: ')
                        child.sendline('infoblox')
                        child.expect('Infoblox > ')
                        child.sendline('show network')
                        child.expect('>')
                        output = child.before
                        output = output.replace("\r\n"," ")
			sleep(05)
                        Active_HA_Local_IP = re.search('HA Local IPv4 Address(.*)Grid Status', output)
			if Active_HA_Local_IP==None:
				assert False
			else:
                        	Active_HA_Local_IP = Active_HA_Local_IP.group(0)
                        Active_HA_Local_IP=Active_HA_Local_IP.replace("HA Local IPv4 Address:","").replace("Grid Status","").replace(" ","")
                        print("\n")
                        print("Active_HA_Local_IP",Active_HA_Local_IP)
                        print("\n")

                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_HA_ACTIVE)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        output = child.before
			sleep(10)
                        output = output.replace("\r\n"," ")
                        data = ['ListenAddress '+config.grid_HA_VIP,'ListenAddress '+config.grid_HA_ACTIVE,'ListenAddress '+Active_HA_Local_IP]
                        print("\n")
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False

                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                print("Test Case 23 Execution Completed")



        @pytest.mark.run(order=24)
        def test_024_Validate_ssh_admin_login_and_enabled_remote_console_in_Grid_through_IPv6_HA_Active_IP_in_Grid_Master(self):
                print("\n============================================\n")
                print(" Validate ssh admin login and enabled remote console in Grid through IPv6 HA Active IP in Grid Master ")
                print("\n============================================\n")
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_ipv6_HA_Active)
                        child.logfile=sys.stdout
                        child.expect('password: ')
                        child.sendline('infoblox')
                        child.expect('Infoblox > ')
                        child.sendline('show remote_console')
                        child.expect('>')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = 'Current remote console access settings: enabled'
                        if data in output:
                                assert True
                                print("Remote console access is enabled ")
                        else:
                                assert False
                        print("\n")
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 24 Execution Completed")

        @pytest.mark.run(order=25)
        def test_025_Validate_Listen_Address_in_sshd_conf_file_through_IPv6_HA_Active_IP_in_Grid_Master(self):
                print("\n============================================\n")
                print("Validate Listen Address in sshd conf file through IPv6 HA Active IP in Grid Master ")
                print("\n============================================\n")
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_ipv6_HA_Active)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        sleep(05)
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print("\n")
                        data = ['ListenAddress ['+config.grid_ipv6_HA_vip_validation+']','ListenAddress ['+config.grid_ipv6_HA_Active_validation+']']
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                print("Test Case 25 Execution Completed")



################
## HA Passive ##
################


        @pytest.mark.run(order=26)
        def test_026_Validate_ssh_admin_login_and_enabled_remote_console_in_HA_Member_through_HA_Passive_IP(self):
                print("\n============================================\n")
                print(" Validate ssh admin login and enabled remote console in HA Member through HA Passive IP ")
                print("\n============================================\n")
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_HA_PASSIVE)
                        child.logfile=sys.stdout
                        child.expect('password: ')
                        child.sendline('infoblox')
                        child.expect('Infoblox > ')
                        child.sendline('show remote_console')
                        child.expect('>')
                        output = child.before
			sleep(05)
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = 'Current remote console access settings: enabled'
                        if data in output:
                                assert True
                                print("Remote console access is enabled ")
                        else:
                                assert False
                        print("\n")
                except Exception as error_message:
                        print(" Remote console access is not enabled ")
                        assert False
                finally:
                        child.close()
                print("Test Case 26 Execution Completed")


        @pytest.mark.run(order=27)
        def test_027_Validate_ssh_root_login_and_PasswordAuthentication_and_PermitRootLogin_in_HA_Member_through_HA_Passive_IP(self):
                print("\n============================================\n")
                print(" Validate ssh root login and PasswordAuthentication and PermitRootLogin in HA Member through HA Passive IP ")
                print("\n============================================\n")
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_HA_PASSIVE)
                        child.logfile=sys.stdout
                        child.expect('#')
			sleep(05)
                        child.sendline('grep -e PasswordAuthentication -e PermitRootLogin /storage/etc/sshd_config')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ['PermitRootLogin yes','PasswordAuthentication yes']
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                print("Test Case 27 Execution Completed")


        @pytest.mark.run(order=28)
        def test_028_Validate_Listen_Address_in_sshd_conf_file_in_HA_Member_through_HA_Passive_IP(self):
                print("\n============================================\n")
                print(" Validate Listen Address in sshd conf file in HA Member through HA Passive IP ")
                print("\n============================================\n")
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_HA_PASSIVE)
                        child.logfile=sys.stdout
                        child.expect('password: ')
                        child.sendline('infoblox')
                        child.expect('Infoblox > ')
                        child.sendline('show network')
                        child.expect('>')
                        output = child.before
			sleep(05)
                        output = output.replace("\r\n"," ")
                        Passive_HA_Local_IP = re.search('HA Local IPv4 Address(.*)Grid Status', output)
			if Passive_HA_Local_IP==None:
				assert False
			else:
	                        Passive_HA_Local_IP = Passive_HA_Local_IP.group(0)
                        Passive_HA_Local_IP = Passive_HA_Local_IP.replace("HA Local IPv4 Address:","").replace("Grid Status","").replace(" ","")
                        print("\n")
                        print("Passive_HA_Local_IP ",Passive_HA_Local_IP)

                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_HA_PASSIVE)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        data = ['ListenAddress '+config.grid_HA_PASSIVE,'ListenAddress '+Passive_HA_Local_IP]
                        print("\n")
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False

                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                print("Test Case 28 Execution Completed")

        @pytest.mark.run(order=29)
        def test_029_Validate_ssh_admin_login_and_enabled_remote_console_in_Grid_through_IPv6_HA_Passive_IP_in_Grid_Master(self):
                print("\n============================================\n")
                print(" Validate ssh admin login and enabled remote console in Grid through IPv6 HA Passive IP in Grid Master ")
                print("\n============================================\n")
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_ipv6_HA_Passive)
                        child.logfile=sys.stdout
                        child.expect('password: ')
                        child.sendline('infoblox')
                        child.expect('Infoblox > ')
                        child.sendline('show remote_console')
                        child.expect('>')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = 'Current remote console access settings: enabled'
                        if data in output:
                                assert True
                                print("Remote console access is enabled ")
                        else:
                                assert False
                        print("\n")
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 29 Execution Completed")

        @pytest.mark.run(order=30)
        def test_030_Validate_Listen_Address_in_sshd_conf_file_through_IPv6_HA_Passive_IP_in_Grid_Master(self):
                print("\n============================================\n")
                print("Validate Listen Address in sshd conf file through IPv6 HA Passive IP in Grid Master ")
                print("\n============================================\n")
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_ipv6_HA_Passive)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        sleep(05)
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print("\n")
                        data = ('ListenAddress ['+config.grid_ipv6_HA_Passive_validation+']')
                        if data in output:
                        	assert True
                        else:
                        	assert False
			print(data)
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                print("Test Case 30 Execution Completed")


#################
## HA Failover ##
#################


        @pytest.mark.run(order=31)
        def test_031_Reboot_HA_Active_member_to_Perform_HA_failover(self):
                print("\n============================================\n")
                print(" Reboot HA Active member to Perform HA failover ")
                print("\n============================================\n")
		sleep(05)
		vm_reboot=os.popen("reboot_system -H "+config.Active_VM_ID).read()
                print(vm_reboot)
		sleep(1000)
                print("Test Case 31 Execution Completed")


############
## HA VIP ##
############


        @pytest.mark.run(order=32)
        def test_032_Validate_After_HA_Failover_ssh_login_and_enabled_remote_console_in_HA_Member_through_HA_VIP(self):
                print("\n============================================\n")
                print(" Validate After HA Failover ssh login and enabled remote console in HA Member through HA VIP ")
                print("\n============================================\n")
		sleep(60)
                try:
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid_HA_VIP)
                        child.logfile=sys.stdout
                        child.expect('password: ')
                        child.sendline('infoblox')
                        child.expect('Infoblox > ')
			sleep(10)
                        child.sendline('show remote_console')
                        child.expect('>')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = 'Current remote console access settings: enabled'
                        if data in output:
                                assert True
                                print("Remote console access is enabled ")
                        else:
                                assert False
                        print("\n")
                except Exception as error_message:
                        print(" Remote console access is not enabled ")
                        assert False
                finally:
                        child.close()
                print("Test Case 32 Execution Completed")


        @pytest.mark.run(order=33)
        def test_033_Validate_After_HA_Failover_ssh_root_login_and_PasswordAuthentication_and_PermitRootLogin_in_HA_Member_through_HA_VIP(self):
                print("\n============================================\n")
                print(" Validate After HA Failover ssh root login and PasswordAuthentication and PermitRootLogin in HA Member through HA VIP ")
                print("\n============================================\n")
		sleep(30)
                try:
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_HA_VIP)
                        child.logfile=sys.stdout
                        child.expect('#')
			sleep(60)
                        child.sendline('grep -e PasswordAuthentication -e PermitRootLogin /storage/etc/sshd_config')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ['PermitRootLogin yes','PasswordAuthentication yes']
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                print("Test Case 33 Execution Completed")


        @pytest.mark.run(order=34)
        def test_034_Validate_After_HA_Failover_Listen_Address_in_HA_Member_through_HA_VIP(self):
                print("\n============================================\n")
                print(" Validate After HA Failover Listen Address in HA Member through HA VIP ")
                print("\n============================================\n")
		sleep(10)
                try:

                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid_HA_PASSIVE)
                        child.logfile=sys.stdout
                        child.expect('password: ')
                        child.sendline('infoblox')
                        child.expect('Infoblox > ')
                        child.sendline('show network')
                        child.expect('>')
                        output = child.before
			sleep(05)
                        output = output.replace("\r\n"," ")
                        Passive_HA_Local_IP = re.search('HA Local IPv4 Address(.*)Grid Status', output)
			if Passive_HA_Local_IP==None:
				assert False
			else:
                        	Passive_HA_Local_IP = Passive_HA_Local_IP.group(0)
                        Passive_HA_Local_IP = Passive_HA_Local_IP.replace("HA Local IPv4 Address:","").replace("Grid Status","").replace(" ","")
                        print("\n")
                        print("Passive_HA_Local_IP ",Passive_HA_Local_IP)
			sleep(60)
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_HA_VIP)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        output = child.before
			print(output)
			sleep(05)
                        output = output.replace("\r\n"," ")
			print(output)
                        data = ['ListenAddress '+config.grid_HA_VIP,'ListenAddress '+config.grid_HA_PASSIVE,'ListenAddress '+Passive_HA_Local_IP]
                        print("\n")
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False

                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                print("Test Case 34 Execution Completed")


        @pytest.mark.run(order=35)
        def test_035_Validate_After_HA_Failover_ssh_login_and_enabled_remote_console_in_IPv6_HA_VIP(self):
                print("\n============================================\n")
                print(" Validate After HA Failover ssh login and enabled remote console in IPv6 HA VIP ")
                print("\n============================================\n")
		sleep(15)
                try:
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid_ipv6_HA_vip)
                        child.logfile=sys.stdout
                        child.expect('password: ')
                        child.sendline('infoblox')
                        child.expect('Infoblox > ')
                        sleep(10)
                        child.sendline('show remote_console')
                        child.expect('>')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = 'Current remote console access settings: enabled'
                        if data in output:
                                assert True
                                print("Remote console access is enabled ")
                        else:
                                assert False
                        print("\n")
                except Exception as error_message:
                        print(" Remote console access is not enabled ")
                        assert False
                finally:
                        child.close()
                print("Test Case 35 Execution Completed")


        @pytest.mark.run(order=36)
        def test_036_Validate_After_HA_Failover_ssh_root_login_and_PasswordAuthentication_and_PermitRootLogin_in_IPv6_HA_VIP(self):
                print("\n============================================\n")
                print(" Validate After HA Failover ssh root login and PasswordAuthentication and PermitRootLogin in IPv6 HA VIP ")
                print("\n============================================\n")
		sleep(10)
                try:
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_ipv6_HA_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        sleep(10)
                        child.sendline('grep -e PasswordAuthentication -e PermitRootLogin /storage/etc/sshd_config')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ['PermitRootLogin yes','PasswordAuthentication yes']
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                print("Test Case 36 Execution Completed")

        @pytest.mark.run(order=37)
        def test_037_Validate_Listen_Address_in_sshd_conf_file_through_IPv6_HA_VIP_in_Grid_Master(self):
                print("\n============================================\n")
                print("Validate Listen Address in sshd conf file through IPv6 HA VIP in Grid Master ")
                print("\n============================================\n")
		sleep(10)
                try:
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_ipv6_HA_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        sleep(05)
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print("\n")
                        data = ['ListenAddress ['+config.grid_ipv6_HA_vip_validation+']','ListenAddress ['+config.grid_ipv6_HA_Passive_validation+']']
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                print("Test Case 37 Execution Completed")




###############
## HA Active ##
###############


        @pytest.mark.run(order=38)
        def test_038_Validate_After_HA_Failover_ssh_admin_login_and_enabled_remote_console_in_HA_Member_through_HA_Active_IP(self):
                print("\n============================================\n")
                print(" Validate After HA Failover ssh admin login and enabled remote console in HA Member through HA Active IP ")
                print("\n============================================\n")
		sleep(30)
                try:
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid_HA_PASSIVE)
                        child.logfile=sys.stdout
                        child.expect('password: ')
                        child.sendline('infoblox')
                        child.expect('Infoblox > ')
			sleep(05)
                        child.sendline('show remote_console')
                        child.expect('>')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = 'Current remote console access settings: enabled'
                        if data in output:
                                assert True
                                print("Remote console access is enabled ")
                        else:
                                assert False
                        print("\n")
                except Exception as error_message:
                        print(" Remote console access is not enabled ")
                        assert False
                finally:
                        child.close()
                print("Test Case 38 Execution Completed")


        @pytest.mark.run(order=39)
        def test_039_Validate_After_HA_Failover_ssh_root_login_and_PasswordAuthentication_and_PermitRootLogin_in_HA_Member_through_HA_Active_IP(self):
                print("\n============================================\n")
                print(" Validate After HA Failover ssh root login and PasswordAuthentication and PermitRootLogin in HA Member through HA Active IP ")
                print("\n============================================\n")
		sleep(10)
                try:
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_HA_PASSIVE)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('grep -e PasswordAuthentication -e PermitRootLogin /storage/etc/sshd_config')
                        child.expect('#')
                        output = child.before
			sleep(05)
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ['PermitRootLogin yes','PasswordAuthentication yes']
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                print("Test Case 39 Execution Completed")


        @pytest.mark.run(order=40)
        def test_040_Validate_After_HA_Failover_Listen_Address_in_HA_Member_through_HA_Active_IP(self):
                print("\n============================================\n")
                print(" Validate After HA Failover Listen Address in HA Member through HA Active IP ")
                print("\n============================================\n")
		sleep(10)
                try:

                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid_HA_PASSIVE)
                        child.logfile=sys.stdout
                        child.expect('password: ')
                        child.sendline('infoblox')
                        child.expect('Infoblox > ')
			sleep(05)
                        child.sendline('show network')
                        child.expect('>')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        Passive_HA_Local_IP = re.search('HA Local IPv4 Address(.*)Grid Status', output)
			if Passive_HA_Local_IP==None:
				assert False
			else:
	                        Passive_HA_Local_IP = Passive_HA_Local_IP.group(0)
                        Passive_HA_Local_IP = Passive_HA_Local_IP.replace("HA Local IPv4 Address:","").replace("Grid Status","").replace(" ","")
                        print("\n")
                        print("Passive_HA_Local_IP ",Passive_HA_Local_IP)
			sleep(60)
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_HA_PASSIVE)
                        child.logfile=sys.stdout
                        child.expect('#')
			sleep(05)
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        output = child.before
                        print(output)
			sleep(05)
                        output = output.replace("\r\n"," ")
                        print(output)
                        data = ['ListenAddress '+config.grid_HA_VIP,'ListenAddress '+config.grid_HA_PASSIVE,'ListenAddress '+Passive_HA_Local_IP]
                        print("\n")
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False

                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                print("Test Case 40 Execution Completed")

        @pytest.mark.run(order=41)
        def test_041_Validate_After_HA_Failover_ssh_login_and_enabled_remote_console_in_HA_VIP(self):
                print("\n============================================\n")
                print(" Validate After HA Failover ssh login and enabled remote console in HA VIP ")
                print("\n============================================\n")
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid_ipv6_HA_Passive)
                        child.logfile=sys.stdout
                        child.expect('password: ')
                        child.sendline('infoblox')
                        child.expect('Infoblox > ')
                        sleep(10)
                        child.sendline('show remote_console')
                        child.expect('>')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = 'Current remote console access settings: enabled'
                        if data in output:
                                assert True
                                print("Remote console access is enabled ")
                        else:
                                assert False
                        print("\n")
                except Exception as error_message:
                        print(" Remote console access is not enabled ")
                        assert False
                finally:
                        child.close()
                print("Test Case 41 Execution Completed")

        @pytest.mark.run(order=42)
        def test_042_Validate_After_HA_Failover_ssh_root_login_and_PasswordAuthentication_and_PermitRootLogin_in_HA_VIP(self):
                print("\n============================================\n")
                print(" Validate After HA Failover ssh root login and PasswordAuthentication and PermitRootLogin in HA VIP ")
                print("\n============================================\n")
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_ipv6_HA_Passive)
                        child.logfile=sys.stdout
                        child.expect('#')
                        sleep(10)
                        child.sendline('grep -e PasswordAuthentication -e PermitRootLogin /storage/etc/sshd_config')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ['PermitRootLogin yes','PasswordAuthentication yes']
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                print("Test Case 42 Execution Completed")

        @pytest.mark.run(order=43)
        def test_043_Validate_Listen_Address_in_sshd_conf_file_through_IPv6_HA_VIP_in_Grid_Master(self):
                print("\n============================================\n")
                print("Validate Listen Address in sshd conf file through IPv6 HA VIP in Grid Master ")
                print("\n============================================\n")
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_ipv6_HA_Passive)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        sleep(05)
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print("\n")
                        data = ['ListenAddress ['+config.grid_ipv6_HA_vip_validation+']','ListenAddress ['+config.grid_ipv6_HA_Passive_validation+']']
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                print("Test Case 43 Execution Completed")

################
## HA Passive ##
################


        @pytest.mark.run(order=44)
        def test_044_Validate_After_HA_Failover_ssh_admin_login_and_enabled_remote_console_in_HA_Member_through_HA_Passive_IP(self):
                print("\n============================================\n")
                print(" Validate After HA Failover ssh admin login and enabled remote console in HA Member through HA Passive IP ")
                print("\n============================================\n")
		sleep(100)
                try:
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid_HA_ACTIVE)
                        child.logfile=sys.stdout
                        child.expect('password: ')
                        child.sendline('infoblox')
                        child.expect('Infoblox > ')
                        child.sendline('show remote_console')
                        child.expect('>')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = 'Current remote console access settings: enabled'
                        if data in output:
                                assert True
                                print("Remote console access is enabled ")
                        else:
                                assert False
                        print("\n")
                except Exception as error_message:
                        print(" Remote console access is not enabled ")
                        assert False
                finally:
                        child.close()
                print("Test Case 44 Execution Completed")

        @pytest.mark.run(order=45)
        def test_045_Validate_After_HA_Failover_ssh_root_login_and_PasswordAuthentication_and_PermitRootLogin_in_HA_Member_through_HA_Passive_IP(self):
                print("\n============================================\n")
                print(" Validate After HA Failover ssh root login and PasswordAuthentication and PermitRootLogin in HA Member through HA Passive IP ")
                print("\n============================================\n")
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_HA_ACTIVE)
                        child.logfile=sys.stdout
                        child.expect('#')
			sleep(05)
                        child.sendline('grep -e PasswordAuthentication -e PermitRootLogin /storage/etc/sshd_config')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ['PermitRootLogin yes','PasswordAuthentication yes']
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                print("Test Case 45 Execution Completed")


        @pytest.mark.run(order=46)
        def test_046_Validate_After_HA_Failover_Listen_Address_in_HA_Member_through_HA_Passive_IP(self):
                print("\n============================================\n")
                print(" Validate After HA Failover Listen Address in HA Member through HA Passive IP ")
                print("\n============================================\n")
		sleep(60)
                try:

                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid_HA_ACTIVE)
                        child.logfile=sys.stdout
                        child.expect('password: ')
                        child.sendline('infoblox')
                        child.expect('Infoblox > ')
                        child.sendline('show network')
                        child.expect('>')
                        output = child.before
                        output = output.replace("\r\n"," ")
			sleep(05)
                        Passive_HA_Local_IP = re.search('HA Local IPv4 Address(.*)Grid Status', output)
			if Passive_HA_Local_IP==None:
				assert False
			else:
                        	Passive_HA_Local_IP = Passive_HA_Local_IP.group(0)
                        Passive_HA_Local_IP = Passive_HA_Local_IP.replace("HA Local IPv4 Address:","").replace("Grid Status","").replace(" ","")
                        print("\n")
                        print("Passive_HA_Local_IP ",Passive_HA_Local_IP)

                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_HA_ACTIVE)
                        child.logfile=sys.stdout
                        child.expect('#')
			sleep(05)
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        output = child.before
                        print(output)
                        output = output.replace("\r\n"," ")
			sleep(05)
                        data = ['ListenAddress '+config.grid_HA_ACTIVE,'ListenAddress '+Passive_HA_Local_IP]
                        print("\n")
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False

                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                print("Test Case 46 Execution Completed")

        @pytest.mark.run(order=47)
        def test_047_Validate_After_HA_Failover_ssh_login_and_enabled_remote_console_in_HA_VIP(self):
                print("\n============================================\n")
                print(" Validate After HA Failover ssh login and enabled remote console in HA VIP ")
                print("\n============================================\n")
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid_ipv6_HA_Active)
                        child.logfile=sys.stdout
                        child.expect('password: ')
                        child.sendline('infoblox')
                        child.expect('Infoblox > ')
                        sleep(10)
                        child.sendline('show remote_console')
                        child.expect('>')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = 'Current remote console access settings: enabled'
                        if data in output:
                                assert True
                                print("Remote console access is enabled ")
                        else:
                                assert False
                        print("\n")
                except Exception as error_message:
                        print(" Remote console access is not enabled ")
                        assert False
                finally:
                        child.close()
                print("Test Case 47 Execution Completed")

        @pytest.mark.run(order=48)
        def test_048_Validate_After_HA_Failover_ssh_root_login_and_PasswordAuthentication_and_PermitRootLogin_in_HA_VIP(self):
                print("\n============================================\n")
                print(" Validate After HA Failover ssh root login and PasswordAuthentication and PermitRootLogin in HA VIP ")
                print("\n============================================\n")
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_ipv6_HA_Active)
                        child.logfile=sys.stdout
                        child.expect('#')
                        sleep(10)
                        child.sendline('grep -e PasswordAuthentication -e PermitRootLogin /storage/etc/sshd_config')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ['PermitRootLogin yes','PasswordAuthentication yes']
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                print("Test Case 48 Execution Completed")
                                                                                                     

        @pytest.mark.run(order=49)
        def test_049_Validate_Listen_Address_in_sshd_conf_file_through_IPv6_HA_VIP_in_Grid_Master(self):
                print("\n============================================\n")
                print("Validate Listen Address in sshd conf file through IPv6 HA VIP in Grid Master ")
                print("\n============================================\n")
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_ipv6_HA_Active)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        child.sendline('grep ListenAddress /storage/etc/sshd_config')
                        child.expect('#')
                        sleep(05)
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print("\n")
                        data = ('ListenAddress ['+config.grid_ipv6_HA_Active_validation+']')
                        if data in output:
                        	assert True
                                print(data)
                        else:
                        	assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                print("Test Case 49 Execution Completed")



#####
	 
        @pytest.mark.run(order=50)
        def test_050_Validate_PasswordAuthentication_and_PermitRootLogin_should_be_set_to_no_in_sshd_conf_file_after_disabling_remote_console(self):
                print("\n============================================\n")
                print("Validate PasswordAuthentication and PermitRootLogin should be set to no in sshd conf file after disabling remote console")
                print("\n============================================\n")
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid_vip)
                        child.expect('password: ')
                        child.sendline('infoblox')
                        child.expect('Infoblox > ')
                        child.sendline('set remote_console')
                        child.expect(':')
                        child.sendline('n')
                        child.expect(':')
                        child.sendline('y')
                        child.expect('Infoblox > ')
                        child.sendline('exit')
                        child.expect('#')
                        sleep(60)
                        child.sendline('grep -e PasswordAuthentication -e PermitRootLogin /storage/etc/sshd_config')
                        child.expect('#')
                        output = child.before
                        output = output.replace("\r\n"," ")
                        print("\n")
                        print(output)
                        print("\n")
                        data = ['PermitRootLogin no','PasswordAuthentication no']
                        for i in data:
                                if i in output:
                                        assert True
                                        print(i)
                                else:
                                        assert False
                except Exception as error_message:
                        print(error_message)
                        assert False

                finally:
                        child.close()
                print("\n")
                print("Test Case 50 Execution Completed")

	
        @pytest.mark.run(order=51)
        def test_051_Validate_ssh_access_after_disabling_the_remote_coonsole(self):
                print("\n============================================\n")
                print("Validate ssh access after disabling the remote console")
                print("\n============================================\n")
                sleep(05)
                try:
                        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')			
			sleep(15)
                        child.sendline('ssh admin@'+config.grid_vip)
			child.expect('#')
		except Exception as error_message:
                        print(error_message)
			error_message = str(error_message)
                        if "Permission denied" in error_message:
				assert True
			else:
				assert False

                finally:
                        child.close()
                print("\n")
                print("Test Case 51 Execution Completed")



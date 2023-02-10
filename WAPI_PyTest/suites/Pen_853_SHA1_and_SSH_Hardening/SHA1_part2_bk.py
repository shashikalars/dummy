#!/usr/bin/env python

__author__ = "Prasad K"
__email__  = "pkondisetty@infoblox.com"
__RFE__    = "PenTest 853 SHA1"
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


#function to generate onedb file
def onedb():
        print("\n============================================\n")
        print("generate onedb file under /tmp directory ")
        print("\n============================================\n")
        try:
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('#')
		sleep(10)
                child.sendline('/infoblox/one/bin/db_dump -silvd /tmp/')
                child.expect('#')
		sleep(5)
        except Exception as error_message:
                print("Failed to genarated onedb.xml file ")
                assert False
        finally:
                child.close()


class PenTest_853_SHA1(unittest.TestCase):

		
        @pytest.mark.run(order=01)
        def test_001_Generate_one_db_file_and_validate_without_first_login_admin_user_password_should_be_in_SHA128(self):
                print("\n============================================\n")
                print("Generate one db file and validate without first login admin user password should be in SHA128")
                print("\n============================================\n")
                db =  onedb()
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''grep -A 1 '"name" VALUE="admin"' /tmp/onedb.xml''')
                        child.expect('#')
                        output1 = child.before
                        result = re.search('SAA(.*)==', output1)
                        print(result)
                        if result==None:
                                assert False
                        else:
                                result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 104:
                                assert True
                                print("admin password is in SHA512")
                        else:
                                assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 001 Execution Completed")
	
        @pytest.mark.run(order=02)
        def test_002_Generate_one_db_file_and_validate_admin_users_password_should_be_in_SHA128(self):
                print("\n============================================\n")
                print(" Generate one db file and validate admin users password should be in SHA128 ")
                print("============================================")
                db =  onedb()
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        for i in range(1,6):
                                print("===============================")
                                print("Validating admin"+str(i)+" user password")
                                print("===============================")
                                child.sendline('''grep -A 1 '"name" VALUE="admin'''+str(i)+'''"' /tmp/onedb.xml''')
                                child.expect('#')
                                output = child.before
                                result = re.search('HAA(.*)="', output)
                                print(result)
                                if result==None:
                                        assert False
                                else:
                                        result = result.group(0)
                                print(result)
                                bit_length = len(result)
                                if bit_length == 45:
                                        assert True
                                        print("===============================")
                                        print("admin users password are in SHA128")
                                        print("===============================")
                                        print("\n")
                                else:
                                        assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 002 Execution Completed")

        @pytest.mark.run(order=03)
        def test_003_Generate_one_db_file_and_validate_infoblox_users_password_should_be_in_SHA128(self):
                print("\n============================================\n")
                print("Generate one db file and validate infoblox users password should be in SHA128")
                print("============================================")
                db =  onedb()
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        for i in range(1,6):
                                print("===============================")
                                print("Validating infoblox"+str(i)+" user password")
                                print("===============================")
                                child.sendline('''grep -A 1 '"name" VALUE="infoblox'''+str(i)+'''"' /tmp/onedb.xml''')
                                child.expect('#')
                                output = child.before
                                result = re.search('HAA(.*)="', output)
                                print(result)
                                if result==None:
                                        assert False
                                else:
                                        result = result.group(0)
                                print(result)
                                bit_length = len(result)
                                if bit_length == 45:
                                        assert True
                                        print("===============================")
                                        print("infoblox"+str(i)+" user password is in SHA128")
                                        print("===============================")
                                        print("\n")
                                else:
                                        assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 003 Execution Completed")

        @pytest.mark.run(order=04)
        def test_004_Generate_one_db_file_and_validate_infoblox_api_users_password_should_be_in_SHA128(self):
                print("\n============================================\n")
                print("Generate one db file and validate infoblox api users password should be in SHA128")
                print("============================================")
                db =  onedb()
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        for i in range(1,6):
                                print("===============================")
                                print("Validating infoblox_api"+str(i)+" user password")
                                print("===============================")
                                child.sendline('''grep -A 1 '"name" VALUE="infoblox_api'''+str(i)+'''"' /tmp/onedb.xml''')
                                child.expect('#')
                                output = child.before
                                result = re.search('HAA(.*)="', output)
                                print(result)
                                if result==None:
                                        assert False
                                else:
                                        result = result.group(0)
                                print(result)
                                bit_length = len(result)
                                if bit_length == 45:
                                        assert True
                                        print("===============================")
                                        print("infoblox_api"+str(i)+" user password is in SHA128")
                                        print("===============================")
                                        print("\n")
                                else:
                                        assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 004 Execution Completed")

        @pytest.mark.run(order=05)
        def test_005_Generate_one_db_file_and_validate_infoblox_cli_users_password_should_be_in_SHA128(self):
                print("\n============================================\n")
                print("Generate one db file and validate infoblox_cli users password should be in SHA128")
                print("============================================")
                db =  onedb()
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        for i in range(1,6):
                                print("===============================")
                                print("Validating infoblox_cli"+str(i)+" user password")
                                print("===============================")
                                child.sendline('''grep -A 1 '"name" VALUE="infoblox_cli'''+str(i)+'''"' /tmp/onedb.xml''')
                                child.expect('#')
                                output = child.before
                                result = re.search('HAA(.*)="', output)
                                print(result)
                                if result==None:
                                        assert False
                                else:
                                        result = result.group(0)
                                print(result)
                                bit_length = len(result)
                                if bit_length == 45:
                                        assert True
                                        print("===============================")
                                        print("infoblox_cli"+str(i)+" user password is in SHA128")
                                        print("===============================")
                                        print("\n")
                                else:
                                        assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 005 Execution Completed")

        @pytest.mark.run(order=06)
        def test_006_Generate_one_db_file_and_validate_saml_users_password_should_be_in_SHA128(self):
                print("\n============================================\n")
                print("Generate one db file and validate saml users password should be in SHA128")
                print("============================================")
                db =  onedb()
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        for i in range(1,6):
                                print("===============================")
                                print("Validating saml"+str(i)+" user password")
                                print("===============================")
                                child.sendline('''grep -A 1 '"name" VALUE="saml'''+str(i)+'''"' /tmp/onedb.xml''')
                                child.expect('#')
                                output = child.before
                                result = re.search('HAA(.*)="', output)
                                print(result)
                                if result==None:
                                        assert False
                                else:
                                        result = result.group(0)
                                print(result)
                                bit_length = len(result)
                                if bit_length == 45:
                                        assert True
                                        print("===============================")
                                        print("saml"+str(i)+" user password is in SHA128")
                                        print("===============================")
                                        print("\n")
                                else:
                                        assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 006 Execution Completed")


        @pytest.mark.run(order=07)
        def test_007_Generate_one_db_file_and_validate_nonsuperuser_users_password_should_be_in_SHA128(self):
                print("\n============================================\n")
                print("Generate one db file and validate nonsuperuser users password should be in SHA128")
                print("============================================")
                db =  onedb()
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        for i in range(1,6):
                                print("===============================")
                                print("Validating nonsuperuser"+str(i)+" user password")
                                print("===============================")
                                child.sendline('''grep -A 1 '"name" VALUE="nonsuperuser'''+str(i)+'''"' /tmp/onedb.xml''')
                                child.expect('#')
                                output = child.before
                                result = re.search('HAA(.*)="', output)
                                print(result)
                                if result==None:
                                        assert False
                                else:
                                        result = result.group(0)
                                print(result)
                                bit_length = len(result)
                                if bit_length == 45:
                                        assert True
                                        print("===============================")
                                        print("nonsuperuser"+str(i)+" user password is in SHA128")
                                        print("===============================")
                                        print("\n")
                                else:
                                        assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 007 Execution Completed")


        @pytest.mark.run(order=108)
        def test_008_ADMIN_USER_password_should_not_convert_to_SHA512_during_unsuccessful_login_through_ssh(self):
                print("\n============================================\n")
                print("ADMIN USER password should not convert to SHA512 during authentication failure through ssh")
                print("============================================")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin1@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('password:')
			child.sendline('admin123')
			child.expect('password:')
			child.sendline('admin123')
			child.expect('password:')
			db =  onedb()
			sleep(05)
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
			child.sendline('''/infoblox/one/bin/db_dump -silvd /tmp/''')
                        child.expect('#')
                        sleep(10)
                        child.sendline('''grep -A 1 '"name" VALUE="admin1"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
			result = re.search('HAA(.*)="', output)
                        print(result)
                        if result==None:
                                assert False
                        else:
                                result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 45:
                                assert True
                                print("===============================")
                                print("admin1 user password is in SHA128")
                                print("===============================")
                                print("\n")
                        else:
                                assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 008 Execution Completed")


        @pytest.mark.run(order=109)
        def test_009_Perform_WAPI_call_with_wrong_credentials_to_validate_admin_user_SHA512_password(self):
                print("\n============================================\n")
                print("Perform WAPI call with wrong credentials to validate admin user SHA512 password")
                print("============================================")
		command = ('curl -k1 -u admin1:admin321 -H "Content-Type:application/json" -X GET https://'+config.grid_vip+'/wapi/v'+config.wapi_version+'/grid')
                output = os.popen(command).read()
                print(output)
		if "Internal Server Error" in output or "Authorization Required" in output:
			assert True
		else:
			assert False
		print("\n")
		print("==========================")
		print("Test Case 009 Execution Completed")

        @pytest.mark.run(order=10)
        def test_010_ADMIN_USER_password_should_not_convert_to_SHA512_during_unsuccessful_login_through_WAPI(self):
                print("\n============================================\n")
                print("ADMIN USER password should not convert to SHA512 during authentication failure through WAPI")
                print("============================================")
		db =  onedb()
		sleep(05)
		try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''grep -A 1 '"name" VALUE="admin1"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
                        result = re.search('HAA(.*)="', output)
                        print(result)
                        if result==None:
                        	assert False
                        else:
                                result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 45:
                                assert True
                                print("===============================")
                                print("admin1 user password is in SHA128")
                                print("===============================")
                                print("\n")
                        else:
                                assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 010 Execution Completed")

	
        @pytest.mark.run(order=11)
        def test_011_ADMIN_USER_validate_password_should_be_converted_to_SHA512_during_first_successful_login_through_ssh(self):
                print("\n============================================\n")
                print("ADMIN USER validate password should be converted to SHA512 during first successful login through ssh")
                print("============================================")
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin1@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('password:')
                        child.sendline('admin1')
                        child.expect('>')
                        db =  onedb()
			sleep(10)
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
			child.sendline('''grep -A 1 '"name" VALUE="admin1"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
                        result = re.search('SAA(.*)==', output)
                        print(result)
                        if result==None:
                        	assert False
                        else:
                                result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 104:
                                assert True
                                print("admin password is in SHA512")
                        else:
                                assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 011 Execution Completed")

        @pytest.mark.run(order=12)
        def test_012_Perform_WAPI_call_with_correct_admin_user_credentials_to_first_login_to_the_grid_and_to_convert_admin_user_password_to_SHA512(self):
                print("\n============================================\n")
                print("Perform WAPI call with correct admin user credentials to first login to the grid and to convert admin user password to SHA512")
                print("============================================")
                command = ('curl -k1 -u admin2:admin2 -H "Content-Type:application/json" -X GET https://'+config.grid_vip+'/wapi/v'+config.wapi_version+'/grid')
                output = os.popen(command).read()
                print(output)
		result = re.search('grid(.*)Infoblox', output)
                result = result.group(0)
                print("==========================")
                print(result)
                print("==========================")
		sleep(10)
                print("Test Case 012 Execution Completed")


        @pytest.mark.run(order=13)
        def test_013_ADMIN_USER_validate_Password_should_be_convert_SHA512_during_first_login_through_WAPI(self):
                print("\n============================================\n")
                print("ADMIN USER validate Password should be convert SHA512 during first login through WAPI")
                print("============================================")
		db =  onedb()
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''grep -A 1 '"name" VALUE="admin2"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
                        result = re.search('SAA(.*)==', output)
                        print(result)
                        if result==None:
                        	assert False
                        else:
                        	result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 104:
                                assert True
                                print("admin password is in SHA512")
                        else:
                                assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 013 Execution Completed")


        @pytest.mark.run(order=14)
        def test_014_All_admin_users_in_the_admin_group_which_are_not_logged_in_to_the_grid_must_be_in_SHA128(self):
                print("\n============================================\n")
                print("All admin users in the admin group which are not logged in to the grid must be in SHA128")
                print("============================================")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        for i in range(3,6):
                                print("===============================")
                                print("Validating admin"+str(i)+" user password")
                                print("===============================")
                                child.sendline('''grep -A 1 '"name" VALUE="admin'''+str(i)+'''"' /tmp/onedb.xml''')
                                child.expect('#')
                                output = child.before
                                result = re.search('HAA(.*)="', output)
                                print(result)
                                if result==None:
                                        assert False
                                else:
                                        result = result.group(0)
                                print(result)
                                bit_length = len(result)
                                if bit_length == 45:
                                        assert True
                                        print("===============================")
                                        print("admin"+str(i)+" user password is in SHA128")
                                        print("===============================")
                                        print("\n")
                                else:
                                        assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 014 Execution Completed")


        @pytest.mark.run(order=15)
        def test_015_INFOBLOX_SUPER_USER_validate_password_should_not_convert_to_SHA512_during_unsuccessful_login_through_ssh(self):
                print("\n============================================\n")
                print("INFOBLOX SUPER USER validate password should not convert to SHA512 during authentication failure through ssh")
                print("============================================")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no infoblox1@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('password:')
                        child.sendline('infoblox123')
                        child.expect('password:')
                        child.sendline('infoblox123')
                        child.expect('password:')
                        db =  onedb()
			sleep(05)
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''grep -A 1 '"name" VALUE="infoblox1"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
                        result = re.search('HAA(.*)="', output)
                        print(result)
                        if result==None:
 	                       assert False
                        else:
                                result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 45:
                                assert True
                                print("===============================")
                                print("infoblox1 user password is in SHA128")
                                print("===============================")
                                print("\n")
                        else:
                                assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 015 Execution Completed")


        @pytest.mark.run(order=16)
        def test_016_Perform_WAPI_call_from_another_super_user_with_wrong_credentials_to_validate_admin_user_SHA512_password(self):
                print("\n============================================\n")
                print("Perform WAPI call from another created super user with wrong credentials to validate admin user SHA512 password")
                print("============================================")
                command = ('curl -k1 -u infoblox1:infoblox321 -H "Content-Type:application/json" -X GET https://'+config.grid_vip+'/wapi/v'+config.wapi_version+'/grid')
                output = os.popen(command).read()
                print(output)
                if "Internal Server Error" in output or "Authorization Required" in output:
                        assert True
                else:
                        assert False
                print("\n")
                print("==========================")
                print("Test Case 016 Execution Completed")

        @pytest.mark.run(order=17)
        def test_017_INFOBLOX_SUPER_USER_validate_password_should_not_convert_to_SHA512_during_unsuccessful_login_through_WAPI(self):
                print("\n============================================\n")
                print("INFOBLOX SUPER USER validate password should not convert to SHA512 during authentication failure through WAPI")
                print("============================================")
                db =  onedb()
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''grep -A 1 '"name" VALUE="infoblox1"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
                        result = re.search('HAA(.*)="', output)
                        print(result)
                        if result==None:
                               assert False
                        else:
                                result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 45:
                                assert True
                                print("===============================")
                                print("infoblox1 user password is in SHA128")
                                print("===============================")
                                print("\n")
                        else:
                                assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 017 Execution Completed")

        @pytest.mark.run(order=18)
        def test_018_INFOBLOX_SUPER_USER_validate_password_should_be_convert_to_SHA512_during_first_login_from_another_created_super_user_through_ssh_login(self):
                print("\n============================================\n")
                print("INFOBLOX SUPER USER validate password should be convert to SHA512 during first login from another created super user through ssh login")
                print("============================================")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no infoblox1@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('password:')
                        child.sendline('infoblox1')
                        child.expect('>')
                        db =  onedb()
			sleep(15)
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''grep -A 1 '"name" VALUE="infoblox1"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
                        result = re.search('SAA(.*)==', output)
                        print(result)
                        if result==None:
                               assert False
                        else:
                               result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 104:
                                assert True
                                print("admin password is in SHA512")
                        else:
                                assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 018 Execution Completed")

        @pytest.mark.run(order=19)
        def test_019_Perform_WAPI_call_from_another_super_user_with_correct_credentials_to_validate_admin_user_SHA512_password(self):
                print("\n============================================\n")
                print("Perform WAPI call from another super user with correct credentials to validate admin user SHA512 password")
                print("============================================")
                command = ('curl -k1 -u infoblox2:infoblox2 -H "Content-Type:application/json" -X GET https://'+config.grid_vip+'/wapi/v'+config.wapi_version+'/grid')
                output = os.popen(command).read()
                print(output)
                result = re.search('grid(.*)Infoblox', output)
		print(result)
                if result==None:
                	assert False
                else:
                        result = result.group(0)
                print(result)
                print("==========================")
                print(result)
                print("==========================")
		sleep(10)
                print("Test Case 019 Execution Completed")


        @pytest.mark.run(order=20)
        def test_020_INFOBLOX_SUPER_USER_validate_password_should_be_convert_to_SHA512_during_first_successful_login_through_WAPI(self):
                print("\n============================================\n")
                print("INFOBLOX SUPER USER validate password should be convert to SHA512 during first successful login through WAPI")
                print("============================================")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
			child.sendline('''/infoblox/one/bin/db_dump -silvd /tmp/''')
                        child.expect('#')
                        sleep(10)
                        child.sendline('''grep -A 1 '"name" VALUE="infoblox2"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
                        result = re.search('SAA(.*)==', output)
                        print(result)
                        if result==None:
                        	assert False
                        else:
                        	result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 104:
                                assert True
                                print("admin password is in SHA512")
                        else:
                                assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 020 Execution Completed")


        @pytest.mark.run(order=21)
        def test_021_ALL_INFOBLOX_SUPER_USERS_in_the_infoblox_group_which_are_not_logged_in_to_the_grid_must_be_in_SHA128(self):
                print("\n============================================\n")
                print("ALL INFOBLOX SUPER USERS in the infoblox group which are not logged in to the grid must be in SHA128")
                print("============================================")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        for i in range(3,6):
                                print("===============================")
                                print("Validating infoblox"+str(i)+" user password")
                                print("===============================")
                                child.sendline('''grep -A 1 '"name" VALUE="infoblox'''+str(i)+'''"' /tmp/onedb.xml''')
                                child.expect('#')
                                output = child.before
                                result = re.search('HAA(.*)="', output)
                                print(result)
                                if result==None:
                                        assert False
                                else:
                                        result = result.group(0)
                                print(result)
                                bit_length = len(result)
                                if bit_length == 45:
                                        assert True
                                        print("===============================")
                                        print("infoblox"+str(i)+" user password is in SHA128")
                                        print("===============================")
                                        print("\n")
                                else:
                                        assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 021 Execution Completed")



        @pytest.mark.run(order=22)
        def test_022_USER_WITH_ONLY_API_ACCESS_validate_password_should_not_convert_to_SHA512_during_unsuccessful_login_through_ssh(self):
                print("\n============================================\n")
                print("USER WITH ONLY API ACCESS validate password should not convert to SHA512 during unsuccessful login through ssh")
                print("============================================")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no infoblox_api1@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('password:')
                        child.sendline('admin123')
                        child.expect('password:')
                        child.sendline('admin123')
                        child.expect('password:')
			child.sendline('admin123')
			sleep(10)
                        db =  onedb()
			sleep(05)
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''grep -A 1 '"name" VALUE="infoblox_api1"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
                        result = re.search('HAA(.*)="', output)
                       	print(result)
                        if result==None:
                               assert False
                        else:
                               result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 45:
                                assert True
                                print("===============================")
                                print("infoblox_api1 user password is in SHA128")
                                print("===============================")
                                print("\n")
                        else:
                                assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 022 Execution Completed")



        @pytest.mark.run(order=23)
        def test_023_USER_WITH_ONLY_API_ACCESS_validate_password_should_not_convert_to_SHA512_during_unsuccessful_login_through_ssh_because_the_user_does_not_have_the_CLI_access(self):
                print("\n============================================\n")
                print("USER WITH ONLY API ACCESS validate password should not convert to SHA512 during unsuccessful login through ssh because the user does not have the CLI access")
                print("============================================")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no infoblox_api1@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('password:')
                        child.sendline('infoblox_api1')
                        child.expect('password:')
                        child.sendline('infoblox_api1')
                        child.expect('password:')
                        db =  onedb()
			sleep(05)
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''grep -A 1 '"name" VALUE="infoblox_api1"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
                        result = re.search('HAA(.*)="', output)
                        print(result)
                        if result==None:
                               assert False
                        else:
                               result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 45:
                                assert True
                                print("===============================")
                                print("infoblox_api1 user password is in SHA128")
                                print("===============================")
                                print("\n")
                        else:
                                assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 023 Execution Completed")

        @pytest.mark.run(order=24)
        def test_024_Perform_WAPI_call_with_wrong_credentials_to_validate_admin_user_SHA512_password(self):
                print("\n============================================\n")
                print("Perform WAPI call with wrong credentials to validate admin user SHA512 password")
                print("============================================")
                command = ('curl -k1 -u infoblox_api1:infoblox123 -H "Content-Type:application/json" -X GET https://'+config.grid_vip+'/wapi/v'+config.wapi_version+'/grid')
                output = os.popen(command).read()
                print(output)
                if "Internal Server Error" in output or "Authorization Required" in output:
                        assert True
                else:
                        assert False
                print("==========================")
                print("Test Case 024 Execution Completed")


        @pytest.mark.run(order=25)
        def test_025_USER_WITH_ONLY_API_ACCESS_validate_password_should_not_convert_to_SHA512_during_unsuccessful_login_through_WAPI(self):
                print("\n============================================\n")
                print("USER WITH ONLY API ACCESS validate password should not convert to SHA512 during unsuccessful login through WAPI")
                print("============================================")
                db =  onedb()
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''grep -A 1 '"name" VALUE="infoblox_api1"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
                        result = re.search('HAA(.*)="', output)
                        print(result)
                        if result==None:
                               assert False
                        else:
                                result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 45:
                                assert True
                                print("===============================")
                                print("infoblox1 user password is in SHA128")
                                print("===============================")
                                print("\n")
                        else:
                                assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 025 Execution Completed")

        @pytest.mark.run(order=26)
        def test_026_USER_WITH_ONLY_API_ACCESS_validate_password_should_be_convert_to_SHA512_during_first_successful_login_through_WAPI(self):
                print("\n============================================\n")
                print("USER WITH ONLY API ACCESS validate password should be convert to SHA512 during first successful login through WAPI")
                print("============================================")
                command = ('curl -k1 -u infoblox_api1:infoblox_api1 -H "Content-Type:application/json" -X GET https://'+config.grid_vip+'/wapi/v'+config.wapi_version+'/grid')
                output = os.popen(command).read()
                print(output)
		result = re.search('grid(.*)Infoblox', output)
               	print(result)
                if result==None:
                	assert False
                else:
                        result = result.group(0)
                print("==========================")
                print(result)
                print("==========================")
		sleep(10)
                print("Test Case 026 Execution Completed")

        @pytest.mark.run(order=27)
        def test_027_USER_WITH_ONLY_API_ACCESS_validate_password_should_be_convert_to_SHA512_during_first_successful_login_through_WAPI(self):
                print("\n============================================\n")
                print("USER WITH ONLY API ACCESS validate password should be convert to SHA512 during first successful login through WAPI")
                print("============================================")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
			sleep(03)
			child.sendline('''/infoblox/one/bin/db_dump -silvd /tmp/''')
                        child.expect('#')	
			sleep(10)
                        child.sendline('''grep -A 1 '"name" VALUE="infoblox_api1"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
                        result = re.search('SAA(.*)==', output)
                        print(result)
                        if result==None:
                        	assert False
                        else:
                                result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 104:
                                assert True
                                print("infoblo_api1 user password is in SHA512")
                        else:
                                assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 027 Execution Completed")

        @pytest.mark.run(order=28)
        def test_028_ALL_INFOBLOX_API_USERS_in_the_infoblox_api_which_are_not_logged_in_to_the_grid_must_be_in_SHA128(self):
                print("\n============================================\n")
                print("ALL INFOBLOX API USERS in the infoblox api which are not logged in to the grid must be in SHA128")
                print("============================================")
		db =  onedb()
                sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        for i in range(2,6):
                                print("===============================")
                                print("Validating infoblox_api"+str(i)+" user password")
                                print("===============================")
                                child.sendline('''grep -A 1 '"name" VALUE="infoblox_api'''+str(i)+'''"' /tmp/onedb.xml''')
                                child.expect('#')
                                output = child.before
                                result = re.search('HAA(.*)="', output)
                                print(result)
                                if result==None:
                                        assert False
                                else:
                                        result = result.group(0)
                                print(result)
                                bit_length = len(result)
                                if bit_length == 45:
                                        assert True
                                        print("===============================")
                                        print("infoblox_api"+str(i)+" user password is in SHA128")
                                        print("===============================")
                                        print("\n")
                                else:
                                        assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 028 Execution Completed")




        @pytest.mark.run(order=29)
        def test_029_USER_WITH_ONLY_CLI_ACCESS_validate_password_should_not_convert_to_SHA512_during_unsuccessful_login_through_ssh(self):
                print("\n============================================\n")
                print("USER WITH ONLY CLI ACCESS validate password should not convert to SHA512 during unsuccessful login through ssh")
                print("============================================")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no infoblox_cli1@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('password:')
                        child.sendline('admin123')
                        child.expect('password:')
                        child.sendline('admin123')
                        child.expect('password:')
                        db =  onedb()
			sleep(05)
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''grep -A 1 '"name" VALUE="infoblox_cli1"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
                        result = re.search('HAA(.*)="', output)
                        print(result)
                        if result==None:
                               assert False
                        else:
                                result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 45:
                                assert True
                                print("===============================")
                                print("infoblox_cli1 user password is in SHA128")
                                print("===============================")
                                print("\n")
                        else:
                                assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 029 Execution Completed")


        @pytest.mark.run(order=30)
        def test_030_USER_WITH_ONLY_CLI_ACCESS_validate_password_bit_length_should_be_converted_SHA512_during_first_successful_login_through_ssh(self):
                print("\n============================================\n")
                print("Generate one db file and validate admin users SHA128 bits")
                print("============================================")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no infoblox_cli1@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('password:')
                        child.sendline('infoblox_cli1')
			child.expect('>')
                        db =  onedb()
			sleep(05)
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''grep -A 1 '"name" VALUE="infoblox_cli1"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
			result = re.search('SAA(.*)==', output)
                        print(result)
                        if result==None:
                               assert False
                        else:
                               result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 104:
                                assert True
                                print("infoblox_cli1 user password is in SHA512")
                        else:
                                assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 030 Execution Completed")


        @pytest.mark.run(order=31)
        def test_031_Perform_WAPI_call_with_wrong_credentials_to_validate_admin_user_SHA512_bit_length(self):
                print("\n============================================\n")
                print("Perform WAPI call with wrong credentials to validate admin user SHA512 password")
                print("============================================")
                command = ('curl -k1 -u infoblox_cli2:infoblox123 -H "Content-Type:application/json" -X GET https://'+config.grid_vip+'/wapi/v'+config.wapi_version+'/grid')
                output = os.popen(command).read()
                print(output)
                if "Internal Server Error" in output or "Authorization Required" in output:
                        assert True
                else:
                        assert False
                print("\n")
                print("==========================")
                print("Test Case 031 Execution Completed")

        @pytest.mark.run(order=32)
        def test_032_USER_WITH_ONLY_CLI_ACCESS_password_should_not_convert_to_SHA512_during_unsuccessful_login_through_WAPI(self):
                print("\n============================================\n")
                print("USER WITH ONLY CLI ACCESS password should not convert to SHA512 during unsuccessful login through WAPI")
                print("============================================")
                db =  onedb()
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''grep -A 1 '"name" VALUE="infoblox_cli2"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
                        result = re.search('HAA(.*)="', output)
                        print(result)
                        if result==None:
                               assert False
                        else:
                                result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 45:
                                assert True
                                print("===============================")
                                print("infoblox_cli2 user password is in SHA128")
                                print("===============================")
                                print("\n")
                        else:
                                assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 032 Execution Completed")

        @pytest.mark.run(order=33)
        def test_033_Perform_WAPI_call_with_wrong_credentials_to_validate_admin_user_SHA512_bit_length(self):
                print("\n============================================\n")
                print("Generate one db file and validate admin users SHA128 bits")
                print("============================================")
                command = ('curl -k1 -u infoblox_cli2:infoblox_cli2 -H "Content-Type:application/json" -X GET https://'+config.grid_vip+'/wapi/v'+config.wapi_version+'/grid')
                output = os.popen(command).read()
                print(output)
                if "Internal Server Error" in output or "Authorization Required" in output:
                        assert True
                else:
                        assert False
                print("\n")
                print("==========================")
                print("Test Case 033 Execution Completed")

        @pytest.mark.run(order=34)
        def test_034_USER_WITH_ONLY_CLI_ACCESS_password_should_convert_to_SHA512_because_the_USER_first_will_login_to_the_grid_for_WAPI_call_even_INFOBLOX_CLI2_does_not_have_the_API_access(self):
                print("\n============================================\n")
                print("USER WITH ONLY CLI ACCESS password should convert to SHA512 because the USER first will login to the grid for WAPI call even INFOBLOX CLI2 does not have the API access")
                print("============================================")
                db =  onedb()
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''grep -A 1 '"name" VALUE="infoblox_cli2"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
			result = re.search('SAA(.*)==', output)
                        print(result)
                        if result==None:
                               assert False
                        else:
                               result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 104:
                                assert True
                                print("admin password is in SHA512")
                        else:
                                assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 034 Execution Completed")

        @pytest.mark.run(order=35)
        def test_035_ALL_INFOBLOX_CLI_USERS_in_the_infoblox_cli_which_are_not_logged_in_to_the_grid_must_be_in_SHA128(self):
                print("\n============================================\n")
                print("ALL INFOBLOX CLI USERS in the infoblox cli which are not logged in to the grid must be in SHA128")
                print("============================================")
		db =  onedb()
                sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        for i in range(3,6):
                                print("===============================")
                                print("Validating infoblox_cli"+str(i)+" user password")
                                print("===============================")
                                child.sendline('''grep -A 1 '"name" VALUE="infoblox_cli'''+str(i)+'''"' /tmp/onedb.xml''')
                                child.expect('#')
                                output = child.before
                                result = re.search('HAA(.*)="', output)
				print(result)
                                if result==None:
                                        assert False
                                else:
                                        result = result.group(0)
                                print(result)                                
                                bit_length = len(result)
                                if bit_length == 45:
                                        assert True
                                        print("===============================")
                                        print("infoblox_cli"+str(i)+" user password is in SHA128")
                                        print("===============================")
                                        print("\n")
                                else:
                                        assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 035 Execution Completed")



##################
## nonsuperuser ##
##################

        @pytest.mark.run(order=36)
        def test_036_NON_SUPER_USER_validate_password_should_not_convert_to_SHA512_during_unsuccessful_login_through_ssh(self):
                print("\n============================================\n")
                print("NON SUPER USER validate password should not convert to SHA512 during unsuccessful login through ssh")
                print("============================================")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no nonsuperuser1@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('password:')
                        child.sendline('infoblox123')
                        child.expect('password:')
                        child.sendline('infoblox123')
                        child.expect('password:')
                        db =  onedb()
			sleep(05)
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''grep -A 1 '"name" VALUE="nonsuperuser1"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
                        result = re.search('HAA(.*)="', output)
                        print(result)
                        if result==None:
                               assert False
                        else:
                               result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 45:
                                assert True
                                print("===============================")
                                print("nonsuperuser1 user password is in SHA128")
                                print("===============================")
                                print("\n")
                        else:
                                assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 036 Execution Completed")

        @pytest.mark.run(order=37)
        def test_037_Perform_WAPI_call_with_wrong_credentials_to_validate_admin_user_SHA512_password(self):
                print("\n============================================\n")
                print("Perform WAPI call with wrong credentials to validate admin user SHA512 password")
                print("============================================")
                command = ('curl -k1 -u nonsuperuser1:admin321 -H "Content-Type:application/json" -X GET https://'+config.grid_vip+'/wapi/v'+config.wapi_version+'/grid')
                output = os.popen(command).read()
                print(output)
                if "Internal Server Error" in output or "Authorization Required" in output:
                        assert True
                else:
                        assert False
                print("\n")
                print("==========================")
                print("Test Case 037 Execution Completed")


        @pytest.mark.run(order=38)
        def test_038_NON_SUPER_USER_password_should_not_convert_to_SHA512_during_unsuccessful_login_through_ssh(self):
                print("\n============================================\n")
                print("NON SUPER USER password should not convert to SHA512 during unsuccessful login through ssh")
                print("============================================")
                db =  onedb()
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''grep -A 1 '"name" VALUE="nonsuperuser1"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
                        result = re.search('HAA(.*)="', output)
                        print(result)
                        if result==None:
                               assert False
                        else:
                               result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 45:
                                assert True
                                print("===============================")
                                print("nonsuperuser1 user password is in SHA128")
                                print("===============================")
                                print("\n")
                        else:
                                assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 038 Execution Completed")


        @pytest.mark.run(order=39)
        def test_039_NON_SUPER_USER_validate_password_should_be_converted_SHA512_during_first_successful_login_through_ssh(self):
                print("\n============================================\n")
                print("NON SUPER USER validate password should be converted SHA512 during first successful login through ssh")
                print("============================================")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no nonsuperuser1@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('password:')
                        child.sendline('nonsuperuser1')
                        child.expect('>')
                        db =  onedb()
			sleep(05)
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''grep -A 1 '"name" VALUE="nonsuperuser1"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
			result = re.search('SAA(.*)==', output)
                        print(result)
                        if result==None:
                               assert False
                        else:
                               result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 104:
                                assert True
                                print("admin password is in SHA512")
                        else:
                                assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 039 Execution Completed")

        @pytest.mark.run(order=40)
        def test_040_Perform_WAPI_call_with_correct_credentials_to_validate_nonsuperuser2n_user_SHA512_password(self):
                print("\n============================================\n")
                print("Perform WAPI call with correct credentials to validate nonsuperuser2n user SHA512 password")
                print("============================================")
                command = ('curl -k1 -u nonsuperuser2:nonsuperuser2 -H "Content-Type:application/json" -X GET https://'+config.grid_vip+'/wapi/v'+config.wapi_version+'/grid')
                output = os.popen(command).read()
                print(output)
		result = re.search('grid(.*)Infoblox', output)
                print(result)
                if result==None:
                	assert False
                else:
                        result = result.group(0)
                print("==========================")
                print(result)
                print("==========================")
		sleep(10)
                print("Test Case 040 Execution Completed")

        @pytest.mark.run(order=41)
        def test_041_NON_SUPER_USER_validate_password_should_be_convert_to_SHA512_during_first_successful_login_through_WAPI(self):
                print("\n============================================\n")
                print("NON SUPER USER validate password should be convert to SHA512 during first successful login through WAPI")
                print("============================================")
                db =  onedb()
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''grep -A 1 '"name" VALUE="nonsuperuser2"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
			result = re.search('SAA(.*)==', output)
                        print(result)
                        if result==None:
                               assert False
                        else:
                               result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 104:
                                assert True
				print("==========================")
                                print("nonsuperuser2 password is in SHA512")
				print("==========================")
                        else:
                                assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 041 Execution Completed")



########################
### SAML group users ###
########################

        @pytest.mark.run(order=42)
        def test_042_SAML_USERS_validate_password_should_not_convert_to_SHA512_during_unsuccessful_login_through_ssh(self):
                print("\n============================================\n")
                print("SAML USERS validate password should not convert to SHA512 during unsuccessful login through ssh")
                print("============================================")
		get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup?name=saml-group", grid_vip=config.grid_vip)
                print(get_ref)
                ref = json.loads(get_ref)[0]['_ref']
		data = {"access_method": ["GUI","API","CLI"]}
		response1 = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data), grid_vip=config.grid_vip)	
		print(response1)
		sleep(20)
		response2 = ib_NIOS.wapi_request('GET',"admingroup?name=saml-group&_return_fields=access_method&_return_as_object=1")
		print(response2)
		data1 = ["GUI","API","CLI"]
		for i in data1:
			if i in response2:
				assert True
			else:
				assert False
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no saml1@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('password:')
                        child.sendline('infoblox123')
                        child.expect('password:')
                        child.sendline('infoblox123')
                        child.expect('password:')
                        db =  onedb()
			sleep(05)
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
			child.sendline('''/infoblox/one/bin/db_dump -silvd /tmp/''')
			child.expect('#')
			sleep(05)
                        child.sendline('''grep -A 1 '"name" VALUE="saml1"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
                        result = re.search('HAA(.*)="', output)
                        print(result)
                        if result==None:
                               assert False
                        else:
                               result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 45:
                                assert True
                                print("===============================")
                                print("saml1 user password is in SHA128")
                                print("===============================")
                                print("\n")
                        else:
                                assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 042 Execution Completed")

        @pytest.mark.run(order=43)
        def test_043_SAML_Group_USER_password_should_not_convert_to_SHA512_during_unsuccessful_login_through_WAPI(self):
                print("\n============================================\n")
                print("SAML Group USER password should not convert to SHA512 during unsuccessful login through WAPI")
                print("============================================")
                command = ('curl -k1 -u saml1:admin321 -H "Content-Type:application/json" -X GET https://'+config.grid_vip+'/wapi/v'+config.wapi_version+'/grid')
                output = os.popen(command).read()
                print(output)
                if "Internal Server Error" in output or "Authorization Required" in output:
                        assert True
                else:
                        assert False
                print("\n")
                print("==========================")
                print("Test Case 043 Execution Completed")


        @pytest.mark.run(order=44)
        def test_044_SAML_GROUP_USER_validate_password_should_not_convert_to_SHA512_during_first_unsuccessful_login_through_WAPI(self):
                print("\n============================================\n")
                print("SAML GROUP USER validate password should not convert to SHA512 during first unsuccessful login through WAPI")
                print("============================================")
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
			child.sendline('''/infoblox/one/bin/db_dump -silvd /tmp/''')
			child.expect('#')
                        child.sendline('''grep -A 1 '"name" VALUE="saml1"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
                        result = re.search('HAA(.*)="', output)
                        print(result)
                        if result==None:
                               assert False
                        else:
                               result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 45:
                                assert True
                                print("===============================")
                                print("saml1 user password is in SHA128")
                                print("===============================")
                                print("\n")
                        else:
                                assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 044 Execution Completed")


        @pytest.mark.run(order=45)
        def test_045_SAML_GROUP_USER_validate_password_should_be_convert_to_SHA512_during_first_successful_login_through_SSH(self):
                print("\n============================================\n")
                print("SAML GROUP USER validate password should be convert to SHA512 during first successful login through SSH")
                print("============================================")
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no saml1@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('password:')
                        child.sendline('saml1')
                        child.expect('>')
			sleep(10)
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
			child.sendline('''/infoblox/one/bin/db_dump -silvd /tmp/''')
			child.expect('#')
			sleep(05)
                        child.sendline('''grep -A 1 '"name" VALUE="saml1"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
                        result = re.search('SAA(.*)==', output)
                        print(result)
                        if result==None:
                               assert False
                        else:
                               result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 104:
                                assert True
                                print("saml1 password is in SHA512")
                        else:
                                assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 045 Execution Completed")

        @pytest.mark.run(order=46)
        def test_046_Perform_WAPI_call_with_correct_credentials_to_validate_SAML_Group_USER_SHA512_password(self):
                print("\n============================================\n")
                print("Perform WAPI call with correct credentials to validate SAML Group USER SHA512 password")
                print("============================================")
                command = ('curl -k1 -u saml2:saml2 -H "Content-Type:application/json" -X GET https://'+config.grid_vip+'/wapi/v'+config.wapi_version+'/grid')
                output = os.popen(command).read()
                print(output)
                result = re.search('grid(.*)Infoblox', output)
                print(result)
		if result==None:
	                assert False
                else:
        	        result = result.group(0)
                print("==========================")
                print(result)
                print("==========================")
		sleep(10)
                print("Test Case 046 Execution Completed")


        @pytest.mark.run(order=47)
        def test_047_SAML_GROUP_USER_validate_password_should_be_convert_to_SHA512_during_first_successful_login_through_WAPI(self):
                print("\n============================================\n")
                print("SAML GROUP USER validate password should be convert to SHA512 during first successful login through WAPI")
                print("============================================")
		sleep(15)
                db =  onedb()
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''grep -A 1 '"name" VALUE="saml2"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
                        result = re.search('SAA(.*)==', output)
			print(result)
                        if result==None:
                               assert False
                        else:
                               result = result.group(0)
                        print(result)                        
                        bit_length = len(result)
                        if bit_length == 104:
                                assert True
                                print("==========================")
                                print("saml2 password is in SHA512")
                                print("==========================")
                        else:
                                assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 047 Execution Completed")




####################################
## Cloud User should be in SHA512 ## 
####################################

        @pytest.mark.run(order=48)
        def test_048_SYSTEM_CLOUD_password_should_be_in_SHA512_without_any_first_successful_login(self):
                print("\n============================================\n")
                print("SYSTEM CLOUD password should be in SHA512 without any first successful login")
                print("============================================")
		sleep(15)
                db =  onedb()
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''grep -A 2 '"name" VALUE="$SYSTEM-CLOUD$"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
                        result = re.search('SAA(.*)==', output)
                        print(result)
                        if result==None:
                               assert False
                        else:
                               result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 104:
                                assert True
                                print("==========================")
                                print("SYSTEM-CLOUD password is in SHA512")
                                print("==========================")
                        else:
                                assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 048 Execution Completed")



######################
## Reporting User ####
######################

        @pytest.mark.run(order=49)
        def test_049_Generate_one_db_file_and_validate_without_first_login_reporting_user_password_should_be_in_SHA128(self):
                print("\n============================================\n")
                print("Generate one db file and validate without first login reporting user password should be in SHA128")
                print("\n============================================\n")
                sleep(10)
                db =  onedb()
		sleep(05)
                try:
                        print("\n###################################################")
                        print("Validate reporting user password should be in SHA128 ")
                        print("####################################################\n")
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''grep -C 2 '"name" VALUE="$SPLUNK-REPORTING-ADMIN$"' /tmp/onedb.xml''')
                        child.expect('#')
                        output = child.before
                        result = re.search('HAA(.*)="', output)
                        print(result)
                        if result==None:
                               assert False
                        else:
                               result = result.group(0)
                        print(result)
                        bit_length = len(result)
                        if bit_length == 45:
                                assert True
                                print("Reporting User password is in SHA128")
                        else:
                                assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 049 Execution Completed")



##################################
## Creating Users Post Upgrade ##
##################################



        @pytest.mark.run(order=50)
        def test_050_Create_Admin_Users(self):
		print("===================================")
		print("Creating Admin Users in admin group")
		print("===================================")
                print("\n")
                for i in range(6,8):
                        print("===================================")
                        print("Creating admin"+str(i)+" user in admin group")
                        print("===================================")
                        data = {"admin_groups": ["admin-group"],"name": "admin"+str(i),"password":"admin"+str(i)}
                        response = ib_NIOS.wapi_request('POST', object_type="adminuser", fields=json.dumps(data))
                        print(response)
			sleep(02)
                        print("\n")
                print("Test Case 050 Execution Completed")

        @pytest.mark.run(order=51)
        def test_051_Validate_created_Admin_Users_in_Admin_Group(self):
		print("===================================")
		print("Validating created Admin Users in Admin Group")
		print("===================================")
                print("\n")
		sleep(10)
                for i in range(6,8):
                        print("=============================================")
                        print("Validating created admin"+str(i)+" user in admin group")
                        print("=============================================")
                        response = ib_NIOS.wapi_request('GET','adminuser?name=admin'+str(i),grid_vip=config.grid_vip)
                        print(response)
                        response = response.replace("\n","").replace(" ","")
                        data = '''"admin_groups":["admin-group"],"name":"admin'''+str(i)+'''"'''
                        if data in response:
                                assert True
                        else:
                                assert False
                        print("\n")
                        print(data)
                        print("\n")
                print("Test Case 051 Execution Completed")


        @pytest.mark.run(order=52)
        def test_052_Generate_one_db_file_and_validate_post_upgrade_created_users_password_should_be_in_SHA512(self):
                print("\n============================================\n")
                print("Generate one db file and validate post upgrade created users password should be in SHA512")
                print("============================================")
		sleep(15)
                db =  onedb()
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        for i in range(6,8):
                                print("===============================")
                                print("Validating admin"+str(i)+" user password")
                                print("===============================")
                                child.sendline('''grep -A 1 '"name" VALUE="admin'''+str(i)+'''"' /tmp/onedb.xml''')
                                child.expect('#')
                                output = child.before
				result = re.search('SAA(.*)==', output)
	                        print(result)
                                if result==None:
                                        assert False
                                else:
                                        result = result.group(0)
                                print(result)
        	                bit_length = len(result)
                		if bit_length == 104:
                                	assert True
                                        print("===================================")
                                        print("admin users passwords are in SHA512")
                                        print("===================================")
                                        print("\n")
                                else:
                                        assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 052 Execution Completed")


        @pytest.mark.run(order=53)
        def test_053_Create_test_Super_User_group(self):
                print("\n============================================\n")
                print("Creating test Super USer Group")
                print("\n============================================\n")
                data = {"name": "test","superuser": True}
                response = ib_NIOS.wapi_request('POST', object_type="admingroup", fields=json.dumps(data))
                print(response)
                print("\n")
		sleep(05)
                print("Test Case 053 Execution Completed")

        @pytest.mark.run(order=54)
        def test_054_Validate_created_test_Super_User_group(self):
                print("\n============================================\n")
                print("Validating created test Super User Group")
                print("\n============================================\n")
                response = ib_NIOS.wapi_request('GET',"admingroup?name=test&_return_fields=superuser,name",grid_vip=config.grid_vip)
                print(response)
                data = ['"name": "test"','"superuser": true']
                for i in data:
                        if i in response:
                                assert True
                        else:
                                assert False
                print("\n")
                print(data)
                print("\n")
                print("Test Case 054 Execution Completed")


        @pytest.mark.run(order=55)
        def test_055_Create_Users_in_created_test_Super_User_group(self):
                print("\n============================================\n")
                print("Creating users in created test Super User group")
                print("\n============================================\n")
                for i in range(1,6):
                        print("===============================")
                        print("Creating test"+str(i)+" user in created super user group")
                        print("===============================")
                        data = {"admin_groups": ["test"],"name": "test"+str(i),"password":"test"+str(i)}
                        response = ib_NIOS.wapi_request('POST', object_type="adminuser", fields=json.dumps(data))
                        print(response)
                        print("\n")
                print("Test Case 055 Execution Completed")

        @pytest.mark.run(order=56)
        def test_056_Validate_created_users_in_test_Super_User_group(self):
		print("\n============================================\n")
		print("Validate created users in test Super User group")
		print("\n============================================\n")
		sleep(10)
                for i in range(1,6):
                        print("=============================================")
                        print("Validating created test"+str(i)+" user in infoblox group")
                        print("=============================================")
                        response = ib_NIOS.wapi_request('GET','adminuser?name=test'+str(i),grid_vip=config.grid_vip)
                        print(response)
                        response = response.replace("\n","").replace(" ","")
                        data = '''"admin_groups":["test"],"name":"test'''+str(i)+'''"'''
                        if data in response:
                                assert True
                        else:
                                assert False
                        print("\n")
                        print(data)
                        print("\n")
                print("Test Case 056 Execution Completed")

        @pytest.mark.run(order=57)
        def test_057_Generate_one_db_file_and_validate_post_upgrade_created_users_password_should_be_in_SHA512(self):
                print("\n============================================\n")
                print("Generate one db file and validate post upgrade created users password should be in SHA512")
                print("============================================")
		sleep(15)
                db =  onedb()
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        for i in range(1,6):
                                print("===============================")
                                print("Validating infoblox"+str(i)+" user password")
                                print("===============================")
                                child.sendline('''grep -A 1 '"name" VALUE="test'''+str(i)+'''"' /tmp/onedb.xml''')
                                child.expect('#')
                                output = child.before
				result = re.search('SAA(.*)==', output)
	                        print(result)
                                if result==None:
                                        assert False
                                else:
                                        result = result.group(0)
                                print(result)
        	                bit_length = len(result)
                	        if bit_length == 104:
                        	        assert True
                                        print("===============================")
                                        print("test"+str(i)+" user password is in SHA512")
                                        print("===============================")
                                        print("\n")
                                else:
                                        assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 057 Execution Completed")


############################
## create non super users ##
############################


        @pytest.mark.run(order=58)
        def test_058_Create_non_super_user_group_with_all_access_methods(self):
                print("\n============================================\n")
                print("Creating non super user group with all access methods")
                print("\n============================================\n")
                data = {"access_method": ["GUI","API","CLI"],"name": "coreddi"}
                response = ib_NIOS.wapi_request('POST', object_type="admingroup", fields=json.dumps(data))
                print(response)
                print("\n")
                print("Test Case 058 Execution Completed")

        @pytest.mark.run(order=59)
        def test_059_Validate_created_coreddi_group_and_access_methods(self):
                print("\n============================================\n")
                print("Validate created coreddi group and access methods")
                print("\n============================================\n")
		sleep(10)
                response = ib_NIOS.wapi_request('GET',"admingroup?name=coreddi&_return_fields=access_method,name",grid_vip=config.grid_vip)
                print(response)
                response = response.replace("\n","").replace(" ","")
                print(response)
                data = '''"access_method":["GUI","API","CLI"],"name":"coreddi"'''
                if data in response:
                        assert True
                else:
                        assert False
                print("\n")
                print(data)
                print("\n")
                print("Test Case 059 Execution Completed")

        @pytest.mark.run(order=60)
        def test_060_Creat_Users_in_coreddi_group(self):
                print("\n============================================\n")
                print("Creating Users in coreddi group")
                print("\n============================================\n")
                for i in range(1,6):
                        print("===============================")
                        print("Creating coreddi"+str(i)+" user in created coreddi group")
                        print("===============================")
                        data = {"admin_groups": ["coreddi"],"name": "coreddi"+str(i),"password":"coreddi"+str(i)}
                        response = ib_NIOS.wapi_request('POST', object_type="adminuser", fields=json.dumps(data))
                        print(response)
                        print("\n")
                print("Test Case 060 Execution Completed")

        @pytest.mark.run(order=61)
        def test_061_Validate_created_users_in_coreddi_group(self):
		print("\n============================================\n")
		print("Validating created users in coreddi group")
		print("\n============================================\n")
                print("\n")
		sleep(10)
                for i in range(1,6):
                        print("=============================================")
                        print("Validating created coreddi"+str(i)+" user in coreddi group")
                        print("=============================================")
                        response = ib_NIOS.wapi_request('GET','adminuser?name=coreddi'+str(i),grid_vip=config.grid_vip)
                        print(response)
                        response = response.replace("\n","").replace(" ","")
                        data = '''"admin_groups":["coreddi"],"name":"coreddi'''+str(i)+'''"'''
                        if data in response:
                                assert True
                        else:
                                assert False
                        print("\n")
                        print(data)
                        print("\n")
                print("Test Case 061 Execution Completed")

        @pytest.mark.run(order=62)
        def test_062_Generate_one_db_file_and_validate_coreddi_users_password_shoulds_be_in_SHA512(self):
                print("\n============================================\n")
                print("Generate one db file and validate coreddi users password shoulds be in SHA512")
                print("============================================")
		sleep(10)
                db =  onedb()
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        for i in range(1,6):
                                print("===============================")
                                print("Validating coreddi"+str(i)+" user password")
                                print("===============================")
                                child.sendline('''grep -A 1 '"name" VALUE="coreddi'''+str(i)+'''"' /tmp/onedb.xml''')
                                child.expect('#')
				output = child.before
				result = re.search('SAA(.*)==', output)
	                        print(result)
                                if result==None:
                                        assert False
                                else:
                                        result = result.group(0)
                                print(result)
        	                bit_length = len(result)
                	        if bit_length == 104:
                        	        assert True
					print("===============================")
                                        print("coreddi"+str(i)+" user password is in SHA512")
                                        print("===============================")
                                        print("\n")
                                else:
                                        assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 062 Execution Completed")



        @pytest.mark.run(order=63)
        def test_063_Create_Users_in_SAML_group(self):
                print("\n============================================\n")
                print("Creating users in SAML group")
                print("\n============================================\n")
                for i in range(6,9):
                        print("===============================")
                        print("Creating SAML"+str(i)+" user in created super user group")
                        print("===============================")
                        data = {"admin_groups": ["saml-group"],"name": "saml"+str(i),"password":"saml"+str(i)}
                        response = ib_NIOS.wapi_request('POST', object_type="adminuser", fields=json.dumps(data))
                        print(response)
                        print("\n")
                print("Test Case 063 Execution Completed")

        @pytest.mark.run(order=64)
        def test_064_Validate_created_users_in_SAML_group(self):
		print("=============================================")
		print("Validate created all SAML group users in SAML group")
		print("=============================================")
                print("\n")
		sleep(10)
                for i in range(6,9):
                        print("=============================================")
                        print("Validating created SAML"+str(i)+" user in SAML group")
                        print("=============================================")
                        response = ib_NIOS.wapi_request('GET','adminuser?name=saml'+str(i),grid_vip=config.grid_vip)
                        print(response)
                        response = response.replace("\n","").replace(" ","")
                        data = '''"admin_groups":["saml-group"],"name":"saml'''+str(i)+'''"'''
                        if data in response:
                                assert True
                        else:
                                assert False
                        print("\n")
                        print(data)
                        print("\n")
                print("Test Case 064 Execution Completed")

        @pytest.mark.run(order=65)
        def test_065_Generate_one_db_file_and_validate_SAML_Group_USERS_passwords_should_be_in_SHA512(self):
                print("\n============================================\n")
                print("Generate one db file and validate SAML Group USERS passwords should be in SHA512")
                print("============================================")
                db =  onedb()
		sleep(05)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        for i in range(6,9):
                                print("===============================")
                                print("Validating saml"+str(i)+" user password")
                                print("===============================")
                                child.sendline('''grep -A 1 '"name" VALUE="saml'''+str(i)+'''"' /tmp/onedb.xml''')
                                child.expect('#')
                                output = child.before
				result = re.search('SAA(.*)==', output)
	                        print(result)
                                if result==None:
                                        assert False
                                else:
                                        result = result.group(0)
                                print(result)
        	                bit_length = len(result)
                	        if bit_length == 104:
                        	        assert True
                                        print("===============================")
                                        print("saml"+str(i)+" user password is in SHA128")
                                        print("===============================")
                                        print("\n")
                                else:
                                        assert False
                except Exception as error_message:
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 065 Execution Completed")

        @pytest.mark.run(order=66)
        def test_066_Validate_password_boundaries_error_message_through_WAPI(self):
                print("\n============================================\n")
                print("Validate Password boundaries error message through WAPI")
                print("\n============================================\n")
		sleep(05)
                data = {"admin_groups": ["admin-group"],"name": "admin11","password":"1"}
                status,response = ib_NIOS.wapi_request('POST', object_type="adminuser", fields=json.dumps(data))
                print(status,response)
		data = 'It must contain 4-64 characters'
		if data in response:
			assert True
		else:
			assert False
		print(data)
                print("\n")
                print("Test Case 066 Execution Completed")



















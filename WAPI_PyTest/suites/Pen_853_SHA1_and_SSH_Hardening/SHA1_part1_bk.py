#!/usr/bin/env python

__author__ = "Prasad K"
__email__  = "pkondisetty@infoblox.com"
__RFE__    =  "PenTest 853 SHA1"
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
                child.sendline('/infoblox/one/bin/db_dump -silvd /tmp/')
                sleep(10)
                child.expect('#')
        except Exception as error_message:
                print("Failed to genarated onedb.xml file ")
                assert False
        finally:
                child.close()


class PenTest_853_SHA1(unittest.TestCase):


        @pytest.mark.run(order=001)
        def test_001_Generate_one_db_file_and_validate_admin_user_SHA128_bit_length(self):
                print("\n============================================\n")
                print("Generate one db file and validate admin user SHA128 bit length")
                print("============================================")
                db =  onedb()
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        child.sendline('''grep -A 1 '"name" VALUE="admin"' /tmp/onedb.xml''')
                        child.expect('#')
			print("\n")
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
                                print("admin password hashed in SHA128")
                        else:
                                assert False
                except Exception as error_message:
                        print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 001 Execution Completed")


        @pytest.mark.run(order=002)
        def test_002_Create_Admin_Users_in_Admin_Group(self):
                print("\n============================================\n")
                print("Create Admin Users in Admin Group")
                print("============================================")
		for i in range(1,6):
			print("===================================")
			print("Creating admin"+str(i)+" user in admin group")
			print("===================================")
			data = {"admin_groups": ["admin-group"],"name": "admin"+str(i),"password":"admin"+str(i)}
			response = ib_NIOS.wapi_request('POST', object_type="adminuser", fields=json.dumps(data))
			print(response)
			print("\n")
		sleep(10)
                print("Test Case 002 Execution Completed")

        @pytest.mark.run(order=003)
        def test_003_Validate_created_Admin_User(self):
                print("\n============================================\n")
                print(" Validate created Admin Users in Admin Group")
                print("============================================")
		for i in range(1,6):
			print("=============================================")
			print("Validating created admin"+str(i)+" user in admin group")	
			print("=============================================")
			response = ib_NIOS.wapi_request('GET','adminuser?name=admin'+str(i),grid_vip=config.grid_vip)
			print(response)
			sleep(05)
			response = response.replace("\n","").replace(" ","")
			data = '''"admin_groups":["admin-group"],"name":"admin'''+str(i)+'''"'''
			if data in response:
				assert True
			else:
				assert False
			print("\n")
			print(data)
			print("\n")
                print("Test Case 003 Execution Completed")

        @pytest.mark.run(order=004)
        def test_004_Generate_one_db_file_and_validate_created_admin_users_SHA128_bit_length(self):
                print("\n============================================\n")
                print(" Generate one db file and validate created admin users SHA128 bit length ")
                print("============================================")
                db =  onedb()
		sleep(10)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
			for i in range(1,6):
				print("===============================")
				print("Validating admin"+str(i)+" user key length")
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
                                	print("admin password key is in SHA128")
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


        @pytest.mark.run(order=005)
        def test_005_Create_Super_User_group(self):
                print("\n============================================\n")
                print("Creating Super User group")
                print("\n============================================\n")
                data = {"name": "infoblox","superuser": True}
                response = ib_NIOS.wapi_request('POST', object_type="admingroup", fields=json.dumps(data))
                print(response)
                print("\n")
		sleep(10)
                print("Test Case 005 Execution Completed")

        @pytest.mark.run(order=006)
        def test_006_Validate_created_Super_User_group(self):
                print("\n============================================\n")
                print("Validating created super user group")
                print("\n============================================\n")
                response = ib_NIOS.wapi_request('GET',"admingroup?name=infoblox&_return_fields=superuser,name",grid_vip=config.grid_vip)
                print(response)
                data = ['"name": "infoblox"','"superuser": true']
		for i in data:
	                if i in response:
        	                assert True
                	else:
                        	assert False
                print("\n")
                print(data)
                print("\n")
                print("Test Case 006 Execution Completed")

        @pytest.mark.run(order=007)
        def test_007_Creating_Users_in_created_Super_User_group(self):
                print("\n============================================\n")
                print("Creating users in created Super User group")
                print("\n============================================\n")
		for i in range(1,6):
			print("===============================")
			print("Creating infoblox"+str(i)+" users in created super user infoblox group")			
			print("===============================")
	                data = {"admin_groups": ["infoblox"],"name": "infoblox"+str(i),"password":"infoblox"+str(i)}
        	        response = ib_NIOS.wapi_request('POST', object_type="adminuser", fields=json.dumps(data))
                	print(response)
	                print("\n")
		sleep(10)
                print("Test Case 007 Execution Completed")

        @pytest.mark.run(order=108)
        def test_008_Validate_created_users_in_created_Super_User_group(self):
                print("\n============================================\n")
                print(" Validating created users in created Super User group")
                print("\n============================================\n")
                for i in range(1,6):
                        print("=============================================")
                        print("Validating created infoblox"+str(i)+" user in infoblox group")
                        print("=============================================")
                        response = ib_NIOS.wapi_request('GET','adminuser?name=infoblox'+str(i),grid_vip=config.grid_vip)
                        print(response)
			sleep(05)
                        response = response.replace("\n","").replace(" ","")
                        data = '''"admin_groups":["infoblox"],"name":"infoblox'''+str(i)+'''"'''
                        if data in response:
                                assert True
                        else:
                                assert False
                        print("\n")
                        print(data)
                        print("\n")
                print("Test Case 008 Execution Completed")

        @pytest.mark.run(order=109)
        def test_009_Generate_one_db_file_and_validate_infoblox_superusers_SHA128_bit_length(self):
                print("\n============================================\n")
                print(" Generate one db file and validate infoblox superusers SHA128 bit length ")
                print("============================================")
                db =  onedb()
		sleep(10)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        for i in range(1,6):
                                print("===============================")
                                print("Validating infoblox"+str(i)+" user key length")
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
                                        print("infoblox"+str(i)+" user password key is in SHA128")
                                        print("===============================")
					print("\n")
                                else:
                                        assert False
                except Exception as error_message:
                        print("Failed to get the infoblox"+str(i)+" SHA128 password length from onedb.xml")
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 009 Execution Completed")


        @pytest.mark.run(order=010)
        def test_010_Create_non_super_user_group_with_only_api_access(self):
                print("\n============================================\n")
                print(" Creating non super user group with only api access ")
                print("\n============================================\n")
                data = {"access_method": ["API"],"name": "infoblox_api"}
                response = ib_NIOS.wapi_request('POST', object_type="admingroup", fields=json.dumps(data))
                print(response)
                print("\n")
		sleep(10)
                print("Test Case 010 Execution Completed")

        @pytest.mark.run(order=011)
        def test_011_Validate_created_non_super_user_group(self):
                print("\n============================================\n")
                print("Validating created non super user group")
                print("\n============================================\n")
                response = ib_NIOS.wapi_request('GET',"admingroup?name=infoblox_api&_return_fields=name,access_method",grid_vip=config.grid_vip)
                print(response)
		response = response.replace("\n","").replace(" ","")		
                data = '''"access_method":["API"],"name":"infoblox_api"'''
                if data in response:
                        assert True
                else:
                        assert False
                print("\n")
                print(data)
                print("\n")
                print("Test Case 011 Execution Completed")


        @pytest.mark.run(order=012)
        def test_012_Create_Users_in_created_non_super_User_group(self):
                print("\n============================================\n")
                print("Creating users in created non super User group")
                print("\n============================================\n")
                for i in range(1,6):
                        print("===============================")
                        print("Creating infoblox_api"+str(i)+" user in created super user group")
                        print("===============================")
                        data = {"admin_groups": ["infoblox_api"],"name": "infoblox_api"+str(i),"password":"infoblox_api"+str(i)}
                        response = ib_NIOS.wapi_request('POST', object_type="adminuser", fields=json.dumps(data))
                        print(response)
                        print("\n")
		sleep(10)
                print("Test Case 012 Execution Completed")

        @pytest.mark.run(order=013)
        def test_013_Validate_created_users_in_non_super_User_group(self):
                print("\n============================================\n")
                print("Validating created users in non super User group")
                print("\n============================================\n")
                for i in range(1,6):
                        print("=============================================")
                        print("Validating created infoblox_api"+str(i)+" user in infoblox_api group")
                        print("=============================================")
                        response = ib_NIOS.wapi_request('GET','adminuser?name=infoblox_api'+str(i),grid_vip=config.grid_vip)
                        print(response)
			sleep(05)
                        response = response.replace("\n","").replace(" ","")
                        data = '''"admin_groups":["infoblox_api"],"name":"infoblox_api'''+str(i)+'''"'''
                        if data in response:
                                assert True
                        else:
                                assert False
                        print("\n")
                        print(data)
                        print("\n")
                print("Test Case 013 Execution Completed")


        @pytest.mark.run(order=014)
        def test_014_Generate_one_db_file_and_validate_created_non_superuser_SHA128_bit_length(self):
                print("\n============================================\n")
                print("Generating one db file and validate created non superuser SHA128 bit length")
                print("============================================")
                db =  onedb()
		sleep(10)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        for i in range(1,6):
                                print("===============================")
                                print("Validating infoblox_api"+str(i)+" user key length")
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
                                        print("infoblox_api"+str(i)+" user password key is in SHA128")
                                        print("===============================")
                                        print("\n")
                                else:
                                        assert False
                except Exception as error_message:
                        print("Failed to get the infoblox_api"+str(i)+" SHA128 password length from onedb.xml")
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 014 Execution Completed")

        @pytest.mark.run(order=015)
        def test_015_Create_non_super_user_group_with_only_CLI_access(self):
                print("\n============================================\n")
                print(" Creating non super user group with only CLI access ")
                print("\n============================================\n")
                data = {"access_method": ["CLI"],"name": "infoblox_cli"}
                response = ib_NIOS.wapi_request('POST', object_type="admingroup", fields=json.dumps(data))
                print(response)
                print("\n")
		sleep(10)
                print("Test Case 015 Execution Completed")

        @pytest.mark.run(order=016)
        def test_016_Validate_created_non_super_user_group_with_only_CLI_access(self):
                print("\n============================================\n")
                print(" Validate created non super user group with only CLI access ")
                print("\n============================================\n")
                response = ib_NIOS.wapi_request('GET',"admingroup?name=infoblox_cli&_return_fields=name,access_method",grid_vip=config.grid_vip)
                print(response)
                response = response.replace("\n","").replace(" ","")
                data = '''"access_method":["CLI"],"name":"infoblox_cli"'''
                if data in response:
                        assert True
                else:
                        assert False
                print("\n")
                print(data)
                print("\n")
                print("Test Case 016 Execution Completed")


        @pytest.mark.run(order=017)
        def test_017_Create_Users_in_created_non_super_User_group_infoblox_cli(self):
                print("\n============================================\n")
                print("Creating users in created non super User group infoblox_cli ")
                print("\n============================================\n")
                for i in range(1,6):
                        print("===============================")
                        print("Creating infoblox_cli"+str(i)+" user in created super user group")
                        print("===============================")
                        data = {"admin_groups": ["infoblox_cli"],"name": "infoblox_cli"+str(i),"password":"infoblox_cli"+str(i)}
                        response = ib_NIOS.wapi_request('POST', object_type="adminuser", fields=json.dumps(data))
                        print(response)
                        print("\n")
		sleep(10)
                print("Test Case 018 Execution Completed")

        @pytest.mark.run(order=18)
        def test_018_Validate_created_non_superusers_in_infoblox_cli_group(self):
                print("\n============================================\n")
                print(" Validating created non superusers in infoblox_cli group ")
                print("\n============================================\n")
                for i in range(1,6):
                        print("=============================================")
                        print("Validating created infoblox_api"+str(i)+" user in infoblox_api group")
                        print("=============================================")
                        response = ib_NIOS.wapi_request('GET','adminuser?name=infoblox_cli'+str(i),grid_vip=config.grid_vip)
                        print(response)
			sleep(05)
                        response = response.replace("\n","").replace(" ","")
                        data = '''"admin_groups":["infoblox_cli"],"name":"infoblox_cli'''+str(i)+'''"'''
                        if data in response:
                                assert True
                        else:
                                assert False
                        print("\n")
                        print(data)
                        print("\n")
                print("Test Case 018 Execution Completed")

        @pytest.mark.run(order=19)
        def test_019_Generate_one_db_file_and_validate_created_infoblox_cli_non_superusers_SHA128_bit_length(self):
                print("\n============================================\n")
                print(" Generate one db file and validate created infoblox_cli non superusers SHA128 bit length ")
                print("============================================")
                db =  onedb()
		sleep(10)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        for i in range(1,6):
                                print("===============================")
                                print("Validating infoblox_cli"+str(i)+" user key length")
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
                                        print("infoblox_cli"+str(i)+" user password key is in SHA128")
                                        print("===============================")
                                        print("\n")
                                else:
                                        assert False
                except Exception as error_message:
                        print("Failed to get the infoblox_cli"+str(i)+" SHA128 password bit length from onedb.xml")
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 019 Execution Completed")


        @pytest.mark.run(order=020)
        def test_020_Create_Users_in_SAML_group(self):
                print("\n============================================\n")
                print("Creating users in SAML group")
                print("\n============================================\n")
                for i in range(1,6):
                        print("===============================")
                        print("Creating SAML"+str(i)+" user in created super user group")
                        print("===============================")
                        data = {"admin_groups": ["saml-group"],"name": "saml"+str(i),"password":"saml"+str(i)}
                        response = ib_NIOS.wapi_request('POST', object_type="adminuser", fields=json.dumps(data))
                        print(response)
                        print("\n")
		sleep(10)
                print("Test Case 020 Execution Completed")

        @pytest.mark.run(order=21)
        def test_021_Validate_created_users_in_SAML_group(self):
                print("\n============================================\n")
                print("Validating created users in SAML group")
                print("\n============================================\n")
                for i in range(1,6):
                        print("=============================================")
                        print("Validating created SAML"+str(i)+" user in saml-group group")
                        print("=============================================")
                        response = ib_NIOS.wapi_request('GET','adminuser?name=saml'+str(i),grid_vip=config.grid_vip)
                        print(response)
			sleep(05)
                        response = response.replace("\n","").replace(" ","")
                        data = '''"admin_groups":["saml-group"],"name":"saml'''+str(i)+'''"'''
                        if data in response:
                                assert True
                        else:
                                assert False
                        print("\n")
                        print(data)
                        print("\n")
                print("Test Case 021 Execution Completed")



        @pytest.mark.run(order=22)
        def test_022_Generate_one_db_file_and_validate_SAML_group_users_SHA128_bit_length(self):
                print("\n============================================\n")
                print(" Generate one db file and validate SAML group users SHA128 bit length ")
                print("============================================")
                db =  onedb()
		sleep(10)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        for i in range(1,6):
                                print("===============================")
                                print("Validating saml"+str(i)+" user key length")
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
                                        print("saml"+str(i)+" user password key is in SHA128")
                                        print("===============================")
                                        print("\n")
                                else:
                                        assert False
                except Exception as error_message:
                        print("Failed to get the saml"+str(i)+" SHA128 password length from onedb.xml")
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 022 Execution Completed")

        @pytest.mark.run(order=023)
        def test_023_Create_non_super_user_group_with_all_access_methods(self):
                print("\n============================================\n")
                print(" Creating non super user group with all access methods ")
                print("\n============================================\n")
                data = {"access_method": ["GUI","API","CLI"],"name": "nonsuperuser"}
                response = ib_NIOS.wapi_request('POST', object_type="admingroup", fields=json.dumps(data))
                print(response)
                print("\n")
		sleep(10)
                print("Test Case 023 Execution Completed")

        @pytest.mark.run(order=024)
        def test_024_Validate_created_non_super_user_group_and_all_access_methods(self):
                print("\n============================================\n")
                print("Validating created non super user group and all access methods")
                print("\n============================================\n")
                response = ib_NIOS.wapi_request('GET',"admingroup?name=nonsuperuser&_return_fields=access_method,name",grid_vip=config.grid_vip)
                print(response)
		response = response.replace("\n","").replace(" ","")
		print(response)
                data = '''"access_method":["GUI","API","CLI"],"name":"nonsuperuser"'''
                if data in response:
                        assert True
                else:
                        assert False
                print("\n")
                print(data)
                print("\n")
                print("Test Case 024 Execution Completed")

        @pytest.mark.run(order=025)
        def test_025_Create_Users_in_nonsuperuser_group(self):
                print("\n============================================\n")
                print("Creating users in created nonsuperUser group")
                print("\n============================================\n")
                for i in range(1,6):
                        print("===============================")
                        print("Creating nonsuperuser"+str(i)+" user in created nonsuperuser group")
                        print("===============================")
                        data = {"admin_groups": ["nonsuperuser"],"name": "nonsuperuser"+str(i),"password":"nonsuperuser"+str(i)}
                        response = ib_NIOS.wapi_request('POST', object_type="adminuser", fields=json.dumps(data))
                        print(response)
                        print("\n")
		sleep(10)
                print("Test Case 025 Execution Completed")

        @pytest.mark.run(order=26)
        def test_026_Validate_created_users_in_nonsuperuser_group(self):
		print("\n============================================\n")
                print("Validating created users in created nonsuperUser group")
		print("\n============================================\n")
                print("\n")
                for i in range(1,6):
                        print("=============================================")
                        print("Validating created nonsuperuser"+str(i)+" user in nonsuperuser group")
                        print("=============================================")
                        response = ib_NIOS.wapi_request('GET','adminuser?name=nonsuperuser'+str(i),grid_vip=config.grid_vip)
                        print(response)
			sleep(05)
                        response = response.replace("\n","").replace(" ","")
                        data = '''"admin_groups":["nonsuperuser"],"name":"nonsuperuser'''+str(i)+'''"'''
                        if data in response:
                                assert True
                        else:
                                assert False
                        print("\n")
                        print(data)
                        print("\n")
                print("Test Case 026 Execution Completed")


        @pytest.mark.run(order=27)
        def test_027_Generate_one_db_file_and_validate_nonsuperusers_SHA128_bit_length(self):
                print("\n============================================\n")
                print(" Generate one db file and validate nonsuperusers SHA128 bit length ")
                print("============================================")
		db =  onedb()
		sleep(10)
                try:
                        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.logfile=sys.stdout
                        child.expect('#')
                        for i in range(1,6):
                                print("===============================")
                                print("Validating nonsuperuser"+str(i)+" user key length")
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
                                        print("nonsuperuser"+str(i)+" user password key is in SHA128")
                                        print("===============================")
                                        print("\n")
                                else:
                                        assert False
                except Exception as error_message:
                        print("Failed to get the nonsuperuser"+str(i)+" SHA128 password length from onedb.xml")
			print(error_message)
                        assert False
                finally:
                        child.close()
                print("Test Case 027 Execution Completed")























































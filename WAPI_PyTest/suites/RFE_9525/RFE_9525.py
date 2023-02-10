import re
import config
import pytest
import unittest
import logging
import os
import os.path
from os.path import join
import subprocess
import commands
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
from ib_utils.log_capture import log_action as log
#import ib_utils.log_validation as logv
from ib_utils.log_validation import log_validation as logv

class RFE_9525(unittest.TestCase):

        @pytest.mark.run(order=1)
        def test_001_Start_DNS_Service(self):
                logging.info("Start DNS Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify a enable_dns")
                data = {"enable_dns": True}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                sleep(20)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 1 Execution Completed")

        @pytest.mark.run(order=2)
        def test_002_Validate_DNS_service_Enabled(self):
                logging.info("Validate DNs Service is enabled")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res 
                for i in res:
                        print i
                        logging.info("found")
                        assert i["enable_dns"] == True
                logging.info("Test Case 2 Execution Completed")
                logging.info("============================")

        @pytest.mark.run(order=3)
        def test_003_Modify_Grid_Properties_To_Configure_DNS_Resolver(self):
                logging.info("Configure DNS Resolver at Grid Level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"dns_resolver_setting": {"resolvers": ["10.102.3.10"]}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 1 Execution Completed")


        @pytest.mark.run(order=4)
        def test_004_Modify_Grid_Properties_To_Configure_Email_Notification(self):
                logging.info("Enable Email Notification at Grid Level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"trap_notifications": [{"enable_email": True,"enable_trap": True,"trap_type": "DNS"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 1 Execution Completed")
                sleep(20)


        @pytest.mark.run(order=5)
        def test_005_Validate_Email_Settings_with_defult_smtps_use_authentication_are_disabled_and_default_port_number_25_is_configured(self):
                logging.info("Validate Enable Email Settings with Only To Email Address Configuration and From Email Address is Empty at Grid Level")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="grid",params="?_return_fields=email_setting")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                string = {"email_setting": {"enabled": False,"port_number": 25,"relay_enabled": False,"smtps": False,"use_authentication": False}}
                if res == string:
                	assert True
                #else:
                 #      	assert False

                logging.info("Test Case 5 Execution Completed")
                logging.info("============================")



        @pytest.mark.run(order=6)
        def test_006_At_Grid_Properties_Try_To_Configure_Email_Settings_with_To_Email_address_and_From_Email_address_with_Port_number_other_than_25_when_SMTP_OR_Use_authentication_are_not_Enabled(self):
                logging.info("Enable Email Settings with To Email Address Configuration and From Email Address and Port Numebr other than 25 when SMTP or Use Authentication are not enabled at Grid Level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "qa@test.lab","port_number": 251}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Valid port is 25."',response)
                logging.info("Test Case 6 Execution Completed")




        @pytest.mark.run(order=7)
        def test_007_At_Grid_Properties_Try_To_Configure_Email_Settings_with_Enable_Use_Authentication_But_with_Empty_From_Email_Address_and_without_Password_Attribute(self):
                logging.info("Try To Configure Email Settings with Enable Use Authentication but with empty From Email Address and without Password attribute at Grid Level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "","relay_enabled": True,"relay": "10.35.141.10","use_authentication": True}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "From Email Address is required when use authentication is enabled."',response)
                logging.info("Test Case 7 Execution Completed")




        @pytest.mark.run(order=8)
        def test_008_At_Grid_Properties_Try_To_Configure_Email_Settings_with_Enable_Use_Authentication_with_valid_From_Email_Address_and_without_Password_Attribute(self):
                logging.info("Try To Configure Email Settings with Enable Use Authentication with valid From Email Address and without Password attribute at Grid Level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "qa@test.lab","relay_enabled": True,"relay": "10.35.141.10","use_authentication": True}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Password cannot be empty."',response)
                logging.info("Test Case 8 Execution Completed")




        @pytest.mark.run(order=9)
        def test_009_At_Grid_Properties_Try_To_Configure_Email_Settings_with_Enable_Use_Authentication_with_valid_From_Email_Address_and_with_Empty_Password_Value(self):
                logging.info("Try To Configure Email Settings with Enable Use Authentication with valid From Email Address and with empty Password value at Grid Level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "qa@test.lab","relay_enabled": True,"relay": "10.35.141.10","use_authentication": True,"password": ""}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Password cannot be empty."',response)
                logging.info("Test Case 9 Execution Completed")




        @pytest.mark.run(order=10)
        def test_010_At_Grid_Properties_Try_To_Configure_Email_Settings_with_Enable_Use_Authentication_with_valid_From_Email_Address_and_with_Password_Value_lesserthan_4_Characters(self):
                logging.info("Try To Configure Email Settings with Enable Use Authentication with valid From Email Address and with Password value as lesser than 4 characters at Grid Level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "qa@test.lab","relay_enabled": True,"relay": "10.35.141.10","use_authentication": True,"password": "abc","port_number": 25}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Password length should be between 4-64 characters."',response)
                logging.info("Test Case 10 Execution Completed")




        @pytest.mark.run(order=11)
        def test_011_At_Grid_Properties_Try_To_Configure_Email_Settings_with_Enable_Use_Authentication_with_valid_From_Email_Address_and_with_Password_Value_More_than_64_Characters(self):
                logging.info("Try To Configure Email Settings with Enable Use Authentication with valid From Email Address and with Password value as more than 64 characters at Grid Level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "qa@test.lab","relay_enabled": True,"relay": "10.35.141.10","use_authentication": True,"password": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","port_number": 25}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                print('------------------------')
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Password length should be between 4-64 characters."',response)
                logging.info("Test Case 11 Execution Completed")



        @pytest.mark.run(order=12)
        def test_012_At_Grid_Properties_Try_To_Configure_Email_Settings_with_Enable_Use_Authentication_with_Port_number_other_than_25_and_465(self):
                logging.info("Try To Configure Email Settings with Enable Use Authentication with valid From Email Address and with port number value other than 25 and 465 at Grid Level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "qa@test.lab","relay_enabled": True,"relay": "10.35.141.10","use_authentication": True,"password": "infoblox","port_number": 251}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Valid ports are 25 and 465."',response)
                logging.info("Test Case 12 Execution Completed")




        @pytest.mark.run(order=13)
        def test_013_At_Grid_Properties_Try_To_Configure_Email_Settings_with_Enable_SMTPS_When_Use_Authentication_is_Disable(self):
                logging.info("Try To Configure Email Settings with Enable SMTPS When Use Authentication is disabled")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "qa@test.lab","relay_enabled": True,"relay": "10.35.141.10","use_authentication": False,"smtps": True}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Use authentication must be enabled when smtps is enabled"',response)
                logging.info("Test Case 13 Execution Completed")





        @pytest.mark.run(order=14)
        def test_014_At_Grid_Properties_Try_To_Configure_Email_Settings_with_Enable_SMTPS_and_Use_Authentication_and_From_Email_address_is_Empty(self):
                logging.info("Try To Configure Email Settings with Enable SMTPS and Use Authentication with From Email Address is Empty")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "","relay_enabled": True,"relay": "10.35.141.10","use_authentication": True,"smtps": True}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "From Email Address is required when use authentication is enabled."',response)
                logging.info("Test Case 14 Execution Completed")







        @pytest.mark.run(order=15)
        def test_015_At_Grid_Properties_Try_To_Configure_Email_Settings_with_Enable_SMTPS_and_Use_Authentication_and_without_Password_attribute(self):
                logging.info("Try To Configure Email Settings with Enable SMTPS and Use Authentication with Valid From Email address and without Password Attribute")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "qa@test.lab","relay_enabled": True,"relay": "10.35.141.10","use_authentication": True,"smtps": True}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Password cannot be empty."',response)
                logging.info("Test Case 15 Execution Completed")





        @pytest.mark.run(order=16)
        def test_016_At_Grid_Properties_Try_To_Configure_Email_Settings_with_Enable_SMTPS_and_Use_Authentication_and_with_Empty_Password_Value(self):
                logging.info("Try To Configure Email Settings with Enable SMTPS and Use Authentication with Valid From Email address and with Empty Password ")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "qa@test.lab","relay_enabled": True,"relay": "10.35.141.10","use_authentication": True,"smtps": True,"password": "","port_number": 2525}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Password cannot be empty."',response)
                logging.info("Test Case 16 Execution Completed")




        @pytest.mark.run(order=17)
        def test_017_At_Grid_Properties_Try_To_Configure_Email_Settings_with_Enable_SMTPS_and_Use_Authentication_and_with_Password_Value_lesserthan_4_Characters(self):
                logging.info("Try To Configure Email Settings with Enable SMTPS and Use Authentication with Valid From Email address and with Password value lesser than 4 characters")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "qa@test.lab","relay_enabled": True,"relay": "10.35.141.10","use_authentication": True,"smtps": True,"password": "abc","port_number": 2525}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Password length should be between 4-64 characters."',response)
                logging.info("Test Case 17 Execution Completed")






        @pytest.mark.run(order=18)
        def test_018_At_Grid_Properties_Try_To_Configure_Email_Settings_with_Enable_SMTPS_and_Use_Authentication_and_with_Password_Value_more_than_64_Characters(self):
                logging.info("Try To Configure Email Settings with Enable SMTPS and Use Authentication with Valid From Email address and with Password value more than 64 characters")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "qa@test.lab","relay_enabled": True,"relay": "10.35.141.10","use_authentication": True,"smtps": True,"password": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","port_number": 2525}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Password length should be between 4-64 characters."',response)
                logging.info("Test Case 18 Execution Completed")



        @pytest.mark.run(order=19)
        def test_019_At_Grid_Properties_Try_To_Configure_Email_Settings_with_Enable_SMTPS_and_Use_Authentication_and_with_valid_Password_But_Port_number_other_than_587_and_2525(self):
                logging.info("Try To Configure Email Settings with Enable SMTPS and Use Authentication with Valid From Email address and with valid Password but Port number other than 578 and 2525")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "qa@test.lab","relay_enabled": True,"relay": "10.35.141.10","use_authentication": True,"smtps": True,"port_number": 25,"password": "infoblox"}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Valid ports are 587 and 2525."',response)
                logging.info("Test Case 19 Execution Completed")



        @pytest.mark.run(order=20)
        def test_020_At_Grid_Properties_Try_To_Configure_Email_Settings_with_Port_number_as_String(self):
                logging.info("Try To Configure Email Settings with Port number as String")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "qa@test.lab","relay_enabled": True,"relay": "10.35.141.10","use_authentication": True,"smtps": True,"port_number": "aa","password": "infoblox"}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Invalid value for port_number: \\\"aa\\\": Must be integer type"',response)
                logging.info("Test Case 20 Execution Completed")



        @pytest.mark.run(order=21)
        def test_021_At_Grid_Properties_Configure_Email_Settings_without_From_Email_address_and_Use_Authentication__as_Before(self):
                logging.info("Configure Email Settings without use authentication or new options and validate it works as before")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                #data = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "","relay_enabled": False}}
                data = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "","relay_enabled": True,"relay": "10.120.3.100"}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 21 Execution Completed")



        @pytest.mark.run(order=22)
        def test_022_Validate_Email_Settings_Configured_with_only_To_Email_and_smtps_use_authentication_are_disabled_and_default_port_number_25_is_configured(self):
                logging.info("Validate Enable Email Settings with Only To Email Address Configuration and From Email Address is Empty at Grid Level")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="grid",params="?_return_fields=email_setting")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
		#because of relay server making below chnages
		#string = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","port_number": 25,"relay_enabled": False,"smtps": False,"use_authentication": False}}
                string = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","port_number": 25,"relay_enabled": True,"relay": "10.120.3.100","smtps": False,"use_authentication": False}}
                if res == string:
                        assert True

                logging.info("Test Case 22 Execution Completed")
                logging.info("============================")


        @pytest.mark.run(order=23)
        def test_023_start_Syslog_Messages_logs(self):
                logging.info("Starting Syslog Messages Logs")
                log("start","/var/log/syslog",config.grid_vip)


        @pytest.mark.run(order=24)
        def test_024_Stop_DNS_Service(self):
                logging.info("Stop DNS Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify a enable_dns")
                data = {"enable_dns": False}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                sleep(40)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 1 Execution Completed")


        @pytest.mark.run(order=25)
        def test_025_stop_Syslog_Messages_Logs(self):
                logging.info("Stopping Syslog Logs")
                log("stop","/var/log/syslog",config.grid_vip)
                print("Test Case 25 Execution Completed")


        @pytest.mark.run(order=26)
        def test_026_validate_Syslog_Messages_for_Sent_Mail_for(self):
                logging.info("Validating Sylog Messages Logs")
                LookFor="\"info Sent mail for no-reply\""
                #LookFor="\"ajit\""

                #LookFor=".*info Sent mail for no.*reply.*"
                logv(LookFor,"/var/log/syslog",config.grid_vip)
                print("Test Case 26 Execution Completed")


        @pytest.mark.run(order=27)
        def test_027_At_Grid_Properties_Configure_Email_Settings_with_From_Email_address_and_without_Use_Authentication__as_Before(self):
                logging.info("Configure Email Settings with From Email Address and without use authentication or new options and validate it works as before")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "qa@test.lab","relay_enabled": True,"relay": "10.120.3.100"}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 27 Execution Completed")



        @pytest.mark.run(order=28)
        def test_028_Validate_Email_Settings_Configured_with_To_Email_and_FRom_Email_and_smtps_use_authentication_are_disabled_and_default_port_number_25_is_configured(self):
                logging.info("Validate Enable Email Settings with Only To Email Address and From Email Address are configured and rest all options are disabled at Grid Level")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="grid",params="?_return_fields=email_setting")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
		#because of relay server making below chnages
                #string = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "qa@test.lab","relay": "10.35.141.10","port_number": 25,"relay_enabled": False,"smtps": False,"use_authentication": False}}
                string = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "qa@test.lab","relay": "10.120.3.100","port_number": 25,"relay_enabled": True,"smtps": False,"use_authentication": False}}
                if res == string:
                        assert True

                logging.info("Test Case 28 Execution Completed")
                logging.info("============================")


        @pytest.mark.run(order=29)
        def test_029_start_Syslog_Messages_logs(self):
                logging.info("Starting Syslog Messages Logs")
                log("start","/var/log/syslog",config.grid_vip)


        @pytest.mark.run(order=30)
        def test_030_Start_DNS_Service(self):
                logging.info("Start DNS Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify a enable_dns")
                data = {"enable_dns": True}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                sleep(40)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 30  Execution Completed")


        @pytest.mark.run(order=31)
        def test_031_stop_Syslog_Messages_Logs(self):
                logging.info("Stopping Syslog Logs")
                log("stop","/var/log/syslog",config.grid_vip)
                print("Test Case 31 Execution Completed")


        @pytest.mark.run(order=32)
        def test_032_validate_Syslog_Messages_for_Sent_Mail_for(self):
                logging.info("Validating Sylog Messages Logs")
                LookFor="\"info Sent mail for qa@test.lab\""
                #LookFor=".*info Sent mail for qa@test.lab.*"
                logv(LookFor,"/var/log/syslog",config.grid_vip)
                print("Test Case 32 Execution Completed")


        @pytest.mark.run(order=33)
        def test_033_At_Grid_Properties_Configure_Email_Settings_with_From_Email_address_and_with_Use_Authentication_is_Enabled_with_not_matched_password(self):
                logging.info("Configure Email Settings with To Email,From Email Address configuration with Use Authentication enabled and not matched password with From Email Address")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "qa@test.lab","relay_enabled": True,"relay": "10.35.141.10","smtps": False,"use_authentication": True,"password": "infoblox12","port_number": 25}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 33 Execution Completed")



        @pytest.mark.run(order=34)
        def test_034_Validate_Email_Settings_Configured_with_To_Email_and_FRom_Email_and_use_authentication_is_enabled_with_password_for_From_Email_Address_with_port_number_25_is_configured(self):
                logging.info("Validate Enable Email Settings with Only To Email Address and From Email Address are configured with Use Authentication enabled with valid port number at Grid Level")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="grid",params="?_return_fields=email_setting")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                string = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "qa@test.lab","relay": "10.35.141.10","port_number": 25,"relay_enabled": True,"smtps": False,"use_authentication": True,"port_number": 25}}
                if res == string:
                        assert True

                logging.info("Test Case 34 Execution Completed")
                logging.info("============================")


        @pytest.mark.run(order=35)
        def test_035_start_Syslog_Messages_logs(self):
                logging.info("Starting Syslog Messages Logs")
                log("start","/var/log/syslog",config.grid_vip)


        @pytest.mark.run(order=36)
        def test_036_Stop_DNS_Service(self):
                logging.info("Stop DNS Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify a enable_dns")
                data = {"enable_dns": False}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                sleep(40)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 36  Execution Completed")



        @pytest.mark.run(order=37)
        def test_037_stop_Syslog_Messages_Logs(self):
                logging.info("Stopping Syslog Logs")
                log("stop","/var/log/syslog",config.grid_vip)
                print("Test Case 37 Execution Completed")


        @pytest.mark.run(order=38)
        def test_038_validate_Syslog_Messages_for_Sent_Mail_for(self):
                logging.info("Validating Sylog Messages Logs")
                LookFor="\"err Authorization failed\""
                logv(LookFor,"/var/log/syslog",config.grid_vip)
                print("Test Case 38 Execution Completed")



        @pytest.mark.run(order=39)
        def test_039_At_Grid_Properties_Configure_Email_Settings_with_From_Email_address_and_with_SMTP_and_Use_Authentication_is_Enabled_with_not_matched_password(self):
                logging.info("Configure Email Settings with To Email,From Email Address configuration with SMTP and  Use Authentication enabled and not matched password with From Email Address")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "qa@test.lab","relay_enabled": True,"relay": "10.35.141.10","smtps": True,"use_authentication": True,"password": "infoblox12","port_number": 2525}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 39 Execution Completed")



        @pytest.mark.run(order=40)
        def test_040_Validate_Email_Settings_Configured_with_To_Email_and_FRom_Email_SMTP_and_use_authentication_is_enabled_with_password_for_From_Email_Address_with_port_number_25_is_configured(self):
                logging.info("Validate Enable Email Settings with Only To Email Address and From Email Address are configured with SMTP and  Use Authentication enabled with valid port number at Grid Level")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="grid",params="?_return_fields=email_setting")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                string = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "qa@test.lab","relay": "10.35.141.10","port_number": 25,"relay_enabled": True,"smtps": True,"use_authentication": True,"port_number": 2525}}
                if res == string:
                        assert True

                logging.info("Test Case 40 Execution Completed")
                logging.info("============================")


        @pytest.mark.run(order=41)
        def test_041_start_Syslog_Messages_logs(self):
                logging.info("Starting Syslog Messages Logs")
                log("start","/var/log/syslog",config.grid_vip)


        @pytest.mark.run(order=42)
        def test_042_Start_DNS_Service(self):
                logging.info("Start DNS Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify a enable_dns")
                data = {"enable_dns": True}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                sleep(40)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 42  Execution Completed")



        @pytest.mark.run(order=43)
        def test_043_stop_Syslog_Messages_Logs(self):
                logging.info("Stopping Syslog Logs")
                log("stop","/var/log/syslog",config.grid_vip)
                print("Test Case 43 Execution Completed")


        @pytest.mark.run(order=44)
        def test_044_validate_Syslog_Messages_for_Sent_Mail_for(self):
                logging.info("Validating Sylog Messages Logs")
                LookFor="\"err Authorization failed\""
                logv(LookFor,"/var/log/syslog",config.grid_vip)
                print("Test Case 44 Execution Completed")




        @pytest.mark.run(order=45)
        def test_045_At_Grid_Properties_Configure_Email_Settings_with_From_Email_address_with_SMTP_and_Use_Authentication_are_Enabled_with_matched_password(self):
                logging.info("Configure Email Settings with To Email,From Email Address configuration with SMTP and Use Authentication enabled and  matched password with From Email Address")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "qa@test.lab","relay_enabled": True,"relay": "10.35.141.10","smtps": True,"use_authentication": True,"password": "infoblox","port_number": 2525}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 45 Execution Completed")



        @pytest.mark.run(order=46)
        def test_046_Validate_Email_Settings_Configured_with_To_Email_and_From_Email_andSMTP_and_use_authentication_are_enabled_with_password_for_From_Email_Address_with_port_number_2525_is_configured(self):
                logging.info("Validate Enable Email Settings with Only To Email Address and From Email Address are configured with SMTP and Use Authentication are  enabled with valid Pasword and  port number at Grid Level")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="grid",params="?_return_fields=email_setting")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                string = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "qa@test.lab","relay": "10.35.141.10","port_number": 2525,"relay_enabled": True,"smtps": True,"use_authentication": True,"port_number": 2525}}
                if res == string:
                        assert True

                logging.info("Test Case 46 Execution Completed")
                logging.info("============================")


        @pytest.mark.run(order=47)
        def test_047_start_Syslog_Messages_logs(self):
                logging.info("Starting Syslog Messages Logs")
                log("start","/var/log/syslog",config.grid_vip)


        @pytest.mark.run(order=48)
        def test_048_Stop_DNS_Service(self):
                logging.info("Stop DNS Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify a enable_dns")
                data = {"enable_dns": False}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                sleep(40)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 48  Execution Completed")



        @pytest.mark.run(order=49)
        def test_049_stop_Syslog_Messages_Logs(self):
                logging.info("Stopping Syslog Logs")
                log("stop","/var/log/syslog",config.grid_vip)
                print("Test Case 49 Execution Completed")


        @pytest.mark.run(order=50)
        def test_050_validate_Syslog_message_for_Creating_SSL_connection_to_host(self):
                logging.info("Validating Sylog Messages Logs for info Creating SSL connection to host")
                LookFor="\"info Creating SSL connection to host\""
                logv(LookFor,"/var/log/syslog",config.grid_vip)
                print("Test Case 50 Execution Completed")

        @pytest.mark.run(order=51)
        def test_051_validate_Syslog_message_for_SSL_connection_using_ECDHE_RSA_AES256_GCM_SHA384(self):
                logging.info("Validating Sylog Messages Logs for SSL connection using ECDHE-RSA-AES256-GCM-SHA384")
                LookFor="\"SSL connection using ECDHE-RSA-AES256-GCM-SHA384\""
                logv(LookFor,"/var/log/syslog",config.grid_vip)
                print("Test Case 51 Execution Completed")


        @pytest.mark.run(order=52)
        def test_052_validate_Syslog_Messages_for_Sent_Mail_for(self):
                logging.info("Validating Sylog Messages Logs")
                LookFor="\"Sent mail for qa@test.lab\""
                logv(LookFor,"/var/log/syslog",config.grid_vip)
                print("Test Case 52 Execution Completed")


        @pytest.mark.run(order=53)
        def test_053_Validate_Email_Settings_At_Member_Level_are_by_Default_disabled_SMTP_and_use_authentication_and_Port_Number_25_is_Configured(self):
                logging.info("Validate at Member Level By default SMTP and Use Authentication are disabled and port number 25 is configured by default")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print res
                print ref1

                get_tacacsplus = ib_NIOS.wapi_request('GET', ref=ref1,params="?_return_fields=email_setting,use_email_setting")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                string = {"use_email_setting": False, "_ref": ref1,"email_setting": {"relay_enabled": False, "port_number": 25, "use_authentication": False, "enabled": False, "smtps": False}}
                if res == string:
                        assert True
                else:
                        assert False
                logging.info("Test Case 53 Execution Completed")
                logging.info("============================")




        @pytest.mark.run(order=54)
        def test_054_At_Member_Properties_Override_Email_Settings_and_dont_Configure_Email_Settings(self):
                logging.info("At Member level Override and dont Configure Email Settings")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1
                data = {"use_email_setting": True}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 54 Execution Completed")


        @pytest.mark.run(order=55)
        def test_055_Validate_Email_Settings_At_Member_Level_when_Email_settings_are_Override_and_not_Configured_Any_Email_settings(self):
                logging.info("Validate at Member Level when Override and not configured then default SMTP and Use Authentication are disabled and port number 25 is configured by default")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print res
                print ref1

                get_tacacsplus = ib_NIOS.wapi_request('GET', ref=ref1,params="?_return_fields=email_setting,use_email_setting")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                string = {"use_email_setting": True, "_ref": ref1,"email_setting": {"relay_enabled": False, "port_number": 25, "use_authentication": False, "enabled": False, "smtps": False}}
                if res == string:
                        assert True
                else:
                        assert False
                logging.info("Test Case 55 Execution Completed")
                logging.info("============================")




        @pytest.mark.run(order=56)
        def test_056_start_Syslog_Messages_logs(self):
                logging.info("Starting Syslog Messages Logs")
                log("start","/var/log/syslog",config.grid_member1_vip)


        @pytest.mark.run(order=57)
        def test_057_Stop_DNS_Service(self):
                logging.info("Stop DNS Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1

                logging.info("Modify a enable_dns")
                data = {"enable_dns": False}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                sleep(40)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 57  Execution Completed")



        @pytest.mark.run(order=58)
        def test_058_stop_Syslog_Messages_Logs(self):
                logging.info("Stopping Syslog Logs")
                log("stop","/var/log/syslog",config.grid_member1_vip)
                print("Test Case 58 Execution Completed")


        @pytest.mark.run(order=59)
        def test_059_validate_Syslog_Messages_for_Sent_Mail_for(self):
                logging.info("Validating Sylog Messages Logs")
                LookFor="\"\""
                logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
                print("Test Case 59 Execution Completed")




        @pytest.mark.run(order=60)
        def test_060_At_Member_Properties_Override_Email_Settings_and_dont_Configure_Email_Settings(self):
                logging.info("At Member level inherit Email Settings from the Grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1
                data = {"use_email_setting": False}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 60 Execution Completed")


        @pytest.mark.run(order=61)
        def test_061_Validate_Email_Settings_At_Member_Level_when_Email_settings_are_Inherited_from_Grid(self):
                logging.info("Validate at Member Level Email Settings are inherrited from the Grid  level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print res
                print ref1

                get_tacacsplus = ib_NIOS.wapi_request('GET', ref=ref1,params="?_return_fields=email_setting,use_email_setting")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                string = {"use_email_setting": False, "_ref": ref1,"email_setting": {"relay_enabled": False, "port_number": 25, "use_authentication": False, "enabled": False, "smtps": False}}
                if res == string:
                        assert True
                else:
                        assert False
                logging.info("Test Case 61 Execution Completed")
                logging.info("============================")




        @pytest.mark.run(order=62)
        def test_062_start_Syslog_Messages_logs(self):
                logging.info("Starting Syslog Messages Logs")
                log("start","/var/log/syslog",config.grid_member1_vip)


        @pytest.mark.run(order=63)
        def test_063_Start_DNS_Service(self):
                logging.info("Start DNS Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1

                logging.info("Modify a enable_dns")
                data = {"enable_dns": True}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                sleep(40)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 63  Execution Completed")



        @pytest.mark.run(order=64)
        def test_064_stop_Syslog_Messages_Logs(self):
                logging.info("Stopping Syslog Logs")
                log("stop","/var/log/syslog",config.grid_member1_vip)
                print("Test Case 64 Execution Completed")


        @pytest.mark.run(order=65)
        def test_065_validate_Syslog_message_for_Creating_SSL_connection_to_host(self):
                logging.info("Validating Sylog Messages Logs for info Creating SSL connection to host")
                LookFor="\"info Creating SSL connection to host\""
                logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
                print("Test Case 65 Execution Completed")

        @pytest.mark.run(order=66)
        def test_066_validate_Syslog_message_for_SSL_connection_using_ECDHE_RSA_AES256_GCM_SHA384(self):
                logging.info("Validating Sylog Messages Logs for SSL connection using ECDHE-RSA-AES256-GCM-SHA384")
                LookFor="\"SSL connection using ECDHE-RSA-AES256-GCM-SHA384\""
                logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
                print("Test Case 66 Execution Completed")


        @pytest.mark.run(order=67)
        def test_067_validate_Syslog_Messages_for_Sent_Mail_for(self):
                logging.info("Validating Sylog Messages Logs")
                LookFor="\"Sent mail for qa@test.lab\""
                logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
                print("Test Case 67 Execution Completed")


        @pytest.mark.run(order=68)
        def test_068_validate_Syslog_Messages_for_Sent_Mail_for(self):
                logging.info("Validating Sylog Messages Logs")
                LookFor="\"Sent mail for qa@test.lab\""
                logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
                print("Test Case 68 Execution Completed")



        @pytest.mark.run(order=69)
        def test_069_At_Member_Properties_Override_Email_Settings_and_Configure_Email_Settings_with_Only_To_Email_Address(self):
                logging.info("At Member level Override and Configure Email Settings with only To Email Address")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1
                data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "","relay_enabled": False}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 69 Execution Completed")


        @pytest.mark.run(order=70)
        def test_070_Validate_Email_Settings_At_Member_Level_when_Email_settings_are_Override_and_Configured_with_only_From_Email_address_is_Configured(self):
                logging.info("Validate at Member Level when Override and Only From Email address is configured and SMTP and Use Authentication are disabled and port number 25 is configured by default")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print res
                print ref1

                get_tacacsplus = ib_NIOS.wapi_request('GET', ref=ref1,params="?_return_fields=email_setting,use_email_setting")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                string = {"use_email_setting": True, "_ref": ref1, "email_setting": {"relay_enabled": False, "enabled": True, "smtps": False, "port_number": 25, "address": "rkarjagi@infoblox.com", "use_authentication": False}}

                if res == string:
                        assert True
                else:
                        assert False
                logging.info("Test Case 70 Execution Completed")
                logging.info("============================")

        @pytest.mark.run(order=71)
        def test_071_At_Member_Properties_Try_to_Configure_Email_Settings_with_Port_Number_Other_than_25_Validate_Not_Allowed_and_Give_Proper_Error_Message(self):
                logging.info("At Member level Try to Configure Email Settings with Port Number Other than 25 and Validate it not allowed and give Proper Error Message")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1
                data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "","relay_enabled": False,"port_number": 251}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Valid port is 25."',response)
                logging.info("Test Case 71 Execution Completed")



        @pytest.mark.run(order=72)
        def test_072_At_Member_Properties_Try_To_Configure_Email_Settings_with_Enable_Use_Authentication_But_with_Empty_From_Email_Address_and_without_Password_Attribute(self):
                logging.info("At Member level Try to Configure Email Settings with Enable Use Authentication but with empty From Email Address and without Password attribute ")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1
                data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "","relay_enabled": True,"port_number": 25,"relay": "10.35.141.10","use_authentication": True}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "From Email Address is required when use authentication is enabled."',response)
                logging.info("Test Case 72 Execution Completed")


        @pytest.mark.run(order=73)
        def test_073_At_Member_Properties_Try_To_Configure_Email_Settings_with_Enable_Use_Authentication_with_valid_From_Email_Address_and_without_Password_Attribute(self):
                logging.info("At Member level Try to Configure Email Settings with Enable Use Authentication but with valid From Email Address and without Password attribute ")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1
                data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "dev@test.lab","relay_enabled": True,"port_number": 25,"relay": "10.35.141.10","use_authentication": True}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Password cannot be empty."',response)
                logging.info("Test Case 73 Execution Completed")



        @pytest.mark.run(order=74)
        def test_074_At_Member_Properties_Try_To_Configure_Email_Settings_with_Enable_Use_Authentication_with_valid_From_Email_Address_and_with_Empty_Password_Value(self):
                logging.info("At Member level Try To Configure Email Settings with Enable Use Authentication with valid From Email Address and with empty Password value")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1
                data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "dev@test.lab","relay_enabled": True,"port_number": 25,"relay": "10.35.141.10","use_authentication": True,"password": ""}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Password cannot be empty."',response)
                logging.info("Test Case 74 Execution Completed")



        @pytest.mark.run(order=75)
        def test_075_At_Member_Properties_Try_To_Configure_Email_Settings_with_Enable_Use_Authentication_with_valid_From_Email_Address_and_with_Password_Value_lesserthan_4_Characters(self):
                logging.info("At Member level Try To Configure Email Settings with Enable Use Authentication with valid From Email Address and with Password value as lesser than 4 characters ")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1
                #data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "dev@test.lab","relay_enabled": True,"port_number": 25,"relay": "10.35.141.10","use_authentication": True,"password": "aa"}}
                data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "dev@test.lab","relay_enabled": True,"port_number": 25,"relay": "10.120.3.100","use_authentication": True,"password": "aa"}}

                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Password length should be between 4-64 characters."',response)
                logging.info("Test Case 75 Execution Completed")


        @pytest.mark.run(order=76)
        def test_076_At_Member_Properties_Try_To_Configure_Email_Settings_with_Enable_Use_Authentication_with_valid_From_Email_Address_and_with_Password_Value_More_than_64_Characters(self):
                logging.info("At Member level Try To Configure Email Settings with Enable Use Authentication with valid From Email Address and with Password value as More than 64 characters ")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1
                #data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "dev@test.lab","relay_enabled": True,"port_number": 25,"relay": "10.35.141.10","use_authentication": True,"password": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}}
                data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "dev@test.lab","relay_enabled": True,"port_number": 25,"relay": "10.120.3.100","use_authentication": True,"password": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}}

                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Password length should be between 4-64 characters."',response)

                logging.info("Test Case 76 Execution Completed")


        @pytest.mark.run(order=77)
        def test_077_At_Member_Properties_Try_To_Configure_Email_Settings_with_Enable_Use_Authentication_with_Port_number_other_than_25_and_465(self):
                logging.info("At Member level Try To Configure Email Settings with Enable Use Authentication with valid From Email Address and with port number value other than 25 and 465 ")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1
                data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "dev@test.lab","relay_enabled": True,"port_number": 251,"relay": "10.35.141.10","use_authentication": True,"password": "infoblox"}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Valid ports are 25 and 465."',response)
                logging.info("Test Case 77 Execution Completed")


        @pytest.mark.run(order=78)
        def test_078_At_Member_Properties_Try_To_Configure_Email_Settings_with_Enable_SMTPS_When_Use_Authentication_is_Disable(self):
                logging.info("At Member level Try To Configure Email Settings with Enable SMTPS When Use Authentication is disabled ")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1
                data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "qa@test.lab","relay_enabled": True,"relay": "10.35.141.10","use_authentication": False,"smtps": True}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Use authentication must be enabled when smtps is enabled"',response)
                logging.info("Test Case 78 Execution Completed")



        @pytest.mark.run(order=79)
        def test_079_At_Member_Properties_Try_To_Configure_Email_Settings_with_Enable_SMTPS_and_Use_Authentication_and_From_Email_address_is_Empty(self):
                logging.info("At Member level Try To Configure Email Settings with Enable SMTPS and Use Authentication with From Email Address is Empty")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1
                data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "","relay_enabled": True,"relay": "10.35.141.10","use_authentication": True,"smtps": True}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "From Email Address is required when use authentication is enabled."',response)
                logging.info("Test Case 79 Execution Completed")


        @pytest.mark.run(order=80)
        def test_080_At_Member_Properties_Try_To_Configure_Email_Settings_with_Enable_SMTPS_and_Use_Authentication_and_without_Password_attribute(self):
                logging.info("At Member level Try To Configure Email Settings with Enable SMTPS and Use Authentication with Valid From Email address and without Password Attribute")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1
                data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "dev@test.lab","relay_enabled": True,"relay": "10.35.141.10","use_authentication": True,"smtps": True}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Password cannot be empty."',response)
                logging.info("Test Case 80 Execution Completed")



        @pytest.mark.run(order=81)
        def test_081_At_Member_Properties_Try_To_Configure_Email_Settings_with_Enable_SMTPS_and_Use_Authentication_and_with_Empty_Password_Value(self):
                logging.info("At Member level Try To Configure Email Settings with Enable SMTPS and Use Authentication with Valid From Email address and with Empty Password")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1
                data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "dev@test.lab","relay_enabled": True,"relay": "10.35.141.10","use_authentication": True,"smtps": True,"password": "","port_number": 2525}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Password cannot be empty."',response)
                logging.info("Test Case 81 Execution Completed")



        @pytest.mark.run(order=82)
        def test_082_At_Member_Properties_Try_To_Configure_Email_Settings_with_Enable_SMTPS_and_Use_Authentication_and_with_valid_Password_without_Port_number_Attribute_Default_25(self):
                logging.info("At Member level Try To Configure Email Settings with Enable SMTPS and Use Authentication with Valid From Email address and with valid Password but without Port number attribute by default port number will be 25 ")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1
                data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "dev@test.lab","relay_enabled": True,"relay": "10.35.141.10","use_authentication": True,"smtps": True,"password": "infoblox"}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Valid ports are 587 and 2525."',response)
                logging.info("Test Case 82 Execution Completed")


        @pytest.mark.run(order=83)
        def test_083_At_Member_Properties_Try_To_Configure_Email_Settings_with_Enable_SMTPS_and_Use_Authentication_and_with_valid_Password_But_Port_number_other_than_587_and_2525(self):
                logging.info("At Member level Try To Configure Email Settings with Enable SMTPS and Use Authentication with Valid From Email address and with valid Password but Port number other than 578 and 2525")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1
                data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "dev@test.lab","relay_enabled": True,"relay": "10.35.141.10","use_authentication": True,"smtps": True,"password": "infoblox","port_number": 251}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Valid ports are 587 and 2525."',response)
                logging.info("Test Case 83 Execution Completed")


        @pytest.mark.run(order=84)
        def test_084_At_Member_Properties_Try_To_Configure_Email_Settings_with_Port_number_as_String(self):
                logging.info("At Member level Try To Configure Email Settings with Port number as String")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1
                #data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "dev@test.lab","relay_enabled": True,"relay": "10.35.141.10","use_authentication": True,"smtps": True,"password": "infoblox","port_number": "aa"}}
                data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "dev@test.lab","relay_enabled": True,"relay": "10.120.3.100","use_authentication": True,"smtps": True,"password": "infoblox","port_number": "aa"}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Invalid value for port_number: \\\"aa\\\": Must be integer type"',response)
                logging.info("Test Case 84 Execution Completed")




        @pytest.mark.run(order=85)
        def test_085_At_Member_Properties_Configure_Email_Settings_without_From_Email_address_and_Use_Authentication__as_Before(self):
                logging.info("At Member level Override and Configure Email Settings with only To Email Address and  without use authentication or new options and validate it works as before")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1
                #data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "","relay_enabled": False}}
                #because of relay server making below chnages
		data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "","relay_enabled": True,"relay": "10.120.3.100"}}
		response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 85 Execution Completed")



        @pytest.mark.run(order=86)
        def test_086_Validate_Email_Settings_At_Member_Level_Configured_with_only_To_Email_and_smtps_use_authentication_are_disabled_and_default_port_number_25_is_configured(self):
                logging.info("Validate at Member Level when Override and Only To Email address is configured without use authentication or new options")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print res
                print ref1

                get_tacacsplus = ib_NIOS.wapi_request('GET', ref=ref1,params="?_return_fields=email_setting,use_email_setting")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                string = {"use_email_setting": True, "_ref": ref1, "email_setting": {"relay_enabled": True,"relay": "10.120.3.100", "enabled": True, "smtps": False, "port_number": 25, "address": "rkarjagi@infoblox.com", "use_authentication": False}}
                #string = {"use_email_setting": True, "_ref": ref1, "email_setting": {"relay_enabled": False, "enabled": True, "smtps": False, "port_number": 25, "address": "rkarjagi@infoblox.com", "use_authentication": False}}

                if res == string:
                        assert True
                else:
                        assert False
                logging.info("Test Case 86 Execution Completed")
                logging.info("============================")



        @pytest.mark.run(order=87)
        def test_087_start_Syslog_Messages_logs_for_Member(self):
                logging.info("Starting Syslog Messages Logs for Member")
                log("start","/var/log/syslog",config.grid_member1_vip)


        @pytest.mark.run(order=88)
        def test_088_Stop_DNS_Service(self):
                logging.info("Stop DNS Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1

                logging.info("Modify a enable_dns")
                data = {"enable_dns": False}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                sleep(60)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 88  Execution Completed")

        @pytest.mark.run(order=89)
        def test_089_stop_Syslog_Messages_Logs_for_Member(self):
                logging.info("Stopping Syslog Logs for Member")
                log("stop","/var/log/syslog",config.grid_member1_vip)
                print("Test Case 89 Execution Completed")


        @pytest.mark.run(order=90)
        def test_090_validate_Syslog_Messages_for_Sent_Mail_for(self):
                logging.info("Validating Sylog Messages Logs")
                LookFor="\"info Sent mail for no-reply\""
                #LookFor=".*info Sent mail for no.*reply.*"
                logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
                print("Test Case 90 Execution Completed")





        @pytest.mark.run(order=91)
        def test_091_At_Member_Properties_Configure_Email_Settings_with_From_Email_address_without_Use_Authentication_as_Before(self):
                logging.info("At Member level Override and Configure Email Settings with To Email Address and From Email Address and  without use authentication or new options and validate it works as before")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1
                #data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "dev@test.lab","relay_enabled": False}}
		#because of relay server making below chnages
		data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "dev@test.lab","relay_enabled": True,"relay": "10.120.3.100"}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 91 Execution Completed")



        @pytest.mark.run(order=92)
        def test_092_Validate_Email_Settings_At_Member_Level_Configured_with_To_Email_and_From_Email_Address_and_without_smtps_use_authentication_are_disabled_and_default_port_number_25_is_configured(self):
                logging.info("Validate at Member Level Enable Email Settings with Only To Email Address and From Email Address are configured and rest all options are disabled")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print res
                print ref1

                get_tacacsplus = ib_NIOS.wapi_request('GET', ref=ref1,params="?_return_fields=email_setting,use_email_setting")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                #string = {"use_email_setting": True, "_ref": ref1, "email_setting": {"relay_enabled": False, "enabled": True, "smtps": False, "port_number": 25, "address": "rkarjagi@infoblox.com","from_address": "dev@test.lab", "use_authentication": False}}
                string = {"use_email_setting": True, "_ref": ref1, "email_setting": {"relay_enabled": True,"relay": "10.120.3.100", "enabled": True, "smtps": False, "port_number": 25, "address": "rkarjagi@infoblox.com","from_address": "dev@test.lab", "use_authentication": False}}

                if res == string:
                        assert True
                else:
                        assert False
                logging.info("Test Case 92 Execution Completed")
                logging.info("============================")


        @pytest.mark.run(order=93)
        def test_093_start_Syslog_Messages_logs_for_Member(self):
                logging.info("Starting Syslog Messages Logs for Member")
                
                log("start","/var/log/syslog",config.grid_member1_vip)



        @pytest.mark.run(order=94)
        def test_094_Start_DNS_Service(self):
                logging.info("Start DNS Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1

                logging.info("Modify a enable_dns")
                data = {"enable_dns": True}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                sleep(60)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 94  Execution Completed")

        @pytest.mark.run(order=95)
        def test_095_stop_Syslog_Messages_Logs_for_Member(self):
                logging.info("Stopping Syslog Logs for Member")
                log("stop","/var/log/syslog",config.grid_member1_vip)
                print("Test Case 95 Execution Completed")



        @pytest.mark.run(order=96)
        def test_096_validate_Syslog_Messages_for_Sent_Mail_for(self):
                logging.info("Validating Sylog Messages Logs")
                LookFor="\"info Sent mail for dev@test.lab\""
                #LookFor=".*info Sent mail for dev@test.lab.*"
                logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
                print("Test Case 96 Execution Completed")




        @pytest.mark.run(order=97)
        def test_097_At_Member_Properties_Configure_Email_Settings_with_From_Email_address_and_with_Use_Authentication_is_Enabled_with_not_matched_password(self):
                logging.info("At Member level Override and Configure Email Settings with To Email,From Email Address configuration with Use Authentication enabled and not matched password with From Email Address")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1
                data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "dev@test.lab","relay_enabled": True,"relay": "10.35.141.10","smtps": False,"use_authentication": True,"password": "infoblox12","port_number": 25}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 97 Execution Completed")



        @pytest.mark.run(order=98)
        def test_098_Validate_Email_Settings_At_Member_Level_Configured_Configured_with_To_Email_and_FRom_Email_and_use_authentication_is_enabled_with_password_for_From_Email_Address_with_port_number_25_is_configured(self):
                logging.info("Validate at Member Level when Override and Email Settings with Only To Email Address and From Email Address are configured with Use Authentication enabled with valid port number ")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print res
                print ref1

                get_tacacsplus = ib_NIOS.wapi_request('GET', ref=ref1,params="?_return_fields=email_setting,use_email_setting")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                string = {"use_email_setting": True, "_ref": ref1, "email_setting": {"relay_enabled": True,"relay": "10.35.141.10", "enabled": True, "smtps": False, "port_number": 25, "address": "rkarjagi@infoblox.com", "from_address": "dev@test.lab", "use_authentication": True}}

                if res == string:
                        assert True
                else:
                        assert False
                logging.info("Test Case 98 Execution Completed")
                logging.info("============================")


        @pytest.mark.run(order=99)
        def test_099_start_Syslog_Messages_logs_for_Member(self):
                logging.info("Starting Syslog Messages Logs for Member")
                log("start","/var/log/syslog",config.grid_member1_vip)


        @pytest.mark.run(order=100)
        def test_100_Stop_DNS_Service(self):
                logging.info("Start DNS Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1

                logging.info("Modify a enable_dns")
                data = {"enable_dns": False}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                sleep(40)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 100  Execution Completed")

        @pytest.mark.run(order=101)
        def test_101_stop_Syslog_Messages_Logs_for_Member(self):
                logging.info("Stopping Syslog Logs for Member")
                log("stop","/var/log/syslog",config.grid_member1_vip)
                print("Test Case 101 Execution Completed")



        @pytest.mark.run(order=102)
        def test_102_validate_Syslog_Messages_for_Sent_Mail_for(self):
                logging.info("Validating Sylog Messages Logs")
                LookFor="\"err Authorization failed\""
                logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
                print("Test Case 102 Execution Completed")


        @pytest.mark.run(order=103)
        def test_103_At_Member_Properties_Configure_Email_Settings_with_From_Email_address_and_with_Use_Authentication_is_Enabled_with_matched_password(self):
                logging.info("At Member level Override and Configure Email Settings with To Email,From Email Address configuration with Use Authentication enabled with matched password with From Email Address")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1
                data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "dev@test.lab","relay_enabled": True,"relay": "10.35.141.10","smtps": False,"use_authentication": True,"password": "infoblox","port_number": 25}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 103 Execution Completed")



        @pytest.mark.run(order=104)
        def test_104_Validate_Email_Settings_At_Member_Level_Configured_Configured_with_To_Email_and_FRom_Email_and_use_authentication_is_enabled_with_password_for_From_Email_Address_with_port_number_25_is_configured(self):
                logging.info("Validate at Member Level when Override and Email Settings with To Email Address and From Email Address are configured with Use Authentication enabled with valid port number and matched Password for From Email Address ")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print res
                print ref1

                get_tacacsplus = ib_NIOS.wapi_request('GET', ref=ref1,params="?_return_fields=email_setting,use_email_setting")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                string = {"use_email_setting": True, "_ref": ref1, "email_setting": {"relay_enabled": True,"relay": "10.35.141.10", "enabled": True, "smtps": False, "port_number": 25, "address": "rkarjagi@infoblox.com", "from_address": "dev@test.lab", "use_authentication": True}}

                if res == string:
                        assert True
                else:
                        assert False
                logging.info("Test Case 104 Execution Completed")
                logging.info("============================")



        @pytest.mark.run(order=105)
        def test_105_start_Syslog_Messages_logs_for_Member(self):
                logging.info("Starting Syslog Messages Logs for Member")
                log("start","/var/log/syslog",config.grid_member1_vip)


        @pytest.mark.run(order=106)
        def test_106_Start_DNS_Service(self):
                logging.info("Start DNS Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1

                logging.info("Modify a enable_dns")
                data = {"enable_dns": True}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                sleep(40)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 106  Execution Completed")

        @pytest.mark.run(order=107)
        def test_107_stop_Syslog_Messages_Logs_for_Member(self):
                logging.info("Stopping Syslog Logs for Member")
                log("stop","/var/log/syslog",config.grid_member1_vip)
                print("Test Case 107 Execution Completed")



        @pytest.mark.run(order=108)
        def test_108_validate_Syslog_Messages_for_Sent_Mail_for(self):
                logging.info("Validating Sylog Messages Logs")
                LookFor="\"Sent mail for dev@test.lab\""
                logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
                print("Test Case 108 Execution Completed")



        @pytest.mark.run(order=109)
        def test_109_At_Member_Properties__Configure_Email_Settings_with_From_Email_address_with_SMTP_and_Use_Authentication_are_Enabled_with_matched_password(self):
                logging.info("At Member level Override and Configure Email Settings with To Email,From Email Address configuration with SMTP and Use Authentication enabled with matched password with From Email Address")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1
                data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "dev@test.lab","relay_enabled": True,"relay": "10.35.141.10","smtps": True,"use_authentication": True,"password": "infoblox","port_number": 2525}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 109 Execution Completed")



        @pytest.mark.run(order=110)
        def test_110_Validate_Email_Settings_At_Member_Level_Configured_Configured_with_To_Email_and_FRom_Email_SMTP_and_use_authentication_is_enabled_with_password_for_From_Email_Address_with_port_number_2525_is_configured(self):
                logging.info("Validate at Member Level when Override and Email Settings with To Email Address and From Email Address are configured with SMTP RFE_9525_original.pyand  Use Authentication enabled with valid port number and matched Password for From Email Address ")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print res
                print ref1

                get_tacacsplus = ib_NIOS.wapi_request('GET', ref=ref1,params="?_return_fields=email_setting,use_email_setting")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                string = {"use_email_setting": True, "_ref": ref1, "email_setting": {"relay_enabled": True,"relay": "10.35.141.10", "enabled": True, "smtps": True, "port_number": 2525, "address": "rkarjagi@infoblox.com", "from_address": "dev@test.lab", "use_authentication": True}}

                if res == string:
                        assert True
                else:
                        assert False
                logging.info("Test Case 110 Execution Completed")
                logging.info("============================")



        @pytest.mark.run(order=111)
        def test_111_start_Syslog_Messages_logs_for_Member(self):
                logging.info("Starting Syslog Messages Logs for Member")
                log("start","/var/log/syslog",config.grid_member1_vip)


        @pytest.mark.run(order=112)
        def test_112_Stop_DNS_Service(self):
                logging.info("Start DNS Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1

                logging.info("Modify a enable_dns")
                data = {"enable_dns": False}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                sleep(40)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 112  Execution Completed")

        @pytest.mark.run(order=113)
        def test_113_stop_Syslog_Messages_Logs_for_Member(self):
                logging.info("Stopping Syslog Logs for Member")
                log("stop","/var/log/syslog",config.grid_member1_vip)
                print("Test Case 113 Execution Completed")


        @pytest.mark.run(order=114)
        def test_114_validate_Syslog_message_for_Creating_SSL_connection_to_host(self):
                logging.info("Validating Sylog Messages Logs for info Creating SSL connection to host")
                LookFor="\"info Creating SSL connection to host\""
                logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
                print("Test Case 114 Execution Completed")

        @pytest.mark.run(order=115)
        def test_115_validate_Syslog_message_for_SSL_connection_using_ECDHE_RSA_AES256_GCM_SHA384(self):
                logging.info("Validating Sylog Messages Logs for SSL connection using ECDHE-RSA-AES256-GCM-SHA384")
                LookFor="\"SSL connection using ECDHE-RSA-AES256-GCM-SHA384\""
                logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
                print("Test Case 115 Execution Completed")



        @pytest.mark.run(order=116)
        def test_116_validate_Syslog_Messages_for_Sent_Mail_for(self):
                logging.info("Validating Sylog Messages Logs")
                LookFor="\"Sent mail for dev@test.lab\""
                logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
                print("Test Case 116 Execution Completed")





        @pytest.mark.run(order=117)
        def test_117_At_Member_Properties_Inherit_Email_Settings_From_the_Grid_Level(self):
                logging.info("At Member level inherit Email Settings from the Grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1
                data = {"use_email_setting": False}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 117 Execution Completed")


        @pytest.mark.run(order=118)
        def test_118_Validate_Email_Settings_At_Member_Level_when_Email_settings_are_Inherited_from_Grid(self):
                logging.info("Validate at Member Level Email Settings are inherrited from the Grid  level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print res
                print ref1

                get_tacacsplus = ib_NIOS.wapi_request('GET', ref=ref1,params="?_return_fields=email_setting,use_email_setting")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                string = {"use_email_setting": False, "_ref": ref1,"email_setting": {"address": "rkarjagi@infoblox.com","from_address": "dev@test.lab","relay": "10.35.141.10","relay_enabled": True, "port_number": 2525, "use_authentication": True, "enabled": True, "smtps": True}}
                if res == string:
                        assert True
                else:
                        assert False
                logging.info("Test Case 118 Execution Completed")
                logging.info("============================")




        @pytest.mark.run(order=119)
        def test_119_start_Syslog_Messages_logs(self):
                logging.info("Starting Syslog Messages Logs")
                log("start","/var/log/syslog",config.grid_member1_vip)


        @pytest.mark.run(order=120)
        def test_120_Start_DNS_Service(self):
                logging.info("Start DNS Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1

                logging.info("Modify a enable_dns")
                data = {"enable_dns": True}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                sleep(40)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 120  Execution Completed")


        @pytest.mark.run(order=121)
        def test_121_stop_Syslog_Messages_Logs(self):
                logging.info("Stopping Syslog Logs")
                log("stop","/var/log/syslog",config.grid_member1_vip)
                print("Test Case 121 Execution Completed")


        @pytest.mark.run(order=122)
        def test_122_validate_Syslog_message_for_Creating_SSL_connection_to_host(self):
                logging.info("Validating Sylog Messages Logs for info Creating SSL connection to host")
                LookFor="\"info Creating SSL connection to host\""
                logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
                print("Test Case 65 Execution Completed")

        @pytest.mark.run(order=123)
        def test_123_validate_Syslog_message_for_SSL_connection_using_ECDHE_RSA_AES256_GCM_SHA384(self):
                logging.info("Validating Sylog Messages Logs for SSL connection using ECDHE-RSA-AES256-GCM-SHA384")
                LookFor="\"SSL connection using ECDHE-RSA-AES256-GCM-SHA384\""
                logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
                print("Test Case 123 Execution Completed")


        @pytest.mark.run(order=124)
        def test_124_validate_Syslog_Messages_for_Sent_Mail_for(self):
                logging.info("Validating Sylog Messages Logs")
                LookFor="\"Sent mail for qa@test.lab\""
                logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
                print("Test Case 124 Execution Completed")



        @pytest.mark.run(order=125)
        def test_125_At_Member_Properties_Just_Override_Email_Settings(self):
                logging.info("At Member level just Override  Email Settings")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1
                data = {"use_email_setting": True}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 225 Execution Completed")


        @pytest.mark.run(order=126)
        def test_126_Validate_Email_Settings_At_Member_Level_when_Email_settings_is_just_Override_and_validated_Previous_values_shown(self):
                logging.info("Validate at Member Level Email Settings are are shown previous value when just clicked on override")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print res
                print ref1

                get_tacacsplus = ib_NIOS.wapi_request('GET', ref=ref1,params="?_return_fields=email_setting,use_email_setting")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                string = {"use_email_setting": True, "_ref": ref1,"email_setting": {"address": "rkarjagi@infoblox.com","from_address": "dev@test.lab","relay": "10.35.141.10","relay_enabled": True, "port_number": 2525, "use_authentication": True, "enabled": True, "smtps": True}}
                if res == string:
                        assert True
                else:
                        assert False
                logging.info("Test Case 126 Execution Completed")
                logging.info("============================")




        @pytest.mark.run(order=127)
        def test_127_start_Syslog_Messages_logs(self):
                logging.info("Starting Syslog Messages Logs")
                log("start","/var/log/syslog",config.grid_member1_vip)


        @pytest.mark.run(order=128)
        def test_128_Stop_DNS_Service(self):
                logging.info("Stop DNS Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print ref1

                logging.info("Modify a enable_dns")
                data = {"enable_dns": False}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                sleep(40)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 128  Execution Completed")


        @pytest.mark.run(order=129)
        def test_129_stop_Syslog_Messages_Logs(self):
                logging.info("Stopping Syslog Logs")
                log("stop","/var/log/syslog",config.grid_member1_vip)
                print("Test Case 129 Execution Completed")


        @pytest.mark.run(order=130)
        def test_130_validate_Syslog_message_for_Creating_SSL_connection_to_host(self):
                logging.info("Validating Sylog Messages Logs for info Creating SSL connection to host")
                LookFor="\"info Creating SSL connection to host\""
                logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
                print("Test Case 130 Execution Completed")

        @pytest.mark.run(order=131)
        def test_131_validate_Syslog_message_for_SSL_connection_using_ECDHE_RSA_AES256_GCM_SHA384(self):
                logging.info("Validating Sylog Messages Logs for SSL connection using ECDHE-RSA-AES256-GCM-SHA384")
                LookFor="\"SSL connection using ECDHE-RSA-AES256-GCM-SHA384\""
                logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
                print("Test Case 131 Execution Completed")


        @pytest.mark.run(order=132)
        def test_132_validate_Syslog_Messages_for_Sent_Mail_for(self):
                logging.info("Validating Sylog Messages Logs")
                LookFor="\"Sent mail for dev@test.lab\""
                logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
                print("Test Case 132 Execution Completed")



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

class RFE_1027(unittest.TestCase):

        @pytest.mark.run(order=1)
        def test_1_Start_DNS_Service(self):
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
                logging.info("Test Case 1 Execution Completed")

        @pytest.mark.run(order=2)
        def test_2_Validate_DNS_service_Enabled(self):
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
        def test_3_Modify_Grid_Properties_To_Configure_DNS_Resolver(self):
                logging.info("Configure DNS Resolver at Grid Level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"dns_resolver_setting": {"resolvers": ["10.0.2.35"]}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 1 Execution Completed")


        @pytest.mark.run(order=4)
        def test_4_Modify_Grid_Properties_To_Configure_Email_Notification(self):
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

        @pytest.mark.run(order=5)
        def test_5_Modify_Grid_Properties_To_Configure_Email_Settings_with_only_To_Email_address_and_From_Email_address_Is_Empty(self):
                logging.info("Enable Email Settings with Only To Email Address Configuration and From Email Address is Empty at Grid Level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": ""}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 1 Execution Completed")

        @pytest.mark.run(order=6)
        def test_6_Validate_Email_Settings_with_only_To_Email_address_and_From_Email_address_Is_Empty(self):
                logging.info("Validate Enable Email Settings with Only To Email Address Configuration and From Email Address is Empty at Grid Level")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="grid",params="?_return_fields=email_setting")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                string = {"email_setting": {"address": "rkarjagi@infoblox.com","enabled": True,"relay_enabled": False}}
                if res == string:
                	assert True
                #else:
                 #      	assert False

                logging.info("Test Case 3 Execution Completed")
                logging.info("============================")



        @pytest.mark.run(order=7)
        def test_7_Stop_DNS_Service(self):
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
                sleep(60)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 1 Execution Completed")


        @pytest.mark.run(order=8)
        def test_8_Validate_log_Message_for_logging_From_Email_address(self):
                logging.info("Validate log Messages or logging From Email Address")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /var/log/syslog | grep \'info Sent mail for no-reply@\'"'
                print sys_log_validation
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info("Test Case 10 Execution Completed")



        @pytest.mark.run(order=9)
        def test_9_Modify_Grid_Properties_To_Configure_Email_Settings_with_To_Email_address_and_From_Email_address(self):
                logging.info("Enable Email Settings with To Email Address Configuration and From Email Address at Grid Level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "admin123@infoblox.com"}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 1 Execution Completed")

        @pytest.mark.run(order=10)
        def test_10_Validate_Email_Settings_with_To_Email_address_and_From_Email_address_At_Grid_level(self):
                logging.info("Validate Enable Email Settings with To Email Address Configuration and From Email Address  at Grid Level")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="grid",params="?_return_fields=email_setting")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                string = {"email_setting": {"address": "rkarjagi@infoblox.com","from_address": "admin123@infoblox.com","enabled": True,"relay_enabled": False}}
                if res == string:
                        assert True
                #else:
                 #              assert False

                logging.info("Test Case 3 Execution Completed")
                logging.info("============================")



        @pytest.mark.run(order=11)
        def test_11_Start_DNS_Service(self):
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
                sleep(60)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 1 Execution Completed")


	@pytest.mark.run(order=12)
        def test_12_Validate_log_Message_for_logging_From_Email_address(self):
	        logging.info("Validate log Messages or logging From Email Address")
        	sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /var/log/syslog | grep \'info Sent mail for admin123@infoblox.com\'"'
		print sys_log_validation
       		out1 = commands.getoutput(sys_log_validation)
        	print out1
        	logging.info("Test Case 10 Execution Completed")

        @pytest.mark.run(order=13)
        def test_13_Modify_Grid_Properties_To_Configure_Email_Settings_with_To_Email_address_and_From_Email_address_AS_Invalid(self):
                logging.info("Enable Email Settings with To Email Address Configuration and From Email Address with Invalid value at Grid Level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "admin123@"}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"Error": "AdmConDataError: The email address\'s domain name is missing.", \n  "code": "Client.Ibap.Data", \n  "text": "The email address\'s domain name is missing."\n',response)
                logging.info("Test Case 1 Execution Completed")

        @pytest.mark.run(order=14)
        def test_14_Modify_Grid_Properties_To_Configure_Email_Settings_with_To_Email_address_and_From_Email_address_AS_Wrong_value(self):
                logging.info("Enable Email Settings with To Email Address Configuration and From Email Address with wrong value at Grid Level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "ddddd"}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Email address must have a name followed by \'@\'."',response)
                logging.info("Test Case 1 Execution Completed")


        @pytest.mark.run(order=15)
        def test_15_Modify_Member_Properties_Override_and__Configure_Email_Settings_with_To_Email_address_and_From_Email_address_AS_Wrong(self):
                logging.info("At Member level Override Enable Email Settings Configure To Email Address Configuration and From Email Address with Wrong value at member Level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "dddd"}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Email address must have a name followed by \'@\'."',response)

        @pytest.mark.run(order=15)
        def test_15_Modify_Member_Properties_Override_and__Configure_Email_Settings_with_To_Email_address_and_From_Email_address_AS_Wrong(self):
                logging.info("At Member level Override Enable Email Settings Configure To Email Address Configuration and From Email Address with Wrong value at member Level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "dddd"}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "Email address must have a name followed by \'@\'."',response)

        @pytest.mark.run(order=16)
        def test_16_Modify_Member_Properties_Override_and__Configure_Email_Settings_with_To_Email_address_and_From_Email_address_AS_Invalid(self):
                logging.info("At Member level Override Enable Email Settings Configure To Email Address Configuration and From Email Address with Invalid value at member Level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "admin@"}}
                status,response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                assert status ==400 and re.search(r'"text": "The email address\'s domain name is missing."',response)



        @pytest.mark.run(order=17)
        def test_17_Modify_Member_Properties_To_Configure_Email_Settings_with_only_To_Email_address_and_From_Email_address_Is_Empty(self):
                logging.info("At Member level Override and  Enable Email Enable Email Settings with Only To Email Address Configuration and From Email Address is Empty at Member Level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": ""}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 1 Execution Completed")

        @pytest.mark.run(order=18)
        def test_18_Validate_At_Member_Level_Email_Settings_with_only_To_Email_address_and_From_Email_address_Is_Empty(self):
                logging.info("Validate Enable Email Settings with Only To Email Address Configuration and From Email Address is Empty at Member Level")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member",params="?_return_fields=email_setting,use_email_setting")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                string = {"use_email_setting": True,"email_setting": {"address": "rkarjagi@infoblox.com","enabled": True,"relay_enabled": False}}
                if res == string:
                        assert True
                #else:
                 #              assert False

                logging.info("Test Case 3 Execution Completed")
                logging.info("============================")


        @pytest.mark.run(order=19)
        def test_19_Stop_DNS_Service(self):
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
                sleep(60)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 1 Execution Completed")


        @pytest.mark.run(order=20)
        def test_20_Validate_log_Message_for_logging_From_Email_address(self):
                logging.info("Validate log Messages or logging From Email Address")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /var/log/syslog | grep \'info Sent mail for no-reply@\'"'
                print sys_log_validation
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info("Test Case 10 Execution Completed")



        @pytest.mark.run(order=21)
        def test_21_Modify_Member_Properties_To_Configure_Email_Settings_with_To_Email_address_and_From_Email_address(self):
                logging.info("Override and Enable Email Settings with To Email Address Configuration and From Email Address at Member Level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"use_email_setting": True,"email_setting": {"enabled": True,"address": "rkarjagi@infoblox.com","from_address": "testing123@infoblox.com"}}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 1 Execution Completed")

        @pytest.mark.run(order=22)
        def test_22_Validate_Email_Settings_with_To_Email_address_and_From_Email_address_At_Member_level(self):
                logging.info("Validate Enable Email Settings with To Email Address Configuration and From Email Address  at Member Level")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member",params="?_return_fields=email_setting,use_email_setting")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                string = {"use_email_setting": True,"email_setting": {"address": "rkarjagi@infoblox.com","from_address": "testing123@infoblox.com","enabled": True,"relay_enabled": False}}
                if res == string:
                        assert True
                #else:
                 #              assert False

                logging.info("Test Case 3 Execution Completed")
                logging.info("============================")



        @pytest.mark.run(order=23)
        def test_23_Start_DNS_Service(self):
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
                sleep(60)
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Test Case 1 Execution Completed")


        @pytest.mark.run(order=24)
        def test_24_Validate_log_Message_for_logging_From_Email_address(self):
                logging.info("Validate log Messages or logging From Email Address")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -100 /var/log/syslog | grep \'info Sent mail for testing123@infoblox.com\'"'
                print sys_log_validation
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info("Test Case 10 Execution Completed")



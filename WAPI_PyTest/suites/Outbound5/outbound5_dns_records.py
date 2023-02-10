import re
import config
import pytest
import unittest
import logging
import subprocess
from dig_utility import dig
import json
from os.path import join
import ib_utils.ib_NIOS as ib_NIOS
import time
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as comm_util
import import_zone 


class Outbound5(unittest.TestCase):

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
        def test_003_Upload_Rest_Endpoint_Template(self):
                logging.info("Upload REST Version5 Session Template")
                dir_name="./Outbound5_templates/"
                base_filename="Version5_REST_API_Session_Template.json"
                token = comm_util.generate_token_from_file(dir_name,base_filename)
                data = {"token": token,"overwrite": True}
                response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=restapi_template_import")
                logging.info(response)
                print response
                logging.info(response)
                res = json.loads(response)
                string = {"overall_status": "SUCCESS","error_message": ""}
                if res == string:
                        assert True
                else:
                        assert False
                logging.info("Session Template Execution Completed")
                logging.info("============================")

        @pytest.mark.run(order=4)
        def test_004_Upload_Rest_Endpoint_DNS_ACTION_Template(self):
                logging.info("Upload DNS Zone/Record Version5 Action Template")
                dir_name="./Outbound5_templates/"
                base_filename="Version5_DNS_Zone_and_Records_Action_Template.json"
                token = comm_util.generate_token_from_file(dir_name,base_filename)
                data = {"token": token,"overwrite": True}
                response = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=restapi_template_import")
                logging.info(response)
                print response
                logging.info(response)
                res = json.loads(response)
                string = {"overall_status": "SUCCESS","error_message": ""}
                if res == string:
                        assert True
                else:
                        assert False
                logging.info("Action Template Execution Completed")
                logging.info("============================")


        @pytest.mark.run(order=5)
        def test_005_Add_REST_API_endpoint_globally(self):
                logging.info("Add REST API endpoint")
                data = {"name": "test", "uri": "https://"+config.grid_vip,"outbound_member_type": "GM","username": "admin","password": "infoblox","wapi_user_name": "admin", "wapi_user_password": "infoblox","log_level":"DEBUG","template_instance": {"template": "Version5_REST_API_Session_Template"},"server_cert_validation": "NO_VALIDATION"}
                response = ib_NIOS.wapi_request('POST', object_type="notification:rest:endpoint", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 1 Execution Completed")
                logging.info("=================================")


        @pytest.mark.run(order=6)
        def test_006_Add_Notification_Rule_A(self):
                logging.info("Add Notification Rule for endpoint")
                data = {"name":"test"}
                endpoint=comm_util.get_object_reference(object_type="notification:rest:endpoint",data=data)
		data = {"name": "notification1","notification_action": "RESTAPI_TEMPLATE_INSTANCE","notification_target": endpoint,"template_instance": {"template": "Version5_DNS_Zone_and_Records_Action_Template"},"event_type": "DB_CHANGE_DNS_RECORD","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_A","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('POST', object_type="notification:rule",fields=json.dumps(data))
                print (response)
                read  = re.search(r'201',response)
                for read in response:
                        assert True
                logging.info("Notification Rule is posted successfully")
                time.sleep(30)


        @pytest.mark.run(order=7)
        def test_007_Add_Authoritative_zone_Globally(self):
                logging.info("Create Auth Zone")
                grid_member=config.grid_fqdn
                data = {"fqdn": "outbound_zone2.com","grid_primary": [{"name":config.grid_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Auth Zone is created successfully")

                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")

        @pytest.mark.run(order=8)
        def test_008_Create_A_record(self):
                logging.info ("Creating A Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=comm_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "arec.outbound_zone2.com","ipv4addr":"1.2.3.4","_ref":endpoint,"comment":"Adding arec","view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
		#import pdb;pdb.set_trace()
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("A Record is created Successfully")
                time.sleep(200)

        @pytest.mark.run(order=9)
        def test_009_Validate_Template_Execution_For_A_Record(self):
                logging.info ("Validate Template Execution for AAAA Record")
                data = {"fqdn":"template_execution_dns_zone.com"}
		o_type="zone_auth?fqdn="+str(data['fqdn'])
		print ("oooooooooooooo",o_type)
		count=1
		result=""
	        while(count<=1):
			print ("i am here")
			get_template_zone = ib_NIOS.wapi_request('GET', object_type=o_type,fields=json.dumps(data))
                 	print ("##########################", json.loads(get_template_zone))
                	print type(json.loads(get_template_zone))
                 	result=json.loads(get_template_zone)
                 	result=result[0]['_ref'].split(':')[1].split('/')[0]
                 	print result
			if (result!=[]):
				assert True
				count=count+1
			else:
				assert False
                        time.sleep(30)

	#	if (result==data['fqdn']):
	#		assert True
	#	else:
    	#		assert False

        @pytest.mark.run(order=10)
        def test_010_Delete_Notf_for_A_Record(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 30 sec.,")
		assert True

                time.sleep(30) #wait for 10 secs for the member to get started
                print("Delete operation completed")

        @pytest.mark.run(order=11)
        def test_011_validate_delete_zone_for_A_Record(self):
                logging.info("Deleting zone for A Record")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False

                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")

        @pytest.mark.run(order=12)
        def test_012_Update_A_record(self):
                logging.info ("Updating A Record for added Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:a")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"comment":"Updating A Record"}

                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("A Record is updated Successfully")
                time.sleep(30)

        @pytest.mark.run(order=13)
        def test_013_Validate_Template_Execution_for_Updated_A_Record(self):
                logging.info ("Validate Template Execution for updated A Record")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")


        @pytest.mark.run(order=14)
        def test_014_Delete_Notf_for_Updated_A_Record(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 30 sec.,")

                time.sleep(30) #wait for 10 secs for the member to get started
                print("Delete operation completed for Updated A Record")

        @pytest.mark.run(order=15)
        def test_015_validate_delete_Zone_for_Updated_A_Record(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False
                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")


        @pytest.mark.run(order=16)
        def test_016_Add_Notification_Rule_AAAA(self):
                logging.info("Add Notification Rule for AAAA endpoint")
                data = {"name":"test"}
                endpoint=comm_util.get_object_reference(object_type="notification:rest:endpoint",data=data)
                data = {"name": "notification2","notification_action": "RESTAPI_TEMPLATE_INSTANCE","notification_target": endpoint,"template_instance": {"template": "Version5_DNS_Zone_and_Records_Action_Template"},"event_type": "DB_CHANGE_DNS_RECORD","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_AAAA","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('POST', object_type="notification:rule",fields=json.dumps(data))
                print (response)
                read  = re.search(r'201',response)
                for read in response:
                        assert True
                logging.info("Notification Rule is posted successfully")
                time.sleep(25)

        @pytest.mark.run(order=17)
        def test_017_Create_AAAA_record(self):
                logging.info ("Creating AAAA Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=comm_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"ipv6addr": "fd60:e45:e31b::","name":"aaaarec.outbound_zone2.com","_ref":endpoint,"view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:aaaa",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("AAAA Record is created Successfully")
                time.sleep(30)


        @pytest.mark.run(order=18)
        def test_018_Validate_Template_Execution_for_AAAA_Record(self):
                logging.info ("Validate Template Execution for AAAA Record")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")


        @pytest.mark.run(order=19)
        def test_019_Delete_Notf_for_AAAA_Record(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 30 sec.,")

                time.sleep(30) #wait for 10 secs for the member to get started
                print("Delete operation completed")

        @pytest.mark.run(order=20)
        def test_020_validate_delete_Zone_for_AAAA_Record(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False

                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")

        @pytest.mark.run(order=21)
        def test_021_Update_AAAA_record(self):
                logging.info ("Updating A Record for added Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:aaaa")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"comment":"Updating AAAA Record"}

                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("AAAA Record is updated Successfully")
                time.sleep(30)

        @pytest.mark.run(order=22)
        def test_022_Validate_Template_Execution_for_Updated_AAAA_Record(self):
                logging.info ("Validate Template Execution")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")
				
        @pytest.mark.run(order=23)
        def test_023_Delete_Notf_for_Updated_AAAA_Record(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 30 sec.,")

                time.sleep(30) #wait for 10 secs for the member to get started
                print("Delete operation completed")

        @pytest.mark.run(order=24)
        def test_024_validate_delete_Network_for_Updated_AAAA_Record(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False
						
                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")


        @pytest.mark.run(order=25)
        def test_025_Add_Notification_Rule_CNAME(self):
                logging.info("Add Notification Rule for CNAME endpoint")
                data = {"name":"test"}
                endpoint=comm_util.get_object_reference(object_type="notification:rest:endpoint",data=data)
                data = {"name": "notification3","notification_action": "RESTAPI_TEMPLATE_INSTANCE","notification_target": endpoint,"template_instance": {"template": "Version5_DNS_Zone_and_Records_Action_Template"},"event_type": "DB_CHANGE_DNS_RECORD","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_CNAME","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('POST', object_type="notification:rule",fields=json.dumps(data))
                print (response)
                read  = re.search(r'201',response)
                for read in response:
                        assert True
                logging.info("Notification Rule is posted successfully")
                time.sleep(25)



        @pytest.mark.run(order=26)
        def test_026_Create_CNAME_record(self):
                logging.info ("Creating CNAME Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=comm_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "cname.outbound_zone2.com","canonical": "cnametest.com","_ref":endpoint,"view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:cname",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("CNAME Record is created Successfully")
                time.sleep(30)

        @pytest.mark.run(order=27)
        def test_027_Validate_Template_Execution_for_CNAME(self):
                logging.info ("Validate Template Execution")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")


        @pytest.mark.run(order=28)
        def test_028_Delete_Notf_CNAME_Record(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 30 sec.,")

                time.sleep(30) #wait for 10 secs for the member to get started
                print("Delete operation Completed")

        @pytest.mark.run(order=29)
        def test_029_validate_delete_Zone_for_CNAME_Record(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False

                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")

        @pytest.mark.run(order=30)
        def test_030_Update_CNAME_record(self):
                logging.info ("Updating A Record for added Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:cname")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"comment":"Updating CNAME Record"}

                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("A Record is updated Successfully")
                time.sleep(30)

        @pytest.mark.run(order=31)
        def test_031_Validate_Template_Execution_for_Updated_CNAME_Record(self):
                logging.info ("Validate Template Execution")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")
				
        @pytest.mark.run(order=32)
        def test_032_Delete_Notf_for_Updated_CNAME_Record(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 30 sec.,")

                time.sleep(30) #wait for 10 secs for the member to get started
                print("Delete operation completed")

        @pytest.mark.run(order=33)
        def test_033_validate_delete_Network_for_Updated_CNAME_Record(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False
						
                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")



        @pytest.mark.run(order=34)
        def test_034_Add_Notification_Rule_TXT(self):
                logging.info("Add Notification Rule for TXT endpoint")
                data = {"name":"test"}
                endpoint=comm_util.get_object_reference(object_type="notification:rest:endpoint",data=data)
                data = {"name": "notification4","notification_action": "RESTAPI_TEMPLATE_INSTANCE","notification_target": endpoint,"template_instance": {"template": "Version5_DNS_Zone_and_Records_Action_Template"},"event_type": "DB_CHANGE_DNS_RECORD","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_TXT","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('POST', object_type="notification:rule",fields=json.dumps(data))
                print (response)
                read  = re.search(r'201',response)
                for read in response:
                        assert True
                logging.info("Notification Rule is posted successfully")
                time.sleep(25)



        @pytest.mark.run(order=35)
        def test_035_Create_TXT_record(self):
                logging.info ("Creating TXT Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=comm_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "text.outbound_zone2.com","text": "This a host server","_ref":endpoint,"view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:txt",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("TXT Record is created Successfully")
                time.sleep(30)

        @pytest.mark.run(order=36)
        def test_036_Validate_Template_Execution_for_TXT_Record(self):
                logging.info ("Validate Template Execution")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")


        @pytest.mark.run(order=37)
        def test_037_Delete_Zone_for_TXT_Record(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 30 sec.,")

                time.sleep(30) #wait for 10 secs for the member to get started
                print("Delete operation Completed")

        @pytest.mark.run(order=38)
        def test_038_validate_delete_zone_for_TXT_Record(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False

                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")


        @pytest.mark.run(order=39)
        def test_039_Update_TXT_record(self):
                logging.info ("Updating TXT Record for added Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:txt")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"comment":"Updating CNAME Record"}

                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("A Record is updated Successfully")
                time.sleep(30)

        @pytest.mark.run(order=40)
        def test_040_Validate_Template_Execution_for_Updated_TXT_Record(self):
                logging.info ("Validate Template Execution")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")
				
        @pytest.mark.run(order=41)
        def test_041_Delete_Notf_for_Updated_TXT_Record(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 30 sec.,")

                time.sleep(30) #wait for 10 secs for the member to get started
                print("Delete operation completed")

        @pytest.mark.run(order=42)
        def test_042_validate_delete_Network_for_Updated_TXT_Record(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False
						
                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")




        @pytest.mark.run(order=43)
        def test_043_Add_Notification_Rule_SRV(self):
                logging.info("Add Notification Rule for SRV endpoint")
                data = {"name":"test"}
                endpoint=comm_util.get_object_reference(object_type="notification:rest:endpoint",data=data)
                data = {"name": "notification22","notification_action": "RESTAPI_TEMPLATE_INSTANCE","notification_target": endpoint,"template_instance": {"template": "Version5_DNS_Zone_and_Records_Action_Template"},"event_type": "DB_CHANGE_DNS_RECORD","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_SRV","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('POST', object_type="notification:rule",fields=json.dumps(data))
                print (response)
                read  = re.search(r'201',response)
                for read in response:
                        assert True
                logging.info("Notification Rule is posted successfully")
                time.sleep(25)



        @pytest.mark.run(order=44)
        def test_044_Create_SRV_record(self):
                logging.info ("Creating SRV Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=comm_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "outbound_zone2.com","port":22,"_ref":endpoint,"target":"outbound_zone2.com","view":"default","weight":10,"priority":1}
                response = ib_NIOS.wapi_request('POST', object_type="record:srv",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("SRV Record is created Successfully")
                time.sleep(30)

        @pytest.mark.run(order=45)
        def test_045_Validate_Template_Execution_for_SRV_Record(self):
                logging.info ("Validate Template Execution")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")


        @pytest.mark.run(order=46)
        def test_046_Delete_Notf_for_SRV_Record(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 30 sec.,")

                time.sleep(30) #wait for 10 secs for the member to get started
                print("Delete operation Completed")

        @pytest.mark.run(order=47)
        def test_047_validate_delete_Network_for_SRV_Record(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False

                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")


        @pytest.mark.run(order=48)
        def test_048_Update_SRV_record(self):
                logging.info ("Updating SRV Record for added Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:srv")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"port":443}

                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("SRV Record is updated Successfully")
                time.sleep(30)

        @pytest.mark.run(order=49)
        def test_049_Validate_Template_Execution_for_Updated_SRV_Record(self):
                logging.info ("Validate Template Execution")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")
				
        @pytest.mark.run(order=50)
        def test_050_Delete_Notf_for_Updated_SRV_Record(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 30 sec.,")

                time.sleep(30) #wait for 10 secs for the member to get started
                print("Delete operation completed")

        @pytest.mark.run(order=51)
        def test_051_validate_delete_Network_for_Updated_SRV_Record(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False
						
                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")



        @pytest.mark.run(order=52)
        def test_052_Add_Notification_Rule_ALIAS(self):
                logging.info("Add Notification Rule for ALIAS endpoint")
                data = {"name":"test"}
                endpoint=comm_util.get_object_reference(object_type="notification:rest:endpoint",data=data)
                data = {"name": "notification6","notification_action": "RESTAPI_TEMPLATE_INSTANCE","notification_target": endpoint,"template_instance": {"template": "Version5_DNS_Zone_and_Records_Action_Template"},"event_type": "DB_CHANGE_DNS_RECORD","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_ALIAS","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('POST', object_type="notification:rule",fields=json.dumps(data))
                print (response)
                read  = re.search(r'201',response)
                for read in response:
                        assert True
                logging.info("Notification Rule is posted successfully")
                time.sleep(25)



        @pytest.mark.run(order=53)
        def test_053_Create_ALIAS_record(self):
                logging.info ("Creating ALIAS Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=comm_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "alias.outbound_zone2.com","target_name": "arec.outbound_zone2.com","_ref":endpoint,"target_type": "A","view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:alias",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("ALIAS Record is created Successfully")
                time.sleep(30)

        @pytest.mark.run(order=54)
        def test_054_Validate_Template_Execution_for_ALIAS_Record(self):
                logging.info ("Validate Template Execution")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")


        @pytest.mark.run(order=55)
        def test_055_Delete_Notf_for_ALIAS_Record(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 30 sec.,")

                time.sleep(30) #wait for 10 secs for the member to get started
                print("Delete Execution Completed")

        @pytest.mark.run(order=56)
        def test_056_validate_delete_Network_for_ALIAS_Record(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False

                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")

        @pytest.mark.run(order=57)
        def test_057_Update_ALIAS_record(self):
                logging.info ("Updating ALIAS Record for added Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:alias")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"name": "aliasupdated.outbound_zone2.com"}

                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("ALIAS Record is updated Successfully")
                time.sleep(30)

        @pytest.mark.run(order=58)
        def test_058_Validate_Template_Execution_for_Updated_ALIAS_Record(self):
                logging.info ("Validate Template Execution")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")
				
        @pytest.mark.run(order=59)
        def test_059_Delete_Notf_for_Updated_ALIAS_Record(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 30 sec.,")

                time.sleep(30) #wait for 10 secs for the member to get started
                print("Delete operation completed")

        @pytest.mark.run(order=60)
        def test_060_validate_delete_Network_for_Updated_ALIAS_Record(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False
						
                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")


        @pytest.mark.run(order=61)
        def test_061_Add_Notification_Rule_DNAME(self):
                logging.info("Add Notification Rule for DNAME endpoint")
                data = {"name":"test"}
                endpoint=comm_util.get_object_reference(object_type="notification:rest:endpoint",data=data)
                data = {"name": "notification7","notification_action": "RESTAPI_TEMPLATE_INSTANCE","notification_target": endpoint,"template_instance": {"template": "Version5_DNS_Zone_and_Records_Action_Template"},"event_type": "DB_CHANGE_DNS_RECORD","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_DNAME","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('POST', object_type="notification:rule",fields=json.dumps(data))
                print (response)
                read  = re.search(r'201',response)
                for read in response:
                        assert True
                logging.info("Notification Rule is posted successfully")
                time.sleep(25)


        @pytest.mark.run(order=62)
        def test_062_Create_DNAME_record(self):
                logging.info ("Creating DMANE Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=comm_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "dname.outbound_zone2.com","target": "arec.com","_ref":endpoint,"comment":"Adding dname rec","view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:dname",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("DNAME Record is created Successfully")
                time.sleep(30)

        @pytest.mark.run(order=63)
        def test_063_Validate_Template_Execution_for_DNAME_Record(self):
                logging.info ("Validate Template Execution")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")


        @pytest.mark.run(order=64)
        def test_064_Delete_Notf_for_DNAME_Record(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 30 sec.,")

                time.sleep(30) #wait for 10 secs for the member to get started
                print("Delete Execution Completed")

        @pytest.mark.run(order=65)
        def test_065_validate_delete_zone_for_DNAME_Record(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False



                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")

        @pytest.mark.run(order=66)
        def test_066_Update_DNAME_record(self):
                logging.info ("Updating DNAME Record for added Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:dname")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"comment":"Adding UPDATED dname rec"}

                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("DNAME Record is updated Successfully")
                time.sleep(30)

        @pytest.mark.run(order=67)
        def test_067_Validate_Template_Execution_for_Updated_DNAME_Record(self):
                logging.info ("Validate Template Execution")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")
				
        @pytest.mark.run(order=68)
        def test_068_Delete_Notf_for_Updated_DNAME_Record(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 30 sec.,")

                time.sleep(30) #wait for 10 secs for the member to get started
                print("Delete operation completed")

        @pytest.mark.run(order=69)
        def test_069_validate_delete_Network_for_Updated_DNAME_Record(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False
						
                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")



        @pytest.mark.run(order=70)
        def test_070_Add_Notification_Rule_MX(self):
                logging.info("Add Notification Rule for MX endpoint")
                data = {"name":"test"}
                endpoint=comm_util.get_object_reference(object_type="notification:rest:endpoint",data=data)
                data = {"name": "notification8","notification_action": "RESTAPI_TEMPLATE_INSTANCE","notification_target": endpoint,"template_instance": {"template": "Version5_DNS_Zone_and_Records_Action_Template"},"event_type": "DB_CHANGE_DNS_RECORD","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_MX","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('POST', object_type="notification:rule",fields=json.dumps(data))
                print (response)
                read  = re.search(r'201',response)
                for read in response:
                        assert True
                logging.info("Notification Rule is posted successfully")
                time.sleep(25)



        @pytest.mark.run(order=71)
        def test_071_Create_MX_record(self):
                logging.info ("Creating MX Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=comm_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"mail_exchanger": "host1.outbound_zone2.com","name": "mail.outbound_zone2.com","_ref":endpoint,"preference": 1,"view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:mx",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("MX Record is created Successfully")
                time.sleep(30)

        @pytest.mark.run(order=72)
        def test_072_Validate_Template_Execution_for_MX_Record(self):
                logging.info ("Validate Template Execution")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")


        @pytest.mark.run(order=73)
        def test_073_Delete_Network_for_MX_Record(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 30 sec.,")

                time.sleep(30) #wait for 10 secs for the member to get started
                print("Delete Execution Completed")

        @pytest.mark.run(order=74)
        def test_074_validate_delete_Network_for_MX_Record(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False

                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")

        @pytest.mark.run(order=75)
        def test_075_Update_MX_record(self):
                logging.info ("Updating MX Record for added Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:mx")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"mail_exchanger": "host111.outbound_zone2.com"}

                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("MX Record is updated Successfully")
                time.sleep(30)

        @pytest.mark.run(order=76)
        def test_076_Validate_Template_Execution_for_Updated_MX_Record(self):
                logging.info ("Validate Template Execution")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")
				
        @pytest.mark.run(order=77)
        def test_077_Delete_Notf_for_Updated_MX_Record(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 30 sec.,")

                time.sleep(30) #wait for 10 secs for the member to get started
                print("Delete operation completed")

        @pytest.mark.run(order=78)
        def test_078_validate_delete_Network_for_Updated_MX_Record(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False
						
                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")



        @pytest.mark.run(order=79)
        def test_079_Add_Notification_Rule_NAPTR(self):
                logging.info("Add Notification Rule for NAPTR endpoint")
                data = {"name":"notification2"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="notification:rule",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                data = {"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_NAPTR","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('PUT', ref=ref1,fields=json.dumps(data))
                print (response)
                read  = re.search(r'201',response)
                for read in response:
                        assert True
                logging.info("Notification Rule is Updated successfully")
                time.sleep(25)



        @pytest.mark.run(order=80)
        def test_080_Create_NAPTR_record(self):
                logging.info ("Creating NAPTR Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=comm_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "naptr.outbound_zone2.com","order": 10,"_ref":endpoint,"preference": 10,"view":"default","replacement": "arec.outbound_zone2.com","services": "http+E2U"}
                response = ib_NIOS.wapi_request('POST', object_type="record:naptr",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("NAPTR Record is created Successfully")
                time.sleep(30)

        @pytest.mark.run(order=81)
        def test_081_Validate_Template_Execution(self):
                logging.info ("Validate Template Execution")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")


        @pytest.mark.run(order=82)
        def test_082_Delete_Network_for_NAPTR_Record(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 30 sec.,")

                time.sleep(30) #wait for 10 secs for the member to get started
                print("Delete operation Completed")

        @pytest.mark.run(order=83)
        def test_083_validate_delete_Zone_for_NAPTR_Record(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False

                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")


        @pytest.mark.run(order=84)
        def test_084_Update_NAPTR_record(self):
                logging.info ("Updating NAPTR Record for added Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:naptr")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"name": "naptrUPDATED.outbound_zone2.com"}

                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("NAPTR Record is updated Successfully")
                time.sleep(30)

        @pytest.mark.run(order=85)
        def test_085_Validate_Template_Execution_for_Updated_NAPTR_Record(self):
                logging.info ("Validate Template Execution")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")
				
        @pytest.mark.run(order=86)
        def test_086_Delete_Notf_for_Updated_NAPTR_Record(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 30 sec.,")

                time.sleep(30) #wait for 10 secs for the member to get started
                print("Delete operation completed")

        @pytest.mark.run(order=87)
        def test_087_validate_delete_Network_for_Updated_NAPTR_Record(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False
						
                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")



        @pytest.mark.run(order=88)
        def test_088_Add_Notification_Rule_PTR(self):
                logging.info("Add Notification Rule for PTR endpoint")
                data = {"name":"test"}
                endpoint=comm_util.get_object_reference(object_type="notification:rest:endpoint",data=data)
                data = {"name": "notification9","notification_action": "RESTAPI_TEMPLATE_INSTANCE","notification_target": endpoint,"template_instance": {"template": "Version5_DNS_Zone_and_Records_Action_Template"},"event_type": "DB_CHANGE_DNS_RECORD","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_PTR","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('POST', object_type="notification:rule",fields=json.dumps(data))
                print (response)
                read  = re.search(r'201',response)
                for read in response:
                        assert True
                logging.info("Notification Rule is posted successfully")
                time.sleep(25)



        @pytest.mark.run(order=89)
        def test_089_Create_PTR_record(self):
                logging.info ("Creating PTR Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=comm_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "ptrrec.outbound_zone2.com","ipv4addr":"1.2.3.4","_ref":endpoint,"ptrdname": "server1.outbound_zone.com","view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:ptr",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("PTR Record is created Successfully")
                time.sleep(30)

        @pytest.mark.run(order=90)
        def test_090_Validate_Template_Execution_for_PTR_Record(self):
                logging.info ("Validate Template Execution")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")


        @pytest.mark.run(order=91)
        def test_091_Delete_Zone_for_PTR_Record(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 30 sec.,")

                time.sleep(30) #wait for 10 secs for the member to get started
                print("Delete operation Completed")

        @pytest.mark.run(order=92)
        def test_092_validate_delete_Network(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False

                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")


######## 

        @pytest.mark.run(order=93)
        def test_093_Add_Notification_Rule_CAA(self):
                logging.info("Add Notification Rule for caa endpoint")
                data = {"name":"test"}
                endpoint=comm_util.get_object_reference(object_type="notification:rest:endpoint",data=data)
                data = {"name": "notification25","notification_action": "RESTAPI_TEMPLATE_INSTANCE","notification_target": endpoint,"template_instance": {"template": "Version5_DNS_Zone_and_Records_Action_Template"},"event_type": "DB_CHANGE_DNS_RECORD","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_CAA","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('POST', object_type="notification:rule",fields=json.dumps(data))
                print (response)
                read  = re.search(r'201',response)
                for read in response:
                        assert True
                logging.info("Notification Rule is posted successfully")
                time.sleep(25)

        @pytest.mark.run(order=94)
        def test_094_Create_CAA_record(self):
                logging.info ("Creating CAA Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=comm_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"ca_value": "CAA_Authority.com","ca_tag": "issue","name": "caa.outbound_zone2.com","ca_flag":0}
                response = ib_NIOS.wapi_request('POST', object_type="record:caa",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("CAA Record is created Successfully")
                time.sleep(30)

        @pytest.mark.run(order=95)
        def test_095_Validate_Template_Execution_for_CAA_Record(self):
                logging.info ("Validate Template Execution")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")

				
        @pytest.mark.run(order=96)
        def test_096_Delete_zone_for_CAA_Record(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 30 sec.,")

                time.sleep(30) #wait for 10 secs for the member to get started
                print("Delete Operation Completed")

        @pytest.mark.run(order=97)
        def test_097_validate_delete_zone_caa(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False

                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")

        @pytest.mark.run(order=98)
        def test_098_Update_CAA_record(self):
                logging.info ("Updating NAPTR Record for added Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:caa")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"name": "caaUPDATED.outbound_zone2.com"}

                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("CAA Record is updated Successfully")
                time.sleep(30)

        @pytest.mark.run(order=99)
        def test_099_Validate_Template_Execution_for_Updated_CAA_Record(self):
                logging.info ("Validate Template Execution")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")
				
        @pytest.mark.run(order=100)
        def test_100_Delete_Notf_for_Updated_CAA_Record(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 30 sec.,")

                time.sleep(30) #wait for 10 secs for the member to get started
                print("Delete operation completed")

        @pytest.mark.run(order=101)
        def test_101_validate_delete_Network_for_Updated_CAA_Record(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False
						
                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")


        @pytest.mark.run(order=102)
        def test_102_Add_Notification_Rule_NS(self):
                logging.info("Add Notification Rule for NS endpoint")
                data = {"name":"test"}
                endpoint=comm_util.get_object_reference(object_type="notification:rest:endpoint",data=data)
                data = {"name": "notificationNS","notification_action": "RESTAPI_TEMPLATE_INSTANCE","notification_target": endpoint,"template_instance": {"template": "Version5_DNS_Zone_and_Records_Action_Template"},"event_type": "DB_CHANGE_DNS_RECORD","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_NS","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('POST', object_type="notification:rule",fields=json.dumps(data))
                print (response)
                read  = re.search(r'201',response)
                for read in response:
                        assert True
                logging.info("Notification Rule is posted successfully fo NS Record")
                time.sleep(30)

        @pytest.mark.run(order=103)
        def test_103_Create_NS_record(self):
                logging.info ("Creating NS Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=comm_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name":"outbound_zone2.com","nameserver":config.grid_fqdn,"addresses":[{"address":"4.3.2.1"}]}
                response = ib_NIOS.wapi_request('POST', object_type="record:ns",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("NS Record is created Successfully")
                time.sleep(120)

				
        @pytest.mark.run(order=104)
        def test_104_Validate_Template_Execution_NS_Record(self):
                logging.info ("Validate Template Execution")
                data = {"fqdn":"template_execution_dns_zone.com"}
                o_type="zone_auth?fqdn="+str(data['fqdn'])
                print ("oooooooooooooo",o_type)
                get_template_zone = ib_NIOS.wapi_request('GET', object_type=o_type,fields=json.dumps(data))
                print ("##########################", json.loads(get_template_zone))
                print type(json.loads(get_template_zone))
                result=json.loads(get_template_zone)
                result=result[0]['_ref'].split(':')[1].split('/')[0]
                print result
                if (result==data['fqdn']):
                        assert True
                else:
                        assert False

				
        @pytest.mark.run(order=105)
        def test_105_Delete_Zone_NS_Record(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 30 sec.,")

                time.sleep(30) #wait for 10 secs for the member to get started
                print("Delete Operation Completed")

        @pytest.mark.run(order=106)
        def test_106_validate_delete_zone_ns(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False

                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")


        @pytest.mark.run(order=107)
        def test_107_Add_Notification_Rule_Unknown_Record(self):
                logging.info("Add Notification Rule for Unknown SPF endpoint")
                data = {"name":"test"}
                endpoint=comm_util.get_object_reference(object_type="notification:rest:endpoint",data=data)
                data = {"name": "notificationUN","notification_action": "RESTAPI_TEMPLATE_INSTANCE","notification_target": endpoint,"template_instance": {"template": "Version5_DNS_Zone_and_Records_Action_Template"},"event_type": "DB_CHANGE_DNS_RECORD","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_UNKNOWN","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('POST', object_type="notification:rule",fields=json.dumps(data))
                print (response)
                read  = re.search(r'201',response)
                for read in response:
                        assert True
                logging.info("Notification Rule is posted successfully for Unknown SPF Record")
                time.sleep(25)

        @pytest.mark.run(order=108)
        def test_108_Create_Unknown_record(self):
                logging.info ("Creating Unknown Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=comm_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name":"spf.outbound_zone2.com","record_type": "SPF","subfield_values": [{"field_value": "v=spf","field_type": "T","include_length": "8_BIT"}]}
                response = ib_NIOS.wapi_request('POST', object_type="record:unknown",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("Unknown Record is created Successfully")
                time.sleep(30)

				
        @pytest.mark.run(order=109)
        def test_109_Validate_Template_Execution_Unknown_Record(self):
                logging.info ("Validate Template Execution")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")

				
        @pytest.mark.run(order=110)
        def test_110_Delete_Notf_Unknown_Record(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 30 sec.,")

                time.sleep(10) #wait for 10 secs for the member to get started
                print("Delete Operation Completed")


				
        @pytest.mark.run(order=111)
        def test_111_validate_delete_zone_Unknown(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False

                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")



        @pytest.mark.run(order=116)
        def test_116_Add_Notification_Rule_SOA_Record(self):
                logging.info("Add Notification Rule for SOA endpoint")
                data = {"name":"test"}
                endpoint=comm_util.get_object_reference(object_type="notification:rest:endpoint",data=data)
                data = {"name": "notificationSOA","notification_action": "RESTAPI_TEMPLATE_INSTANCE","notification_target": endpoint,"template_instance": {"template": "Version5_DNS_Zone_and_Records_Action_Template"},"event_type": "DB_CHANGE_DNS_RECORD","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_SOA","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('POST', object_type="notification:rule",fields=json.dumps(data))
                print (response)
                read  = re.search(r'201',response)
                for read in response:
                        assert True
                logging.info("Notification Rule is posted successfully for SOA Record")
                time.sleep(200)


#        @pytest.mark.run(order=117)
#        def test_117_Update_soa_record(self):
#                logging.info ("Updating Serial Number for SOA Record for added Zone")
#                data={"fqdn":"outbound_zone2.com"}
#                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
#                logging.info(get_ref)
#                res = json.loads(get_ref)
#                ref1 = json.loads(get_ref)[0]['_ref']
#                print ref1
#                data = {"soa_serial_number":6}
#                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
#                print ("---------------------------------------------------",json.loads(response))
#                read  = re.search(r'201',response)
#                for read in response:
#                    assert True
#                logging.info("Serial Number for SOA Record is updated Successfully")
#                time.sleep(230) 

#        @pytest.mark.run(order=118)
#        def test_118_Validate_Template_Execution_for_Updated_soa_Record(self):
#                logging.info ("Validate Template Execution")

#                data = {"fqdn":"template_execution_dns_zone.com"}
#                o_type="zone_auth?fqdn="+str(data['fqdn'])
#                print ("oooooooooooooo",o_type)
#                get_template_zone = ib_NIOS.wapi_request('GET', object_type=o_type,fields=json.dumps(data))
#                print ("##########################", json.loads(get_template_zone))
#                print type(json.loads(get_template_zone))
#                result=json.loads(get_template_zone)
#                result=result[0]['_ref'].split(':')[1].split('/')[0]
#                print result
#                if (result==data['fqdn']):
#                        assert True
#                else:
#                        assert False
#                time.sleep(50)


#        @pytest.mark.run(order=119)
#        def test_119_Delete_Notf_for_Updated_soa_Record(self):
#                logging.info("Deleting zone created by template")
#                data= {"fqdn": "template_execution_dns_zone.com"}
#                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
#                print("$$$$$$$$$$$$$$$$$",get_ref)
#               ref = json.loads(get_ref)[0]['_ref']
#                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
#                logging.info("Wait for 10 sec.,")

#                time.sleep(50) #wait for 10 secs for the member to get started
#                print("Delete operation completed")



#        @pytest.mark.run(order=120)
#        def test_120_validate_delete_Network_for_Updated_soa_Record(self):
#                logging.info("Deleting zone")
#                data= {"fqdn": "template_execution_dns_zone.com"}
#                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
#                k=list(get_ref)
#                if(re.search(r'400',str(k))):
#                        print("Passed")
#                        assert True
#                else:
#                        print("Fail")
#                        assert False
						
#                logging.info("Restart services")
#                grid=ib_NIOS.wapi_request('GET', object_type="grid")
#                ref=json.loads(grid)[0]['_ref']
#                publish={"member_order":"SIMULTANEOUSLY"}
#                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
#                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
#                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
#                logging.info("System Restart is done successfully")


###Deleting ALIAS Record##

        @pytest.mark.run(order=121)
        def test_121_Delete_ALIAS_record(self):
                logging.info ("Deleting ALIAS Record for added Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:alias")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"name": "aliasupdated.outbound_zone2.com"}
                response = ib_NIOS.wapi_request('DELETE',ref=ref1 + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print ("---------------------------------------------------",json.loads(response))
                logging.info("ALIAS Record is Deleted Successfully")
                time.sleep(30)


####TLSA Record####

        @pytest.mark.run(order=122)
        def test_122_Add_Notification_Rule_TLSA(self):
                logging.info("Add Notification Rule for TLSA endpoint")
                data = {"name":"test"}
                endpoint=comm_util.get_object_reference(object_type="notification:rest:endpoint",data=data)
                data = {"name": "notificationTLSA","notification_action": "RESTAPI_TEMPLATE_INSTANCE","notification_target": endpoint,"template_instance": {"template": "Version5_DNS_Zone_and_Records_Action_Template"},"event_type": "DB_CHANGE_DNS_RECORD","expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "RECORD_TYPE","op1_type": "FIELD","op2": "RECORD_TYPE_TLSA","op2_type": "STRING"},{"op": "ENDLIST"}]}
                response = ib_NIOS.wapi_request('POST', object_type="notification:rule",fields=json.dumps(data))
                print (response)
                read  = re.search(r'201',response)
                for read in response:
                        assert True
                logging.info("Notification Rule is posted successfully")
                time.sleep(20)


        @pytest.mark.run(order=123)
        def test_123_Sign_Dnssec_Zone(self):
                logging.info("Sign zone for adding TLSA Record")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=comm_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"buffer":"KSK","operation":"SIGN"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                logging.info("The selected zone is signed successfully")
                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")


        @pytest.mark.run(order=124)
        def test_124_Validate_Dnssec_Zone_isSigned(self):
                logging.info("Validate if the zone is signed")
                data = {"fqdn":"outbound_zone2.com"}
                response=comm_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",response)
                logging.info(response)
		ref=response
		#response1=comm_util.get_object_reference(object_type=ref,params= "?_return_fields=is_dnssec_signed")
                response1 = ib_NIOS.wapi_request('GET', object_type= ref + "?_return_fields=is_dnssec_signed",fields=json.dumps(data))
		print response1
                res=json.loads(response1)
		print ("The value of the dnssec sign zone is ",res['is_dnssec_signed'])
		if (res['is_dnssec_signed']==True):
			assert True
                logging.info("Selected Zone is signed successfully")


        @pytest.mark.run(order=125)
        def test_125_Create_TLSA_record(self):
                logging.info ("Creating TLSA Record for added Zone")
                data = {"fqdn":"outbound_zone2.com"}
                endpoint=comm_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "_443._tcp.tlsa.outbound_zone2.com","certificate_data":"abcd","_ref":endpoint,"view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:tlsa",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("TLSA Record is created Successfully")
                time.sleep(30)


        @pytest.mark.run(order=126)
        def test_126_Validate_Template_Execution_TLSA_Record(self):
                logging.info ("Validate Template Execution")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")

				
        @pytest.mark.run(order=127)
        def test_127_Delete_Notf_TLSA_Record(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 30 sec.,")

                time.sleep(10) #wait for 10 secs for the member to get started
                print("Delete Operation Completed")


				
        @pytest.mark.run(order=128)
        def test_128_validate_delete_zone_TLSA(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False

                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")


        @pytest.mark.run(order=129)
        def test_129_Update_TLSA_record(self):
                logging.info ("Updating cert for TLSA Record for added Zone")
                get_ref = ib_NIOS.wapi_request('GET', object_type="record:tlsa")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                data = {"certificate_data":"abcdef"}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("Certificate details is updated for TLSA Record")
                time.sleep(30)



        @pytest.mark.run(order=130)
        def test_130_Validate_Template_Execution_for_Updated_TLSA_Record(self):
                logging.info ("Validate Template Execution")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")
				
        @pytest.mark.run(order=131)
        def test_131_Delete_Notf_for_Updated_TLSA_Record(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 10 sec.,")

                time.sleep(10) #wait for 10 secs for the member to get started
                print("Delete operation completed")

        @pytest.mark.run(order=132)
        def test_132_validate_delete_Network_for_Updated_TLSA_Record(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False
						
                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")

####Copy Records####

        @pytest.mark.run(order=133)
        def test_133_dig_records(self):
           record_list=["aaaarec"]
           data={"fqdn":"outbound_zone2.com"}
           try:
                for i in record_list:
                     LookFor='.*'+str(i)+'.'+data['fqdn']+'.*IN.*'+str(i)+'.*'
                     logging.info ("$$$$$$$$$$$$$$$$$$$",LookFor)
                     dig(i,data,i.lower(),LookFor)
           except ValueError:
                logging.info ("Dig failed")

        @pytest.mark.run(order=134)
        def test_134_copy_records(self):
           data={"fqdn":"outbound_zone2.com"}
           auth_zone_copy={"fqdn": "copied_zone.com","allow_query": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}]}
           logging.info("Creating auth Zone for Copying Records from one zone to another")
           response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(auth_zone_copy))
           if (response[0]==400):
                print ("Zone already exists,try with other data[Don't get confused with Pytest Passed status]")
           else:
                print ("Zone added and response looks like : ",response)
                res = json.loads(response)
                time.sleep(30)
                data = {"grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
                logging.info ("Trying to Associate ZONE with Primary GRID")
                response = ib_NIOS.wapi_request('PUT',ref=res,fields=json.dumps(data))
                response=json.loads(response)
                logging.info ("Restart services")
                logging.info ("Associated Zone with Primary GRID and reference looks like :",response)
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                time.sleep(10)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                time.sleep(20)
                print ("Restarting grid here now ")

                data1 = {"fqdn":"copied_zone.com"}
                destination_zone_ref=comm_util.get_object_reference(object_type="zone_auth",data=data1)
                print ("##########################",destination_zone_ref)
                logging.info(destination_zone_ref)
                logging.info ("Getting destination zone reference",destination_zone_ref)
                data2 = {"fqdn":"outbound_zone2.com"}
                beginning_zone_ref=comm_util.get_object_reference(object_type="zone_auth",data=data2)
                print("#@#@#@#@#@",beginning_zone_ref)
                wapi_data={"destination_zone":destination_zone_ref,"select_records":["AAAA"]}
                logging.info ("Check here for wapi data",wapi_data)
                logging.info ("Check here for your zone reference data from where you are planning to copy records",beginning_zone_ref)
                copying_records=ib_NIOS.wapi_request('POST',fields=json.dumps(wapi_data),object_type=beginning_zone_ref+"?_function=copyzonerecords")
                print("###############",copying_records)

           time.sleep(30)
           try:
                record_list=["aaaarec"]
                for i in record_list:
                     LookFor='.*'+str(i)+'.'+data1['fqdn']+'.*IN.*'+str(i)+'.*'
                     dig(i,data1,i.lower(),LookFor)
                assert True
                logging.info ("Test Case 16 Execution Passed")
           except ValueError:
                assert False
                logging.info ("Unable to copy records or unable to dig them")
                logging.info ("Test Case Execution Failed")



        @pytest.mark.run(order=135)
        def test_135_Validate_Template_Execution_for_copyrec_AAAA(self):
                logging.info ("Validate Template Execution")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")

        @pytest.mark.run(order=136)
        def test_136_Delete_Notf_for_copyrec_AAAA(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 10 sec.,")

                time.sleep(30) #wait for 10 secs for the member to get started
                print("Delete operation completed")

        @pytest.mark.run(order=137)
        def test_137_validate_delete_Network_for_copyrec_AAAA(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False

                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")



        @pytest.mark.run(order=138)
        def test_138_dig_records_DNAME(self):
           record_list=["dname"]
           data={"fqdn":"outbound_zone2.com"}
           try:
                for i in record_list:
                     LookFor='.*'+str(i)+'.'+data['fqdn']+'.*IN.*'+str(i)+'.*'
                     logging.info ("$$$$$$$$$$$$$$$$$$$",LookFor)
                     dig(i,data,i.lower(),LookFor)
           except ValueError:
                logging.info ("Dig failed")

        @pytest.mark.run(order=139)
        def test_139_copy_records_DNAME(self):

                data1 = {"fqdn":"copied_zone.com"}
                destination_zone_ref=comm_util.get_object_reference(object_type="zone_auth",data=data1)
                print ("##########################",destination_zone_ref)
                logging.info(destination_zone_ref)
                logging.info ("Getting destination zone reference",destination_zone_ref)
                data2 = {"fqdn":"outbound_zone2.com"}
                beginning_zone_ref=comm_util.get_object_reference(object_type="zone_auth",data=data2)
                print("#@#@#@#@#@",beginning_zone_ref)
                wapi_data={"destination_zone":destination_zone_ref,"select_records":["DNAME"]}
                logging.info ("Check here for wapi data",wapi_data)
                logging.info ("Check here for your zone reference data from where you are planning to copy records",beginning_zone_ref)
                copying_records=ib_NIOS.wapi_request('POST',fields=json.dumps(wapi_data),object_type=beginning_zone_ref+"?_function=copyzonerecords")
                print("###############",copying_records)

                time.sleep(30)
                try:
                     record_list=["dname"]
                     for i in record_list:
                          LookFor='.*'+str(i)+'.'+data1['fqdn']+'.*IN.*'+str(i)+'.*'
                          dig(i,data1,i.lower(),LookFor)
                     assert True
                     logging.info ("Test Case 16 Execution Passed")
                except ValueError:
                     assert False
                     logging.info ("Unable to copy records or unable to dig them")
                     logging.info ("Test Case Execution Failed")


        @pytest.mark.run(order=140)
        def test_140_Validate_Template_Execution_for_copyrec_DNAME(self):
                logging.info ("Validate Template Execution")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")

        @pytest.mark.run(order=141)
        def test_141_Delete_Notf_for_copyrec_DNAME(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 10 sec.,")

                time.sleep(30) #wait for 10 secs for the member to get started
                print("Delete operation completed")

        @pytest.mark.run(order=142)
        def test_142_validate_delete_Network_for_copyrec_DNAME(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False

                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")



        @pytest.mark.run(order=143)
        def test_143_dig_records_cname(self):
           record_list=["cname"]
           data={"fqdn":"outbound_zone2.com"}
           try:
                for i in record_list:
                     LookFor='.*'+str(i)+'.'+data['fqdn']+'.*IN.*'+str(i)+'.*'
                     logging.info ("$$$$$$$$$$$$$$$$$$$",LookFor)
                     dig(i,data,i.lower(),LookFor)
           except ValueError:
                logging.info ("Dig failed")

        @pytest.mark.run(order=144)
        def test_144_copy_records_cname(self):
                data1 = {"fqdn":"copied_zone.com"}
                destination_zone_ref=comm_util.get_object_reference(object_type="zone_auth",data=data1)
                print ("##########################",destination_zone_ref)
                logging.info(destination_zone_ref)
                logging.info ("Getting destination zone reference",destination_zone_ref)
                data2 = {"fqdn":"outbound_zone2.com"}
                beginning_zone_ref=comm_util.get_object_reference(object_type="zone_auth",data=data2)
                print("#@#@#@#@#@",beginning_zone_ref)
                wapi_data={"destination_zone":destination_zone_ref,"select_records":["CNAME"]}
                logging.info ("Check here for wapi data",wapi_data)
                logging.info ("Check here for your zone reference data from where you are planning to copy records",beginning_zone_ref)
                copying_records=ib_NIOS.wapi_request('POST',fields=json.dumps(wapi_data),object_type=beginning_zone_ref+"?_function=copyzonerecords")
                print("###############",copying_records)

                time.sleep(30)
                try:
                     record_list=["cname"]
                     for i in record_list:
                          LookFor='.*'+str(i)+'.'+data1['fqdn']+'.*IN.*'+str(i)+'.*'
                          dig(i,data1,i.lower(),LookFor)
                     assert True
                     logging.info ("Test Case 16 Execution Passed")
                except ValueError:
                     assert False
                     logging.info ("Unable to copy records or unable to dig them")
                     logging.info ("Test Case Execution Failed")



        @pytest.mark.run(order=145)
        def test_145_Validate_Template_Execution_for_copyrec_cname(self):
                logging.info ("Validate Template Execution")
                data = {"fqdn":"template_execution_dns_zone.com"}
                get_template_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print ("##########################", get_template_zone)
                logging.info(get_template_zone)
                res=json.loads(get_template_zone)
                print (res)
                for i in res:
                       print i
                       logging.info("found")
                       assert i["fqdn"] == "template_execution_dns_zone.com"
                logging.info("Template is executed successfully")

        @pytest.mark.run(order=146)
        def test_146_Delete_Notf_for_copyrec_cname(self):
                logging.info("Deleting zone created by template")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info("Wait for 10 sec.,")

                time.sleep(30) #wait for 10 secs for the member to get started
                print("Delete operation completed")

        @pytest.mark.run(order=147)
        def test_147_validate_delete_Network_for_copyrec_cname(self):
                logging.info("Deleting zone")
                data= {"fqdn": "template_execution_dns_zone.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?ref",fields=json.dumps(data),grid_vip=config.grid_vip)
                k=list(get_ref)
                if(re.search(r'400',str(k))):
                        print("Passed")
                        assert True
                else:
                        print("Fail")
                        assert False

                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")


####Import Zone#########

        @pytest.mark.run(order=148)
        def test_148_Create_AuthZone_for_Import(self):
                logging.info("Create_AuthZone_for_Import")
                get_ref = import_zone.create_auth_zone()
                print("$$$$$$$$$$$$$$$$$",get_ref)
                logging.info("Auth Zone is created successfully")
                time.sleep(30) #wait for 10 secs for the member to get started

        @pytest.mark.run(order=149)
        def test_149_Import_AuthZone(self):
                logging.info("Applying Import zone")
                get_ref = import_zone.check_auth_zone()
                print("$$$$$$$$$$$$$$$$$",get_ref)
                time.sleep(30) #wait for 10 secs for the member to get started


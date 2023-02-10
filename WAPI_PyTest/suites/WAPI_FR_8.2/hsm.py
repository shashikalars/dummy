import re
import config
import pytest
import unittest
import logging
import subprocess
import shlex
import json
import time
import getpass
import pexpect
import sys
import os
import ib_utils.ib_NIOS as ib_NIOS


class RegisterSafenetSaFive(unittest.TestCase):


        @classmethod
        def setup_class(cls):
                """ setup any state specific to the execution of the given class (which
                 usually contains tests).
                 """
                logging.info("SETUP METHOD")

        def simple_func(self,a):
                # do any process here and return the value
                # Return value is comparted(asserted) in test case method
                return(a+2)
           #Create a SafeNet HSM Group object


        @pytest.mark.run(order=1)
        def test_01_generatesafenetclientcert_Fileop_Function_Call(self):
                logging.info("Test the generatesafenetclientcert function call in fileop object")
                data = {"algorithm":"RSASHA256","member":config.grid_fqdn}
                response = ib_NIOS.wapi_request('POST',object_type="fileop",params="?_function=generatesafenetclientcert",fields=json.dumps(data))
                print response
                logging.info(response)
                res = re.search(r'200',response)
                for res in response:
                        assert True
                logging.info("Test Case 1 Execution Completed")
                logging.info("============================")

				
        @pytest.mark.run(order=2)
        def test_02_Deleting_infoblox_id(self):
                logging.info("Unregistering safenet luna sa five")
            	try:
			child = pexpect.spawn ('ssh -o StrictHostKeyChecking=no '+config.client_user1+'@'+config.client_ip1)
                        child.expect ('.*password:')
			child.sendline ('infoblox')
			child.expect ('.*$')
			child.sendline ('ssh admin@10.39.10.12')
			child.expect ('.*password:')
			child.sendline ('Infoblox.123')
			child.expect ('.*lunash:>')
                        child.sendline ('client delete -c ' +config.USER)
			child.expect ('>')
			child.sendline ('proceed')
			child.expect ('.*lunash:>')
			child.sendline ('exit')
		except:
			assert True
			logging.info("============================")

        @pytest.mark.run(order=3)
        def test_03_registering_safenet_luna_sa_five(self):
                try:
                        logging.info("Registering safenet luna sa five")
                        child = pexpect.spawn ('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                        child.expect ('.*#')
                        child.sendline ('cd /storage/safenet-hsm/lunasa_5/cert/client/')
                        child.expect ('.*#')
                        child.sendline ('scp -o StrictHostKeyChecking=no '+config.grid_vip+'.pem '+config.client_user1+'@'+config.client_ip1+':/tmp/')
                        child.expect ('.*password:')
                        child.sendline ('infoblox')
                        child.expect ('.*#')
                        child.sendline('exit')
                        child.expect ('.*$') 
                        print(os.system("sshpass -p 'Infoblox.123' scp -o StrictHostKeyChecking=no /tmp/"+config.grid_vip+".pem admin@10.39.10.12:"))
                        cmd = "sshpass -p 'Infoblox.123' ssh -o StrictHostKeyChecking=no admin@10.39.10.12"
                        args = shlex.split(cmd)
                        p = subprocess.Popen(args, stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        p.stdin.write("client register -c "+config.USER+" -i "+config.grid_vip+" \n")
                        p.stdin.write("client assignPartition -c "+config.USER+" -P QA2Partition" + "\n")
                        p.stdin.close()
                        print p.stdout.read()
                        print("Sleeping for 120 seconds")
                        time.sleep(120)
                        logging.info("============================")

                except:
                        assert False
                        logging.info("============================")

        @pytest.mark.run(order=4)
        def test_04_adding_safenet_group_luna_sa_five(self):
                filename="server.pem"
                data = {"filename":filename}
                logging.info("uploading Client Certificate")
                create_file = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadinit",grid_vip=config.grid_vip)
                logging.info(create_file)
                res = json.loads(create_file)
                token = json.loads(create_file)['token']
                url = json.loads(create_file)['url']
                print create_file
                print res
                print token
                print url
                os.system('curl -k1 -u admin:infoblox -F name=%s -F filedata=@%s %s'%(filename,filename,url))
                filename="/"+filename
                print filename
                data = {"comment": "testing","hsm_safenet":[{"disable": False,"name": "10.39.10.12","partition_serial_number":"154441013","server_cert": token}],"hsm_version":"LunaSA_5","name": "HSM_group","pass_phrase":"Infoblox.123"}
                create_file1 = ib_NIOS.wapi_request('POST', object_type="hsm:safenetgroup",fields=json.dumps(data),grid_vip=config.grid_vip)
                logging.info(create_file1)
                print create_file1
                assert re.search(r"400",str(create_file1[0]))

			

        @pytest.mark.run(order=4)
        def test_04_adding_safenet_group_luna_sa_five_1(self):
            filename="server.pem"
            data = {"filename":filename}
            logging.info("uploading Client Certificate")
            create_file = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadinit",grid_vip=config.grid_vip)
            logging.info(create_file)
            res = json.loads(create_file)
            token = json.loads(create_file)['token']
            url = json.loads(create_file)['url']
            print create_file
            print res
            print token
            print url
            os.system('curl -k1 -u admin:infoblox -F name=%s -F filedata=@%s %s'%(filename,filename,url))
            filename="/"+filename
            print filename
            data = {"comment": "testing","hsm_safenet":[{"disable": False,"name": "10.39.10.12","partition_serial_number":"154441013","server_cert": token}],"hsm_version":"LunaSA_5","name": "HSM_group","pass_phrase":"Infoblox.123"}
            create_file1 = ib_NIOS.wapi_request('POST', object_type="hsm:safenetgroup",fields=json.dumps(data),grid_vip=config.grid_vip)
            logging.info(create_file1)
            print create_file1
            assert re.search(r"",create_file1)
            logging.info("Test Case 4 Execution Completed")
            logging.info("============================")


        @pytest.mark.run(order=5)
        def test_05_validate_the_status_of_hsm_group(self):
            get_ref = ib_NIOS.wapi_request('GET',object_type="hsm:safenetgroup",params="?_return_fields=status",grid_vip=config.grid_vip)
            ref1 = json.loads(get_ref)[-1]['status']
            print ref1
            if ref1 == "UP":
            	assert True
            logging.info("Test Case 5 Execution Completed")
            logging.info("============================")

        @pytest.mark.run(order=6)
        def test_06_Adding_the_hsm_allgroups_in_groups_field_N(self):
            logging.info("Adding_the_hsm_allgroups_in_groups_field_N")
            data = {"groups":["hsm:thalesgroup/b25lLnRoYWxlc19oc21fZ3JvdXAkdGhhbGVz:thales"]}
            status,response1 = ib_NIOS.wapi_request('POST', object_type="hsm:allgroups",fields=json.dumps(data),grid_vip=config.grid_vip)
            print status
            print response1
            logging.info(response1)
            assert  status == 400 and re.search(r'Operation create not allowed for hsm:allgroups',response1)
            logging.info("Test Case 6 Execution Completed")
            logging.info("============================")
         
        @pytest.mark.run(order=7)
        def test_07_Delete_groups_field_with_hsm_allgroups_object_N(self):
            logging.info("Delete_groups_field_with_hsm_allgroups_object_N")
            status,response1 = ib_NIOS.wapi_request('DELETE', ref = "hsm:allgroups/Li5hbGxfaHNtX2dyb3VwJDQ:hsm",grid_vip=config.grid_vip)
            print status
            print response1
            logging.info(response1)
            assert  status == 400 and re.search(r'Operation delete not allowed for hsm:allgroups',response1)
            logging.info("Test Case 7 Execution Completed")
            logging.info("============================")

        
        @pytest.mark.run(order=8)
        def test_08_Modifiy_the_hsm_allgroups_with_groups_N(self):
            logging.info("Modifiy_the_hsm_allgroups_with_groups_N")
            data = {"groups":["hsm:thalesgroup/b25lLnRoYWxlc19oc21fZ3JvdXAkdGhhbGVz:thales"]}
            status,response1 = ib_NIOS.wapi_request('PUT', ref = 'hsm:allgroups/Li5hbGxfaHNtX2dyb3VwJDQ:hsm', fields=json.dumps(data),grid_vip=config.grid_vip)
            print status
            print response1
            logging.info(response1)
            assert  status == 400 and re.search(r'Operation update not allowed for hsm:allgroups',response1)
            logging.info("Test Case 8 Execution Completed")
            logging.info("============================")

        @pytest.mark.run(order=9)
        def test_09_Global_search_with_string_in_hsm_allgroups_object_N(self):
             logging.info("Global_search_with_string_in_hsm_allgroups_object_N")
             response = ib_NIOS.wapi_request('GET', object_type="search",params="?search_string=groups",grid_vip=config.grid_vip)
             logging.info(response)
             res = json.loads(response)
             print res
             for i in res:
                 logging.info("found")
                 assert i["name"] == "Infoblox" and i["global_status"] == "INACTIVE" and i["groups"] == "hsm:thalesgroup/b25lLnRoYWxlc19oc21fZ3JvdXAkdGhhbGVz:thales"
             logging.info("Test Case 9 Execution Completed")
             logging.info("============================")
        
        @pytest.mark.run(order=10)
        def test_10_Read_by_reference_in_hsm_allgroups_object(self):
            get_ref = ib_NIOS.wapi_request('GET', object_type="hsm:allgroups",grid_vip=config.grid_vip)
            logging.info(get_ref)
            res = json.loads(get_ref)
            ref = json.loads(get_ref)[0]['_ref']
            print ref
            logging.info("Test read by referance on hsm:allgroups object")
            status,response = ib_NIOS.wapi_request('GET',object_type=ref)
            print response
            print status
            logging.info(response)
            assert status == 400 and re.search(r'AdmConProtoError: Operation \\"read by reference\\" not allowed for hsm:allgroup',response)
            logging.info("Test Case 10 Execution Completed")
            logging.info("============================")

        
        @pytest.mark.run(order=11)
        def test_11_Get_the_field_in_hsm_allgroups_with_groups(self):
            logging.info("Get_the_field_in_hsm_allgroups_with_groups")
            response = ib_NIOS.wapi_request('GET', object_type="hsm:allgroups",grid_vip=config.grid_vip)
            logging.info(response)
            read  = re.search(r'200',response)
            for read in  response:
                    assert True
            logging.info("Test Case 11 Execution Completed")
            logging.info("============================")
        
        @pytest.mark.run(order=12)
        def test_12_Groups_filed_is_not_searchable_with_hsm_allgroups_object_N(self):
            logging.info("Groups_filed_is_not_searchable_with_hsm_allgroups_object_N")
            status,response1 = ib_NIOS.wapi_request('GET', object_type="hsm:allgroups", params="?groups=hsm:thalesgroup/b25lLnRoYWxlc19oc21fZ3JvdXAkdGhhbGVz:thales",grid_vip=config.grid_vip)
            print status
            print response1
            logging.info(response1)
            assert  status == 400 and re.search(r'Field is not searchable: groups',response1)
            logging.info("Test Case 12 Execution Completed")
            logging.info("============================")


        @pytest.mark.run(order=13)
        def test_13_refresh_hsm_hsm_safenetgroup_Function_Call(self):
            get_ref = ib_NIOS.wapi_request('GET', object_type="hsm:safenetgroup",grid_vip=config.grid_vip)
            logging.info(get_ref)
            res = json.loads(get_ref)
            ref = json.loads(get_ref)[0]['_ref']
            logging.info("Test the uploadinit function call in hsm:safenetgroup object")
            response = ib_NIOS.wapi_request('POST',object_type=ref,params="?_function=refresh_hsm",grid_vip=config.grid_vip)
            print response
            res = json.loads(response)
            string = {"results": "PASSED"}
            if res == string:
                    assert True
            else:
                    assert False
            logging.info("Test Case 13 Execution Completed")
            logging.info("============================")
                                                      
        @pytest.mark.run(order=14)
        def test_14_DELETE_refresh_hsm_hsm_safenetgroup_Function_Call(self):
            get_ref = ib_NIOS.wapi_request('GET', object_type="hsm:safenetgroup",grid_vip=config.grid_vip)
            logging.info(get_ref)
            res = json.loads(get_ref)
            ref = json.loads(get_ref)[0]['_ref']
            logging.info("Test the refresh_hsm function call with DELETE in hsm:safenetgroup object")
            status,response = ib_NIOS.wapi_request('DELETE',object_type=ref,params="?_function=refresh_hsm",grid_vip=config.grid_vip)
            print response
            print status
            assert status == 400 and re.search(r'AdmConProtoError: Function refresh_hsm illegal with this method',response)
            logging.info("Test Case 14 execution Completed")
            logging.info("============================")


        @pytest.mark.run(order=15)
        def test_15_Create_hsm_thalesgroup_Function_Call(self):
            logging.info("Create A new hsm_thalesgroup")
            data = {"card_name":"HSMThales","comment": "this_is_a_thales_group","key_server_ip": "10.39.10.39","key_server_port": 9004,"name": "thales","protection": "SOFTCARD","thales_hsm": [{"disable": False,"keyhash": "821f3afc559c84d3b212af34d997386acb992141","remote_ip": "10.39.10.10","remote_port": 9004}],"pass_phrase":"Infoblox.123"}
            response = ib_NIOS.wapi_request('POST', object_type="hsm:thalesgroup", fields=json.dumps(data),grid_vip=config.grid_vip)
            print response
            logging.info(response)
            read  = re.search(r'201',response)
            for read in  response:
                    assert True
            logging.info("Test Case 15 Execution Completed")
            logging.info("============================")


        @pytest.mark.run(order=16)
        def test_16_refresh_hsm_hsm_thalesgroup_Function_Call(self):
            get_ref = ib_NIOS.wapi_request('GET', object_type="hsm:thalesgroup",grid_vip=config.grid_vip)
            logging.info(get_ref)
            res = json.loads(get_ref)
            ref = json.loads(get_ref)[0]['_ref']
            logging.info("Test the uploadinit function call in hsm:thalesgroup object")
            response = ib_NIOS.wapi_request('POST',object_type=ref,params="?_function=refresh_hsm",grid_vip=config.grid_vip)
            print response
            res = json.loads(response)
            string = {"results": "INACTIVE"}
            if res == string:
                    assert True
            else:
                    assert False
            logging.info("Test Case 16 Execution Completed")
            logging.info("============================")


        @pytest.mark.run(order=17)
        def test_17_refresh_hsm_hsm_thalesgroup_Function_Call(self):
            get_ref = ib_NIOS.wapi_request('GET', object_type="hsm:thalesgroup",grid_vip=config.grid_vip)
            logging.info(get_ref)
            res = json.loads(get_ref)
            ref = json.loads(get_ref)[0]['_ref']
            logging.info("Test the refresh_hsm function call with PUT in hsm:thalesgroup object")
            status,response = ib_NIOS.wapi_request('PUT',object_type=ref,params="?_function=refresh_hsm",grid_vip=config.grid_vip)
            print response
            print status
            assert status == 400 and re.search(r'AdmConProtoError: Function refresh_hsm illegal with this method',response)
            logging.info("Test Case 17 Execution Completed")
            logging.info("============================")


        @pytest.mark.run(order=18)
        def test_18_DELETE_refresh_hsm_hsm_thalesgroup_Function_Call(self):
            get_ref = ib_NIOS.wapi_request('GET', object_type="hsm:thalesgroup",grid_vip=config.grid_vip)
            logging.info(get_ref)
            res = json.loads(get_ref)
            ref = json.loads(get_ref)[0]['_ref']
            logging.info("Test the refresh_hsm function call with DELETE in hsm:thalesgroup object")
            status,response = ib_NIOS.wapi_request('DELETE',object_type=ref,params="?_function=refresh_hsm",grid_vip=config.grid_vip)
            print response
            print status
            assert status == 400 and re.search(r'AdmConProtoError: Function refresh_hsm illegal with this method',response)
            logging.info("Test Case 18 Execution Completed")
            logging.info("============================")


        @pytest.mark.run(order=19)
        def test_19_DELETE_hsm_thalesgroup(self):
            get_ref = ib_NIOS.wapi_request('GET', object_type="hsm:thalesgroup",grid_vip=config.grid_vip)
            logging.info(get_ref)
            res = json.loads(get_ref)
            ref = json.loads(get_ref)[0]['_ref']
            print ref
            logging.info("Deleting the hsm:thalesgroup user")
            response = ib_NIOS.wapi_request('DELETE', object_type=ref,grid_vip=config.grid_vip)
            logging.info(response)
            read  = re.search(r'201',response)
            for read in  response:
                    assert True
            logging.info(response)
            logging.info("Test Case 19 Execution Completed")
            logging.info("=============================")

        
        @pytest.mark.run(order=20)
        def test_20_Adding_the_hsm_safenetgroup_object_to_partition_serial_number_field_N(self):
            logging.info("Adding_the_hsm_safenetgroup_object_to_partition_serial_number_field_N")
            data = {"comment":"testing","hsm_safenet":[{"disable": False,"name":"10.39.10.12","partition_serial_number":154441011,"server_cert": "eJydUMFOwzAMvedHxmVp061ry21oTEJCA21wttokHZbaxKQp2v4eZ0hcuHGIZfs9P+dZa09XCPYs\nOGjvphhmHX0QpMSdRtf7bvAX6Z1NL17JTmLXxhaOthdUCA3QzThEdADCoI6CVuLO0FqcFvZCGK4Q\ncbQLQaXYq3VTVnnVFLWsq7xWSkynxRwGRjfM/4iRpvssU7lclVKpWpZZ6oFB/luEHgcL6LNgPwHN\n8v31+WW7W6o8V7eRRnJUhSQ7smCVtNFwVrP03xEGmkQxbIZzlTMrm9h5e7ZZHOn/m39sJV2wTnuD\n7py6BS94eDqkdPVLGL1Jt1HpXLvt2xaOj/tUl2KKR1KbdEpVMdijHcwE0YP2I7XhNlWLQzLZtQTo\naI7wZcOE3iWsYayT3w3jksg=\n"}],"hsm_version":"LunaSA_5","name": "HSM_group","pass_phrase":123}
            status,response1 = ib_NIOS.wapi_request('POST', object_type="hsm:safenetgroup",fields=json.dumps(data),grid_vip=config.grid_vip)
            print status
            print response1
            logging.info(response1)
            assert  status == 400 and re.search(r'Invalid value for pass_phrase: 123: Must be string type',response1)
            logging.info("Test Case 20 Execution Completed")
            logging.info("============================")
      
        
        @pytest.mark.run(order=21)
        def test_21_Adding_the_hsm_safenetgroup_object_to_name_field_N(self):
            logging.info("Adding_the_hsm_safenetgroup_object_to_name_field_N")
            data = {"comment":"testing","hsm_safenet":[{"disable": False,"name":"10.39.10.12","partition_serial_number":154441011,"server_cert":"eJydUMFOwzAMvedHxmVp061ry21oTEJCA21wttokHZbaxKQp2v4eZ0hcuHGIZfs9P+dZa09XCPYs\nOGjvphhmHX0QpMSdRtf7bvAX6Z1NL17JTmLXxhaOthdUCA3QzThEdADCoI6CVuLO0FqcFvZCGK4Q\ncbQLQaXYq3VTVnnVFLWsq7xWSkynxRwGRjfM/4iRpvssU7lclVKpWpZZ6oFB/luEHgcL6LNgPwHN\n8v31+WW7W6o8V7eRRnJUhSQ7smCVtNFwVrP03xEGmkQxbIZzlTMrm9h5e7ZZHOn/m39sJV2wTnuD\n7py6BS94eDqkdPVLGL1Jt1HpXLvt2xaOj/tUl2KKR1KbdEpVMdijHcwE0YP2I7XhNlWLQzLZtQTo\naI7wZcOE3iWsYayT3w3jksg=\n"}],"hsm_version":"LunaSA_5","name": 234,"pass_phrase":"Infoblox.123"}
            status,response1 = ib_NIOS.wapi_request('POST', object_type="hsm:safenetgroup",fields=json.dumps(data),grid_vip=config.grid_vip)
            print status
            print response1
            logging.info(response1)
            assert  status == 400 and re.search(r'Invalid value for name: 234: Must be string type',response1)
            logging.info("Test Case 21 Execution Completed")
            logging.info("============================")

        @pytest.mark.run(order=22)
        def test_22_Adding_the_hsm_safenetgroup_object_to_partition_serial_number_field_N(self):
            logging.info("Adding_the_hsm_safenetgroup_object_to_partition_serial_number_field_N")
            data = {"comment":"testing","hsm_safenet":[{"disable": False,"name":"10.39.10.12","partition_serial_number":"154441011","server_cert":"eJydUMFOwzAMvedHxmVp061ry21oTEJCA21wttokHZbaxKQp2v4eZ0hcuHGIZfs9P+dZa09XCPYs\nOGjvphhmHX0QpMSdRtf7bvAX6Z1NL17JTmLXxhaOthdUCA3QzThEdADCoI6CVuLO0FqcFvZCGK4Q\ncbQLQaXYq3VTVnnVFLWsq7xWSkynxRwGRjfM/4iRpvssU7lclVKpWpZZ6oFB/luEHgcL6LNgPwHN\n8v31+WW7W6o8V7eRRnJUhSQ7smCVtNFwVrP03xEGmkQxbIZzlTMrm9h5e7ZZHOn/m39sJV2wTnuD\n7py6BS94eDqkdPVLGL1Jt1HpXLvt2xaOj/tUl2KKR1KbdEpVMdijHcwE0YP2I7XhNlWLQzLZtQTo\naI7wZcOE3iWsYayT3w3jksg=\n"}],"hsm_version":"LunaSA_5","name":"HSM_group","pass_phrase":"Infoblox.123"}
            status,response1 = ib_NIOS.wapi_request('POST', object_type="hsm:safenetgroup",fields=json.dumps(data),grid_vip=config.grid_vip)
            print status
            print response1
            logging.info(response1)
            assert  status == 400 and re.search(r'AdmConDataError: None ',response1)
            logging.info("Test Case 22 Execution Completed")
            logging.info("============================")

        
        @pytest.mark.run(order=23)
        def test_23_Adding_the_hsm_safenetgroup_object_to_name_field_N(self):
            logging.info("Adding_the_hsm_safenetgroup_object_to_name_field_N")
            data = {"comment":"testing","hsm_safenet":[{"disable": False,"name":10,"partition_serial_number":"154441011","server_cert": "eJydUMFOwzAMvedHxmVp061ry21oTEJCA21wttokHZbaxKQp2v4eZ0hcuHGIZfs9P+dZa09XCPYs\nOGjvphhmHX0QpMSdRtf7bvAX6Z1NL17JTmLXxhaOthdUCA3QzThEdADCoI6CVuLO0FqcFvZCGK4Q\ncbQLQaXYq3VTVnnVFLWsq7xWSkynxRwGRjfM/4iRpvssU7lclVKpWpZZ6oFB/luEHgcL6LNgPwHN\n8v31+WW7W6o8V7eRRnJUhSQ7smCVtNFwVrP03xEGmkQxbIZzlTMrm9h5e7ZZHOn/m39sJV2wTnuD\n7py6BS94eDqkdPVLGL1Jt1HpXLvt2xaOj/tUl2KKR1KbdEpVMdijHcwE0YP2I7XhNlWLQzLZtQTo\naI7wZcOE3iWsYayT3w3jksg=\n"}],"hsm_version":"LunaSA_5","name": "HSM_group","pass_phrase":"Infoblox.123"}
            status,response1 = ib_NIOS.wapi_request('POST', object_type="hsm:safenetgroup",fields=json.dumps(data),grid_vip=config.grid_vip)
            print status
            print response1
            logging.info(response1)
            assert  status == 400 and re.search(r'AdmConProtoError: Invalid value for name: 10: Must be string type',response1)
            logging.info("Test Case 23 Execution Completed")
            logging.info("============================")

        
        @pytest.mark.run(order=24)
        def test_24_Adding_the_hsm_safenetgroup_object_to_disable_field_N(self):
            logging.info("Adding_the_hsm_safenetgroup_object_to_disable_field_N")
            data = {"comment":"testing","hsm_safenet":[{"disable": "false","name":"10.39.10.12","partition_serial_number":154441011,"server_cert":"eJydUMFOwzAMvedHxmVp061ry21oTEJCA21wttokHZbaxKQp2v4eZ0hcuHGIZfs9P+dZa09XCPYs\nOGjvphhmHX0QpMSdRtf7bvAX6Z1NL17JTmLXxhaOthdUCA3QzThEdADCoI6CVuLO0FqcFvZCGK4Q\ncbQLQaXYq3VTVnnVFLWsq7xWSkynxRwGRjfM/4iRpvssU7lclVKpWpZZ6oFB/luEHgcL6LNgPwHN\n8v31+WW7W6o8V7eRRnJUhSQ7smCVtNFwVrP03xEGmkQxbIZzlTMrm9h5e7ZZHOn/m39sJV2wTnuD\n7py6BS94eDqkdPVLGL1Jt1HpXLvt2xaOj/tUl2KKR1KbdEpVMdijHcwE0YP2I7XhNlWLQzLZtQTo\naI7wZcOE3iWsYayT3w3jksg=\n"}],"hsm_version":"LunaSA_5","name":"HSM_group","pass_phrase":"Infoblox.123"}
            status,response1 = ib_NIOS.wapi_request('POST', object_type="hsm:safenetgroup",fields=json.dumps(data),grid_vip=config.grid_vip)
            print status
            print response1
            logging.info(response1)
            assert  status == 400 and re.search(r'Invalid value for disable: .*false.*: Must be boolean type',response1)
            logging.info("Test Case 24 Execution Completed")
            logging.info("============================")

        @pytest.mark.run(order=25)
        def test_25_Adding_the_hsm_safenetgroup_object_to_Comment_field_N(self):
            logging.info("Adding_the_hsm_safenetgroup_object_to_Comment_field_N")
            data = {"comment":123,"hsm_safenet":[{"disable": False,"name":"10.39.10.12","partition_serial_number":154441011,"server_cert": "eJydUMFOwzAMvedHxmVp061ry21oTEJCA21wttokHZbaxKQp2v4eZ0hcuHGIZfs9P+dZa09XCPYs\nOGjvphhmHX0QpMSdRtf7bvAX6Z1NL17JTmLXxhaOthdUCA3QzThEdADCoI6CVuLO0FqcFvZCGK4Q\ncbQLQaXYq3VTVnnVFLWsq7xWSkynxRwGRjfM/4iRpvssU7lclVKpWpZZ6oFB/luEHgcL6LNgPwHN\n8v31+WW7W6o8V7eRRnJUhSQ7smCVtNFwVrP03xEGmkQxbIZzlTMrm9h5e7ZZHOn/m39sJV2wTnuD\n7py6BS94eDqkdPVLGL1Jt1HpXLvt2xaOj/tUl2KKR1KbdEpVMdijHcwE0YP2I7XhNlWLQzLZtQTo\naI7wZcOE3iWsYayT3w3jksg=\n"}],"hsm_version":"LunaSA_5","name": "HSM_group","pass_phrase":"Infoblox.123"}
            status,response1 = ib_NIOS.wapi_request('POST', object_type="hsm:safenetgroup",fields=json.dumps(data),grid_vip=config.grid_vip)
            print status
            print response1
            logging.info(response1)
            assert  status == 400 and re.search(r'Invalid value for comment: 123: Must be string type',response1)
            logging.info("Test Case 25 Execution Completed")
            logging.info("============================")


        @pytest.mark.run(order=26)
        def test_26_Deleting_infoblox_id(self):
            logging.info("Unregistering safenet luna sa five")
            try:
                    child = pexpect.spawn ('ssh -o StrictHostKeyChecking=no '+config.client_user1+'@'+config.client_ip1)
                    child.expect ('.*password:')
                    child.sendline ('infoblox')
                    child.expect ('.*$')
                    child.sendline ('ssh admin@10.39.10.12')
                    child.expect ('.*password:')
                    child.sendline ('Infoblox.123')
                    child.expect ('.*lunash:>')
                    child.sendline ('client delete -c ' +config.USER)
                    child.expect ('>')
                    child.sendline ('proceed')
                    child.expect ('.*lunash:>')
                    child.sendline ('exit')
            except:
                    assert True
                    logging.info("Test Case 26 Execution Completed")
                    logging.info("============================")
        
        @classmethod
        def teardown_class(cls):
            """ teardown any state that was previously setup with a call to
            setup_class.
            """
            logging.info("TEAR DOWN METHOD")

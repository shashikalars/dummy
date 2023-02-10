import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import config
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
import commands
import json, ast
import requests
import time
import getpass
import sys
import pexpect
import re

def configure_SAML_Service_By_Upload():
    ref=ib_NIOS.wapi_request('GET',object_type='saml:authservice')
    if ref !='[]':
        ref=json.loads(ref)[0]['_ref']
        delete_saml_service(ref)
    filename="metadata.xml"
    logging.info("Test Uploading the Template with fileop")
    data = {"filename":filename}
    create_file = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadinit")
    logging.info(create_file)
    res = json.loads(create_file)
    token = json.loads(create_file)['token']
    url = json.loads(create_file)['url']
    file1=url.split("/")
    os.system('curl -k1 -u admin:infoblox -F name=%s -F filedata=@%s %s'%(filename,filename,url))
    filename="/"+filename
    data = {"name":"saml","session_timeout":1234,"idp":{"idp_type": "OKTA","metadata_token":token}}
    create_file1 = ib_NIOS.wapi_request('POST', object_type="saml:authservice",fields=json.dumps(data))
    create_file1=json.loads(create_file1)
    return create_file1


def get_ref_value_for_admingroup(ref1):
    ref2=ref1
    get_ref=ib_NIOS.wapi_request("GET",object_type=ref2+"_?return_fields=roles")
    res = json.loads(get_ref)
    ref1 = json.loads(get_ref)
    logging.info ("*********************************************************************************",ref1)
    return ref1

def super_user_check(ref1):
    ref2=ref1
    logging.info("get value for super user or not")
    get_ref = ib_NIOS.wapi_request('GET', object_type=ref2+"?_return_fields=superuser")
    logging.info(get_ref)
    super_user = json.loads(get_ref)
    return super_user

def get_reference_value_auto_create_user(ref1):
    ref2=ref1
    get_ref = ib_NIOS.wapi_request('GET', object_type=ref2+"?_return_fields=saml_setting")
    logging.info(get_ref)
    res = json.loads(get_ref)#convert to dictionary
    ref1 =json.loads(get_ref)['saml_setting']['auto_create_user']
    #logging.info ("*********************************************************************************",ref1)
    return ref1

def get_reference_value_persist_auto_create_user(ref1):
    ref2=ref1
    get_ref = ib_NIOS.wapi_request('GET', object_type=ref2+"?_return_fields=saml_setting")
    logging.info(get_ref)
    res = json.loads(get_ref)#convert to dictionary
    ref1 = json.loads(get_ref)['saml_setting']['persist_auto_created_user']
    #logging.info ("*********************************************************************************",ref1)
    return ref1

def configure_saml_service():
    logging.info("Configuring SAML Service")
    data={"idp":{"idp_type": "OKTA","sso_redirect_url":config.grid_vip,"metadata_url": "https://dev-197701.oktapreview.com/app/exk11ibbc7xmdOTaC0h8/sso/saml/metadata","sso_redirect_url":config.grid_mgmt_ip}, "name": "test1", "session_timeout": 120,"comment":"test"}
    get_ref = ib_NIOS.wapi_request('POST', object_type="saml:authservice",fields=json.dumps(data))
    logging.info(get_ref)
    saml_ref= json.loads(get_ref)
    return saml_ref

def delete_saml_service(ref1):
    ref2=ref1
    get_ref = ib_NIOS.wapi_request('DELETE', object_type=ref2)
    logging.info(get_ref)
    del_ref= json.loads(get_ref)
    return del_ref

def delete_adminuser():
    reference=[]
    ref=ib_NIOS.wapi_request('GET',object_type="adminuser")
    ref=json.loads(ref)
    print ref
    for i in ref:
        if i['name']!='admin':
            reference.append(i['_ref'])
    for j in reference:
        ref=ib_NIOS.wapi_request('DELETE',object_type=j)
        print ref
   

def delete_admingroup():
    reference=[]
    ref=ib_NIOS.wapi_request('GET',object_type="admingroup")
    ref=json.loads(ref)
    print ref
    for i in ref:
        if i['name']!='admin-group' and i['name']!='saml-group' and i['name']!='cloud-api-only' and i['name']!='splunk-reporting-group':
           reference.append(i['_ref'])
    for j in reference:
        ref=ib_NIOS.wapi_request('DELETE',object_type=j)
        print ref

def enable_GUI_and_API_access_through_LAN_and_MGMT():
    ref=ib_NIOS.wapi_request('GET', object_type="grid")
    logging.info (ref)
    ref=json.loads(ref)[0]['_ref']
    logging.info(ref)
    data={"enable_gui_api_for_lan_vip":True}
    ref1=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
    logging.info (ref1)
    time.sleep(120)


class Network(unittest.TestCase):
    logging.basicConfig(filename='saml.log', filemode='w', level=logging.DEBUG)

    @pytest.mark.run(order=1)
    def test_001_change_lan_settings(self):
        cmd1 = 'whoami'
        cmd_result1 = subprocess.check_output(cmd1, shell=True)
        cmd_result1=cmd_result1.strip('\n')
        print cmd_result1
        #cmd = 'rm -v /home/'+cmd_result1+'/.ssh/known_hosts'
        #cmd_result = subprocess.check_output(cmd, shell=True)
        #print cmd_result
        os.system("netctl_system -i mgmt -S 10.36.0.0 -a vlanset -H "+config.vm_id)
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set interface mgmt')
        child.expect("Enable Management port\? \(y or n\):",timeout=30)
        child.sendline("y")
        child.expect('Enter Management IP address:')
        child.sendline(config.grid_mgmt_ip)
        child.expect('\[Default: 255.255.255.0\]:')
        child.sendline("255.255.0.0")
        child.expect('\[Default: 10.36.0.1\]:')
        child.sendline("10.36.0.1")
        child.expect("Configure Management IPv6 network settings\? \(y or n\):",timeout=30)
        child.sendline("n")
        child.expect("Restrict Support and remote console access to MGMT port\? \(y or n\):",timeout=30)
        child.sendline("n")
        child.expect("Is this correct\? \(y or n\):",timeout=30)
        child.sendline("y")
        child.expect("Are you sure\? \(y or n\):",timeout=30)
        child.sendline("y")
        sleep(100)
        child.expect('Infoblox >')
        child.sendline("exit")
        c= child.before
        return 1

    @pytest.mark.run(order=2)
    def test_002_enable_https_port(self):
        ref=ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_mgmt_ip)
        print config.grid_mgmt_ip
        print ref
        ref=json.loads(ref)[0]['_ref']
        #data={"enable_gui_api_for_lan_vip":"true","dns_resolver_setting": {"resolvers": ["10.0.2.35"]}}
        data={"dns_resolver_setting": {"resolvers": [config.resolver]},"enable_gui_api_for_lan_vip":True}
        ref1=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data),grid_vip=config.grid_mgmt_ip)
        print ref1
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('-bash-5.0#')
        child.sendline('ip route del default via 10.35.0.1 dev eth1 table main')
        child.expect('-bash-5.0#')
        child.sendline('ip route add default via 10.36.0.1 dev eth0 table main')
        child.sendline('exit')
        child.expect(pexpect.EOF)
        time.sleep(60)
        assert True
        
    @pytest.mark.run(order=3)
    def test_003_configure_saml_service(self):
        get_ref=ib_NIOS.wapi_request('GET', object_type="saml:authservice")
        print get_ref
        if get_ref!='[]':
            get_ref1=json.loads(get_ref)[0]['_ref']
            delete_saml_service(get_ref1)
        logging.info("getting saml service"+get_ref)
        get_ref1=json.loads(get_ref)
        if get_ref=='[]':
            ref=configure_saml_service()
            print ref
            if ref is not None:
                logging.info("Test case 1 passed as SAML service configured")
                assert True
                #delete_saml_service(ref)
            else:
                logging.info("Test case 1 failed as SAML service is not configured")
                assert False
    
    @pytest.mark.run(order=4)
    def test_004_Modify_SAML_Service(self):
        ref=ib_NIOS.wapi_request('GET',object_type='saml:authservice')
        print ref
        if ref == "[]":
            ref2=configure_saml_service()
            data_new={"name":"test2","session_timeout": 200,"comment":"test2"}
            get_ref = ib_NIOS.wapi_request('PUT', object_type=ref2,fields=json.dumps(data_new))
            get_ref1=json.loads(get_ref)
            if get_ref is not None:
                logging.info("Test case 3 passed as SAML service modified")
                assert True
                #delete_saml_service(get_ref1)            
            else:
                assert False
                logging.info("Test case 3 failed as SAML service not modified")
    
    @pytest.mark.run(order=5)
    def test_005_enabling_auto_create_user(self):
        data = []
        logging.info("get reference value for GROUP level")
        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup")
        logging.info(get_ref)
        res = json.loads(get_ref)
        logging.info ("----------------------Groups where conditions will be applied------------------------------------------")
        time.sleep(5)
        for i in res:
            if (i['name'] not in ('splunk-reporting-group', 'cloud-api-only')):  # it gets data /reference other than splunk and clou-api
                data.append(i)
        logging.info (data)
        for i in data:
            ref1=i['_ref']
            #logging.info ("reference value for group is:",ref1)
            data = {"saml_setting":{"auto_create_user":True}}
            response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data), grid_vip=config.grid_vip)
            time.sleep(5)
            logging.info(response)
            logging.info("=========================================================================")
            condition=get_reference_value_auto_create_user(ref1) #condition is to check what you have passed in data and what has updated after passing put command
            #print ("#######################################",condition)
            if (condition == (data['saml_setting']["auto_create_user"])):
                logging.info("Test case 1 Passed for Enabling Auto create user ")
                assert True
    
    @pytest.mark.run(order=6)
    def test_006_enabling_persist_auto_create_user(self):
        data = []
        logging.info("get reference value for GROUP level")
        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup")
        logging.info(get_ref)
        res = json.loads(get_ref)
        logging.info ("----------------------Groups where conditions will be applied------------------------------------------")
        time.sleep(5)
        for i in res:
            if (i['name'] not in ('splunk-reporting-group', 'cloud-api-only')):  # it gets data /reference other than splunk and clou-api
                data.append(i)
        logging.info (data)
        for i in data:
            ref1=i['_ref']
            #logging.info ("reference value for group is:",ref1)
            data = {"saml_setting":{"persist_auto_created_user":True}}
            response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data), grid_vip=config.grid_vip)
            time.sleep(5)
            logging.info(response)
            logging.info("=========================================================================")
            condition=get_reference_value_persist_auto_create_user(ref1) #condition is to check what you have passed in data and what has updated after passing put command
            #print ("#######################################",condition)
            if (condition == (data['saml_setting']["persist_auto_created_user"])):
                logging.info("Test case 2 Passed for enabling persist auto create user ")
                assert True
    
    @pytest.mark.run(order=7)
    def test_007_adding_SAML_admin_role(self):
        data = []
        logging.info("get reference value for GROUP level")
        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup")
        logging.info(get_ref)
        res = json.loads(get_ref)
        logging.info ("----------------------Groups where conditions will be applied------------------------------------------")
        time.sleep(5)
        for i in res:
            if (i['name'] not in ('splunk-reporting-group', 'cloud-api-only')):  # it gets data /reference other than splunk and clou-api
                data.append(i)
        #logging.info (">***********************",data)
        for i in data:
            ref1=i['_ref']
            #logging.info ("reference value for group is:",ref1)
            data = {"roles":["SAML Admin"]}
            response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data), grid_vip=config.grid_vip)
            time.sleep(5)
            logging.info(response)
            logging.info("=========================================================================")
            condition=get_ref_value_for_admingroup(ref1) #condition is to check what you have passed in data and what has updated after passing put comman
            print ("#######################################",condition)
            if (condition == (data['roles'])):
                assert True
                logging.info("Test case 6 Passed for adding SAML admin role")
    
    @pytest.mark.run(order=8)
    def test_008_removing_SAML_admin_role(self):
        data = []
        logging.info("get reference value for GROUP level")
        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup")
        logging.info(get_ref)
        res = json.loads(get_ref)
        logging.info ("----------------------Groups where conditions will be applied------------------------------------------")
        time.sleep(5)
        for i in res:
            if (i['name'] not in ('splunk-reporting-group', 'cloud-api-only')):  # it gets data /reference other than splunk and clou-api
                data.append(i)
        #logging.info (">***********************",data)
        for i in data:
            ref1=i['_ref']
            #logging.info ("reference value for group is:",ref1)
            data = {"roles":[]}
            response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data), grid_vip=config.grid_vip)
            time.sleep(5)
            logging.info(response)
            logging.info("=========================================================================")
            condition=get_ref_value_for_admingroup(ref1) #condition is to check what you have passed in data and what has updated after passing put comman
            print ("#######################################",condition)
            if (condition == (data['roles'])):
                assert True
                logging.info("Test case 6 Passed for removing SAML admin role")


    @pytest.mark.run(order=9)
    def test_009_add_SAML_permission(self):
        data = {"group":"saml-group","permission":"WRITE","resource_type":"SAML_AUTH_SERVICE"}
        response = ib_NIOS.wapi_request('POST', object_type="permission", fields=json.dumps(data), grid_vip=config.grid_vip)
        res1=json.loads(response)
        print res1
        get_ref = ib_NIOS.wapi_request('GET', object_type="permission")
        res=json.loads(get_ref)
        for i in res:
            if str(i['resource_type'])==data['resource_type']:
                assert True
                logging.info("Test case passed for adding SAML_permission")
    
    @pytest.mark.run(order=10)
    def test_010_delete_saml_service(ref1):
        get_ref=ib_NIOS.wapi_request('GET',object_type="saml:authservice")
        logging.info("reference value for saml service to delete")
        if get_ref!='[]':
            get_ref1=json.loads(get_ref)[0]['_ref']
            ref=delete_saml_service(get_ref1)
            get_ref=ib_NIOS.wapi_request('GET',object_type="saml:authservice")
            if get_ref==[]:
                ref2=configure_saml_service()
                ref3=json.loads(ref2)[0]['_ref']
                ref4=delete_saml_service(ref3)
                if ref4 is not None:
                    logging.info('test case 2 passed as SAML service is deleteed')
                    assert True
                else:
                    logging.info('test case 2 failed as SAML service is not deleteed')
                    assert False

    @pytest.mark.run(order=11)
    def test_011_Configure_SAML_Service_By_Upload(self):
        ref=ib_NIOS.wapi_request('GET',object_type='saml:authservice')
        if ref =='[]':
            filename="metadata.xml"
            logging.info("Test Uploading the Template with fileop")
            data = {"filename":filename}
            create_file = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadinit")
            logging.info(create_file)
            res = json.loads(create_file)
            token = json.loads(create_file)['token']
            url = json.loads(create_file)['url']   
            file1=url.split("/")
            os.system('curl -k1 -u admin:infoblox -F name=%s -F filedata=@%s %s'%(filename,filename,url))
            filename="/"+filename
            data = {"name":"saml","session_timeout":1234,"idp":{"idp_type": "OKTA","metadata_token":token,"sso_redirect_url":config.grid_mgmt_ip,"groupname":"groupname"}}
            create_file1 = ib_NIOS.wapi_request('POST', object_type="saml:authservice",fields=json.dumps(data))
            create_file1=json.loads(create_file1)
            if create_file1!="[]":
                assert True
                logging.info(create_file1)
                logging.info("Test case 8 passed for adding SAML service through file upload")
                #delete_saml_service(create_file1)
            else:
                assert False
        else:
            ref=json.loads(ref)
            ref2=ref[0]['_ref']
            delete_saml_service(ref2)
            filename="metadata.xml"
            logging.info("Test Uploading the Template with fileop")
            data = {"filename":filename}
            create_file = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadinit")
            logging.info(create_file)
            res = json.loads(create_file)
            token = json.loads(create_file)['token']
            url = json.loads(create_file)['url']
            file1=url.split("/")
            os.system('curl -k1 -u admin:infoblox -F name=%s -F filedata=@%s %s'%(filename,filename,url))
            filename="/"+filename
            data = {"name":"saml","session_timeout":1234,"idp":{"idp_type": "OKTA","metadata_token":token,"sso_redirect_url":config.grid_mgmt_ip,"groupname":"groupname"}}
            create_file1 = ib_NIOS.wapi_request('POST', object_type="saml:authservice",fields=json.dumps(data))
            print create_file1
            create_file1=json.loads(create_file1)
            if create_file1!="[]":
                logging.info(create_file1)
                logging.info("Test case 8 passed for adding SAML service through file upload")
                assert True
                delete_saml_service(create_file1)
            else:
                assert False
  
    @pytest.mark.run(order=12)    
    def test_012_set_auth_type_to_SAML_to_non_superuser_group(self):
        logging.info("Creating User Group for testing SAML only ")
        group={"name":"nonsuperusergroup","superuser":False,"access_method":["CLI"],"networking_show_commands":{"show_network":True}}
        get_ref = ib_NIOS.wapi_request('POST',object_type="admingroup", fields=json.dumps(group))
        print get_ref
        logging.info(get_ref)
        res_group = json.loads(get_ref)
        user={"name":"nonsuperuser","admin_groups":["nonsuperusergroup"],"auth_type":"SAML"}
        get_ref = ib_NIOS.wapi_request('POST',object_type="adminuser", fields=json.dumps(user))
        get_ref3=(json.loads(get_ref))
        get_ref3
        get_ref4=ib_NIOS.wapi_request('GET',object_type=get_ref3+"?_return_fields=auth_type")
        get_ref5=json.loads(get_ref4)
        if get_ref5["auth_type"]=="SAML":
            assert True
    
    @pytest.mark.run(order=13)
    def test_013_set_auth_type_to_SAML_LOCAL_for_super_user_group_saml_local(self):
        logging.info("Creating User Group for testing SAML/LOCAL")
        group={"name":"group2","superuser":True}
        get_ref = ib_NIOS.wapi_request('POST',object_type="admingroup", fields=json.dumps(group))
        logging.info(get_ref)
        res_group = json.loads(get_ref)
        user={"name":"saml_local","password":"infoblox","admin_groups":["group2"],"auth_type":"SAML_LOCAL"}
        get_ref = ib_NIOS.wapi_request('POST',object_type="adminuser", fields=json.dumps(user))
        get_ref3=(json.loads(get_ref))
        get_ref4=ib_NIOS.wapi_request('GET',object_type=get_ref3+"?_return_fields=auth_type")
        get_ref5=json.loads(get_ref4)
        if get_ref5["auth_type"]=="SAML_LOCAL":
            assert True
    
    @pytest.mark.run(order=14)
    def test_014_set_auth_type_to_LOCAL_for_super_user_group_local(self):
        logging.info("Creating User Group for testing LOCAL")
        group={"name":"group3","superuser":True}
        get_ref = ib_NIOS.wapi_request('POST',object_type="admingroup", fields=json.dumps(group))
        logging.info(get_ref)
        res_group = json.loads(get_ref)
        user={"name":"local","password":"infoblox","admin_groups":["group3"],"auth_type":"LOCAL"}
        get_ref = ib_NIOS.wapi_request('POST',object_type="adminuser", fields=json.dumps(user))
        get_ref3=(json.loads(get_ref))
        get_ref4=ib_NIOS.wapi_request('GET',object_type=get_ref3+"?_return_fields=auth_type")
        get_ref5=json.loads(get_ref4)
        if get_ref5["auth_type"]=="LOCAL":
            assert True
    
    @pytest.mark.run(order=15)
    def test_015_set_auth_type_to_SAML_LOCAL_with_single_char_saml_local(self):
        logging.info("Creating User with 1 char for testing SAML/LOCAL")
        user={"name":"single_char","password":"i","admin_groups":["group2"],"auth_type":"SAML_LOCAL"}
        get_ref = ib_NIOS.wapi_request('POST',object_type="adminuser", fields=json.dumps(user))
        print get_ref
        if type(get_ref)==tuple:
            if re.search(r'"text": "Enter a new password. It must contain 4-64 characters."',get_ref[1]):
                assert True
                logging.info("test case 14 execution passed")
            else:
                assert False
                logging.info("test case 14 execution failed")


    @pytest.mark.run(order=16)
    def test_016_login_to_CLI_as_SAML_with_superuser(self):
	user={"name":"arunchurimanjunath","password":"infoblox","admin_groups":["admin-group"],"auth_type":"SAML"}
       	get_ref = ib_NIOS.wapi_request('POST',object_type="adminuser", fields=json.dumps(user))
	get_ref3=(json.loads(get_ref))
        cmd='reset_console -H '+config.vm_id
        output = subprocess.check_output(cmd, shell=True)
        ref1=configure_SAML_Service_By_Upload()
        child = pexpect.spawn('console_connect -H '+config.vm_id)
    	child.logfile=sys.stdout
    	child.expect('Escape chara.*')
    	child.sendline('\n')
        child.sendline('\n')
        child.sendline('\n')
    	sleep(10)
    	child.expect('login:')
    	child.sendline('arunchurimanjunath')
    	sleep(10)
   	child.expect('OKTA SAML password:')
    	sleep(5)
    	child.sendline('Arun@123')
    	child.expect('Infoblox >')
    	child.sendline('show network')
        sleep(20)
    	child.expect('Infoblox >')
        c= child.before
        child.sendline('exit')
        child.expect('login:')
        assert re.search(r'.*Current LAN1 Network Settings.*',c)
        logging.info("Test Case 14 execution completed")

    @pytest.mark.run(order=17)
    def test_017_login_to_CLI_as_SAML_with_non_super_user(self):
        cmd='reset_console -H '+config.vm_id
        output = subprocess.check_output(cmd, shell=True)
        child = pexpect.spawn('console_connect -H '+config.vm_id)
        child.logfile=sys.stdout
        child.expect('Escape chara.*')
        child.sendline('\n')
        child.sendline('\n')
        child.sendline('\n')
        sleep(5)
        child.expect('login:')
        child.sendline('nonsuperuser')
        sleep(5)
        child.expect('OKTA SAML password:')
        sleep(5)
        child.sendline('Arun@123')
        child.expect('Infoblox >')
        child.sendline('show network')
        sleep(5)
        child.expect('Infoblox >')
        c= child.before
        child.sendline('exit')
        child.expect('login:')
        assert re.search(r'.*Current LAN1 Network Settings.*',c)
        logging.info("Test Case 14 execution completed")

    @pytest.mark.run(order=18)
    def test_018_login_to_CLI_as_SAML_with_super_user_when_auth_type_set_to_SAML_LOCAL(self):
        cmd='reset_console -H '+config.vm_id
        output = subprocess.check_output(cmd, shell=True)
        child = pexpect.spawn('console_connect -H '+config.vm_id)
        child.logfile=sys.stdout
        child.expect('Escape chara.*')
        child.sendline('\n')
        child.sendline('\n')
        child.sendline('\n')
        sleep(10)
        child.expect('login:')
        child.sendline('saml_local')
        sleep(10)
        child.expect('password:')
        sleep(5)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show network')
        sleep(20)
        child.expect('Infoblox >')
        c= child.before
        child.sendline('exit')
        child.expect('login:')
        assert re.search(r'.*Current LAN1 Network Settings.*',c)
        logging.info("Test Case 14 execution completed")

    @pytest.mark.run(order=16)
    def test_019_login_to_CLI_as_SAML_with_non_superuser_to_execute_command_set_httpd_client(self):
        cmd='reset_console -H '+config.vm_id
        output = subprocess.check_output(cmd, shell=True)
        child = pexpect.spawn('console_connect -H '+config.vm_id)
        child.logfile=sys.stdout
        child.expect('Escape chara.*')
        child.sendline('\n')
        child.sendline('\n')
        child.sendline('\n')
        sleep(10)
        child.expect('login:')
        child.sendline('nonsuperuser')
        sleep(10)
        child.expect('OKTA SAML password:')
        sleep(5)
        child.sendline('Arun@123')
        child.expect('Infoblox >')
        child.sendline('set httpd_client keepalive on')
        sleep(5)
        child.expect('Infoblox >')
        c= child.before
        child.sendline('exit')
        child.expect('login:')
        assert re.search(r'.*Error: The user does not have sufficient privileges to run this command.*',c)
        logging.info("Test Case 14 execution completed")

    @pytest.mark.run(order=16)
    def test_020_login_to_CLI_as_SAML_with_superuser_to_execute_command_set_httpd_client(self):
        cmd='reset_console -H '+config.vm_id
        output = subprocess.check_output(cmd, shell=True)
        child = pexpect.spawn('console_connect -H '+config.vm_id)
        child.logfile=sys.stdout
        child.expect('Escape chara.*')
        child.sendline('\n')
        child.sendline('\n')
        child.sendline('\n')
        sleep(10)
        child.expect('login:')
        child.sendline('arunchurimanjunath')
        sleep(10)
        child.expect('OKTA SAML password:')
        sleep(5)
        child.sendline('Arun@123')
        child.expect('Infoblox >')
        child.sendline('set httpd_client keepalive on')
        sleep(5)
        child.expect('Infoblox >')
        c= child.before
        child.sendline('exit')
        child.expect('login:')
        res=re.search(r'.*Error: The user does not have sufficient privileges to run this command.*',c)
        if res==None:
            logging.info("Test Case 19 execution completed")
            assert True
        else:
            assert False
            logging.info("Test Case 19 execution completed")


    @pytest.mark.run(order=19)
    def test_021_delete_saml_group(self):
        get_ref=ib_NIOS.wapi_request("GET",object_type="admingroup")
        get_ref=json.loads(get_ref)
        for name in get_ref:
            #print name['name']
            if name['name']=='saml-group':
                ref1=name['_ref']
                get_ref1=ib_NIOS.wapi_request("DELETE",object_type=ref1)
                if get_ref1[0]==400:
                    assert True
                    print("cannot delete")
                    logging.info("SAML group cannot be deleted")
                else:
                    assert False
                    print("test case failed")
                    logging.info("SAML group is deleted hence the test case got failed")
    
    @pytest.mark.run(order=20)
    def test_022_delete_saml_service(ref1):
        get_ref=ib_NIOS.wapi_request('GET',object_type="saml:authservice")
        logging.info("reference value for saml service to delete")
        if get_ref!='[]':
            get_ref1=json.loads(get_ref)[0]['_ref']
            ref=delete_saml_service(get_ref1)
            get_ref=ib_NIOS.wapi_request('GET',object_type="saml:authservice")
            if get_ref==[]:
                ref2=configure_saml_service()
                ref3=json.loads(ref2)[0]['_ref']
                ref4=delete_saml_service(ref3)
                if ref4 is not None:
                    logging.info('test case 2 passed as SAML service is deleteed')
                    assert True
                else:
                    logging.info('test case 2 failed as SAML service is not deleteed')
                    assert False

    @pytest.mark.run(order=21)
    def test_023_configure_saml_service_using_metadata_url(self):
        get_ref=ib_NIOS.wapi_request('GET', object_type="saml:authservice")
        print get_ref
        if get_ref!='[]':
            get_ref1=json.loads(get_ref)[0]['_ref']
            delete_saml_service(get_ref1)
        logging.info("getting saml service"+get_ref)
        get_ref1=json.loads(get_ref)
        if get_ref=='[]':
            ref=configure_saml_service()
            print ref
            if ref is  not None:
                assert True
                logging.info("Test case 1 passed as SAML service configured")
                #delete_saml_service(ref)
            else:
                assert True
                logging.info("Test case 1 failed as SAML service is not configured")
    
    @pytest.mark.run(order=22)
    def test_024_login_to_CLI_as_SAML_with_superuser_when_saml_is_configured_using_metadata_url(self):
        logging.info("login_to_CLI_as_SAML_with_superuser_when_saml_is_configured_using_metadata_url")
        cmd='reset_console -H '+config.vm_id
        output = subprocess.check_output(cmd, shell=True)
        ref1=configure_SAML_Service_By_Upload()
        child = pexpect.spawn('console_connect -H '+config.vm_id)
        child.logfile=sys.stdout
        child.expect('Escape chara.*')
        child.sendline('\n')
        child.sendline('\n')
        child.sendline('\n')
        sleep(10)
        child.expect('login:')
        child.sendline('arunchurimanjunath')
        sleep(10)
        child.expect('OKTA SAML password:')
        sleep(5)
        child.sendline('Arun@123')
        child.expect('Infoblox >')
        child.sendline('show network')
        sleep(20)
        child.expect('Infoblox >')
        c= child.before
        child.sendline('exit')
        child.expect('login:')
        assert re.search(r'.*Current LAN1 Network Settings.*',c)
        logging.info("Test Case 14 execution completed")

    @pytest.mark.run(order=23)
    def test_025_remove_mgmt_settings(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:',timeout=None)
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set interface mgmt')
        child.expect("Enable Management port\? \(y or n\):",timeout=30)
        child.sendline("n")
        child.expect("Disable Management port\? \(y or n\):",timeout=30)
        child.sendline("y")
        child.expect('Infoblox >')
        c= child.before
        child.sendline("exit")
        assert re.search(r'.*Management port has been disabled.*',c)
        logging.info("Test Case 14 execution completed")




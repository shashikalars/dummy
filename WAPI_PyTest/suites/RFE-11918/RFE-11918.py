import pytest
import unittest
import commands
import ib_utils.ib_NIOS as ib_NIOS
import subprocess
import re
import json
import json, ast
import os
import time
import sys
import logging
import pexpect
import config
from time import sleep
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv







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

def get_reference_value_auto_create_user(ref1):
    ref2=ref1
    get_ref = ib_NIOS.wapi_request('GET', object_type=ref2+"?_return_fields=saml_setting")
    logging.info(get_ref)
    res = json.loads(get_ref)#convert to dictionary
    ref1 =json.loads(get_ref)['saml_setting']['auto_create_user']
    #logging.info ("*********************************************************************************",ref1)
    return ref1

def get_reference_value_auto_create_user(ref1):
    ref2=ref1
    get_ref = ib_NIOS.wapi_request('GET', object_type=ref2+"?_return_fields=saml_setting",grid_vip=config.grid_vip6)
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

def map_remote_user_to_the_group(group='admin-group'):
    print("Selecting remote user to be mapped to the group "+group)
    response = ib_NIOS.wapi_request("GET",object_type="authpolicy")
    auth_policy_ref = json.loads(response)[0]['_ref']
    data={"default_group": group}
    response = ib_NIOS.wapi_request('PUT', ref=auth_policy_ref, fields=json.dumps(data), grid_vip=config.grid_vip)
    print(response)
    if bool(re.match("\"authpolicy*.",str(response))):
        print("Selected '"+group+"' for remote user mapping successfully")
        assert True
    else:
        print("Selecting '"+group+"' for remote user mapping failed")
        assert False

def delete_saml_service(ref1):
    ref2=ref1
    get_ref = ib_NIOS.wapi_request('DELETE', object_type=ref2, grid_vip=config.grid_mgmt_ipv6)
    logging.info(get_ref)
    del_ref= json.loads(get_ref)
    return del_ref



class RFE_11918(unittest.TestCase):


    @pytest.mark.run(order=1)
    def test_001_change_lan_settings(self):
        cmd1 = 'whoami'
        cmd_result1 = subprocess.check_output(cmd1, shell=True)
        cmd_result1=cmd_result1.strip('\n')
        print cmd_result1
        #cmd = 'rm -v /home/'+cmd_result1+'/.ssh/known_hosts'
        #cmd_result = subprocess.check_output(cmd, shell=True)
        #print cmd_result
       # os.system("netctl_system -i mgmt -S 10.36.0.0 -a vlanset -H "+config.vm_id)
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
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
    def test_002_add_default_route_as_mgmt_ip(self):
        ref=ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_mgmt_ip)
        print config.grid_mgmt_ip
        print ref
        ref=json.loads(ref)[0]['_ref']
        data={"dns_resolver_setting": {"resolvers": [config.resolver]},"enable_gui_api_for_lan_vip":True}
        ref1=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data),grid_vip=config.grid_mgmt_ip)
        print ref1
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect("#|\$",timeout=240)
        child.sendline('ip route del default via 10.35.0.1 dev eth1 table main')
        child.expect("#|\$",timeout=240)
        child.sendline('ip route add default via 10.36.0.1 dev eth0 table main')
        child.sendline('exit')
        child.expect(pexpect.EOF)
        time.sleep(60)
        assert True



    @pytest.mark.run(order=3)
    def test_003_Configure_SAML_Service_By_Upload(self):
        ref=ib_NIOS.wapi_request('GET',object_type='saml:authservice',grid_vip=config.grid_mgmt_ip)
        if ref =='[]':
            filename="metadata.xml"
            logging.info("Test Uploading the Template with fileop")
            data = {"filename":filename}
            create_file = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadinit",grid_vip=config.grid_mgmt_ip)
            logging.info(create_file)
            res = json.loads(create_file)
	    print("resr is",res)
            token = json.loads(create_file)['token']
	    print("token is",token)
            url = json.loads(create_file)['url']
            file1=url.split("/")
            os.system('curl -k1 -u admin:infoblox -F name=%s -F filedata=@%s %s'%(filename,filename,url))
            filename="/"+filename
            data = {"name":"saml","session_timeout":1234,"idp":{"idp_type": "OKTA","metadata_token":token,"sso_redirect_url":config.grid_mgmt_ip,"groupname":"groupname"}}
            create_file1 = ib_NIOS.wapi_request('POST', object_type="saml:authservice",fields=json.dumps(data),grid_vip=config.grid_mgmt_ip)
            create_file1=json.loads(create_file1)
            if create_file1!="[]":
                assert True
                logging.info(create_file1)
                logging.info("Test case  passed for adding SAML service through file upload")
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
            create_file = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadinit",grid_vip=config.grid_mgmt_ip)
            logging.info(create_file)
            res = json.loads(create_file)
            token = json.loads(create_file)['token']
            url = json.loads(create_file)['url']
            file1=url.split("/")
            os.system('curl -k1 -u admin:infoblox -F name=%s -F filedata=@%s %s'%(filename,filename,url))
            filename="/"+filename
            data = {"name":"saml","session_timeout":1234,"idp":{"idp_type": "OKTA","metadata_token":token,"sso_redirect_url":config.grid_mgmt_ip,"groupname":"groupname"}}
            create_file1 = ib_NIOS.wapi_request('POST', object_type="saml:authservice",fields=json.dumps(data),grid_vip=config.grid_mgmt_ip)
            print create_file1
            create_file1=json.loads(create_file1)
            if create_file1!="[]":
                logging.info(create_file1)
                logging.info("Test case  passed for adding SAML service through file upload")
                assert True
                delete_saml_service(create_file1)
            else:
                assert False


    @pytest.mark.run(order=4)
    def test_004_enable_super_user_for_saml_group(self):
	get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup?name=saml-group",grid_vip=config.grid_mgmt_ip)
	ref1 = json.loads(get_ref)[0]['_ref']
	print(ref1)
	data = {"superuser":True}
	response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_mgmt_ip)
	print(response)
	print(type(response))
	response =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=saml-group&_return_fields%2B=superuser", grid_vip=config.grid_mgmt_ip)
	print(response)
	assert re.search(r'"superuser": true',response)



    @pytest.mark.run(order=5)
    def test_005_enabling_auto_create_user(self):
        data = []
        logging.info("get reference value for GROUP level")
        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup",grid_vip=config.grid_mgmt_ip)
	print(get_ref)
        logging.info(get_ref)
        res = json.loads(get_ref)
	print("res is",res)
        logging.info ("----------------------Groups where conditions will be applied------------------------------------------")
        time.sleep(5)
        for i in res:
	    print("i is",i)
            if (i['name']  in ('saml-group')):  # it gets data /reference other than splunk and clou-api
                data.append(i)
        logging.info (data)
	print("data is",data)
        for i in data:
            ref1=i['_ref']
	    print("ref is",ref1)
            #logging.info ("reference value for group is:",ref1)
            data = {"saml_setting":{"auto_create_user":True}}
            response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data),grid_vip=config.grid_mgmt_ip)
            time.sleep(5)
            logging.info(response)


    @pytest.mark.run(order=6)
    def test_006_enabling_persist_auto_create_user(self):
        data = []
        logging.info("get reference value for GROUP level")
        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup",grid_vip=config.grid_mgmt_ip)
        logging.info(get_ref)
	print(get_ref)
        res = json.loads(get_ref)
	print(res)
        logging.info ("----------------------Groups where conditions will be applied------------------------------------------")
        time.sleep(5)
        for i in res:
            if (i['name']  in ('saml-group')):  # it gets data /reference other than splunk and clou-api
                data.append(i)
		print(data)
	print("i is",i)
        logging.info (data)
        for i in data:
            ref1=i['_ref']
	    print("resf is",ref1)
            #logging.info ("reference value for group is:",ref1)
            data = {"saml_setting":{"persist_auto_created_user":True}}
            response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data), grid_vip=config.grid_mgmt_ip)
            time.sleep(5)
            logging.info(response)



    @pytest.mark.run(order=7)
    def test_007_validate_all_three_TLS_protocols_are_enabled_for_default_setting(self):
        logging.info("validate all three tls protocols are enabled")
        cmd1 = 'whoami'
	cmd_result1 = subprocess.check_output(cmd1, shell=True)
        cmd_result1=cmd_result1.strip('\n')
        print cmd_result1
        cmd2 = 'rm -f  /home/'+cmd_result1+'/.ssh/known_hosts'
	response1 = subprocess.check_output(cmd2, shell=True)
	print("response is",response1)
        #cmd2 =  'rm -f /mnt/home/'+cmd+'/.ssh/known_hosts'
        #reponse2 = os.system(cmd2)
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show ssl_tls_protocols')
        child.expect('>')
        output = child.before
        if "TLSv1.0 TLSv1.1 TLSv1.2" in output:
            print("TLSv1.0,TLSv1.1,TLSv1.2 are active")
            logging.info("TLSv1.0,TLSv1.1,TLSv1.2 are active")
	    assert True
        else:
            print("TLSv1.0,TLSv1.1,TLSv1.2 are not active")
            logging.info("TLSv1.0,TLSv1.1,TLSv1.2 are not active")
	    assert False
	child.sendline('exit')
	child.close()
	sleep(10)
	

    @pytest.mark.run(order=8)
    def test_008_validate_TLS_protocol_TLSv1_active_for_default_setting_for_saml_port_with_openssl(self):
    	logging.info("validating TLS protocol TLSv1.0 active for saml port")
    	child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
    	child.logfile=sys.stdout
    	child.expect('#')
    	child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1")
    	sleep(5)
    	child.sendline('\n')
    	child.sendline('\n')
    	child.expect('#')
    	output = child.before
    	#print ("output is", output)
	if (("wrong version number" not in output) and ("ssl handshake failure" not in output) and ("Protocol  : TLSv1" in output)):
        	print("TLS protocols TLSv1.0 is active for default setting")
        	logging.info("TLS protocols TLSv1.0 is active for default setting")
        	assert True
    	else:
        	print("TLS protocols TLSv1.0 is not active for default setting")
        	logging.info("TLS protocols TLSv1.0 is not active for default setting")
        	assert False
	child.close()



    @pytest.mark.run(order=9)
    def test_009_validate_TLS_protocol_TLSv1_1_active_for_default_setting_for_saml_port_with_openssl(self):
    	logging.info("validating TLS protocol TLSv1.1 active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        #print ("output is", output)
	if (("wrong version number" not in output) and ("ssl handshake failure" not in output) and ("Protocol  : TLSv1.1" in output)):
        	print("TLS protocols TLSv1.1 is active for default setting")
        	logging.info("TLS protocols TLSv1.1 is active for default setting")
                assert True
        else:
                print("TLS protocols TLSv1.1 is not active for default setting for saml port")
                logging.info("TLS protocols TLSv1.1 is not active for default setting for saml port")
                assert False
	child.close()


    @pytest.mark.run(order=10)
    def test_010_validate_TLS_protocol_TLSv1_2_active_for_default_setting_for_saml_port_with_openssl(self):
    	logging.info("validating TLS protocol TLSv1.2 active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_2")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        #print ("output is", output)
	if (("wrong version number" not in output) and ("ssl handshake failure" not in output) and ("Protocol  : TLSv1.2" in output)):
                print("TLS protocols TLSv1.2 is active for default setting for saml port")
                logging.info("TLS protocols TLSv1.2 is active for default setting for saml port")
                assert True
        else:
                print("TLS protocols TLSv1.2 is not active for default setting")
                logging.info("TLS protocols TLSv1.2 is not active for default setting")
                assert False
	child.close()



    @pytest.mark.run(order=11)
    def test_011_validate_all_three_protocols_with_supported_ciphers_are_active_for_default_setting__for_saml_port_with_nmap(self):
        logging.info("validate all three protocols with supported ciphers are active for default setting")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("nmap -sV --script ssl-enum-ciphers -p 8765 "+config.grid_mgmt_ip)
        sleep(15)
        child.expect('#')
        output = child.before
        print ("output is", output)
        data = ['TLSv1.0','TLSv1.1','TLSv1.2','TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA','TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256','TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256','TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA','TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384','TLS_RSA_WITH_AES_128_CBC_SHA','TLS_RSA_WITH_AES_128_CBC_SHA256','TLS_RSA_WITH_AES_128_GCM_SHA256','TLS_RSA_WITH_AES_256_CBC_SHA','TLS_RSA_WITH_AES_256_CBC_SHA256','TLS_RSA_WITH_AES_256_GCM_SHA384']
        if (("TLS_DHE_RSA_WITH_AES_128_CBC_SHA" not in output) and ("TLS_DHE_RSA_WITH_AES_128_CBC_SHA256" not in output) and ("TLS_DHE_RSA_WITH_AES_128_GCM_SHA256" not in output) and ("TLS_DHE_RSA_WITH_AES_256_CBC_SHA" not in output) and ("TLS_DHE_RSA_WITH_AES_256_CBC_SHA256" not in output) and ("TLS_DHE_RSA_WITH_AES_256_GCM_SHA384" not in output) and ("TLS_RSA_WITH_3DES_EDE_CBC_SHA" not in output)):
        	flag=False
		for i in data:
			if i in output:
				print(i,"ciphers is active")
				flag=True
			else:
				print(i,"ciphers is not active")
				assert False
		if flag==True:
			print("supported ciphers are acitve")
			assert True
		else:
			print("supported ciphers are not active")
			assert False
	else:
		print("weak ciphers are active")
		assert False
	print("strong ciphers are acitve and weak ciphers are inactive")
	child.close()
			 

    @pytest.mark.run(order=12)
    def test_012_validate_all_three_protocols_are_active_for_saml_port_with_testssl_sh_script(self):
        logging.info("validate all three protocols are active saml port with testssl_sh script")
	cmd= 'scp -pr testssl.sh-3.0.6 root@' +config.grid_mgmt_ip+':/tmp'
        response=os.popen(cmd).read()
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
	child.sendline('ls')
	child.expect('#')
        child.sendline('mount -o remount,rw /')
        child.expect('#')
        child.sendline('cp /tmp/testssl.sh-3.0.6/testssl.sh  /infoblox/one/bin/')
        child.expect('#')
        child.sendline('export TESTSSL_INSTALL_DIR=/tmp')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --protocols --fast --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(30)
        child.expect('Done')
        output = child.before
        output = output.replace("\x1b[m\x1b[1;33m","").replace("\x1b[m\x1b[0;33m","").replace("\x1b[m","").replace("\x1b[0;32m","").replace("\x1b[1;32m","")
        #print("output is",output)
        if (("TLS 1      offered" in output) and  ("TLS 1.1    offered" in output) and ("TLS 1.2    offered" in output)):
                print("all 3 TLS protocols are enabled for default setting")
                logging.info("all 3 TLS protocols are enabled for default setting")
                assert True
        else:
                print("all 3  TLS protocols are not enabled for default setting")
                logging.info("all 3  TLS protocols are not enabled for default setting")
                assert False
	child.close()
	sleep(10)




    @pytest.mark.run(order=13)
    def test_013_validate_all_three_protocols_with_supported_ciphers_are_active_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('export TESTSSL_INSTALL_DIR=/tmp')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh -E --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(30)
        child.expect('Done')
        output = child.before
        #print("output is",output)
        data = ['TLS 1','TLS 1.1','TLS 1.2','ECDHE-RSA-AES256-GCM-SHA384','ECDHE-RSA-AES256-SHA','AES256-GCM-SHA384','AES256-SHA256','AES256-SHA','ECDHE-RSA-AES128-GCM-SHA256','ECDHE-RSA-AES128-SHA256','ECDHE-RSA-AES128-SHA','AES128-GCM-SHA256','AES128-SHA256','AES128-SHA']
        for i in data:
            if i in output:
                print(i,"is active")
                logging.info("all 3 protocols with supported ciphers are active")
		assert True
            else:
		print(i,"is not active")
                logging.info("all 3 protocols with supported ciphers are not active")
		assert False
	child.close()
	sleep(10)



    @pytest.mark.run(order=14)
    def test_014_validated_3DES_ciphers_are_active_for_default_setting_saml_port_with_testssl_sh_script(self):
        logging.info("validate  3DES ciphers are active for default setting for saml port with testssl.sh script")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --vulnerable '+config.grid_mgmt_ip+':8765 ')
        sleep(40)
        child.expect('Done')
        output = child.before
        output = output.replace("\x1b[m","").replace("\x1b[1;32m","").replace("\x1b[0;31m","").replace("\x1b[0;32m","").replace("\x1b[1;33m","")
        print('output is',output)
	if (("SWEET32 (CVE-2016-2183, CVE-2016-6329)    not vulnerable" in output) and ("RC4 (CVE-2013-2566, CVE-2015-2808)        no RC4 ciphers detected" in output)):
            logging.info("3DES ciphers are active for default setting for saml port with testssl.sh script")
            print("3DES ciphers are active for default setting for saml port with testssl.sh script")
            assert True
        else:
            logging.info("3DES ciphers are not active for saml port with testssl.sh script")
            print("3DES ciphers are not active for saml port with testssl.sh script")
            assert False
	child.close()
        sleep(10)


    @pytest.mark.run(order=15)
    def test_015_login_to_CLI_as_SAML_with_superuser(self):
        user={"name":config.okta_username ,"password":config.okta_password,"admin_groups":["saml-group"],"auth_type":"SAML"}
        get_ref = ib_NIOS.wapi_request('POST',object_type="adminuser", fields=json.dumps(user))
        get_ref3=(json.loads(get_ref))
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
        child.sendline(config.okta_username)
        sleep(10)
        child.expect('OKTA SAML password:')
        sleep(5)
        child.sendline(config.okta_password)
        child.expect('Infoblox >')
        child.sendline('show network')
        sleep(20)
        child.expect('Infoblox >')
        c= child.before
        child.sendline('exit')
        child.expect('login:')
        assert re.search(r'.*Current LAN1 Network Settings.*',c)
        logging.info("Test Case  execution completed")
	



    @pytest.mark.run(order=16)
    def test_016_enabling_tls_protocols_TLSv1(self):
	logging.info("enabling tls protocols TLSv1")
	child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        log("start","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('set ssl_tls_settings override')
        child.expect('>')
        child.sendline('set ssl_tls_protocols enable TLSv1.0')
        child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSv1.1')
        child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSV1.2')
        child.expect('>')
        child.sendline('show ssl_tls_protocols')
	child.expect('>')
        output = child.before
  	#print ("output is" ,output)
	sleep(120)
	log("stop","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        if "Current configuration for the SAML  : TLSv1.0" in output:
		print("Tls protocols set to TLSv1.0")
                logging.info("Tls protocols set to TLSv1.0")
                assert True
        else:
                print("Tls protocols not set to TLSv1.0")
                logging.info("Tls protocols not set to TLSV1.0")
                assert False
	data = ["Restarting saml","TLS PROTOCOL for the SAML is set to PROTOCOL_TLSv1"]
	for i in data:
	    	logs=logv(i,"/infoblox/var/infoblox.log",config.grid_mgmt_ip)
            	print("logs are" , logs)
		if logs != None:
			print("validated tls protocols set to TLSv1 in logs")
	 	        assert True
		else:
		 	print("error")
			assert False
	child.sendline('exit')
	child.close()
        sleep(120)
            

      

    @pytest.mark.run(order=17)
    def test_017_validate_TLS_protocol_TLSv1_active_when_disabled_weak_cipher_for_saml_port_with_openssl(self):
	logging.info("validating TLS protocol TLSv1.0 active for saml port")
	child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
	child.logfile=sys.stdout
	child.expect('#')
	child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1")
	sleep(5)
	child.sendline('\n')
	child.sendline('\n')
	child.expect('#')
	output = child.before
	print ("output is", output)
	if (("wrong version number" not in output) and ("ssl handshake failure" not in output) and ("Protocol  : TLSv1" in output)):
		print("TLS protocols TLSv1.0 is active when disabled weak cipher")
		logging.info("TLS protocols TLSv1.0 is active when disabled weak cipher")
		assert True
	else:
		print("TLS protocols TLSv1.0 is not active when disabled weak cipher")
		logging.info("TLS protocols TLSv1.0 is not active when disabled weak cipher")
		assert False
	child.close()
	sleep(10)
	
    
    @pytest.mark.run(order=18)
    def test_018_validate_TLS_protocol_TLSv1_1_not_active_when_disabled_weak_cipher_for_saml_port_with_openssl(self):
	logging.info("validating TLS protocols TLSv1.1 not active for saml port")
	child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
	child.logfile=sys.stdout
	child.expect('#')
	child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_1")
	sleep(5)
	child.sendline('\n')
	child.sendline('\n')
	child.expect('#')
	output = child.before
	print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
	    print("TLS protocols TLSv1.1 not active when disabled weak cipher")
	    logging.info("TLS protocols TLSv1.1 not active when disabled weak cipher")
	    assert True
	else:
	    print("TLS protocols TLSv1.1  active when disabled weak cipher")
	    logging.info("TLS protocols TLSv1.1  active when disabled weak cipher")
	    assert False
        child.close()

    @pytest.mark.run(order=19)
    def test_019_validate_TLS_protocol_TLSv1_2_not_active_when_disabled_weak_cipher_for_saml_port_with_openssl(self):
	logging.info("validating TLS protocols TLSv1.2 not active for saml port")
	child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
	child.logfile=sys.stdout
	child.expect('#')
	child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_2")
	sleep(5)
	child.sendline('\n')
	child.sendline('\n')
	child.expect('#')
	output = child.before
	print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
		print("TLS protocols TLSv1.2 not active when disabled weak cipher")
		logging.info("TLS protocols TLSv1.2 not active when disabled weak cipher")
		assert True
	else:
		print("TLS protocols TLSv1.2  active when disabled weak cipher")
		logging.info("TLS protocols TLSv1.2  active when disabled weak cipher")
		assert False
        child.close()
        sleep(10)


    @pytest.mark.run(order=20)
    def test_020_disabling_weak_cipher(self):
        logging.info("disabling weak ciphers")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        log("start","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set ssl_tls_ciphers disable 15')
        child.expect('>')
        #child.sendline('set ssl_tls_ciphers disable 17')
        #child.expect('>')
        child.sendline('show ssl_tls_ciphers')
        child.expect('>')
        output = child.before
        print("outputis",output)
	sleep(140)
        log("stop","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        if ("TLS_RSA_WITH_3DES_EDE_CBC_SHA           disabled") in output:
                print("TLS_RSA_WITH_3DES_EDE_CBC_SHA    ciphers is disabled")
                logging.info("TLS_RSA_WITH_3DES_EDE_CBC_SHA  is disabled")
                assert True
        else:
                print("TLS_RSA_WITH_3DES_EDE_CBC_SHA    ciphers not disable")
                logging.info("TLS_RSA_WITH_3DES_EDE_CBC_SHA  is not disabled")
                assert False
        data = "DES-CBC3-SHA"
        logs=logv(data,"/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        print("logs are", logs)
        if logs == None:
                print("restarted saml and validated ciphers binding to saml")
                assert True
        else:
                print("error")
                assert False
        child.sendline('exit')
        child.close()
		
	    
    @pytest.mark.run(order=21)
    def test_021_validate_TLS_protocol_TLSv1_is_active_and_disabled_weak_ciphers_for_saml_port_with_nmap(self):
	logging.info("validating TLS protocol TLSv1.0 active and disabled weak ciphers for saml port with nmap")
	child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
	child.logfile=sys.stdout
	child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
	child.sendline("nmap -sV --script ssl-enum-ciphers -p 8765 "+config.grid_mgmt_ip)
	sleep(15)
        child.expect('#')
	output1 = child.before
	print("output is", output1)
	if (("TLSv1.0" in output1) and ("TLS_RSA_WITH_3DES_EDE_CBC_SHA"  not in output1)):
		print('validated TLSv1.0 is active and TLS_RSA_WITH_3DES_EDE_CBC_SHA is not active for saml port with nmap')
		assert True
	else:
		print('validated TLSv1.0 is not active and TLS_RSA_WITH_3DES_EDE_CBC_SHA is  active for saml port with nmap')
		assert False
        child.close()
        sleep(10)			 
		


    @pytest.mark.run(order=22)
    def test_022_validate_TLS_protocol_TLSv1_active_when_disabled_weak_cipher_for_saml_port_with_testssl_sh_script(self):
	logging.info("validate TLS protocol TLSv1 active for saml port with testssl.sh script")   
	child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
	child.logfile=sys.stdout
	child.expect('#')
	child.sendline('cd /tmp/testssl.sh-3.0.6')
	child.expect('#')
	child.sendline('export TESTSSL_INSTALL_DIR=/tmp')
	child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --protocols --fast --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(25)
        child.expect('Done')
        output = child.before
        output1 = output.replace("\x1b[m\x1b[1;33m","").replace("\x1b[m\x1b[0;33m","").replace("\x1b[m","").replace("\x1b[0;32m","")
	print("output is",output1)
	if "TLS 1      offered" in output1: 	
		print("validated TLSv1 is enabled when disabled weak cipher with testssl.sh script")
		logging.info("validated TLSv1 is enabled when disabled weak cipher with testssl.sh script")
		assert True
	else:
		print("validated TLSv1 is not enabled when disabled weak cipher with testssl.sh script")
		logging.info("validated TLSv1 is not enabled when disabled weak cipher with testssl.sh script")
		assert False
	child.close()
        sleep(10)
	
 


    @pytest.mark.run(order=23)
    def test_023_validate_weak_ciphers_are_not_active_for_saml_port_with_testssl_sh_script(self):
        logging.info("validate weak ciphers are not active for saml port with testssl_sh script")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh -E --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(35)
        child.expect('Done')
        output = child.before
	print ("output is", output)
        if "DES-CBC3-SHA" in output:
                print("Validated weak ciphers  active for saml port with testssl.sh script")
                logging.info("Validated weak ciphers  active for saml port with testssl.sh script")
                assert False
        else:
                print("Validated weak ciphers  not active for saml port with testssl.sh script")
                logging.info("Validated weak ciphers not  active for saml port with testssl.sh script")
                assert True
	child.close()


    @pytest.mark.run(order=24)
    def test_024_validate_RC4_and_3DES_ciphers_are_not_active_when_disabled_weak_cipher_for_saml_port_with_testssl_sh_script(self):
	logging.info("validate RC4 and 3DES ciphers are not active for saml port with testssl.sh script")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
	child.sendline('cd /tmp/testssl.sh-3.0.6')
	child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --vulnerable '+config.grid_mgmt_ip+':8765 ')
        sleep(40)
        child.expect('Done')
        output = child.before
	output = output.replace("\x1b[m","").replace("\x1b[1;32m","").replace("\x1b[0;31m","").replace("\x1b[0;32m","").replace("\x1b[m\x1b[0;33m","")
	print ("output is", output)
	if (("SWEET32 (CVE-2016-2183, CVE-2016-6329)    not vulnerable" in output) and ("RC4 (CVE-2013-2566, CVE-2015-2808)        no RC4 ciphers detected" in output)):
                logging.info("Validated RC4 and 3DES ciphers not active for saml port with testssl.sh script")
		print("Validated RC4 and 3DES ciphers not active when disabled weak cipher")
                assert True
        else:
                print("Validated RC4 and 3DES ciphers active disabled weak cipher with testssl.sh script")
                logging.info("Validated RC4 and 3DES ciphers active disabled weak cipher with testssl.sh script")
                assert False
        child.close()
        sleep(10)

    @pytest.mark.run(order=25)
    def test_025_login_to_CLI_as_SAML_with_superuser(self):
        cmd='reset_console -H '+config.vm_id
        output = subprocess.check_output(cmd, shell=True)
        child = pexpect.spawn('console_connect -H '+config.vm_id)
        child.logfile=sys.stdout
        child.expect('Escape chara.*')
        child.sendline('\n')
        child.sendline('\n')
        child.sendline('\n')
        child.expect('login:')
        child.sendline(config.okta_username)
        sleep(10)
        child.expect('OKTA SAML password:')
        sleep(5)
        child.sendline(config.okta_password)
        child.expect('Infoblox >')
        child.sendline('show network')
        sleep(20)
        child.expect('Infoblox >')
        c= child.before
        child.sendline('exit')
        child.expect('login:')
        assert re.search(r'.*Current LAN1 Network Settings.*',c)
        logging.info("Test Case  execution completed")
        print("SSO login worked")




    @pytest.mark.run(order=26)
    def test_026_enabling_tls_protocols_TLSv1_1(self):
	logging.info("enabling tls protocols TLSv1_1")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        data = ["Restarting saml","TLS PROTOCOL for the SAML is set to PROTOCOL_TLSv1_1"]
	log("start","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set ssl_tls_protocols enable TLSv1.1')
        child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSv1.2')
        child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSV1.0')
        child.expect('>')
        child.sendline('show ssl_tls_protocols')
        child.expect('>')
        output = child.before
        #print ("output is" ,output)
        sleep(120)
        log("stop","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        if "Current configuration for the SAML  : TLSv1.1" in output:
		print("Tls protocols set to TLSv1.1")
                logging.info("Tls protocols set to TLSv1.1")
                assert True
        else:
                print("Tls protocols not set to TLSv1.1")
                logging.info("Tls protocols not set to TLSV1.1")
                assert False
        for i in data:
                logs=logv(i,"/infoblox/var/infoblox.log",config.grid_mgmt_ip)
                print("logs are" , logs)
                if logs != None:
                        print("validated tls protocols set to TLSv1.1 in logs")
                        assert True
                else:
                        print("TLSv1.1 is not active in logs")
                        assert False
	child.sendline('exit')
	child.close()
	sleep(10)

    @pytest.mark.run(order=27)
    def test_027_validate_TLS_protocol_TLSv1_1_active_when_disabled_weak_cipher_for_saml_port_with_openssl(self):
	logging.info("validating TLS protocol TLSv1.1 active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("wrong version number" not in output) and ("ssl handshake failure" not in output) and ("Protocol  : TLSv1.1" in output)):
		print("TLS protocols TLSv1.1 is active when_disabled_weak_cipher")
		logging.info("TLS protocols TLSv1.1 is active when_disabled_weak_cipher")
                assert True
        else:
                print("TLS protocols TLSv1.1 is not active when_disabled_weak_cipher")
                logging.info("TLS protocols TLSv1.1 is not active when_disabled_weak_cipher")
                assert False
	child.close()
        
    @pytest.mark.run(order=28)
    def test_028_validate_TLS_protocol_TLSv1_0_not_active_when_disabled_weak_cipher_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.0 not active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
		print("TLS protocols TLSv1.0  not active when_disabled_weak_cipher")
		logging.info("TLS protocols TLSv1.0 not when_disabled_weak_cipher")
            	assert True
        else:
	        logging.info("TLS protocols TLSv1.0  active when_disabled_weak_cipher")
		print("TLS protocols TLSv1.0  active when_disabled_weak_cipher")
                assert False
	child.close()


    @pytest.mark.run(order=29)
    def test_029_validate_TLS_protocol_TLSv1_2_not_active_when_disabled_weak_cipher_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.2 not active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_2")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
	    print("TLS protocols TLSv1.2  not active when disabled weak cipher")     
            logging.info("TLS protocols TLSv1.2 not active when disabled weak cipher")
            assert True
        else:
            print("TLS protocols TLSv1.2  active when disabled weak cipher")
            logging.info("TLS protocols TLSv1.2  active when disabled weak cipher")
            assert False
	child.close()
	sleep(10)



    @pytest.mark.run(order=30)
    def test_030_validate_TLS_protocol_TLSv1_1_active_and_weak_ciphers_not_active_for_saml_port_with_nmap(self):
        logging.info("validating TLS protocol TLSv1.1 active for saml port with nmap")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("nmap -sV --script ssl-enum-ciphers -p 8765 "+config.grid_mgmt_ip)
        sleep(15)
        child.expect('#')
        output1 = child.before
        print ("output is", output1)
        if (("TLSv1.1" in output1) and ("TLS_RSA_WITH_3DES_EDE_CBC_SHA"  not in output1)):
                 print('validated TLSv1.1 is active and TLS_RSA_WITH_3DES_EDE_CBC_SHA is  not active for saml port with nmap')
		 logging.info('validated TLSv1.1 is active and TLS_RSA_WITH_3DES_EDE_CBC_SHA is active for saml port with nmap')
                 assert True
        else:
                 print('validated TLS protocols TLSv1.1 not active and ciphers is active for saml port with nmap')
		 logging.info('validated TLS protocols TLSv1.1 not active and ciphers is  active for saml port with nmap')
                 assert False
	child.close()



    @pytest.mark.run(order=31)
    def test_031_validate_TLS_protocol_TLSv1_1_active_when_disabled_weak_cipher_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --protocols --fast --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(25)
        child.expect('Done')
        output = child.before
        output1 = output.replace("\x1b[m\x1b[1;33m","").replace("\x1b[m\x1b[0;33m","").replace("\x1b[m","").replace("\x1b[0;32m","")
        print("output is",output1)
        if "TLS 1.1    offered" in output1:
                print("validated TLSv1.1 is enabled when disabled weak cipher with testssl.sh script")
                logging.info("validated TLSv1.1 is enabled when disabled weak cipher with testssl.sh script")
                assert True
        else:
                print("validated TLSv1.1 is not enabled when disabled weak cipher with testssl.sh script")
                logging.info("validated TLSv1.1 is not enabled when disabled weak cipher with testssl.sh script")
                assert False
	child.close()


    @pytest.mark.run(order=32)
    def test_032_validated_weak_ciphers_are_not_active_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('export TESTSSL_INSTALL_DIR=/tmp')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh -E --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(25)
        child.expect('Done')
        output = child.before
        print("output is",output)
        if "DES-CBC3-SHA" in output:
                print("validated weak ciphers are  active for saml port with testssl.sh script")
                logging.info("validated weak ciphers are  active for saml port with testssl.sh script")
                assert False
        else:
                print("validated weak ciphers are not active for saml port with testssl.sh script")
		logging.info("validated weak ciphers are not active for saml port with testssl.sh script")
                assert True
	child.close()


    @pytest.mark.run(order=33)
    def test_033_validated_RC4_and_3DES_ciphers_are_not_active_when_disabled_weak_cipher_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('export TESTSSL_INSTALL_DIR=/tmp')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --vulnerable '+config.grid_mgmt_ip+':8765 ')
        sleep(40)
        child.expect('Done')
        output = child.before
        #print("output is",output)
        output = output.replace("\x1b[m","").replace("\x1b[1;32m","").replace("\x1b[0;31m","").replace("\x1b[0;32m","")
        print("output isss",output)
	if (("SWEET32 (CVE-2016-2183, CVE-2016-6329)    not vulnerable" in output) and ("RC4 (CVE-2013-2566, CVE-2015-2808)        no RC4 ciphers detected" in output)):
                logging.info("Validated RC4 and 3DES ciphers not active when disabled weak cipher  with testssl.sh script")
		print("Validated RC4 and 3DES ciphers not active when disabled weak cipher  with testssl.sh script")
                assert True
        else:
                print("Validated RC4 and 3DES ciphers active when disabled weak cipher with testssl.sh script")
                logging.info("Validated RC4 and 3DES ciphers active when disabled weak cipher with testssl.sh script")
                assert False
	child.close()
	sleep(10)

    @pytest.mark.run(order=34)
    def test_034_login_to_CLI_as_SAML_with_superuser(self):
        cmd='reset_console -H '+config.vm_id
        output = subprocess.check_output(cmd, shell=True)
        print(cmd)
	print(output)
	child = pexpect.spawn('console_connect -H '+config.vm_id)
        child.logfile=sys.stdout
        child.expect('Escape chara.*')
        child.sendline('\n')
        child.sendline('\n')
        child.sendline('\n')
        child.expect('login:')
        child.sendline(config.okta_username)
        sleep(10)
        child.expect('OKTA SAML password:')
        sleep(5)
        child.sendline(config.okta_password)
        child.expect('Infoblox >')
        child.sendline('show network')
        sleep(20)
        child.expect('Infoblox >')
        c= child.before
        child.sendline('exit')
        child.expect('login:')
        assert re.search(r'.*Current LAN1 Network Settings.*',c)
        logging.info("Test Case  execution completed")
	print("SSO login worked")



    @pytest.mark.run(order=35)
    def test_035_enabling_tls_protocols_TLSv1_2(self):
	logging.info("enabling tls protocols TLSv1_2")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        data = ["Restarting saml","TLS PROTOCOL for the SAML is set to PROTOCOL_TLSv1_2"]
        log("start","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set ssl_tls_protocols enable TLSv1.2')
        child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSv1.0')
        child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSV1.1')
        child.expect('>')
        child.sendline('show ssl_tls_protocols')
        child.expect('>')
        output = child.before
        sleep(120)
        log("stop","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        if "Current configuration for the SAML  : TLSv1.2" in output:
		print("Tls protocols set to TLSv1.2")
                logging.info("Tls protocols set to TLSv1.2")
                assert True
        else:
                print("Tls protocols not set to TLSv1.2")
                logging.info("Tls protocols not set to TLSV1.2")
                assert False
        for i in data:
                logs=logv(i,"/infoblox/var/infoblox.log",config.grid_mgmt_ip)
                print("logs are" , logs)
                if logs != None:
                        print("validated tls protocols set to TLSv1.2 in logs")
                        assert True
                else:
                        print("validated tls protocols  not set to TLSv1.2 in logs")
                        assert False
	child.sendline('exit')
	child.close()
	sleep(10)


    @pytest.mark.run(order=36)
    def test_036_validate_TLS_protocol_TLSv1_0_not_active_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.0 not active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLS protocols TLSv1.0  not active when disabled weak cipher")
                logging.info("TLS protocols TLSv1.0 not active when disabled weak cipher")
                assert True
        else:
                logging.info("TLS protocols TLSv1.0  active when disabled weak cipher")
                print("TLS protocols TLSv1.0  active when disabled weak cipher")
                assert False
        child.close()

    @pytest.mark.run(order=37)
    def test_037_validate_TLS_protocol_TLSv1_2_active_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.2 not active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_2")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("wrong version number" not in output) and ("ssl handshake failure" not in output) and ("Protocol  : TLSv1.2" in output)):
                print("TLS protocols TLSv1.2  active when disabled weak cipher")
                logging.info("TLS protocols TLSv1.2 active when disabled weak cipher")
                assert True
        else:
                logging.info("TLS protocols TLSv1.2 not  active when disabled weak cipher")
                print("TLS protocols TLSv1.2 not active when disabled weak cipher")
                assert False
        child.close()



    @pytest.mark.run(order=38)
    def test_038_validate_TLS_protocol_TLSv1_1_not_active_when_disabled_weak_cipher_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.1 not active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
            print("TLS protocols TLSv1.1  not active when disabled weak cipher for saml port")
            logging.info("TLS protocols TLSv1.1 not active when disabled weak cipher for saml port")
            assert True
        else:
            print("TLS protocols TLSv1.1  active when disabled weak cipher for saml port")
            logging.info("TLS protocols TLSv1.1  active when disabled weak cipher for saml port")
            assert False
	child.close()


    @pytest.mark.run(order=39)
    def test_039_validate_TLS_protocol_TLSv1_2_active_and_weak_ciphers_not__active_for_saml_port_with_nmap(self):
        logging.info("validating TLS protocol TLSv1.2 active and weak ciphers are not active for saml port with nmap")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("nmap -sV --script ssl-enum-ciphers -p 8765 "+config.grid_mgmt_ip)
        sleep(15)
        child.expect('#')
        output1 = child.before
	print ("output is", output1)
	if (("TLSv1.2" in output1) and ("TLS_RSA_WITH_3DES_EDE_CBC_SHA"  not in output1)):
		print('validated TLSv1.2 is active and TLS_RSA_WITH_3DES_EDE_CBC_SHA not active for saml port with nmap')
		logging.info('validated TLSv1.2 is active and TLS_RSA_WITH_3DES_EDE_CBC_SHA not active for saml port with nmap')
                assert True
        else:
                print('TLS protocols TLSv1.2 not active and cipher is  active for saml port')
		logging.info('TLS protocols TLSv1.2 not active and cipher is  active for saml port')
                assert False
	child.close()

    @pytest.mark.run(order=40)
    def test_040_validate_TLS_protocol_TLSv1_2_is_active_when_disabled_weak_cipher_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --protocols --fast --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(25)
        child.expect('Done')
        output = child.before
        output1 = output.replace("\x1b[m\x1b[1;33m","").replace("\x1b[m\x1b[0;33m","").replace("\x1b[m","").replace("\x1b[1;32m","")
        print("output is",output1)
        if "TLS 1.2    offered" in output1:
                print("validated TLSv1.2 is enabled when disabled weak cipher with testssl.sh script")
                logging.info("validated TLSv1.2 is enabled when disabled weak cipher with testssl.sh script")
                assert True
        else:
                print("validated TLSv1.2 is not enabled when disabled weak cipher with testssl.sh script")
                logging.info("validated TLSv1.2 is not enabled when disabled weak cipher with testssl.sh script")
                assert False
	child.close()
	sleep(10)



    @pytest.mark.run(order=41)
    def test_041_validate_weak_ciphers_are_not_active_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh -E --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(25)
        child.expect('Done')
        output = child.before
        print("output is",output)
        if "DES-CBC3-SHA" in output:
		print("validated weak ciphers are active for saml port with testssl.sh script")
		logging.info("validated weak ciphers are active for saml port with testssl.sh script")
                assert False
        else:
		print("validated weak ciphers not  active for saml port with testssl.sh script")
		logging.info("validated weak ciphers not  active for saml port with testssl.sh script")
                assert True
	child.close()


    @pytest.mark.run(order=42)
    def test_042_validated_RC4_and_3DES_ciphers_are_not_active_when_disabled_weak_cipher_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --vulnerable '+config.grid_mgmt_ip+':8765 ')
        sleep(40)
        child.expect('Done')
        output = child.before
        output = output.replace("\x1b[m","").replace("\x1b[1;32m","").replace("\x1b[0;31m","").replace("\x1b[0;32m","")
        print("output is",output)
	if (("SWEET32 (CVE-2016-2183, CVE-2016-6329)    not vulnerable" in output) and ("RC4 (CVE-2013-2566, CVE-2015-2808)        no RC4 ciphers detected" in output)):
		print("Validated RC4 and 3DES ciphers not active when disabled weak cipher with testssl.sh script")
		logging.info("Validated RC4 and 3DES ciphers not active when disabled weak cipher with testssl.sh script")
                assert True
        else:
		print("Validated RC4 and 3DES ciphers  active when disabled weak cipher with testssl.sh script")
		logging.info("Validated RC4 and 3DES ciphers active when disabled weak cipher with testssl.sh script")
                assert False
	child.close()
	sleep(10)




    @pytest.mark.run(order=43)
    def test_043_login_to_CLI_as_SAML_with_superuser(self):
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
        child.sendline(config.okta_username)
        sleep(10)
        child.expect('OKTA SAML password:')
        sleep(5)
        child.sendline(config.okta_password)
        child.expect('Infoblox >')
        child.sendline('show network')
        sleep(20)
        child.expect('Infoblox >')
        c= child.before
        child.sendline('exit')
        child.expect('login:')
        assert re.search(r'.*Current LAN1 Network Settings.*',c)
        logging.info("Test Case  execution completed")



    @pytest.mark.run(order=44)
    def test_044_enabling_tls_protocols_TLSv1_0_and_TLSV1_1(self):
	logging.info("enabling tls protocols TLSv1_0 and TLSv1.1")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        data = ["Restarting saml","TLS PROTOCOL for the SAML is set to PROTOCOL_TLSv1_1"]
        log("start","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set ssl_tls_protocols enable TLSv1.0')
        child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSV1.2')
        child.expect('>')
	child.sendline('set ssl_tls_protocols enable TLSV1.1')
	child.expect('>')
        child.sendline('show ssl_tls_protocols')
        child.expect('>')
        output = child.before
        #print ("output is" ,output)
        sleep(120)
        log("stop","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        if "Current configuration for the SAML  : TLSv1.1" in output:
		print("Tls protocols set to TLSv1.1")
                logging.info("Tls protocols set to TLSv1.1")
                assert True
        else:
                print("Tls protocols not set to TLSv1.1")
                logging.info("Tls protocols not set to TLSV1.1")
                assert False
        for i in data:
                logs=logv(i,"/infoblox/var/infoblox.log",config.grid_mgmt_ip)
                print("logs are" , logs)
                if logs != None:
                        print("validated tls protocols set to TLSv1.1 in logs")
                        assert True
                else:
                        print("validated tls protocols not set to TLSv1.1 in logs")
                        assert False
	child.sendline('exit')
	child.close()
	sleep(10)



    @pytest.mark.run(order=45)
    def test_045_validate_TLS_protocol_TLSv1_1_active_when_TLSv1_0_and_TLSV1_1_are_enabled_for_saml_port_with_openssl(self):
	logging.info("validating TLS protocol TLSv1.1 active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("wrong version number" not in output) and ("ssl handshake failure" not in output) and ("Protocol  : TLSv1.1" in output)):
		print("TLSv1.1 is  active when TLSv1.0 and TLSv1.1 are enabled")
                logging.info("TLS protocols TLSv1.1 is   active when TLSv1.0 and TLSv1.1 are enabled")
                assert True
        else:
                print("TLS protocols TLSv1.1 is not  active when TLSv1.0 and TLSv1.1 are enabled")
                logging.info("TLS protocols TLSv1.1 is not active when TLSv1.0 and TLSv1.1 are enabled")
                assert False
	child.close()


    @pytest.mark.run(order=46)
    def test_046_validate_TLS_protocol_TLSv1_0_not_active_when_TLSv1_0_and_TLSV1_1_are_enabled_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.0 not active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLS protocols TLSv1.0  not active when TLSv1.0 and TLSv1.1 are enabled")
                logging.info("TLS protocols TLSv1.0 not active when TLSv1.0 and TLSv1.1 are enabled")
                assert True
        else:
                logging.info("TLS protocols TLSv1.0  active when TLSv1.0 and TLSv1.1 are enabled")
		print("TLS protocols TLSv1.0  active when TLSv1.0 and TLSv1.1 are enabled")
                assert False
	child.close()


    @pytest.mark.run(order=47)
    def test_047_validate_TLS_protocol_TLSv1_2_not_active_when_TLSv1_0_and_TLSV1_1_are_enabled_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.2 not active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_2")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLS protocols TLSv1.2  not active for saml port")
                logging.info("TLS protocols TLSv1.2 not active for saml port")
                assert True
        else:
                logging.info("TLS protocols TLSv1.2  active for saml port")
                assert False
	child.close()
	sleep(10)

    @pytest.mark.run(order=48)
    def test_048_validate_TLS_protocol_TLSv1_1_active_and_weak_ciphers_not_active_for_saml_port_with_nmap(self):
        logging.info("validating TLS protocol TLSv1.1 active and weak ciphers are not active for saml port with nmap")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("nmap -sV --script ssl-enum-ciphers -p 8765 "+config.grid_mgmt_ip)
        sleep(15)
        child.expect('#')
        output1 = child.before
        print("output is", output1)
        if (("TLSv1.1" in output1) and ("TLS_RSA_WITH_3DES_EDE_CBC_SHA"  not in output1)):
                 print('validated TLSv1.1 is active and TLS_RSA_WITH_3DES_EDE_CBC_SHA not active for saml port with nmap ')
		 logging.info('validated TLSv1.1 is active and TLS_RSA_WITH_3DES_EDE_CBC_SHA not active for saml port with nmap ')
                 assert True
        else:
                 print('TLS protocols TLSv1.1  not active and weak ciphers active for saml port')
		 logging.info('TLS protocols TLSv1.1  not active and weak ciphers active for saml port')
                 assert False
	child.close()




    @pytest.mark.run(order=49)
    def test_049_validate_TLS_protocol_TLSv1_1_active_when_TLSv1_0_and_TLSV1_1_are_enabled_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --protocols --fast --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(25)
        child.expect('Done')
        output = child.before
        output1 = output.replace("\x1b[m\x1b[1;33m","").replace("\x1b[m\x1b[0;33m","").replace("\x1b[m","").replace("\x1b[1;32m","").replace("\x1b[0;32m","")
        print("output is",output1)
        if "TLS 1.1    offered" in output1:
                print("validated TLSv1.1 is enabled when TLSv1.0 and TLSv1.1 are enabled with testssl.sh script")
                logging.info("validated TLSv1.1 is enabled when TLSv1.0 and TLSv1.1 are enabledwith testssl.sh script")
                assert True
        else:
                print("validated TLSv1.1 is not enabled when TLSv1.0 and TLSv1.1 are enabled with testssl.sh script")
                logging.info("validated TLSv1.1 is not enabled when TLSv1.0 and TLSv1.1 are enabled with testssl.sh script")
                assert False
	child.close()
	sleep(10)




    @pytest.mark.run(order=50)
    def test_050_validate_weak_ciphers_are_not_active_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh -E --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(25)
        child.expect('Done')
        output = child.before
        print("output is",output)
        if "DES-CBC3-SHA" in output:
		print("Validated weak ciphers  active for saml port with testssl.sh script")
		logging.info("Validated weak ciphers  active for saml port with testssl.sh script")
                assert False
        else:
		print("Validated weak ciphers  not active for saml port with testssl.sh script")
		logging.info("Validated weak ciphers not  active for saml port with testssl.sh script")
                assert True
	child.close()


    @pytest.mark.run(order=51)
    def test_051_validate_RC4_and_3DES_ciphers_are_not_active_when_TLSv1_0_and_TLSV1_1_are_enabled_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --vulnerable '+config.grid_mgmt_ip+':8765 ')
        sleep(40)
        child.expect('Done')
        output = child.before
        output = output.replace("\x1b[m","").replace("\x1b[1;32m","").replace("\x1b[0;31m","").replace("\x1b[0;32m","")
        print("output isss",output)
	if (("SWEET32 (CVE-2016-2183, CVE-2016-6329)    not vulnerable" in output) and ("RC4 (CVE-2013-2566, CVE-2015-2808)        no RC4 ciphers detected" in output)):
                logging.info("Validated RC4 and 3DES ciphers not active when TLSv1.0 and TLSv1.1 are enabled for saml port with testssl.sh script")
		print("Validated RC4 and 3DES ciphers not active when TLSv1.0 and TLSv1.1 are enabled for saml port with testssl.sh script")
		assert True
        else:
		print("Validated RC4 and 3DES ciphers active when TLSv1.0 and TLSv1.1 are enabled with testssl.sh script")
		logging.info("Validated RC4 and 3DES ciphers active when TLSv1.0 and TLSv1.1 are enabled  with testssl.sh script")
                assert False
	child.close()
	sleep(10)



    @pytest.mark.run(order=52)
    def test_052_login_to_CLI_as_SAML_with_superuser(self):
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
        child.sendline(config.okta_username)
        sleep(10)
        child.expect('OKTA SAML password:')
        sleep(5)
        child.sendline(config.okta_password)
        child.expect('Infoblox >')
        child.sendline('show network')
        sleep(20)
        child.expect('Infoblox >')
        c= child.before
        child.sendline('exit')
        child.expect('login:')
        assert re.search(r'.*Current LAN1 Network Settings.*',c)
        logging.info("Test Case  execution completed")



    @pytest.mark.run(order=53)
    def test_053_enabling_tls_protocols_TLSv1_0_and_TLSV1_2(self):
	logging.info("enabling tls protocols TLSv1_0 and TLSv1.2")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        data = ["Restarting saml","TLS PROTOCOL for the SAML is set to PROTOCOL_TLSv1_2"]
        log("start","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set ssl_tls_protocols enable TLSv1.0')
        child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSv1.1')
        child.expect('>')
        child.sendline('set ssl_tls_protocols enable TLSV1.2')
        child.expect('>')
        child.sendline('show ssl_tls_protocols')
        child.expect('>')
        output = child.before
        #print ("output is" ,output)
        sleep(120)
        log("stop","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        if "Current configuration for the SAML  : TLSv1.2" in output:
		print("Tls protocols set to TLSv1.2")
                logging.info("Tls protocols set to TLSv1.2")
                assert True
        else:
                print("Tls protocols not set to TLSv1.2")
                logging.info("Tls protocols not set to TLSV1.2")
                assert False
        for i in data:
                logs=logv(i,"/infoblox/var/infoblox.log",config.grid_mgmt_ip)
                print("logs are" , logs)
                if logs != None:
                        print("validated tls protocols set to TLSv1.2 in logs when TLSv1.0 and TLSv1.2 are enabled")
                        assert True
                else:
                        print("validated tls protocols not set to TLSv1.2 in logs when TLSv1.0 and TLSv1.2 are enabled")
                        assert False
	child.sendline('exit')
	child.close()
	sleep(10)



    @pytest.mark.run(order=54)
    def test_054_validate_TLS_protocol_TLSv1_2_active_when_TLSv1_0_and_TLSV1_2_are_enabled_for_saml_port_with_openssl(self):
	logging.info("validating TLS protocol TLSv1.2  active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_2")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("wrong version number" not in output) and ("ssl handshake failure" not in output) and ("Protocol  : TLSv1.2" in output)):
		print("TLSv1.2 is  active when TLSv1.0 and TLSv1.2 are enabled")
                logging.info("TLS protocols TLSv1.2 is   active when TLSv1.0 and TLSv1.2 are enabled")
                assert True
        else:
                print("TLS protocols TLSv1.2 is not  active when TLSv1.0 and TLSv1.2 are enabled")
                logging.info("TLS protocols TLSv1.2 is not active when TLSv1.0 and TLSv1.2 are enabled")
                assert False
	child.close()

    @pytest.mark.run(order=55)
    def test_055_validate_TLS_protocol_TLSv1_0_not_active_when_TLSv1_0_and_TLSV1_2_are_enabled_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.0 not active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLS protocols TLSv1.0  not active when TLSv1.0 and TLSv1.2 are enabled")
                logging.info("TLS protocols TLSv1.0 not active when TLSv1.0 and TLSv1.2 are enabled")
                assert True
        else:
                print("TLS protocols TLSv1.0  active when TLSv1.0 and TLSv1.2 are enabled")
		logging.info("TLS protocols TLSv1.0  active when TLSv1.0 and TLSv1.2 are enabled")
                assert False
	child.close()


    @pytest.mark.run(order=56)
    def test_056_validate_TLS_protocol_TLSv1_1_not_active_when_TLSv1_0_and_TLSV1_2_are_enabled_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.1 not active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLS protocols TLSv1.1  not active when TLSv1.0 and TLSv1.2 are enabled")
                logging.info("TLS protocols TLSv1.1 not active when TLSv1.0 and TLSv1.2 are enabled")
                assert True
        else:
                logging.info("TLS protocols TLSv1.1  active when TLSv1.0 and TLSv1.2 are enabled")
		print("TLS protocols TLSv1.1  active when TLSv1.0 and TLSv1.2 are enabled")
                assert False
	child.close()
	sleep(10)


    @pytest.mark.run(order=57)
    def test_057_validate_TLS_protocol_TLSv1_2_active__and_weak_ciphers_not_active_for_saml_port_with_nmap(self):
        logging.info("validating TLS protocol TLSv1.2 active for saml port with nmap")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("nmap -sV --script ssl-enum-ciphers -p 8765 "+config.grid_mgmt_ip)
        sleep(15)
        child.expect('#')
        output1 = child.before
        print("output is", output1)
        if (("TLSv1.2" in output1) and ("TLS_RSA_WITH_3DES_EDE_CBC_SHA"  not in output1) and ("TLS_RSA_WITH_RC4_128_SHA" not in output1)):
                 print('validated TLSv1.2 is active and TLS_RSA_WITH_3DES_EDE_CBC_SHA and TLS_RSA_WITH_RC4_128_SHA are not active for saml port with nmap ')
		 logging.info('validated TLSv1.2 is active and TLS_RSA_WITH_3DES_EDE_CBC_SHA and TLS_RSA_WITH_RC4_128_SHA are not active for saml port with nmap ')
                 assert True
        else:
                 print('TLS protocols TLSv1.2 not active and weak ciphers are active for saml port')
		 logging.info('TLS protocols TLSv1.2 not active and weak ciphers are active for saml port')
                 assert False
	child.close()


    @pytest.mark.run(order=58)
    def test_058_validate_TLS_protocol_TLSv1_2_active_when_TLSv1_0_and_TLSV1_2_are_enabled_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --protocols --fast --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(25)
        child.expect('Done')
        output = child.before
        output1 = output.replace("\x1b[m\x1b[1;33m","").replace("\x1b[m\x1b[0;33m","").replace("\x1b[m","").replace("\x1b[1;32m","")
        print("output is",output1)
        if "TLS 1.2    offered" in output1:
                print("validated TLSv1.2 is enabled  when TLSv1.0 and TLSv1.2 are enabled with testssl.sh script")
                logging.info("validated TLSv1.2 is enabled when TLSv1.0 and TLSv1.2 are enabled with testssl.sh script")
                assert True
        else:
                print("validated TLSv1.2 is not enabled when TLSv1.0 and TLSv1.2 are enabled with testssl.sh script")
                logging.info("validated TLSv1.2 is not enabled when TLSv1.0 and TLSv1.2 are enabled with testssl.sh script")
                assert False
	child.close()
	sleep(10)


    @pytest.mark.run(order=59)
    def test_059_validate_weak_ciphers_are_not_active_when_TLSv1_0_and_TLSV1_2_are_enabled_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('export TESTSSL_INSTALL_DIR=/tmp')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh -E --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(25)
        child.expect('Done')
        output = child.before
        print("output is",output)
        if "DES-CBC3-SHA" in output:
                print("weak ciphers  active for saml port with testssl.sh script")
                logging.info(" weak ciphers  active for saml port with testssl.sh script")
                assert False
        else:
                print("weak ciphers  not active for saml port with testssl.sh script")
                logging.info("weak ciphers not  active for saml port with testssl.sh script")
                assert True
	child.close()



    @pytest.mark.run(order=60)
    def test_060_validate_RC4_and_3DES_ciphers_are_not_active_when_TLSv1_0_and_TLSV1_2_are_enabled_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('export TESTSSL_INSTALL_DIR=/tmp')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --vulnerable '+config.grid_mgmt_ip+':8765 ')
        sleep(40)
        child.expect('Done')
        output = child.before
        output = output.replace("\x1b[m","").replace("\x1b[1;32m","").replace("\x1b[0;31m","").replace("\x1b[0;32m","")
	print ("output is", output)
	if (("SWEET32 (CVE-2016-2183, CVE-2016-6329)    not vulnerable" in output) and ("RC4 (CVE-2013-2566, CVE-2015-2808)        no RC4 ciphers detected" in output)):
		print("Validated RC4 and 3DES  ciphers not active when TLSv1.0 and TLSv1.2 are enabled with testssl.sh script")
                logging.info("Validated RC4 and 3DES  ciphers not active when TLSv1.0 and TLSv1.2 are enabled with testssl.sh script")
                assert True
        else:
                print("Validated RC4 and 3DES ciphers active when TLSv1.0 and TLSv1.2 are enabled with testssl.sh script")
                logging.info("Validated RC4 and 3DES ciphers active when TLSv1.0 and TLSv1.2 are enabled with testssl.sh script")
                assert False
	child.close()
	sleep(10)


    @pytest.mark.run(order=61)
    def test_061_login_to_CLI_as_SAML_with_superuser(self):
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
        child.sendline(config.okta_username)
        sleep(10)
        child.expect('OKTA SAML password:')
        sleep(5)
        child.sendline(config.okta_password)
        child.expect('Infoblox >')
        child.sendline('show network')
        sleep(20)
        child.expect('Infoblox >')
        c= child.before
        child.sendline('exit')
        child.expect('login:')
        assert re.search(r'.*Current LAN1 Network Settings.*',c)
        logging.info("Test Case  execution completed")



    @pytest.mark.run(order=62)
    def test_062_enabling_tls_protocols_TLSv1_1_and_TLSV1_2(self):
	logging.info("enabling tls protocols TLSv1_1 and TLSv1.2")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        data = ["Restarting saml","TLS PROTOCOL for the SAML is set to PROTOCOL_TLSv1_2"]
        log("start","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set ssl_tls_protocols enable TLSv1.1')
        child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSv1.0')
        child.expect('>')
        child.sendline('set ssl_tls_protocols enable TLSV1.2')
        child.expect('>')
        child.sendline('show ssl_tls_protocols')
        child.expect('>')
        output = child.before
        #print ("output is" ,output)
        sleep(120)
        log("stop","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        if "Current configuration for the SAML  : TLSv1.2" in output:
		print("Tls protocols set to TLSv1.2")
                logging.info("Tls protocols set to TLSv1.2")
                assert True
        else:
                print("Tls protocols not set to TLSv1.2")
                logging.info("Tls protocols not set to TLSV1.2")
                assert False
        for i in data:
                logs=logv(i,"/infoblox/var/infoblox.log",config.grid_mgmt_ip)
                print("logs are" , logs)
                if logs != None:
                        print("validated tls protocols set to TLSv1.2 in logs when TLSv1.1 and TLSv1.2 are enabled")
                        assert True
                else:
                        print("validated tls protocols not set to TLSv1.2 in logs when TLSv1.1 and TLSv1.2 are enabled")
                        assert False

	child.sendline('exit')
	child.close()
	sleep(10)


    @pytest.mark.run(order=63)
    def test_063_validate_TLS_protocol_TLSv1_2_active_when_TLSv1_1_and_TLSV1_2_are_enabled_for_saml_port_with_openssl(self):
	logging.info("validate TLS protocol TLSv1.2  active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_2")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("wrong version number" not in output) and ("ssl handshake failure" not in output) and ("Protocol  : TLSv1.2" in output)):
                print("TLSv1.2 is  active when TLSv1.1 and TLSv1.2 are enabled")
                logging.info("TLS protocols TLSv1.2 is   active when TLSv1.1 and TLSv1.2 are enabled")
                assert True
        else:
                print("TLS protocols TLSv1.2 is not  active when TLSv1.1 and TLSv1.2 are enabled")
                logging.info("TLS protocols TLSv1.2 is not active when TLSv1.1 and TLSv1.2 are enabled")
                assert False
	child.close()


    @pytest.mark.run(order=64)
    def test_064_validate_TLS_protocol_TLSv1_0_not_active_when_TLSv1_1_and_TLSV1_2_are_enabled_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.0 not active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLS protocols TLSv1.0  not active when TLSv1.1 and TLSv1.2 are enabled")
                logging.info("TLS protocols TLSv1.0 not active when TLSv1.1 and TLSv1.2 are enabled")
                assert True
        else:
                logging.info("TLS protocols TLSv1.0  active when TLSv1.1 and TLSv1.2 are enabled")
		print("TLS protocols TLSv1.0  active when TLSv1.1 and TLSv1.2 are enabled")
                assert False
	child.close()
	sleep(10)


    @pytest.mark.run(order=65)
    def test_065_validate_TLS_protocol_TLSv1_1_not_active_when_TLSv1_1_and_TLSV1_2_are_enabled_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.1 not active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLS protocols TLSv1.1  not active when TLSv1.1 and TLSv1.2 are enabled")
                logging.info("TLS protocols TLSv1.1 not active when TLSv1.1 and TLSv1.2 are enabled")
                assert True
        else:
                logging.info("TLS protocols TLSv1.1  active when TLSv1.1 and TLSv1.2 are enabled")
		print("TLS protocols TLSv1.1  active when TLSv1.1 and TLSv1.2 are enabled")
                assert False
	child.close()


    @pytest.mark.run(order=66)
    def test_066_validate_TLS_protocol_TLSv1_2_active_and_weak_ciphers_not_active_for_saml_port_with_nmap(self):
        logging.info("validating TLS protocol TLSv1.2 active for saml port with nmap")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("nmap -sV --script ssl-enum-ciphers -p 8765 "+config.grid_mgmt_ip)
        sleep(15)
        child.expect('#')
        output1 = child.before
        print("output is", output1)
        if (("TLSv1.2" in output1) and ("TLS_RSA_WITH_3DES_EDE_CBC_SHA"  not in output1) and ("TLS_RSA_WITH_RC4_128_SHA" not in output1)):
                 print('validated TLSv1.2 is active and TLS_RSA_WITH_3DES_EDE_CBC_SHA and TLS_RSA_WITH_RC4_128_SHA are not active for saml port with nmap ')
                 assert True
        else:
                 print('TLS protocols TLSv1.2 not active and weak ciphers are active for saml port')
                 assert False
	child.close()
	sleep(10)


    @pytest.mark.run(order=67)
    def test_067_validate_TLS_protocol_TLSv1_2_active_when_TLSv1_1_and_TLSV1_2_are_enabled_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --protocols --fast --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(45)
        child.expect('Done')
        output = child.before
        output1 = output.replace("\x1b[m\x1b[1;33m","").replace("\x1b[m\x1b[0;33m","").replace("\x1b[m","").replace("\x1b[1;32m","")
        print("output is",output1)
        if "TLS 1.2    offered" in output1:
                print("validated TLSv1.2 is enabled when TLSv1.1 and TLSv1.2 are enabled  with testssl.sh script")
                logging.info("validated TLSv1.2 is enabled when TLSv1.1 and TLSv1.2 are enabled with testssl.sh script")
                assert True
        else:
                print("validated TLSv1.2 is not enabled when TLSv1.1 and TLSv1.2 are enabled with testssl.sh script")
                logging.info("validated TLSv1.2 is not enabled when TLSv1.1 and TLSv1.2 are enabled with testssl.sh script")
                assert False
	child.close()


    @pytest.mark.run(order=68)
    def test_068_validated_weak_ciphers_are_not_active_when_TLSv1_1_and_TLSV1_2_are_enabled_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh -E --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(40)
        child.expect('Done')
        output = child.before
        print("output is",output)
        if "DES-CBC3-SHA" in output:
                print("Validated weak ciphers  active for saml port with testssl.sh script")
                logging.info("Validated weak ciphers  active for saml port with testssl.sh script")
                assert False
        else:
                print("Validated weak ciphers  not active for saml port with testssl.sh script")
                logging.info("Validated weak ciphers not  active for saml port with testssl.sh script")
                assert True
	child.close()
	sleep(10)



    @pytest.mark.run(order=69)
    def test_069_validate_RC4_and_3DES_ciphers_are_not_active_when_TLSv1_1_and_TLSV1_2_are_enabled_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --vulnerable '+config.grid_mgmt_ip+':8765 ')
        sleep(40)
        child.expect('Done')
        output = child.before
        output = output.replace("\x1b[m","").replace("\x1b[1;32m","").replace("\x1b[0;31m","").replace("\x1b[0;32m","")
        print("output isss",output)
	if (("SWEET32 (CVE-2016-2183, CVE-2016-6329)    not vulnerable" in output) and ("RC4 (CVE-2013-2566, CVE-2015-2808)        no RC4 ciphers detected" in output)):
		print("RC4 and 3DES ciphers not active when_TLSv1_1_and_TLSV1_2_are_enabled with testssl.sh script")
                logging.info("Validated RC4 and 3DES ciphers not active when TLSv1.1 and TLSv1.2 are enabled with testssl.sh script")
                assert True
        else:
                print("Validated RC4 and 3DES ciphers active when TLSv1.1 and TLSv1.2 are enabled with testssl.sh script")
                logging.info("Validated RC4 and 3DES ciphers active when TLSv1.1 and TLSv1.2 are enabled  with testssl.sh script")
                assert False
	child.close()




    @pytest.mark.run(order=70)
    def test_070_login_to_CLI_as_SAML_with_superuser(self):
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
        child.sendline(config.okta_username)
        sleep(10)
        child.expect('OKTA SAML password:')
        sleep(5)
        child.sendline(config.okta_password)
        child.expect('Infoblox >')
        child.sendline('show network')
        sleep(20)
        child.expect('Infoblox >')
        c= child.before
        child.sendline('exit')
        child.expect('login:')
        assert re.search(r'.*Current LAN1 Network Settings.*',c)
        logging.info("Test Case  execution completed")



    @pytest.mark.run(order=71)
    def test_071_enabling_tls_protocols_TLSv1_2_and_enabling_single_cipher(self):
            logging.info("enabling tls protocols TLSv1.2 and single cipher")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip)
            child.logfile=sys.stdout
            log("start","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
            child.expect('password')
            child.sendline('infoblox')
            child.expect('>')
            child.sendline('set ssl_tls_protocols enable TLSv1.2')
            child.expect('>')
	    child.sendline('set ssl_tls_protocols disable TLSv1.0')
            child.expect('>')
	    child.sendline('set ssl_tls_protocols disable TLSv1.1')
            child.expect('>')
            child.sendline('set ssl_tls_ciphers disable 19')
            child.expect('>')
            child.sendline('set ssl_tls_ciphers disable 18')
            child.expect('>')
            child.sendline('set ssl_tls_ciphers disable 17')
            child.expect('>')
            child.sendline('set ssl_tls_ciphers disable 16')
            child.expect('>')
            child.sendline('set ssl_tls_ciphers disable 15')
            child.expect('>')
            child.sendline('set ssl_tls_ciphers disable 14')
            child.expect('>')
            child.sendline('set ssl_tls_ciphers disable 13')
            child.expect('>')
            child.sendline('set ssl_tls_ciphers disable 12')
            child.expect('>')
            child.sendline('set ssl_tls_ciphers disable 11')
            child.expect('>')
            child.sendline('set ssl_tls_ciphers disable 10')
            child.expect('>')
            child.sendline('set ssl_tls_ciphers disable 9')
            child.expect('>')
            child.sendline('set ssl_tls_ciphers disable 8')
            child.expect('>')
            child.sendline('set ssl_tls_ciphers disable 7')
            child.expect('>')
            child.sendline('set ssl_tls_ciphers disable 6')
            child.expect('>')
            child.sendline('set ssl_tls_ciphers disable 5')
            child.expect('>')
            child.sendline('set ssl_tls_ciphers disable 4')
            child.expect('>')
            child.sendline('set ssl_tls_ciphers disable 2')
            child.expect('>')
            child.sendline('set ssl_tls_ciphers disable 1')
            child.expect('>')
	    child.sendline('show ssl_tls_ciphers')
	    child.expect('>')
	    output = child.before
	   # print("output is",output)
            sleep(120)
            log("stop","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
	    data = ['TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA      disabled','TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256 disabled','TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 disabled','TLS_DHE_DSS_WITH_AES_256_CBC_SHA        disabled','TLS_DH_RSA_WITH_3DES_EDE_CBC_SHA        disabled','TLS_DH_DSS_WITH_3DES_EDE_CBC_SHA        disabled','TLS_RSA_WITH_AES_256_CBC_SHA256         disabled','TLS_RSA_WITH_AES_256_GCM_SHA384         disabled','TLS_RSA_WITH_AES_128_CBC_SHA256         disabled','TLS_DHE_DSS_WITH_AES_128_CBC_SHA256     disabled','TLS_DHE_DSS_WITH_AES_128_GCM_SHA256     disabled','TLS_DHE_DSS_WITH_AES_256_CBC_SHA256     disabled','TLS_DHE_DSS_WITH_AES_256_GCM_SHA384     disabled','TLS_DHE_DSS_WITH_AES_128_CBC_SHA        disabled','TLS_RSA_WITH_AES_256_CBC_SHA            disabled','TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384   disabled','TLS_RSA_WITH_AES_128_CBC_SHA            disabled','TLS_DHE_RSA_WITH_AES_128_CBC_SHA256     disabled','TLS_RSA_WITH_AES_128_GCM_SHA256         disabled','TLS_DHE_RSA_WITH_AES_256_CBC_SHA256     disabled','TLS_DHE_RSA_WITH_AES_256_CBC_SHA        disabled','TLS_DHE_RSA_WITH_AES_128_CBC_SHA        disabled','TLS_DHE_RSA_WITH_AES_256_GCM_SHA384     disabled','TLS_DHE_RSA_WITH_AES_128_GCM_SHA256     disabled','TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256   disabled','TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256   disabled','TLS_RSA_WITH_RC4_128_SHA                disabled','TLS_RSA_WITH_3DES_EDE_CBC_SHA           disabled']
	    for i in data:
		if i in output: 
               		logging.info("single cipher TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA is enabled")
			assert True
            	else:
                	print(i)
                	logging.info("single cipher TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA  is not enabled")
			assert False
	    print("single cipher is enabled")
	    data = ["Restarting saml","TLSv1_2","ECDHE-RSA-AES256-SHA"]
	    for i in data:
		logs=logv(i,"/infoblox/var/infoblox.log",config.grid_mgmt_ip)
		print("logs are",logs)
		if logs != None:
			print("validated single cipher enabled in logs")
			assert True
		else:
			print("validated single cipher not enabled in logs")
			assert False
	    child.sendline('exit')
	    child.close()
            sleep(10)		
		    
	    





    @pytest.mark.run(order=72)
    def test_072_validate_TLS_protocol_TLSv1_2_active_when_single_server_supported_cipher_enabled_for_saml_port_with_openssl(self):
            logging.info("validating TLS protocol TLSv1.2  active for saml port")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
            child.logfile=sys.stdout
            child.expect('#')
            child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_2")
            sleep(5)
            child.sendline('\n')
            child.sendline('\n')
            child.expect('#')
            output = child.before
            print ("output is", output)
            if (("Protocol  : TLSv1.2" in output) and ("Cipher    : ECDHE-RSA-AES256-SHA" in output)):
                print("TLSv1.2 and single cipher is  active when single server supported cipher enabled")
                logging.info("TLS protocols TLSv1.2 and single cipher is active for saml port")
                assert True
            else:
                print("TLS protocols TLSv1.2 and single cipher is not  active for saml port")
                logging.info("TLS protocols TLSv1.2 and single cipher is not active for saml port")
                assert False
	    child.close()

    @pytest.mark.run(order=73)
    def test_073_validate_TLS_protocol_TLSv1_0_not_active_when_single_server_supported_cipher_enabled_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.0 not active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLS protocols TLSv1.0  not active when single server supported cipher enabled")
                logging.info("TLS protocols TLSv1.0 not active when single server supported cipher enabled")
                assert True
        else:
                logging.info("TLS protocols TLSv1.0  active when single server supported cipher enabled")
		print("TLS protocols TLSv1.0  active when single server supported cipher enabled")
                assert False
	child.close()
	sleep(10)



    @pytest.mark.run(order=74)
    def test_074_validate_TLS_protocol_TLSv1_1_not_active_when_single_server_supported_cipher_enabled_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.1 not active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLS protocols TLSv1.1  not active when single server supported cipher enabled")
                logging.info("TLS protocols TLSv1.1 not active when single server supported cipher enabled")
                assert True
        else:
                logging.info("TLS protocols TLSv1.1  active when single server supported cipher enabled")
		print("TLS protocols TLSv1.1  active when single server supported cipher enabled")
                assert False
	child.close()


    @pytest.mark.run(order=75)
    def test_075_validate_TLS_protocol_TLSv1_2_active_and_single_cipher__active_for_saml_port_with_nmap(self):
        logging.info("validating TLS protocol TLSv1.2 and single cipher active for saml port with nmap")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("nmap -sV --script ssl-enum-ciphers -p 8765 "+config.grid_mgmt_ip)
        sleep(15)
        child.expect('#')
        output = child.before
        output=output.replace("\r\n| ","")
        print("output is", output)
	data = ['TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA','TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256','TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384','TLS_DHE_DSS_WITH_AES_256_CBC_SHA','TLS_DH_RSA_WITH_3DES_EDE_CBC_SHA','TLS_DH_DSS_WITH_3DES_EDE_CBC_SHA','TLS_RSA_WITH_AES_256_CBC_SHA256','TLS_RSA_WITH_AES_256_GCM_SHA384','TLS_RSA_WITH_AES_128_CBC_SHA256','TLS_DHE_DSS_WITH_AES_128_CBC_SHA256','TLS_DHE_DSS_WITH_AES_128_GCM_SHA256','TLS_DHE_DSS_WITH_AES_256_CBC_SHA256','TLS_DHE_DSS_WITH_AES_256_GCM_SHA384','TLS_DHE_DSS_WITH_AES_128_CBC_SHA','TLS_RSA_WITH_AES_256_CBC_SHA','TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384','TLS_RSA_WITH_AES_128_CBC_SHA','TLS_DHE_RSA_WITH_AES_128_CBC_SHA256','TLS_RSA_WITH_AES_128_GCM_SHA256','TLS_DHE_RSA_WITH_AES_256_CBC_SHA256','TLS_DHE_RSA_WITH_AES_256_CBC_SHA','TLS_DHE_RSA_WITH_AES_128_CBC_SHA','TLS_DHE_RSA_WITH_AES_256_GCM_SHA384','TLS_DHE_RSA_WITH_AES_128_GCM_SHA256','TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256','TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256','TLS_RSA_WITH_RC4_128_SHA','TLS_RSA_WITH_3DES_EDE_CBC_SHA']
        if (("TLSv1.2" in output) and ("TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA" in output)):
		flag=False
                for i in data:
                        if i in output:
                                print(i,"cipher is active")
				flag=True
                        else:
                                print(i,"cipher is not active")
		if flag==True:
			print("one or more ciphers are active")
			assert False
		else:
			print("single cipher is active")
			assert True
        else:
                print('TLSv1.2 and single cipher is not active')
		assert False
	print('TLSv1.2 and only single cipher is active')
	child.close()


    @pytest.mark.run(order=76)
    def test_076_validate_TLS_protocol_TLSv1_2_active_when_single_server_supported_cipher_enabled_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --protocols --fast --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(35)
        child.expect('Done')
        output = child.before
        output1 = output.replace("\x1b[m\x1b[1;33m","").replace("\x1b[m\x1b[0;33m","").replace("\x1b[m","").replace("\x1b[1;32m","")
        print("output is",output1)
        if "TLS 1.2    offered" in output1:
                print("validated TLSv1.2 is enabled when single server supported cipher enabled with testssl.sh script")
                logging.info("validated TLSv1.2is enabled when single server supported cipher enabled with testssl.sh script")
                assert True
        else:
                print("validated TLSv1.2 is not enabled when single server supported cipher enabled with testssl.sh script")
                logging.info("validated TLSv1.2 is not enabled when single server supported cipher enabled with testssl.sh script")
                assert False
	child.close()



    @pytest.mark.run(order=77)
    def test_077_validate_single_cipher_active_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh -E --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(40)
        child.expect('Done')
        output = child.before
        print("output is",output)
        if "ECDHE-RSA-AES256-SHA" in output:
                print("single cipher is  active for saml port with testssl.sh script")
                logging.info("single cipher is active for saml port with testssl.sh script")
                assert True
        else:
                print("single  cipher  not active for saml port with testssl.sh script")
                logging.info("single cipher not  active for saml port with testssl.sh script")
                assert False
	child.close()
	sleep(10)




    @pytest.mark.run(order=78)
    def test_078_validated_RC4_and_3DES_ciphers_are_not_active_when_single_server_supported_cipher_enabled_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --vulnerable '+config.grid_mgmt_ip+':8765 ')
        sleep(40)
        child.expect('Done')
        output = child.before
        output = output.replace("\x1b[m","").replace("\x1b[1;32m","").replace("\x1b[0;31m","").replace("\x1b[0;32m","")
        print("output isss",output)
	if (("SWEET32 (CVE-2016-2183, CVE-2016-6329)    not vulnerable" in output) and ("RC4 (CVE-2013-2566, CVE-2015-2808)        no RC4 ciphers detected" in output)):
                logging.info("Validated RC4 and 3DES ciphers not active for saml port with testssl.sh script")
                assert True
        else:
                print("Validated RC4 and 3DES ciphers active for saml port with testssl.sh script")
                logging.info("Validated RC4 and  3DES  ciphers active for saml port with testssl.sh script")
                assert False
	child.close()



    @pytest.mark.run(order=79)
    def test_079_login_to_CLI_as_SAML_with_superuser(self):
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
        child.sendline(config.okta_username)
        sleep(10)
        child.expect('OKTA SAML password:')
        sleep(5)
        child.sendline(config.okta_password)
        child.expect('Infoblox >')
        child.sendline('show network')
        sleep(20)
        child.expect('Infoblox >')
        c= child.before
        child.sendline('exit')
        child.expect('login:')
        assert re.search(r'.*Current LAN1 Network Settings.*',c)
        logging.info("Test Case  execution completed")



    @pytest.mark.run(order=80)
    def test_080_enabling_tls_protocols_TLSv1_1_and_enabling_single_cipher(self):
            logging.info("enabling tls protocols TLSv1_1 and single ciphers")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip)
            child.logfile=sys.stdout
            log("start","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set ssl_tls_protocols enable TLSv1.1')
            child.expect('>')
            child.sendline('set ssl_tls_protocols disable TLSv1.0')
            child.expect('>')
	    child.sendline('set ssl_tls_protocols disable TLSv1.2')
	    child.expect('>')
	    child.sendline('show ssl_tls_protocols')
	    child.expect('>')
	    output = child.before
	    if "Current configuration for the SAML  : TLSv1.1" in output:
		print("TLSv1.1 is enabled")
		logging.info("TLSv1.1 is enabled")
            else:
		print("TLSv1.1 is not enabled")
		logging.info("TLSv1.1 is not enabled")
            sleep(120)
            log("stop","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
            data = ["Restarting saml","TLSv1_1","ECDHE-RSA-AES256-SHA"]
            for i in data:
                logs=logv(i,"/infoblox/var/infoblox.log",config.grid_mgmt_ip)
                print("logs are",logs)
                if logs != None:
                        print("validated TLSv1.1 and single ciphers active in logs")
		        logging.info("validated TLSv1.1 and single ciphers active in logs")
			assert True
		else:
			print("validated TLSv1.1 and single ciphers not active in logs")
			logging.info("validated TLSv1.1 and single ciphers not active in logs")
			assert False
	    child.sendline('exit')
	    child.close()
	    sleep(10)





    @pytest.mark.run(order=81)
    def test_081_validate_TLS_protocol_TLSv1_1_and_single_cipher_active_for_saml_port_with_openssl(self):
            logging.info("validating TLS protocol TLSv1.1 and single cipher  active for saml port")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
            child.logfile=sys.stdout
            child.expect('#')
            child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_1")
            sleep(5)
            child.sendline('\n')
            child.sendline('\n')
            child.expect('#')
            output = child.before
            print ("output is", output)
            if (("Protocol  : TLSv1.1" in output) and ("Cipher    : ECDHE-RSA-AES256-SHA" in output)):
                print("TLSv1.1 and single cipher is  active")
                logging.info("TLS protocols TLSv1.1 and single cipher is active for saml port")
                assert True
            else:
                print("TLS protocols TLSv1.1 and single cipher is not  active for saml port")
                logging.error("TLS protocols TLSv1.1 and single cipher is not active for saml port")
                assert False
	    child.close()



    @pytest.mark.run(order=82)
    def test_082_validate_TLS_protocol_TLSv1_0__not_active_when_single_cipher_active_for_saml_port_with_openssl(self):
        logging.info("validate TLS protocols TLSv1.0 not active when single cipher active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLS protocols TLSv1.0  not active for saml port")
                logging.info("TLS protocols TLSv1.0 not active for saml port")
                assert True
        else:
		print("TLS protocols TLSv1.0  active for saml port")
                logging.error("TLS protocols TLSv1.0 active for saml port")
                assert False
	child.close()


    @pytest.mark.run(order=83)
    def test_083_validate_TLS_protocol_TLSv1_2_not_active_when_single_cipher_active_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.2 with single cipher not active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_2")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLS protocols TLSv1.1 with single cipher  not active for saml port")
                logging.info("TLS protocols TLSv1.1 with single cipher not active for saml port")
                assert True
        else:
                print("TLS protocols TLSv1.1 with single cipher  active for saml port")
                logging.error("TLS protocols TLSv1.1 with single cipher  active for saml port")
                assert False

	child.close()
	sleep(10)


    @pytest.mark.run(order=84)
    def test_084_validate_TLS_protocol_TLSv1_2_not_active_when_single_cipher_active_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.2 nto active when single cipher active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_2")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLddS protocols TLSv1.2 with single cipher   not active for saml port")
                logging.info("TLS protocols TLSv1.2 with single cipher  not active for saml port")
                assert True
        else:
                print("TLS protocols TLSv1.2 with single cipher  active for saml port")
                logging.error("TLS protocols TLSv1.2 with single cipher   active for saml port")
                assert False
	child.close()


    @pytest.mark.run(order=85)
    def test_085_validate_TLS_protocol_TLSv1_1_active_and_single_cipher__active_for_saml_port_with_nmap(self):
        logging.info("validating TLS protocol TLSv1.0 and single cipher active for saml port with nmap")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("nmap -sV --script ssl-enum-ciphers -p 8765 "+config.grid_mgmt_ip)
        sleep(15)
        child.expect('#')
        output = child.before
        output=output.replace("\r\n| ","")
        print("output is", output)
	data = ['TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA','TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256','TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384','TLS_DHE_DSS_WITH_AES_256_CBC_SHA','TLS_DH_RSA_WITH_3DES_EDE_CBC_SHA','TLS_DH_DSS_WITH_3DES_EDE_CBC_SHA','TLS_RSA_WITH_AES_256_CBC_SHA256','TLS_RSA_WITH_AES_256_GCM_SHA384','TLS_RSA_WITH_AES_128_CBC_SHA256','TLS_DHE_DSS_WITH_AES_128_CBC_SHA256','TLS_DHE_DSS_WITH_AES_128_GCM_SHA256','TLS_DHE_DSS_WITH_AES_256_CBC_SHA256','TLS_DHE_DSS_WITH_AES_256_GCM_SHA384','TLS_DHE_DSS_WITH_AES_128_CBC_SHA','TLS_RSA_WITH_AES_256_CBC_SHA','TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384','TLS_RSA_WITH_AES_128_CBC_SHA','TLS_DHE_RSA_WITH_AES_128_CBC_SHA256','TLS_RSA_WITH_AES_128_GCM_SHA256','TLS_DHE_RSA_WITH_AES_256_CBC_SHA256','TLS_DHE_RSA_WITH_AES_256_CBC_SHA','TLS_DHE_RSA_WITH_AES_128_CBC_SHA','TLS_DHE_RSA_WITH_AES_256_GCM_SHA384','TLS_DHE_RSA_WITH_AES_128_GCM_SHA256','TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256','TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256','TLS_RSA_WITH_RC4_128_SHA','TLS_RSA_WITH_3DES_EDE_CBC_SHA']
        if (("TLSv1.1" in  output) and ("TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA" in output)):
                flag=False
                for i in data:
                        if i in output:
                                print(i,"cipher is active")
                                flag=True
                        else:
                                print(i,"cipher is not active")
                if flag==True:
                        print("one or more ciphers are active")
                        assert False
                else:
                        print("single cipher is active")
                        assert True
        else:
                print('TLSv1.1 and single cipher is not active')
		assert False
        print('TLSv1.1 and only single cipher is active')
	child.close()
	sleep(10)




    @pytest.mark.run(order=86)
    def test_086_validate_TLS_protocol_TLSv1_1_active_when_single_cipher_active_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --protocols --fast --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(35)
        child.expect('Done')
        output = child.before
        output1 = output.replace("\x1b[m\x1b[1;33m","").replace("\x1b[m\x1b[0;33m","").replace("\x1b[m","").replace("\x1b[1;33m","").replace("\x1b[1;32m","")
        print("output is",output1)
        if "TLS 1.1    offered" in output1:
                print("validated TLSv1 is enabled with testssl.sh script")
                logging.info("validated TLSv1 is enabled with testssl.sh script")
                assert True
        else:
                print("validated TLSv1 is not enabled with testssl.sh script")
                logging.error("validated TLSv1 is not enabled with testssl.sh script")
                assert False
	child.close()



    @pytest.mark.run(order=87)
    def test_087_validate_weak_ciphers_are_not_active_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh -E --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(35)
        child.expect('Done')
        output = child.before
        print("output is",output)
        if "ECDHE-RSA-AES256-SHA" in output:
		print("validated single cipher is active for saml port with testssl.sh script")
		logging.info("validated single cipher is active for saml port with testssl.sh script")
                assert True
        else:
		print("validated single cipher is not active for saml port with testssl.sh script")
		logging.info("validated single cipher is not active for saml port with testssl.sh script")
                assert False
	child.close()
	sleep(10)



    @pytest.mark.run(order=88)
    def test_088_validate_RC4_and_3DES_ciphers_are_not_active_when_single_cipher_active_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --vulnerable '+config.grid_mgmt_ip+':8765 ')
        sleep(40)
        child.expect('Done')
        output = child.before
        output = output.replace("\x1b[m","").replace("\x1b[1;32m","").replace("\x1b[0;31m","").replace("\x1b[0;32m","")
        print("output isss",output)
	if (("SWEET32 (CVE-2016-2183, CVE-2016-6329)    not vulnerable" in output) and ("RC4 (CVE-2013-2566, CVE-2015-2808)        no RC4 ciphers detected" in output)):
                logging.info("Validated RC4 and 3DES ciphers not active for saml port with testssl.sh script")
                assert True
        else:
                print("Validated RC4 and 3DES  ciphers active for saml port with testssl.sh script")
                logging.error("Validated RC4 and 3DES  ciphers active for saml port with testssl.sh script")
                assert False
	child.close()



    @pytest.mark.run(order=89)
    def test_089_login_to_CLI_as_SAML_with_superuser(self):
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
        child.sendline(config.okta_username)
        sleep(10)
        child.expect('OKTA SAML password:')
        sleep(5)
        child.sendline(config.okta_password)
        child.expect('Infoblox >')
        child.sendline('show network')
        sleep(20)
        child.expect('Infoblox >')
        c= child.before
        child.sendline('exit')
        child.expect('login:')
        assert re.search(r'.*Current LAN1 Network Settings.*',c)
        logging.info("Test Case  execution completed")






    @pytest.mark.run(order=90)
    def test_090_enabling_only_DHE_ciphers_for_TLSv1_1(self):
        logging.info("enabling only DHE ciphers")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        log("start","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set ssl_tls_protocols enable TLSv1.1')
        child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSv1.2')
        child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSv1.0')
        child.expect('>')
        child.sendline('set ssl_tls_ciphers enable TLS_DHE_RSA_WITH_AES_128_CBC_SHA')
        child.expect('>')
        child.sendline('set ssl_tls_ciphers enable TLS_DHE_RSA_WITH_AES_128_CBC_SHA256')
        child.expect('>')
        child.sendline('set ssl_tls_ciphers enable TLS_DHE_RSA_WITH_AES_128_GCM_SHA256')
        child.expect('>')
        child.sendline('set ssl_tls_ciphers enable TLS_DHE_RSA_WITH_AES_256_CBC_SHA')
        child.expect('>')
        child.sendline('set ssl_tls_ciphers enable TLS_DHE_RSA_WITH_AES_256_CBC_SHA256')
        child.expect('>')
        child.sendline('set ssl_tls_ciphers enable TLS_DHE_RSA_WITH_AES_256_GCM_SHA384')
        child.expect('>')
        child.sendline('set ssl_tls_ciphers disable 1')
        child.expect('>')
        child.sendline('show ssl_tls_ciphers')
        child.expect('>')
        output = child.before
        #print('output is',output)
        sleep(120)
        log("stop","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        data = ['TLS_DHE_RSA_WITH_AES_128_CBC_SHA        enabled','TLS_DHE_RSA_WITH_AES_128_CBC_SHA256     enabled','TLS_DHE_RSA_WITH_AES_128_GCM_SHA256     enabled','TLS_DHE_RSA_WITH_AES_256_CBC_SHA        enabled','TLS_DHE_RSA_WITH_AES_256_CBC_SHA256     enabled','TLS_DHE_RSA_WITH_AES_256_GCM_SHA384     enabled']
        for i in data:
            if i in output:
		print(i)
                logging.info("only DHE ciphers are enabled")
		assert True
            else:
                print(i)
                loggig.error("only DHE ciphers are not enabled")
		assert False
	print("only DHE ciphers are enabled")
	data1 = ["Restarting saml","TLSv1_1","DHE-RSA-AES128-GCM-SHA256","DHE-RSA-AES256-GCM-SHA384","DHE-RSA-AES128-SHA","DHE-RSA-AES256-SHA","DHE-RSA-AES128-SHA256","DHE-RSA-AES256-SHA256"]
	for i in data1:
                logs=logv(i,"/infoblox/var/infoblox.log",config.grid_mgmt_ip)
                print("logs are",logs)
                if logs != None:
                        print("validated only DHE ciphers and TLSv1.1are active in logs")
                        logging.info("validated only DHE ciphers and TLSv1.1 are active in logs")
			assert True
                else:
                        print("validated only DHE ciphers and TLSv1.1are not active in logs")
                        logging.error("validated only DHE ciphers and TLSv1.1are  not active in logs")
			assert False
	child.sendline('exit')
	child.close()
	sleep(10)


    @pytest.mark.run(order=91)
    def test_091_validate_TLS_protocol_TLSv1_0_not_active_when_DHE_ciphers_are_active_for_saml_port_with_openssl(self):
            logging.info("validating TLS protocol TLSv1.0 not  active when DHE ciphers are active for saml port")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
            child.logfile=sys.stdout
            child.expect('#')
            child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1")
            sleep(5)
            child.sendline('\n')
            child.sendline('\n')
            child.expect('#')
            output = child.before
            print ("output is", output)
	    if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLSv1 is not  active")
                logging.info("TLS protocols TLSv1 isnot active for saml port")
                assert True
            else:
                print("TLS protocols TLSv1 is  active for saml port")
                logging.error("TLS protocols TLSv1 is active for saml port")
                assert False
	    child.close()


    @pytest.mark.run(order=92)
    def test_092_validate_TLS_protocol_TLSv1_1_active_when_DHE_ciphers_are_active_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.1  active when DHE ciphers are active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("wrong version number" not in output) and ("ssl handshake failure" not in output) and ("Protocol  : TLSv1.1" in output)):
                print("TLS protocols TLSv1.1 active")
                logging.info("TLS protocols TLSv1.1 active")
                assert True
        else:
                print("TLS protocols TLSv1.1 not active")
                logging.error("TLS protocols TLSv1.1not  active for saml port")
                assert False
	child.close()

    @pytest.mark.run(order=93)
    def test_093_validate_TLS_protocol_TLSv1_2_not_active_when_DHE_ciphers_are_active_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.2 not active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_2")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLS protocols TLSv1.2 with single cipher   not active for saml port")
                logging.info("TLS protocols TLSv1.2 with single cipher  not active for saml port")
                assert True
        else:
                print("TLS protocols TLSv1.2 with single cipher  active for saml port")
                logging.error("TLS protocols TLSv1.2 with single cipher   active for saml port")
                assert False
	child.close()
	sleep(10)


    @pytest.mark.run(order=94)
    def test_094_validate_only_DHE_ciphers_and_TLSv1_1_are_active_for_saml_port_with_nmap(self):
        logging.info("validate only DHE ciphers are active for TLSv1.1 for saml port with nmap")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("nmap -sV --script ssl-enum-ciphers -p 8765 "+config.grid_mgmt_ip)
        sleep(15)
        child.expect('#')
        output = child.before
        output=output.replace("\r\n| ","")
        print("output is", output)
        if  (("TLSv1.1" in output) and ("TLS_DHE_RSA_WITH_AES_128_CBC_SHA" in output) and ("TLS_DHE_RSA_WITH_AES_256_CBC_SHA" in output)):
            print("DHE ciphers supported by TLSv1.1 are active")
            logging.info("DHE ciphers supported by TLSv1.1 are active")
	    assert False
        else:
            print("DHE ciphers for TLSv1.1 are not active")
            logging.error("DHE ciphers for TLSv1.1 are not active")
	    assert True
	child.close()





    @pytest.mark.run(order=95)
    def test_095_validate_TLSv1_1_are_active_when_DHE_ciphers_are_active_for_saml_port_with_testssl_sh_script(self):
        logging.info("validate only DHE ciphers are active for saml port with testssl_sh script")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --protocols --fast --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(35)
	child.expect('-->')
        child.sendline('yes')
	child.expect('-->')
	child.sendline('yes')
	child.expect('#')
        output = child.before
        output = output.replace("\x1b[m\x1b[1;33m","").replace("\x1b[m\x1b[0;33m","").replace("\x1b[m","").replace("\x1b[0;32m","")
        print("output is",output)
        if "TLS 1.1    offered" in output:
                print("TLSv1.1 is active")
                logging.info("TLSv1.1 is active")
                assert False
        else:
                print("TLSv1.1 is not active")
                logging.error("TLSv1.1 is not active")
                assert True
	child.close()


    @pytest.mark.run(order=96)
    def test_096_validate_only_DHE_ciphers_are_active_for_TLSv1_1_for_saml_port_with_testssl_sh_script(self):
        logging.info("validate all ciphers which are supported by server for TLSv1_1 are  active for saml port with testssl.sh")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh -E --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(35)
	child.expect('-->')
	child.sendline('yes')
        child.expect('Done')
        output = child.before
        print("output is",output)
        if (("TLS 1.1" in output) and  ("DHE-RSA-AES256-SHA" in output)  and ("DHE-RSA-AES128-SHA" in output)):
            print("DHE ciphers for TLSV1.1 are active")
            assert False
        else:
            print("DHE ciphers for TLSV1.1 is not active")
            assert True
	child.close()
	sleep(10)

    @pytest.mark.run(order=97)
    def test_097_validated_RC4_and_3DES_ciphers_are_not_active_when_only_DHE_ciphers_are_enabled_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --vulnerable '+config.grid_mgmt_ip+':8765 ')
        sleep(40)
	child.expect('-->')
	child.sendline('yes')
        child.expect('Done')
        output = child.before
        output = output.replace("\x1b[m","").replace("\x1b[1;32m","").replace("\x1b[0;31m","").replace("\x1b[0;32m","")
        print("output is",output)
	if (("SWEET32 (CVE-2016-2183, CVE-2016-6329)    not vulnerable" in output) and ("RC4 (CVE-2013-2566, CVE-2015-2808)        no RC4 ciphers detected" in output)):
                print("Validated RC4 and 3DES ciphers not active for saml port with testssl.sh script")
                logging.info("Validated RC4 and 3DES ciphers not active for saml port with testssl.sh script")
                assert True
        else:
                print("Validated RC4 and 3DES ciphers  active for saml port with testssl.sh script")
                logging.error("Validated RC4 and 3DES ciphers active for saml port with testssl.sh script")
                assert False
	child.close()



    @pytest.mark.run(order=98)
    def test_098_login_to_CLI_as_SAML_with_superuser(self):
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
        child.sendline(config.okta_username)
        sleep(10)
        child.expect('OKTA SAML password:')
        sleep(5)
        child.sendline(config.okta_password)
        child.expect('Infoblox >')
        child.sendline('show network')
        sleep(20)
        child.expect('Infoblox >')
        c= child.before
        child.sendline('exit')
        child.expect('login:')
        assert re.search(r'.*Current LAN1 Network Settings.*',c)
        logging.info("Test Case  execution completed")






    @pytest.mark.run(order=99)
    def test_099_enabling_only_DHE_ciphers_for_TLSv1_0(self):
        logging.info("enabling only DHE ciphers")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        log("start","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('set ssl_tls_protocols enable TLSv1.0')
        child.expect('>')
	child.sendline('set ssl_tls_protocols disable TLSv1.1')
        child.expect('>')
	child.sendline('set ssl_tls_protocols disable TLSv1.2')
        child.expect('>')
        child.sendline('show ssl_tls_protocols')
        child.expect('>')
        output = child.before
        #print('output is',output)
        sleep(120)
        log("stop","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        if "Current configuration for the SAML  : TLSv1.0" in output:
            print("TLSv1.0 is enbaled")
            assert True
        else:
            print("TLSv1.0 is not enabled")
            assert False
        data = ["Restarting saml","TLSv1","DHE-RSA-AES128-GCM-SHA256","DHE-RSA-AES256-GCM-SHA384","DHE-RSA-AES128-SHA","DHE-RSA-AES256-SHA","DHE-RSA-AES128-SHA256","DHE-RSA-AES256-SHA256"]
        for i in data:
                logs=logv(i,"/infoblox/var/infoblox.log",config.grid_mgmt_ip)
                print("logs are",logs)
                if logs != None:
                        print("validated only DHE ciphers and TLSv1.0 are active in logs")
                        logging.info("validated only DHE ciphers and TLSv1.0 are active in logs")
                        assert True
                else:
                        print("validated only DHE ciphers and TLSv1.0 are not active in logs")
                        logging.error("validated only DHE ciphers and TLSv1.0 are not  active in logs")
                        assert False
	child.sendline('exit')
	child.close()
	sleep(10)


    @pytest.mark.run(order=100)
    def test_100_validate_TLS_protocol_TLSv1_0_active_when_only_DHE_ciphers_are_active_for_saml_port_with_openssl(self):
            logging.info("validating TLS protocol TLSv1.0  active for saml port")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
            child.logfile=sys.stdout
            child.expect('#')
            child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1")
            sleep(5)
            child.sendline('\n')
            child.sendline('\n')
            child.expect('#')
            output = child.before
            print ("output is", output)
	    if (("wrong version number" not in output) and ("ssl handshake failure" not in output) and ("Protocol  : TLSv1" in output)):
                print("TLSv1.0 is  active when only DHE ciphers are active")
                logging.info("TLS protocols TLSv1.0 is active for saml port")
                assert True
            else:
		print("TLS protocols TLSv1.0 is not  active when only DHE ciphers are not active for saml port")
                logging.info("TLS protocols TLSv1.0 is not active for saml port")
                assert False
	    child.close()



    @pytest.mark.run(order=101)
    def test_101_validate_TLS_protocol_TLSv1_1_not_active_when_only_DHE_ciphers_are_active_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.1 not active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLS protocols TLSv1.1 not active when only DHE ciphers are enabled for saml port")
                logging.info("TLS protocols TLSv1.1 not active when only DHE ciphers are enabled for saml port")
                assert True
        else:
                print("TLS protocols TLSv1.1  active when only DHE ciphers are enabled for saml port")
                assert False
	child.close()


    @pytest.mark.run(order=102)
    def test_102_validate_TLS_protocol_TLSv1_2_not_active_when_only_DHE_ciphers_are_active_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.2  not active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_2")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
		print("TLS protocols TLSv1.2 not active when only DHE ciphers are enabled for saml port")
                logging.info("TLS protocols TLSv1.2 not active when only DHE ciphers are enabled for saml port")
                assert True
        else:
                print("TLS protocols TLSv1.2 active when only DHE ciphers are enabled for saml port")
                assert False
	child.close()
	sleep(10)


    @pytest.mark.run(order=103)
    def test_103_validate_only_DHE_ciphers_are_active_for_TLSv1_for_saml_port_with_nmap(self):
        logging.info("validate only DHE ciphers are active for TLSv1 for saml port with nmap")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("nmap -sV --script ssl-enum-ciphers -p 8765 "+config.grid_mgmt_ip)
        sleep(15)
        child.expect('#')
        output = child.before
        output=output.replace("\r\n| ","")
        print("output is", output)
        if  (("TLSv1.0" in output) and ("TLS_DHE_RSA_WITH_AES_128_CBC_SHA" in output) and ("TLS_DHE_RSA_WITH_AES_256_CBC_SHA" in output)):
            print("DHE ciphers supported by TLSv1 are active")
            logging.info("DHE ciphers supported by TLSv1 are active")
	    assert False
        else:
            print("DHE ciphers for TLSv1 are not active")
            logging.error("DHE ciphers for TLSv1 are not active")
	    assert True
	child.close()




    @pytest.mark.run(order=104)
    def test_104_validate_only_DHE_ciphers_are_active_for_TLSv1_are_active_for_saml_port_with_testssl_sh_script(self):
        logging.info("validate only DHE ciphers are active for saml port with testssl_sh script")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --protocols --fast --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(35)
	child.expect('-->')
	child.sendline('yes')
        child.expect('-->')
        child.sendline('yes')
        child.expect('#')
        output = child.before
        output = output.replace("\x1b[m\x1b[1;33m","").replace("\x1b[m\x1b[0;33m","").replace("\x1b[m","").replace("\x1b[0;32m","")
        print("output is",output)
        if "TLS 1      offered" in output:
                print("TLSv1 is active")
                logging.info("TLSv1 is active")
                assert False
        else:
                print("TLSv1 is not active")
                logging.error("TLSv1 is not active")
                assert True
        child.close()


    @pytest.mark.run(order=105)
    def test_105_validate_only_DHE_ciphers__are_active_for_TLSv1_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh -E --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(25)
	child.expect('-->')
        child.sendline('yes')
        child.expect('Done')
        output = child.before
        print("output is",output)
        if (("TLS 1" in output) and  ("DHE-RSA-AES256-SHA" in output)  and ("DHE-RSA-AES128-SHA" in output)):
            print("DHE ciphers for TLSV1.1 are active")
            assert False
        else:
            print("DHE ciphers for TLSV1.1 is not active")
            assert True
	child.close()
	sleep(10)



    @pytest.mark.run(order=106)
    def test_106_validated_RC4_and_3DES_ciphers_are_not_active_when_only_DHE_ciphers_are_enabled_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --vulnerable '+config.grid_mgmt_ip+':8765 ')
        sleep(40)
	child.expect('-->')
        child.sendline('yes')
        child.expect('Done')
        output = child.before
        output = output.replace("\x1b[m","").replace("\x1b[1;32m","").replace("\x1b[0;31m","").replace("\x1b[0;32m","")
        print("output is",output)
	if (("SWEET32 (CVE-2016-2183, CVE-2016-6329)    not vulnerable" in output) and ("RC4 (CVE-2013-2566, CVE-2015-2808)        no RC4 ciphers detected" in output)):
                print("Validated RC4 and 3DES ciphers not active for saml port with testssl.sh script")
                logging.info("Validated RC4 and 3DES ciphers not active for saml port with testssl.sh script")
                assert True
        else:
                print("Validated RC4 and 3DES ciphers  active for saml port with testssl.sh script")
                logging.error("Validated RC4 and 3DES ciphers active for saml port with testssl.sh script")
                assert False
	child.close()



    @pytest.mark.run(order=107)
    def test_107_login_to_CLI_as_SAML_with_superuser(self):
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
        child.sendline(config.okta_username)
        sleep(10)
        child.expect('OKTA SAML password:')
        sleep(5)
        child.sendline(config.okta_password)
        child.expect('Infoblox >')
        child.sendline('show network')
        sleep(20)
        child.expect('Infoblox >')
        c= child.before
        child.sendline('exit')
        child.expect('login:')
        assert re.search(r'.*Current LAN1 Network Settings.*',c)
        logging.info("Test Case  execution completed")





    @pytest.mark.run(order=108)
    def test_108_enabling_only_DHE_ciphers_for_TLSv1_2(self):
        logging.info("enabling only DHE ciphers")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        log("start","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set ssl_tls_protocols enable TLSv1.2')
        child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSv1.1')
        child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSv1.0')
        child.expect('>')
        child.sendline('show ssl_tls_protocols')
        child.expect('>')
        output = child.before
        #print('output is',output)
        sleep(120)
        log("stop","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        if "Current configuration for the SAML  : TLSv1.2" in output:
            print("TLSv1.2 is enbaled")
            assert True
        else:
            print("TLSv1.2 is not enabled")
            assert False
        data = ["Restarting saml","TLSv1_2","DHE-RSA-AES128-GCM-SHA256","DHE-RSA-AES256-GCM-SHA384","DHE-RSA-AES128-SHA","DHE-RSA-AES256-SHA","DHE-RSA-AES128-SHA256","DHE-RSA-AES256-SHA256"]
        for i in data:
                logs=logv(i,"/infoblox/var/infoblox.log",config.grid_mgmt_ip)
                print("logs are",logs)
                if logs != None:
                        print("validated DHE ciphers for TLSv1.2 are active in logs")
                        logging.info("validated DHE ciphers for TLSv1.2 are active in logs")
                        assert True
                else:
                        print("validated DHE ciphers for TLSv1.2 are not  active in logs")
                        logging.error("validated DHE ciphers for TLSv1.2 are not active in logs")
                        assert False
	child.sendline('exit')
	child.close()
	sleep(10)


    @pytest.mark.run(order=109)
    def test_109_validate_TLS_protocol_TLSv1_2_active_when_DHE_ciphers_are_active_for_saml_port_with_openssl(self):
            logging.info("validating TLS protocol TLSv1.2active when DHE cipher  active for saml port")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
            child.logfile=sys.stdout
            child.expect('#')
            child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_2")
            sleep(5)
            child.sendline('\n')
            child.sendline('\n')
            child.expect('#')
            output = child.before
            print ("output is", output)
	    if (("wrong version number" not in output) and ("ssl handshake failure" not in output) and ("Protocol  : TLSv1.2" in output)):
                print("TLSv1.2 is  active when only DHE ciphers are enabled")
                logging.info("TLSv1.2 is  active when only DHE ciphers are enabled")
                assert True
            else:
                print("TLSv1.2 is not active when only DHE ciphers are enabled")
                logging.error("TLSv1.2 is not  active when only DHE ciphers are enabled")
                assert False
	    child.close()




    @pytest.mark.run(order=110)
    def test_110_validate_TLS_protocol_TLSv1_not_active_when_DHE_ciphers_are_active_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1 not active when DHE ciphers are active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLS protocols TLSv1  not active when only DHE ciphers are enabled for saml port")
                logging.info("TLS protocols TLSv1  not active when only DHE ciphers are enabled for saml port")
                assert True
        else:
		print("TLS protocols TLSv1  active when only DHE ciphers are enabled for saml port")
                logging.error("TLS protocols TLSv1 active when only DHE ciphers are enabled for saml port")
                assert False
	child.close()
	sleep(10)



    @pytest.mark.run(order=111)
    def test_111_validate_TLS_protocol_TLSv1_1_not_active_when_DHE_ciphers_are_active_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.2 with single cipher not active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
		print("TLS protocols TLSv1_1  not active when only DHE ciphers are enabled for saml port")
                logging.info("TLS protocols TLSv1_1  not active when only DHE ciphers are enabled for saml port")
                assert True
        else:
		print("TLS protocols TLSv1.1  active when only DHE ciphers are enabled for saml port")
                logging.error("TLS protocols TLSv1.1 active when only DHE ciphers are enabled for saml port")
                assert False
	child.close()


    @pytest.mark.run(order=112)
    def test_112_validate_only_DHE_ciphers_are_active_for_TLSv1_2_are_active_for_saml_port_with_nmap(self):
        logging.info("validate only DHE ciphers are active for TLSv1.2 for saml port with nmap")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("nmap -sV --script ssl-enum-ciphers -p 8765 "+config.grid_mgmt_ip)
        sleep(15)
        child.expect('#')
        output = child.before
        output=output.replace("\r\n| ","")
        print("output is", output)
        data = ['TLSv1.2','TLS_DHE_RSA_WITH_AES_128_CBC_SHA','TLS_DHE_RSA_WITH_AES_128_CBC_SHA256','TLS_DHE_RSA_WITH_AES_128_GCM_SHA256','TLS_DHE_RSA_WITH_AES_256_CBC_SHA','TLS_DHE_RSA_WITH_AES_256_CBC_SHA256','TLS_DHE_RSA_WITH_AES_256_GCM_SHA384']
        for i in data:
		if i in output:
                	print(i,"is active")
                	logging.info("DHE ciphers supported by TLSv1.2 are active")
			assert False 
        	else:
                	print(i,"is not active")
                	logging.error("DHE ciphers for TLSv1.2 are not active")
			assert True
	print("DHE ciphers supported by TLSv1.2 are active")
	child.close()
	sleep(10)



    @pytest.mark.run(order=113)
    def test_113_validate_only_DHE_ciphers_are_active_for_TLSv1_2_are_active_for_saml_port_with_testssl_sh_script(self):
        logging.info("validate only DHE ciphers are active for saml port with testssl_sh script")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --protocols --fast --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(25)
	child.expect('-->')
        child.sendline('yes')
        child.expect('-->')
        child.sendline('yes')
	child.expect('#')
	output = child.before
        output = output.replace("\x1b[m\x1b[1;33m","").replace("\x1b[m\x1b[0;33m","").replace("\x1b[m","").replace("\x1b[0;32m","").replace("\x1b[1;32m","")
        print("output is",output)
        if "TLS 1.2    offered" in output:
                print("TLSv1.2 is active")
                logging.info("TLSv1.2 is active")
                assert False
        else:
                print("TLSv1.2 is not active")
                logging.error("TLSv1.2 is not active")
                assert True
	child.close()



    @pytest.mark.run(order=114)
    def test_114_validate_only_DHE_ciphers__are_active_when_TLSv1_2_is_enabled_for_saml_port_with_testssl_sh_script_for_saml_port_with_testssl_sh(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh -E --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(25)
	child.expect('-->')
        child.sendline('yes')
        child.expect('Done')
        output = child.before
        print("output is",output)
        data = ['DHE-RSA-AES256-GCM-SHA384','DHE-RSA-AES256-SHA256','DHE-RSA-AES256-SHA','DHE-RSA-AES128-GCM-SHA256','DHE-RSA-AES128-SHA256','DHE-RSA-AES128-SHA']
        for i in  data:
            	if i in output:
                	print(i, "is active")
                	assert False
        	else:
                	print(i," is not active")
                	assert True
	print("all DHE ciphers for TLSV1.2 are active")
	child.close()




    @pytest.mark.run(order=115)
    def test_115_validate_RC4_and_3DES_ciphers_are_not_active_when_only_DHE_ciphers_are_enabled_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --vulnerable '+config.grid_mgmt_ip+':8765 ')
        sleep(40)
	child.expect('-->')
        child.sendline('yes')
        child.expect('Done')
        output = child.before
        output = output.replace("\x1b[m","").replace("\x1b[1;32m","").replace("\x1b[0;31m","").replace("\x1b[0;32m","")
        print("output is",output)
	if (("SWEET32 (CVE-2016-2183, CVE-2016-6329)    not vulnerable" in output) and ("RC4 (CVE-2013-2566, CVE-2015-2808)        no RC4 ciphers detected" in output)):
                print("Validated RC4 and 3DES ciphers not active when only DHE ciphers are active")
                logging.info("Validated RC4 and 3DES ciphers not active for saml port with testssl.sh script")
                assert True
        else:
                print("Validated RC4 and 3DES ciphers  active when only DHE ciphers are active")
                logging.error("Validated RC4 and 3DES ciphers active for saml port with testssl.sh script")
                assert False
	child.close()
	sleep(10)



    @pytest.mark.run(order=116)
    def test_116_login_to_CLI_as_SAML_with_superuser(self):
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
        child.sendline(config.okta_username)
        sleep(10)
        child.expect('OKTA SAML password:')
        sleep(5)
        child.sendline(config.okta_password)
        child.expect('Infoblox >')
        child.sendline('show network')
        sleep(20)
        child.expect('Infoblox >')
        c= child.before
        child.sendline('exit')
        child.expect('login:')
        assert re.search(r'.*Current LAN1 Network Settings.*',c)
        logging.info("Test Case  execution completed")






    @pytest.mark.run(order=117)
    def test_117_enabling_ciphers_not_supported_by_server_for_TLSv1_0(self):
        logging.info("enabling cipher not supported by server")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        log("start","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set ssl_tls_ciphers enable TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384')
        child.expect('>')
        child.sendline('set ssl_tls_ciphers enable TLS_DHE_DSS_WITH_AES_128_CBC_SHA256')
        child.expect('>')
        child.sendline('set ssl_tls_ciphers disable 6')
        child.expect('>')
        child.sendline('set ssl_tls_ciphers disable 5')
        child.expect('>')
        child.sendline('set ssl_tls_ciphers disable 4')
        child.expect('>')
        child.sendline('set ssl_tls_ciphers disable 3')
        child.expect('>')
        child.sendline('set ssl_tls_ciphers disable 2')
        child.expect('>')
        child.sendline('set ssl_tls_ciphers disable 1')
        child.expect('>')
	child.sendline('set ssl_tls_protocols enable TLSv1.0')
	child.expect('>')
	child.sendline('set ssl_tls_protocols disable TLSv1.2')
	child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSv1.1')
        child.expect('>')
        child.sendline('show ssl_tls_ciphers')
        child.expect('>')
        output = child.before
        sleep(120)
        log("stop","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        if (("TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 enabled" in output) and ("TLS_DHE_DSS_WITH_AES_128_CBC_SHA256     enabled" in output)):
		print("ciphers not supported by server for TLSv1.0 are enabled")
        else:
		print("ciphers not supported by server for TLSv1.0 are not enabled")
        data = ["Restarting saml","TLS PROTOCOL for the SAML is set to PROTOCOL_TLSv1","ECDHE-ECDSA-AES256-GCM-SHA384","DHE-DSS-AES128-SHA256"]
        for i in data:
                logs=logv(i,"/infoblox/var/infoblox.log",config.grid_mgmt_ip)
                print("logs are",logs)
                if logs != None:
                        print("validated ciphers not supported by server for TLSv1.0 are active in logs")
                        logging.info("validated ciphers not supported by server for TLSv1.0 are active in logs")
			assert True
                else:
                        print("validated ciphers not supported by server for TLSv1.0 are not active in logs")
                        logging.error("validated ciphers not supported by server for TLSv1.0 are not active in logs")
			assert False
	child.sendline('exit')
	child.close()
	sleep(10)



    @pytest.mark.run(order=118)
    def test_118_validate_TLS_protocol_TLSv1_0_is_not_active_when_only_ciphers_not_supported_by_server_are_active_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.0 not   active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLS protocols TLSv1  is not  active when only ciphers not supported by server are active for saml port")
                logging.info("TLS protocols TLSv1 not  active when only ciphers not supported by server are active for saml port")
                assert True
        else:
                logging.error("TLS protocols TLSv1   active when only ciphers not supported by server are active for saml port")
                print("TLS protocols TLSv1   active for saml port")
                assert False
	child.close()





    @pytest.mark.run(order=119)
    def test_119_validate_ciphers_which_are_not_supported_by_server_are_not_active_for_saml_port_with_nmap(self):
        logging.info("validate ciphers which are not supported by server are not active(TLSv1.0) for saml port with nmap")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("nmap -sV --script ssl-enum-ciphers -p 8765 "+config.grid_mgmt_ip)
        sleep(15)
        child.expect('#')
        output = child.before
        output=output.replace("\r\n| ","")
        print("output is", output)
        if (("TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384" not in output) and ("TLS_DHE_DSS_WITH_AES_128_CBC_SHA256" not in output)):
                print("ciphers not supported by server are not active")
                logging.info("ciphers not supported by server are not active")
                assert True
        else:
                print("ciphers not  supported by server are active")
                logging.error("ciphers not  supported by server are active")
                assert False
	child.close()



    @pytest.mark.run(order=120)
    def test_120_validate_TLS_protocol_TLSv1_0_not_active_when_only_ciphers_not_supported_by_server_are_active_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --protocols --fast --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(15)
	child.expect('proceed')
        output = child.before
	print ("output is", output)
        if "-->" in output:
                print("expected output found")
                child.sendline('yes')
                child.expect('-->')
		child.sendline('yes')
		child.expect('#')
                output = child.before
		output = output.replace("\x1b[m","").replace("\x1b[m\x1b[0;33m","").replace("\x1b[m\x1b[1;33m","").replace("\x1b[0;33m","")
		print ("output iss",output)
                if "TLS 1      not offered" in output:
                        print("TLSv1 is not active")
                        assert True
                else:
                        print("TLSV1 is not active")
                        assert False
        else:
                print("expected output not found")
                assert False
	child.close()
	sleep(10)

    @pytest.mark.run(order=121)
    def test_121_validate_cipher_not_supported_by_server_are_not_active_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('export TESTSSL_INSTALL_DIR=/tmp')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh -E --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(15)
        child.expect('proceed')
	output = child.before
	if "-->" in output:
		print("expected output found")
		child.sendline('yes')
		child.expect('Done')
        	output = child.before
	#	print output
       		if (("ECDHE-ECDSA-AES256-GCM-SHA384" not in output)  and ("DHE-DSS-AES128-SHA256" not in output)):
                	print("ciphers not  supported by server are not active")
                	assert True
        	else:
                	print("ciphers not supported by server are active")
                	assert False
	else:
		print("expected output not found")
		assert False
	child.close()


    @pytest.mark.run(order=122)
    def test_122_validate_handshake_is_getting_failed_for_TLSv1_when_only_ciphers_not_supported_by_server_are_active_for_saml_port_with_testssl_sh_script(self):
        logging.info("validate handshake is getting failed for TLSv1 for saml port with testssl.sh script")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --vulnerable '+config.grid_mgmt_ip+':8765 ')
        sleep(20)
        child.expect('proceed')
        output = child.before
        if "-->" in output:
                print("expected output found")
                child.sendline('yes')
		sleep(5)
                child.expect('Done')
                output = child.before
                print ("output is",output)
		if "OpenSSL handshake didn\'t succeed" in output:
			print("handshake got failed")
			assert True
		else:
			print("handshake succedded")
			assert False
	child.close()
	sleep(10)
		


    @pytest.mark.run(order=123)
    def test_123_enabling_TLSv1_1_with_ciphers_not_supported_by_server(self):
        logging.info("enabling tLSv1.1 with ciphers not supported by server")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        log("start","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set ssl_tls_protocols enable TLSv1.1')
        child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSv1.0')
        child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSv1.2')
        child.expect('>')
        child.sendline('show ssl_tls_protocols')
        child.expect('>')
        output = child.before
        sleep(120)
        log("stop","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        if "Current configuration for the SAML  : TLSv1.1" in output:
		print("TLSv1.1 is enabled with ciphers not supported by server")
                logging.info("TLSv1.1 is enabled with ciphers not supported by server")
		assert True
        else:
		print("TLSv1.1 is not  enabled with ciphers not supported bt server")
		logging.info("TLSv1.1 is not  enabled with cihers not supported bt server")
		assert False
        data = ["Restarting saml","TLS PROTOCOL for the SAML is set to PROTOCOL_TLSv1_1","ECDHE-ECDSA-AES256-GCM-SHA384","DHE-DSS-AES128-SHA256"]
        for i in data:
                logs=logv(i,"/infoblox/var/infoblox.log",config.grid_mgmt_ip)
                print("logs are",logs)
                if logs != None:
			print("validated ciphers not supported by server for TLSv1.1 are enabled  in logs")
                        assert True
                else:
			print("validated ciphers not supported by server for TLSv1.1 are not enabled  in logs")
                        logging.error("validation failed")
                        assert False
	child.sendline('exit')
	child.close()
	sleep(10)



    @pytest.mark.run(order=124)
    def test_124_validate_TLS_protocol_TLSv1_1_not_active_when_only_ciphers_not_supported_by_server_are_active_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.1 not  active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLS protocols TLSv1.1 not  activewhen only ciphers not supported by server are active for saml port")
                logging.info("TLS protocols TLSv1.1 not active when only ciphers not supported by server are active for saml port")
                assert True
        else:
		print("TLSv.1 is active when only ciphers not supported by server are active")
                assert False
	child.close()



    @pytest.mark.run(order=125)
    def test_125_validate_TLS_protocol_TLSv1_0_not_active_when_only_ciphers_not_supported_by_server_are_active_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.0 not  active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLS protocols TLSv1  not  active when only ciphers not supported by server are active")
                logging.info("TLS protocols TLSv1 not  active when only ciphers not supported by server are active")
                assert True
        else:
                logging.error("TLS protocols TLSv1  active when only ciphers not supported by server are active")
                print("TLS protocols TLSv1 active when only ciphers not supported by server are active")
                assert False
	child.close()

    @pytest.mark.run(order=126)
    def test_126_validate_TLS_protocol_TLSv1_2_not_active_when_only_ciphers_not_supported_by_server_are_active_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.2 not  active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_2")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLS protocols TLSv1.2  not  active when only ciphers not supported by server are active for saml port")
                logging.info("TLS protocols TLSv1.2 not  active when only ciphers not supported by server are active")
                assert True
        else:
                logging.error("TLS protocols TLSv1.2  active when only ciphers not supported by server are active")
                print("TLS protocols TLSv1.2 active when only ciphers not supported by server are active")
                assert False
	child.close()
	sleep(10)




    @pytest.mark.run(order=127)
    def test_127_validate_ciphers_which_are_not_supported_by_server_are_not_active_for_TLSv1_1_for_saml_port_with_nmap(self):
        logging.info("validate ciphers which are not supported by server are not active(TLSv1.1) for saml port with nmap")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("nmap -sV --script ssl-enum-ciphers -p 8765 "+config.grid_mgmt_ip)
        sleep(15)
        child.expect('#')
        output = child.before
        output=output.replace("\r\n| ","")
        print("output is", output)
        if (("TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384" not in output) and ("TLS_DHE_DSS_WITH_AES_128_CBC_SHA256" not in output)):
                print("ciphers not supported by server are not active for TLSv1.1")
                logging.info("ciphers not supported by server are not active")
                assert True
        else:
                print("ciphers not  supported by server are active for TLSv1.1")
                logging.error("ciphers not  supported by server are active")
                assert False
	child.close()



    @pytest.mark.run(order=128)
    def test_128_validate_TLS_protocol_TLSv1_1_not_active_when_only_ciphers_not_supported_by_server_are_active_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --protocols --fast --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(15)
        child.expect('proceed')
        new = child.before
        #print new
        if "-->" in new:
                print("expected output found")
                child.sendline('yes')
                child.expect('-->')
                child.sendline('yes')
                child.expect('#')
                output = child.before
                output = output.replace("\x1b[m","").replace("\x1b[m\x1b[0;33m","").replace("\x1b[m\x1b[1;33m","").replace("\x1b[0;33m","")
                print ("output iss",output)
                if "TLS 1.1    not offered" in output:
                        print("TLSv1.1 is not active")
                        assert True
                else:
                        print("TLSV1.1 is  active")
                        assert False
        else:
                print("expected output not found")
                assert False
	child.close()

    @pytest.mark.run(order=129)
    def test_129_validate_cipher_not_supported_by_server_are_not_active_for_TLSv1_1_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('export TESTSSL_INSTALL_DIR=/tmp')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh -E --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(15)
        child.expect('proceed')
        new = child.before
        #print new
        if "-->" in new:
                print("expected output found")
                child.sendline('yes')
                child.expect('Done')
                output = child.before
        #       print output
                if (("ECDHE-ECDSA-AES256-GCM-SHA384" not in output)  and ("DHE-DSS-AES128-SHA256" not in output)):
                        print("ciphers not  supported by server are not active")
                        assert True
                else:
                        print("ciphers not supported by server are active")
                        assert False
        else:
                print("expected output not found")
                assert False
	child.close()
	sleep(10)



    @pytest.mark.run(order=130)
    def test_130_validate_handshake_is_getting_failed_for_TLSv1_1_when_only_ciphers_not_supported_by_server_are_active_for_saml_port_with_testssl_sh_script(self):
        logging.info("validate handshake is getting failed for TLSv1.1 for saml port with testssl.sh script")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --vulnerable '+config.grid_mgmt_ip+':8765 ')
        sleep(20)
        child.expect('proceed')
        new = child.before
        #print new
        if "-->" in new:
                print("expected output found")
                child.sendline('yes')
                sleep(5)
                child.expect('Done')
                output = child.before
                print ("output is",output)
                if "OpenSSL handshake didn\'t succeed" in output:
			print("handshake got failed")
                        assert True
                else:
			print("handshake succedded")
                        assert False
	child.close()

    @pytest.mark.run(order=131)
    def test_131_enabling_TLSv1_2_with_ciphers_not_supported_by_server(self):
        logging.info("enabling tLSv1.2 with ciphers not supported by server")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        log("start","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('set ssl_tls_protocols  enable TLSV1.2')
        child.expect('>')
	child.sendline('set ssl_tls_protocols disable TLSv1.0')
	child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSv1.1')
        child.expect('>')
        child.sendline('show ssl_tls_protocols')
        child.expect('>')
        output = child.before
        sleep(120)
        log("stop","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        if "Current configuration for the SAML  : TLSv1.2" in output:
                print("TLSv1.1 is enabled with ciphers not supported by server")
                logging.info("TLSv1.1 is enabled with ciphers not supported by server")
		assert True
        else:
                print("TLSv1.1 is not  enabled with ciphers not supported bt server")
                logging.info("TLSv1.1 is not  enabled with cihers not supported bt server")
		assert False
        data = ["Restarting saml","TLS PROTOCOL for the SAML is set to PROTOCOL_TLSv1_2","ECDHE-ECDSA-AES256-GCM-SHA384","DHE-DSS-AES128-SHA256"]
        for i in data:
                logs=logv(i,"/infoblox/var/infoblox.log",config.grid_mgmt_ip)
                print("logs are",logs)
                if logs != None:
			print("validated ciphers not supported by server for TLSv1.2 are enabled  in logs")
			logging.info("validated ciphers not supported by server for TLSv1.2 are enabled  in logs")
                        assert True
                else:
			print("validated ciphers not supported by server for TLSv1.2 are not enabled in logs")
                        assert False
	child.close()
	sleep(10)

    @pytest.mark.run(order=132)
    def test_132_validate_TLS_protocol_TLSv1_2_not_active_when_only_ciphers_not_supported_by_server_are_active_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.1 not  active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_2")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                logging.info("TLS protocols TLSv1.2 not active when only ciphers not supported by server are active")
                assert True
        else:
		print("TLSv1.2 active when only ciphers not supported by server are active")
                assert False
	child.close()



    @pytest.mark.run(order=133)
    def test_133_validate_TLS_protocol_TLSv1_0_not_active_when_only_ciphers_not_supported_by_server_are_active_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.0 not  active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLS protocols TLSv1  not  active for saml port")
                logging.info("TLS protocols TLSv1 not  active for saml port")
                assert True
        else:
                logging.error("TLS protocols TLSv1  active for saml port")
                print("TLS protocols TLSv1 active for saml port")
                assert False
	child.close()




    @pytest.mark.run(order=134)
    def test_134_validate_TLS_protocol_TLSv1_1_not_active_when_only_ciphers_not_supported_by_server_are_active_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.1 not  active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLS protocols TLSv1.1 not  active for saml port")
                logging.info("TLS protocols TLSv1.1 not  active for saml port")
                assert True
        else:
                logging.error("TLS protocols TLSv1.1  active for saml port")
                print("TLS protocols TLSv1.1 active for saml port")
                assert False
	child.close()
	sleep(10)



    @pytest.mark.run(order=135)
    def test_135_validate_ciphers_which_are_not_supported_by_server_are_not_active_for_TLSv1_2_when_only_ciphers_not_supported_by_server_are_active_for_saml_port_with_nmap(self):
        logging.info("validate ciphers which are not supported by server are not active(TLSv1.2) for saml port with nmap")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("nmap -sV --script ssl-enum-ciphers -p 8765 "+config.grid_mgmt_ip)
        sleep(15)
        child.expect('#')
        output = child.before
        output=output.replace("\r\n| ","")
        print("output is", output)
        if (("TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384" not in output) and ("TLS_DHE_DSS_WITH_AES_128_CBC_SHA256" not in output)):
                print("ciphers not supported by server are not active for tls1.2")
                logging.info("ciphers not supported by server are not active for tls1.2")
                assert True
        else:
                print("ciphers not  supported by server are active for tls1.2")
                logging.error("ciphers not  supported by server are active for tls1.2")
                assert False
	child.close()




    @pytest.mark.run(order=136)
    def test_136_validate_TLS_protocol_TLSv1_2_not_active_when_only_ciphers_not_supported_by_server_are_active_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --protocols --fast --parallel '+config.grid_vip+':8765 ')
        sleep(15)
        child.expect('proceed')
        new = child.before
        #print new
        if "-->" in new:
                print("expected output found")
                child.sendline('yes')
                child.expect('-->')
                child.sendline('yes')
                child.expect('#')
                output = child.before
                output = output.replace("\x1b[m","").replace("\x1b[m\x1b[0;33m","").replace("\x1b[m\x1b[1;33m","").replace("\x1b[0;33m","")
                print ("output iss",output)
                if "TLS 1.2    not offered" in output:
                        print("TLSv1.2 is not active")
                        assert True
                else:
                        print("TLSV1.2 is  active")
                        assert False
        else:
                print("expected output not found")
                assert False
	child.close()


    @pytest.mark.run(order=137)
    def test_137_validate_cipher_not_supported_by_server_are_not_active_for_TLSv1_2_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('export TESTSSL_INSTALL_DIR=/tmp')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh -E --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(15)
        child.expect('proceed')
        new = child.before
        #print new
        if "-->" in new:
                print("expected output found")
                child.sendline('yes')
                child.expect('Done')
                output = child.before
        #       print output
                if (("ECDHE-ECDSA-AES256-GCM-SHA384" not in output)  and ("DHE-DSS-AES128-SHA256" not in output)):
                        print("ciphers not  supported by server are not active")
                        assert True
                else:
                        print("ciphers not supported by server are active")
                        assert False
        else:
                print("expected output not found")
                assert False
	child.close()
	sleep(10)



    @pytest.mark.run(order=138)
    def test_138_validate_handshake_is_getting_failed_for_TLSv1_when_only_ciphers_not_supported_by_server_are_active_for_saml_port_with_testssl_sh_script(self):
        logging.info("validate  handshake is getting failed for TLSv1.2 for saml port with testssl.sh script")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --vulnerable '+config.grid_mgmt_ip+':8765 ')
        sleep(20)
        child.expect('proceed')
        new = child.before
        #print new
        if "-->" in new:
                print("expected output found")
                child.sendline('yes')
                sleep(5)
                child.expect('Done')
                output = child.before
                print ("output is",output)
                if "OpenSSL handshake didn\'t succeed" in output:
                        print("handshake got failed")
                        assert True
                else:
                        print("handshake succedded")
                        assert False
	child.close()
    

    @pytest.mark.run(order=139)
    def test_139_enabling_RC4_cipher_with_TLSv1_0_TLSv1_1_TLSv1_2(self):
        logging.info("enabling RC4 cipher with TLSv1_0 TLSv1_1 TLSv1_2")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        log("start","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set ssl_tls_protocols enable TLSv1.1')
        child.expect('Infoblox >')
        child.sendline('set ssl_tls_protocols enable TLSv1.0')
        child.expect('>')
        child.sendline('set ssl_tls_protocols enable TLSv1.2')
        child.expect('>')
        child.sendline('set ssl_tls_ciphers enable TLS_RSA_WITH_RC4_128_SHA')
        child.expect('>')
        child.sendline('set ssl_tls_ciphers  disable 2')
        child.expect('>')
        child.sendline('set ssl_tls_ciphers  disable 1')
        child.expect('>')
        child.sendline('show ssl_tls_ciphers')
        child.expect('>')
        output = child.before
        #print('output is',output)
        sleep(120)
        log("stop","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
	data = ["Restarting saml","TLS CIPHERS for the SAML is set to RC4-SHA"]
        for i in data:
                logs=logv(i,"/infoblox/var/infoblox.log",config.grid_mgmt_ip)
                print("logs are",logs)
                if logs != None:
                        print("restarted saml and validated protocols binding to saml")
                        logging.info("restarted saml and validated protocols binding to saml")
                        assert True
                else:
                        print("validation failed")
                        logging.error("validation failed")
                        assert False
	child.close()
	sleep(10)


    @pytest.mark.run(order=140)
    def test_140_validate_TLS_protocol_TLSv1_0_TLSv1_1_TLSv1_2_and_RC4_cipher_active_for_saml_port_with_nmap(self):
        logging.info("validate TLSv1.0 TLSv1.1 TLSv1.2 and RC4 active for saml port with nmap")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("nmap -sV --script ssl-enum-ciphers -p 8765 "+config.grid_mgmt_ip)
        sleep(15)
        child.expect('#')
        output = child.before
        print("output is", output)
	data = ["TLSv1.0","TLSv1.1","TLSv1.2","TLS_RSA_WITH_RC4_128_SHA"]
	for i in data:
		if i in output:
			print(i,"is active")
			assert False
		else:
			print(i,"is not active")
			assert True
	child.close()



    @pytest.mark.run(order=141)
    def test_141_validate_TLS_protocol_TLSv1_active_when_RC4_cipher_active_for_saml_port_with_openssl(self):
    	logging.info("validate TLS protocol TLSv1 active when RC4 active for saml port")
    	child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
    	child.logfile=sys.stdout
    	child.expect('#')
    	child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1  -cipher RC4-SHA")
    	sleep(5)
    	child.sendline('\n')
    	child.sendline('\n')
    	child.expect('#')
    	output = child.before
    	print ("output is", output)
	if (("wrong version number" not in output) and ("ssl handshake failure" not in output) and ("Protocol  : TLSv1" in output)):
        	print("TLS protocols TLSv1.0 is active when RC4 is active for saml port")
        	logging.info("TLS protocols TLSv1.0 is active for saml port")
        	assert False
    	else:
        	print("TLS protocols TLSv1.0 is not active when RC4 is active active for saml port")
        	logging.error("TLS protocols TLSv1.0 is not active for saml port")
        	assert True
	child.close()

    @pytest.mark.run(order=142)
    def test_142_validate_TLS_protocol_TLSv1_1_active_when_RC4_cipher_active_for_saml_port_with_openssl(self):
    	logging.info("validating TLS protocol TLSv1.1 active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_1 -cipher RC4-SHA")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("wrong version number" not in output) and ("ssl handshake failure" not in output) and ("Protocol  : TLSv1.1" in output)):
        	print("TLS protocols TLSv1.1 is active when RC4 is active for saml port")
        	logging.info("TLS protocols TLSv1.1 is active for saml port")
                assert False
        else:
                print("TLS protocols TLSv1.0 is not active when RC4 is active active for saml port")
                logging.error("TLS protocols TLSv1.1 is not active for saml port")
                assert True
	child.close()
	sleep(10)



    @pytest.mark.run(order=143)
    def test_143_validate_TLS_protocol_TLSv1_2_active_when_RC4_cipher_active_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocol TLSv1.1 active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_2 -cipher RC4-SHA")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("wrong version number" not in output) and ("ssl handshake failure" not in output) and ("Protocol  : TLSv1.2" in output)):
                print("TLS protocols TLSv1.2 is active when RC4 is active for saml port")
                logging.info("TLS protocols TLSv1.2 is active for saml port")
                assert False
        else:
                print("TLS protocols TLSv1.2 is not active when RC4 is active active for saml port")
                logging.error("TLS protocols TLSv1.2 is not active for saml port")
                assert True
	child.close()




    @pytest.mark.run(order=144)
    def test_144_enabling_all_ciphers_with_TLSv1_0(self):
        logging.info("enabling all ciphers with TLSv1_0")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        log("start","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set ssl_tls_protocols enable TLSv1.0')
        child.expect('>')
	child.sendline('set ssl_tls_protocols disable TLSv1.2')
	child.expect('>')
	child.sendline('set ssl_tls_protocols disable TLSv1.1')
	child.expect('>')
        child.sendline('set ssl_tls_ciphers enable_all')
        child.expect('>')
        child.sendline('show ssl_tls_ciphers')
        child.expect('>')
        output = child.before
        #print('output is',output)
        sleep(120)
        log("stop","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        data = ['TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 enabled','TLS_DHE_DSS_WITH_AES_256_CBC_SHA        enabled','TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256 enabled','TLS_RSA_WITH_AES_256_CBC_SHA256         enabled ','TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256   enabled','TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256   enabled','TLS_RSA_WITH_3DES_EDE_CBC_SHA           enabled','TLS_DHE_DSS_WITH_AES_128_CBC_SHA256     enabled','TLS_DHE_DSS_WITH_AES_128_GCM_SHA256     enabled','TLS_DHE_DSS_WITH_AES_256_CBC_SHA256     enabled','TLS_DHE_DSS_WITH_AES_256_GCM_SHA384     enabled','TLS_RSA_WITH_RC4_128_SHA                enabled','TLS_DHE_DSS_WITH_AES_128_CBC_SHA        enabled','TLS_DH_DSS_WITH_3DES_EDE_CBC_SHA        enabled','TLS_DH_RSA_WITH_3DES_EDE_CBC_SHA        enabled','TLS_RSA_WITH_AES_256_CBC_SHA            enabled','TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA      enabled','TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA      enabled','TLS_RSA_WITH_AES_256_GCM_SHA384         enabled','TLS_RSA_WITH_AES_128_CBC_SHA256         enabled','TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384   enabled','TLS_RSA_WITH_AES_128_GCM_SHA256         enabled','TLS_RSA_WITH_AES_128_CBC_SHA            enabled','TLS_DHE_RSA_WITH_AES_256_CBC_SHA256     enabled','TLS_DHE_RSA_WITH_AES_256_GCM_SHA384     enabled','TLS_DHE_RSA_WITH_AES_128_CBC_SHA256     enabled','TLS_DHE_RSA_WITH_AES_128_CBC_SHA        enabled','TLS_DHE_RSA_WITH_AES_128_GCM_SHA256     enabled','TLS_DHE_RSA_WITH_AES_256_CBC_SHA        enabled']
        for i in data:
                if i in output:
                        print(i)
                        assert True
                else:
                        print(i)
                        assert False
	child.close()
	sleep(10)


    @pytest.mark.run(order=145)
    def test_145_validate_TLS_protocol_TLSv1_0_active_when_all_ciphers_are_enabled_for_saml_port_with_openssl(self):
            logging.info("validating TLS protocol TLSv1.1 and single cipher  active for saml port")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
            child.logfile=sys.stdout
            child.expect('#')
            child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1")
            sleep(5)
            child.sendline('\n')
            child.sendline('\n')
            child.expect('#')
            output = child.before
            print ("output is", output)
	    if (("wrong version number" not in output) and ("ssl handshake failure" not in output) and ("Protocol  : TLSv1" in output)):
                print("TLSv1 is  active when all ciphers are enabled")
                logging.info("TLS protocols TLSv1 is active for saml port")
                assert True
            else:
                print("TLS protocols TLSv1 is not  active when all ciphers are enabled for saml port")
                logging.error("TLS protocols TLSv1 is not active for saml port")
                assert False
	    child.close()



    @pytest.mark.run(order=146)
    def test_146_validate_all_ciphers_which_are_supported_by_server_for_TLSv1_are_active_for_saml_port_with_nmap(self):
        logging.info("validate all ciphers which are supported by server for TLSv1 are  active for saml port with nmap")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("nmap -sV --script ssl-enum-ciphers -p 8765 "+config.grid_mgmt_ip)
        sleep(15)
        child.expect('#')
        output = child.before
        output=output.replace("\r\n| ","")
        print("output is", output)
        data = ['TLSv1.0:     ciphers:       TLS_RSA_WITH_AES_256_CBC_SHA','TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA','TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA','TLS_RSA_WITH_AES_128_CBC_SHA']
        for i in data:
                if i in output:
                        print(i,"cipher is active")
                        logging.info("cipher is active")
                        assert True
                else:
                        print(i,"cipher is not active")
                        logging.error("cipher is not active")
                        assert False
	child.close()




    @pytest.mark.run(order=147)
    def test_147_validate_all_ciphers_which_are_supported_by_server_for_TLSv1_are_active_for_saml_port_with_testssl_sh(self):
        logging.info("validate all ciphers which are supported by server for TLSv1 are  active for saml port with testssl.sh")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh -E --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(10)
        child.expect('Done')
        output = child.before
        output = output.replace("\x1b[m  \r\n xc014","")
        print("output is",output)
        data = ['TLS 1',' ECDHE-RSA-AES256-SHA','AES256-SHA','ECDHE-RSA-AES128-SHA','AES128-SHA']
        for i in data:
                if i in output:
                        print(i,"cipher active")
                        assert True
                else:
                        print(i,"ciphers not active, verified with testssl.sh")
                        assert False
	child.close()
	sleep(10)

    @pytest.mark.run(order=148)
    def test_148_validated_RC4_and_3DES_ciphers_are_active_when_all_ciphers_are_enabled_for_saml_port_with_testssl_sh_script(self):
        logging.info("validate RC4 and 3DES ciphers are active for saml port with testssl.sh script")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --vulnerable '+config.grid_mgmt_ip+':8765 ')
        sleep(40)
        child.expect('Done')
        output = child.before
        output = output.replace("\x1b[m","").replace("\x1b[1;32m","").replace("\x1b[0;31m","").replace("\x1b[0;32m","").replace("\x1b[1;33m","")
        print('output is',output)
        if (("SWEET32 (CVE-2016-2183, CVE-2016-6329)    not vulnerable" in output) and ("RC4 (CVE-2013-2566, CVE-2015-2808)        no RC4 ciphers detected" in output)):
                logging.info("RC4 and 3DES ciphers are active for saml port with testssl.sh script")
                print("RC4 and 3DES ciphers are active when all ciphers are enabled for saml port with testssl.sh script")
                assert True
        else:
                logging.info("RC4 and 3DES ciphers are not active for saml port with testssl.sh script")
                print("RC4 and 3DES ciphers are not active when all ciphers are enabled for saml port with testssl.sh script")
                assert False
	child.close()


    @pytest.mark.run(order=149)
    def test_149_login_to_CLI_as_SAML_with_superuser(self):
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
        child.sendline(config.okta_username)
        sleep(10)
        child.expect('OKTA SAML password:')
        sleep(5)
        child.sendline(config.okta_password)
        child.expect('Infoblox >')
        child.sendline('show network')
        sleep(20)
        child.expect('Infoblox >')
        c= child.before
        child.sendline('exit')
        child.expect('login:')
        assert re.search(r'.*Current LAN1 Network Settings.*',c)
        logging.info("Test Case  execution completed")




    @pytest.mark.run(order=150)
    def test_150_enabling_TLSv1_1_with_all_ciphers_enabled(self):
        logging.info("enabling TLSv1.1 with all ciphers enabled")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        log("start","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set ssl_tls_protocols  enable TLSv1.1')
        child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSv1.0')
        child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSv1.2')
        child.expect('>')
        child.sendline('show ssl_tls_protocols')
        child.expect('Infoblox >')
        output = child.before
        #print("output is",output)
        sleep(120)
        log("stop","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        if "Current configuration for the SAML  : TLSv1.1" in output:
                print("TLSv1.1 is enabled")
                logging.info("TLSv1.1 is enabled")
		assert True
        else:
                print("TLSv1.1 is not enabled")
                logging.info("TLSv1.1 is not enabled")
		assert False
        data = ["Restarting saml","TLS PROTOCOL for the SAML is set to PROTOCOL_TLSv1_1"]
        for i in data:
                logs=logv(i,"/infoblox/var/infoblox.log",config.grid_mgmt_ip)
                print("logs are",logs)
                if logs != None:
                        print("validated TLS protocols set to TLSv1.1 in logs when all ciphers are enabled")
                        assert True
                else:
                        print("TLS protocols not set to TLSv1.1 in logs when all ciphers are enabled")
                        assert False
	child.sendline('exit')
	child.close()
	sleep(10)


    @pytest.mark.run(order=151)
    def test_151_validate_TLS_protocol_TLSv1_1_active_when_all_ciphers_are_enabled_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.1  when all ciphers are enabled active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("wrong version number" not in output) and ("ssl handshake failure" not in output) and ("Protocol  : TLSv1.1" in output)):
                print("TLS protocols TLSv1.1   active when all ciphers are enabled  for saml port")
                logging.info("TLS protocols TLSv1.1 active when all ciphers are enabled for saml port")
                assert True
        else:
                logging.error("TLS protocols TLSv1.1 not active when all ciphers are enabled for saml port")
                print("TLS protocols TLSv1.1 not active when all ciphers are enabled for saml port")
                assert False
	child.close()




    @pytest.mark.run(order=152)
    def test_152_validate_TLS_protocol_TLSv1_0_not_active_when_all_ciphers_are_enabled_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.0 not  active  when all ciphers are enabled for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLS protocols TLSv1  not  active when all ciphers are enabled for saml port")
                logging.info("TLS protocols TLSv1 not  active when all ciphers are enabled for saml port")
                assert True
        else:
                logging.error("TLS protocols TLSv1  active when all ciphers are enabled for saml port")
                print("TLS protocols TLSv1 active when all ciphers are enabled for saml port")
                assert False
	child.close()


    @pytest.mark.run(order=153)
    def test_153_validate_TLS_protocol_TLSv1_2_not_active_when_all_ciphers_are_enabled_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.2 not  active when all ciphers are enabled for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_2")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLS protocols TLSv1_2  not  active when all ciphers are enabled for saml port")
                logging.info("TLS protocols TLSv1_2 not  active when all ciphers are enabled for saml port")
                assert True
        else:
                logging.error("TLS protocols TLSv1_2  active when all ciphers are enabled for saml port")
                print("TLS protocols TLSv1_2 active when all ciphers are enabled for saml port")
                assert False
	child.close()
	sleep(10)




    @pytest.mark.run(order=154)
    def test_154_validate_all_ciphers_which_are_supported_by_server_for_TLSv1_1_are_active_for_saml_port_with_nmap(self):
        logging.info("validate all ciphers which are supported by server for TLSv1_1 are  active for saml port with nmap")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("nmap -sV --script ssl-enum-ciphers -p 8765 "+config.grid_mgmt_ip)
        sleep(15)
        child.expect('#')
        output = child.before
        output=output.replace("\r\n| ","")
        print("output is", output)
        data = ['TLSv1.1:     ciphers:       TLS_RSA_WITH_AES_256_CBC_SHA','TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA','TLS_RSA_WITH_AES_128_CBC_SHA'	,'TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA']
        for i in data:
                if i in output:
                        print(i,"cipher is active")
                        logging.info("cipher is active")
                        assert True
                else:
                        print(i,"cipher is not active")
                        logging.error("cipher is not active")
                        assert False
	child.close()





    @pytest.mark.run(order=155)
    def test_155_validate_TLS_protocol_TLSv1_1_active_with_all_supported_ciphers_for_saml_port_with_testssl_sh_script(self):
        logging.info("validate TLS  protocol TLSv1.1  active  with all supported ciphers for saml port with testssl_sh script")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --protocols --fast --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(25)
        child.expect('Done')
        output = child.before
        output = output.replace("\x1b[m\x1b[1;33m","").replace("\x1b[m\x1b[0;33m","").replace("\x1b[m","").replace("\x1b[0;32m","")
        print("output is",output)
        if "TLS 1.1    offered" in output:
                print("TLSv1.1 is enabled with testssl.sh script")
                logging.info(" TLSv1.1 is enabled with testssl.sh script")
                assert True
        else:
                print("validated TLSv1.1 is not enabled with testssl.sh script")
                logging.error("validated TLSv1.1 is not enabled with testssl.sh script")
                assert False
	child.close()



    @pytest.mark.run(order=156)
    def test_156_validate_all_ciphers_which_are_supported_by_server_for_TLSv1_1_are_active_for_saml_port_with_testssl_sh(self):
        logging.info("validate all ciphers which are supported by server for TLSv1_1 are  active for saml port with testssl.sh")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh -E --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(25)
        child.expect('Done')
        output = child.before
        output = output.replace("\x1b[m  \r\n xc014","")
        print("output is",output)
        data = ['TLS 1.1','ECDHE-RSA-AES256-SHA','AES256-SHA','ECDHE-RSA-AES128-SHA','AES128-SHA']
        for i in data:
                if i in output:
                        print(i,"cipher active")
                        assert True
                else:
                        print(i,"ciphers not active, verified with testssl.sh")
                        assert False
	child.close()


    @pytest.mark.run(order=157)
    def test_157_validate_RC4_and_3DES_ciphers_are_active_when_all_ciphers_are_enabled_for_saml_port_with_testssl_sh_script(self):
        logging.info("validate RC4 and 3DES ciphers are active when all ciphers are enabled for saml port with testssl.sh script")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --vulnerable '+config.grid_mgmt_ip+':8765 ')
        sleep(40)
        child.expect('Done')
        output = child.before
        output = output.replace("\x1b[m","").replace("\x1b[1;32m","").replace("\x1b[0;31m","").replace("\x1b[0;32m","").replace("\x1b[1;33m","")
        print('output is',output)
        if (("SWEET32 (CVE-2016-2183, CVE-2016-6329)    not vulnerable" in output) and ("RC4 (CVE-2013-2566, CVE-2015-2808)        no RC4 ciphers detected" in output)):
                logging.info("RC4 and 3DES ciphers are active when all ciphers are enabled for saml port with testssl.sh script")
                print("RC4 and 3DES ciphers are active when all ciphers are enabled for saml port with testssl.sh script")
                assert True
        else:
                logging.info("RC4 and 3DES ciphers are not active when all ciphers are enabled for saml port with testssl.sh script")
                print("RC4 and 3DES ciphers are not active when all ciphers are enabled for saml port with testssl.sh script")
                assert False
	child.close()
	sleep(10)



    @pytest.mark.run(order=158)
    def test_158_login_to_CLI_as_SAML_with_superuser(self):
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
        child.sendline(config.okta_username)
        sleep(10)
        child.expect('OKTA SAML password:')
        sleep(5)
        child.sendline(config.okta_password)
        child.expect('Infoblox >')
        child.sendline('show network')
        sleep(20)
        child.expect('Infoblox >')
        c= child.before
        child.sendline('exit')
        child.expect('login:')
        assert re.search(r'.*Current LAN1 Network Settings.*',c)
        logging.info("Test Case  execution completed")





    @pytest.mark.run(order=159)
    def test_159_enabling_tls_protocols_TLSv1_2_with_all_ciphers_enabled(self):
        logging.info("enabling tls protocols TLSv1.2 with all ciphers enabled")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        log("start","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set ssl_tls_protocols enable TLSv1.2')
        child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSv1.0')
        child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSv1.1')
        child.expect('>')
        child.sendline('show ssl_tls_protocols')
        child.expect('>')
        output = child.before
        sleep(120)
        log("stop","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        if "Current configuration for the SAML  : TLSv1.2" in output:
                print("tLSv1.2 is enable")
		assert True
        else:
                print("TLSv1.2 is not enabled")
		assert False
        data = ["Restarting saml","TLSv1_2"]
        for i in data:
                logs=logv(i,"/infoblox/var/infoblox.log",config.grid_mgmt_ip)
                print("logs are",logs)
                if logs != None:
			print("validated TLSv1.2 is active when all ciphers are active")
                        logging.info("validated TLSv1.2 is active when all ciphers are active")
			assert True
                else:
                        print("validated TLSv1.2 is not active when all ciphers are active")
                        logging.error("validated TLSv1.2 is not active when all ciphers are active")
			assert False
	child.sendline('exit')
	child.close()
	sleep(10)

    @pytest.mark.run(order=160)
    def test_160_validate_TLS_protocol_TLSv1_2_active_when_all_ciphers_are_enabled_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.2  active when all ciphers are enabled for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_2")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("wrong version number" not in output) and ("ssl handshake failure" not in output) and ("Protocol  : TLSv1.2" in output)):
                print("TLS protocols TLSv1.2   active when all ciphers are enabled for saml port")
                logging.info("TLS protocols TLSv1.2 active when all ciphers are enabled for saml port")
                assert True
        else:
                logging.error("TLS protocols TLSv1.2 not active when all ciphers are enabled for saml port")
                print("TLS protocols TLSv1.2 not active when all ciphers are enabled for saml port")
                assert False
	child.close()



    @pytest.mark.run(order=161)
    def test_161_validate_TLS_protocol_TLSv1_0_not_active_when_all_ciphers_are_enabled_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.0 not  active when all ciphers are enabled for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLS protocols TLSv1  not  active when all ciphers are enabled for saml port")
                logging.info("TLS protocols TLSv1 not  active when all ciphers are enabled for saml port")
                assert True
        else:
                logging.error("TLS protocols TLSv1  active when all ciphers are enabled for saml port")
                print("TLS protocols TLSv1 active when all ciphers are enabled for saml port")
                assert False
	child.close()



    @pytest.mark.run(order=162)
    def test_162_validate_TLS_protocol_TLSv1_1_not_active_when_all_ciphers_are_enabled_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.1 not  active when all ciphers are enabled for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("no protocols available" in output) or ("SSL alert number 70" in output) or ("SSL alert number 40" in output) or ("unsupported protocol" in output) or ("handshake failure" in output)):
                print("TLS protocols TLSv1_1  not  active when all ciphers are enabled for saml port")
                logging.info("TLS protocols TLSv1_1 not  active when all ciphers are enabled for saml port")
                assert True
        else:
                logging.error("TLS protocols TLSv1_1  active when all ciphers are enabled for saml port")
                print("TLS protocols TLSv1_1 active when all ciphers are enabled for saml port")
                assert False
	child.close()




    @pytest.mark.run(order=163)
    def test_163_validate_all_ciphers_which_are_supported_by_server_for_TLSv1_2_are_active_for_saml_port_with_nmap(self):
        logging.info("validate all ciphers which are supported by server for TLSv1_2 are  active for saml port with nmap")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("nmap -sV --script ssl-enum-ciphers -p 8765 "+config.grid_mgmt_ip)
        sleep(15)
        child.expect('#')
        output = child.before
        output=output.replace("\r\n| ","")
        print("output is", output)
        data = ['TLSv1.2:     ciphers:       TLS_RSA_WITH_AES_256_CBC_SHA256','TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA','TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256','TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256','TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA','TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384','TLS_RSA_WITH_AES_128_CBC_SHA','TLS_RSA_WITH_AES_128_CBC_SHA256','TLS_RSA_WITH_AES_128_GCM_SHA256','TLS_RSA_WITH_AES_256_CBC_SHA','TLS_RSA_WITH_AES_256_GCM_SHA384']
        for i in data:
                if i in output:
                        print(i,"cipher is active")
                        logging.info("cipher is active")
                        assert True
                else:
                        print(i,"cipher is not active")
                        logging.error("cipher is not active")
                        assert False
	child.close()
	sleep(10)


    @pytest.mark.run(order=164)
    def test_164_validate_TLS_protocol_TLSv1_2_active_with_all_supported_ciphers_for_saml_port_with_testssl_sh_script(self):
        logging.info("validate TLS  protocol TLSv1.2  active  with all supported ciphers for saml port with testssl_sh script")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --protocols --fast --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(25)
        child.expect('Done')
        output = child.before
        output = output.replace("\x1b[m\x1b[1;33m","").replace("\x1b[m\x1b[0;33m","").replace("\x1b[m","").replace("\x1b[0;32m","").replace("\x1b[1;32m","").replace("\x1b[1;33m","")
        print("output is",output)
        if "TLS 1.2    offered" in output:
                print("validated TLSv1.2 is active when all ciphers are enabled with testssl.sh script")
                logging.info(" TLSv1.2 is active when all ciphers are enabled with testssl.sh script")
                assert True
        else:
                print("validated TLSv1.2 is not enabled when all ciphers are enabled with testssl.sh script")
                logging.error("validated TLSv1.2 is not enabled when all ciphers are enabled with testssl.sh script")
                assert False
	child.close()



    @pytest.mark.run(order=165)
    def test_165_validate_all_ciphers_which_are_supported_by_server_for_TLSv1_2_are_active_for_saml_port_with_testssl_sh(self):
        logging.info("validate all ciphers which are supported by server for TLSv1_2 are  active for saml port with testssl.sh")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh -E --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(25)
        child.expect('Done')
        output = child.before
        print("output is",output)
        data = ['ECDHE-RSA-AES256-GCM-SHA384','ECDHE-RSA-AES256-SHA','AES256-GCM-SHA384','AES256-SHA256','AES256-SHA','ECDHE-RSA-AES128-GCM-SHA256','ECDHE-RSA-AES128-SHA256','ECDHE-RSA-AES128-SHA','AES128-GCM-SHA256','AES128-SHA256','AES128-SHA']
        for i in data:
                if i in output:
                        print(i,'cipher is active for TLSv1.2')
                        assert True
                else:
                        print(i,'cipher is not active for TLSv1.2')
                        assert False
	child.close()




    @pytest.mark.run(order=166)
    def test_166_validated_RC4_and_3DES_ciphers_are_active_when_all_ciphers_are_enabled_for_saml_port_with_testssl_sh_script(self):
        logging.info("validate RC4 and 3DES ciphers are active when all ciphers are enabled for saml port with testssl.sh script")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --vulnerable '+config.grid_mgmt_ip+':8765 ')
        sleep(40)
        child.expect('Done')
        output = child.before
        output = output.replace("\x1b[m","").replace("\x1b[1;32m","").replace("\x1b[0;31m","").replace("\x1b[0;32m","").replace("\x1b[1;33m","")
        print('output is',output)
        if (("SWEET32 (CVE-2016-2183, CVE-2016-6329)    not vulnerable" in output) and ("RC4 (CVE-2013-2566, CVE-2015-2808)        no RC4 ciphers detected" in output)):
                logging.info("RC4 and 3DES ciphers are active when all ciphers are enabled for saml port with testssl.sh script")
                print("RC4 and 3DES ciphers are active when all ciphers are enabled for saml port with testssl.sh script")
                assert True
        else:
                logging.info("RC4 and 3DES ciphers are not active when all ciphers are enabled for saml port with testssl.sh script")
                print("RC4 and 3DES ciphers are not activewhen all ciphers are enabled  for saml port with testssl.sh script")
                assert False
	child.close()



    @pytest.mark.run(order=167)
    def test_167_login_to_CLI_as_SAML_with_superuser(self):
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
        child.sendline(config.okta_username)
        sleep(10)
        child.expect('OKTA SAML password:')
        sleep(5)
        child.sendline(config.okta_password)
        child.expect('Infoblox >')
        child.sendline('show network')
        sleep(20)
        child.expect('Infoblox >')
        c= child.before
        child.sendline('exit')
        child.expect('login:')
        assert re.search(r'.*Current LAN1 Network Settings.*',c)
        logging.info("Test Case  execution completed")





    @pytest.mark.run(order=168)
    def test_168_disabling_weak_ciphers_for_TLSv1_2(self):
	logging.info("enabling tls protocols TLSv1_1")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
	log("start","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set ssl_tls_protocols enable TLSv1.2')
        child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSv1.0')
        child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSv1.1')
        child.expect('>')
        child.sendline('set ssl_tls_ciphers  disable 9')
        child.expect('>')
        child.sendline('set ssl_tls_ciphers  disable 3')
        child.expect('>')
        child.sendline('set ssl_tls_ciphers  disable 1')
        child.expect('>')
        child.sendline('show ssl_tls_ciphers')
        child.expect('>')
        output = child.before
        #print ("output is" ,output)
        sleep(110)
        log("stop","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
	if (("TLS_RSA_WITH_3DES_EDE_CBC_SHA           disabled" in output) and ("TLS_RSA_WITH_RC4_128_SHA                disabled" in output) and ("TLS_DH_RSA_WITH_3DES_EDE_CBC_SHA        disabled" in output)):
		print("weak ciphers are disabled for TLSv1.2")
		assert True
	else:
		print("weak ciphers are not disabled")
		assert False
	data = ["Restarting saml","TLS PROTOCOL for the SAML is set to PROTOCOL_TLSv1_2"]
        for i in data:
                logs=logv(i,"/infoblox/var/infoblox.log",config.grid_mgmt_ip)
                print("logs are" , logs)
                if logs != None:
                        print("validated tls protocols set to TLSv1.2 in logs when weak ciphers are disabled")
                        assert True
                else:
                        print("validated TLSv1.2 is not active in logs when weak ciphers are disabled")
                        assert False
	child.sendline('exit')
	child.close()
	sleep(10)




    @pytest.mark.run(order=169)
    def test_169_validate_TLS_protocol_TLSv1_2_active_when_weak_ciphers_are_disabled_for_saml_port_with_openssl(self):
        logging.info("validating TLS protocols TLSv1.2 active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_2")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("wrong version number" not in output) and ("ssl handshake failure" not in output) and ("Protocol  : TLSv1.2" in output)):
	    print("TLS protocols TLSv1.2   active when weak ciphers are disabled for saml port")      
            logging.info("TLS protocols TLSv1.2  active when weak ciphers are disabled for saml port")
            assert True
        else:
            print("TLS protocols TLSv1.2  not active when weak ciphers are disabled for saml port")
            logging.error("TLS protocols TLSv1.2 not  active when weak ciphers are disabled for saml port")
            assert False
	child.close()

    

    @pytest.mark.run(order=170)
    def test_170_validate_weak_ciphers_not_active_for_TLSv1_2_for_saml_port_with_nmap(self):
        logging.info("validating TLS protocol TLSv1.1 active for saml port with nmap")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("nmap -sV --script ssl-enum-ciphers -p 8765 "+config.grid_mgmt_ip)
        sleep(15)
        child.expect('#')
        output = child.before
        print ("output is", output)
	data = ['TLS_RSA_WITH_3DES_EDE_CBC_SHA','TLS_RSA_WITH_RC4_128_SHA','TLS_DHE_RSA_WITH_3DES_EDE_CBC_SHA']
	for i in data:
		if i not in output:
			print(i,"is not  active")
			assert True
		else:
			print(i,"is  active")
			assert False
	print("disabled all weak ciphers")
	child.close()
		


    @pytest.mark.run(order=171)
    def test_171_validate_TLS_protocol_TLSv1_2_active_when_weak_ciphers_are_disabled_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --protocols --fast --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(25)
        child.expect('Done')
        output = child.before
        output1 = output.replace("\x1b[m\x1b[1;33m","").replace("\x1b[m\x1b[0;33m","").replace("\x1b[m","").replace("\x1b[0;32m","").replace("\x1b[1;32m","")
        #print("output is",output1)
        if "TLS 1.2    offered" in output1:
                print("validated TLSv1.2 is enabled with testssl.sh script")
                logging.info("validated TLSv1.2 is enabled with testssl.sh script")
                assert True
        else:
                print("validated TLSv1.2 is not enabled with testssl.sh script")
                logging.error("validated TLSv1.2 is not enabled with testssl.sh script")
                assert False
	child.close()




    @pytest.mark.run(order=172)
    def test_172_validated_weak_ciphers_are_not_active_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('export TESTSSL_INSTALL_DIR=/tmp')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh -E --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(25)
        child.expect('Done')
        output = child.before
        print("output is",output)
        data = ['TLS_RSA_WITH_3DES_EDE_CBC_SHA','TLS_RSA_WITH_RC4_128_SHA','TLS_DHE_RSA_WITH_3DES_EDE_CBC_SHA']
        for i in data:
                if i not in output:
                        print(i,"is not  active")
                        assert True
                else:
                        print(i,"is  active")
                        assert False
        print("disabled all weak ciphers")
	child.close()
	sleep(10)

    @pytest.mark.run(order=173)
    def test_173_validate_RC4_and_3DES_ciphers_are_not_active_when_weak_ciphers_are_disabled_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('export TESTSSL_INSTALL_DIR=/tmp')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --vulnerable '+config.grid_mgmt_ip+':8765 ')
        sleep(40)
        child.expect('Done')
        output = child.before
        output = output.replace("\x1b[m","").replace("\x1b[1;32m","").replace("\x1b[0;31m","").replace("\x1b[0;32m","").replace("\x1b[1;33m","")
        print("output isss",output)
	if (("SWEET32 (CVE-2016-2183, CVE-2016-6329)    not vulnerable" in output) and ("RC4 (CVE-2013-2566, CVE-2015-2808)        no RC4 ciphers detected" in output)):
                logging.info("Validated RC4 and 3DES ciphers not active when weak ciphers are disabled for saml port with testssl.sh script")
		print("Validated RC4 and 3DES ciphers not active when weak ciphers are disabled")
                assert True
        else:
                print("Validated RC4 and 3DES ciphers active for saml port with testssl.sh script")
                logging.error("Validated RC4 and 3DES ciphers active for saml port with testssl.sh script")
                assert False
	child.close()


    @pytest.mark.run(order=174)
    def test_174_login_to_CLI_as_SAML_with_superuser(self):
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
        child.sendline(config.okta_username)
        sleep(10)
        child.expect('OKTA SAML password:')
        sleep(5)
        child.sendline(config.okta_password)
        child.expect('Infoblox >')
        child.sendline('show network')
        sleep(20)
        child.expect('Infoblox >')
        c= child.before
        child.sendline('exit')
        child.expect('login:')
        assert re.search(r'.*Current LAN1 Network Settings.*',c)
        logging.info("Test Case  execution completed")



    @pytest.mark.run(order=175)
    def test_175_Create_a_group_named_asmgroup(self):
        print("Creating a group named 'asmgroup'")
        data={"name":"asmgroup","superuser":True}
        response = ib_NIOS.wapi_request('POST',object_type="admingroup",fields=json.dumps(data),grid_vip=config.grid_mgmt_ip)
        print(response)
        if bool(re.match("\"admingroup*.",str(response))):
            print("Group 'asmgroup' created successfully")
            assert True
        else:
            print("Group 'asmgroup' creation unsuccessful")
            assert False




    @pytest.mark.run(order=176)
    def test_176_Configure_AD_server_details_in_the_grid(self):
        print("Configuring AD server details in the grid")
        data={
                "name": "adserver",
                "ad_domain": config.ad_domain,
                "domain_controllers": [
                    {
                        "auth_port": 389,
                        "disabled": False,
                        "fqdn_or_ip": config.ad_ip,
                        "encryption": "NONE",
                        "use_mgmt_port": False
                    }
                ]
            }
        response = ib_NIOS.wapi_request('POST', object_type="ad_auth_service",fields=json.dumps(data),grid_vip=config.grid_mgmt_ip)
        print(response)
        if bool(re.match("\"ad_auth_service*.",str(response))):
            print("AD service configured sucessfully")
            assert True
        else:
            print("AD service configuration failed")
            assert False


    @pytest.mark.run(order=177)
    def test_177_Add__AD_to_the_Authentiation_Policy_list(self):
	print("Fetch Authentication policy ref")
        response = ib_NIOS.wapi_request('GET',object_type='authpolicy',grid_vip=config.grid_mgmt_ip)
        auth_policy_ref = json.loads(response)[0]['_ref']
        print("Authentication Policy ref: "+auth_policy_ref)


        print("Fetch local user ref")
        response = ib_NIOS.wapi_request('GET',object_type='authpolicy?_return_fields=auth_services',grid_vip=config.grid_mgmt_ip)
        local_user_ref = json.loads(response)[0]['auth_services'][0]
        print("Local user ref: "+local_user_ref)

	print("Fetch AD server ref")
        response = ib_NIOS.wapi_request('GET', object_type="ad_auth_service",grid_vip=config.grid_mgmt_ip)
        ad_ref = json.loads(response)[0]['_ref']
        print("AD server ref : "+ad_ref)


        print("Add AD server to the authentiation policy list")
        data={"auth_services":[local_user_ref,ad_ref]}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=auth_policy_ref,grid_vip=config.grid_mgmt_ip)
        print(response)
        if bool(re.match("\"authpolicy*.",str(response))):
            print("AD server added to the authentiation policy list successfully")
            sleep(10)
            assert True
        else:
            print("AD server addition to the authentiation policy list failed")
            assert False




    @pytest.mark.run(order=178)
    def test_178_Assign_remote_users_admin_group_as_superuser(self):
        map_remote_user_to_the_group('asmgroup')
        sleep(5)

    @pytest.mark.run(order=179)
    def test_179_enable_TLSv1_1_as_AD_User(self):
	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+config.ad_username+'@'+config.grid_mgmt_ip)
	child.logfile=sys.stdout
	log("start","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        child.expect("password:")
        child.sendline(config.ad_password)
        child.expect("Infoblox >")
        child.sendline('set ssl_tls_protocols enable TLSv1.1')
        child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSv1.0')
        child.expect('>')
        child.sendline("set ssl_tls_protocols disable TLSv1.2")
        child.expect("Infoblox >")	
        child.sendline("show ssl_tls_protocols")
        child.expect("Infoblox >")
        output = child.before
        #print('output is',output)
        sleep(120)
        log("stop","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        if "Current configuration for the SAML  : TLSv1.1" in output:
		print("Tls protocols set to TLSv1.1")
                logging.info("Tls protocols set to TLSv1.1")
                assert True
        else:
                print("Tls protocols not set to TLSv1.1")
                logging.error("Tls protocols not set to TLSV1.1")
                assert False
	data = ["Restarting saml","TLS PROTOCOL for the SAML is set to PROTOCOL_TLSv1_1"]
        for i in data:
                logs=logv(i,"/infoblox/var/infoblox.log",config.grid_mgmt_ip)
                print("logs are" , logs)
                if logs != None:
                        print("validated enabled TLSv1.1 as AD user in logs")
                        assert True
                else:
                        print("validated TLSv1.1 not enabled as AD user in logs")
                        assert False
	child.sendline('exit')
	child.close()
	sleep(10)


    @pytest.mark.run(order=180)
    def test_180_validate_TLS_protocol_TLSv1_1_active_for_saml_port_with_openssl(self):
	logging.info("validating TLS protocol TLSv1.1 active for saml port")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline("openssl s_client -connect "+config.grid_mgmt_ip+":8765 -tls1_1")
        sleep(5)
        child.sendline('\n')
        child.sendline('\n')
        child.expect('#')
        output = child.before
        print ("output is", output)
	if (("wrong version number" not in output) and ("ssl handshake failure" not in output) and ("Protocol  : TLSv1.1" in output)):
		print("TLS protocols TLSv1.1 is active for saml port")
		logging.info("TLS protocols TLSv1.1 is active for saml port")
                assert True
        else:
                print("TLS protocols TLSv1.1 is not active for saml port")
                logging.error("TLS protocols TLSv1.1 is not active for saml port")
                assert False
	child.close()


    @pytest.mark.run(order=181)
    def test_181_validate_TLS_protocol_TLSv1_1_is_active_for_saml_port_with_testssl_sh_script(self):
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('cd /tmp/testssl.sh-3.0.6')
        child.expect('#')
        child.sendline('/infoblox/one/bin/testssl.sh --protocols --fast --parallel '+config.grid_mgmt_ip+':8765 ')
        sleep(25)
        child.expect('Done')
        output = child.before
        output1 = output.replace("\x1b[m\x1b[1;33m","").replace("\x1b[m\x1b[0;33m","").replace("\x1b[m","").replace("\x1b[1;32m","")
        print("output is",output1)
        if "TLS 1.1    offered" in output1:
                print("validated TLSv1.1 is enabled with testssl.sh script")
                logging.info("validated TLSv1.1 is enabled with testssl.sh script")
                assert True
        else:
                print("validated TLSv1.1 is not enabled with testssl.sh script")
                logging.error("validated TLSv1.1 is not enabled with testssl.sh script")
                assert False
	child.close()


    @pytest.mark.run(order=182)
    def test_182_login_to_CLI_as_SAML_with_superuser(self):
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
        child.sendline(config.okta_username)
        sleep(10)
        child.expect('OKTA SAML password:')
        sleep(5)
        child.sendline(config.okta_password)
        child.expect('Infoblox >')
        child.sendline('show network')
        sleep(20)
        child.expect('Infoblox >')
        c= child.before
        child.sendline('exit')
        child.expect('login:')
        assert re.search(r'.*Current LAN1 Network Settings.*',c)
        logging.info("Test Case  execution completed")

    @pytest.mark.run(order=183)
    def test_183_GRID_BACKUP(self):
        print ("Take Grid Backup")
        data = {"type": "BACKUP"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data),grid_vip=config.grid_mgmt_ip)
        res = json.loads(response)
        URL=res['url']
        print("URL is : %s", URL)
        infoblox_log_validation ='curl -k -u admin:infoblox -H  "content-type: application/force-download" "' + str(URL) +'" -o "database.bak"'
        print ("infoblox.log",infoblox_log_validation)
        out2 = commands.getoutput(infoblox_log_validation)
        print("logs are",out2)
        print ("Backup is Done")
        read  = re.search(r'201',URL)
        for read in  response:
                assert True
        logging.info("Test Case Execution Completed")
        sleep(10)



    @pytest.mark.run(order=184)
    def test_184_enabling_tls_protocols_TLSv1_2(self):
        logging.info("enabling tls protocols TLSv1.2")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        log("start","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set ssl_tls_settings override')
        child.expect('>')
	child.sendline('set ssl_tls_protocols enable TLSv1.2')
        child.expect('>')
	child.sendline('set ssl_tls_protocols disable TLSv1.0')
        child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSv1.1')
        child.expect('>')
        child.sendline('show ssl_tls_protocols')
        child.expect('>')
        output = child.before
        #print ("output is" ,output)
        sleep(120)
        log("stop","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        if "Current configuration for the SAML  : TLSv1.2" in output:
                print("Tls protocols set to TLSv1.2")
                logging.info("Tls protocols set to TLSv1.2")
                assert True
        else:
                print("Tls protocols not set to TLSv1.2")
                logging.info("Tls protocols not set to TLSV1.2")
                assert False
        data = ["Restarting saml","TLS PROTOCOL for the SAML is set to PROTOCOL_TLSv1_2"]
        for i in data:
                print (i)
                logs=logv(i,"/infoblox/var/infoblox.log",config.grid_mgmt_ip)
                print("logs are" , logs)
                if logs != None:
                        print("validated tls protocols set to TLSv1.2 in logs")
                        assert True
                else:
                        print("error")
                        assert False
        child.sendline('exit')
        child.close()
        sleep(10)




    @pytest.mark.run(order=185)
    def test_185_GRID_RESTORE(self):
        logging.info("Grid Restore")
        response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=uploadinit",grid_vip=config.grid_mgmt_ip)
        print response
        res = json.loads(response)
        URL=res['url']
        token1=res['token']
        print("URL is : %s", URL)
        print("Token is %s",token1)
        infoblox_log_validation ='curl -k -u admin:infoblox -H content_type="content-typemultipart-formdata" ' + str(URL) +' -F file=@database.bak'
        print infoblox_log_validation
        out2 = commands.getoutput(infoblox_log_validation)
        print ("out2$$$$$$",out2)
        data2={"mode":"NORMAL","nios_data":True,"token":token1}
        print ("&*&*&*&*&*&*",data2)
        response2 = ib_NIOS.wapi_request('POST', object_type="fileop?_function=restoredatabase",fields=json.dumps(data2),grid_vip=config.grid_mgmt_ip)
        sleep(400)
        logging.info("Validate Syslog afer perform queries")
        infoblox_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str( config.grid_mgmt_ip) + ' " tail -3000 /infoblox/var/infoblox.log "'
        out1 = commands.getoutput(infoblox_log_validation)
        print out1
        logging.info(out1)
        assert re.search(r'restore_node complete',out1)
        sleep(50)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        logging.info("Test Case Execution Completed")




    @pytest.mark.run(order=186)
    def test_186_validating_tls_protocols_TLSv1_1_is_active_after_restore(self):
        logging.info("validating tls protocols TLSv1.1 is active after restore")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip)
        child.logfile=sys.stdout
        log("start","/infoblox/var/infoblox.log",config.grid_mgmt_ip)
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show ssl_tls_protocols')
	child.expect('>')
	output = child.before
	if "Current configuration for the SAML  : TLSv1.1" in output:
		print("Tls protocols set to TLSv1.1")
                logging.info("Tls protocols set to TLSv1.1")
                assert True
        else:
                print("Tls protocols not set to TLSv1.1")
                logging.info("Tls protocols not set to TLSV1.1")
                assert False



    @pytest.mark.run(order=187)
    def test_187_change_lan_settings(self):
        cmd1 = 'whoami'
        cmd_result1 = subprocess.check_output(cmd1, shell=True)
        cmd_result1=cmd_result1.strip('\n')
        print cmd_result1
        #cmd = 'rm -v /home/'+cmd_result1+'/.ssh/known_hosts'
        #cmd_result = subprocess.check_output(cmd, shell=True)
        #print cmd_result
       # os.system("netctl_system -i mgmt -S 10.36.0.0 -a vlanset -H "+config.vm_id)
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_ip6)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set interface mgmt')
        child.expect("Enable Management port\? \(y or n\):",timeout=30)
        child.sendline("y")
        child.expect('Enter Management IP address:')
        child.sendline(config.grid_mgmt_ip6)
        child.expect('\[Default: none\]:')
        child.sendline("64")
        child.expect('\[Default: none\]:')
        child.sendline("2001:0550:040A:2500:0000:0000:0000:0001")
	child.expect("Configure Management IPv4 network settings\? \(y or n\):",timeout=30)
        child.sendline("n")
        child.expect("Restrict Support and remote console access to MGMT port\? \(y or n\):",timeout=30)
        child.sendline("n")
        child.expect("Is this correct\? \(y or n\):",timeout=30)
        child.sendline("y")
        child.expect("Are you sure\? \(y or n\):",timeout=30)
        child.sendline("y")
        child.expect('Infoblox >')
        child.sendline("exit")
	sleep(180)
        c= child.before
        return 1




    @pytest.mark.run(order=188)
    def test_188_enable_super_user_for_saml_group(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup?name=saml-group",grid_vip=config.grid_mgmt_ipv6)
        ref1 = json.loads(get_ref)[0]['_ref']
        print(ref1)
        data = {"superuser":True}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_mgmt_ipv6)
        print(response)
        print(type(response))
        response =  ib_NIOS.wapi_request('GET', object_type="admingroup?name=saml-group&_return_fields%2B=superuser", grid_vip=config.grid_mgmt_ipv6)
        print(response)
        assert re.search(r'"superuser": true',response)


    @pytest.mark.run(order=189)
    def test_189_Configure_SAML_Service_By_Upload(self):
        grid_vip=config.grid_mgmt_ipv6
        print(grid_vip)
        ref=ib_NIOS.wapi_request('GET',object_type='saml:authservice',grid_vip=config.grid_mgmt_ipv6)
        print ("ref is",ref)
        if ref =='[]':
            filename="metadataipv6.xml"
            logging.info("Test Uploading the Template with fileop")
            data = {"filename":filename}
            create_file = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadinit",grid_vip=config.grid_mgmt_ipv6)
            logging.info(create_file)
            res = json.loads(create_file)
            print("create_file is ",create_file)
            token = json.loads(create_file)['token']
            url = json.loads(create_file)['url']
            file1=url.split("/")
            os.system('curl -k1 -u admin:infoblox -F name=%s -F filedata=@%s %s'%(filename,filename,url))
            filename="/"+filename
            data = {"name":"saml","session_timeout":1234,"idp":{"idp_type": "OKTA","metadata_token":token,"sso_redirect_url":config.grid_mgmt_ipv6,"groupname":"groupname"}}
            create_file1 = ib_NIOS.wapi_request('POST', object_type="saml:authservice",fields=json.dumps(data),grid_vip=config.grid_mgmt_ipv6)
            create_file1=json.loads(create_file1)
            if create_file1!="[]":
                assert True
                logging.info(create_file1)
                print("Test case  passed for adding SAML service through file upload")
                logging.info("Test case  passed for adding SAML service through file upload")
                #delete_saml_service(create_file1)
            else:
                assert False
        else:
            ref=json.loads(ref)
            ref2=ref[0]['_ref']
            print(ref2)
            delete_saml_service(ref2)
            filename="metadataipv6.xml"
            logging.info("Test Uploading the Template with fileop")
            data = {"filename":filename}
            create_file = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadinit",grid_vip=config.grid_mgmt_ipv6)
            logging.info(create_file)
            res = json.loads(create_file)
            token = json.loads(create_file)['token']
            url = json.loads(create_file)['url']
            file1=url.split("/")
            os.system('curl -k1 -u admin:infoblox -F name=%s -F filedata=@%s %s'%(filename,filename,url))
            filename="/"+filename
            data = {"name":"saml","session_timeout":1234,"idp":{"idp_type": "OKTA","metadata_token":token,"sso_redirect_url":config.grid_vip6,"groupname":"groupname"}}
            create_file1 = ib_NIOS.wapi_request('POST', object_type="saml:authservice",fields=json.dumps(data),grid_vip=config.grid_mgmt_ipv6)
            print create_file1
            create_file1=json.loads(create_file1)
            if create_file1!="[]":
                logging.info(create_file1)
                logging.info("Test case  passed for adding SAML service through file upload")
                assert True
                #delete_saml_service(create_file1)
            else:
                assert False
            sleep(20)



    @pytest.mark.run(order=190)
    def test_190_enabling_auto_create_user(self):
        data = []
        logging.info("get reference value for GROUP level")
        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup",grid_vip=config.grid_mgmt_ipv6)
	print("ref is",get_ref)
        logging.info(get_ref)
        res = json.loads(get_ref)
        logging.info ("----------------------Groups where conditions will be applied------------------------------------------")
        time.sleep(5)
        for i in res:
            if (i['name'] in ('saml-group')):  # it gets data /reference other than splunk and clou-api
                data.append(i)
        logging.info (data)
	print("i is",i)
        for i in data:
            ref1=i['_ref']
	    print("ref is",ref1)
            #logging.info ("reference value for group is:",ref1)
            data = {"saml_setting":{"auto_create_user":True}}
            response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data),grid_vip=config.grid_mgmt_ipv6)
            time.sleep(5)
            logging.info(response)



    @pytest.mark.run(order=191)
    def test_191_enabling_persist_auto_create_user(self):
        data = []
        logging.info("get reference value for GROUP level")
        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup",grid_vip=config.grid_mgmt_ipv6)
        logging.info(get_ref)
        res = json.loads(get_ref)
        logging.info ("----------------------Groups where conditions will be applied------------------------------------------")
        time.sleep(5)
        for i in res:
		if (i['name'] in ('saml-group')):
                	data.append(i)
        logging.info (data)
        for i in data:
            ref1=i['_ref']
            #logging.info ("reference value for group is:",ref1)
            data = {"saml_setting":{"persist_auto_created_user":True}}
            response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data), grid_vip=config.grid_mgmt_ipv6)
            time.sleep(5)
            logging.info(response)

    @pytest.mark.run(order=192)
    def test_192_validate_all_three_TLS_protocols_are_enabled_for_default_setting(self):
        logging.info("validate all three tls protocols are enabled")
	cmd1 = 'whoami'
	cmd_result1 = subprocess.check_output(cmd1, shell=True)
        cmd_result1=cmd_result1.strip('\n')
        print cmd_result1
        cmd2 = 'rm -f  /home/'+cmd_result1+'/.ssh/known_hosts'
	response1 = subprocess.check_output(cmd2, shell=True)
	print("response is",response1)
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip6)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show ssl_tls_protocols')
        child.expect('>')
        output = child.before
        if "TLSv1.0 TLSv1.1 TLSv1.2" in output:
            print("TLSv1.0,TLSv1.1,TLSv1.2 are active")
            logging.info("TLSv1.0,TLSv1.1,TLSv1.2 are active")
            assert True
        else:
            print("TLSv1.0,TLSv1.1,TLSv1.2 are not active")
            logging.info("TLSv1.0,TLSv1.1,TLSv1.2 are not active")
            assert False
        child.sendline('exit')
        child.close()
        sleep(10)


    @pytest.mark.run(order=193)
    def test_193_enabling_tls_protocols_TLSv1_2_and_disabling_weak_ciphers_for_ipv6_only_grid(self):
	logging.info("enabling tls protocols TLSv1.2")
	child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_mgmt_ip6)
        child.logfile=sys.stdout
	log("start","/infoblox/var/infoblox.log",config.grid_mgmt_ip6)
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('set ssl_tls_settings override')
        child.expect('>')
        child.sendline('set ssl_tls_protocols enable TLSv1.2')
        child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSv1.1')
        child.expect('>')
        child.sendline('set ssl_tls_protocols disable TLSV1.0')
        child.expect('>')
        child.sendline('set ssl_tls_ciphers disable 15')
        child.expect('>')
        child.sendline('show ssl_tls_protocols')
	child.expect('>')
        output = child.before
  	#print ("output is" ,output)
	sleep(130)
	log("stop","/infoblox/var/infoblox.log",config.grid_mgmt_ip6)
        if "Current configuration for the SAML  : TLSv1.2" in output:
		print("Tls protocols set to TLSv1.2")
                logging.info("Tls protocols set to TLSv1.2")
                assert True
        else:
                print("Tls protocols not set to TLSv1.2")
                logging.info("Tls protocols not set to TLSV1.2")
                assert False
	data = ["Restarting saml","TLS PROTOCOL for the SAML is set to PROTOCOL_TLSv1_2"]
	for i in data:
	    	logs=logv(i,"/infoblox/var/infoblox.log",config.grid_mgmt_ip6)
            	print("logs are" , logs)
		if logs != None:
			print("validated tls protocols set to TLSv1.2 in logs")
	 	        assert True
		else:
		 	print("validated tls protocols not set to TLSv1.2 in logs")
			assert False
	child.sendline('exit')
	child.close()
        sleep(20)





    @pytest.mark.run(order=194)
    def test_194_changing_username_and_password(self):
        name = "arunchurimanjunath"
        name1 = '"{}"'.format(name)
        print ("b is",name1)
        data1 = "sed -i -e s/'username.*'/'username="+name1+"'/g config.py"
#       data1 = 'sed -i "s/username=.*/username='+b+'/g" config.py'
        response1 = os.system(data1)
        pwd = "Arun@123"
        pwd1 = '"{}"'.format(pwd)
        data2 = "sed -i -e s/'password.*'/'password="+pwd1+"'/g config.py"
        response2 = os.system(data2)
        print("pass")


    @pytest.mark.run(order=195)
    def test_195_sso_login(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup",grid_vip=config.grid_vip)
        ref = json.loads(get_ref)
        print(ref)
	if ref!="[]":
		print("case passed")
		assert True
	else:
		print("case failed")
		assert False

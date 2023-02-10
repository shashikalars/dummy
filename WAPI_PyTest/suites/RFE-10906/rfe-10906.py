
import urllib3
import os
import re
import requests
import config                                    
import pytest                                    
import unittest                                  
import logging
import pexpect
import sys
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.FileHandler(config.backup_path+'/log.txt', mode="w")
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
requests_log.addHandler(handler)

"""
|----------------------------------------------------------|
|  Author - Chanchal Sutradhar                             |
|  Email - csutradhar@infoblox.com                         |
|  Grid Configuration :-                                   |
|  Grid Master (IB-v815) and Grid Member (IB-v815)         |
|----------------------------------------------------------|

"""
#Getting the member Reference sting

def mem_ref(hostname):
    response = ib_NIOS.wapi_request('GET', object_type="member",grid_vip=config.grid_vip)
    logging.info(response)
    print(response)
    if type(response)!=tuple:
        ref1 = json.loads(response)
        for key in ref1:
            if key.get('host_name') == hostname:
                mem_ref = key.get('_ref')
                break
    else:
        print("Failed to get member DNS ref string")
        mem_ref = "NIL"
    
    return mem_ref
                    
class RFE_10906(unittest.TestCase):
        
        @pytest.mark.run(order=1)

        def test_001_create_an_admin_group_with_grid_admin_role(self):
            logging.info("Create one admin group with Grid admin role")
            data = {"name":"asm1","access_method":["API","CLI","GUI"], "roles":["Grid Admin"]}
            response = ib_NIOS.wapi_request('POST', object_type="admingroup", fields=json.dumps(data),grid_vip=config.grid_vip)
            if type(response)!=tuple:
                sleep(5)
                logging.info("Test Case Passed")
                assert True
            else:
                logging.info("Test Case Failed")
                assert False

        def test_002_validate_the_admin_group(self):
            logging.info("Validate the Admin Group")
            response = ib_NIOS.wapi_request('GET', object_type="admingroup", grid_vip=config.grid_vip)
            val = 0
            if type(response)!=tuple:
                ref1 = json.loads(response)
                for key in ref1:
                    if key.get('name') == "asm1":
                        val = 1
                        break
                if val == 1:
                    logging.info("Test Case Passed")
                    assert True
                else:
                    logging.info("Test Case Failed")
                    assert False
            else:
                logging.info("Test Case Failed")
                assert False

        def test_003_create_non_super_user_on_non_admin_grp(self):
            logging.info("Create non super user on non admin grp")
            data = {"admin_groups":["asm1"], "name":"test", "password":"test123", "auth_type":"LOCAL"}
            response = ib_NIOS.wapi_request('POST', object_type="adminuser", fields=json.dumps(data),grid_vip=config.grid_vip)
            #response = ib_NIOS.wapi_request('POST', object_type="adminuser", fields=json.dumps(data),grid_vip='10.35.161.9')
            if type(response)!=tuple:
                sleep(5)
                logging.info("Test Case Passed")
                assert True
            else:
                logging.info("Test Case Failed")
                assert False
        
        def test_004_validate_the_user(self):
            logging.info("Validate the user")
            response = ib_NIOS.wapi_request('GET', object_type="adminuser", grid_vip=config.grid_vip)
            val = 0
            if type(response)!=tuple:
                ref1 = json.loads(response)
                for key in ref1:
                    if key.get('name') == "test":
                        val = 1
                        break
                if val == 1:
                    logging.info("Test Case Passed")
                    assert True
                else:
                    logging.info("Test Case Failed")
                    assert False
            else:
                logging.info("Test Case Failed")
                assert False

        
        def test_005_configure_tacacsplus(self):
            logging.info("Configure TACACS+ server")
            data = {"name":"chanchal_tacacs", "servers":[{"address":config.tacacs_server,"auth_type":"CHAP","shared_secret":config.tacacs_secrect}]}
            response = ib_NIOS.wapi_request('POST', object_type="tacacsplus:authservice", fields=json.dumps(data),grid_vip=config.grid_vip)
            #response = ib_NIOS.wapi_request('POST', object_type="tacacsplus:authservice", fields=json.dumps(data),grid_vip='10.35.161.9')
            if type(response)!=tuple:
                sleep(5)
                logging.info("Test Case Passed")
                assert True
            else:
                logging.info("Test Case Failed")
                assert False
        
        def test_006_validate_tacacsplus_server(self):
            logging.info("Validate TACACS+ server")
            val = 0
            response = ib_NIOS.wapi_request('GET', object_type="tacacsplus:authservice", grid_vip=config.grid_vip)
            if type(response)!=tuple:
                ref1 = json.loads(response)
                for key in ref1:
                    if key.get('name') == "chanchal_tacacs":
                        val = 1
                        break
                if val == 1:
                    logging.info("Test Case Passed")
                    assert True
                else:
                    logging.info("Test Case Failed")
                    assert False
            else:
                logging.info("Test Case Failed")
                assert False
        
        def test_007_configure_radius(self):
            logging.info("Configure radius server")
            data = {"name":"chanchal_radius", "servers":[{"address":config.radius_server,"auth_type":"PAP","shared_secret":config.radius_secrect}]}
            response = ib_NIOS.wapi_request('POST', object_type="radius:authservice", fields=json.dumps(data),grid_vip=config.grid_vip)
            if type(response)!=tuple:
                sleep(5)
                logging.info("Test Case Passed")
                assert True
            else:
                logging.info("Test Case Failed")
                assert False
        
        def test_008_validate_radius_server(self):
            logging.info("Validate radius server")
            val = 0
            response = ib_NIOS.wapi_request('GET', object_type="radius:authservice", grid_vip=config.grid_vip)
            if type(response)!=tuple:
                ref1 = json.loads(response)
                for key in ref1:
                    if key.get('name') == "chanchal_radius":
                        val = 1
                        break
                if val == 1:
                    logging.info("Test Case Passed")
                    assert True
                else:
                    logging.info("Test Case Failed")
                    assert False
            else:
                logging.info("Test Case Failed")
                assert False
        
        def test_009_configure_ad_server(self):
            logging.info("Configure ad server")
            data = {"name":"chanchal_ad", "domain_controllers":[{"fqdn_or_ip":config.ad_server, "auth_port":389, "encryption": "NONE"}], "ad_domain":config.ad_domain}
            response = ib_NIOS.wapi_request('POST', object_type="ad_auth_service", fields=json.dumps(data),grid_vip=config.grid_vip)
            if type(response)!=tuple:
                sleep(5)
                logging.info("Test Case Passed")
                assert True
            else:
                logging.info("Test Case Failed")
                assert False
        
        def test_010_validate_ad_server(self):
            logging.info("Validate ad server")
            val = 0
            response = ib_NIOS.wapi_request('GET', object_type="ad_auth_service", grid_vip=config.grid_vip)
            if type(response)!=tuple:
                ref1 = json.loads(response)
                for key in ref1:
                    if key.get('name') == "chanchal_ad":
                        val = 1
                        break
                if val == 1:
                    logging.info("Test Case Passed")
                    assert True
                else:
                    logging.info("Test Case Failed")
                    assert False
            else:
                logging.info("Test Case Failed")
                assert False

        def test_011_adding_third_party_servers_to_authentication_policy(self):
            logging.info("Adding third party servers to authentication policies")
            response = ib_NIOS.wapi_request('GET', object_type="ad_auth_service", grid_vip=config.grid_vip)
            if type(response)!=tuple:
                ref1_ad = json.loads(response)[0].get('_ref')
            else:
                logging.info("Test Case Failed")
                assert False
            response = ib_NIOS.wapi_request('GET', object_type="radius:authservice", grid_vip=config.grid_vip)
            if type(response)!=tuple:
                ref1_radius = json.loads(response)[0].get('_ref')
            else:
                logging.info("Test Case Failed")
                assert False
            response = ib_NIOS.wapi_request('GET', object_type="tacacsplus:authservice", grid_vip=config.grid_vip)
            if type(response)!=tuple:
                ref1_tacacs = json.loads(response)[0].get('_ref')
            else:
                logging.info("Test Case Failed")
                assert False
            response = ib_NIOS.wapi_request('GET', object_type="authpolicy?_return_fields=auth_services", grid_vip=config.grid_vip)
            if type(response)!=tuple:
                ref1_local = json.loads(response)[0].get('auth_services')[0]
                ref1 = json.loads(response)[0].get('_ref')
            else:
                logging.info("Test Case Failed")
                assert False
            data = {"default_group": "asm1", "auth_services": [ref1_local,ref1_radius,ref1_tacacs,ref1_ad]}
            response = ib_NIOS.wapi_request('PUT', object_type=ref1, fields=json.dumps(data),grid_vip=config.grid_vip)
            print(response)
            if type(response)!=tuple:
                sleep(5)
                logging.info("Test Case Passed")
                assert True
            else:
                logging.info("Test Case Failed")
                assert False

        def test_012_enable_keepalive_on_gm_with_non_super_user(self):
            logging.info("Enable Keepalive on GM with non super user")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no test@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('test123')
            child.expect('Infoblox >')
            child.sendline('set httpd_client keepalive on')
            try:
                child.expect('The user does not have sufficient privileges to run this command')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(50)
                child.close()
                logging.info("Test case Successfull")
                assert True
            except:
                child.expect('Infoblox >')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(120)
                child.close()
                logging.info("Test case Failed")
                assert False
        
        def test_013_enable_keepalive_on_gm_with_ad_user(self):
            logging.info("Enable Keepalive on GM with ad user")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+config.ad_user+'@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline(config.ad_password)
            child.expect('Infoblox >')
            child.sendline('set httpd_client keepalive on')
            try:
                child.expect('The user does not have sufficient privileges to run this command')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(50)
                child.close()
                logging.info("Test case Successfull")
                assert True
            except:
                child.expect('Infoblox >')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(120)
                child.close()
                logging.info("Test case Failed")
                assert False

        def test_014_enable_keepalive_on_gm_with_tacacs_user(self):
            logging.info("Enable Keepalive on GM with tacacs user")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+config.tacacs_user+'@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline(config.tacacs_password)
            child.expect('Infoblox >')
            child.sendline('set httpd_client keepalive on')
            try:
                child.expect('The user does not have sufficient privileges to run this command')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(50)
                child.close()
                logging.info("Test case Successfull")
                assert True
            except:
                child.expect('Infoblox >')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(120)
                child.close()
                logging.info("Test case Failed")
                assert False
        
        def test_015_enable_keepalive_on_gm_with_radius_user(self):
            logging.info("Enable Keepalive on GM with radius user")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+config.radius_user+'@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline(config.radius_password)
            child.expect('Infoblox >')
            child.sendline('set httpd_client keepalive on')
            try:
                child.expect('The user does not have sufficient privileges to run this command')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(50)
                child.close()
                logging.info("Test case Successfull")
                assert True
            except:
                child.expect('Infoblox >')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(120)
                child.close()
                logging.info("Test case Failed")
                assert False
                
        def test_016_enable_keepalive_on_gm_with_super_user(self):
            logging.info("Enable Keepalive on GM")
            log("start","/infoblox/var/audit.log",config.grid_vip)
            log("start","/infoblox/var/infoblox.log",config.grid_vip)
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set httpd_client keepalive on')
            try:
                child.expect('Infoblox >')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(120)
                child.close()
                logging.info("Test case Successfull")
                assert True
            except:
                child.expect('This setting may only be changed on Master or Master candidate.')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(120)
                child.close()
                logging.info("Test case Failed")
                assert False

        def test_017_validate_audit_logs_on_gm(self):
            logging.info("Validate the output on GM")
            log("stop","/infoblox/var/audit.log",config.grid_vip)
            sleep(3)
            LookForAudit="set_httpd_client: keepalive=on keepalivetime=150"
            logaudit = logv(LookForAudit,"/infoblox/var/audit.log",config.grid_master_vip)
            if logaudit!=None:
                logging.info("Test Case Execution Completed")
                assert True
            else:
                logging.info("Test Case Execution Failed")
                assert False
        
        def test_018_validate_infoblox_logs_on_gm_to_check_apache_restart(self):
            logging.info("Validate the infoblox.log to check apache restart on GM")
            log("stop","/infoblox/var/infoblox.log",config.grid_vip)
            sleep(3)
            LookFordebug="Restarting Apache"
            logaudit = logv(LookFordebug,"/infoblox/var/infoblox.log",config.grid_master_vip)
            if logaudit!=None:
                logging.info("Test Case Execution Completed")
                assert True
            else:
                logging.info("Test Case Execution Failed")
                assert False

        def test_019_check_show_httpd_client_output_on_gm(self):
            logging.info("Validate the output on GM")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('show httpd_client')
            try:
                child.expect('keepalive=on')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(50)
                child.close()
                logging.info("Test case Successfull")
                assert True
            except:
                child.expect('No user settings')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(20)
                child.close()
                logging.info("Test case Failed")
                assert False

        def test_020_enable_keepalivetime_on_gm(self):
            logging.info("Configure keepalivetime to 5 sec")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set httpd_client keepalivetime 5')
            try:
                child.expect('Infoblox >')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(50)
                child.close()
                logging.info("Test case Successfull")
                assert True
            except:
                child.expect('This setting may only be changed on Master or Master candidate.')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(20)
                child.close()
                logging.info("Test case Failed")
                assert False

        def test_021_validate_the_show_httpd_client_output_on_gm_for_keepalivetime(self):
            logging.info("Validate the output on GM for keepalivetime")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('show httpd_client')
            try:
                child.expect('keepalivetime=5')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(50)
                child.close()
                logging.info("Test case Successfull")
                assert True
            except:
                child.expect('No user settings')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(20)
                child.close()
                logging.info("Test case Failed")
                assert False

        def test_022_check_keepalivetime_with_an_ipv4_api_call_on_gm(self):
            logging.info("Validate keepalivetime with v4 API Call")
            path = config.backup_path+"/log.txt"
            try:
                s = requests.session()
                s.verify = False
                url1 = 'https://'+config.grid_vip+'/wapi/v'+config.wapi_version+'/grid'
                s.get(url1, auth=('admin','infoblox'))
                s.get(url1)
                sleep(6)
                s.get(url1)
                fi = open(path, "rb").read()
                print(fi)
                s.close()
                if "Resetting dropped connection" in fi:
                    logging.info("Test case Successfull")
                    assert True                        
                else:
                    logging.info("Test case Failed")
                    assert False
            except requests.exceptions.RequestException as e:
                print(e)
                logging.info("Test case Failed")
                assert False
        
        def test_023_check_keepalivetime_with_an_ipv6_api_call_on_gm(self):
            logging.info("Validate keepalivetime with v6 API Call")
            path = config.backup_path+"/log.txt"
            try:
                s = requests.session()
                s.verify = False
                url1 = 'https://['+config.mas_lan_v6+']/wapi/v'+config.wapi_version+'/grid'
                s.get(url1, auth=('admin','infoblox'))
                s.get(url1)
                sleep(6)
                s.get(url1)
                fi = open(path, "rb").read()
                print(fi)
                s.close()
                if "Resetting dropped connection" in fi:
                    logging.info("Test case Successfull")
                    assert True                        
                else:
                    logging.info("Test case Failed")
                    assert False
            except requests.exceptions.RequestException as e:
                print(e)
                logging.info("Test case Failed")
                assert False

        def test_024_set_keepalivetime_to_incorrect_values_on_gm(self):

            logging.info("Confiuring incorrect values on GM")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set httpd_client keepalivetime -99')
            try:
                child.expect('Incorrect value')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(50)
                child.close()
                logging.info("Test case Successfull")
                assert True
            except:
                child.expect('Infoblox >')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(20)
                child.close()
                logging.info("Test case Failed")
                assert False
            
        def test_025_set_only_keepalivetime_to_default_values_on_gm(self):

            logging.info("Confiuring keepalive to default values on GM")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set httpd_client keepalivetime -1')
            try:
                child.expect('keepalivetime=5')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(50)
                child.close()
                logging.info("Test case Failed")
                assert False
            except:
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(50)
                child.close()
                logging.info("Test case Passed")
                assert True

        def test_026_test_the_lower_limit_of_keepalivetime_values_on_gm(self):
            logging.info("Test the lower limit of keepalive")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set httpd_client keepalivetime 0')
            try:
                child.expect('Infoblox >')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(50)
                child.close()
                logging.info("Test case Successfull")
                assert True
            except:
                child.expect('Incorrect value')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(20)
                child.close()
                logging.info("Test case Failed")
                assert False

        def test_027_test_the_upper_limit_of_keepalivetime_values_on_gm(self):
            logging.info("Test the higher limit of keepalive")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set httpd_client keepalivetime 99999')
            try:
                child.expect('Infoblox >')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(50)
                child.close()
                logging.info("Test case Successfull")
                assert True
            except:
                child.expect('Incorrect value')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(20)
                child.close()
                logging.info("Test case Failed")
                assert False

        def test_028_enable_maxkeepaliverequests_on_gm(self):
            logging.info("Enable maxkeepaliverequests")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set httpd_client maxkeepaliverequests 5')
            try:
                child.expect('Infoblox >')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(50)
                child.close()
                logging.info("Test case Successfull")
                assert True
            except:
                child.expect('Incorrect value')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(20)
                child.close()
                logging.info("Test case Failed")
                assert False

        def test_029_validate_the_show_httpd_client_output_on_gm_for_maxkeepaliverequests(self):
            logging.info("Validate the output on GM for maxkeepaliverequests")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('show httpd_client')
            try:
                child.expect('maxkeepaliverequests=5')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(50)
                child.close()
                logging.info("Test case Successfull")
                assert True
            except:
                child.expect('No user settings')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(20)
                child.close()
                logging.info("Test case Failed")
                assert False

        def test_030_check_maxkeepaliverequests_with_a_api_call_on_gm(self):
            logging.info("Validate maxkeepaliverequests with v4 API Call")
            sleep(5)
            path = config.backup_path+"/log.txt"
            try:
                s = requests.session()
                s.verify = False
                url1 = 'https://'+config.grid_vip+'/wapi/v'+config.wapi_version+'/grid'
                s.get(url1, auth=('admin','infoblox'))
                for i in range(1,7):
                    s.get(url1)
                fi = open(path, "rb").read()
                s.close()
                if "Resetting dropped connection" in fi:
                    logging.info("Test case Successfull")
                    assert True                        
                else:
                    logging.info("Test case Failed")
                    assert False    

            except requests.exceptions.RequestException as e:
                print(e)
                logging.info("Test case Failed")
                assert False

        def test_031_check_maxkeepaliverequests_with_an_ipv6_api_call_on_gm(self):
            logging.info("Validate maxkeepaliverequests with v6 API Call")
            sleep(5)
            path = config.backup_path+"/log.txt"
            try:
                s = requests.session()
                s.verify = False
                url1 = 'https://['+config.mas_lan_v6+']/wapi/v'+config.wapi_version+'/grid'
                s.get(url1, auth=('admin','infoblox'))
                for i in range(1,7):
                    s.get(url1)
                fi = open(path, "rb").read()
                s.close()
                if "Resetting dropped connection" in fi:
                    logging.info("Test case Successfull")
                    assert True                        
                else:
                    logging.info("Test case Failed")
                    assert False    
                    
            except requests.exceptions.RequestException as e:
                print(e)
                logging.info("Test case Failed")
                assert False

        def test_032_set_only_maxkeepaliverequests_to_default_values_on_gm(self):

            logging.info("Confiuring incorrect values on GM")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set httpd_client maxkeepaliverequests -1')
            try:
                child.expect('maxkeepaliverequests=5')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(20)
                child.close()
                logging.info("Test case Successfull")
                assert False
            except:
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(50)
                child.close()
                logging.info("Test case Passed")
                assert True

        def test_033_set_maxkeepaliverequests_to_incorrect_values_on_gm(self):
            logging.info("Confiuring incorrect values on GM")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set httpd_client maxkeepaliverequests -99')
            try:
                child.expect('Incorrect value')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(50)
                child.close()
                logging.info("Test case Successfull")
                assert True
            except:
                child.expect('Infoblox >')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(20)
                child.close()
                logging.info("Test case Failed")
                assert False

        def test_034_test_the_lower_limit_of_maxkeepaliverequests_values_on_gm(self):
            logging.info("Test the lower limit of maxkeepaliverequests")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set httpd_client maxkeepaliverequests 0')
            try:
                child.expect('Infoblox >')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(50)
                child.close()
                logging.info("Test case Successfull")
                assert True
            except:
                child.expect('Incorrect value')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(20)
                child.close()
                logging.info("Test case Failed")
                assert False

        def test_035_test_the_upper_limit_of_maxkeepaliverequests_values_on_gm(self):
            logging.info("Test the Upper limit of maxkeepaliverequests")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set httpd_client maxkeepaliverequests 99999')
            try:
                child.expect('Infoblox >')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(50)
                child.close()
                logging.info("Test case Successfull")
                assert True
            except:
                child.expect('Incorrect value')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(20)
                child.close()
                logging.info("Test case Failed")
                assert False

        def test_036_check_the_configured_values_in_tmpfs_one_httpd_conf_file_on_gm(self):
            logging.info("Validate one_httpd.conf file")
            sleep(120)
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('-bash-5.0#')
            child.sendline('cat /tmpfs/one-httpd.conf')
            try:
                child.expect('KeepAlive On')
                child.expect('MaxKeepAliveRequests 99999')
                child.expect('KeepAliveTimeout 99999')
                child.expect('-bash-5.0#')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(50)
                child.close()
                print("Test case Successfull")
                assert True
            except:
                child.expect('-bash-5.0#')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(20)
                child.close()
                print("Test case Failed")
                assert False

        def test_037_set_the_keepalivetime_and_maxkeepaliverequests_to_default_values_on_gm(self):
            logging.info("Test the default value of maxkeepaliverequests")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set httpd_client default')
            try:
                child.expect('Infoblox >')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(50)
                child.close()
                logging.info("Test case Successfull")
                assert True
            except:
                child.expect('Incorrect value')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(20)
                child.close()
                logging.info("Test case Failed")
                assert False

        def test_038_check_the_default_values_in_tmpfs_one_httpd_conf_file_on_gm(self):
            logging.info("Validate one_httpd.conf file")
            sleep(120)
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('-bash-5.0#')
            child.sendline('cat /tmpfs/one-httpd.conf')
            try:
                child.expect('KeepAlive Off')
                child.expect('MaxKeepAliveRequests 0')
                child.expect('KeepAliveTimeout 150')
                child.expect('-bash-5.0#')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(50)
                child.close()
                logging.info("Test case Passed")
                assert True
            except:
                child.expect('-bash-5.0#')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(20)
                child.close()
                logging.info("Test case Failed")
                assert False

        def test_039_test_if_we_can_enable_keepalive_on_member(self):
            logging.info("Enable Keepalive on member")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set httpd_client keepalive on')
            try:
                child.expect('On current Grid Member all settings may be changed only to the default value')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(50)
                child.close()
                logging.info("Test case Passed")
                assert True
            except:
                child.expect('Infoblox >')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(20)
                child.close()
                logging.info("Test case Failed")
                assert False


        def test_040_configure_the_member_as_gmc_with_read_only_api(self):
            logging.info("Configure a Grid Member as a Grid member Candidate with read only api")
            data = {"master_candidate":True, "enable_ro_api_access": True}
            mem_ref_str = mem_ref(config.grid_member1_fqdn)
            if mem_ref_str == "NIL":
                logging.info("Test Case Failed")
                assert False
            else:
                response = ib_NIOS.wapi_request('PUT', object_type=mem_ref_str, fields=json.dumps(data),grid_vip=config.grid_vip)
                if type(response)!=tuple:
                    sleep(120)
                    logging.info("Test Case Passed")
                    assert True
                else:
                    logging.info("Test Case Failed")
                    assert False
        
        def test_041_validate_gmc(self):
            logging.info("Validate GMC status")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('show status')
            try:
                child.expect('Master Candidate: true')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(50)
                child.close()
                logging.info("Test case Passed")
                assert True
            except:
                child.expect('Infoblox >')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(20)
                child.close()
                logging.info("Test case Failed")
                assert False

        def test_042_enable_kepalilve_on_gmc_with_keepalivetime_maxkeepaliverequests(self):
            logging.info("Enable Keepalive on GMC with keepalivetime and maxkeepaliverequests")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set httpd_client keepalive on keepalivetime 5 maxkeepaliverequests 5')
            try:
                child.expect('Infoblox >')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(50)
                child.close()
                logging.info("Test case Successfull")
                assert True
            except:
                child.expect('This setting may only be changed on Master or Master candidate.')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(20)
                child.close()
                logging.info("Test case Failed")
                assert False

        def test_043_validate_keepalivetime_and_maxkeepaliverequests_from_cli_of_gmc(self):
            logging.info("Validate Keepalive on GMC from the CLI")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            #child.sendline('show httpd_client')
            try:
                #child.expect('keepalive=off (default) keepalivetime=5 minspare=5 (default) maxspare=5 (default) maxserver=150 (default) maxrequest=100 (default) maxkeepaliverequests=5')
                child.sendline('show httpd_client')
                child.expect('Infoblox >')
                output=child.before
                if "keepalive=off (default) keepalivetime=5 minspare=5 (default) maxspare=5 (default) maxserver=150 (default) maxrequest=100 (default) maxkeepaliverequests=5" in output:
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    sleep(50)
                    child.close()
                    logging.info("Test case Successfull")
                    assert True
            except:
                child.expect('No user settings')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(20)
                child.close()
                logging.info("Test case Failed")
                assert False
       
        def test_044_check_maxkeepaliverequests_with_a_api_call_on_gmc(self):
            logging.info("Validate maxkeepaliverequests with v4 API Call on GMC")
            path = config.backup_path+"/log.txt"
            try:
                s = requests.session()
                s.verify = False
                url1 = 'https://'+config.grid_member1_vip+'/wapi/v'+config.wapi_version+'/grid'
                s.get(url1, auth=('admin','infoblox'))
                for i in range(1,7):
                    s.get(url1)
                fi = open(path, "rb").read()
                s.close()
                if "Resetting dropped connection" in fi:
                    logging.info("Test case Successfull")
                    sleep(5)
                    assert True                        
                else:
                    logging.info("Test case Failed")
                    assert False    

            except requests.exceptions.RequestException as e:
                print(e)
                logging.info("Test case Failed")
                assert False

        def test_045_check_maxkeepaliverequests_with_an_ipv6_api_call_on_gmc(self):
            logging.info("Validate maxkeepaliverequests with v6 API Call on gmc")
            path = config.backup_path+"/log.txt"
            try:
                s = requests.session()
                s.verify = False
                url1 = 'https://['+config.mem_lan_v6+']/wapi/v'+config.wapi_version+'/grid'
                s.get(url1, auth=('admin','infoblox'))
                for i in range(1,7):
                    s.get(url1)
                fi = open(path, "rb").read()
                s.close()
                if "Resetting dropped connection" in fi:
                    logging.info("Test case Successfull")
                    sleep(5)
                    assert True                        
                else:
                    logging.info("Test case Failed")
                    assert False    

            except requests.exceptions.RequestException as e:
                print(e)
                logging.info("Test case Failed")
                assert False

        def test_046_check_keepalivetime_with_an_ipv4_api_call_on_gmc(self):
            logging.info("Validate keepalivetime with v4 API Call on GMC")
            path = config.backup_path+"/log.txt"
            try:
                s = requests.session()
                s.verify = False
                url1 = 'https://'+config.grid_member1_vip+'/wapi/v'+config.wapi_version+'/grid'
                s.get(url1, auth=('admin','infoblox'))
                s.get(url1)
                sleep(6)
                s.get(url1)
                fi = open(path, "rb").read()
                s.close()
                if "Resetting dropped connection" in fi:
                    logging.info("Test case Successfull")
                    assert True                        
                else:
                    logging.info("Test case Failed")
                    assert False
            except requests.exceptions.RequestException as e:
                print(e)
                logging.info("Test case Failed")
                assert False
        
        def test_047_check_keepalivetime_with_an_ipv6_api_call_on_gmc(self):
            logging.info("Validate keepalivetime with v6 API Call on gmc")
            path = config.backup_path+"/log.txt"
            try:
                s = requests.session()
                s.verify = False
                url1 = 'https://['+config.mem_lan_v6+']/wapi/v'+config.wapi_version+'/grid'
                s.get(url1, auth=('admin','infoblox'))
                s.get(url1)
                sleep(6)
                s.get(url1)
                fi = open(path, "rb").read()
                s.close()
                if "Resetting dropped connection" in fi:
                    logging.info("Test case Successfull")
                    assert True                        
                else:
                    logging.info("Test case Failed")
                    assert False
            except requests.exceptions.RequestException as e:
                print(e)
                logging.info("Test case Failed")
                assert False
        
        def test_048_promote_gmc_to_gm(self):
            logging.info("Promote the Grid Master Candidate as Grid Master")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set promote_master')
            try:
                child.expect('Do you want a delay between notification to grid members')
                child.sendline('y')
                child.expect('Set delay time for notification to grid member')
                child.sendline('1')
                child.expect('Are you sure you want to do this')
                child.sendline('y')
                child.expect('Are you really sure you want to do this')
                child.sendline('y')
                child.expect('Master promotion beginning on this member')
                sleep(120)
                child.close()
                logging.info("Test case Successfull")
                assert True
            except:
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(20)
                child.close()
                logging.info("Test case Failed")
                assert False
            
        def test_049_validate_gmc_promotion(self):
            logging.info("Validate GMC promotion")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('show status')
            try:
                child.expect('Grid Status: ID Grid Master')
                child.sendline('exit')
                sleep(50)
                child.close()
                logging.info("Test case Successfull")
                assert True
            except:
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(20)
                child.close()
                logging.info("Test case Failed")
                assert False
        
        def test_050_check_httpd_client_CLI_output_of_promoted_gm(self):
            logging.info("Check httpd_client CLI output of promoted GM")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            #child.sendline('show httpd_client')
            try:
                #child.expect('keepalive=off (default) keepalivetime=5 minspare=5 (default) maxspare=5 (default) maxserver=150 (default) maxrequest=100 (default) maxkeepaliverequests=5')
                child.sendline('show httpd_client')
                child.expect('Infoblox >')
                output=child.before
                if "keepalive=off (default) keepalivetime=5 minspare=5 (default) maxspare=5 (default) maxserver=150 (default) maxrequest=100 (default) maxkeepaliverequests=5" in output:
                    child.sendline('exit')
                    sleep(50)
                    child.close()
                    logging.info("Test case Successfull")
                    assert True
            except:
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(20)
                child.close()
                logging.info("Test case Failed")
                assert False
        
        def test_051_check_the_configured_values_in_tmpfs_one_httpd_conf_file_on_promoted_gm(self):
            logging.info("Validate one_httpd.conf file")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('-bash-5.0#')
            child.sendline('cat /tmpfs/one-httpd.conf')
            try:
                child.expect('KeepAlive On')
                child.expect('MaxKeepAliveRequests 5')
                child.expect('KeepAliveTimeout 5')
                child.expect('-bash-5.0#')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(50)
                child.close()
                print("Test case Successfull")
                assert True
            except:
                child.expect('-bash-5.0#')
                child.sendline('exit')
                child.expect(pexpect.EOF)
                sleep(20)
                child.close()
                print("Test case Failed")
                assert False

        def test_052_check_maxkeepaliverequests_with_a_api_call_on_promoted_gm(self):
            logging.info("Validate maxkeepaliverequests with v4 API Call on promoted GM")
            path = config.backup_path+"/log.txt"
            try:
                s = requests.session()
                s.verify = False
                url1 = 'https://'+config.grid_member1_vip+'/wapi/v'+config.wapi_version+'/grid'
                s.get(url1, auth=('admin','infoblox'))
                for i in range(1,7):
                    s.get(url1)
                fi = open(path, "rb").read()
                s.close()
                if "Resetting dropped connection" in fi:
                    logging.info("Test case Successfull")
                    sleep(5)
                    assert True                        
                else:
                    logging.info("Test case Failed")
                    assert False    

            except requests.exceptions.RequestException as e:
                print(e)
                logging.info("Test case Failed")
                assert False

        def test_053_check_maxkeepaliverequests_with_an_ipv6_api_call_on_promoted_gm(self):
            logging.info("Validate maxkeepaliverequests with v6 API Call on promoted gm")
            path = config.backup_path+"/log.txt"
            try:
                s = requests.session()
                s.verify = False
                url1 = 'https://['+config.mem_lan_v6+']/wapi/v'+config.wapi_version+'/grid'
                s.get(url1, auth=('admin','infoblox'))
                for i in range(1,7):
                    s.get(url1)
                fi = open(path, "rb").read()
                s.close()
                if "Resetting dropped connection" in fi:
                    logging.info("Test case Successfull")
                    sleep(5)
                    assert True                        
                else:
                    logging.info("Test case Failed")
                    assert False    

            except requests.exceptions.RequestException as e:
                print(e)
                logging.info("Test case Failed")
                assert False

        def test_054_check_keepalivetime_with_an_ipv4_api_call_on_promoted_gm(self):
            logging.info("Validate keepalivetime with v4 API Call on promoted GM")
            path = config.backup_path+"/log.txt"
            try:
                s = requests.session()
                s.verify = False
                url1 = 'https://'+config.grid_member1_vip+'/wapi/v'+config.wapi_version+'/grid'
                s.get(url1, auth=('admin','infoblox'))
                s.get(url1)
                sleep(6)
                s.get(url1)
                fi = open(path, "rb").read()
                s.close()
                if "Resetting dropped connection" in fi:
                    logging.info("Test case Successfull")
                    sleep(5)
                    assert True                        
                else:
                    logging.info("Test case Failed")
                    assert False
            except requests.exceptions.RequestException as e:
                print(e)
                logging.info("Test case Failed")
                assert False
        
        def test_055_check_keepalivetime_with_an_ipv6_api_call_on_promoted_gm(self):
            logging.info("Validate keepalivetime with v6 API Call on promoted gm")
            path = config.backup_path+"/log.txt"
            try:
                s = requests.session()
                s.verify = False
                url1 = 'https://['+config.mem_lan_v6+']/wapi/v'+config.wapi_version+'/grid'
                s.get(url1, auth=('admin','infoblox'))
                s.get(url1)
                sleep(6)
                s.get(url1)
                fi = open(path, "rb").read()
                s.close()
                if "Resetting dropped connection" in fi:
                    logging.info("Test case Successfull")
                    sleep(5)
                    assert True                        
                else:
                    logging.info("Test case Failed")
                    assert False
            except requests.exceptions.RequestException as e:
                print(e)
                logging.info("Test case Failed")
                assert False
        
        def test_056_install_CNA_license_on_promoted_gm(self):
            logging.info("Install CNA license on promoted GM")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            f = open(config.backup_path + "/mylogdca.txt", "wb")
            path = config.backup_path + "/mylogdca.txt"
            child.logfile=open(path,'wb')
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set temp_license')
            try:
                child.expect('Select license')
                fi = open(path, "rb").read()
                for i in fi.splitlines():
                    if "Cloud Network Automation license" in i:
                        a=re.sub('[^0-9]', '', i)
                child.sendline(a)
                child.expect('Are you sure you want to do this')
                child.sendline('y')
                child.expect('Cloud Network Automation temporary license installed.')
                sleep(50)
                child.close()
                os.remove(path)
                logging.info("Test case Successfull")
                assert True
            except:
                child.sendline('exit')
                sleep(20)
                child.close()
                logging.info("Test case Failed")
                assert False

        def test_057_validate_CNA_License_on_promoted_gm(self):
            logging.info("Valiadate CNA license on promoted GM")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('show license')
            try:
                child.expect('Cloud Network Automation')
                child.sendline('exit')
                sleep(50)
                child.close()
                logging.info("Test case Successfull")
                assert True
            except:
                child.sendline('exit')
                sleep(20)
                child.close()
                logging.info("Test case Failed")
                assert False

        def test_058_check_keepalivetime_with_an_ipv4_api_call_on_promoted_gm(self):
            logging.info("Validate keepalivetime with v4 API Call on promoted GM")
            path = config.backup_path+"/log.txt"
            try:
                s = requests.session()
                s.verify = False
                url1 = 'https://'+config.grid_member1_vip+'/wapi/v'+config.wapi_version+'/grid'
                s.get(url1, auth=('admin','infoblox'))
                s.get(url1)
                sleep(6)
                s.get(url1)
                fi = open(path, "rb").read()
                s.close()
                if "Resetting dropped connection" in fi:
                    logging.info("Test case Successfull")
                    sleep(5)
                    assert True                        
                else:
                    logging.info("Test case Failed")
                    assert False
            except requests.exceptions.RequestException as e:
                print(e)
                logging.info("Test case Failed")
                assert False
        
        def test_059_check_keepalivetime_with_an_ipv6_api_call_on_promoted_gm(self):
            logging.info("Validate keepalivetime with v6 API Call on promoted gm")
            path = config.backup_path+"/log.txt"
            try:
                s = requests.session()
                s.verify = False
                url1 = 'https://['+config.mem_lan_v6+']/wapi/v'+config.wapi_version+'/grid'
                s.get(url1, auth=('admin','infoblox'))
                s.get(url1)
                sleep(6)
                s.get(url1)
                fi = open(path, "rb").read()
                s.close()
                if "Resetting dropped connection" in fi:
                    logging.info("Test case Successfull")
                    sleep(5)
                    assert True                        
                else:
                    logging.info("Test case Failed")
                    assert False
            except requests.exceptions.RequestException as e:
                print(e)
                logging.info("Test case Failed")
                assert False

        def test_060_disable_keepalive_on_promoted_gm(self):
            logging.info("Disable keepalive on promoted GM")
            log("start","/infoblox/var/audit.log",config.grid_member1_vip)
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('set httpd_client keepalive off')
            try:
                child.expect('Infoblox >')
                child.sendline('exit')
                sleep(50)
                child.close()
                logging.info("Test case Successfull")
                assert True
            except:
                child.expect('This setting may only be changed on Master or Master candidate.')
                child.sendline('exit')
                sleep(20)
                child.close()
                logging.info("Test case Failed")
                assert False

        def test_061_validate_audit_logs_on_promoted_gm(self):
            logging.info("Validate the audit log output on GM")
            log("stop","/infoblox/var/audit.log",config.grid_member1_vip)
            LookForAudit="keepalive=off"
            logaudit = logv(LookForAudit,"/infoblox/var/audit.log",config.grid_member1_vip)
            if logaudit!=None:
                logging.info("Test Case Execution Completed")
                assert True
            else:
                logging.info("Test Case Execution Failed")
                assert False

        def test_062_validate_keepalive_status_on_promoted_gm_from_the_cli(self):
            logging.info("validate keepalive status on promoted GM from the cli")
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('show httpd_client')
            try:
                child.expect('keepalive=off')
                child.sendline('exit')
                sleep(50)
                child.close()
                logging.info("Test case Successfull")
                assert True
            except:
                child.sendline('exit')
                sleep(20)
                child.close()
                logging.info("Test case Failed")
                assert False

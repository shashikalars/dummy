import os
import re
import config
import pytest
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import paramiko
import commands
import pexpect
import sys

def start_HTTP_services(obj_index,IP,which_mem):
    log("start","/infoblox/var/infoblox.log",IP)
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:filedistribution")
    
    ref=json.loads(get_ref)[obj_index]['_ref']
    print(ref)
    data = {"enable_http": True}
    response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))

    print(response)
    if type(response) == tuple:
        if response[0]==200:
            print("\n Success: Start HTTP service on "+which_mem)
            assert True
        else:
            print("\n Failure: did not Start HTTP service on "+which_mem)
            assert False
    sleep(30)           
    log("stop","/infoblox/var/infoblox.log",IP)

    
def stop_HTTP_services(obj_index,IP,which_mem):
    log("start","/infoblox/var/infoblox.log",IP)
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:filedistribution")
    
    ref=json.loads(get_ref)[obj_index]['_ref']
    print(ref)
    data = {"enable_http": False}
    response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
    print(response)
    if type(response) == tuple:
        if response[0]==200:
            print("\n Success: Stop HTTP service on "+which_mem)
            assert True
        else:
            print("\n Failure: did not Stop HTTP service on "+which_mem)
            assert False
    sleep(20)           
    log("stop","/infoblox/var/infoblox.log",IP)

def grep_HTTPd_and_validate_PID(IP):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(IP, username='root', pkey = mykey)
    sleep(2)
    data="pgrep httpd"
    stdin, stdout, stderr = client.exec_command(data)
    sleep(2)
    stdout=stdout.read()
    stderr=stderr.read()
    print(data,stdout,stderr)
    res=re.findall(r'\d+',stdout)
    print(res)
    if res:
        print("\n Success: Got the PID ")
        assert True
    else:
        print("\n Failure: did not get PID")
        assert False
                
def Verify_the_HTTP_service_is_running(IP): 
    print("\n Verify the HTTP service is running on "+IP+"\n")
    LookFor=".*Sending state change trap for.*http_file_dist.*HTTP File Dist Service is working.* from 40 to 38"
    print(LookFor)
    logs=logv(LookFor,"/infoblox/var/infoblox.log",IP)
    print(logs)
    print('-------------------------')
    if logs:
        print("Success: Verified the HTTP service is running")
        assert True
        
    else:
        print("Failure: Verified the HTTP service is not running")
        assert False 

def Check_the_status_of_HTTP_service_are_running(obj_index): 
    print("\n Check if HTTP services are running\n")
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:filedistribution?_return_fields=http_status")
    print(get_ref)
    ref=json.loads(get_ref)[obj_index]['http_status']
    print(ref)
    
    if 'WORKING' in ref:
        print("Success: **HTTP services is working state**")
        assert True
    else:
        print("Failure: **THTTP services is not in working state**")
        assert False
        
def Check_the_status_of_HTTP_service_is_inactive(obj_index): 
    print("\n Check if THTTP services is inactive state\n")
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:filedistribution?_return_fields=http_status")
    #print(get_ref)
    ref=json.loads(get_ref)[obj_index]['http_status']
    print(ref)
    
    if 'INACTIVE' in ref:
        print("Success: **HTTP services is inactive state**")
        assert True
    else:
        print("Failure: **HTTP services is not in inactive state**")
        assert False
        

def upload_files(file_name,IP):
    log("start","/infoblox/var/audit.log",IP)
    response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=uploadinit")
    print(response)
    res = json.loads(response)
    URL=res['url']
    token1=res['token']
    print("URL is : %s", URL)
    print("Token is %s",token1)
    infoblox_log_validation ='curl -k -u admin:infoblox -H content_type="content-typemultipart-formdata" ' + str(URL) +' -F file=@'+file_name
    out2 = commands.getoutput(infoblox_log_validation)
    print (out2)
    data={ "dest_path": "/"+file_name, "type": "TFTP_FILE","token":token1}
    print (data)
    response2 = ib_NIOS.wapi_request('POST', object_type="fileop?_function=setfiledest",fields=json.dumps(data))
    print(response2)
    log("stop","/infoblox/var/audit.log",IP)

    if type(response2) == tuple:           
        if response2[0]==400:  
            print("\n Failure: did not Uploaded file\n")
            assert False
        else:
            print("\n Success: Uploaded files successfully\n")
            assert False

def Verify_the_HTTP_service_is_stopped(IP): 
    print("\n======================================")
    print("\n Verify the HTTP service is stopped on "+IP+"\n")
    print("======================================\n")
    LookFor=".*Sending process start.*stop trap for.*httpd .*The process started normally.*"
    print(LookFor)
    logs=logv(LookFor,"/infoblox/var/infoblox.log",IP)
    print(logs)
    print('-------------------------')
    if logs:
        print("Success: Verified the HTTP service is stopped")
        assert True
        
    else:
        print("Failure: Verified the HTTP service is not stopped")
        assert False 
        
def Set_HTTP_ACLs_to_the_member(val,obj_index,which_mem,add,permission):
    
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:filedistribution")
    
    ref=json.loads(get_ref)[obj_index]['_ref']
    print(ref)
    data = {"enable_http_acl":val,"http_acls": [{"address": add,"permission": permission}]}
    response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
    print(response)
    if type(response) == tuple:
        if response[0]==200:
            print("\n Success: Set HTTP ACLs on "+which_mem)
            assert True
        else:
            print("\n Failure: did not Set HTTP ACLs on "+which_mem)
            assert False
    elif 'member' in response:
        
        print("\n Success: Set HTTP ACLs on "+which_mem)
        assert True
    sleep(20)           
    
def Validate_HTTP_ACLs_is_set_to_the_member(obj_index,which_mem,address,permission):
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:filedistribution?_return_fields=http_acls")
    
    add=json.loads(get_ref)[obj_index]['http_acls'][0]['address']
    per=json.loads(get_ref)[obj_index]['http_acls'][0]['permission']
    print(add,per)
    if address in add and permission in per:
        print("Sucess: validated successfully on set HTTP ACLs")
        assert True
    else:
        print("Failure: Could not validate successfully on set HTTP ACLs")
        assert False
           
def delete_HTTP_ACLs_from_member(obj_index,which_mem):
    
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:filedistribution")
    
    ref=json.loads(get_ref)[obj_index]['_ref']
    print(ref)
    data = {"http_acls": []}
    response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
    print(response)
    if type(response) == tuple:
        if response[0]==200:
            print("\n Success: deleted HTTP ACLs on "+which_mem)
            assert True
        else:
            print("\n Failure: did not delete HTTP ACLs on "+which_mem)
            assert False
    sleep(20)           

def validate_uploaded_files_in_storage_path(IP,file_name):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(IP, username='root', pkey = mykey)
    sleep(2)
    channel = client.invoke_shell()
    stdin = channel.makefile('wb')
    stdout = channel.makefile('rb')
    stdin.write('''
    cd /storage/tftpboot
    ls
    exit
    ''')
    stdout=stdout.read()
    
    print(stdout)
    
    if file_name in stdout:
        print("\n Success: uploaded file is present in /storage path")
        assert True
    else:
        print("\n Failure: Could not find the file in the /storage path")
        assert False

def upload_download_file_when_Permission_set_to_ALLOW(IP,file_name):
    log("start","/var/log/messages", IP)
    try:
        http_upload=os.popen('curl -v -T "'+file_name+'" http://'+IP+'/ &> http_u.txt').read()
        http_download=os.popen('curl -v -m "1" http://'+IP+'/'+file_name+' &> http_d.txt').read()
        http_upload=os.popen("cat http_u.txt").read()
        http_download=os.popen("cat http_d.txt").read()
        str(http_upload)
        str(http_download)

        print(re.search('We are completely uploaded and fine',http_upload))
        print(re.search("GET /"+file_name, http_download))
        if re.search('We are completely uploaded and fine',http_upload) and re.search("GET /"+file_name, http_download):
            print("\nSucess: Successfully uploaded and downloaded file to grid")
            assert True
        else:
            print("\nFailure: did not uploaded and downloaded file to grid")
            return False
            assert False
            
    except Exception as e:
        print("\n Failure: error in upload and download HTTP file")
        print("\n================Error====================\n")
        print(e)
        return False 
        assert False 
        
    finally:  
        log("stop","/var/log/messages", IP)

          
def check_able_to_login_appliances(ip):

    for i in range(5):
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+ip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.close()
            print("\n************Appliances is Working************\n ")
            sleep(120)
            assert True
            break

        except Exception as e:
            child.close()
            print(e)
            sleep(120)
            continue
            
            print("Failure: Appliances did not comeup(vm didn't comeup)")

            assert False

def delete_files_through_path(IP):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(IP, username='root', pkey = mykey)
    sleep(2)
    channel = client.invoke_shell()
    stdin = channel.makefile('wb')
    stdout = channel.makefile('rb')
    
    stdin.write('''
    cd /storage/tftpboot
    rm -rf *
    ls -ltr
    exit
    ''')
    sleep(2)
    stdout=stdout.read()
    
    print(stdout)
    
    if "total 0" in stdout:
        print("\n Success: Removed all files from /storage path")
        assert True
    else:
        print("\n Failure: Could not Removed all files from /storage path")
        assert False

def enable_Allow_grid_member(val):
    get_ref = ib_NIOS.wapi_request('GET', object_type='grid:filedistribution')
    getref=json.loads(get_ref)[0]['_ref']
    print(getref)
    data={"allow_uploads": val}

    response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
    print(response)
    
    if type(response) == tuple:           
        if response[0]==200:  
            print("\nSuccess:uploads to Grid members are "+str(val)+" \n")
            assert True
        else:
            print("\Failure: uploads to Grid members are "+str(val)+" \n")
            assert False
    elif 'grid' in response:
        print("\n Success: uploads to Grid members are "+str(val)+" ")
        assert True
    else:
        print("\n Failure:uploads to Grid members are not allowed.")
        assert False

def reboot_node(IP):
    print("start rebooting "+str(IP))
    try:
        child1 = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+IP)
        child1.logfile=sys.stdout
        child1.expect('password:')
        child1.sendline('infoblox')
        child1.expect('Infoblox >')
        child1.sendline('reboot')
        child1.expect('y or n')
        child1.sendline('y')
        sleep(60)
        check_able_to_login_appliances(IP)
        sleep(30)
        child1.close()
    except Exception as e:
        child1.close()
        print("\n Failure: error in rebooting")
        print("\n================Error====================\n")
        print(e)
        assert False  

def restart_services(obj_index):
    print("\nRestart Services")
    grid =  ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid1_master_mgmt_vip)
    ref = json.loads(grid)[obj_index]['_ref']
    print(ref)
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","services": "ALL"}
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid1_master_mgmt_vip)
    sleep(30)

def GMC_promote_member_as_master_candidate():
    
    get_ref = ib_NIOS.wapi_request('GET', object_type="member?_return_fields=master_candidate", grid_vip=config.grid1_master_mgmt_vip)
    print(get_ref)

    for ref in json.loads(get_ref):
        if config.grid1_member2_fqdn in ref['_ref']:
            data = {"master_candidate": True}
            response = ib_NIOS.wapi_request('PUT', ref=ref['_ref'], fields=json.dumps(data), grid_vip=config.grid1_master_mgmt_vip)
            print(response)
            if type(response) == tuple:
                if response[0]==200:
                    print("Success: set master candidate to true for member")
                    assert True
                else:
                    print("Failure: Can't set master candidate to true for member")
                    assert False
            elif "member" in response:
                print("Success: set master candidate to true for member")
                assert True

def promote_master(IP):
    
    child1 = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+IP)
    try:
        child1.logfile=sys.stdout
        child1.expect('password:')
        child1.sendline('infoblox')
        child1.expect('Infoblox >')
        child1.sendline('set promote_master')
        child1.expect('y or n')
        child1.sendline('y')
        child1.expect('Default: 30s')
        child1.sendline('\n')
        child1.expect('y or n')

        child1.sendline('y\n')

        child1.expect('y or n')
        child1.sendline('y\n')

        child1.expect('y or n')
        child1.sendline('y\n')

        output = child1.before
        print(output)
        check_able_to_login_appliances(IP)
        child1.close()
        assert True


    except Exception as e:
        child1.close()
        print("Failure: Can't promote GMC Master as master candidate")
        print(e)
        assert False

def validate_status_GM_after_GMC_promotion(IP):
    check_able_to_login_appliances(IP)
    try:
        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+IP)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show network')
        child.expect('Infoblox >')
        print("\n")
        output = child.before
        print("==============================")
        print(output)
        data = 'Master of Infoblox Grid'
        if data in output:
            print("Success: this member become GMC after the promotion")
            assert True
        else:
            print("Failure: this member did not become GMC after the promotion")
            assert False

    except Exception as error_message:
            print(error_message)
            assert False
    finally:
            child.close()

def verify_the_node_after_a_HA_failover(IP,data):
    try:
        child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+IP)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show status')
        child.expect('Infoblox >')
        print("\n")
        output = child.before
        print("==============================")
        #print(output)
        if data in output:
            print("Success: this member become "+data+" node after the HA failover")
            assert True
        else:
            print("Failure: this member did not become "+data+" node after the HA failover")
            assert False

    except Exception as error_message:
            print(error_message)
            assert False
    finally:
            child.close()

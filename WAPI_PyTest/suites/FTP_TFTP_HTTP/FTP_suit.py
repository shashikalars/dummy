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
# global dir_ref

def start_FTP_services(obj_index,IP,which_mem):
    log("start","/infoblox/var/infoblox.log",IP)
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:filedistribution")
    
    ref=json.loads(get_ref)[obj_index]['_ref']
    print(ref)
    data = {"enable_ftp": True}
    response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))

    print(response)
    if type(response) == tuple:
        if response[0]==200:
            print("\n Success: Start FTP service on "+which_mem)
            assert True
        else:
            print("\n Failure: did not Start FTP service on "+which_mem)
            assert False
    sleep(30)           
    log("stop","/infoblox/var/infoblox.log",IP)

    
def stop_FTP_services(obj_index,IP,which_mem):
    log("start","/infoblox/var/infoblox.log",IP)
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:filedistribution")
    
    ref=json.loads(get_ref)[obj_index]['_ref']
    print(ref)
    data = {"enable_ftp": False}
    response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
    print(response)
    if type(response) == tuple:
        if response[0]==200:
            print("\n Success: Stop FTP service on "+which_mem)
            assert True
        else:
            print("\n Failure: did not Stop FTP service on "+which_mem)
            assert False
    sleep(20)           
    log("stop","/infoblox/var/infoblox.log",IP)

def grep_vsftpd_and_validate_PID(IP):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(IP, username='root', pkey = mykey)
    sleep(2)
    data="pgrep vsftpd"
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
                
def Verify_the_FTP_service_is_running(IP): 
    print("\n Verify the FTP service is running on "+IP+"\n")
    LookFor=".*Sending state change trap for.*- ftp .*FTP Service is working.* from 28 to 26.*"
    print(LookFor)
    logs=logv(LookFor,"/infoblox/var/infoblox.log",IP)
    print(logs)
    print('-------------------------')
    if logs:
        print("Success: Verified the FTP service is running")
        assert True
        
    else:
        print("Failure: Verified the FTP service is not running")
        assert False 

def Check_the_status_of_FTP_service_are_running(obj_index): 
    print("\n Check if FTP services are running\n")
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:filedistribution?_return_fields=ftp_status")
    #print(get_ref)
    ref=json.loads(get_ref)[obj_index]['ftp_status']
    print(ref)
    
    if 'WORKING' in ref:
        print("Success: **FTP services is working state**")
        assert True
    else:
        print("Failure: **FTP services is not in working state**")
        assert False
        
def Check_the_status_of_FTP_service_is_inactive(obj_index): 
    print("\n Check if FTP services is inactive state\n")
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:filedistribution?_return_fields=ftp_status")
    #print(get_ref)
    ref=json.loads(get_ref)[obj_index]['ftp_status']
    print(ref)
    
    if 'INACTIVE' in ref:
        print("Success: **FTP services is inactive state**")
        assert True
    else:
        print("Failure: **FTP services is not in inactive state**")
        assert False
        
def Validate_the_log_index_forbidden_by_Options(IP,which_mem): 
    print("======================================")
    print("\n Validate the log index forbidden by options log present on "+which_mem+"\n")
    print("======================================")
    
    LookFor=".*server-generated directory index forbidden by Options directive.*"
    print(LookFor)
    logs=logv(LookFor,"/infoblox/var/infoblox.log",IP)
    print(logs)
    print('-------------------------')
    if logs:
        print("Failure: Got index forbidden by options messages in log ")
        assert False 
    else:
        print("Success: Did not get index forbidden by options messages and no error on "+which_mem+"")
        assert True
    
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

def Verify_the_FTP_service_is_stopped(IP): 
    print("\n======================================")
    print("\n Verify the FTP service is stopped on "+IP+"\n")
    print("======================================\n")
    LookFor=".*Sending state change trap for.*- ftp .*FTP Service is inactive.* from 26 to 28.*"
    print(LookFor)
    logs=logv(LookFor,"/infoblox/var/infoblox.log",IP)
    print(logs)
    print('-------------------------')
    if logs:
        print("Success: Verified the FTP service is stopped")
        assert True
        
    else:
        print("Failure: Verified the FTP service is not stopped")
        assert False 
        
def Set_FTP_ACLs_to_the_member(obj_index,which_mem,add,permission):
    
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:filedistribution")
    
    ref=json.loads(get_ref)[obj_index]['_ref']
    print(ref)
    data = {"ftp_acls": [{"address": add,"permission": permission}]}
    response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
    print(response)
    if type(response) == tuple:
        if response[0]==200:
            print("\n Success: Set FTP ACLs on "+which_mem)
            assert True
        else:
            print("\n Failure: did not Set FTP ACLs on "+which_mem)
            assert False
    sleep(20)           
    
def Validate_FTP_ACLs_is_set_to_the_member(obj_index,which_mem,address,permission):
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:filedistribution?_return_fields=ftp_acls")
    
    add=json.loads(get_ref)[obj_index]['ftp_acls'][0]['address']
    per=json.loads(get_ref)[obj_index]['ftp_acls'][0]['permission']
    print(add,per)
    if address in add and permission in per:
        print("Sucess: validated successfully on set FTP ACLs")
        assert True
    else:
        print("Failure: Could not validate successfully on set FTP ACLs")
        assert False
        
def restart_services(obj_index):
    print("\nRestart DNS Services")
    grid =  ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)
    ref = json.loads(grid)[obj_index]['_ref']
    print(ref)
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","services": "ALL"}
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
    sleep(30)
    
def delete_FTP_ACLs_from_member(obj_index,which_mem):
    
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:filedistribution")
    
    ref=json.loads(get_ref)[obj_index]['_ref']
    print(ref)
    data = {"ftp_acls": []}
    response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
    print(response)
    if type(response) == tuple:
        if response[0]==200:
            print("\n Success: deleted FTP ACLs on "+which_mem)
            assert True
        else:
            print("\n Failure: did not delete FTP ACLs on "+which_mem)
            assert False
    sleep(20)           
    
def change_permission_to_DENY(obj_index,which_mem,add,permission):  
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:filedistribution")
    
    ref=json.loads(get_ref)[obj_index]['_ref']
    print(ref)
    data = {"ftp_acls": [{"address": add,"permission": permission}]}
    response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
    print(response)
    if type(response) == tuple:
        if response[0]==200:
            print("\n Success: Updated FTP ACLs on "+which_mem)
            assert True
        else:
            print("\n Failure: did not Updated FTP ACLs on "+which_mem)
            assert False
    sleep(20)

def validate_uploaded_files_in_storage_path(IP,file_name):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(IP, username='root', pkey = mykey)
    sleep(2)
    data="cd /storage/tftpboot"
    stdin, stdout, stderr = client.exec_command(data)
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
                
def Create_a_directory(IP,dir_name):
    
    dir_ref=os.popen('curl -k1 -u admin:infoblox -H "Content-Type:application/json" -X POST https://'+IP+'/wapi/v'+config.wapi_version+'/tftpfiledir -d \'{"name":"'+dir_name+'","type":"DIRECTORY"}\'').read()
    
    print(dir_ref)
    if type(dir_ref) == tuple:
        if dir_ref[0]==200:
            print("\n Success: Created directory")
            assert True
        else:
            print("\n Failure: did not created directory")
            assert False
    elif 'tftpfiledir' in dir_ref:
        print("\n Success: Created directory")
        assert True
    return dir_ref
    
def validate_directory_created_in_storage_path(IP,dir_name,path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(IP, username='root', pkey = mykey)
    sleep(5)
    channel = client.invoke_shell()
    stdin = channel.makefile('wb')
    stdout = channel.makefile('rb')

    stdin.write('''
    cd {}
    ls
    exit
    '''.format(path))
    stdout=stdout.read()
    '''
    data="cd /storage/tftpboot"
    stdin, stdout, stderr = client.exec_command(data)
    print(data,stderr.read(),stdout.read())
    sleep(5)
    data="ls -ltr"
    stdin, stdout, stderr = client.exec_command(data)
    stdout=stdout.read()
    stderr=stderr.read()
    print(data,stdout,stderr)
    '''
    print(stdout)
    if dir_name in stdout:
        print("\n Success: The /storage path contains the "+dir_name)
        client.close()
        assert True
        
    else:
        print("\n Failure: The created directory is not present in the "+dir_name)
        client.close()
        assert False

def rename_created_dir(IP,dir_ref,new_dir):
    response=os.popen('curl -k1 -u admin:infoblox -H "Content-Type:application/json" -X PUT https://'+IP+'/wapi/v'+config.wapi_version+'/'+dir_ref+' -d \'{"name":"'+new_dir+'"}\'').read()
    
    #response = curl -k -u admin:infoblox -H "Content-Type:application/json" -X PUT https://10.36.171.1/wapi/v2.12.2/tftpfiledir/Li5vbmUuZGlyZWN0b3J5JC9GVFBfRGlyZWN0b3J5:DIRECTORY/ -d '{"name":"FTP_Directory1"}'
    print(response)
    if type(response) == tuple:
        if response[0]==200:
            print("\n Success: renamed the created directory")
            assert True
        else:
            print("\n Failure: renamed the created directory")
            assert False
    elif 'tftpfiledir' in response:
        print("\n Success: renamed the created directory")
        assert True
    else:
        print("\n Failure: renamed the created directory")
        assert False
    
def Create_ftpuser(IP,ftp_name,permission,passwd):
    #print('curl -k1 -u admin:infoblox -H "Content-Type:application/json" -X POST https://'+IP+'/wapi/v'+config.wapi_version+'/ftpuser -d \'{"create_home_dir":True,"password":"'+passwd+'","permission":"'+permission+'","username":"'+ftp_name+'"}\'')
    ftpusr=os.popen('curl -k1 -u admin:infoblox -H "Content-Type:application/json" -X POST https://'+IP+'/wapi/v'+config.wapi_version+'/ftpuser -d \'{"create_home_dir":true,"password":"'+passwd+'","permission":"'+permission+'","username":"'+ftp_name+'"}\'').read()
    
    print(ftpusr)
    if type(ftpusr) == tuple:
        if ftpusr[0]==200:
            print("\n Success: Created FTPuser")
            assert True
        else:
            print("\n Failure: did not create FTPuser")
            assert False
    elif 'ftpuser' in ftpusr:
        print("\n Success: Created FTPuser")
        assert True
    else:
        print("\n Failure: did not create FTPuser")
        assert False

def Try_connecting_the_IP_after_adding_ACL_ALLOW_Permission(IP):
    try:
        child1 = pexpect.spawn('ftp '+IP)
        child1.logfile=sys.stdout
        child1.expect(':')
        child1.sendline(config.client_user)
        child1.expect('Password:')
        child1.sendline(config.password)
        child1.expect('ftp>')
        
        output= child1.before
        
        if 'Login successful' in output:
            print("\nSucess: Successfully logined in")
            child1.sendline("exit")
            assert True
            child1.close()
        else:
            print("\nFailure: did not log in successfully")
            child1.sendline("exit")
            assert False
            child1.close()
    except Exception as e:
        child1.close()
        print("\n Failure: error in login ftp")
        print("\n================Error====================\n")
        print(e)
        assert False   

def Try_connecting_the_IP_after_adding_ACL_DENY_Permission(IP):
    try:
        child1 = pexpect.spawn('ftp '+IP)
        child1.logfile=sys.stdout
        child1.expect('ftp>')
                
        output= child1.before
        if 'Restricted Access Only' in output or 'Service not available' in output:
            print("Restricted Access Only")
            child1.sendline("exit")
            assert True
            child1.close()
        else:
            print("Successfully logined in")
            child1.sendline("exit")
            assert False
            child1.close()
    except Exception as e:
        child1.close()
        print("\n Failure: Successfully logined in")
        print("\n================Error====================\n")
        print(e)
        assert False
   
def check_for_ftp_files_list(obj_index,IP):
    get_ref = ib_NIOS.wapi_request('GET', object_type='member:filedistribution?_return_fields=enable_ftp_filelist')
    getref=json.loads(get_ref)[obj_index]['_ref']
    get_FTP_F=json.loads(get_ref)[obj_index]['enable_ftp_filelist']
    print(get_FTP_F)
    
    try:
        child1 = pexpect.spawn('ftp '+IP)
        child1.logfile=sys.stdout
        child1.expect(':')
        child1.sendline("anonymous")
        child1.expect('ftp>')
        child1.sendline("ls")
        child1.expect('ftp>')
        output= child1.before
          
        if config.client_user in output :
            if get_FTP_F==True: 
                print("Success: Listing files successfully")
                assert True
                child1.sendline("exit")
                child1.close()
            else:
                print("Failure: file which you are looking for is not present permission denied")
                child1.sendline("exit")
                child1.close()
                assert False
                
        elif "Permission denied" in output:
            if get_FTP_F==False: 
                print("Success: restricted from listing files")
                child1.sendline("exit")
                assert True
                child1.close()
            else:
                print("Failure: Allowed listing files")
                child1.sendline("exit")
                assert False
                child1.close()
    except Exception as e:
        child1.sendline("exit")
        child1.close()
        print("\n Failure: Below, there is a spelling error.")
        print("\n================Error====================\n")
        print(e)
        assert False

def enable_Anonymous_FTP(obj_index):
    get_ref = ib_NIOS.wapi_request('GET', object_type='grid:filedistribution')
    getref=json.loads(get_ref)[obj_index]['_ref']
    print(getref)
    data={"enable_anonymous_ftp": True}

    response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
    print(response)
    
    if type(response) == tuple:           
        if response[0]==200:  
            print("\nSuccess: Enabled anonymous FTP\n")
            assert True
        else:
            print("\Failure: Can't Enabled anonymous FTP\n")
            assert False
            
def enable_ftp_filelist(obj_index):
    get_ref = ib_NIOS.wapi_request('GET', object_type='member:filedistribution')
    getref=json.loads(get_ref)[obj_index]['_ref']
    print(getref)
    data={"enable_ftp_filelist": True,"enable_ftp_passive":True}

    response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
    print(response)
    
    if type(response) == tuple:           
        if response[0]==200:  
            print("\nSuccess: Enabled FTP file listing\n")
            assert True
        else:
            print("\Failure: Can't Enabled FTP file listing\n")
            assert False

def Download_files_using_mget(IP,file_name):
    try:
        child1 = pexpect.spawn('ftp '+IP)
        child1.logfile=sys.stdout
        child1.expect(':')
        child1.sendline("anonymous")
        child1.expect('ftp>')
        child1.sendline('mget '+file_name)
        child1.expect('mget')
        child1.sendline('y')
        child1.expect('ftp>')
        output= child1.before
        
        if 'File send OK' in output:
            print("\nSucess: Successfully Downloaded file")
            child1.sendline("exit")
            assert True
            child1.close()
        else:
            print("\nFailure: Failed to Download file")
            child1.sendline("exit")
            assert False
            child1.close()

    except Exception as e:
        child1.sendline("exit")
        child1.close()
        print("\n Failure: Below, there is a spelling error.")
        print("\n================Error====================\n")
        print(e)
        assert False   

def Include_files_and_directories(value):
    get_ref = ib_NIOS.wapi_request('GET', object_type='grid:filedistribution')
    getref=json.loads(get_ref)[0]['_ref']
    print(getref)
    data={"backup_storage": value}

    response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
    print(response)
    
    if type(response) == tuple:           
        if response[0]==200:  
            print("\nSuccess: Enabled Include Files and Directories in System Backup\n")
            assert True
        else:
            print("\Failure: Can't Include Files and Directories in System Backup\n")
            assert False

def Taking_Grid_Backup_File():
    data = {"type": "BACKUP"}
    response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=getgriddata",grid_vip=config.grid_vip)
    response = json.loads(response)
    token_of_GM = response['token']
    token_of_URL = response['url']
    curl_download='curl -k -u admin:infoblox -H  "content-type: application/force-download" '+token_of_URL+' -o "database.bak"'
    os.system(curl_download)
    print(token_of_GM)
    print(token_of_URL)
    x = os.listdir(".")
    print(x)
    if 'database.bak' in x:
        print("Success: Successfully downloaded the file")
        assert True
    else:
        print("Failure: No file was downloaded")
        assert False

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

def Restore_Grid_Backup_File():
    print("Restore_Grid_Backup_File")
    log("start","/infoblox/var/infoblox.log", config.grid_vip)
    response = ib_NIOS.wapi_request('POST', object_type="fileop",params="?_function=uploadinit",grid_vip=config.grid_vip)
    response = json.loads(response)
    print(response)
    token_of_GM = response['token']
    token_of_URL = response['url']
    curl_upload='curl -k -u admin:infoblox -H "content-typemultipart-formdata" '+token_of_URL+' -F file=@database.bak'
    os.system(curl_upload)
    print(curl_upload)
    data = {"mode": "FORCED", "token": token_of_GM}
    response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=restoredatabase",grid_vip=config.grid_vip)
    sleep(260)
    check_able_to_login_appliances(config.grid_vip)
    log("stop","/infoblox/var/infoblox.log",config.grid_vip)
    
    check_master=commands.getoutput(" grep -cw \".*restore_node complete.*\" /tmp/"+str(config.grid_vip)+"_infoblox_var_infoblox.lo*")
    if (int(check_master)!=0):
        assert True
    else:
        assert False
    sleep(60)

def validate_empty_uploaded_files_in_storage_path(IP,file_name,path):
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
    cd {}
    ls
    exit
    '''.format(path))
    stdout=stdout.read()
    print(stdout,type(stdout))

    if file_name not in stdout:
        print("\n Success: No longer any files in the storage path")
        assert True
    else:
        print("\n Failure: files can be found in the storage path.")
        assert False

def Set_storage_limit(val):
    print("Set storage limit as "+str(val)+" MB\n\n")
    get_ref = ib_NIOS.wapi_request('GET', object_type='grid:filedistribution')
    getref=json.loads(get_ref)[0]['_ref']
    print(getref)
    data={"storage_limit": val}

    response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
    print(response)
    
    if type(response) == tuple:           
        if response[0]==200:  
            print("\nSuccess:To limit storage to "+str(val)+" MB\n")
            assert True
        else:
            print("\Failure: can't not set storage limit as "+str(val)+" MB\n")
            assert False
    elif 'grid' in response:
        print("\n Success: To limit storage to "+str(val)+" MB")
        assert True
    else:
        print("\n Failure: can't not create FTPuser")
        assert False
    sleep(10)
def validate_storage_limit(val):
        print("Validate storage limit set as 1 MB\n\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:filedistribution')
        getref=json.loads(get_ref)
        print(getref)   
        print(getref[0]['storage_limit'])
        
        if getref[0]['storage_limit']==val:  
            print("\nSuccess: Validate storage limit is set to "+str(val)+" MB\n")
            assert True
        else:
            print("\Failure: Validate storage limit is not to set "+str(val)+" MB\n")
            assert False
            
def upload_files_after_set_to_1MB_size(file_name,IP):
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
            print("\n Success: Exceed the TFTP Storage limit\n")
            assert True 
        else:
            print("\n Failure: Able to upload less than 1MB file\n")
            assert False

def create_permission_group(ref):
    
    data= {"group": "cloud-api-only","permission": "WRITE","object": ref}
    response = ib_NIOS.wapi_request('POST', object_type = "permission",fields=json.dumps(data),grid_vip=config.grid_vip)
    print(response)

    if type(response) == tuple:           
        if response[0]==200: 
            print("\n Success: permission group was added to the folder.\n")
            assert True 
        else:
            print("\n Failure: permission group was not added to the folder.\n")
            assert False
    elif 'permission' in response:
        print("\n Success: Added permission group to the folder\n")
        assert True 
    return response

def change_permission_group(per_ref,dir_ref):
    per_ref=per_ref.strip('\"')
    #print(per_ref)
    data={"group": "cloud-api-only","permission": "READ","object": dir_ref}

    response = ib_NIOS.wapi_request('PUT', ref=per_ref, fields=json.dumps(data))
    print(response)

    if type(response) == tuple:           
        if response[0]==200: 
            print("\n Success: Changed the permission to the folder.\n")
            assert True 
        else:
            print("\n Failure: cant chnage permission  to the folder.\n")
            assert False
    elif 'permission' in response:
        print("\n Success: Changed the permission to the folder\n")
        assert True 


def Start_DNS_Service(obj_index,which_mem):
    
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
    
    ref=json.loads(get_ref)[obj_index]['_ref']
    print(ref)
    data = {"enable_dns": True}
    response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
    print(response)
    if type(response) == tuple:
        if response[0]==200:
            print("\n Success: Start DNS service on "+which_mem)
            assert True
        else:
            print("\n Failure: did not start DNS service on "+which_mem)
            assert False
    sleep(20)        

def Stop_DNS_Service(obj_index,which_mem):
    
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
    
    ref=json.loads(get_ref)[obj_index]['_ref']
    print(ref)
    data = {"enable_dns": False}
    response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
    print(response)
    if type(response) == tuple:
        if response[0]==200:
            print("\n Success: Stop DNS service on "+which_mem)
            assert True
        else:
            print("\n Failure: did not stop DNS service on "+which_mem)
            assert False
    sleep(20)      

def Validate_enabled_DNS_service(obj_index):
    print("\n Check if DNS services are running\n")
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns?_return_fields=enable_dns")
    print(get_ref)
    ref=json.loads(get_ref)[obj_index]['enable_dns']
    print(ref)
    
    if ref==True:
        print("Success: **DNS services is enabled**")
        assert True
    else:
        print("Failure: **DNS services is not enabled**")
        assert False

def Configure_AD_server_details_in_the_grid():
    print("Configuring AD server details in the grid")
    data={
            "name": "testing",
            "ad_domain": "adser",
            "domain_controllers": [
                {
                    "auth_port": 389,
                    "disabled": False,
                    "fqdn_or_ip": "5.5.5.5",
                    "encryption": "NONE",
                    "use_mgmt_port": False
                }
            ]
        }
    response = ib_NIOS.wapi_request('POST', object_type="ad_auth_service",fields=json.dumps(data))
    print(response)
    if bool(re.match("\"ad_auth_service*.",str(response))):
        print("AD service configured sucessfully")
        assert True
    else:
        print("AD service configuration failed")
        assert False


def start_Captive_service():
    
    get_ref = ib_NIOS.wapi_request('GET', object_type="captiveportal")
    print(get_ref)
    ref=json.loads(get_ref)[1]['_ref']
    print(ref)
    data={"service_enabled":True}
    response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data))
    print(response)
    return response

def add_AD_server_to_the_member():
 
    get_ref = ib_NIOS.wapi_request('GET', object_type="ad_auth_service")
    
    aduser=json.loads(get_ref)[0]['name']
    print(aduser)
    data={"authn_server_group":aduser}
    response = ib_NIOS.wapi_request('POST', object_type="captiveportal",fields=json.dumps(data))
    print(response)
    if type(response) == tuple:           
        if response[0]==200: 
            print("\n Success: added Auth server to the member.\n") 
            assert True 
        else:
            print("\n Failure: did not added Auth server to the member open bug: NIOS-88917\n")
            assert False
    elif 'captiveportal' in response:
        print("\n Success: added Auth server to the member\n")
        assert True 

def start_FTP_services_on_M2(obj_index,IP,which_mem):
    log("start","/infoblox/var/infoblox.log",IP)
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:filedistribution",grid_vip=config.grid2_master_vip)
    
    ref=json.loads(get_ref)[obj_index]['_ref']
    print(ref)
    data = {"enable_ftp": True}
    response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data),grid_vip=config.grid2_master_vip)

    print(response)
    if type(response) == tuple:
        if response[0]==200:
            print("\n Success: Start FTP service on "+which_mem)
            assert True
        else:
            print("\n Failure: did not Start FTP service on "+which_mem)
            assert False
    sleep(30)           
    log("stop","/infoblox/var/infoblox.log",IP)

    
def stop_FTP_services_on_M2(obj_index,IP,which_mem):
    log("start","/infoblox/var/infoblox.log",IP)
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:filedistribution",grid_vip=config.grid2_master_vip)
    
    ref=json.loads(get_ref)[obj_index]['_ref']
    print(ref)
    data = {"enable_ftp": False}
    response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data),grid_vip=config.grid2_master_vip)
    print(response)
    if type(response) == tuple:
        if response[0]==200:
            print("\n Success: Stop FTP service on "+which_mem)
            assert True
        else:
            print("\n Failure: did not Stop FTP service on "+which_mem)
            assert False
    sleep(20)           
    log("stop","/infoblox/var/infoblox.log",IP)
               
def Verify_the_FTP_service_is_running_on_M2(IP): 
    print("\n Verify the FTP service is running on "+IP+"\n")
    LookFor=".*Sending state change trap for.*- ftp .*FTP Service is working.* from 28 to 26.*"
    print(LookFor)
    logs=logv(LookFor,"/infoblox/var/infoblox.log",IP)
    print(logs)
    print('-------------------------')
    if logs:
        print("Success: Verified the FTP service is running")
        assert True
        
    else:
        print("Failure: Verified the FTP service is not running")
        assert False 

def Check_the_status_of_FTP_service_are_running_on_M2(obj_index): 
    print("\n Check if FTP services are running\n")
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:filedistribution?_return_fields=ftp_status",grid_vip=config.grid2_master_vip)
    #print(get_ref)
    ref=json.loads(get_ref)[obj_index]['ftp_status']
    print(ref)
    
    if 'WORKING' in ref:
        print("Success: **FTP services is working state**")
        assert True
    else:
        print("Failure: **FTP services is not in working state**")
        assert False
'''       
def Check_the_status_of_FTP_service_is_inactive(obj_index): 
    print("\n Check if FTP services is inactive state\n")
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:filedistribution?_return_fields=ftp_status",grid_vip=config.grid2_master_vip)
    #print(get_ref)
    ref=json.loads(get_ref)[obj_index]['ftp_status']
    print(ref)
    
    if 'INACTIVE' in ref:
        print("Success: **FTP services is inactive state**")
        assert True
    else:
        print("Failure: **FTP services is not in inactive state**")
        assert False
'''    
        
def Set_FTP_ACLs_to_the_member_on_M2(obj_index,which_mem,add,permission):
    
    get_ref = ib_NIOS.wapi_request('GET', object_type="member:filedistribution",grid_vip=config.grid2_master_vip)
    
    ref=json.loads(get_ref)[obj_index]['_ref']
    print(ref)
    data = {"ftp_acls": [{"address": add,"permission": permission}]}
    response = ib_NIOS.wapi_request('PUT', ref=ref, fields=json.dumps(data),grid_vip=config.grid2_master_vip)
    print(response)
    if type(response) == tuple:
        if response[0]==200:
            print("\n Success: Set FTP ACLs on "+which_mem)
            assert True
        else:
            print("\n Failure: did not Set FTP ACLs on "+which_mem)
            assert False
    sleep(20)      


def enable_Allow_grid_member(val):
    get_ref = ib_NIOS.wapi_request('GET', object_type='grid:filedistribution',grid_vip=config.grid_vip)
    getref=json.loads(get_ref)[0]['_ref']
    print(getref)
    data={"allow_uploads": val}

    response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data),grid_vip=config.grid_vip)
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

def Taking_Grid_Backup_using_FTP():
    filename="backup_FTP.bak"

    data = {"type": "BACKUP", "nios_data": True, "remote_url": "ftp://"+config.client_user+":"+config.password+"@"+config.grid2_master_vip +"/"+filename}
    print(json.dumps(data))
    response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data))
    print(response)
    
    if type(response) == tuple:           
        if response[0]==200:  
            print("\nSuccess:Downloaded grid backup files using FTP  \n")
            assert True
        else:
            print("\Failure: 550 Permission denied while taking grid backup using FTP: Open bug:NIOS-86316 \n")
            assert False
    
    return filename


def enable_lan2_and_nic(val,e_d):
    get_ref = ib_NIOS.wapi_request('GET', object_type='member',grid_vip=config.grid_vip)
    getref=json.loads(get_ref)[2]['_ref']
    print(getref)
    data={"lan2_port_setting":{"enabled":val, "nic_failover_enable_primary":val,"nic_failover_enabled":val}}

    response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
    print(response)
    if type(response) == tuple:           
        if response[0]==200: 
            print("\n Success: "+e_d+" Lan2 details.\n") 
            assert True 
        else:
            print("\n Failure: did not "+e_d+" Lan2 details\n")
            assert False
    elif 'member' in response:
        print("\n Success: "+e_d+" Lan2 details\n")
        assert True 

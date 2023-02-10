#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
# Grid Set up required:                                                     #
#  1. Grid + HA + SA member + reporting member                              #
#  2. Licenses : Grid,NIOS                                                  #
#############################################################################
import os
import re
import config
import pytest
import unittest
import logging
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import shlex
from time import sleep
from subprocess import Popen, PIPE
import pexpect
import paramiko
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
import commands

class NIOS_FTP_TFTP_HTTP(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_Set_storage_limit_1MB(self):
        print("Set storage limit as 1 MB\n\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:filedistribution')
        getref=json.loads(get_ref)[0]['_ref']
        print(getref)
        data={"storage_limit": 1}

        response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
        print(response)
       
        if type(response) == tuple:           
            if response[0]==200:  
                print("\nSuccess: To Set storage limit as 1 MB\n")
                assert True
            else:
                print("\Failure: To Set storage limit as 1 MB\n")
                assert False
                
    @pytest.mark.run(order=2)
    def test_001_validate_storage_limit_set_to_1MB(self):
        print("Validate storage limit set as 1 MB\n\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:filedistribution')
        getref=json.loads(get_ref)[0]['_ref']
        print(getref['storage_limit'])
        
        if getref['storage_limit']==1:  
            print("\nSuccess: Validate storage limit is set to 1 MB\n")
            assert True
        else:
            print("\Failure: Validate storage limit is not to set 1 MB\n")
            assert False
            
    @pytest.mark.run(order=3)
    def test_002_Upload_files_1MB_size(self):
        
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=uploadinit")
        print(response)
        res = json.loads(response)
        URL=res['url']
        token1=res['token']
        print("URL is : %s", URL)
        print("Token is %s",token1)
        infoblox_log_validation ='curl -k -u admin:infoblox -H content_type="content-typemultipart-formdata" ' + str(URL) +' -F file=@file-example_PDF_1MB.pdf'
        out2 = commands.getoutput(infoblox_log_validation)
        print (out2)
        data={ "dest_path": "/file-example_PDF_500_kB.pdf", "type": "TFTP_FILE","token":token1}
        print (data)
        response2 = ib_NIOS.wapi_request('POST', object_type="fileop?_function=setfiledest",fields=json.dumps(data))
        print(response2)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        
        
        if type(response2) == tuple:           
            if response2[0]==400:  
                print("\n Failure: Exceed the TFTP Storage limit\n")
                assert False
            else:
                print("\n Success: Able to upload less than 1MB file\n")
                assert False
 
    @pytest.mark.run(order=4)
    def test_003_validate_1MB_size_file_uploaded(self):
        pass
        
        
    @pytest.mark.run(order=5)
    def test_004_validate_infoblox_log_storage_limit_message(self): 
        print("\n Validate infoblox log\n")
        LookFor=".*Exceed the TFTP Storage limit.*"
        print(LookFor)
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        print(logs)
        print('-------------------------')
        if logs:
            print("Uploaded file exceeds the storage limit")
            assert False 
        else:
        
            assert True
            
    @pytest.mark.run(order=6)
    def test_005_Set_storage_limit_back_to_default_size(self):
        print("Set storage limit back to default size \n\n")           
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:filedistribution')
        getref=json.loads(get_ref)[0]['_ref']
        print(getref)
        data={"storage_limit": 500}

        response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
        print(response)
       
        if type(response) == tuple:           
            if response[0]==200:  
                print("\nSuccess: To Set storage limit back to default size\n")
                assert True
            else:
                print("\Failure: To Set storage limit back to default size\n")
                assert False 

    @pytest.mark.run(order=7)
    def test_006_validate_storage_limit_set_to_default(self):
        print("Validate storage limit set to default \n\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid:filedistribution')
        getref=json.loads(get_ref)[0]['_ref']
        print(getref['storage_limit'])
        
        if getref['storage_limit']==500:  
            print("\nSuccess: Validate storage limit is set default\n")
            assert True
        else:
            print("\Failure: Validate storage limit is not to default\n")
            assert False
            
    @pytest.mark.run(order=8)
    def test_007_upload_csv_file_with_UTF_8_symbol_in_filename(self): 
        log("start","/infoblox/var/audit.log",config.grid_vip)
        response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=uploadinit")
        print(response)
        res = json.loads(response)
        URL=res['url']
        token1=res['token']
        print("URL is : %s", URL)
        print("Token is %s",token1)
        infoblox_log_validation ='curl -k -u admin:infoblox -H content_type="content-typemultipart-formdata" ' + str(URL) +' -F file=@file-example_PDF_1MB.pdf'
        out2 = commands.getoutput(infoblox_log_validation)
        print (out2)
        data={ "dest_path": "/py_UTF-8.csv.xlsx", "type": "TFTP_FILE","token":token1}
        print (data)
        response2 = ib_NIOS.wapi_request('POST', object_type="fileop?_function=setfiledest",fields=json.dumps(data))
        print(response2)
        log("stop","/infoblox/var/audit.log",config.grid_vip)

        if type(response2) == tuple:           
            if response2[0]==200:  
                print("\n Success: Uploaded the file which contain UTF-8 symbol with filename \n")
                assert True
            else:
                print("\n Failure: Unable to upload file which contain UTF-8 filename symbol\n")
                assert False
      
    @pytest.mark.run(order=9)
    def test_008_validate_audit_log_able_to_upload_utf_8_symbol_filename(self): 
        print("\n Validate audit log\n")
        LookFor=".*imported tftp file.*"
        print(LookFor)
        logs=logv(LookFor,"/infoblox/var/audit.log",config.grid_vip)
        print(logs)
        print('-------------------------')
        if logs:
            print("Success: Uploaded the file which contain UTF-8 symbol with filename")
            assert True 
        else:
        
            assert False
            
    @pytest.mark.run(order=10)
    def test_009_Validate_active_master_is_1(self): 
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data="/bin/bash -x /infoblox/one/bin/generate_tftp_dir_checksum"
        stdin, stdout, stderr = client.exec_command(data)
        
        sleep(5)
        output=stderr.read()
        stdout=stdout.read()
        
        if "'[' active_master == active_master -a 1 == 1 ']'" in output:
            print(output)
            print("\nSuccess : Active master is 1\n")
            client.close()
            assert True
        else:
            client.close()
            assert False

    @pytest.mark.run(order=11)
    def test_010_Enable_hhtps_services(self): 
        log("start","/infoblox/var/audit.log",config.grid_vip)
        
        log("stop","/infoblox/var/audit.log",config.grid_vip)
    
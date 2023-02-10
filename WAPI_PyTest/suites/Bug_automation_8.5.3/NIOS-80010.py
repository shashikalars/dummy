#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
# Grid Set up required:                                                     #
#  1. Licenses : Grid                                                       #
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
from scapy import *
from scapy.utils import RawPcapReader
from scapy.all import *
import shutil
from shutil import copyfile
import ib_utils.common_utilities as common_util
class NIOS_80010(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_000_upload_bin2_file_click_on_update(self):
        cw=os.getcwd()
        path = "/import/builds/prod/analytics/MAIN"
        dir_list = os.listdir(path)
        print(dir_list[-1])
        path="/import/builds/prod/analytics/MAIN/"+str(dir_list[-1])
        files = os.listdir(path)
        print(files)
        for i in files:
            if re.match(r'moduleset-.*.bin2$', i):
                print(i)
                filename=i
                copyfile(path+'/'+filename,cw+'/moduleset.bin2')
                break
        
        print("Test Uploading the Template with fileop")
        filename="moduleset.bin2"
        data = {"filename":filename}
        create_file = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadinit")
        print(create_file)
        res = json.loads(create_file)
        token = json.loads(create_file)['token']
        url = json.loads(create_file)['url']
        file1=url.split("/")
        os.system('curl -k1 -u admin:infoblox -F name=%s -F filedata=@%s %s'%(filename,filename,url))
        print(filename,url)

        data = {"moduleset_token":token}
        res_set = ib_NIOS.wapi_request('POST', object_type="grid:threatanalytics",fields=json.dumps(data),params="?_function=set_last_uploaded_threat_analytics_moduleset")
        print(res_set)
        print("----------------------")

        res_upload = ib_NIOS.wapi_request('POST', object_type="grid:threatanalytics",params="?_function=update_threat_analytics_moduleset")
        print(res_upload,type(res_upload))
        
        data = {"filename":filename}
        create_file = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadinit")
        print(create_file)
        res = json.loads(create_file)
        token = json.loads(create_file)['token']
        url = json.loads(create_file)['url']
        file1=url.split("/")
        os.system('curl -k1 -u admin:infoblox -F name=%s -F filedata=@%s %s'%(filename,filename,url))
        print(filename,url)

        data = {"moduleset_token":token}
        res_set = ib_NIOS.wapi_request('POST', object_type="grid:threatanalytics",fields=json.dumps(data),params="?_function=set_last_uploaded_threat_analytics_moduleset")
        print(res_set)
        print("----------------------")

        res_upload = ib_NIOS.wapi_request('POST', object_type="grid:threatanalytics",params="?_function=update_threat_analytics_moduleset")
        print(res_upload,type(res_upload))


        if type(res_upload) == tuple and 'uploaded already exists in Grid' in res_upload[1]:
            print("Success: Module set already uploaded")
            assert True
        else:
            assert False
            #print(res_upload)




    @pytest.mark.run(order=2)
    def test_001_validate_xml_file_has_write_access(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        client.connect(config.grid_vip, username='root', pkey = mykey)
        data="ls -lrt /infoblox/var/analytics/model.xml\n"
        stdin, stdout, stderr = client.exec_command(data)
        stdout=stdout.read()
        print(stdout)
        if '-rw-rw-rw-' in stdout:
            print("Success : Write access provided to Other groups")
            client.close()
            assert True

        else:
            print("Failure : Write access not provided to Other groups")
            client.close()
            assert False





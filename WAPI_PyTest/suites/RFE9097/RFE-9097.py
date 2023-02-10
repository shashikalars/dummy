import re
from ib_utils.common_utilities import generate_token_from_file
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
from paramiko import client
import commands
import json, ast
import requests
import time
import pexpect
import getpass
import sys
import socket
import paramiko
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv

global host_ip

host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)

class ConnectionError:
    print("Check for SSH connection")

class SSH:
    client = None

    def __init__(self, address):
        print("connecting to server \n : ", address)
        self.client = client.SSHClient()
        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        self.client.load_system_host_keys()
        self.client.connect(address, username='root', port=22)

    def send_command(self, command):
        if (self.client):
            stdin, stdout, stderr = self.client.exec_command(command)
            result = stdout.read()
            print(result)
            error = stderr.read()
            print(error)
            return result
        else:
            print("Connection not opened.")

def log_validation(grid_vip,lookfor_list,file_path="/infoblox/var/infoblox.log"):
    try:
        connection = SSH(config.grid_vip)
        for look in lookfor_list:
	    command1="tail -200 " +str(file_path) + "| grep -i "+'"' + str(look)+'"'
            print (command1)
            conf_details = connection.send_command(command1)
            print (conf_details)
        return conf_details
    except ConnectionError:
        print ("Connection failed ")


class Network(unittest.TestCase):
    logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)

    @pytest.mark.run(order=1)
    def test_01_validate_discovery_csv_error_path_not_found(self):
        logging.info("validate discovery_csv_error path not found for fresh login")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('#')
            child.sendline('cd /infoblox/var/discovery_csv_error')
            child.expect('No such file or directory')
            child.sendline("exit")
            print(child.before)
            assert True
            print("Testcase 1 is passed")
        except:
            assert False
        finally:
            child.close()
	
    
    @pytest.mark.run(order=2)
    def test_02_import_netmri_csv_file(self):
          logging.info("Import Netmri CSV file using setdiscoverycsv & validate CSV import error logs should not be captured")
          #dir_name = "/import/qaddi/mgovarthanan"
          dir_name = os.getcwd()
	  base_filename = "ibsync.10.csv"
          token = generate_token_from_file(dir_name,base_filename)
          data = {"token": token,"network_view":"default"}
          response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=setdiscoverycsv")
          response=json.loads(response)
          sleep(30)
          print("File Uploaded Successfully")
	  #command1=os.system("cd /tmp/discovery_csv_error_files")
	  #command=os.system('scp root@'+config.grid_vip+':/infoblox/var/discovery_csv_error/* /tmp/discovery_csv_error_files')
	  #logging.info(command)
          ##########################################Log Validation ################################
          lookfor_list=["Memory allocation error while parsing the CSV file","Maximum column number reached 128, ignoring column","Unknown field name in header found, column will be ignored","Duplicate header field","Missing mandatory column","Skipped line in CSV file","Error while importing line in CSV file","No network was found for IP address","moving to last_csv_import failed","Detected an error in CSV file at line, aborting import","Couldn't initialize CSV parser for discovery import","Couldn't open CSV file","Import ended with the following status"]
	  log_validation_result=log_validation(config.grid_vip,lookfor_list)
          print("log_validation_result data check here :",log_validation_result)
          if (log_validation_result == ''):
              assert True
              print ("log validation passed ")
	  else:
	      assert False
	      print ("Testcase is failed")
	  print("Test case 2 completed")	  

    @pytest.mark.run(order=3)
    def test_03_validate_discovery_csv_error_path_created(self):
        logging.info("validate discovery_csv_error path created after csv import")
        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('#')
            child.sendline('cd /infoblox/var/discovery_csv_error')
            child.expect('#')
            child.sendline("exit")
            print(child.before)
            assert True
            print("Testcase 3 is passed")
        except:
            assert False
	    print("Testcase 3 is failed")
        finally:
            child.close()


    @pytest.mark.run(order=4)
    def test_04_validate_error_messages_csv_files_Unknown_field_name(self):
        #dir_name = "/import/qaddi/mgovarthanan"
        dir_name = os.getcwd()
	base_filename = "unknown.field.name.csv"
        token = generate_token_from_file(dir_name,base_filename)
        data = {"token": token,"network_view":"default"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=setdiscoverycsv")
        response=json.loads(response)
        sleep(60)
        print("File Uploaded Successfully")
        lookfor_list=["Unknown field name in header found, column will be ignored"]
        log_validation_result=log_validation(config.grid_vip,lookfor_list)
        print("log_validation_result data check here :",log_validation_result)
        if (log_validation_result == ''):
            assert True
            print ("log validation passed ")
        else:
            assert False
            print ("Log validation failed")
	command1=os.system("mkdir /tmp/discovery_csv_error_files")
        command=os.system('scp root@'+config.grid_vip+':/infoblox/var/discovery_csv_error/* /tmp/discovery_csv_error_files')
        logging.info(command)
        cmd="ls -ltr /tmp/discovery_csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/discovery_csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[0]
	    print(res)
	    final=re.search("Unknown field name",res)
	    print(final)
            if final is not None:
                logging.info("Test case 4 passed")
		assert True
            else:
                logging.info("Test case 4 Failed")
		assert False
	print("Test case 4 is completed")

    @pytest.mark.run(order=5)
    def test_05_validate_error_messages_csv_files_Duplicate_header_field(self):
        #dir_name = "/import/qaddi/mgovarthanan"
        dir_name = os.getcwd()
	base_filename = "duplicate.header.csv"
        token = generate_token_from_file(dir_name,base_filename)
        data = {"token": token,"network_view":"default"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=setdiscoverycsv")
        response=json.loads(response)
        sleep(60)
        print("File Uploaded Successfully")
        lookfor_list=["Discovery CSV import csvFileName : Duplicate header field found"]
        log_validation_result=log_validation(config.grid_vip,lookfor_list)
        print("log_validation_result data check here :",log_validation_result)
        if (log_validation_result == ''):
            assert True
            print ("log validation passed ")
        else:
            assert False
            print ("Log validation failed")
        command1=os.system("cd /tmp/discovery_csv_error_files")
        command=os.system('scp root@'+config.grid_vip+':/infoblox/var/discovery_csv_error/* /tmp/discovery_csv_error_files')
        logging.info(command)
        cmd="ls -ltr /tmp/discovery_csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        result=result.split(" ")
        #print result
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/discovery_csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[0]
            print(res)
            final=re.search("Duplicate header field",res)
            print(final)
            if final is not None:
                logging.info("Test case 5 passed")
                assert True
            else:
                logging.info("Test case 5 Failed")
                assert False
	print("Test case 5 is completed")


    @pytest.mark.run(order=6)
    def test_06_validate_error_messages_csv_files_skipping_row(self):
        #dir_name = "/import/qaddi/mgovarthanan"
        dir_name = os.getcwd()
	base_filename = "skipping.row.csv"
        token = generate_token_from_file(dir_name,base_filename)
        data = {"token": token,"network_view":"default"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=setdiscoverycsv")
        response=json.loads(response)
        sleep(60)
        print("File Uploaded Successfully")
        lookfor_list=["Discovery CSV import csvFileName : %s %scolumn '%s' with value '%s' at line %u, skipping row"]
        log_validation_result=log_validation(config.grid_vip,lookfor_list)
        print("log_validation_result data check here :",log_validation_result)
        if (log_validation_result == ''):
            assert True
            print ("log validation passed ")
        else:
            assert False
            print ("Log validation failed")
        command1=os.system("cd /tmp/discovery_csv_error_files")
        command=os.system('scp root@'+config.grid_vip+':/infoblox/var/discovery_csv_error/* /tmp/discovery_csv_error_files')
        logging.info(command)
        cmd="ls -ltr /tmp/discovery_csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/discovery_csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[0]
	    print(res)
            final=re.search("Discovery CSV import csvFileName : %s %scolumn '%s' with value '%s' at line %u, skipping row",res)
            if final is not None:
                logging.info("Test case 6 passed")
            else:
                logging.info("Test case 6 Failed")
	print("Test case 6 is completed")

    @pytest.mark.run(order=7)
    def test_07_validate_error_messages_csv_files_Missing_mandatory_column(self):
        #dir_name = "/import/qaddi/mgovarthanan"
        dir_name = os.getcwd()
	base_filename = "missing.mandatory.csv"
        token = generate_token_from_file(dir_name,base_filename)
        data = {"token": token,"network_view":"default"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=setdiscoverycsv")
        response=json.loads(response)
        sleep(60)
        print("File Uploaded Successfully")
        lookfor_list=["Discovery CSV import csvFileName : Missing mandatory column"]
        log_validation_result=log_validation(config.grid_vip,lookfor_list)
        print("log_validation_result data check here :",log_validation_result)
        if (log_validation_result == ''):
            assert True
            print ("log validation passed ")
        else:
            assert False
            print ("Log validation failed")
        command1=os.system("cd /tmp/discovery_csv_error_files")
        command=os.system('scp root@'+config.grid_vip+':/infoblox/var/discovery_csv_error/* /tmp/discovery_csv_error_files')
        logging.info(command)
        cmd="ls -ltr /tmp/discovery_csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/discovery_csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[0]
	    print(res)
            final=re.search("Missing mandatory column*header",res)
            if final is not None:
                logging.info("Test case 7 passed")
            else:
                logging.info("Test case 7 Failed")
	print("Test case 7 is completed")

    @pytest.mark.run(order=8)
    def test_08_validate_error_messages_csv_files_skipped_line(self):
        #dir_name = "/import/qaddi/mgovarthanan"
        dir_name = os.getcwd()
	base_filename = "skipping.row.csv"
        token = generate_token_from_file(dir_name,base_filename)
        data = {"token": token,"network_view":"default"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=setdiscoverycsv")
        response=json.loads(response)
        sleep(60)
        print("File Uploaded Successfully")
        lookfor_list=["Skipped line in CSV file"]
        log_validation_result=log_validation(config.grid_vip,lookfor_list)
        print("log_validation_result data check here :",log_validation_result)
        if (log_validation_result == ''):
            assert True
            print ("log validation passed ")
        else:
            assert False
            print ("Log validation failed")
        command1=os.system("cd /tmp/discovery_csv_error_files")
        command=os.system('scp root@'+config.grid_vip+':/infoblox/var/discovery_csv_error/* /tmp/discovery_csv_error_files')
        logging.info(command)
        cmd="ls -ltr /tmp/discovery_csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/discovery_csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[1]
	    print(res)
            final=re.search("Discovery CSV import [%s]: Skipped line #%u in CSV file",res)
            if final is not None:
                logging.info("Test case 8 passed")
            else:
                logging.info("Test case 8 Failed")
	print("Test case 8 completed")

    @pytest.mark.run(order=9)
    def test_09_validate_error_messages_could_not_open_csv_file(self):
        #dir_name = "/import/qaddi/mgovarthanan"
        dir_name = os.getcwd()
	base_filename = "skipping.row.csv"
        token = generate_token_from_file(dir_name,base_filename)
	data = {"token": token,"network_view":"default"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=setdiscoverycsv")
        response=json.loads(response)
        sleep(60)
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=setdiscoverycsv")
        response=json.loads(response)
        sleep(60)
        print("File Uploaded Successfully")
        lookfor_list=["Couldn't open CSV file"]
        log_validation_result=log_validation(config.grid_vip,lookfor_list)
        print("log_validation_result data check here :",log_validation_result)
        if (log_validation_result == ''):
            assert True
            print ("log validation passed ")
        else:
            assert False
            print ("Log validation failed")
        command1=os.system("cd /tmp/discovery_csv_error_files")
        command=os.system('scp root@'+config.grid_vip+':/infoblox/var/discovery_csv_error/* /tmp/discovery_csv_error_files')
        logging.info(command)
        cmd="ls -ltr /tmp/discovery_csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/discovery_csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
            res=res[0]
	    print(res)
            final=re.search("Discovery CSV import [%s]: Couldn't open CSV file (%s)",res)
            if final is not None:
                logging.info("Test case 09 passed")
            else:
                logging.info("Test case 09 Failed")
	print("Test case 9 is completed")

    @pytest.mark.run(order=10)
    def test_10_validate_error_messages_csv_file_Import_ended_with_following_status(self):
        #dir_name = "/import/qaddi/mgovarthanan"
        dir_name = os.getcwd()
	base_filename = "skipping.row.csv"
        token = generate_token_from_file(dir_name,base_filename)
        data = {"token": token,"network_view":"default"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=setdiscoverycsv")
        response=json.loads(response)
        sleep(60)
        print("File Uploaded Successfully")
        lookfor_list=["Import ended with the following status"]
        log_validation_result=log_validation(config.grid_vip,lookfor_list)
        print("log_validation_result data check here :",log_validation_result)
        if (log_validation_result == ''):
            assert True
            print ("log validation passed ")
        else:
            assert False
            print ("Log validation failed")
        command1=os.system("cd /tmp/discovery_csv_error_files")
        command=os.system('scp root@'+config.grid_vip+':/infoblox/var/discovery_csv_error/* /tmp/discovery_csv_error_files')
        logging.info(command)
        cmd="ls -ltr /tmp/discovery_csv_error_files"
        result = subprocess.check_output(cmd, shell=True)
        result=result.split(" ")
        error_log=result[-1].strip("\n")
        print error_log
        path='/tmp/discovery_csv_error_files/'+error_log
        with open(path,"r") as fobj:
            res=(fobj.readlines())
	    for i in res:
		if re.search("Import ended with the following status:",i):
		    break
		    assert True
	    else:
	        assert False
   	print("Test case 10 is completed")

    @pytest.mark.run(order=11)
    def test_11_validate_download_discovery_csv_errorlog(self):
	logging.info("validate discovery_csv_error.log can be downloaded using DISCOVERYCSVERRLOG object")
    	data={"include_rotated": False,"log_type":"DISCOVERY_CSV_ERRLOG","node_type":"ACTIVE"}
	create_file=ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=get_log_files")
    	print(create_file)
    	res = json.loads(create_file)
    	token = json.loads(create_file)['token']
    	url = json.loads(create_file)['url']
	logging.info (create_file)
     	print (res)
    	print(token)
    	print (url)
    	print("Create the fileop function to download the csv file to the specified url")
    	cmd='curl -k1 -u admin:infoblox -H "Content-type:application/force-download" -O %s'%(url)
    	result = subprocess.check_output(cmd, shell=True)
 	cmd="tar -xvzf discoveryCsvErrLog.tar.gz"
	result1 = subprocess.check_output(cmd, shell=True)
        cmd="ls -lrt tmp/discovery_csv_error_tarfiles"
        result2 = subprocess.check_output(cmd, shell=True)
	result2 = result2.split(" ")
	print(result2)
	for i in result2:
            if re.search("discovery_csv_error.log",i):
		print i
                assert True
		break
        else:
            assert False
	
	print("Discovery csv error logs has been downloaded successfully")


    @pytest.mark.run(order=12)
    def test_12_validate_download_support_bundle(self):
        logging.info("validate discovery_csv_error path not found for fresh login")
        path = os.getcwd()
	print(path)
	print(type(path))
	try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
	    child.sendline('infoblox')
	    child.expect('Infoblox >')
	    child.sendline('set transfer_supportbundle scp '+host_ip+' root infoblox dest '+path)
            child.expect(':')
            child.sendline("y")
	    sleep(50)
	    child.expect(".*scp succeeds.*Infoblox >")
            #print(child.before)
            assert True
            print("Testcase 12 is passed")
        except:
            assert False
        finally:
            child.close()

    @pytest.mark.run(order=13)
    def test_13_validate_count_error_log_after_download_support_bundle(self):
	logging.info("validate count of error log files after downloaded from support bundle")
        path = os.getcwd()
        print(path)
        print(type(path))
	cmd='tar -xvzf '+path+'/supportBundle.tar.gz'
        result1 = subprocess.check_output(cmd, shell=True)
	print("\n")
        cmd="ls "+path+"/infoblox/var/discovery_csv_error | wc -l"
        result2 = subprocess.check_output(cmd, shell=True)
	print(result2)
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('#')
        child.sendline('ls /infoblox/var/discovery_csv_error | wc -l')
	child.expect('#')
	result = child.before
	result = result.split(" ")
	print(result)
	error_log=result[-1][-12].strip("\n")
	print(error_log)
	child.close()
	if (int(error_log) == int(result2)):
	    assert True
	    print("Test case 13 is passed")
	else:
	    assert False
	    print("Test case 13 is passed")
	
	
    @pytest.mark.run(order=14)
    def test_14_validate_count_error_log_not_more_than_5_after_1_hour(self):
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
	mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
	client.connect(config.grid_vip, username='root', pkey = mykey)
	stdin, stdout, stderr = client.exec_command("ls -lrt /infoblox/var/discovery_csv_error | grep discovery_csv_error")
	result = stdout.read()
	result = list(filter(None, result.split('\n')))
	count = len(result)
	latest_five = result[-5:]
	old_files = result[:-5]
	print(result)
	print(latest_five)
	print("Count : "+str(count))
	print("Latest five : ")
	for log_file  in latest_five:
	    print(log_file)
	print("Old files : ")
	for log_file in old_files:
	    print(log_file)
	print("Sleeping for 3420 seconds")
	sleep(3420)
	stdin2, stdout2, stderr2 = client.exec_command("ls -lrt /infoblox/var/discovery_csv_error | grep discovery_csv_error")
	result2 = stdout2.read()
	result2 = list(filter(None, result2.split('\n')))
	count2 = len(result2)
	if count2 > 5:
    	    print("Failed")
	    assert False
	if old_files and old_files in result2:
	    print("Failed")
	    assert False

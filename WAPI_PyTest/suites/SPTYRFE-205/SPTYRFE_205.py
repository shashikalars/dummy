import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
import commands
import json, ast
import requests
import time
import pexpect
import sys
import pdb
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv


def prod_status(ip):
    ping_cmd= 'ping -c 3 '+str(ip)
    print ping_cmd
    for i in range(3):
        result_ping= os.system(ping_cmd)
    	if result_ping == 0:
	    print("product restarted successfully")
	    return True
	else:
	    sleep(30)
    else:
	print("product is still restarting")
	return False


def restart_services(grid_vip):
    """
    Restart Services
    """
    print("Restart services")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=grid_vip)
    ref = json.loads(grid)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data),grid_vip=grid_vip)
    sleep(10)


class sptyrfe_205(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_01_validating_synctime_command(self):
	try:
	    logging.info("Validating synctime command is present in list")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('help')
	    child.expect('Maintenance Mode >')
	    output = child.before
	    print ("output is" ,output)
	    if "synctime" in output:
	        logging.info("synctime command is present in Maintenance Mode command list")
	        assert True
	    else:
		logging.error("synctime command is not present in Maintenance Mode command list")
		assert False
	except Exception as error_message:
	    logging.info("synctime command is not present in Maintenance Mode command list")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)

    @pytest.mark.run(order=2)
    def test_02_validating_synctime_command(self):
	try:
	    logging.info("Validating synctime command output for offset value")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    child.expect('[Default: None]')
	    child.sendline(config.external_server_ip)
	    #child.expect(':')
	    #child.sendline('\r')
	    sleep(5)
	    child.expect(':')
	    child.sendline('n')
	    child.expect('Maintenance Mode >')
	    output = child.before
	    print ('my output',output)
	    #output= 
	    #output=output.replace('\n','').replace('\r','').replace(' ','').replace(':','').replace(']','').replace('(','').replace(')','').replace('?','')
	    output1 = re.findall("\d+\.\d+",output)
	    offset=output1[-1]	    
	    print (offset)
	    if offset:
	        logging.info("synctime command is displaying the offset values between systems")
	        assert True
	    else:
		logging.error("synctime command is not displaying the offset values between systems")
		assert False
	except Exception as error_message:
	    logging.info("synctime command is not displaying the offset values between systems")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)

    @pytest.mark.run(order=3)
    def test_03_validating_synctime_command(self):
	try:
	    logging.info("Validating synctime command output for proper messages when offset is small")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    child.expect('[Default: None]')
	    child.sendline(config.external_server_ip)
	    sleep(5)
	    child.expect(':')
	    child.sendline('n')
	    child.expect('Maintenance Mode >')
	    output = child.before
	    print ('my output',output)
	    output1 = re.findall("\d+\.\d+",output)
	    offset=output1[-1]	    
	    print (offset)
	    if float(offset) <=3:
		print ("offset value is less than 3 seconds")
	        if "Because the offset is very small, we recommend that you let NTP server handle it" in output:
		    logging.info("Notification that offset is small is displayed properly")
		    assert True
		else:
		    logging.info("Notification that offset is small is not displayed properly and system asks for restart")
		    assert False
	    else:
		if "Because the offset is very small, we recommend that you let NTP server handle it" in output:
		    logging.info("Notification that offset is small is displayed even when offset is not small")
		    assert False
		else:
		    logging.info("Offset value is more than 3 seconds")
		    assert True
		    
	except Exception as error_message:
	    logging.info("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)


    @pytest.mark.run(order=4)
    def test_04_validating_synctime_command(self):
	try:
	    logging.info("Validating synctime command output for proper messages when offset is more")
	    child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
	    child.logfile=sys.stdout
	    child.sendline('date')
	    child.expect("#")
	    date=str(config.date)
	    child.sendline('date --set='+'"'+date+'"')
	    child.sendline('exit')
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
	    #pdb.set_trace()
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    child.expect('[Default: None]')
	    child.sendline(config.external_server_ip)
	    sleep(5)
	    child.expect(':')
	    child.sendline('n')
	    child.expect('Maintenance Mode >')
	    output = child.before
	    print ('my output',output)
	    output1 = re.findall("\d+\.\d+",output)
	    offset=output1[-1]
	    if float(offset) > 3:
		print("offset value is greater than 3 seconds")
		if "The adjustment made to the system time will cause the product to restart." in output:
		    logging.info("Notification message that offset is more and product needs restart is displayed")
		    assert True
		else:
		    logging.info("Notification message that offset is more and product needs restart is not displayed")
		    assert False
	    else:
		logging.info("offset value is less than 3")
		print ("offset value is",offset)
	except Exception as error_message:
	    logging.info("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(120)

    @pytest.mark.run(order=5)
    def test_05_validating_synctime_command(self):
	try:
	    logging.info("Validating synctime command output for invalid IP address")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    child.expect('[Default: None]')
	    child.sendline('10..3.10')
	    sleep(5)
	    child.expect(':')
	    child.sendline('\n')
	    sleep(5)
	    child.expect(':')
	    child.sendline('n')
	    child.expect(':')
	    child.sendline('n')
	    child.expect('Maintenance Mode >')
	    output = child.before
	    print ('my output',output)
	    if "is not a valid IP address" in output:
		print (output, "IP is not valid")
		logging.info("Proper invalid IP address message is displaying")
		assert True
	    else:
		logging.error("Message is not displaying properly")
		assert False
	except Exception as error_message:
	    logging.info("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)

    @pytest.mark.run(order=6)
    def test_06_start_ntp_service_and_add_ntpserver_master(self):
	get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=ntp_setting',grid_vip=config.grid_vip)
        get_ref = json.loads(get_ref)[0]['_ref']
        data={"ntp_setting":{"enable_ntp": True,"ntp_servers": [{"address": config.external_server_ip,"burst": True,"preferred": True}]}}
        response = ib_NIOS.wapi_request('PUT', ref=get_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member?_return_fields=ntp_setting", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            data={"ntp_setting":{"enable_ntp": True,"ntp_servers": [{"address": config.external_server_ip,"burst": True,"preferred": True}]}}
            response = ib_NIOS.wapi_request('PUT',ref=ref['_ref'],fields=json.dumps(data), grid_vip=config.grid_vip)
            print("Test Case 6 Execution Completed")
            assert True
	sleep(30)
	if prod_status(config.grid_vip):
		logging.info("system is avaiable for testing")
		assert True
	else:
		logging.info("system is still taking restart")
		assert False
		sleep(100)
	sleep(120)
	
    @pytest.mark.run(order=7)
    def test_07_validate_ip_address_added_master(self):
		print("Validating if NTP ENABLED on master")
		request = ib_NIOS.wapi_request('GET', object_type="member",grid_vip=config.grid_vip)
		request = json.loads(request)
		print(request)
		#pdb.set_trace()
		#for i in request:
		ref=request[0]
		request_ref = ref['_ref']
		print(request_ref)
		res = ib_NIOS.wapi_request('GET', object_type=request_ref, params='?_return_fields=ntp_setting',grid_vip=config.grid_vip)
		res = json.loads(res)	
		res_address = res['ntp_setting']['ntp_servers']
		print(res_address)
		ip_address=res_address[-1]['address']
		print(ip_address)
		if ip_address == config.external_server_ip:
			print("IP address is added")
			assert True
		else:
			print("IP address is not added")
			assert False
		print("TestCase 7 executed successfully")

    @pytest.mark.run(order=8)
    def test_08_start_ntp_service_and_add_ntpserver_on_member(self):
	get_ref = ib_NIOS.wapi_request('GET', object_type='member?_return_fields=ntp_setting', grid_vip=config.grid_vip)
	#pdb.set_trace()
        get_ref = json.loads(get_ref)[1]['_ref']
        data={"ntp_setting":{"enable_ntp": True,"ntp_servers": [{"address": config.external_server_ip1,"burst": True,"preferred": True},{"address": config.external_server_ip2,"burst": True,"preferred": False},{"address": config.external_server_ip3,"burst": True,"preferred": False}]}}
        response = ib_NIOS.wapi_request('PUT', ref=get_ref, fields=json.dumps(data))
        print(response)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member?_return_fields=ntp_setting", grid_vip=config.grid_vip)
        for ref in json.loads(get_ref):
            data={"ntp_setting":{"enable_ntp": True}}
            response = ib_NIOS.wapi_request('PUT',ref=ref['_ref'],fields=json.dumps(data))
            print("Test Case 8 Execution Completed")
            assert True
	sleep(30)
	if prod_status(config.grid_vip):
		logging.info("system is avaiable for testing")
		assert True
	else:
		logging.info("system is still taking restart")
		assert False
		sleep(100)

    @pytest.mark.run(order=9)
    def test_09_validate_ip_address_added_member(self):
		print("Validating if NTP ENABLED on master")
		request = ib_NIOS.wapi_request('GET', object_type="member",grid_vip=config.grid_vip)
		request = json.loads(request)
		print(request)
		#pdb.set_trace()
		#for i in request:
		ref=request[1]
		request_ref = ref['_ref']
		print(request_ref)
		res = ib_NIOS.wapi_request('GET', object_type=request_ref, params='?_return_fields=ntp_setting')
		res = json.loads(res)	
		res_address = res['ntp_setting']['ntp_servers']
		print(res_address)
		ip_address1=res_address[0]['address']
		ip_address2=res_address[1]['address']
		ip_address3=res_address[2]['address']
		print(ip_address1,ip_address2,ip_address3)
		if ip_address1 == config.external_server_ip1 and ip_address2== config.external_server_ip2 and ip_address3== config.external_server_ip3 :
			print("IP address is added")
			assert True
		else:
			print("IP address is not added")
			assert False
		print("TestCase 9 executed successfully")




    @pytest.mark.run(order=10)
    def test_10_validating_synctime_command_on_member(self):
	try:
	    logging.info("Validating synctime command output for invalid IP address")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #child.expect("Do you want to continue ? (y or n): ")
	    child.sendline('n')
	    child.expect('Maintenance Mode >')
	    output=child.before
	    print ("output is", output)
	    if "It is recommended to sync grid manager with external server first." in output:
		logging.info("Message for member grid is displaying properly")
		assert True
	    else:
		logging.error("Message for member grid is not displaying properly")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)
		
    @pytest.mark.run(order=11)
    def test_11_validating_synctime_command_on_member(self):
	try:
	    logging.info("Validating synctime command output for valid messages on member")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #child.expect("Do you want to continue ? (y or n): ")
	    child.sendline('y')
	    child.expect(':')
	    child.sendline(config.server_ip1)
	    child.sendline('\n')
	    sleep(5)
	    child.expect('Maintenance Mode >')
	    output=child.before
	    print ("output is", output)
	    if "VPN IP Address of NTP Server in Grid:" in output:
		print ("output is", output)
		logging.info("VPN address messages are displaying through synctime command")
		assert True
	    else:
		logging.error("VPN address messages are not displaying through synctime command")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)


    @pytest.mark.run(order=12)
    def test_12_validating_synctime_command_on_member(self):
	try:
	    logging.info("Validating synctime command output for valid messages on member")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #child.expect("Do you want to continue ? (y or n): ")
	    child.sendline('y')
	    child.expect(':')
	    child.sendline(config.server_ip1)
	    child.sendline('\n')
	    sleep(5)
	    child.expect('Maintenance Mode >')
	    output=child.before
	    print ("output is", output)
	    if "If grid manager is not excluded as an NTP Server, please use above VPN IP address!" in output:
		print ("output is", output)
		logging.info("Notification to use grid manager VPN ip as NTP server is displayed")
		assert True
	    else:
		logging.error("Notification to use grid manager VPN ip as NTP server is not displayed")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)

    @pytest.mark.run(order=13)
    def test_13_validating_synctime_command_on_member(self):
	try:
	    logging.info("Validating synctime command output for valid messages on member")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
	    #pdb.set_trace()
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #child.expect("Do you want to continue ? (y or n): ")
	    #child.sendline('y')
	    child.expect(':')
	    output2=child.before
	    output2=output2.replace('\n',' ').replace('\r',' ')
	    #child.sendline(config.server_ip1)
	    #child.sendline('\n')
	    #sleep(5)
	    #child.expect('Maintenance Mode >')
	    #output=child.before
	    #output1=child.after
	    print ("output is", output2)
	    
	    if " synctime  Configured external NTP servers" in output2:
		print ("output is", output2)
		logging.info("NTP server list messages are displaying through synctime command")
		assert True
	    else:
		logging.error("NTP server list messages are not displaying through synctime command")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)

    @pytest.mark.run(order=14)
    def test_14_validating_synctime_command_on_member(self):
	try:
	    logging.info("Validating synctime command output for valid messages on member")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #child.expect("Do you want to continue ? (y or n): ")
	    child.sendline('y')
	    child.expect(':')
	    child.sendline(config.server_ip1)
	    child.sendline('\n')
	    sleep(5)
	    child.expect('Maintenance Mode >')
	    output=child.before
	    print ("output is", output)
	    if "The server is not a part of the list of configured NTP servers. If one of the listed configured NTP servers is reachable, please use that NTP server." in output:
		print ("output is", output)
		logging.info("NTP server not part of list message is displayed")
		assert True
	    else:
		logging.error("NTP server not part of list message is not displayed")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)


    

    @pytest.mark.run(order=15)
    def test_15_validating_synctime_command_on_master(self):
	try:
	    logging.info("Validating synctime command output for valid messages on master")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #child.expect("Do you want to continue ? (y or n): ")
	    child.sendline('y')
	    child.expect(':')
	    child.sendline(config.server_ip1)
	    child.sendline('\n')
	    sleep(5)
	    child.expect('Maintenance Mode >')
	    output=child.before
	    print ("output is", output)
	    if "The server is not a part of the list of configured NTP servers. If one of the listed configured NTP servers is reachable, please use that NTP server." in output:
		print ("output is", output)
		logging.info("NTP server not part of list message is displayed")
		assert True
	    else:
		logging.error("NTP server not part of list message is not displayed")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)

    @pytest.mark.run(order=16)
    def test_16_validating_synctime_command_on_member(self):
	try:
	    logging.info("Validating synctime command output for valid messages on member")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #child.expect("Do you want to continue ? (y or n): ")
	    child.sendline('y')
	    child.expect(':')
	    child.sendline(config.server_ip1)
	    child.sendline('\n')
	    sleep(5)
	    child.expect('Maintenance Mode >')
	    output=child.before
	    print ("output is", output)
	    if "Check the connection, network firewalls, to make sure the NTP server is reachable." in output:
		print ("output is", output)
		logging.info("Warning messages are displayed")
		assert True
	    else:
		logging.error("Warning messages are not displayed")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)


    @pytest.mark.run(order=17)
    def test_17_validating_synctime_command_on_member_for_restart(self):
	try:
	    logging.info("Validating synctime command output for restart to start synchronising")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
	    child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
	    #pdb.set_trace()
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #child.expect("Do you want to continue ? (y or n): ")
	    child.sendline('y')
	    child.expect(':')
	    child.sendline(config.external_server_ip)
	    child.sendline('\n')
	    sleep(5)
	    #child.expect(':')
	    child.sendline('y')
	    sleep(5)
	    child.expect('Maintenance Mode > ')
	    sleep(5)
	    child.expect('$')
	    output=child.before
	    #print ("output is", output)
	    status= ("Connection to %s closed." % config.grid_member1_vip)
	    sleep(10)
	    if prod_status(config.grid_member1_vip):
		print("system can be used for further testing")
	    else:
		print("system cannot be used for further testing")
	    if status in output:
		print ("output is", status)
		logging.info("Product is taking restart for synctime command")
		assert True
	    else:
		logging.error("Product retsart is not initiated")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(120)

    @pytest.mark.run(order=18)
    def test_18_validating_synctime_command_on_member(self):
	try:
	    logging.info("Validating synctime command output for valid messages on member")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #child.expect("Do you want to continue ? (y or n): ")
	    child.sendline('y')
	    child.expect(':')
	    child.sendline(config.server_ip1)
	    child.sendline('\n')
	    sleep(5)
	    child.expect('Maintenance Mode >')
	    output=child.before
	    print ("output is", output)
	    if "Last NTP server used to synchronize the time through the synctime command is:" in output:
		print ("output is", output)
		logging.info("Last server synced ip list is displayed")
		assert True
	    else:
		logging.error("Last server synced ip list is displayed")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(30)


    @pytest.mark.run(order=19)
    def test_19_validating_synctime_command_on_master_for_restart(self):
	try:
	    logging.info("Validating synctime command output for restart to start synchronising")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
	    child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #child.expect("Do you want to continue ? (y or n): ")
	    child.sendline('y')
	    child.expect(':')
	    child.sendline(config.external_server_ip)
	    child.sendline('\n')
	    sleep(5)
	    #child.expect(':')
	    child.sendline('y')
	    sleep(5)
	    child.expect('Maintenance Mode > ')
	    sleep(5)
	    child.expect('$')
	    output=child.before
	    #print ("output is", output)
	    status= ("Connection to %s closed." % config.grid_vip)
	    sleep(10)
	    if prod_status(config.grid_vip):
		print("system can be used for further testing")
	    else:
		print("system cannot be used for further testing")
	    if status in output:
		print ("output is", status)
		logging.info("Product is taking restart for synctime command")
		assert True
	    else:
		logging.error("Product restart is not initiated")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(200)


    @pytest.mark.run(order=20)
    def test_20_validating_synctime_command_on_master(self):
	try:
	    logging.info("Validating synctime command output for valid messages on master")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #child.expect("Do you want to continue ? (y or n): ")
	    child.sendline('y')
	    child.expect(':')
	    child.sendline(config.server_ip1)
	    child.sendline('\n')
	    sleep(5)
	    child.expect('Maintenance Mode >')
	    output=child.before
	    print ("output is", output)
	    if "Check the connection, network firewalls, to make sure the NTP server is reachable." in output:
		print ("output is", output)
		logging.info("Warning messages are displayed on master")
		assert True
	    else:
		logging.error("Warning messages are not displayed on master")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)


    @pytest.mark.run(order=21)
    def test_21_validating_synctime_command_on_member_for_VPN_address(self):
	try:
	    logging.info("Validating synctime command output to get VPN address")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
	    child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #child.expect("Do you want to continue ? (y or n): ")
	    child.sendline('y')
	    child.expect(':')
	    child.sendline(config.server_ip1)
	    child.sendline('\n')
	    sleep(5)
	    child.expect('Maintenance Mode >')
	    output=child.before
	    print ("output is", output)
	    #pdb.set_trace()
	    #output= re.search('this system is(.*)seconds.',output)
            #result1 = output.group(0)
            #print("my result is",result1)
	    #output=output.replace('\n','').replace('\r','').replace(' ','').replace(':','').replace('=','').replace('\t','')
	    #output1= re.search('yVPNIPAddressofNTPServerinGrid(.*)IfgridmanagerisnotexcludedasanNTPServe',output)
	    #print (output1)
	    ip= re.findall(r'[0-9]+(?:\.[0-9]+){3}', output)
	    print ("VPN address suggested to use is %s" %ip[0])
	    logging.info("VPN address suggested to use is %s" %ip[0])
	    assert True
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)

    

    @pytest.mark.run(order=22)
    def test_22_validating_synctime_command_on_master_get_configured_ip_address(self):
	try:
	    logging.info("Get the configured IP addresses")
	    sleep(20)
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
	    child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #child.expect("Do you want to continue ? (y or n): ")
	    child.sendline('y')
	    child.expect(':')
	    child.sendline(config.server_ip1)
	    child.sendline('\n')
	    sleep(5)
	    child.expect('Maintenance Mode >')
	    output=child.before
	    print ("output is", output)
	    ip= re.findall(r'[0-9]+(?:\.[0-9]+){3}', output)
	    print ("configured ip addresses are %s,%s" %(ip[0],ip[1]))
	    logging.info("configured ip addresses to use are %s" %ip[0])
	    assert True
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(30)
    
    @pytest.mark.run(order=23)
    def test_23_validate_synctime_with_grid_master_ip(self):
	try:
	    logging.info("Validating synctime command output sync with grid master")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    child.expect(':')
	    child.sendline('y')
	    output = child.before
	    print (output)
	    #child.sendline('\n')
	    #pdb.set_trace()
	    child.sendline(config.grid_vip)
	    child.sendline('\n')
	    sleep(5)
	    #child.expect(':')
	    child.sendline('y')
	    sleep(5)
	    child.expect('Maintenance Mode > ')
	    sleep(5)
	    child.expect('$')
	    output=child.before
	    #print ("output is", output)
	    status= ("Connection to %s closed." % config.grid_member1_vip)
	    sleep(120)
	    if prod_status(config.grid_member1_vip):
		print("system can be used for further testing")
	    else:
		print("system cannot be used for further testing")
	    if status in output:
		print ("output is", status)
		logging.info("Product is taking restart for synctime command and got sync with grid master")
		assert True
	    else:
		logging.error("Product restart is not initiated for sync with grid master")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(120)

    
    @pytest.mark.run(order=24)
    def test_24_validating_synctime_command_on_master_for_last_synched_address(self):
	try:
	    logging.info("Validating synctime command to get last synched ip address")
	    sleep(240)
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
	    child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #child.expect("Do you want to continue ? (y or n): ")
	    child.sendline('y')
	    child.expect(':')
	    child.sendline(config.server_ip1)
	    child.sendline('\n')
	    sleep(5)
	    child.expect('Maintenance Mode >')
	    output=child.before
	    print ("output is", output)
	    ip= re.findall(r'[0-9]+(?:\.[0-9]+){3}', output)
	    print ("Last synched ip addresses are %s" %ip[1])
	    logging.info("Last synched ip addresses to use are %s" %ip[1])
	    assert True
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)


    @pytest.mark.run(order=25)
    def test_25_validating_synctime_command_on_master_sync_external_ip(self):
	try:
	    logging.info("Validating synctime command output for synctime with external ip")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
	    child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #child.expect("Do you want to continue ? (y or n): ")
	    child.sendline('y')
	    child.expect(':')
	    child.sendline(config.external_server_ip)
	    child.sendline('\n')
	    sleep(5)
	    child.sendline('y')
	    sleep(5)
	    child.expect('Maintenance Mode > ')
	    sleep(5)
	    child.expect('$')
	    output=child.before
	    if prod_status(config.grid_vip):
		print("system can be used for further testing")
	        sleep(180)
	    else:
		print("system cannot be used for further testing")
	    print ("Last synched ip address is 10.195.3.10" )
	    logging.info("Last synched ip address is 10.195.3.10")
	    assert True
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(120)


    @pytest.mark.run(order=26)
    def test_26_validating_synctime_command_on_master_for_last_synched_address(self):
	try:
	    logging.info("Validating synctime command output for last synched ip address")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
	    child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #child.expect("Do you want to continue ? (y or n): ")
	    #child.sendline('y')
	    child.expect(':')
	    child.sendline(config.server_ip1)
	    child.sendline('\n')
	    sleep(5)
	    child.expect('Maintenance Mode >')
	    output=child.before
	    print ("output is", output)
	    ip= re.findall(r'[0-9]+(?:\.[0-9]+){3}', output)
	    if ip[1] == config.external_server_ip:
	    	print ("Last synched ip addresses are %s" %ip[1])
	    	logging.info("Last synched ip addresses to use are %s" %ip[1])
	    	assert True
	    else:
		logging.error("IP address is not displayed")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)


    @pytest.mark.run(order=27)
    def test_27_validating_synctime_command_on_master_for_default_address(self):
	try:
	    logging.info("Validating synctime command output for default address")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
	    child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #child.expect("Do you want to continue ? (y or n): ")
	    child.sendline('y')
	    child.expect(':')
	    child.sendline(config.server_ip1)
	    child.sendline('\n')
	    sleep(5)
	    child.expect('Maintenance Mode >')
	    output=child.before
	    print ("output is", output)
	    #pdb.set_trace()
	    ip= re.findall(r'[0-9]+(?:\.[0-9]+){3}', output)
	    print(ip)
	    if ip[0] == config.external_server_ip:
	    	print ("Configured ip addresses list is %s" %ip[1])
	    	logging.info("Default ip addresses to use are %s which is same as external ip address" %ip[1])
	    	assert True
	    else:
		logging.error("IP address is not displayed")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)


    @pytest.mark.run(order=28)
    def test_28_validating_synctime_command_on_master_for_list_address(self):
	try:
	    logging.info("Validating synctime command output for list of address")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
	    child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #child.expect("Do you want to continue ? (y or n): ")
	    child.sendline('y')
	    child.expect(':')
	    child.sendline(config.server_ip1)
	    child.sendline('\n')
	    sleep(5)
	    child.expect('Maintenance Mode >')
	    output=child.before
	    print ("output is", output)
	    ip= re.findall(r'[0-9]+(?:\.[0-9]+){3}', output)
	    if ip[1] == config.external_server_ip:
	    	print ("Default ip addresses are %s" %ip[1])
	    	logging.info("Default ip addresses to use are %s which is same as configured at UI" %ip[0])
	    	assert True
	    else:
		logging.error("List is not displayed")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(30)


    @pytest.mark.run(order=29)
    def test_29_validating_synctime_command_infoblox_log(self):
	try:
	    logging.info("Validating synctime command output in infoblox log")
	    logging.info("Starting infoblox logs")
	    log("start","/infoblox/var/infoblox.log",config.grid_vip)
	    child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
	    child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
	    child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    child.expect(':')
	    #log("start","/infoblox/var/infoblox.log",config.grid_vip)
	    child.sendline(config.external_server_ip)
	    child.sendline('\n')
	    sleep(5)
	    child.expect(':')
	    child.sendline('n')
	    #pdb.set_trace()
	    child.expect('Maintenance Mode >')
	    output = child.before
	    print ('my output',output)
	    output1= re.search('this system is(.*)seconds',output)
            result1 = output1.group(0)
	    offset = result1.replace("this system is","").replace("seconds","").replace(" ","")
            print("my output is",result1)
	    log("stop","/infoblox/var/infoblox.log",config.grid_vip)
	    lookfor="Offset between ntp server, " +config.external_server_ip +", and me = " +offset
	    print(lookfor)
	    display_offset=logv(lookfor,"/infoblox/var/infoblox.log",config.grid_vip)
	    if display_offset !=None:
		print(display_offset)
		logging.info("offset value is getting logged at infoblox log")
		assert True
	    else:
		logging.error("offset value is not getting logged at infoblox log")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    #child.sendline('exit')
	    #child.close()
	    sleep(30)
	    
    @pytest.mark.run(order=30)
    def test_30_validating_synctime_command_infoblox_log_when_offset_cannot_calculate(self):
	try:
	    logging.info("Validating synctime command output in infoblox log when offset cannot calculate")
	    logging.info("Starting infoblox logs")
	    log("start","/infoblox/var/infoblox.log",config.grid_vip)
	    child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
	    child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
	    child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    child.expect(':')
	    #log("start","/infoblox/var/infoblox.log",config.grid_vip)
	    child.sendline(config.server_ip1)
	    child.sendline('\n')
	    sleep(5)
	    child.expect(':')
	    child.sendline('n')
	    child.expect('Maintenance Mode >')
	    output = child.before
	    print ('my output',output)
	    output1 = re.findall("\d+\.\d+",output)
	    offset=output1[-1]
	    ip= re.findall(r'[0-9]+(?:\.[0-9]+){3}', output)
	    ip=ip[-1]
	    sleep(10)
	    log("stop","/infoblox/var/infoblox.log",config.grid_vip)
	    lookfor=".*Unknown response.*"
	    display_offset=logv(lookfor,"/infoblox/var/infoblox.log",config.grid_vip)
	    if display_offset !=None:
		print(display_offset)
		logging.info("offset value cannot calculate when IP address is not valid")
		assert True
	    else:
		logging.error("offset value cannot calculate message is not displayed")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    #child.sendline('exit')
	    #child.close()
	    sleep(120)
    

    @pytest.mark.run(order=31)
    def test_31_create_user_group(self):
        logging.info("Create a non-super-user group")
        data={"name":"test1","access_method": ["API","CLI"]}
        response = ib_NIOS.wapi_request('POST',object_type="admingroup",fields=json.dumps(data),grid_vip=config.grid_vip)
        print("#######################",response)
        logging.info(response)
        logging.info("============================")
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Group 'test1' is created")
	sleep(20)

    @pytest.mark.run(order=32)
    def test_32_validate_created_user_group(self):
	logging.info("Validate Created a non-super-user group")
	#pdb.set_trace()
	get_group=ib_NIOS.wapi_request('GET',object_type="admingroup",params="?_return_fields=name",grid_vip=config.grid_vip)
	print(get_group)
	res = json.loads(get_group)
        logging.info(res)
	res=res[-1]
	res=list(res.values())
	for i in res:
	    if i =="test1":
		logging.info("User group has been created")
	logging.info("Test Case 29 Execution Completed")
		
	

    @pytest.mark.run(order=33)
    def test_33_updating_access_user_group(self):
        logging.info("Create a non-super-user group")
	#pdb.set_trace()
        data={"admin_set_commands": {"set_maintenancemode": True}}
	get_ref =ib_NIOS.wapi_request('GET',object_type="admingroup",params="?_return_fields=admin_set_commands",grid_vip=config.grid_vip)
	logging.info(get_ref)
	res = json.loads(get_ref)
	ref1 = json.loads(get_ref)[-1]['_ref']
	response = ib_NIOS.wapi_request('PUT',object_type=ref1,fields=json.dumps(data))
        print("#######################",response)
        logging.info(response)
        logging.info("============================")
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Group 'test1' is modified with maintenancemode access ")


    @pytest.mark.run(order=34)
    def test_34_updating_access_user_group(self):
        logging.info("Create a non-super-user group")
	#pdb.set_trace()
        data={"admin_toplevel_commands": {"iostat": False,"netstat": False,"ps": False,"resilver": False,"restart_product": False,"rndc": False,"saml_restart": False,"sar": False,"scrape": False,"synctime": True,"tcpdump": False,"vmstat": False}}
	get_ref =ib_NIOS.wapi_request('GET',object_type="admingroup",params="?_return_fields=admin_toplevel_commands",grid_vip=config.grid_vip)
	logging.info(get_ref)
	res = json.loads(get_ref)
	ref1 = json.loads(get_ref)[-1]['_ref']
	response = ib_NIOS.wapi_request('PUT',object_type=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
        print("#######################",response)
        logging.info(response)
        logging.info("============================")
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Group 'test1' is modified with synctime access")
	sleep(20)

    @pytest.mark.run(order=35)
    def test_35_create_nonsuperuser_user(self):
        logging.info("Create a non-super-user group")
        data = {"name":config.username1,"password":config.password,"admin_groups": ["test1"]}
        response = ib_NIOS.wapi_request('POST',object_type="adminuser",fields=json.dumps(data))
        print("#######################",response)
        logging.info(response)
        logging.info("============================")
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Non-super user 'sneha' is created")
	sleep(20)

    @pytest.mark.run(order=36)
    def test_36_validate_created_non_super_user(self):
	logging.info("Validate Created a non-super-user")
	#pdb.set_trace()
	get_user=ib_NIOS.wapi_request('GET',object_type="adminuser",params="?_return_fields=name",grid_vip=config.grid_vip)
	print(get_user)
	res = json.loads(get_user)
        logging.info(res)
	res=res[-1]
	res=list(res.values())
	for i in res:
	    if i ==config.username1:
		logging.info("non-super User has been created")
	logging.info("Test Case 32 Execution Completed")


    @pytest.mark.run(order=37)
    def test_37_validating_synctime_command_non_super_user(self):
	try:
	    logging.info("Validating synctime command is present in list when logged in with non-supe user")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no sneha@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('help')
	    child.expect('Maintenance Mode >')
	    output = child.before
	    print (output)
	    if "synctime" in output:
	        logging.info("synctime command is present in Maintenance Mode command list")
	        assert True
	    else:
		logging.error("synctime command is not present in Maintenance Mode command list")
		assert False
	except Exception as error_message:
	    logging.info("synctime command is not present in Maintenance Mode command list")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)


    @pytest.mark.run(order=38)
    def test_38_validating_synctime_command_offset_value_non_super_user(self):
	try:
	    logging.info("Validating synctime command output for offset value for non-super user")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no sneha@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    child.expect('[Default: None]')
	    child.sendline(config.external_server_ip)
	    #child.expect(':')
	    #child.sendline('\r')
	    sleep(5)
	    child.expect(':')
	    child.sendline('n')
	    child.expect('Maintenance Mode >')
	    output = child.before
	    print ('my output',output)
	    #output= 
	    #output=output.replace('\n','').replace('\r','').replace(' ','').replace(':','').replace(']','').replace('(','').replace(')','').replace('?','')
	    output1 = re.findall("\d+\.\d+",output)
	    offset=output1[-1]	    
	    print (offset)
	    if offset:
	        logging.info("synctime command is displaying the offset values between systems")
	        assert True
	    else:
		logging.error("synctime command is not displaying the offset values between systems")
		assert False
	except Exception as error_message:
	    logging.info("synctime command is not displaying the offset values between systems")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)


    @pytest.mark.run(order=39)
    def test_39_validating_synctime_command_on_master_for_restart_non_super_user(self):
	try:
	    logging.info("Validating synctime command output for restart with non-super user")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no sneha@'+config.grid_vip)
	    child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #child.expect("Do you want to continue ? (y or n): ")
	    #child.sendline('y')
	    child.expect(':')
	    child.sendline(config.external_server_ip)
	    child.sendline('\n')
	    sleep(5)
	    #child.expect(':')
	    child.sendline('y')
	    sleep(5)
	    child.expect('Maintenance Mode > ')
	    sleep(5)
	    child.expect('$')
	    output=child.before
	    #print ("output is", output)
	    status= ("Connection to %s closed." % config.grid_vip)
	    if prod_status(config.grid_vip):
		print("system can be used for further testing")
	    else:
		print("system cannot be used for further testing")
	    if status in output:
		print ("output is", status)
		logging.info("Product is taking restart for synctime command")
		assert True
	    else:
		logging.error("Product is not taking restart")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(120)

    @pytest.mark.run(order=40)
    def test_40_updating_access_user_group(self):
        logging.info("Create a non-super-user group")
	#pdb.set_trace()
        data={"admin_toplevel_commands": {"iostat": False,"netstat": False,"ps": False,"resilver": False,"restart_product": False,"rndc": False,"saml_restart": False,"sar": False,"scrape": False,"synctime": False,"tcpdump": False,"vmstat": False}}
	get_ref =ib_NIOS.wapi_request('GET',object_type="admingroup",params="?_return_fields=admin_toplevel_commands",grid_vip=config.grid_vip)
	logging.info(get_ref)
	res = json.loads(get_ref)
	ref1 = json.loads(get_ref)[-1]['_ref']
	response = ib_NIOS.wapi_request('PUT',object_type=ref1,fields=json.dumps(data),grid_vip=config.grid_vip)
        print("#######################",response)
        logging.info(response)
        logging.info("============================")
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Group 'test1' is modified with synctime access")
	sleep(20)

    @pytest.mark.run(order=41)
    def test_41_validating_synctime_command_on_master_for_restart_non_super_user(self):
	try:
	    logging.info("Validating synctime command output for restart with non-super user")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no sneha@'+config.grid_vip)
	    child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    child.expect('Maintenance Mode >')
	    output=child.before
	    print(output)
	    #pdb.set_trace()
	    output=output.replace('\n','').replace('\r','')
	    if "Error: The user does not have sufficient privileges to run this command" in output:
		logging.info("By chaning permission synctime is not working in non-super user")
		assert True
	    else:
		logging.error("Synctime is working even when permission is not given")
	except Exception as error_message:
	    logging.info("synctime command is not present in Maintenance Mode command list")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(30)

    @pytest.mark.run(order=42)
    def test_42_validating_synctime_command_v6_grid(self):
	try:
	    logging.info("Validating synctime command is present in list for v6 grid")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip6)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('help')
	    child.expect('Maintenance Mode >')
	    output = child.before
	    print (output)
	    if "synctime" in output:
	        logging.info("synctime command is present in Maintenance Mode command list for v6 grid")
	        assert True
	    else:
		logging.error("synctime command is not present in Maintenance Mode command list")
		assert False
	except Exception as error_message:
	    logging.info("synctime command is not present in Maintenance Mode command list")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)

    @pytest.mark.run(order=43)
    def test_43_validating_synctime_command_for_ipv6_address(self):
	try:
	    logging.info("Validating synctime command output for ipv6 address")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip6)
	    child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
	    #pdb.set_trace()
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
    	    child.expect(':')
	    child.sendline(config.grid_ip6)
	    child.sendline('\n')
	    sleep(5)
  	    child.sendline('y')
	    sleep(5)
	    child.expect('Maintenance Mode > ')
	    sleep(5)
	    child.expect('$')
	    output=child.before
	    output=output.replace("\r","")
	    output=output.upper()
	    #print ("output is", output)
	    status= ("CONNECTION TO %s CLOSED." % config.grid_vip6)
	    
	    if status in output:
		print ("output is", status)
		logging.info("Product is taking restart for synctime command for ipv6 grid")
		assert True
	    else:
		logging.error("Product is not taking restart")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(120)

    @pytest.mark.run(order=44)
    def test_44_validating_synctime_command_on_v6_grid(self):
	try:
	    logging.info("Validating synctime command output for last synched ip on v6 grid")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip6)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            #output = child.before
            #print ('my output',output)
	    #pdb.set_trace()
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #child.expect("Do you want to continue ? (y or n): ")
	    child.sendline('y')
	    child.expect(':')
	    output=child.before
	    output=output.replace('\n','').replace('\r','')
	    #child.sendline(config.server_ip1)
	    #child.sendline('\n')
	    #sleep(5)
	    #child.expect('Maintenance Mode >')
	    #output=child.before
	    print ("output is", output)
	    if " synctimeConfigured external NTP servers" in output:
		print ("output is", output)
		logging.info("Last server synced ip list is displayed in v6 grid")
		assert True
	    else:
		logging.error("Last server synced ip list is displayed in v6 grid")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(30)


    @pytest.mark.run(order=45)
    def test_45_validating_synctime_command(self):
	try:
	    logging.info("Validating synctime command output for offset value for v6 grid")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip6)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #pdb.set_trace()
	    child.expect(':')
	    child.sendline(config.grid_ip6)
	    #child.expect(':')
	    #child.sendline('\r')
	    sleep(5)
	    child.expect(':')
	    child.sendline('n')
	    child.expect('Maintenance Mode >')
	    output = child.before
	    print ('my output',output)
	    output1 = re.findall("\d+\.\d+",output)
	    offset=output1[-1]	    
	    print (offset)
	    if offset:
	        logging.info("synctime command is displaying the offset values between systems with ipv6 grid")
	        assert True
	    else:
		logging.error("synctime command is not displaying the offset values between systems with ipv6 grid")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not displaying the offset values between systems")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)
    
    @pytest.mark.run(order=46)
    def test_46_validating_synctime_command_for_ipv6_address(self):
	try:
	    logging.info("Validating synctime command output for invalid ipv6 address")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip6)
	    child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
	    #pdb.set_trace()
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
    	    child.expect(':')
	    child.sendline('-1b::2f')
	    sleep(5)
	    child.expect(':')
	    child.sendline('\n')
	    sleep(5)
	    child.expect(':')
	    child.sendline('n')
	    child.expect(':')
	    child.sendline('n')
	    child.expect('Maintenance Mode >')
	    output = child.before
	    print ('my output',output)
	    if "is not a valid IP address" in output:
		print (output, "IP is not valid")
		logging.info("Proper invalid IP address message is displaying")
		assert True
	    else:
		logging.error("Message is not displaying properly")
		assert False
	except Exception as error_message:
	    logging.info("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)

    @pytest.mark.run(order=47)
    def test_47_start_ntp_service_and_add_ntpserver(self):
	get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=ntp_setting',grid_vip=config.grid_vip2)
        get_ref = json.loads(get_ref)[0]['_ref']
        data={"ntp_setting":{"enable_ntp": True,"ntp_servers": [{"address": "10.120.3.10","burst": True,"preferred": True},{"address": "10.210.3.10","burst": True,"preferred": False}]}}
        response = ib_NIOS.wapi_request('PUT', ref=get_ref, fields=json.dumps(data),grid_vip=config.grid_vip2)
        print(response)
        get_ref = ib_NIOS.wapi_request('GET', object_type="member?_return_fields=ntp_setting", grid_vip=config.grid_vip2)
        for ref in json.loads(get_ref):
            data={"ntp_setting":{"enable_ntp": True,"ntp_servers": [{"address": "10.195.3.10","burst": True,"preferred": True}]}}
            response = ib_NIOS.wapi_request('PUT',ref=ref['_ref'],fields=json.dumps(data), grid_vip=config.grid_vip2)
            print("Test Case 71 Execution Completed")
            assert True
	sleep(30)
	if prod_status(config.grid_vip2):
		logging.info("system is avaiable for testing")
		assert True
	else:
		logging.info("system is still taking restart")
		assert False
		sleep(100)


    @pytest.mark.run(order=48)
    def test_48_start_dns_service(self):
        '''Add DNS Resolver'''
        logging.info("Add DNS Resolver 10.0.2.35")
        grid_ref = ib_NIOS.wapi_request('GET', object_type='grid')
        data = {"dns_resolver_setting":{"resolvers":["127.0.0.1","10.103.3.10"]}}
        response = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_ref)[0]['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip2)
        logging.info(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                logging.info("Failure: Adding DNS Resolver")
                assert False
        '''Start DNS Service '''
        member_ref=ib_NIOS.wapi_request('GET',object_type="member:dns",grid_vip=config.grid_vip2)
        member_ref=json.loads(member_ref)
        print (member_ref)
        print ("__________________________________")
        dns_ref=member_ref[0]['_ref']
        condition=ib_NIOS.wapi_request('GET',object_type=dns_ref+"?_return_fields=enable_dns",grid_vip=config.grid_vip2)
        data={"enable_dns": True}
        enable_dns_ref = ib_NIOS.wapi_request('PUT', ref=dns_ref, fields=json.dumps(data),grid_vip=config.grid_vip2)
        print (enable_dns_ref)
        print ("*************************************")
        #res=json.loads(enable_dns_ref)+"?_return_fields=enable_dns"

    @pytest.mark.run(order=49)
    def test_49_Validate_DNS_service_is_Enabled(self):
        logging.info("Validate DNs Service is enabled")
        get_response = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns",grid_vip=config.grid_vip2)
        logging.info(get_response)
	print(get_response)
        res = json.loads(get_response)
        logging.info(res)
        for i in res:
            logging.info("found")
            assert i["enable_dns"] == True
        logging.info("Test Case 49 Execution Completed")

    @pytest.mark.run(order=50)
    def test_50_start_TP_service(self):
        logging.info("start the TP service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection",grid_vip=config.grid_vip2)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        logging.info (ref1)
        data = {"enable_service": True}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_vip2)
        sleep(420)
        logging.info(response)
        logging.info("Test Case 38 Execution Completed")
	for i in range(2):
	    if prod_status(config.grid_vip2):
		print("system can be used for further testing")
	    else:
		print("system cannot be used for further testing")
		sleep(300)
 
    
    @pytest.mark.run(order=51)
    def test_51_Validate_TP_service_running(self):
        logging.info("Validate TP Service is enabled")
        response = ib_NIOS.wapi_request('GET', object_type="member:threatprotection",params="?_return_fields=enable_service",grid_vip=config.grid_vip2)
        logging.info(response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        logging.info("Started Threat protection services")
	    

    @pytest.mark.run(order=52)
    def test_52_download_auto_ruleset(self):
        logging.info("Modify_grid_threatprotection_object_for_download_ruleset")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatprotection", grid_vip=config.grid_vip2)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        logging.info (ref1)
        data = {"enable_auto_download": True}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip2)
        logging.info(response)
        logging.info("============================")
        logging.info (response)
        restart_services(config.grid_vip2)
        logging.info("Restart services")
        logging.info("Create_download_atp_rule_update_function_call_to_download_ruleset")
        response = ib_NIOS.wapi_request('POST',object_type="fileop",params="?_function=download_atp_rule_update", grid_vip=config.grid_vip2)
	sleep(300)

    @pytest.mark.run(order=53)
    def test_53_validate_synctime_ADP_active(self):
	try:
	    logging.info("Validating synctime command output for offset value")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip2)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #pdb.set_trace()
	    child.expect(':')
	    child.sendline(config.server_ip1)
	    child.sendline('\n')
	    sleep(10)
	    #child.expect('Maintenance Mode >')
	    child.sendline('n')
	    child.expect('Maintenance Mode >')
	    output = child.before
	    output=output.replace('\n','').replace('\r','').replace('\t','')
	    print ('my output',output)
	    if "ADP is running on the appliance and if NTP isn't configured on the node" and "we would recommend to run the node on monitoring-mode" and "before checking synctime between current-node and external-NTP-Server." in output:
		logging.info("ADP related messages are displaying")
	        assert True
	    else:
		logging.error("ADP related messages are not displaying")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not displaying the offset values between systems")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10) 

    @pytest.mark.run(order=54)
    def test_54_validate_synctime_ADP_active(self):
	try:
	    logging.info("Validating synctime command output when ADP is active and monitoring mode is on")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip2)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
	    child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('set adp monitor-mode on')
	    child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #pdb.set_trace()
	    child.expect(':')
	    child.sendline(config.external_server_ip)
	    child.sendline('\n')
	    sleep(10)
	    child.sendline('n')
	    child.expect('Maintenance Mode >')
	    output = child.before
	    if "The adjustment made to the system time will cause the product to restart." in output:
		print ("output is", output)
		logging.info("Synctime related messages are displaying")
		assert True
	    else:
		logging.error("Synctime related messages are not displaying")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)

    @pytest.mark.run(order=55)
    def test_55_validate_synctime_ADP_active(self):
	try:
	    logging.info("Validating synctime command output when ADP is active and monitoring mode is on")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip2)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
	    child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('set adp monitor-mode on')
	    child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #pdb.set_trace()
	    child.expect(':')
	    child.sendline(config.external_server_ip)
	    child.sendline('\n')
	    sleep(10)
	    child.sendline('y')
	    sleep(5)
	    child.expect('Maintenance Mode > ')
	    sleep(15)
	    child.expect('$')
	    output=child.before
	    status= ("Connection to %s closed." % config.grid_vip2)
	    if prod_status(config.grid_vip2):
		print("system can be used for further testing")
	    else:
		print("system cannot be used for further testing")
		sleep(400)
	    if status in output:
		print ("output is", status)
		logging.info("Product is taking restart for synctime command")
		assert True
	    else:
		logging.error("Product restart is not initiated")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(30)

    @pytest.mark.run(order=56)
    def test_56_validate_show_ntp_commad(self):
	try:
	    logging.info("Validating show ntp command to check NTP server configured")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
	    #pdb.set_trace()
            #child.sendline('\r')
	    child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('show ntp')
	    child.expect('Maintenance Mode >')
	    output=child.before
	    print(output)
	    ip= re.findall(r'[0-9]+(?:\.[0-9]+){3}', output)
	    print (ip)
	    print("configured ip are %s" %ip[0])
	    logging.info("show ntp command shows the ntp server ips configured")
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(30)


    @pytest.mark.run(order=57)
    def test_57_Make_Member_as_GMC_in_Admin_Local(self):
                logging.info("Making Member as GMC in Admin Local")
                grid_member=config.grid2_fqdn
                grid =  ib_NIOS.wapi_request('GET', object_type="member")
                ref = json.loads(grid)[1]['_ref']
                print("The reference of member is ",ref)
                data={"master_candidate": True}
		#pdb.set_trace()
                gmc = ib_NIOS.wapi_request('PUT',ref=ref,object_type ="member",fields=json.dumps(data))
        	print(gmc)
                print("The Member is made as GMC Successfully")
        	get_temp = ib_NIOS.wapi_request('GET', object_type="member",ref=ref,params="?_return_fields=master_candidate")
                print(get_temp)
                result = '"master_candidate": true'
                if result in get_temp:
                      assert True
                else:
                      assert False
                print(result)
        	print("\nTest Case 57 Executed Successfully")
        	sleep(500)
	
    @pytest.mark.run(order=58)
    def test_58_promote_member_as_master(self):
               logging.info("promote member as master")
               child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
               child.logfile=sys.stdout
               child.expect('password:')
               child.sendline('infoblox')
               child.expect('Infoblox >')
               child.sendline('set promote_master')
               child.expect('Do you want a delay between notification to grid members\? \(y or n\): ')
               child.sendline('y')
               child.expect(': ')
               child.sendline('30')
               #child.expect('Are you sure you want to do this\? \(y or n\): ')
               child.expect(': ')
               child.sendline('y')
               child.expect(': ')
               child.sendline('y')
               child.expect('Master promotion beginning on this member')
               #print(output)
               print("\nTest Case 58 Executed Successfully")
               sleep(700)

    @pytest.mark.run(order=59)
    def test_59_validating_synctime_command_on_new_member(self):
	try:
	    logging.info("Validating synctime command output on new member")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #child.expect("Do you want to continue ? (y or n): ")
	    child.sendline('n')
	    child.expect('Maintenance Mode >')
	    output=child.before
	    print ("output is", output)
	    if "It is recommended to sync grid manager with external server first." in output:
		logging.info("Message for member grid is displaying properly")
		print("After GMC promotion, synctime command works properly on new member")
		assert True
	    else:
		logging.error("Message for member grid is not displaying properly")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)
 
    @pytest.mark.run(order=60)
    def test_60_validating_synctime_command_on_new_master(self):
	try:
	    logging.info("Validating synctime command output for valid messages on new master")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
	    #pdb.set_trace()
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #child.expect("Do you want to continue ? (y or n): ")
	    #child.sendline('y')
	    child.expect(':')
	    output2=child.before
	    output2=output2.replace('\n',' ').replace('\r',' ')
	    #child.sendline(config.server_ip1)
	    #child.sendline('\n')
	    #sleep(5)
	    #child.expect('Maintenance Mode >')
	    #output=child.before
	    #output1=child.after
	    print ("output is", output2)
	    
	    if " synctime  Configured external NTP servers" in output2:
		print ("output is", output2)
		logging.info("NTP server list messages are displaying through synctime command")
		print("After GMC promotion, synctime command works properly on new master")
		assert True
	    else:
		logging.error("NTP server list messages are not displaying through synctime command")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
   	    child.close()
	    sleep(10)

    @pytest.mark.run(order=61)
    def test_61_synctime_command_different_offset_range(self):
	try:
	    logging.info("Check synctime command when 2 different NTP servers with more than 60 sec difference of time is given")
	    child= pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_member1_vip)
	    child.logfile=sys.stdout
	    date=str(config.date)
	    print(date)
	    child.sendline('date --set='+'"'+date+'"')
	    child.sendline('exit')
	    child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
	    child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #child.expect("Do you want to continue ? (y or n): ")
	    #child.sendline('y')
	    child.expect(':')
	    child.sendline(config.external_server_ip1)
	    child.sendline('\n')
	    sleep(5)
	    #child.expect(':')
	    child.sendline('y')
	    sleep(5)
	    child.expect('Maintenance Mode > ')
	    output=child.before
	    sleep(5)
	    child.expect('$')
	    print ('my output',output)
	    output1 = re.findall("\d+\.\d+",output)
	    offset=output1[-1]
	    print (float(offset))
	    sleep(120)
	    if (float(offset)) >3:
	    	status= ("Connection to %s closed." % config.grid_member1_vip)
	    	sleep(100)
	    logging.info("System is starting sync with external IP with greater offset value")	
	    if prod_status(config.grid_member1_vip):
	    	print("system can be used for further testing")   
	    else:
	    	print("system cannot be used for further testing")
		sleep(120)
	    logging.info("Product takes restart and gets synchronise with IP configured in list")
	    child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
	    child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #child.expect("Do you want to continue ? (y or n): ")
	    child.sendline('y')
	    child.expect(':')
	    child.sendline(config.server_ip1)
	    child.sendline('\n')
	    sleep(5)
	    child.expect('Maintenance Mode >')
	    output=child.before
	    print ("output is", output)
	    ip= re.findall(r'[0-9]+(?:\.[0-9]+){3}', output)
	    if ip[3] == config.external_server_ip1:
		logging.info("System is synched back with ip address present in list")
		assert True
	    else:
		logging.info("System is not synched back with ip address present in list")
		assert False

	    sleep(10)
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    sleep(120)

    

    @pytest.mark.run(order=62)
    def test_62_test_enable_fips_mode(self):
        logging.info("validate the fips mode is enabled ")
	#pdb.set_trace()
	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip2)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline("set fips_mode")
        child.expect(".*Enable FIPS mode?.*")
        child.sendline("y")
        child.expect(".*is this correct?.*")
        child.sendline("y")
        child.expect(".*Are you sure you want to continue.*")
        child.sendline("y")
	output = child.before
	print(output)
	child.sendline('exit')
	child.close()
	sleep(1200)
	for i in range(3):	
	    if prod_status(config.grid_vip2):
	        print("system can be used for further testing")
		sleep(120)
	    else:
	    	print("system cannot be used for further testing")
	    	sleep(1200)
	else:
	    sleep(900)

    @pytest.mark.run(order=63)
    def test_63_validate_fips_mode_enabled(self):
        logging.info("validate the fips mode is enabled ")
	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip2)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('show fips_mode')
	child.expect('Infoblox >')
	output=child.before
	if "Yes" in output:
		logging.info("fips mode is enabled")
		assert True
	else:
		logging.error("fips mode is not enabled")
		assert False

    @pytest.mark.run(order=64)
    def test_64_validating_synctime_command(self):
	try:
	    logging.info("Validating synctime command is present in list")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip2)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('help')
	    child.expect('Maintenance Mode >')
	    output = child.before
	    print (output)
	    if "synctime" in output:
	        logging.info("synctime command is present in Maintenance Mode command list")
	        assert True
	    else:
		logging.error("synctime command is not present in Maintenance Mode command list")
		assert False
	except Exception as error_message:
	    logging.info("synctime command is not present in Maintenance Mode command list")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)

    @pytest.mark.run(order=65)
    def test_65_validating_synctime_command_on_master_with_fips_mode(self):
	try:
	    logging.info("Validating synctime command output for offset value with fips mode")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip2)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    child.expect('[Default: None]')
	    child.sendline(config.external_server_ip)
	    #child.expect(':')
	    #child.sendline('\r')
	    sleep(5)
	    child.expect(':')
	    child.sendline('n')
	    child.expect('Maintenance Mode >')
	    output = child.before
	    print ('my output',output)
	    #output= 
	    #output=output.replace('\n','').replace('\r','').replace(' ','').replace(':','').replace(']','').replace('(','').replace(')','').replace('?','')
	    output1 = re.findall("\d+\.\d+",output)
	    offset=output1[-1]	    
	    print (offset)
	    if offset:
	        logging.info("synctime command is displaying the offset values between systems in fips mode")
	        assert True
	    else:
		logging.error("synctime command is not displaying the offset values between systems in fips mode")
		assert False
	except Exception as error_message:
	    logging.info("synctime command is not displaying the offset values between systems")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)

    
    @pytest.mark.run(order=66)
    def test_66_test_disable_fips_mode(self):
        logging.info("disable fips_mode ")
        #pdb.set_trace()
	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip2)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline("set fips_mode")
        child.expect(".*Enable FIPS mode?.*")
        child.sendline("n")
        child.expect(".*is this correct?.*")
        child.sendline("y")
        child.expect(".*Are you sure you want to continue.*")
        child.sendline("y")
	output = child.before
	print(output)
	child.sendline('exit')
	child.close()
	sleep(500)
	for i in range(2):	
	    if prod_status(config.grid_vip2):
	        print("system can be used for further testing")
	    else:
	    	print("system cannot be used for further testing")
	    	sleep(800)
	else:
	    sleep(200)


    @pytest.mark.run(order=67)
    def test_67_validate_fips_mode_disabled(self):
        logging.info("validate the fips mode is enabled ")
	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip2)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('show fips_mode')
	child.expect('Infoblox >')
	output=child.before
	if "No" in output:
		logging.info("fips mode is not enabled")
		assert True
	else:
		logging.error("fips mode is enabled")
		assert False


    @pytest.mark.run(order=68)
    def test_68_enable_cc_mode_enabled(self):
        logging.info("validate the fips mode is enabled ")
	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip2)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
	child.expect('Infoblox >')
	#pdb.set_trace()
	child.sendline('set cc_mode')
	child.expect(":")
	#child.sendline('\n')
	print(child.after)
	child.sendline('y')
	child.expect(":")
	child.sendline('\n')
	child.sendline('y')
	print(child.before)
	child.expect(":")
	child.sendline('y')
	#child.expect(".*Rebooting....*", timeout=120)
	sleep(600)
	if prod_status(config.grid_vip):
		logging.info("system is avaiable for testing")
	else:
		logging.info("system is still taking restart")
		sleep(100)
	
    @pytest.mark.run(order=69)
    def test_69_validate_cc_mode_enabled(self):
        logging.info("validate the cc mode is enabled ")
	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip2)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	child.sendline('show cc_mode')
	child.expect('Infoblox >')
	output=child.before
	if "Yes" in output:
		logging.info("cc mode is enabled")
		assert True
	else:
		logging.error("cc mode is not enabled")
		assert False

    @pytest.mark.run(order=70)
    def test_70_validating_synctime_command(self):
	try:
	    logging.info("Validating synctime command is present in list")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip2)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('help')
	    child.expect('Maintenance Mode >')
	    output = child.before
	    print (output)
	    if "synctime" in output:
	        logging.info("synctime command is present in Maintenance Mode command list")
	        assert True
	    else:
		logging.error("synctime command is not present in Maintenance Mode command list")
		assert False
	except Exception as error_message:
	    logging.info("synctime command is not present in Maintenance Mode command list")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)

    
   
    @pytest.mark.run(order=71)
    def test_71_validating_synctime_command_on_master_with_cc_mode(self):
	try:
	    logging.info("Validating synctime command output for offset value with cc mode")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip2)
            child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    child.expect('[Default: None]')
	    child.sendline(config.external_server_ip)
	    #child.expect(':')
	    #child.sendline('\r')
	    sleep(5)
	    child.expect(':')
	    child.sendline('n')
	    child.expect('Maintenance Mode >')
	    output = child.before
	    print ('my output',output)
	    #output= 
	    #output=output.replace('\n','').replace('\r','').replace(' ','').replace(':','').replace(']','').replace('(','').replace(')','').replace('?','')
	    output1 = re.findall("\d+\.\d+",output)
	    offset=output1[-1]	    
	    print (offset)
	    if offset:
	        logging.info("synctime command is displaying the offset values between systems with cc mode")
	        assert True
	    else:
		logging.error("synctime command is not displaying the offset values between systems with cc mode")
		assert False
	except Exception as error_message:
	    logging.info("synctime command is not displaying the offset values between systems")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)

    


    @pytest.mark.run(order=72)
    def test_72_disable_cc_mode(self):
        logging.info("Disable the cc mode ")
	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip2)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
	child.expect('Infoblox >')
	child.sendline('set cc_mode')
	child.expect(":")
	child.sendline('n')
	child.expect(":")
	#child.sendline('\n')
	print(child.after)
	child.sendline('y')
	child.expect(":")
	child.sendline('\n')
	child.sendline('y')	
	sleep(300)
	if prod_status(config.grid_vip):
		logging.info("system is avaiable for testing")
	else:
		logging.info("system is still taking restart")
		sleep(100)


    @pytest.mark.run(order=73)
    def test_73_validate_cc_mode_disabled(self):
        logging.info("validate the cc mode is disabled ")
	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip2)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
	#pdb.set_trace()
	child.sendline('show cc_mode')
	child.expect('Infoblox >')
	output=child.before
	if "No" in output:
		logging.info("cc mode is disabled")
		assert True
	else:
		logging.error("cc mode is enabled")
		assert False

    


    @pytest.mark.run(order=74)
    def test_74_validating_synctime_command_on_member_configured_ip_address_for_ip_separted_comma(self):
	try:
	    logging.info("Validating synctime command output to get VPN address")
            child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
	    child.logfile=sys.stdout
            child.expect('password')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('\r')
            output = child.before
            print ('my output',output)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode >')
	    child.sendline('synctime')
	    #child.expect("Do you want to continue ? (y or n): ")
	    child.sendline('y')
	    child.expect(':')
	    output=child.before
	    output1=child.after
	    child.sendline(config.server_ip1)
	    child.sendline('\n')
	    sleep(5)
	    child.expect('Maintenance Mode >')
	    output2=child.before
	    print ("output is", output2)
	    #pdb.set_trace()
	    output=output2.replace('\n',' ').replace('\r',' ').replace('\t','')
	    pattern=re.compile('((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
	    list_ip=[]
	    for i in output.split():
		if pattern.search(i):
		     list_ip.append(i)
		else:
		    break
	    print(list_ip)
	    new_string=''.join(list_ip)
	    if ',' in new_string:
		logging.info("Ip addresses are separated by commas")
		assert True
	    else:
		logging.error("IP addresses are not separated by commas")
		assert False
	except Exception as error_message:
	    logging.error("synctime command is not giving expected results")
	    assert False
	finally:
	    child.sendline('exit')
	    child.close()
	    sleep(10)

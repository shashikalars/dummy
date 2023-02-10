import re
import pprint
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
from itertools import groupby
import paramiko
    

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

def parse_get_lab_info(hostname):
    """
    hostnam : hostname of the machine
    Returns : Dictionary containing lab unit info
    """
    info = os.popen("get_lab_info -H "+hostname).read()
    info_list = info.split('\n')
    info_list = list(filter(None, info_list))
    info_dict = {}
    for pair in info_list:
        info_dict[pair.split('=')[0]] = pair.split('=')[1]
    #print(info_dict)
    return info_dict

def check_console(vmid):
    """
    vmid    : hostname of the machine
    Returns : Null
    """
    child = pexpect.spawn("console_connect -H "+vmid,  maxread=2000)
    try:
        child.expect(".*Escape character is .*")
        print(child.after)
        child.sendline("\r")
        child.expect(".*login:")
        print(child.after)
        return
    except Exception as e:
        child.sendline("exit")
    finally:
        child.close()
        sleep(30)

def touch_debug_fipsmode(grid):
    print("Enable touch /infoblox/var/debug_fipsmode")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    client.connect(grid, username='root', pkey = mykey)
    stdin, stdout, stderr = client.exec_command("touch /infoblox/var/debug_fipsmode")
    print(stderr.read())
    client.close()

def restart_services():
    """
    Restart Services
    """
    print("Restart services")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
    ref = json.loads(grid)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data),grid_vip=config.grid_vip)
    sleep(10)


def dns_configuration():
    '''Enable DNS at mgmt'''
    ref=ib_NIOS.wapi_request('GET', object_type="member:dns")
    ref=json.loads(ref)[0]['_ref']
    data={"use_mgmt_port":True}
    ref1=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
    logging.info (ref1)
    time.sleep(120)

    '''Add DNS Forwarder'''
    logging.info("Add DNS forwarder  ")
    grid_dns_ref = ib_NIOS.wapi_request('GET', object_type='grid:dns')
    data = {"forwarders":[config.forwarder]}
    response = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_dns_ref)[0]['_ref'], fields=json.dumps(data))
    if type(response) == tuple:
        if response[0]==400 or response[0]==401:
            logging.info("Failure: Adding DNS Forwarder")
            assert False
    '''Add DNS Resolver'''
    logging.info("Add DNS Resolver 10.103.3.10")
    grid_ref = ib_NIOS.wapi_request('GET', object_type='grid')
    data = {"dns_resolver_setting":{"resolvers":[config.resolver]}}
    response = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_ref)[0]['_ref'], fields=json.dumps(data))
    logging.info(response)
    if type(response) == tuple:
        if response[0]==400 or response[0]==401:
            logging.info("Failure: Adding DNS Resolver")
            assert False

    '''Allow recursive query for GRID 1'''
    logging.info("Allow recursive query")
    data =  {"recursive_query_list": [{"address": "Any", "permission": "ALLOW"}]}
    response = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_dns_ref)[0]['_ref'], fields=json.dumps({"allow_recursive_query": True}))
    logging.info(response)
    if type(response) == tuple:
        if response[0]==400 or response[0]==401:
            logging.info("Failure: Allow recursive query")
            assert False
        logging.info("Update recursive query list")
        response2 = ib_NIOS.wapi_request('PUT', ref=json.loads(grid_dns_ref)[0]['_ref'], fields=json.dumps(data))
        logging.info(response2)
        if type(response2) == tuple:
            if response2[0]==400 or response2[0]==401:
                logging.info("Failure: Add recursive query list")
                assert False


class rfe_8675(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_01_validating_wred_status(self):
        logging.info("Validating for default status of  wred-status")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        #pdb.set_trace()
        child.sendline('\r')
        output = child.before
        print ('my output',output)
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
        child.sendline('show wred-status')
        child.expect('Maintenance Mode >')
        output = child.before
        print ('my output',output)
        if ('enabled' in output):
            logging.info("WRED is enabled by default")
            assert True
        else:
            logging.info("WRED is not enabled by default")
            assert False
        child.sendline('exit')
	sleep(10)

    @pytest.mark.run(order=2)
    def test_02_disable_wred(self):
        logging.info("Disabling wred with disable command")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
        child.sendline('set wred disable')
        child.expect('Maintenance Mode >')
        output = child.before
        print (output)
        if (' disabled' in output):
            logging.info("WRED is disabled by cli command")
            assert True
        else:
            logging.info("WRED is not able to disable")
            assert False
        child.sendline('exit')
	sleep(10)

    @pytest.mark.run(order=3)
    def test_03_validating_wred_disable_command(self):
        logging.info("Validating wred-status after disable command")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
        child.sendline('show wred-status')
        child.expect('Maintenance Mode >')
        output = child.before
        print (output)
        if ('disabled' in output):
            logging.info("WRED is disabled by command")
            assert True
        else:
            logging.info("WRED is not disabled by commnd")
            assert False
        child.sendline('exit')
	sleep(10)

    @pytest.mark.run(order=4)
    def test_04_enable_wred(self):
        logging.info("Enabling wred with enable command")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
        child.sendline('set wred enable')
        child.expect('Maintenance Mode >')
        output = child.before
        print (output)
        if ('enabled' in output):
            logging.info("WRED is enabled by cli command")
            assert True
        else:
            logging.info("WRED is not able to enable")
            assert False
        child.sendline('exit')
	sleep(10)

    @pytest.mark.run(order=5)
    def test_05_validating_wred_enable_command(self):
        logging.info("Validating wred status after enable command")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
        child.sendline('show wred-status')
        child.expect('Maintenance Mode >')
        output = child.before
        print (output)
        if ('enabled' in output):
            logging.info("WRED is enabled by command")
            assert True
        else:
            logging.info("WRED is not enabled by commnd")
            assert False
        child.sendline('exit')
	sleep(10)

    @pytest.mark.run(order=6)
    def test_06_set_wred_threshold_values(self):
        logging.info("Validating wred threshold values")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
        child.sendline('set wred 10 20 30')
        child.expect('Maintenance Mode >')
        output = child.before
        print (output)
        if ('For port 0: eth0 rx wred filter is enabled: rxd_thres1=10, rxd_thres2=20, rxd_thres3=30, rxd_count=512'and 'For port 1: eth1 rx wred filter is enabled: rxd_thres1=10, rxd_thres2=20, rxd_thres3=30, rxd_count=512' or 'For port 2: eth2 rx wred filter is enabled: rxd_thres1=10, rxd_thres2=20, rxd_thres3=30, rxd_count=512' or 'For port 3: eth3 rx wred filter is enabled: rxd_thres1=10, rxd_thres2=20, rxd_thres3=30, rxd_count=512' in output):
            logging.info("WRED threshold values can be set through cli commands for eth0 interface")
            assert True
        else:
            logging.info("WRED threshold values cannot be set through cli commands for eth0")
            assert False
        child.sendline('exit')
        sleep(20)

    @pytest.mark.run(order=7)
    def test_07_validate_wred_disable_packets_not_dropped(self):
        logging.info("Validating that after disabling wred ,feature doesn't monitor and packets are not dropped")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
        child.sendline('set wred disable')
        child.expect('Maintenance Mode >')
        output = child.before
        print (output)
        ping_cmd= 'ping -c 3 '+str(config.grid_vip)
        print ping_cmd
        result_ping= os.system(ping_cmd)
        if result_ping == 0:
            logging.info ("packets are not dropped when wred is disabled")
            assert True
        else:
            logging.info ("packets are dropped when wred is disabled")
            assert False
        child.sendline('exit')
	sleep(10)

    @pytest.mark.run(order=8)
    def test_08_validate_wred_stats_command(self):
        logging.info("Validating wred-stats command shows number of packets and type of packets dropped for ICMP") 
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
	child.sendline('set wred 10 20 30')
        child.expect('Maintenance Mode >')
        child.sendline('show wred-stats')
        child.expect('Maintenance Mode >')
        output = child.before
        output=output.replace('\n','').replace('\r','').replace(' ','').replace(':','').replace('=','')
        output1= re.search('eth1(.*)eth0',output)
        result1 = output1.group(0)
        print(result1)
        output1 = re.search('DropcountforICMP(.*)TCP',result1)
        result1 = output1.group(0)
        print(result1)
        output1 = re.findall(r'\d+',str(result1))
        print(output1)
        print ("ICMP packets dropped are " +output1[0])
        if output1 == 0:
            logging.info ('ICMP packets are not dropped as expected')
            assert False
        else:
            logging.info ('ICMP packets are dropped as expected')
            assert True
        child.sendline('exit')
        sleep(60)

    @pytest.mark.run(order=9)
    def test_09_validate_wred_stats_command(self):
        logging.info("Validating wred-stats command shows number of packets and type of packets dropped for TCP")
        #pdb.set_trace()
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
        child.sendline('show wred-stats')
        child.expect('Maintenance Mode >')
        output = child.before
        output=output.replace('\n','').replace('\r','').replace(' ','').replace(':','').replace('=','')
        output1= re.search('eth1(.*)eth0',output)
        result1 = output1.group(0)
        print(result1)
        output1 = re.search('TCPconnectionsdropped(.*)UDP',result1)
        result1 = output1.group(0)
        print(result1)
        output1 = re.findall(r'\d+',str(result1))
        print(output1)
        print ("TCP packets dropped are " +output1[0])
        if output1[0] == '0':
            logging.info ('TCP packets are not dropped as expected')
            assert True
        else:
            logging.info ('TCP packets are dropped as expected')
            assert False
        child.sendline('exit')
        sleep(30)


    @pytest.mark.run(order=10)
    def test_10_validate_wred_stats_command(self):
        logging.info("Validating wred-stats command shows number of packets and type of packets dropped for UDP")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
        child.sendline('show wred-stats')
        child.expect('Maintenance Mode >')
        output = child.before
        output=output.replace('\n','').replace('\r','').replace(' ','').replace(':','').replace('=','')
        output1= re.search('eth1(.*)eth0',output)
        result1 = output1.group(0)
        print(result1)
        output1 = re.search('UDPpacketsdropped(.*)Other',result1)
        result1 = output1.group(0)
        print(result1)
        output1 = re.findall(r'\d+',str(result1))
        print(output1)
        print ("UDP packets dropped are " +output1[0])
        if output1 == 0:
            logging.info ('UDP packets are not dropped as expected')
            assert False
        else:
            logging.info ('UDP packets are dropped as expected')
            assert True
        child.sendline('exit')
	sleep(10)

    
    @pytest.mark.run(order=11)
    def test_11_validate_packet_drops_at_threshold(self):
	#pdb.set_trace()
	dns_configuration()
	sleep(10)
	restart_services()
	sleep(10)
        logging.info("Validating wred-stats command shows number of packets and type of packets dropped after threshold resets")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect(' >')
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
        child.sendline('set wred 0 0 0')
        child.expect('Maintenance Mode >')
        output = child.before
        print (output)
        ping_cmd= 'ping -c 3 '+str(config.grid_vip)
        print ping_cmd
        result_ping= os.system(ping_cmd)
        if result_ping == 0:
            logging.info('packets are not dropping even when threshold is set ')
            assert False
        else:
            logging.info('packets are dropping  when threshold is set ')
            assert True
        child.sendline('set wred 10 10 10')
        child.expect('Maintenance Mode >')
        output = child.before
        print (output)
        ping_cmd= 'ping -c 3 '+str(config.grid_vip)
        print ping_cmd
        result_ping= os.system(ping_cmd)
        if result_ping == 0:
            logging.info('packets are not dropping when threshold is reset ')
            assert True
        else:
            logging.info('packets are dropping  when threshold is reset ')
            assert False
        child.sendline('exit')
	sleep(10)
	
    @pytest.mark.run(order=12)
    def test_12_test_wred_stats_command(self):
        logging.info("Validating wred-stats command shows number of packets and type of packets dropped")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
        child.sendline('show wred-stats')
        child.expect('Maintenance Mode >')
        output = child.before
        print (output)
        if ('Drop count for ICMP' in output):
            logging.info("WRED is enabled and wred-stats command is working")
            assert True
        else:
            logging.info("wred-stats command is not working")
            assert False
        child.sendline('exit')
        sleep(30)

    @pytest.mark.run(order=13)
    def test_13_test_wred_stats_command(self):
        logging.info("Validating wred  lower threshold values ")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
        child.sendline('set wred -1 -1 -1')
        child.expect('Maintenance Mode >')
        #pdb.set_trace()
        output = child.before
        print (output)
        if ('t1, t2, t3 should be between 0 and 512 and should be in increasing order' in output):
            logging.info("WRED threshold value should be a positve number")
            assert True
        else:
            logging.info('CLI command is accepting negative threshold value')
            assert False
        child.sendline('exit')
	sleep(10)
      
    @pytest.mark.run(order=14)
    def test_14_test_wred_stats_command(self):
        logging.info("Validating wred with higher to that of  threshold values ")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
        child.sendline('set wred 2000 3003 513')
        child.expect('Maintenance Mode >')
        #pdb.set_trace()
        output = child.before
        print (output)
        if ('t1, t2, t3 should be between 0 and 512 and should be in increasing order' in output):
            logging.info("WRED threshold value should be a between 0 to  512")
            assert True
        else:
            logging.info('WRED CLI command is accepting threshold values >512')
            assert False
        child.sendline('exit')
	sleep(10)

    @pytest.mark.run(order=15)
    def test_15_test_validating_udp_packets_dropped(self):
        logging.info("Validating number of UPD packets dropped after setting WRED thresholds ")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
        child.sendline('set wred 0 0 0')
        child.expect('Maintenance Mode >')
        child.sendline('show wred-stats')
        child.expect('Maintenance Mode >')
        output = child.before
        #pdb.set_trace()
        output=output.replace('\n','').replace('\r','').replace(':','').replace('=','')
        print('my replace output',output)
        output1= re.search('eth1(.*)eth0',output)
        #print ('my output1 is', output1)
        result1 = output1.group(0)
        print(result1)
        output2=re.search('UDP(.*)Other',result1)
        output2=output2.group(0)
        print (output2)
        final1= output2.split(' ')
        print (type(final1))
        value1= (final1[-2])
        #pdb.set_trace()
        result= os.system('dig @'+config.grid_master_vip +' '+'google.com')
        print (result)
        sleep(10)
        child.sendline('show wred-stats')
        child.expect('Maintenance Mode >')
        output = child.before
        output=output.replace('\n','').replace('\r','').replace(':','').replace('=','')
        output1= re.search('eth1(.*)eth0',output)
        result1 = output1.group(0)
        print(result1)
        output2=re.search('UDP(.*)Other',result1)
        output2=output2.group(0)
        print (output2)
        final1= output2.split(' ')
        print (type(final1))
        value2= (final1[-2])
        if int(value2)  >= int(value1):
            logging.info ('After setting wred threshold UDP packets are', value2)
            assert True
        else:
            logging.info ('After setting wred threshold UDP packets are', value2)
            assert False
        child.sendline('exit')
	sleep(10)

    @pytest.mark.run(order=16)
    def test_16_test_validating_tcp_packets_dropped(self):
        logging.info("Validating number of TCP packets dropped after setting WRED thresholds ")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
        child.sendline('show wred-stats')
        child.expect('Maintenance Mode >')
        output = child.before
        output=output.replace('\n','').replace('\r','').replace(':','').replace('=','')
        print('my replace output',output)
        output1= re.search('eth1(.*)eth0',output)
        result1 = output1.group(0)
        print(result1)
        #pdb.set_trace()
        output2=re.search('TCP(.*)UDP',result1)
        output2=output2.group(0)
        print (output2)
        final1= output2.split(' ')
        print (type(final1))
        value1= (final1[-2])
        result= os.system('dig @'+config.grid_master_vip +' '+'google.com'+' '+ '+tcp')
        print (result)
        sleep(10)
        child.sendline('show wred-stats')
        child.expect('Maintenance Mode >')
        output = child.before
        output=output.replace('\n','').replace('\r','').replace(':','').replace('=','')
        print('my replace output',output)
        output1= re.search('eth1(.*)eth0',output)
        result1 = output1.group(0)
        output2=re.search('TCP(.*)UDP',result1)
        output2=output2.group(0)
        print (output2)
        final1= output2.split(' ')
        value2 = int(final1[-2])
        if int(value2) >= int(value1):
            logging.info ('After setting wred threshold TCP packets are', value2)
            assert True
        else:
            logging.info ('After setting wred threshold TCP packets are',value2)
            assert False
        child.sendline('exit')
	sleep(10)

    @pytest.mark.run(order=17)
    def test_17_test_validating_ICMP_packets_dropped(self):
        logging.info("Validating number of ICMP packets dropped after setting WRED thresholds ")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
        child.sendline('show wred-stats')
        child.expect('Maintenance Mode >')
        output = child.before
        #pdb.set_trace()
        output=output.replace('\n','').replace('\r','').replace(':','').replace('=','')
        print('my replace output',output)
        output1= re.search('eth1(.*)eth0',output)
        result1 = output1.group(0)
        print(result1)
        output2=re.search('ICMP(.*)TCP',result1)
        output2=output2.group(0)
        print (output2)
        final1= output2.split(' ')
        print (type(final1))
        value1= int(final1[-2])
        child.sendline('set wred 0 0 0')
        child.expect('Maintenance Mode >')
        ping_cmd= 'ping -c 1 '+str(config.grid_vip)
        print ping_cmd
        result_ping= os.system(ping_cmd)
        sleep(5)
        child.sendline('show wred-stats')
        child.expect('Maintenance Mode >')
        output = child.before
        #pdb.set_trace()
        output=output.replace('\n','').replace('\r','').replace(':','').replace('=','')
        print('my replace output',output)
        output1= re.search('eth1(.*)eth0',output)
        result1 = output1.group(0)
        print(result1)
        output2=re.search('ICMP(.*)TCP',result1)
        output2=output2.group(0)
        print (output2)
        final1= output2.split(' ')
        print (type(final1))
        value2= int(final1[-2])
        if value2 >= value1:
            logging.info ('ICMP packets dropped after setting WRED threshold is ', value2)
            assert True
        else:
            logging.info('ICMP packets are not dropping as expected after setting WRED threshold, drop counts of before and after setting threshold respectively are ', value1 , value2)
            assert False
        child.sendline('exit')
	sleep(120)
 
    @pytest.mark.run(order=18)
    def test_18_test_enable_fips_mode(self):
	logging.info("validate the fips mode is enabled ")
	#pdb.set_trace()
	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
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
	    if prod_status(config.grid_vip):
	        print("system can be used for further testing")
		sleep(120)
	    else:
	    	print("system cannot be used for further testing")
	    	sleep(1200)
	else:
	    sleep(900)


    @pytest.mark.run(order=19)
    def test_19_test_validating_wred_stats_command_fips_mode(self):
        logging.info("Validating wred-stats command in fips_mode ")
        #sleep(360)
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show fips_mode')
        child.expect('Infoblox >')
        output = child.before
        if ('FIPS Mode Enabled:  Yes' in output):
            logging.info("system has entered FIPS mode")
        else:
            logging.info("system is not in FIPS mode")
            assert False
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
        child.sendline('show wred-stats')
        child.expect('Maintenance Mode >')
        output = child.before
        print ('my output',output)
   	if ('Drop count for ICMP' in output):
            logging.info("WRED is enabled and wred-stats command is working in FIPS mode")
            assert True
        else:
            logging.info("wred-stats command is not working in FIPS mode")
            assert False
	child.sendline('exit') 
	sleep(10)

    @pytest.mark.run(order=20)
    def test_20_test_validating_wred_status_command_fips_mode(self):
        logging.info("Validating wred-status command in fips_mode ")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show fips_mode')
        child.expect('Infoblox >')
        output = child.before
        if ('FIPS Mode Enabled:  Yes' in output):
            logging.info("system has entered FIPS mode")
        else:
            logging.info("system is not in FIPS mode")
            assert False
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
        child.sendline('show wred-status')
        child.expect('Maintenance Mode >')
        output = child.before
        print ('my output',output)
        if ('rx wred filter is enabled' in output):
            logging.info("WRED is enabled by default")
            assert True
        else:
            logging.info("WRED is not enabled by default")
            assert False
        child.sendline('exit')
	sleep(10)

    @pytest.mark.run(order=21)
    def test_21_test_validating_set_wred_command_fips_mode(self):
        logging.info("Validating set wred commands in fips_mode ")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show fips_mode')
        child.expect('Infoblox >')
        output = child.before
        if ('FIPS Mode Enabled:  Yes' in output):
            logging.info("system has entered FIPS mode")
        else:
            logging.info("system is not in FIPS mode")
            assert False
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
        child.sendline('set maintenancemode')
        #pdb.set_trace()
        child.expect('Maintenance Mode >')
        child.sendline('set wred 10 20 30')
        child.expect('Maintenance Mode >')
        output = child.before
        print (output)
        if ('rx wred filter is enabled: rxd_thres1=10, rxd_thres2=20, rxd_thres3=30, rxd_count=512' in output):
            logging.info("WRED threshold values can be set through cli commands")
            assert True
        else:
            logging.info("WRED threshold values cannot be set through cli commands")
            assert False
        child.sendline('exit')
	sleep(10)
    
    @pytest.mark.run(order=22)
    def test_22_test_disable_fips_mode(self):
	logging.info("disable fips_mode ")
        #pdb.set_trace()
	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
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
	    if prod_status(config.grid_vip):
	        print("system can be used for further testing")
	    else:
	    	print("system cannot be used for further testing")
	    	sleep(800)
	else:
	    sleep(200)



    @pytest.mark.run(order=23)
    def test_23_disable_TP(self):
          logging.info("Disabling TP license")
          sleep(420)
          logging.info("stop the TP service")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
          logging.info(get_ref)
          res = json.loads(get_ref)
          for i in res:
              ref1=i["_ref"]
              logging.info("Disable TP")
              data = {"enable_service": False}
              response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
              logging.info(response)
          sleep(420)
          logging.info("Test Case 23 Execution Completed")
          assert True

    @pytest.mark.run(order=24)
    def test_24_disable_DCA(self):
          logging.info("Disabling DCA license")
          sleep(520)
          logging.info("stop the DCA service")
          get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
          logging.info(get_ref)
          res = json.loads(get_ref)
          logging.info(res)
          for i in res:
              ref1=i["_ref"]
              logging.info("Disable DCA")
              data = {"enable_dns_cache_acceleration": False}
              response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
              logging.info(response)
          sleep(420)
          logging.info("Test Case 24 Execution Completed")
          assert True



    @pytest.mark.run(order=25)
    def test_25_test_wred_status_command_DCA_TP_Disabled(self):
        logging.info("Validating wred command doesn't work when DCA+TP disabled ")
	sleep(420)
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('set maintenancemode')
        child.expect('Maintenance Mode >')
        child.sendline('show wred-status')
        child.expect('Maintenance Mode >')
        output = child.before
        print (output)
        if ('Need to start DNS Cache Acceleration or Threat Protection service to enable WRED'or 'rx wred filter is disabled' in output):
            logging.info("DCA+TP should be working to enable WRED")
            assert True
        else:
            logging.info('WRED is working even when DCA+TP is disabled')
            assert False
        child.sendline('exit')









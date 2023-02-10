#__author__ = "Sneha Kulkarni"
#__email__  = "skulkarni@infoblox.com"

######################################################################################################################
#  #Grid Set up required:                                                                                             #
#  #===========
#"1) Request a standalone master 
#2) Add Threat Protection (TP), Threat Analytics,Threat Protection subscription (TP-Sub) license and RPZ licenses
######################################################################################################################


import re
import pytest
import unittest
import logging
import subprocess
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
import getpass
import shlex
import sys
import paramiko
import config
from datetime import datetime
from paramiko import client
#from log_capture import log_action as log
#from log_validation import log_validation as logv
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
import pdb




def restart_services():
    """
    Restart Services
    """
    logging.info("Restart services")
    grid = ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
    ref = json.loads(grid)[0]['_ref']
    data = {"member_order": "SIMULTANEOUSLY", "restart_option": "FORCE_RESTART", "service_option": "ALL"}
    restart = ib_NIOS.wapi_request('POST', object_type=ref + "?_function=restartservices", fields=json.dumps(data),grid_vip=config.grid_vip)
    sleep(40)


def dig_commands():
    fobj=open("removed.txt", 'r')
    record_type="TXT"
    for line in fobj:
        line=line.replace("\n","")
        for i in range(1,20):
            dig_cmd = 'dig @'+config.grid_vip+' '+'226L01TTL-0.'+str(i)+'.'+line+str(' IN ')+str(record_type)
            #sleep(1)
            print dig_cmd
            os.system(dig_cmd)
    fobj.close()


class NIOSSPT_10970(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_001_configure_snmp_trap(self):
        """
        Configuring snmp receivers and traps
        """
        logging.info("enable snmp queries")
        ref= ib_NIOS.wapi_request('GET', object_type="grid",params="?_return_fields=snmp_setting",grid_vip=config.grid_vip)
        ref= json.loads(ref)
        logging.info(ref)
        grid_ref=ref[0]['_ref']
        data={"snmp_setting": {"queries_community_string": "public","queries_enable": True,"trap_receivers": [{"address": "10.120.20.93"}],"traps_community_string": "public","traps_enable": True}}
        response= ib_NIOS.wapi_request('PUT', ref=grid_ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        logging.info(response)
        if type(response) == tuple:
	    if response[0]==400 or response[0]== 401:
	        logging.info("Failed to configure snmp")
	        assert False
	    else:
	        logging.info("SNMP configured successfully")
	        assert True
        logging.info("Test case execution completed")

    @pytest.mark.run(order=2)
    def test_002_enable_notifications(self):
        """
        After confguring snmp, need to enable notifications
        """
        ref= ib_NIOS.wapi_request('GET', object_type="grid",params="?_return_fields=trap_notifications", grid_vip=config.grid_vip)
        ref= json.loads(ref)
        logging.info(ref)
        grid_ref=ref[0]['_ref']
        data = {"trap_notifications": [{"enable_email": True,"enable_trap": True,"trap_type": "AnalyticsRPZ"},{"enable_email": True,"enable_trap": True,"trap_type": "AutomatedTrafficCapture"},{"enable_email": True,"enable_trap": True,"trap_type": "BFD"},{"enable_email": True,"enable_trap": True,"trap_type": "BGP"},{"enable_email": True,"enable_trap": True,"trap_type": "Backup"},{"enable_email": True,"enable_trap": True,"trap_type": "Bloxtools"},{"enable_email": True,"enable_trap": True,"trap_type": "CPU"},{"enable_email": True,"enable_trap": True,"trap_type": "CaptivePortal"},{"enable_email": True,"enable_trap": True,"trap_type": "CiscoISEServer"},{"enable_email": True,"enable_trap": True,"trap_type": "Clear"},{"enable_email": True,"enable_trap": True,"trap_type": "CloudAPI"},{"enable_email": True,"enable_trap": True,"trap_type": "Cluster"},{"enable_email": True,"enable_trap": True,"trap_type": "Controld"},{"enable_email": True,"enable_trap": True,"trap_type": "DHCP"},{"enable_email": True,"enable_trap": True,"trap_type": "DNS"},{"enable_email": True,"enable_trap": True,"trap_type": "DNSAttack"},{"enable_email": True,"enable_trap": True,"trap_type": "DNSIntegrityCheck"},{"enable_email": True,"enable_trap": True,"trap_type": "DNSIntegrityCheckConnection"},{"enable_email": True,"enable_trap": True,"trap_type": "Database"},{"enable_email": True,"enable_trap": True,"trap_type": "DisconnectedGrid"},{"enable_email": True,"enable_trap": True,"trap_type": "Discovery"},{"enable_email": True,"enable_trap": True,"trap_type": "DiscoveryConflict"},{"enable_email": True,"enable_trap": True,"trap_type": "DiscoveryUnmanaged"},{"enable_email": True,"enable_trap": True,"trap_type": "Disk"},{"enable_email": True,"enable_trap": True,"trap_type": "DuplicateIP"},{"enable_email": True,"enable_trap": True,"trap_type": "ENAT"},{"enable_email": True,"enable_trap": True,"trap_type": "FDUsage"},{"enable_email": True,"enable_trap": True,"trap_type": "FTP"},{"enable_email": True,"enable_trap": True,"trap_type": "Fan"},{"enable_email": True,"enable_trap": True,"trap_type": "HA"},{"enable_email": True,"enable_trap": True,"trap_type": "HSM"},{"enable_email": True,"enable_trap": True,"trap_type": "HTTP"},{"enable_email": True,"enable_trap": True,"trap_type": "IFMAP"},{"enable_email": True,"enable_trap": True,"trap_type": "IMC"},{"enable_email": True,"enable_trap": True,"trap_type": "IPAMUtilization"},{"enable_email": True,"enable_trap": True,"trap_type": "IPMIDevice"},{"enable_email": True,"enable_trap": True,"trap_type": "LCD"},{"enable_email": True,"enable_trap": True,"trap_type": "LDAPServers"},{"enable_email": True,"enable_trap": True,"trap_type": "License"},{"enable_email": True,"enable_trap": True,"trap_type": "Login"},{"enable_email": True,"enable_trap": True,"trap_type": "MGM"},{"enable_email": True,"enable_trap": True,"trap_type": "MSServer"},{"enable_email": True,"enable_trap": True,"trap_type": "Memory"},{"enable_email": True,"enable_trap": True,"trap_type": "NTP"},{"enable_email": True,"enable_trap": True,"trap_type": "Network"},{"enable_email": True,"enable_trap": True,"trap_type": "OCSPResponders"},{"enable_email": True,"enable_trap": True,"trap_type": "OSPF"},{"enable_email": True,"enable_trap": True,"trap_type": "OSPF6"},{"enable_email": True,"enable_trap": True,"trap_type": "Outbound"},{"enable_email": True,"enable_trap": True,"trap_type": "PowerSupply"},{"enable_email": True,"enable_trap": True,"trap_type": "RAID"},{"enable_email": True,"enable_trap": True,"trap_type": "RIRSWIP"},{"enable_email": True,"enable_trap": True,"trap_type": "RPZHitRate"},{"enable_email": True,"enable_trap": True,"trap_type": "RecursiveClients"},{"enable_email": True,"enable_trap": True,"trap_type": "Reporting"},{"enable_email": True,"enable_trap": True,"trap_type": "RootFS"},{"enable_email": True,"enable_trap": True,"trap_type": "SNMP"},{"enable_email": True,"enable_trap": True,"trap_type": "SSH"},{"enable_email": True,"enable_trap": True,"trap_type": "SerialConsole"},{"enable_email": True,"enable_trap": True,"trap_type": "SwapUsage"},{"enable_email": True,"enable_trap": True,"trap_type": "Syslog"},{"enable_email": True,"enable_trap": True,"trap_type": "System"},{"enable_email": True,"enable_trap": True,"trap_type": "TFTP"},{"enable_email": True,"enable_trap": True,"trap_type": "Taxii"},{"enable_email": True,"enable_trap": True,"trap_type": "ThreatAnalytics"},{"enable_email": True,"enable_trap": True,"trap_type": "ThreatProtection"}]}
        response= ib_NIOS.wapi_request('PUT', ref=grid_ref, fields=json.dumps(data), grid_vip=config.grid_vip)
        logging.info(response)
        if type(response) == tuple:
	    if response[0]==400 or response[0]== 401:
	        logging.info("Failed to configure snmp")
	        assert False
	    else:
	        logging.info("SNMP configured successfully")
	        assert True
        logging.info("Test case execution completed")
        restart_services()

    @pytest.mark.run(order=3)
    def test_003_Configure_Global_Forwarders_Logging_Categories_Allow_Recursion_At_Grid_level(self):
	    logging.info("Configure Global Forwarders Logging Categories Allow Recursion at Grid level")
	    get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
	    logging.info(get_ref)
	    res = json.loads(get_ref)
	    ref1 = json.loads(get_ref)[0]['_ref']
	    print ref1
	    logging.info("Modify Grid DNS Properties")
	    data = {"allow_recursive_query": True,"forwarders":[config.dns_forwarder],"logging_categories": {"log_queries": True,"log_responses": True,"log_rpz": True}}
	    response = ib_NIOS.wapi_request('PUT',ref= ref1,fields=json.dumps(data))
	    print (response)
	    logging.info(response)
            read  = re.search(r'200',response)
            for read in  response:
                assert True
            print("Test Case 3 Execution Completed")


    @pytest.mark.run(order=4)
    def test_004_Validate_Global_Forwarders_Logging_Categories_Allow_Recursion_At_Grid_level(self):
        logging.info("Validate Configured Global Forwarders Logging Categories Allow Recursion at Grid level")
        get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="grid:dns",params="?_return_fields=allow_recursive_query,forwarders")
        res = json.loads(get_tacacsplus)
        res = eval(json.dumps(get_tacacsplus))
	forwarder=config.dns_forwarder
        print(res)
        output=res.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
        print(output)
        result = ['allow_recursive_query:true']
        for i in result:
	    if i in output:
                assert True
            else:
                assert False
        print(result)
	logging.info("Test Case 4 Execution Completed")
        #logging.info("============================")

   
    @pytest.mark.run(order=5)
    def test_005_add_rpz_zone(self):
        data={"fqdn": "zone1","grid_primary":[{"name": config.grid_fqdn,"stealth":False}]}
        get_ref=ib_NIOS.wapi_request('POST', object_type="zone_rp",fields=json.dumps(data))
        logging.info("adding RPZ zone ")
        if type(get_ref)!=tuple:
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            time.sleep(10)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            time.sleep(20)
            print ("Restarting the grid ")
            response=ib_NIOS.wapi_request('GET', object_type="zone_rp")
            response1=json.loads(response)
            if response1[0]["fqdn"]==data["fqdn"]:
                logging.info("Test case 12 passed as RPZ zone is added")
                assert True
            else:
                logging.info("Test case 12 failed as RPZ zone is not added")
                assert False
        else:
            logging.info("Test case 12 failed as RPZ zone is not added")
            assert False

    @pytest.mark.run(order=6)
    def test_006_add_RPZ_zone_to_threat_analytics(self):
        get_ref=ib_NIOS.wapi_request('GET', object_type="zone_rp")
        getref1=json.loads(get_ref)
        data={"dns_tunnel_black_list_rpz_zones":[getref1[0]['_ref']]}
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics")
        logging.info(get_ref)
        get_ref1=json.loads(get_ref)[0]['_ref']
        get_ref_of_TA=ib_NIOS.wapi_request('PUT', object_type=get_ref1,fields=json.dumps(data))
        logging.info(get_ref_of_TA)
        if type(get_ref_of_TA)!=tuple:
            logging.info(get_ref_of_TA)
            logging.info("Test case 6 passed")
            assert True
        else:
            logging.info("Test case 6 failed")
            assert False

    @pytest.mark.run(order=7)
    def test_007_start_threat_analytics(self):
        members=[]
        get_ref=ib_NIOS.wapi_request('GET', object_type="member:threatanalytics")
        get_ref=json.loads(get_ref)
        for i in get_ref:
            members.append(i["_ref"])
        for ref in members:
            data={"enable_service":True}
            get_ref_of_TA=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
            logging.info(get_ref)
            time.sleep(30)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        time.sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        time.sleep(40)
        logging.info("Restarting the grid ")
        for i in members:
            get_ref=ib_NIOS.wapi_request('GET', object_type=i)
            get_ref1=json.loads(get_ref)
            if get_ref1["status"]=="WORKING":
                assert True
                logging.info("Test case 7 passed as threat analytics is running")
            else:
                assert False
                logging.info("Test case 7 failed as threat analytics is not running")


    @pytest.mark.run(order=8)
    def test_008_Start_DNS_Service(self):
        logging.info("Start DNS Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        logging.info(get_ref)
        res = json.loads(get_ref)
        for ref in res:
            ref1 = ref["_ref"]
            logging.info("Modify a enable_dns")
            data = {"enable_dns": True}
            response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
            print response
            sleep(20)
            logging.info(response)
            read  = re.search(r'200',response)
            for read in  response:
                assert True
        logging.info("Test Case 8 Execution Completed")

    @pytest.mark.run(order=9)
    def test_009_Validate_DNS_service_Enabled(self):
        logging.info("Validate DNs Service is enabled")
        get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
        logging.info(get_tacacsplus)
        res = json.loads(get_tacacsplus)
        print res
        for i in res:
            print i
            logging.info("found")
            assert i["enable_dns"] == True
        logging.info("Test Case 9 Execution Completed")
        logging.info("============================")


    
	
    @pytest.mark.run(order=10)
    def test_010_start_snmp_trap(self):
        logging.info("starting snmp traps")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no rkarjagi@'+config.grid_ws)
	child.logfile=sys.stdout
        child.expect('password')
        child.sendline('resetm33')
	child.expect('[rkarjagi@rkarjagi-vm LRT]$')	
	child.sendline("cd /home/rkarjagi/NIOS_8.5_checkout_new/fr/Core_DDI/regression/LRT")
	child.expect('[rkarjagi@rkarjagi-vm LRT]$')
	child.sendline("perl ../func_util/snmp_trap.pl -i"+' '+config.grid_vip+' '+"-t mibs -e positive")
	sleep(10)
	child.sendline("perl ../func_util/snmp_trap.pl -t start -e positive")
	sleep(10)
	logging.info("Test case  10 execution completed")


    @pytest.mark.run(order=11)
    def test_011_start_snmptrapd_logs(self):
	logging.info("starting snmp traps")
        child= pexpect.spawn('ssh -o StrictHostKeyChecking=no rkarjagi@'+config.grid_ws)
	child.logfile=sys.stdout
        child.expect('password')
        child.sendline('resetm33')
	child.sendline("cd /home/rkarjagi/NIOS_8.5_checkout_new/fr/Core_DDI/regression/LRT")
	child.expect('[rkarjagi@rkarjagi-vm LRT]$')
        logging.info("Starting snmp  Logs")
	child.sendline('tail -f ./dump/snmptrapd.log')
	child.expect('[rkarjagi@rkarjagi-vm LRT]$')
	#output=child.before()
	#if output:
	 #   logging.info("started snmptrap logs")
	  #  assert True
	#else:
	 #   logging.info("snmptrap logs are not started")
	  #  assert False
	logging.info("Test case 11 execution completed")
        

    @pytest.mark.run(order=13)
    def test_013_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/messages",config.grid_vip)
        logging.info("test case 13 passed")


    @pytest.mark.run(order=14)
    def test_014_validate_Syslog_Messages_for_DNS_tunneling_detection(self):
        logging.info("Validating Sylog Messages Logs")
        dig_commands()
        sleep(60)
        LookFor="DNS Tunneling detected"
        log("stop","/var/log/messages",config.grid_vip)
        logs=logv(LookFor,"/var/log/messages",config.grid_vip)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 14 Execution Completed")
            assert True
        else:
            logging.info("Test Case 14 Execution Failed")
            assert False





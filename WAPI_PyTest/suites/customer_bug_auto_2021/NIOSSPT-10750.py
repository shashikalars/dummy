#!/usr/bin/env python
__author__ = "Shivasai"
__email__  = "sbandaru@infoblox.com"
########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master + Grid Member IB-FLEX                                                #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415),DTC                                  #
########################################################################################

import os
import pexpect
import re
import config
import pytest
import unittest
import shlex
import logging
import json
import subprocess
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_xxxx.log" ,level=logging.DEBUG,filemode='w')



def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

class NIOSSPT_10766(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_000_setup(self):
        """
        setup method: creating zone nios-10766.com
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case setup Started            |")
        display_msg("------------------------------------------------")
        data={"fqdn":"nios-10766.com","view":"default","grid_primary":[{"name": config.grid_fqdn,"stealth": False}],"grid_secondaries": [{"name": config.grid_member1_fqdn,"stealth": False,"grid_replicate": True,"enable_preferred_primaries": False,"preferred_primaries": []}]}
        zone_ref=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
        logging.info(zone_ref)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        data={"dns_resolver_setting": {"resolvers": ["10.103.3.10"]}}
        ref1=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(5)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(5)
        if type(zone_ref) == tuple:
            assert False
        else:
            assert True
    
    @pytest.mark.run(order=2)
    def test_001_enable_dns(self):
        """
        Enable DNS
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|             Test Case 1 Started              |")
        display_msg("------------------------------------------------")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns", grid_vip=config.grid_vip)
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[1]['_ref']
        data = {"use_mgmt_port": True,"enable_dns": True}
        response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data),grid_vip=config.grid_vip)
        ref2 = json.loads(get_ref)[0]['_ref']
        data = {"enable_dns": True}
        response = ib_NIOS.wapi_request('PUT', ref=ref2, fields=json.dumps(data),grid_vip=config.grid_vip)
        res=json.loads(response)
        logging.info(response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        
    
    
    @pytest.mark.run(order=3)
    def test_002_enable_snmp(self):
        """
        Enable Snmp
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        get_ref = json.loads(get_ref)[0]['_ref']
        data={"snmp_setting":{"queries_enable":True,"queries_community_string":"public","trap_receivers":[{"address": config.client_ip}],"traps_community_string":"public","traps_enable":True}}
        response = ib_NIOS.wapi_request('PUT', ref=get_ref, fields=json.dumps(data))
        if type(response) == tuple:
            assert False
        else:
            assert True
        display_msg("-----------Test Case 2 Execution Completed------------")

    @pytest.mark.run(order=4)
    def test_003_create_dtc_server_pool_lbdn(self):
        """
        create dtc server pool lbdn
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 3 Execution Started           |")
        display_msg("----------------------------------------------------")
        data={"host": config.Server1,"name": "server1snmp"}
        server1_ref=ib_NIOS.wapi_request('POST',object_type='dtc:server',fields=json.dumps(data))
        print(server1_ref)
        data={"host": config.Server2,"name": "server2snmp"}
        server2_ref=ib_NIOS.wapi_request('POST',object_type='dtc:server',fields=json.dumps(data))
        print(server2_ref)
        sleep(15)
        server=ib_NIOS.wapi_request('GET',object_type='dtc:server?name=server1snmp')
        server1=json.loads(server)[0]['_ref']
        server=ib_NIOS.wapi_request('GET',object_type='dtc:server?name=server2snmp')
        server2=json.loads(server)[0]['_ref']
        data={"name": "poolsnmp","lb_preferred_method": "ROUND_ROBIN","servers": [{"ratio": 1,"server": server1},{"ratio": 1,"server": server2}],"monitors": ["dtc:monitor:snmp/ZG5zLmlkbnNfbW9uaXRvcl9zbm1wJHNubXA:snmp"]}
        pool_ref=ib_NIOS.wapi_request('POST',object_type='dtc:pool',fields=json.dumps(data))
        print(pool_ref)
        zone=ib_NIOS.wapi_request('GET',object_type='zone_auth?fqdn=nios-10766.com')
        zone_ref=json.loads(zone)[0]['_ref']
        pool=ib_NIOS.wapi_request('GET',object_type='dtc:pool?name=poolsnmp')
        pool_ref=json.loads(pool)[0]['_ref']
        data={"name": "lbdnsnmp","lb_method": "ROUND_ROBIN","patterns": ["*.nios-10766.com"],"auth_zones": [zone_ref],"pools": [{"pool": pool_ref,"ratio": 1}]}
        lbdn_ref=ib_NIOS.wapi_request('POST',object_type='dtc:lbdn',fields=json.dumps(data))
        sleep(10)
        
        grid = ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(5)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(5)
        if type(lbdn_ref) == tuple:
            assert False
        else:
            assert True
        display_msg("-----------Test Case 3 Execution Completed------------")
        
        
    @pytest.mark.run(order=5)
    def test_004_add_snmp_oid(self):
        """
        add snmp oid in health monitors
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|       Test Case 4 Execution Started          |")
        display_msg("------------------------------------------------")
        snmpref=ib_NIOS.wapi_request('GET', object_type="dtc:monitor:snmp")
        snmpref = json.loads(snmpref)[0]['_ref']
        data={"oids": [{"condition": "EXACT","first": "The MIB module for SNMPv2 entities","oid": ".1.3.6.1.2.1.1.9.1.3.4","type": "STRING"}]}
        monitor_ref=ib_NIOS.wapi_request('PUT',ref=snmpref,fields=json.dumps(data))
        print(monitor_ref)
        sleep(30)
        grid = ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(35)
        if type(monitor_ref) == tuple:
            assert False
        else:
            assert True
        display_msg("-----------Test Case 4 Execution Completed------------")       
            
     
    @pytest.mark.run(order=6)
    def test_005_Verify_server_status(self):
        """
        Verify that server1snmp and server2snmp status is showing as GREEN
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|       Test Case 5 Execution Started          |")
        display_msg("------------------------------------------------")
        server=ib_NIOS.wapi_request('GET',object_type='dtc:server?name=server1snmp')
        server1=json.loads(server)[0]['_ref']
        server1status=ib_NIOS.wapi_request('GET',object_type=server1+'?_return_fields=health')
        print(server1status)
        server1status=json.loads(server1status)
        print(type(str(server1status['health']['availability'])))
        server=ib_NIOS.wapi_request('GET',object_type='dtc:server?name=server2snmp')
        server2=json.loads(server)[0]['_ref']
        server2status=ib_NIOS.wapi_request('GET',object_type=server2+'?_return_fields=health')
        print(server2status)
        server2status=json.loads(server2status)
        if server1status['health']['availability'] == server2status['health']['availability'] == "GREEN":
            assert True
        else:
            assert False
        display_msg("-----------Test Case 5 Execution Completed------------")        
            

    @pytest.mark.order(order=7)
    def test_006_verify_round_robin(self):
        """
        Verify round robin
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|       Test Case 6 Execution Started          |")
        display_msg("------------------------------------------------")
        ip='@'+config.grid_vip
        validation1=config.Server1
        validation2=config.Server2
        output=subprocess.check_output(['dig',ip,'a.nios-10766.com','in','a'])
        logging.info(output)
        if validation1 in output:
            logging.info("Validation1 successful")
            sleep(5)
        else:
            raise Exception("Incorrect dig output")
            
        output2=subprocess.check_output(['dig',ip,'a.nios-10766.com','in','a'])
        if validation2 in output2:
            logging.info("Validation2 successful")
        else:
            raise Exception("Incorrect dig output")
        logging.info("Round robin validation succesfull")
        assert True
        display_msg("-----------Test Case 6 Execution Completed------------")    
     
    @pytest.mark.order(order=8)
    def test_007_Perform_snmp_walk1(self):
        """
        Perform snmp walk from client before enabling Threat protection service
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 7 Execution Started      |")
        display_msg("------------------------------------------------")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.client_ip)
        try:
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('#')
            child.sendline('snmpwalk -v2c -c public -m all ' + config.grid_member1_vip +' -O n &> snmp_walk1.txt\n')
            child.expect('#')
            
            assert True
            
        except Exception as e:
            child.close()
            logger.info("Failure:")
            assert False
        display_msg("-----------Test Case 7 Execution Completed------------")
    
    @pytest.mark.run(order=9)
    def test_008_validate_snmpwalk_output_before_enabling_TP(self):
        """
        Validate snmpwalk command has executed properly
        Verify member fqdn is present in snmpwalk output
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 8 Execution Started      |")
        display_msg("------------------------------------------------")
        cmd=('sshpass -p "infoblox" ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@%s' % (config.client_ip))
        cmd = shlex.split(cmd)
        command1 = 'grep -i -c '+ config.grid_member1_fqdn +' snmp_walk1.txt'
        cmd.append(command1)
        
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output = process.communicate()
        print(output[0])
        if int(output[0]) > 0 :
            print("Found grid oid in smpwalk output")
            assert True
        else:
            assert False   
    
        display_msg("-----------Test Case 8 Execution Completed------------")

    @pytest.mark.run(order=10)
    def test_009_enable_threat_protection(self):
        """
        enable threat protection on member1
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 9 Execution Started      |")
        display_msg("------------------------------------------------")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        ref1 = json.loads(get_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps({"enable_service": True}))
        res=json.loads(response)
        logging.info(response)
        read  = re.search(r'201',response)
        for read in  response:
            assert True
        sleep(300)
        grid = ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(15)
        display_msg("-----------Test Case 9 Execution Completed------------")
    
    
    @pytest.mark.run(order=11)
    def test_010_enable_automatic_download(self):
        """
        Enable auto download in threat protection service.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 10 Execution Started          |")
        display_msg("----------------------------------------------------")
        get_ref = ib_NIOS.wapi_request('GET', object_type="grid:threatprotection")
        display_msg(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps({"enable_auto_download": True}))
        display_msg(response)
        if type(response) == tuple:
            display_msg("Failure: Enable automatic download in threat protection service")
            assert False
        else:
            get_ref =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(get_ref)[0]['_ref']
            data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data))
            sleep(60)
            assert True
        display_msg("-----------Test Case 10 Execution Completed------------")
    
    
    @pytest.mark.run(order=12)
    def test_011_Perform_snmp_walk1(self):
        """
        Perform snmp walk on member1 LAN interface after enabling TP 
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|          Test Case 11 Execution Started      |")
        display_msg("------------------------------------------------")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.client_ip)
        try:
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('#')
            child.sendline('snmpwalk -v2c -c public -m all ' + config.grid_member1_vip +' -O n &> snmp_walk3.txt\n')
            child.expect('#')
            
            assert True
            
        except Exception as e:
            child.close()
            logger.info("Failure:")
            assert False
        display_msg("-----------Test Case 11 Execution Completed------------")
    
    
    @pytest.mark.run(order=13)
    def test_012_check_Timeout_in_snmpwalk_output(self):
        """
        Validate that snmpwalk got Timeout, since TP is enabled
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|          Test Case 12 Execution Started      |")
        display_msg("------------------------------------------------")
        cmd=('sshpass -p "infoblox" ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@%s' % (config.client_ip))
        cmd = shlex.split(cmd)
        command1 = 'grep -i -c "Timeout: No Response from" snmp_walk3.txt'
        cmd.append(command1)
        
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output = process.communicate()
        print(output[0])
        if int(output[0]) == 1 :
            print("Found Timeout : No Response from")
            assert True
        else:
            assert False
        display_msg("-----------Test Case 12 Execution Completed------------") 

    
    @pytest.mark.run(order=14)        
    def test_013_Perform_snmp_walk_on_member1_MGMT_interface(self):
        """
        Perform snmp walk on member1 MGMT interface after enabling TP
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|          Test Case 13 Execution Started      |")
        display_msg("------------------------------------------------")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.client_ip)
        try:
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('#')
            child.sendline('snmpwalk -v2c -c public -m all ' + config.grid_member1_mgmt +' -O n &> snmp_walk4.txt\n')
            child.expect('#')
            
            assert True
            
        except Exception as e:
            child.close()
            logger.info("Failure:")
            assert False
        display_msg("-----------Test Case 13 Execution Completed------------")
    
    
    @pytest.mark.run(order=15)
    def test_014_check_grid_member1_fqdn_in_snmpwalk_output(self):
        """
        Snmpwalk command should execute properly from mgmt interface
        validate the response for snmpwalk command
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|          Test Case 14 Execution Started      |")
        display_msg("------------------------------------------------")
        cmd=('sshpass -p "infoblox" ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@%s' % (config.client_ip))
        cmd = shlex.split(cmd)
        command1 = 'grep -i -c '+ config.grid_member1_fqdn +' snmp_walk4.txt'
        cmd.append(command1)
        
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output = process.communicate()
        print(output[0])
        if int(output[0]) > 0 :
            print("Found grid oid in smpwalk output")
            assert True
        else:
            assert False
        display_msg("-----------Test Case 14 Execution Completed------------")
    
    
    @pytest.mark.run(order=16)
    def test_015_check_server_status(self):
        """
        check dtc server status
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|         Test Case 15 Execution Started           |")
        display_msg("----------------------------------------------------")
        server=ib_NIOS.wapi_request('GET',object_type='dtc:server?name=server1snmp')
        server1=json.loads(server)[0]['_ref']
        server1status=ib_NIOS.wapi_request('GET',object_type=server1+'?_return_fields=health')
        print(server1status)
        server1status=json.loads(server1status)
        print(type(str(server1status['health']['availability'])))
        server=ib_NIOS.wapi_request('GET',object_type='dtc:server?name=server2snmp')
        server2=json.loads(server)[0]['_ref']
        server2status=ib_NIOS.wapi_request('GET',object_type=server2+'?_return_fields=health')
        print(server2status)
        server2status=json.loads(server2status)
        if server1status['health']['availability'] == server2status['health']['availability'] == "GREEN":
            assert True
        else:
            assert False
        display_msg("-----------Test Case 15 Execution Completed------------")
    

    @pytest.mark.run(order=17)
    def test_016_cleanup(self):
        """
        cleanup method: Delete all the objects created from this script.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|          Test Case cleanup Started           |")
        display_msg("------------------------------------------------")
        display_msg("Disable threat protection service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        ref1 = json.loads(get_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps({"enable_service": False}))
        sleep(30)
        
        display_msg("Delete server pool lbdn")
        lbdn=ib_NIOS.wapi_request('GET',object_type='dtc:lbdn?name=lbdnsnmp')
        lbdn_ref=json.loads(lbdn)[0]['_ref']
        del_lbdn=ib_NIOS.wapi_request('DELETE',ref=lbdn_ref)
        
        pool=ib_NIOS.wapi_request('GET',object_type='dtc:pool?name=poolsnmp')
        pool_ref=json.loads(pool)[0]['_ref']
        del_pool=ib_NIOS.wapi_request('DELETE',ref=pool_ref)
        
        server=ib_NIOS.wapi_request('GET',object_type='dtc:server?name=server1snmp')
        server1=json.loads(server)[0]['_ref']
        del_server1=ib_NIOS.wapi_request('DELETE',ref=server1)

        server=ib_NIOS.wapi_request('GET',object_type='dtc:server?name=server2snmp')
        server2=json.loads(server)[0]['_ref']
        del_server2=ib_NIOS.wapi_request('DELETE',ref=server2)


        zone=ib_NIOS.wapi_request('GET',object_type='zone_auth?fqdn=nios-10766.com')
        zone_ref=json.loads(zone)[0]['_ref']
        del_zone=ib_NIOS.wapi_request('DELETE',ref=zone_ref)

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(5)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(5)

        if type(del_zone) == tuple:
            assert False
        else:
            assert True
        display_msg("-----------Test Cleanup Execution Completed------------")

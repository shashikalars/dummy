#!/usr/bin/env python
__author__ = "Shivasai"
__email__  = "sbandaru@infoblox.com"
########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master + Grid Member UB-FLEX                                                #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415),DTC                                  #
########################################################################################

import os
import re
import config
import pytest
import unittest
import logging
import json
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
    def test_001_enable_snmp(self):
        """
        Enable Snmp
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        get_ref = json.loads(get_ref)[0]['_ref']
        data={"snmp_setting":{"queries_enable":True,"queries_community_string":"public","trap_receivers":[{"address": config.client_ip}],"traps_community_string":"public","traps_enable":True}}
        response = ib_NIOS.wapi_request('PUT', ref=get_ref, fields=json.dumps(data))
        if type(response) == tuple:
            assert False
        else:
            assert True
        display_msg("-----------Test Case 1 Execution Completed------------")

    @pytest.mark.run(order=3)
    def test_002_create_dtc_server_pool_lbdn(self):
        """
        create dtc server pool lbdn
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 2 Execution Started           |")
        display_msg("----------------------------------------------------")
        data={"host": config.server1,"name": "server1snmp"}
        server1_ref=ib_NIOS.wapi_request('POST',object_type='dtc:server',fields=json.dumps(data))
        print(server1_ref)
        data={"host": config.server2,"name": "server2snmp"}
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

    @pytest.mark.run(order=4)
    def test_003_add_snmp_oid(self):
        """
        add snmp oid in health monitors
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|       Test Case 4 Execution Started          |")
        display_msg("------------------------------------------------")
        snmpref=ib_NIOS.wapi_request('GET', object_type="dtc:monitor:snmp")
        snmpref = json.loads(snmpref)[0]['_ref']
        data={"oids": [{"condition": "EXACT","first": "30","oid": ".1.3.6.1.2.1.25.3.8.1.1.30","type": "INTEGER"},{"condition": "EXACT","first": "64","oid": ".1.3.6.1.2.1.4.2.0","type": "INTEGER"}]}
        monitor_ref=ib_NIOS.wapi_request('PUT',ref=snmpref,fields=json.dumps(data))
        print(monitor_ref)
        if type(monitor_ref) == tuple:
            assert False
        else:
            assert True

    @pytest.mark.run(order=5)
    def test_004_enable_threat_protection(self):
        """
        enable threat protection
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 4 Execution Started      |")
        display_msg("------------------------------------------------")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        ref1 = json.loads(get_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps({"enable_service": True}))
        if type(response) == tuple:
            display_msg("Failure: Enable threat protection service")
            assert False
        else:
            get_ref =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=grid)
            ref = json.loads(get_ref)[0]['_ref']
            data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data),grid_vip=grid)
            sleep(30)
            assert True

    @pytest.mark.run(order=6)
    def test_005_enable_automatic_download(self):
        """
        Enable auto download in threat protection service.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 5 Execution Started           |")
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
            get_ref =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=grid)
            ref = json.loads(get_ref)[0]['_ref']
            data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data),grid_vip=grid)
            sleep(60)
            assert True
        
    @pytest.mark.run(order=7)
    def test_006_check_server_status(self):
        """
        check dtc server status
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 6 Execution Started           |")
        display_msg("----------------------------------------------------")
        server=ib_NIOS.wapi_request('GET',object_type='dtc:server?name=server1snmp')
        server1=json.loads(server)[0]['_ref']
        server1status=ib_NIOS.wapi_request('GET',object_type=server1+'?_return_fields=health')
        print(server1status)
        server1status=json.loads(server1status)
        print(type(str(server1status['health']['availability'])))
        server=ib_NIOS.wapi_request('GET',object_type='dtc:server?name=server2snmp')
        server2=json.loads(server)[0]['_ref']
        server2status=ib_NIOS.wapi_request('GET',object_type=server1+'?_return_fields=health')
        print(server2status)
        server2status=json.loads(server1status)
        if str((server1status['health']['availability'])) and str((server2status['health']['availability']))== "GREEN":
            assert True
        else:
            assert False


    @pytest.mark.run(order=8)
    def test_cleanup(self):
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

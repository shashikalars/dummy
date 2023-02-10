"""
 Copyright (c) Infoblox Inc., 2016
 ReportName          :DNS Query Trend per IP Block Group
 ReportCategory      : DNS Query 
 Number of Test cases: 1
 Execution time      : 600 ~ 700 seconds
 Execution Group     : Minute Group (MG)
 Description         : 'DNS Query Trend per IP Block Group' report will be updated every 5 min. 

 Author   : Raghavendra MN
 History  : 06/05/2016 (Created)
 Reviewer : Raghavendra MN
"""
import config
import json
import os
import pytest
import pexpect
import re
import sys
import subprocess
import unittest
import time
from ib_utils.ib_papi import add_ip_block_group 
from ib_utils.ib_papi import remove_ip_block_group
from ib_utils.ib_papi import configure_ip_block_group 
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump 
from ib_utils.ib_system import vlanset
from ib_utils.ib_validaiton import compare_results

"""
TEST Steps:
      1.  Input/Preparation  : Add IP Block Group Say group1, group2, group3 & group4 with different IP address. 
      2.  Search             : Performing Search operaion with default/custom filter
      3.  Validation         : Comparing Search results against inputdata.
"""

class DNSQueryTrendPerIPBlockGroup(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:DNS Query Trend per IP Block Group"+'-'*15)
        logger.info("Configuring IP Block Groups group1:%s, group2:%s, group3:%s,group4:%s and group5:%s", \
	config.client_eth1_ip9,config.client_eth1_ip10,config.client_eth1_ip11,config.client_eth1_ip12,config.client_eth1_ip13)
        add_ip_block_group('group1',config.client_eth1_ip9)
        add_ip_block_group('group2',config.client_eth1_ip10)
        add_ip_block_group('group3',config.client_eth1_ip11)
        add_ip_block_group('group4',config.client_eth1_ip12)
        add_ip_block_group('group5',config.client_eth1_ip13)
        logger.info("Waiting for CSV import operaion completion") 
        time.sleep(60)
        logger.info("Assigning IP Block group in Grid Reporting Properties")
        configure_ip_block_group('group1,group2,group3,group4,group5')
        
        logger.info("Adding zone say 'ip_block_group.com'")
        zone1 = {"fqdn":"ip_block_group.com","view":"default","grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(zone1))
  
        logger.info("Restarting DNS Service")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        logger.info("Waiting 60 sec., for Service restart operation")
        time.sleep(60)

      
        epoc=ib_get.indexer_epoch_time(config.indexer_ip)
        minute=int(time.strftime('%M',time.gmtime(int(epoc))))
        t=minute%5
        wait_time = (5-t)*60
        new_epoc = int(epoc)+wait_time 
        new_min =int(time.strftime('%M',time.gmtime(new_epoc)))
        ts = time.strftime('%Y-%m-%dT%H', time.gmtime(new_epoc))
        ms = (new_min) - ((new_min)%5)
        new_minute= '0'+str(ms) if ms <=9 else str(ms) #'00' format

        logger.info("Waiting for %d sec., to perform dig operation",wait_time) 
        time.sleep(wait_time)

        
        logger.info("Performing dig operation from differnt netwrok ips which are belongs to group1, group2, group3, group4 & grout5")
        #VLAN SET
        vlanset(config.client_vm,"10.34.220.0")
        #Configure Client#9
        os.system("sudo ifconfig eth1 inet "+config.client_eth1_ip9+" netmask "+config.client_netmask+" up")
        os.system("dig @"+config.grid_vip+" -f ib_data/DNS_Query/DNS_Query_Trend_Per_IP_Block_Group/group1.txt -b "+config.client_eth1_ip9 +" > /dev/null 2>&1")
        #time.sleep(5)
        os.system("sudo ifconfig eth1 inet "+config.client_eth1_ip9+" netmask "+config.client_netmask+" down")

        #Configure Client#10
        os.system("sudo ifconfig eth1 inet "+config.client_eth1_ip10+" netmask "+config.client_netmask+" up")
        os.system("dig @"+config.grid_vip+" -f ib_data/DNS_Query/DNS_Query_Trend_Per_IP_Block_Group/group2.txt -b "+config.client_eth1_ip10 +" > /dev/null 2>&1")
        #time.sleep(5)
        os.system("sudo ifconfig eth1 inet "+config.client_eth1_ip10+" netmask "+config.client_netmask+" down")

        #Configure Client#11
        os.system("sudo ifconfig eth1 inet "+config.client_eth1_ip11+" netmask "+config.client_netmask+" up")
        os.system("dig @"+config.grid_vip+" -f ib_data/DNS_Query/DNS_Query_Trend_Per_IP_Block_Group/group3.txt -b "+config.client_eth1_ip11 +" > /dev/null 2>&1")
        #time.sleep(5)
        os.system("sudo ifconfig eth1 inet "+config.client_eth1_ip11+" netmask "+config.client_netmask+" down")

        #Configure Client#12
        os.system("sudo ifconfig eth1 inet "+config.client_eth1_ip12+" netmask "+config.client_netmask+" up")
        os.system("dig @"+config.grid_vip+" -f ib_data/DNS_Query/DNS_Query_Trend_Per_IP_Block_Group/group4.txt -b "+config.client_eth1_ip12 +" > /dev/null 2>&1")
        #time.sleep(5)
        os.system("sudo ifconfig eth1 inet "+config.client_eth1_ip12+" netmask "+config.client_netmask+" down")

        #Configure Client#13
        os.system("sudo ifconfig eth1 inet "+config.client_eth1_ip13+" netmask "+config.client_netmask+" up")
        os.system("dig @"+config.grid_vip+" -f ib_data/DNS_Query/DNS_Query_Trend_Per_IP_Block_Group/group5.txt -b "+config.client_eth1_ip13 +" > /dev/null 2>&1")
        #time.sleep(5)
        os.system("sudo ifconfig eth1 inet "+config.client_eth1_ip13+" netmask "+config.client_netmask+" down")

        time_stamp=ts+":"+new_minute+":00.000+00:00"
        cls.test1=[ \
        {"_time":time_stamp, "Query Count":"1000","Group":"\"group1\""}, \
        {"_time":time_stamp, "Query Count":"900","Group":"\"group2\""}, \
        {"_time":time_stamp, "Query Count":"800","Group":"\"group3\""}, \
        {"_time":time_stamp, "Query Count":"700","Group":"\"group4\""}, \
        {"_time":time_stamp, "Query Count":"600","Group":"\"group5\""}]

        logger.info ("Input Json for validation")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))
        logger.info ("Waiting for 5 min for updating reports")
        time.sleep(300) #wait till reports gets udpated

    def test_1_dns_query_trend_per_ip_block_group(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        search_str=r"search source=ib:dns:query:ip_block_group index=ib_dns | lookup dns_viewkey_displayname_lookup VIEW output display_name | bucket span=5m _time | stats sum(QCOUNT) as QCOUNT by _time, IP_BLOCK_GROUP | rename IP_BLOCK_GROUP as \"Group\", QCOUNT as \"Query Count\""
        cmd = config.search_py + " \"" + search_str + "\" --output_mode=json"
        logger.info (cmd)
        os.system(cmd)
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Looks like reporting service not started please check the GRID")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        results_dist= results_list[-240::1]
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test1,results_dist)  
	logger.info("compare_resutls with 'delta' value as 0")
        result = compare_results(self.test1,results_list,0)
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg

    @classmethod
    def teardown_class(cls):
        logger.info("Removing IP Block Configuraiton from Grid Reporting Properties")
        remove_ip_block_group('group1,group2,group3,group4,group5')
        logger.info("Cleanup deleting added zones")
        del_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn~=ip_block_group.com")
        ref = json.loads(del_zone)[0]['_ref']
        del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)

        logger.info("Restaring DNS Service")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        logger.info('-'*15+"END:DNS Query Trend per IP Block Group"+'-'*15)



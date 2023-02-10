"""
 Copyright (c) Infoblox Inc., 2016

 Report Name           : DNS Traffic Control Resource Distribution trend (Detailed)
 Report Category       : DNS Traffic Control
 Number of Test cases  : 1 
 Execution time        : 842 seconds
 Execution Group       : Minute Group (MG)
 Description           : Validating Response Distribution trend with Server response count as per Query answered by the DTC server. this Report will update immediately after 10 minutes.
 
 Author 	       : Sunil Kumar Nagaraju
 History 	       : 05/23/2016 (Created)
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

import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results

"""
TEST Steps:
	1.  Input/Preparation  : 
            a) Add Zone dtc.com with Master as Grid Primary. 
	    b) Add DTC servers as, 
		1) server1 - 10.120.21.51 	(Status : Running)
		2) server2 - 10.120.22.146 	(Status : Running)
		3) server3 - 1.1.1.1 		(Status : Error) 
		4) server4 - 1.1.1.2 		(Status : Error)
		5) server5 - 10.120.21.236 	(Status : Running)
		6) server6 - 1.1.1.3 		(Status : Error)
	    c) Add DTC Pool as,
		1) pool1 - server1		(Status : Running)
		2) pool2 - server2 		(Status : Running)
		3) pool3 - server3 		(Status : Error)
		4) pool4 - server4 		(Status : Error)
		5) pool5 - server5 & server6.	(Status : Warning)
	    d) Add DTC LBDN as, 
		1) lbdn1 - a1.dtc.com, pool1 	(Status : Running)
		2) lbdn2 - a2.dtc.com, pool2	(Status : Running) 
		3) lbdn3 - a3.dtc.com, pool3 	(Status : Error)
		4) lbdn4 - a4.dtc.com, pool4 	(Status : Error)
		5) lbdn5 - a5.dtc.com, pool5	(Status : Warning)
	    e) Reports :
		1) DNS Traffic Control Response Distribution Trend (Detailed)
	 		Report will show Query distributed count on DTC servers, 
			a)server1 = 100 					b) server2 = 50		
			c) server3, server4 & server6 = 0   and			d) server5 = 75

	2.  Search     : Performing Search operation with default/custom filter
	3.  Validation : comparing Search results with Retrieved 'DNS Traffic Control Response Distribution trend' report with delta=1.
"""

class dnstrafficcontrolresponsedistributiontrend(unittest.TestCase):
    @classmethod
    def setup_class(cls):
	logger.info('-'*15+"START:DNS Traffic Control Response Distribution Trend"+'-'*15)
	logger.info("Add Zone dtc.com")
	zone1 = {"fqdn":"dtc.com","view":"default","grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
	zone1_response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(zone1))			       
        zone1_get = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn~=dtc.com")
        zone1_ref = json.loads(zone1_get)[0]['_ref']
	
	logger.info("Add DTC Server 'server1' with host '10.120.21.51'")
        server1 = {"name":"server1","host":"10.120.21.51"}
        server1_response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(server1))
	
	logger.info("Add DTC Server 'server2' with host '10.120.22.146'")
        server2 = {"name":"server2","host":"10.120.22.146"}
        server2_response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(server2))

	logger.info("Add DTC Server 'server3' with host '1.1.1.1'")
        server3 = {"name":"server3","host":"1.1.1.1"}
        server3_response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(server3))

	logger.info("Add DTC Server 'server4' with host '1.1.1.2'")
        server4 = {"name":"server4","host":"1.1.1.2"}
        server4_response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(server4))

	logger.info("Add DTC Server 'server5' with host '10.120.21.236'")
        server5 = {"name":"server5","host":"10.120.21.236"}
        server5_response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(server5))

	logger.info("Add DTC Server 'server6' with host '1.1.1.3'")
        server6 = {"name":"server6","host":"1.1.1.3"}
        server6_response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(server6))

	logger.info("Add DTC Pool 'pool1' with servers= server1, monitors=icmp")
	icmp_monitor_get = ib_NIOS.wapi_request('GET', object_type="dtc:monitor:icmp?name~=icmp")
        icmp_monitor_ref = json.loads(icmp_monitor_get)[0]['_ref']
	
        server1_get = ib_NIOS.wapi_request('GET', object_type="dtc:server?name~=server1")
	server1_ref = json.loads(server1_get)[0]['_ref']

        pool1 = {"name":"pool1","lb_preferred_method":"ROUND_ROBIN","servers":[{"server":server1_ref}],"monitors":[icmp_monitor_ref]}
        pool1_response = ib_NIOS.wapi_request('POST', object_type="dtc:pool", fields=json.dumps(pool1))
        pool1_get = ib_NIOS.wapi_request('GET', object_type="dtc:pool?name~=pool1")
        pool1_ref = json.loads(pool1_get)[0]['_ref']
	
	logger.info("Add DTC Pool 'pool2' with servers= server2, monitors=icmp")
        server2_get = ib_NIOS.wapi_request('GET', object_type="dtc:server?name~=server2")
        server2_ref = json.loads(server2_get)[0]['_ref']

        pool2 = {"name":"pool2","lb_preferred_method":"ROUND_ROBIN","servers":[{"server":server2_ref}],"monitors":[icmp_monitor_ref]}
        pool2_response = ib_NIOS.wapi_request('POST', object_type="dtc:pool", fields=json.dumps(pool2))
        pool2_get = ib_NIOS.wapi_request('GET', object_type="dtc:pool?name~=pool2")
        pool2_ref = json.loads(pool2_get)[0]['_ref']
		
	logger.info("Add DTC Pool 'pool3' with servers= server3, monitors=icmp")
        server3_get = ib_NIOS.wapi_request('GET', object_type="dtc:server?name~=server3")
        server3_ref = json.loads(server3_get)[0]['_ref']

        pool3 = {"name":"pool3","lb_preferred_method":"ROUND_ROBIN","servers":[{"server":server3_ref}],"monitors":[icmp_monitor_ref]}
        pool3_response = ib_NIOS.wapi_request('POST', object_type="dtc:pool", fields=json.dumps(pool3))
        pool3_get = ib_NIOS.wapi_request('GET', object_type="dtc:pool?name~=pool3")
        pool3_ref = json.loads(pool3_get)[0]['_ref']
		
	logger.info("Add DTC Pool 'pool4' with servers= server4, monitors=icmp")
        server4_get = ib_NIOS.wapi_request('GET', object_type="dtc:server?name~=server4")
        server4_ref = json.loads(server4_get)[0]['_ref']

        pool4 = {"name":"pool4","lb_preferred_method":"ROUND_ROBIN","servers":[{"server":server4_ref}],"monitors":[icmp_monitor_ref]}
        pool4_response = ib_NIOS.wapi_request('POST', object_type="dtc:pool", fields=json.dumps(pool4))
        pool4_get = ib_NIOS.wapi_request('GET', object_type="dtc:pool?name~=pool4")
        pool4_ref = json.loads(pool4_get)[0]['_ref']
		
	logger.info("Add DTC Pool 'pool5' with servers= server5&server6, monitors=icmp")
        server5_get = ib_NIOS.wapi_request('GET', object_type="dtc:server?name~=server5")
        server5_ref = json.loads(server5_get)[0]['_ref']
        server6_get = ib_NIOS.wapi_request('GET', object_type="dtc:server?name~=server6")
        server6_ref = json.loads(server6_get)[0]['_ref']		

        pool5 = {"name":"pool5","lb_preferred_method":"ROUND_ROBIN","servers":[{"server":server5_ref},{"server":server6_ref}],"monitors":[icmp_monitor_ref]}
        pool5_response = ib_NIOS.wapi_request('POST', object_type="dtc:pool", fields=json.dumps(pool5))
        pool5_get = ib_NIOS.wapi_request('GET', object_type="dtc:pool?name~=pool5")
        pool5_ref = json.loads(pool5_get)[0]['_ref']
	
	logger.info("Add DTC LBDN 'lbdn1' with pool= pool1, zones=dtc.com, pattern=a1.dtc.com")
        lbdn1 = {"name":"lbdn1","lb_method":"ROUND_ROBIN","pools":[{"pool":pool1_ref}],"types":["A","AAAA","NAPTR"],"patterns":["a1.dtc.com"],"auth_zones":[zone1_ref]}
        lbdn1_response = ib_NIOS.wapi_request('POST', object_type="dtc:lbdn", fields=json.dumps(lbdn1))
	
	logger.info("Add DTC LBDN 'lbdn2' with pool= pool2, zones=dtc.com, pattern=a2.dtc.com")
        lbdn2 = {"name":"lbdn2","lb_method":"ROUND_ROBIN","pools":[{"pool":pool2_ref}],"types":["A","AAAA","NAPTR"],"patterns":["a2.dtc.com"],"auth_zones":[zone1_ref]}
        lbdn2_response = ib_NIOS.wapi_request('POST', object_type="dtc:lbdn", fields=json.dumps(lbdn2))
	
	logger.info("Add DTC LBDN 'lbdn3' with pool= pool3, zones=dtc.com, pattern=a3.dtc.com")
        lbdn3 = {"name":"lbdn3","lb_method":"ROUND_ROBIN","pools":[{"pool":pool3_ref}],"types":["A","AAAA","NAPTR"],"patterns":["a3.dtc.com"],"auth_zones":[zone1_ref]}
        lbdn3_response = ib_NIOS.wapi_request('POST', object_type="dtc:lbdn", fields=json.dumps(lbdn3))
	
	logger.info("Add DTC LBDN 'lbdn4' with pool= pool4, zones=dtc.com, pattern=a4.dtc.com")
        lbdn4 = {"name":"lbdn4","lb_method":"ROUND_ROBIN","pools":[{"pool":pool4_ref}],"types":["A","AAAA","NAPTR"],"patterns":["a4.dtc.com"],"auth_zones":[zone1_ref]}
        lbdn4_response = ib_NIOS.wapi_request('POST', object_type="dtc:lbdn", fields=json.dumps(lbdn4))

	logger.info("Add DTC LBDN 'lbdn5' with pool= pool5, zones=dtc.com, pattern=a5.dtc.com")
        lbdn5 = {"name":"lbdn5","lb_method":"ROUND_ROBIN","pools":[{"pool":pool5_ref}],"types":["A","AAAA","NAPTR"],"patterns":["a5.dtc.com"],"auth_zones":[zone1_ref]}
        lbdn5_response = ib_NIOS.wapi_request('POST', object_type="dtc:lbdn", fields=json.dumps(lbdn5))

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        time.sleep(25) 

        epoc=ib_get.indexer_epoch_time(config.indexer_ip)
        minute=int(time.strftime('%M',time.gmtime(int(epoc))))
        t=minute%10
        wait_time = (10-t)*60
        logger.info('Waiting for Restart operation %s', wait_time)
        time.sleep(wait_time)

	logger.info('Queryperf for DTC')
	fin1=os.popen("/usr/bin/queryperf -s "+config.grid_vip+" -d ib_data/DNS_Traffic_Control/DNS_Traffic_Control_Response_Distribution_Trend/input.txt")
	logger.info("%s",''.join(fin1.readlines()))

        cls.test1=[
	{"server1":"100.000000","server2":"50.000000","server3":"0.000000","server4":"0.000000","server5":"75.000000","server6":"0.000000"}]
	logger.info ("Input Json Data for DNS Traffic Control Response Distribution Trend report validation")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))

        logger.info ("Wait 10 minutes for reports to get update")
        time.sleep(700)

    def test_1_dns_traffic_control_response_distribution_trend(self):
        logger.info("Test:"+sys._getframe().f_code.co_name)    
	search_str=r"search sourcetype=ib:dns:reserved source=/infoblox/var/reporting/idns_res_resp.csv index=ib_dtc | bucket span=10m _time | stats sum(response_count) as response_count by _time, resource | timechart bins=1000 avg(response_count) by resource"
        cmd = config.search_py + " \"" + search_str + "\" --output_mode=json"
        logger.info (cmd)
        os.system(cmd)
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operation failed, Please check Grid Configuration")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        results_dist= results_list[-240::1]
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test1,results_dist)
        logger.info("compare_results with 'delta=1'")
        result = compare_results(self.test1,results_list,1)
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg

    @classmethod
    def teardown_class(cls):
        logger.info("Cleanup: Delete all DTC Objects and Zone Associated with it")
	
	lbdn1_get = ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?name~=lbdn1")
        lbdn1_ref = json.loads(lbdn1_get)[0]['_ref']
	lbdn1del_status = ib_NIOS.wapi_request('DELETE', object_type = lbdn1_ref)
		
	lbdn2_get = ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?name~=lbdn2")
        lbdn2_ref = json.loads(lbdn2_get)[0]['_ref']
	lbdn2del_status = ib_NIOS.wapi_request('DELETE', object_type = lbdn2_ref)
		
	lbdn3_get = ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?name~=lbdn3")
        lbdn3_ref = json.loads(lbdn3_get)[0]['_ref']
	lbdn3del_status = ib_NIOS.wapi_request('DELETE', object_type = lbdn3_ref)
		
	lbdn4_get = ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?name~=lbdn4")
        lbdn4_ref = json.loads(lbdn4_get)[0]['_ref']
	lbdn4del_status = ib_NIOS.wapi_request('DELETE', object_type = lbdn4_ref)
		
	lbdn5_get = ib_NIOS.wapi_request('GET', object_type="dtc:lbdn?name~=lbdn5")
        lbdn5_ref = json.loads(lbdn5_get)[0]['_ref']
	lbdn5del_status = ib_NIOS.wapi_request('DELETE', object_type = lbdn5_ref)
		
	pool1_get = ib_NIOS.wapi_request('GET', object_type="dtc:pool?name~=pool1")
        pool1_ref = json.loads(pool1_get)[0]['_ref']
	pool1del_status = ib_NIOS.wapi_request('DELETE', object_type = pool1_ref)
	
        pool2_get = ib_NIOS.wapi_request('GET', object_type="dtc:pool?name~=pool2")
        pool2_ref = json.loads(pool2_get)[0]['_ref']
	pool2del_status = ib_NIOS.wapi_request('DELETE', object_type = pool2_ref)
		
        pool3_get = ib_NIOS.wapi_request('GET', object_type="dtc:pool?name~=pool3")
        pool3_ref = json.loads(pool3_get)[0]['_ref']
	pool3del_status = ib_NIOS.wapi_request('DELETE', object_type = pool3_ref)
		
        pool4_get = ib_NIOS.wapi_request('GET', object_type="dtc:pool?name~=pool4")
        pool4_ref = json.loads(pool4_get)[0]['_ref']
	pool4del_status = ib_NIOS.wapi_request('DELETE', object_type = pool4_ref)
		
        pool5_get = ib_NIOS.wapi_request('GET', object_type="dtc:pool?name~=pool5")
        pool5_ref = json.loads(pool5_get)[0]['_ref']
	pool5del_status = ib_NIOS.wapi_request('DELETE', object_type = pool5_ref)	
	
	server1_get = ib_NIOS.wapi_request('GET', object_type="dtc:server?name~=server1")
	server1_ref = json.loads(server1_get)[0]['_ref']
	server1del_status = ib_NIOS.wapi_request('DELETE', object_type = server1_ref)
		
	server2_get = ib_NIOS.wapi_request('GET', object_type="dtc:server?name~=server2")
	server2_ref = json.loads(server2_get)[0]['_ref']
	server2del_status = ib_NIOS.wapi_request('DELETE', object_type = server2_ref)
		
	server3_get = ib_NIOS.wapi_request('GET', object_type="dtc:server?name~=server3")
	server3_ref = json.loads(server3_get)[0]['_ref']
	server3del_status = ib_NIOS.wapi_request('DELETE', object_type = server3_ref)
		
	server4_get = ib_NIOS.wapi_request('GET', object_type="dtc:server?name~=server4")
	server4_ref = json.loads(server4_get)[0]['_ref']
	server4del_status = ib_NIOS.wapi_request('DELETE', object_type = server4_ref)
		
	server5_get = ib_NIOS.wapi_request('GET', object_type="dtc:server?name~=server5")
	server5_ref = json.loads(server5_get)[0]['_ref']
	server5del_status = ib_NIOS.wapi_request('DELETE', object_type = server5_ref)
		
	server6_get = ib_NIOS.wapi_request('GET', object_type="dtc:server?name~=server6")
	server6_ref = json.loads(server6_get)[0]['_ref']
	server6del_status = ib_NIOS.wapi_request('DELETE', object_type = server6_ref)

        del_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn~=dtc.com")
        ref = json.loads(del_zone)[0]['_ref']
        del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        logger.info('Grid Restart services after cleanup')
        time.sleep(30)
	
	logger.info('-'*15+"END: DNS Traffic Control Response Distribution Trend"+'-'*15)

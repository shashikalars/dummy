"""
 Copyright (c) Infoblox Inc., 2016

 Report Name          	: 	1) DNS Traffic Control Resource Availability Trend (Detailed) 
				2) DNS Traffic Control Resource Pool Availability Trend (Detailed)
					   
 Report Category      	: 	DNS Traffic Control
 Number of Test cases	: 	2
 Execution time     	: 	702.61 seconds
 Execution Group     	: 	Minute Group (MG)
 Description         	: 	Validating Resource Availability Trend by Server health status, this Report will update immediately after 10 minutes. 
				Validating Pool Availability Trend by Pool health status, this Report will update immediately after 10 minutes.
					   
 Author			:	Sunil Kumar Nagaraju
 History		:	05/27/2016 (Created)
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
		1) server1 - 10.120.21.249 	(Status : Error,  2 out of 3 monitors in error status, 33.34%)
		2) server2 - 10.120.21.204 	(Status : Error,  1 out of 2 monitors in error status, 50.00%)
		3) server3 - 10.120.21.33	(Status : Error,  2 out of 2 monitors in error status, 0) 
		4) server4 - 10.120.20.151	(Status : Error,  1 out of 3 monitors in error status, 66.67%)
		5) server5 - 10.120.21.139 	(Status : Running, 100% )
		6) server6 - 1.1.1.1		(Status : Error, Dummy IP, 0)
	    c) Add DTC Pool as,
		1) pool1 - server1				, Monitors : ICMP, SIP, PDP			(Status : Warning)
		2) pool2 - server2 				, Monitors : ICMP, SIP 				(Status : Warning)
		3) pool3 - server3 				, Monitors : SIP, PDP  				(Status : Error)
		4) pool4 - server4 				, Monitors : ICMP, TCP, SIP			(Status : Error)
		5) pool5 - server5 & server6. 	, Monitors : ICMP					(Status : Warning)
	    d) Add DTC LBDN as, 
		1) lbdn1 - a1.dtc.com, pool1 	(Status : Running)
		2) lbdn2 - a2.dtc.com, pool2	(Status : Running) 
		3) lbdn3 - a3.dtc.com, pool3 	(Status : Error)
		4) lbdn4 - a4.dtc.com, pool4 	(Status : Error)
		5) lbdn5 - a5.dtc.com, pool5	(Status : Warning)
	    e) Reports :
		1) DNS Traffic Control Resource Availability Trend (Detailed).
		      Report will show Server Availability based on health status of DTC servers, 
			a)server1 = 33.34% 	b) server2 = 50%	c) server3 = 0%		d)server4 = 66.67%	  e)server5 = 100%   and f) server6 = 0%
		2) DNS Traffic Control Resource Pool Availability Trend (Detailed).
			Report will show pool Availability based on status of DTC servers,
			a) pool1 	b) pool2 = 		c) pool3 = 		d) pool4 = 		e) pool5 = 
				
	2.  Search     : Performing Search operation with default/custom filter
	3.  Validation : comparing Search results with Retrieved 'DNS Traffic Control Resource Pool/Resource Availability Trend' with delta=.5.
"""

class dnstrafficcontrolresourceavailabilitytrend(unittest.TestCase):
    @classmethod
    def setup_class(cls):
	logger.info('-'*15+"START : DNS Traffic Control Pool/Resource Availability Trend"+'-'*15)
	logger.info("Add Zone dtc.com")
	zone1 = {"fqdn":"dtc.com","view":"default","grid_primary": [{"name": config.grid_fqdn,"stealth": False}]}
	zone1_response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(zone1))			       
	zone1_get = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn~=dtc.com")
    	zone1_ref = json.loads(zone1_get)[0]['_ref']
	
	logger.info("Add DTC Server 'server1' with host '10.120.21.249'")
    	server1 = {"name":"server1","host":"10.120.21.249"}
    	server1_response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(server1))
	
	logger.info("Add DTC Server 'server2' with host '10.120.21.204'")
    	server2 = {"name":"server2","host":"10.120.21.204"}
    	server2_response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(server2))

	logger.info("Add DTC Server 'server3' with host '10.120.21.33'")
    	server3 = {"name":"server3","host":"10.120.21.33"}
    	server3_response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(server3))

	logger.info("Add DTC Server 'server4' with host '10.120.20.151'")
    	server4 = {"name":"server4","host":"10.120.20.151"}
    	server4_response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(server4))

	logger.info("Add DTC Server 'server5' with host '10.120.21.139'")
    	server5 = {"name":"server5","host":"10.120.21.139"}
    	server5_response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(server5))

	logger.info("Add DTC Server 'server6' with host '1.1.1.1'")
    	server6 = {"name":"server6","host":"1.1.1.1"}
    	server6_response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(server6))

	logger.info("Add DTC Pool 'pool1' with servers= server1, monitors=icmp")
	icmp_monitor_get = ib_NIOS.wapi_request('GET', object_type="dtc:monitor:icmp?name~=icmp")
    	icmp_monitor_ref = json.loads(icmp_monitor_get)[0]['_ref']
	
	pdp_monitor_get = ib_NIOS.wapi_request('GET', object_type="dtc:monitor:pdp?name~=pdp")
    	pdp_monitor_ref = json.loads(pdp_monitor_get)[0]['_ref']
	
	sip_monitor_get = ib_NIOS.wapi_request('GET', object_type="dtc:monitor:sip?name~=sip")
    	sip_monitor_ref = json.loads(sip_monitor_get)[0]['_ref']
	
	tcp = {"name":"tcp","port":22}
	tcp_response = ib_NIOS.wapi_request('POST', object_type="dtc:monitor:tcp", fields=json.dumps(tcp))
	tcp_monitor_get = ib_NIOS.wapi_request('GET', object_type="dtc:monitor:tcp?name~=tcp")
    	tcp_monitor_ref = json.loads(tcp_monitor_get)[0]['_ref']	
	
    	server1_get = ib_NIOS.wapi_request('GET', object_type="dtc:server?name~=server1")
	server1_ref = json.loads(server1_get)[0]['_ref']

    	pool1 = {"name":"pool1","lb_preferred_method":"ROUND_ROBIN","servers":[{"server":server1_ref}],"monitors":[icmp_monitor_ref,pdp_monitor_ref,sip_monitor_ref]}
    	pool1_response = ib_NIOS.wapi_request('POST', object_type="dtc:pool", fields=json.dumps(pool1))
    	pool1_get = ib_NIOS.wapi_request('GET', object_type="dtc:pool?name~=pool1")
    	pool1_ref = json.loads(pool1_get)[0]['_ref']
	
	logger.info("Add DTC Pool 'pool2' with servers= server2, monitors=icmp")
    	server2_get = ib_NIOS.wapi_request('GET', object_type="dtc:server?name~=server2")
    	server2_ref = json.loads(server2_get)[0]['_ref']

    	pool2 = {"name":"pool2","lb_preferred_method":"ROUND_ROBIN","servers":[{"server":server2_ref}],"monitors":[icmp_monitor_ref,sip_monitor_ref]}
    	pool2_response = ib_NIOS.wapi_request('POST', object_type="dtc:pool", fields=json.dumps(pool2))
    	pool2_get = ib_NIOS.wapi_request('GET', object_type="dtc:pool?name~=pool2")
    	pool2_ref = json.loads(pool2_get)[0]['_ref']
		
	logger.info("Add DTC Pool 'pool3' with servers= server3, monitors=icmp")
    	server3_get = ib_NIOS.wapi_request('GET', object_type="dtc:server?name~=server3")
    	server3_ref = json.loads(server3_get)[0]['_ref']

    	pool3 = {"name":"pool3","lb_preferred_method":"ROUND_ROBIN","servers":[{"server":server3_ref}],"monitors":[pdp_monitor_ref,sip_monitor_ref]}
    	pool3_response = ib_NIOS.wapi_request('POST', object_type="dtc:pool", fields=json.dumps(pool3))
    	pool3_get = ib_NIOS.wapi_request('GET', object_type="dtc:pool?name~=pool3")
    	pool3_ref = json.loads(pool3_get)[0]['_ref']
		
	logger.info("Add DTC Pool 'pool4' with servers= server4, monitors=icmp")
    	server4_get = ib_NIOS.wapi_request('GET', object_type="dtc:server?name~=server4")
    	server4_ref = json.loads(server4_get)[0]['_ref']

    	pool4 = {"name":"pool4","lb_preferred_method":"ROUND_ROBIN","servers":[{"server":server4_ref}],"monitors":[icmp_monitor_ref,tcp_monitor_ref,sip_monitor_ref]}
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

        epoc=ib_get.indexer_epoch_time(config.indexer_ip)
        minute=int(time.strftime('%M',time.gmtime(int(epoc))))
        t=minute%10
        wait_time = (10-t)*60
        logger.info('Waiting for Restart operation %s', wait_time)
        time.sleep(wait_time)

    	grid =  ib_NIOS.wapi_request('GET', object_type="grid")
    	ref = json.loads(grid)[0]['_ref']
    	request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
    	restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")

	cls.test1=[
	{"server1":"33.333333","server2":"50.000000","server3":"0.000000","server4":"66.666667","server5":"100.000000","server6":"0.000000"}]
	logger.info ("Input Json data for validation of DNS Traffic Control Resource Availability trend report")
    	logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))

	cls.test2=[
	{"pool1":"100.000000","pool2":"100.000000","pool3":"0.000000","pool4":"0.000000","pool5":"100.000000"}]
	logger.info ("Input Json data for validation of DNS Traffic Control Resource Pool Availability Trend report")
    	logger.info(json.dumps(cls.test2, sort_keys=True, indent=4, separators=(',', ': ')))	

        logger.info ("Wait 15 minutes for reports to get update")
        time.sleep(900)
		
    def test_1_dns_traffic_control_resource_availability_trend(self):
        logger.info("Test:"+sys._getframe().f_code.co_name)       
	search_str=r"search sourcetype=ib:dns:reserved source=/infoblox/var/reporting/idns_res_avail.csv index=ib_dtc | bucket span=10m _time | stats sum(available) as available, sum(unavailable) as unavailable by _time, resource | eval percent = 100*available/(available + unavailable) | timechart bins=1000 avg(percent) by resource"
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
	logger.info("compare_resutls with 'delta'=.5")
        result = compare_results(self.test1,results_list,.5)
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg

    def test_2_dns_traffic_control_resource_pool_availability_trend(self):
        logger.info("Test:"+sys._getframe().f_code.co_name)
	search_str=r"search sourcetype=ib:dns:reserved source=/infoblox/var/reporting/idns_res_pool_avail.csv index=ib_dtc | bucket span=10m _time | stats sum(available) as available, sum(unavailable) as unavailable by _time, pool | eval percent = 100*available/(available + unavailable) | timechart bins=1000 avg(percent) by pool"
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
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test2,results_dist)
	logger.info("compare_resutls with 'delta'=.5")
        result = compare_results(self.test2,results_list,.5)
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
		
	del_tcp_monitor = ib_NIOS.wapi_request('GET', object_type="dtc:monitor:tcp?name~=tcp")
	ref = json.loads(del_tcp_monitor)[0]['_ref']
	del_tcp_status = ib_NIOS.wapi_request('DELETE', object_type = ref)	
		
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        logger.info('Grid Restart Service after Cleanup')
        time.sleep(30)
	
	logger.info('-'*15+"END:DNS Traffic Control Resource/Pool Availability Trend"+'-'*15)

#############################################################################
#!/usr/bin/env python
__author__ ="Vijaya Sinha"
__email__  = "vsinha@infoblox.com"
#############################################################################
# Bug Description : NIOSSPT-10954                                      #
#  Grid Set up required:                                                    #
#  Confire 2 grids
# grid1 should be IB-4030, member added should be IB-Flex
###########################################################################


import re
import config
import pytest
import unittest
import logging
import os
import os.path
from os.path import join
import subprocess
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
import pexpect
import sys




class NIOSSPT_10954(unittest.TestCase):

#Starting DNS service

        @pytest.mark.run(order=1)
        def test_001_Start_DNS_Service(self):
                logging.info("Start DNS Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                for i in res:
                        logging.info("Modify a enable_dns")
                        data = {"enable_dns": True}
                        response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                        print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 1 Execution Completed")


	@pytest.mark.run(order=2)
        def test_002_Validate_DNS_service_Enabled(self):
                logging.info("Validate DNs Service is enabled")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                for i in res:
                        print i
                        logging.info("found")
                        assert i["enable_dns"] == True
                print("Test Case 2 Execution Completed")



	@pytest.mark.run(order=3)
        def test_003_Configure_Logging_Categories_At_Grid_level(self):
                logging.info("Configure Logging Categoriesat Grid level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify Grid DNS Properties")
                data = {"logging_categories": {"log_queries": True,"log_query_rewrite": True,"log_responses": True,"log_rpz": True}}
                response = ib_NIOS.wapi_request('PUT',ref= ref1,fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 3 Execution Completed")

        @pytest.mark.run(order=4)
        def test_004_Validate_Logging_Categories_At_Grid_level(self):
                logging.info("Validate Configured logging Categories at Grid level")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="grid:dns",params="?_return_fields=logging_categories")
                res = json.loads(get_tacacsplus)
                res = eval(json.dumps(get_tacacsplus))
                print(res)
                output=res.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                print(output)
                result = 'log_client:true,log_config:true,log_database:true,log_dnssec:true,log_dtc_gslb:false,log_dtc_health:false,log_general:true,log_lame_servers:true,log_network:true,log_notify:true,log_queries:true,log_query_rewrite:true,log_rate_limit:true,log_resolver:true,log_responses:true,log_rpz:true,log_security:true,log_update:true,log_update_security:true,log_xfer_in:true,log_xfer_out:true'
                for i in result:
                  if i in output:
                        assert True
                  else:
                        assert False
                print(result)
                logging.info("Test Case 4 Execution Completed")

	@pytest.mark.run(order=5)
        def test_005_Start_DCA_Service(self):
                logging.info("Start DCA Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                for i in res:
                        logging.info("Modify a enable_dca")
                        data = {"enable_dns_cache_acceleration": True}
                        response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                        print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 5 Execution Completed")

	@pytest.mark.run(order=6)
        def test_006_Start_TP_Service_on_member(self):
                logging.info("Start TP service on member")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
                logging.info(get_ref)
                res = json.loads(get_ref)
                for i in res:
                        logging.info("enable_TP")
                        data = {"enable_service": True}
                        response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                        print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 6 Execution Completed")

	@pytest.mark.run(order=7)
        def test_007_Add_subscriber_site(self):
		logging.info("Add Subscriber Site")
        	data={"name": "site1","nas_port": 1813,"members": [{"name": config.grid_fqdn},{"name": config.grid_member1_fqdn}],"nas_gateways": [{"ip_address": "10.35.6.80","name": "NAS","shared_secret":"testing123","send_ack": True},{"ip_address": "10.36.6.80","name": "NAS","shared_secret":"testing123","send_ack": True}]}
		subs_site = ib_NIOS.wapi_request('POST', object_type="parentalcontrol:subscribersite",fields=json.dumps(data))
        	print(subs_site)
        	if type(subs_site) == tuple:
            		if subs_site[0]==400 or subs_site[0]==401:
				print("Failure: Adding subscriber site")
                	assert False
		print("Test Case 7 Execution Completed")


	@pytest.mark.run(order=8)
        def test_008_Update_Interim_Accounting_Interval_to_60min(self):
		logging.info("Update Interim Accounting Interval to 60min")
        	get_ref = ib_NIOS.wapi_request('GET', object_type='parentalcontrol:subscriber')
        	response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps({"interim_accounting_interval":120}))
        	if type(response) == tuple:
            		if response[0]==400 or response[0]==401:
                		print("Failure: Updating Interim Accounting Interval to 60min")
                	assert False
		print("Test Case 8 Execution Completed")


	@pytest.mark.run(order=9)
        def test_009_start_subscriber_collection_service(self):
		logging.info("Start Subscriber Collection Service")
        	get_ref = ib_NIOS.wapi_request('GET', object_type="member:parentalcontrol")
		logging.info(get_ref)
                res = json.loads(get_ref)
                for i in res:
                        logging.info("Modify a enable_dns")
                        data = {"enable_service": True}
                        response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                        print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
		print("Test Case 9 Execution Completed")
        	sleep(60)


		logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                print("System Restart is done successfully")
                sleep(20)

	@pytest.mark.run(order=10)
	def test_010_Copy_Subscriber_Record_radfiles_to_radclient(self):
        	logging.info("Copy Subscriber Record radius message files to RAD Client")
        	dig_cmd = 'scp 1k.txt root@'+str(config.rad_client_ip)+':/root '
        	dig_result = subprocess.check_output(dig_cmd, shell=True)
        	print dig_result
        	assert re.search(r'',str(dig_result))
        	print "Copied the files to radclient"
        	logging.info("Test Case 10 Execution Completed")
        	sleep(5)	
		
	@pytest.mark.run(order=11)
    	def test_011_From_Radclient_Send_Start_Radius_Message(self):
        	logging.info("From Rad client send Start Radius message with PCP Policy and Proxy-All Configured")
        	dig_cmd = 'sshpass -p infoblox ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.rad_client_ip)+' "radclient -q -f 1k.txt -r 1 '+str(config.grid_vip)+' acct testing123"'
        	dig_result = subprocess.check_output(dig_cmd, shell=True)
        	print dig_result
        	assert re.search(r'',str(dig_result))
        	logging.info("Test Case 11 Execution Completed")
        	sleep(5)

	@pytest.mark.run(order=12)
    	def test_012_Validate_Subscriber_Record(self):
        	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        	child.logfile=sys.stdout
        	child.expect('password:',timeout=None)
        	child.sendline('infoblox')
        	child.expect('Infoblox >')
        	child.sendline('show subscriber_secure_data')
        	child.expect('Infoblox >')
        	c=child.before
        	assert re.search(r'.*'+config.rad_client_ip+'\/32\|LID\:N\/A\|IPS\:N\/A.*',c)
        	logging.info("Test case 12 execution completed")








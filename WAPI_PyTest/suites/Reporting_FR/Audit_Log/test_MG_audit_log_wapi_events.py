import config
import json
import os
import pytest
import pexpect
import re
import sys
import subprocess
from time import sleep
import unittest
import ib_utils.ib_NIOS as ib_NIOS

class AuditLogWAPIEvents(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_001_enable_audit_log_wapi_detailed(self):
    	get_ref = ib_NIOS.wapi_request('GET', object_type="grid?_return_fields=audit_log_format")
       	logging.info(get_ref)
       	ref1=json.loads(get_ref)[0]['_ref']
	data={"audit_log_format":"WAPI_DETAILED"}
	response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
	print("#######################",response)
	print("Audit Log WAPI Detailed option has been enabled")
	print("Test Case 01 passed")

     @pytest.mark.run(order=2)
     def test_002_add_auth_zone(self):
         logging.info("Creating auth Zone")
	 data={"fqdn": "source.com"}
	 response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
	 if (response[0]==400):
	     print("Zone \'source.com\' already exists")
	 else:
	     print("Zone \'source.com\' has been created")
	 data = {"grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
         get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=source.com")
         res = json.loads(get_ref)
         ref1 = json.loads(get_ref)[0]['_ref']
         response = ib_NIOS.wapi_request('PUT',ref=res,fields=json.dumps(data))
         response=json.loads(response)
         logging.info("Restart services")
         grid =  ib_NIOS.wapi_request('GET', object_type="grid")
         ref = json.loads(grid)[0]['_ref']
         publish={"member_order":"SIMULTANEOUSLY"}
         request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
         sleep(10)
         request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
         restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
         sleep(20)
	 print("Test Case 02 passed")





	


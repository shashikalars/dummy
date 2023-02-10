"""
 Copyright (c) Infoblox Inc., 2016

 ReportName          : DDNS Update Rate Trend
 ReportCategory      : DDNS
 Number of Test cases: 1
 Execution time      : 302.61 seconds
 Execution Group     : Minute Group (MG)
 Description         : 'DDNS Update Rate Trend' Reports will be updated every 1 min. 

 Author   : Raghavendra MN
 History  : 05/28/2016 (Created)
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
import time
import unittest
import random
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump 
from ib_utils.ib_validaiton import compare_results
"""
TEST Steps:
      1.  Input/Preparaiton      : Add zone say 'ddns.com & ddns1.com' , Adding RR's through NS update.  
      2.  Search                 : Performing Search operaion with default/custom filter
      3.  Validation             : comparing Search results with inputdata (with delta 0).
"""
class DDNSUpdateRateTrend(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        cls.test1=[]
        cls.test2=[]
        logger.info('-'*15+"START:DDNS Update Rate Trend"+'-'*15)
        logger.info('Added Zone ddns.com')
	print(config.grid_fqdn)
        zone_ddns = {"fqdn":"ddns.com","view":"default","grid_primary": [{"name": config.grid_fqdn,"stealth": False}],"allow_update":[{"_struct":"addressac", "address":"Any","permission":"ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(zone_ddns))
	print(response)

        logger.info('Added Zone ddns1.com with allow update with ACL 2.2.2.2/allow')
        zone_ddns1 = {"fqdn":"ddns1.com","view":"default","grid_primary": [{"name": config.grid_fqdn,"stealth": False}],"allow_update":[{"_struct":"addressac", "address":"2.2.2.2","permission":"ALLOW"}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(zone_ddns1))
         
        logger.info('Restart Service')
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        logger.info('Waiting 60 sec., restart operation')
        time.sleep(20)

        epoch=int(ib_get.indexer_epoch_time(config.indexer_ip))
        sleep_sec = 60-int(time.strftime('%S', time.gmtime(epoch)))
        logger.info("Waiting for %d sec., for NS Update operaiton.",sleep_sec)
        time.sleep(sleep_sec)

        ttl=random.randint(5000,6000)
        ip=repr(random.randint(10,30))+'.'+repr(random.randint(10,30))+'.'+repr(random.randint(10,30))+'.'+repr(random.randint(10,30))
        logger.info("Performed nsupdate for 'Prerequisite', 'Reject', 'Sucess' & 'Failure'" )
        #fout=open("../dumps/nsupdate.log","w")
	fout=open("dumps/nsupdate.log","w")
        proc=pexpect.spawn("nsupdate",timeout=300)
        proc.expect(r"> ")
        proc.logfile_read=fout
        proc.sendline("server "+config.grid_vip)
        proc.expect(r"> ")
        proc.sendline("update add arec.ddns.com " +str(ttl)+ " in a " + ip)
        proc.expect(r"> ")
        proc.sendline("send")
        proc.expect(r"> ")
        proc.sendline("prereq nxrrset arec.ddns.com A")
        proc.expect(r"> ")
        proc.sendline("update add hello.ddns.com 123 in a 12.12.12.12")
        proc.expect(r"> ")
        proc.sendline("send")
        proc.expect(r"> ")
        proc.sendline("update add arec.ddns1.com " +str(ttl)+ " in a " + ip)
        proc.expect(r"> ")
        proc.sendline("send")
        proc.expect(r"> ")
        fout.close()
	
        #fp=open("../dumps/nsupdate.log",'r')
	fp=open("dumps/nsupdate.log","r")
        k=''.join(fp.readlines())
        logger.info("NS Update Results\n %s",k)
        fp.close()

        temp={}
        new_time = time.strftime('%Y-%m-%dT%H:%M', time.gmtime(epoch+sleep_sec))
        #temp["_time"]= new_time+":00.000+00:00" #ib_get.indexer_date(config.indexer_ip) 
        temp["Failure"]='0'
        temp["Prerequisite Reject"]="0.01666667"
        temp["Reject"]="0.01666667"
        temp["Success"]="0.01666667"
        cls.test1.append(temp)
        logger.info ("Json Input for validation")
        logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))
        logger.info ("Waiting for 4 min., for updating reports")
        time.sleep(240) #wait for report update

    def test_1_ddns_update_rate_trend_validate_failure_prerequisiteReject_reject_success_count(self):
        logger.info ("TestCase:"+sys._getframe().f_code.co_name)
        search_str=r"search sourcetype=ib:ddns index=ib_dns | rex field=REST \"'(?<ZONE>[^ ]+)/IN'\" | eval TYPE=if(isnull(TYPEA), case(match(REST, \"updating zone '[^ ]+/IN': adding an RR at\") OR match(REST, \"updating zone '[^ ]+/IN': delet\"), \"Success\", match(REST, \"update '[^ ]+/IN' denied\"), \"Reject\", match(REST, \"updating zone '[^ ]+/IN': update unsuccessful.*prerequisite not satisfied \([NY]XDOMAIN\)\"), \"PrerequisiteReject\", match(REST, \"updating zone '[^ ]+/IN': update failed\"), \"Failure\"), TYPEA) | eval VIEW=if(isnull(VIEW),\"_default\",replace(VIEW,\"view (\d+)\",\"\\1\")) | bucket span=1m _time | stats count by _time TYPE | timechart bins=1000 eval(avg(count)/60) by TYPE | eval Success=if(isnull(Success),0,Success) | eval Failure=if(isnull(Failure),0,Failure) | eval Reject=if(isnull(Reject),0,Reject) | eval PrerequisiteReject=if(isnull(PrerequisiteReject),0,PrerequisiteReject) | rename PrerequisiteReject as \"Prerequisite Reject\""

        cmd = config.search_py + " \"" + search_str + "\" --output_mode=json"
        os.system(cmd)
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        results_dist= results_list[-240::1]
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test1,results_dist)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0.02")
        result = compare_results(self.test1,results_list,0.02)
	print("----------------------------------------------------")
	print(self.test1)
	print("--------------------------------------*********************--------------")
	print(results_list)
	print("----------------------------------------------------")
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg

    @classmethod
    def teardown_class(cls):
        logger.info("Cleanup, Removed added zones ddns.com and ddns1.com")
        del_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn~=ddns.com")
        ref = json.loads(del_zone)[0]['_ref']
        del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)

        del_zone = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn~=ddns1.com")
        ref = json.loads(del_zone)[0]['_ref']
        del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)
        logger.info('-'*15+"END:DDNS Update Rate Trend"+'-'*15)

import sys
#sys.path.insert(0, str(os.getenv("HOME"))+'/qa-xaas/main/api/janus/ngp/')
sys.path.insert(0,'/home/vadga-143/IB/qa/vadpga-143/FR/')
import config
import pytest
import unittest
import logging
import subprocess
import commands
import json
import os
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import re
#import ib_utils.ib_get as ib_get
from time import sleep
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="license.log" ,level=logging.DEBUG,filemode='w')


class NetworkView(unittest.TestCase):

    @classmethod
    def setup_class(cls):
        """ setup any state specific to the execution of the given class (which
         usually contains tests).
         """
        logging.info("SETUP METHOD")

    def simple_func(self,a):
        # do any process here and return the value
        # Return value is comparted(asserted) in test case method
        return(a+2)


    @pytest.mark.run(order=1)
    def test_validate_validate_sid(self):
        logging.info('-'*30+"Test Case 28 Execution Started"+'-'*30)
        sid_value=110100100
        print sid_value
             
        dig_cmd = os.system('dnsq -ns='+str(config.grid_member1_vip)+' -qname=authors.bind. -repeat=9 -wait=0.03')
        print dig_cmd
        logging.info(dig_cmd)
        sleep(30)

        ssh_cmd ='ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null -q root@'+str(config.grid_member2_vip)+' " grep -A 4 '+str(sid_value)+' /infoblox/var/atp_sid_hits.txt | grep -v '+str(sid_value)+'  " '
        out = commands.getoutput(ssh_cmd)
        alist=tuple(out.split('\n'))
        print alist[0]
        print alist[1]
        assert alist[0]=='0' and alist[1]=='10'


    @pytest.mark.run(order=2)
    def test_2_validate_validate_sid(self):
        logging.info('-'*30+"Test Case 28 Execution Started"+'-'*30)
        sid_value=110100200
        print sid_value

        dig_cmd = os.system('dnsq -ns='+str(config.grid_member1_vip)+' -qname=version.bind. -repeat=9 -wait=0.03')
        print dig_cmd
        logging.info(dig_cmd)
        sleep(30)

        ssh_cmd ='ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null -q root@'+str(config.grid_member2_vip)+' " grep -A 4 '+str(sid_value)+' /infoblox/var/atp_sid_hits.txt | grep -v '+str(sid_value)+'  " '
        out = commands.getoutput(ssh_cmd)
        alist=tuple(out.split('\n'))
        print alist[0]
        print alist[1]
        assert alist[0]=='0' and alist[1]=='10'

         

   
    '''  
    @pytest.mark.run(order=1)
    def test_validate_validate_sid(self):
        logging.info('-'*30+"Test Case 28 Execution Started"+'-'*30)
        logging.info("Get Member Threat Protection using member:threatprotection object")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[0]['_ref']

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        #ref_version_2 = json.loads(get_ruleset)[1]['version']

        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120202000\
        &ruleset=%s"%ref_version_1)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[0]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)
             
        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"ALERT","log_severity":"WARNING","params":[{"name":"LIMITED_IP","value":config.client_ip},{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"PACKETS_PER_SECOND","value":"1"},{"name":"DROP_INTERVAL","value":"5"},{"name":"RATE_ALGORITHM","value":"Blocking"}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)
    
        logging.info(response)
        
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)
        
     #   get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate*')
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate%20limited*')
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value
         
        dig_cmd = os.system('for i in {1..10};do dnsq -ns='+str(config.grid_member1_vip)+' -qname=rate_udp_modified.com -protocol=tcp -wait=0.03;done')
        print dig_cmd
        logging.info(dig_cmd)
        sleep(30)
        
        ssh_cmd ='ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null -q root@'+str(config.grid_member2_vip)+' " grep -A 4 '+str(sid_value)+' /infoblox/var/atp_sid_hits.txt | grep -v '+str(sid_value)+'  " '
        out = commands.getoutput(ssh_cmd)
        alist=tuple(out.split('\n'))
        print alist[0]
        print alist[1] 
        assert alist[0]=='1' and alist[1]=='8'
         
    
    
    @pytest.mark.run(order=2)
    def test_2_update_log_severity_and_fqdn_for_rate_limited_tcp_fqdn_lookup(self):
        logging.info('-'*30+"Test Case 81 Execution Started"+'-'*30)
        logging.info('-'*15+"Delete custom rule for Rate Limited TCP IP"'-'*15)
        logging.info('-'*15+"Get ThreatProtection Grid rule for Rate Limited TCP IP"'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~=Rate%20limited*')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1
        
        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2


        data={"name":"Rate limited:config.client_ip"}
        modify_drop_field = ib_NIOS.wapi_request('DELETE',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field
          
        logging.info('-'*30+"Test Case 81 Execution Completed"+'-'*30)
   
    '''


        
 
    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """
        logging.info("TEAR DOWN METHOD")   


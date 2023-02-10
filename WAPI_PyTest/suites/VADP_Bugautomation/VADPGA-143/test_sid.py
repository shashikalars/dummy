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
    '''
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
    '''   
    @pytest.mark.run(order=1)
    def test_000_validate_blacklist_udp_fqdn_lookup_validate_sid_txt_file(self):
        logging.info('-'*30+"Test Case 1 Execution Started"+'-'*30)
        logging.info("Validated Threat Protection Profile-Search for 'name' field")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        print(get_ref)
        res = json.loads(get_ref)
        print res
        ref_1 = json.loads(get_ref)[0]['_ref']
 
        
        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        print(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']
        #print ref_version_1
        print ref_version_2
          
        #get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120303000&ruleset=%s"%ref_version_2)
	get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120303000&ruleset=%s"%ref_version_2)
        print(get_rule_temp_ref)
	res_rule_template = json.loads(get_rule_temp_ref)
        print res_rule_template 
        ref_1_temp = json.loads(get_rule_temp_ref)[0]['_ref']
        print ref_1_temp  
        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)
                   
        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"DROP",
        "log_severity":"WARNING","params":[{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"FQDN","value":"black_udp.com"}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)
        print response
        sleep(10)
        logging.info("Perform Publish Operation")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(120)
        
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Blacklist:black_udp.com')
        custom_rule=json.loads(get_custom_rule)
        ref_2 = custom_rule[0]['name']
        sid_value = custom_rule[0]['sid']
        execute_dnsq='/import/tools/qa/bin/dnsq -ns='+str(config.grid_member1_vip)+' -qname=black_udp.com -qtype=A -repeat=9 -wait=0.03' 
        print(execute_dnsq)
	logs_dnsq=os.system(execute_dnsq)  
        sleep(30)  
        ssh_cmd ='ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null -q root@'+str(config.grid_member2_vip)+' " grep -A 4 '+str(sid_value)+' /infoblox/var/atp_sid_hits.txt | grep -v '+str(sid_value)+'  " '
        out = commands.getoutput(ssh_cmd)
        alist=tuple(out.split('\n'))
        print alist
        assert alist[0]=='0' and alist[1]=='10'
	#assert alist[1]=='0' and alist[2]=='4'
        logging.info('-'*30+"Test Case 1 Execution Completed"+'-'*30) 
          
   
        
    @pytest.mark.run(order=2)
    def test_001_delete_custom_rule_blacklist_udp_fqdn(self):
        logging.info('-'*30+"Test Case 2 Execution Started"+'-'*30)
        logging.info('-'*30+"Delete custom rule for Blacklist UDP FQDN lookup"'-'*30)
        logging.info('-'*15+"Get ThreatProtection Grid rule for Blacklist"'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name=Blacklist:black_udp.com')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2


        data={"name":"Blacklist:black_udp.com"}
        modify_drop_field = ib_NIOS.wapi_request('DELETE',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field
        sleep(10)
        logging.info('-'*30+"Test Case 2 Execution Completed"+'-'*30)

    

    @pytest.mark.run(order=3)
    def test_002_validate_blacklist_tcp_fqdn_lookup_validate_sid_txt_file(self):
        logging.info('-'*30+"Test Case 3 Execution Started"+'-'*30)
        logging.info("Validated Threat Protection Profile-Search for 'name' field")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[0]['_ref']


        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']

        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120304000&ruleset=%s"%ref_version_2)
	print(get_rule_temp_ref)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[0]['_ref']
        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        logging.info(rule_temp_ref)
        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"DROP","log_severity":"WARNING","params":[{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"FQDN","value":"black_tcp.com"}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)

        sleep(10)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name=Blacklist:black_tcp.com')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        execute_dnsq='for i in {1..10};do dig @'+str(config.grid_member1_vip)+' black_tcp.com +tcp  +time=0 +retries=0;done'
        logs_dnsq=os.system(execute_dnsq)
        sleep(30)
        ssh_cmd ='ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null -q root@'+str(config.grid_member2_vip)+' " grep -A 4 '+str(sid_value)+' /infoblox/var/atp_sid_hits.txt | grep -v '+str(sid_value)+'  " '
        out = commands.getoutput(ssh_cmd)
        alist=tuple(out.split('\n'))
        assert alist[0]=='0' and alist[1]=='10'
        logging.info('-'*30+"Test Case 3 Execution Completed"+'-'*30) 
    
    @pytest.mark.run(order=4)
    def test_003_delete_custom_rule_blacklist_tcp_fqdn(self):
        logging.info('-'*30+"Test Case 4 Execution Started"+'-'*30)
        logging.info('-'*30+"Delete custom rule for Blacklist TCP FQDN lookup"'-'*30)
        logging.info('-'*15+"Get ThreatProtection Grid rule for Blacklist"'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name=Blacklist:black_tcp.com')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2


        data={"name":"Blacklist:black_tcp.com"}
        modify_drop_field = ib_NIOS.wapi_request('DELETE',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field

        logging.info('-'*30+"Test Case 4 Execution Completed"+'-'*30)

    

    @pytest.mark.run(order=5)
    def test_004_validate_rate_limited_tcp_fqdn_with_blocking_option_validate_sid_txt_file(self):
        logging.info('-'*30+"Test Case 5 Execution Started"+'-'*30)
        logging.info("Validated Threat Protection Profile-Search for 'name' field")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[0]['_ref']


        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120302000&ruleset=%s"%ref_version_2)
	print(get_rule_temp_ref)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[0]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)
        
        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"ALERT","log_severity":"WARNING","params":[{"name":"FQDN","value":"rate_tcp.com"},{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"PACKETS_PER_SECOND","value":"1"},{"name":"DROP_INTERVAL","value":"5"},{"name":"RATE_ALGORITHM","value":"Blocking"}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)

        sleep(10)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)

        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        execute_dnsq='for i in {1..10};do /import/tools/qa/bin/dnsq -ns='+str(config.grid_member1_vip)+' -qname=rate_tcp.com -protocol=tcp -wait=0.03;done' 
        logs_dnsq=os.system(execute_dnsq)
        sleep(90)
        
        ssh_cmd ='ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null -q root@'+str(config.grid_member2_vip)+' " grep -A 4 '+str(sid_value)+' /infoblox/var/atp_sid_hits.txt | grep -v '+str(sid_value)+'  " '
        out = commands.getoutput(ssh_cmd)
        alist=tuple(out.split('\n'))
        print alist[0]
        print alist[1]
        assert alist[0]=='1' and alist[1]=='8'
        logging.info('-'*30+"Test Case 5 Execution Completed"+'-'*30)  
    
    @pytest.mark.run(order=6)
    def test_005_update_log_severity_and_fqdn_for_rate_limited_tcp_fqdn_lookup(self):
        logging.info('-'*30+"Test Case 6 Execution Started"+'-'*30)
        logging.info('-'*15+"Modify Log Severity and FQDN Values in Custom Rule(Rate Limited TCP FQDN)"+'-'*15)
        logging.info("Get ThreatProtection Grid rule for Whitelist")
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~=Rate.*')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120302000&ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[0]['_ref']
        print ref_1_temp


        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)
         
        data={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"ALERT","log_severity":"WARNING","params":[{"name":"FQDN","value":"rate_tcp_modified.com"},{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"PACKETS_PER_SECOND","value":"1"},{"name":"DROP_INTERVAL","value":"5"},{"name":"RATE_ALGORITHM","value":"Rate_Limiting"}]}}
        modify_drop_field = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field
        
        sleep(10)
        
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)

        get_custom_rule_2 = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~=Rate.*')
        factory = json.loads(get_custom_rule)
        ref_2 = json.loads(get_custom_rule)[0]['_ref']
        print ref_2


        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_2+'?_return_fields=disabled,name,config')
        print get_ref_disable

        validate = json.loads(get_ref_disable)
        print validate
        ref_ipv4_1 = validate['config']
        print ref_ipv4_1


        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        execute_dnsq='for i in {1..10};do /import/tools/qa/bin/dnsq -ns='+str(config.grid_member1_vip)+' -qname=rate_tcp_modified.com -protocol=tcp -wait=0.03;done'
        logs_dnsq=os.system(execute_dnsq)
        sleep(90)

        ssh_cmd ='ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null -q root@'+str(config.grid_member2_vip)+' " grep -A 4 '+str(sid_value)+' /infoblox/var/atp_sid_hits.txt | grep -v '+str(sid_value)+'  " '
        out = commands.getoutput(ssh_cmd)
        alist=tuple(out.split('\n'))
        assert alist[0]=='1' and alist[1]=='8'
        logging.info('-'*30+"Test Case 6 Execution Completed"+'-'*30) 
    
    @pytest.mark.run(order=7)
    def test_006_delete_custom_rule_rate_limited_tcp_fqdn(self):
        logging.info('-'*30+"Test Case 7 Execution Started"+'-'*30)
        logging.info('-'*15+"Delete custom rule for Rate Limited TCP FQDN"'-'*15)
        logging.info('-'*15+"Get ThreatProtection Grid rule for RATE LIMTED"'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~=Rate.*')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2

        data={"name":"Rate Limited:rate_tcp_modified.com"}
        modify_drop_field = ib_NIOS.wapi_request('DELETE',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field
        logging.info('-'*30+"Test Case 7 Execution Completed"+'-'*30)
   
    
    @pytest.mark.run(order=8)
    def test_007_validate_rate_limited_udp_fqdn_blocking_validate_sid_txt_file(self):
        logging.info('-'*30+"Test Case 8 Execution Started"+'-'*30)
        logging.info("Validated Threat Protection Profile-Search for 'name' field")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:threatprotection")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref_1 = json.loads(get_ref)[0]['_ref']


        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120301000&ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        print res_rule_template
        ref_1_temp = json.loads(get_rule_temp_ref)[0]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)
        
        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"ALERT","log_severity":"WARNING","params":[{"name":"FQDN","value":"rate_udp.com"},{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"PACKETS_PER_SECOND","value":"1"},{"name":"DROP_INTERVAL","value":"5"},{"name":"RATE_ALGORITHM","value":"Blocking"}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)

        sleep(10)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)
        
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
   #     ref_2 = custom_rule['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
   #     sid_value = custom_rule['sid']
        print sid_value
         
        execute_dnsq='for i in {1..10};do /import/tools/qa/bin/dnsq -ns='+str(config.grid_member1_vip)+' -qname=rate_udp.com -protocol=udp -wait=0.03;done' 
        logs_dnsq=os.system(execute_dnsq)
        sleep(90)
        ssh_cmd ='ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null -q root@'+str(config.grid_member2_vip)+' " grep -A 4 '+str(sid_value)+' /infoblox/var/atp_sid_hits.txt | grep -v '+str(sid_value)+'  " '
        out = commands.getoutput(ssh_cmd)
        alist=tuple(out.split('\n'))
        assert alist[0]=='1' and alist[1]=='8'
        logging.info('-'*30+"Test Case 8 Execution Started"+'-'*30)
     
         
    @pytest.mark.run(order=9)
    def test_008_update_log_severity_and_fqdn_for_rate_limited_udp_fqdn_lookup_rate_limiting(self):
        logging.info('-'*30+"Test Case 9 Execution Started"+'-'*30)
        logging.info('-'*15+"Modify Log Severity and FQDN Values in Custom Rule(Rate Limited TCP FQDN)"+'-'*15)
        logging.info("Get ThreatProtection Grid rule for Whitelist")
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~=Rate.*')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2

        logging.info("Get Ruleset Version for ad")
        get_ruleset = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruleset")
        logging.info(get_ruleset)
        res = json.loads(get_ruleset)
        ref_version_1 = json.loads(get_ruleset)[0]['version']
        ref_version_2 = json.loads(get_ruleset)[1]['version']


        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120301000&ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[0]['_ref']
        print ref_1_temp


        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)
             
        data={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"ALERT","log_severity":"WARNING","params":[{"name":"FQDN","value":"rate_udp_modified.com"},{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"PACKETS_PER_SECOND","value":"1"},{"name":"DROP_INTERVAL","value":"5"},{"name":"RATE_ALGORITHM","value":"Rate_Limiting"}]}}
        modify_drop_field = ib_NIOS.wapi_request('PUT',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field
        sleep(10)

        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)

        get_custom_rule_2 = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~=Rate.*')
        factory = json.loads(get_custom_rule)
        ref_2 = json.loads(get_custom_rule)[0]['_ref']
        print ref_2


        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_2+'?_return_fields=disabled,name,config')
        print get_ref_disable

        validate = json.loads(get_ref_disable)
        print validate
        ref_ipv4_1 = validate['config']
        print ref_ipv4_1


        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print custom_rule
        print type(custom_rule)
        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        execute_dnsq='for i in {1..10};do /import/tools/qa/bin/dnsq -ns='+str(config.grid_member1_vip)+' -qname=rate_udp_modified.com -protocol=udp -wait=0.03;done'
        logs_dnsq=os.system(execute_dnsq)
        sleep(90)

        ssh_cmd ='ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null -q root@'+str(config.grid_member2_vip)+' " grep -A 4 '+str(sid_value)+' /infoblox/var/atp_sid_hits.txt | grep -v '+str(sid_value)+'  " '
        out = commands.getoutput(ssh_cmd)
        alist=tuple(out.split('\n'))
        assert alist[0]=='1' and alist[1]=='8'
   
    

    @pytest.mark.run(order=10)
    def test_009_delete_custom_rule_rate_limited_udp_fqdn_lookup(self):
        logging.info('-'*30+"Test Case 10 Execution Started"+'-'*30)
        logging.info('-'*15+"Delete custom rule for Rate Limited UDP FQDN Lookup"'-'*15)
        logging.info('-'*15+"Get ThreatProtection Grid rule for Whitelist"'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~=Rate.*')
        factory = json.loads(get_custom_rule)
        ref_1 = json.loads(get_custom_rule)[0]['_ref']
        print ref_1

        get_ref_disable = ib_NIOS.wapi_request('GET', object_type = ref_1+'?_return_fields=disabled,name')
        print get_ref_disable
        logging.info(get_ref_disable)
        ref_2 = json.loads(get_ref_disable)['_ref']
        print ref_2


        data={"name":"Rate limited:rate_udp_modified.com"}
        modify_drop_field = ib_NIOS.wapi_request('DELETE',object_type=ref_2,fields=json.dumps(data))
        logging.info(modify_drop_field)
        print modify_drop_field

        logging.info('-'*30+"Test Case 10 Execution Completed"+'-'*30)
      
    
    @pytest.mark.run(order=11)
    def test_010_validate_validate_rate_limited_tcp_ip_sid(self):
        logging.info('-'*30+"Test Case 11 Execution Started"+'-'*30)
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
        ref_version_2 = json.loads(get_ruleset)[1]['version']
        print ref_version_1
        print ref_version_2
        get_rule_temp_ref = ib_NIOS.wapi_request('GET', object_type="threatprotection:ruletemplate?sid=120202000&ruleset=%s"%ref_version_2)
        res_rule_template = json.loads(get_rule_temp_ref)
        ref_1_temp = json.loads(get_rule_temp_ref)[0]['_ref']
        print ref_1_temp

        reg1=re.search('(\S+):',ref_1_temp)
        rule_temp_ref=reg1.group(1)
        print rule_temp_ref
        logging.info(rule_temp_ref)

        add_custom_rule={"template":rule_temp_ref,"disabled":False,"comment": "rule1","config":{"action":"ALERT","log_severity":"WARNING","params":[{"name":"LIMITED_IP","value":config.client_ip},{"name": "EVENTS_PER_SECOND","value":"1"},{"name":"PACKETS_PER_SECOND","value":"1"},{"name":"DROP_INTERVAL","value":"5"},{"name":"RATE_ALGORITHM","value":"Rate_Limiting"}]}}
        response = ib_NIOS.wapi_request('POST',object_type="threatprotection:grid:rule",fields=json.dumps(add_custom_rule))
        logging.info(response)
        print response
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(90)

     #   get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate*')
        get_custom_rule = ib_NIOS.wapi_request('GET', object_type='threatprotection:grid:rule?name~=Rate.*')
        custom_rule=json.loads(get_custom_rule)
        print get_custom_rule
        print type(custom_rule)

        ref_2 = custom_rule[0]['name']
        print ref_2
        sid_value = custom_rule[0]['sid']
        print sid_value

        dig_cmd = os.system('for i in {1..10};do /import/tools/qa/bin/dnsq -ns='+str(config.grid_member1_vip)+' -qname=rate_udp_modified.com -protocol=tcp -wait=0.03;done')
        print dig_cmd
        logging.info(dig_cmd)
        sleep(30)

        ssh_cmd ='ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null -q root@'+str(config.grid_member2_vip)+' " grep -A 4 '+str(sid_value)+' /infoblox/var/atp_sid_hits.txt | grep -v '+str(sid_value)+'  " '
        out = commands.getoutput(ssh_cmd)
        alist=tuple(out.split('\n'))
        print alist[0]
        print alist[1]
        assert alist[0]=='1' and alist[1]=='8'
        logging.info('-'*30+"Test Case 11 Execution Started"+'-'*30) 

    
    @pytest.mark.run(order=12)
    def test_011_update_log_severity_and_fqdn_for_rate_limited_tcp_fqdn_lookup(self):
        logging.info('-'*30+"Test Case 12 Execution Started"+'-'*30)
        logging.info('-'*15+"Delete custom rule for Rate Limited TCP IP"'-'*15)
        logging.info('-'*15+"Get ThreatProtection Grid rule for Rate Limited TCP IP"'-'*15)
        get_custom_rule = ib_NIOS.wapi_request('GET',object_type='threatprotection:grid:rule?name~=Rate.*')
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
        logging.info('-'*30+"Test Case 12 Execution Completed"+'-'*30)
    
    
    @pytest.mark.run(order=13)
    def test_012_validate_auto_rule_sid_txt_file(self):
        logging.info('-'*30+"Test Case 13 Execution Started"+'-'*30)
        sid_value=110100100
        print sid_value

        dig_cmd = os.system('/import/tools/qa/bin/dnsq -ns='+str(config.grid_member1_vip)+' -qname=authors.bind. -repeat=9 -wait=0.03')
        print dig_cmd
        logging.info(dig_cmd)
        sleep(30)

        ssh_cmd ='ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null -q root@'+str(config.grid_member2_vip)+' " grep -A 4 '+str(sid_value)+' /infoblox/var/atp_sid_hits.txt | grep -v '+str(sid_value)+'  " '
        out = commands.getoutput(ssh_cmd)
        alist=tuple(out.split('\n'))
        print alist[0]
        print alist[1]
        assert alist[0]=='0' and alist[1]=='10'
        logging.info('-'*30+"Test Case 13 Execution Started"+'-'*30) 

    

    @pytest.mark.run(order=14)
    def test_013_validate_system_rule_validate_sid_txt_file(self):
        logging.info('-'*30+"Test Case 14 Execution Started"+'-'*30)
        sid_value=110100200
        print sid_value

        dig_cmd = os.system('/import/tools/qa/bin/dnsq -ns='+str(config.grid_member1_vip)+' -qname=version.bind. -repeat=9 -wait=0.03')
        print dig_cmd
        logging.info(dig_cmd)
        sleep(30)

        ssh_cmd ='ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null -q root@'+str(config.grid_member2_vip)+' " grep -A 4 '+str(sid_value)+' /infoblox/var/atp_sid_hits.txt | grep -v '+str(sid_value)+'  " '
        out = commands.getoutput(ssh_cmd)
        alist=tuple(out.split('\n'))
        print alist[0]
        print alist[1]
        assert alist[0]=='0' and alist[1]=='10'
        logging.info('-'*30+"Test Case 14 Execution Started"+'-'*30)   
   
     
    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """
        logging.info("TEAR DOWN METHOD")   


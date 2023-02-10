import config
import json
import os
import pytest
import pexpect
import re
import sys
import paramiko
import shlex
from scp import SCPClient
import subprocess
from subprocess import Popen, PIPE
import unittest
import time
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from time import sleep
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results

"""
TEST Steps:
      1.  Input/Preparation  : Add an Authoritative zone .
                               Create some records under the zone
      2.  Search     : Performing Search operation with default & custom filter
      3.  Validation : comparing Search results with Reterived "zone and record" data from NIOS Grid using WAPI
"""

class DHCPLeaseHistory(unittest.TestCase):
    @classmethod
    def setup_class(cls):
	
        logger.info('-'*15+"START:DNS STATISTICS PER DNS VIEW"+'-'*15)
	data = {"fqdn": "abc.com"}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
        print response
        logger.info(response)

        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=abc.com")
        logger.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print ref1

        data = {"grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        logger.info(response)	

        logger.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(20)

        data={"name":"arec.abc.com","ipv4addr":"3.3.3.3","view": "default"}
        response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
	data={"name":"aaaa.abc.com","ipv6addr": "23::","view": "default"}
	response = ib_NIOS.wapi_request('POST', object_type="record:aaaa",fields=json.dumps(data))
	data={"name":"cname.abc.com","canonical": "test.com","view": "default"}
	response = ib_NIOS.wapi_request('POST', object_type="record:cname",fields=json.dumps(data))
	data={"name": "mx.abc.com","mail_exchanger": "test.com","preference": 10,"view": "default"}
	response = ib_NIOS.wapi_request('POST', object_type="record:mx",fields=json.dumps(data))
	data={"name": "hinfo.abc.com","record_type": "hinfo","subfield_values": [{"field_type": "P","field_value": "\"INTEL\" \"INTEL\"","include_length": "NONE"}],"view": "default"}
	response = ib_NIOS.wapi_request('POST', object_type="record:unknown",fields=json.dumps(data))

	cls.statistics_view = [{"AAAA Records":"1","MX Records":"1","A Records":"1","CNAME Records":"1","HINFO":"1"}]
	
	cls.statistics_zone = [{"Zone":"abc.com","Function":"Forward-Mapping","A Records":"1","AAAA Records":"1","CNAME Records":"1","MX Records":"1","HINFO":"1"}]	

	cls.dns_object_count = [{"DNS Object Count":"7"}]

    def is_grid_alive(grid=config.grid_vip):
        """
        Checks whether the grid is reachable
        """
        
	ping = os.popen("ping -c 2 "+grid).read()
        print(ping)
        if "0 received" in ping:
            return False
        else:
            return True


    def test_000(self):

        logger.info("Logging into Grid Master as 'root'")
        child = pexpect.spawn("ssh root@"+config.grid_vip,  maxread=4000)
        print("##############################",config.grid_vip)
	try:
            #child.expect('(yes/no)?',timeout=100)
            #child.sendline("yes")

            child.expect('0#',timeout=100)
            child.sendline("cd /infoblox/var/reporting")
            child.expect('0#',timeout=100)
            child.sendline("/infoblox/dns/bin/dns_reporter -z")
            child.expect('0#',timeout=100)
            print("command executed")
	    print("\n")
	    print("#############################################")
	    #Wait for some time for the reports to be generated
            sleep(600)

        except Exception as e:
            print(e)
            child.close()
            assert False


        finally:
            child.close()

    def test_001_perpetual_license_validation(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        logger.info("New Perpetual License Validation")

	file_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(config.indexer_ip)+' "cat /opt/splunk/etc/licenses/fixed-sourcetype_E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855/500MB.lic"'
	validation_result = subprocess.check_output(file_validation, shell=True)
	print("$$$$$$$$$$$$$$$$$$$$$$$$$$$",validation_result)
	assert re.search(r'.*<creation_time>1644796800</creation_time>*',str(validation_result))
	assert re.search(r'.*<relative_expiration_interval>126230400</relative_expiration_interval>*',str(validation_result))
	assert re.search(r'.*<absolute_expiration_time>1802563200</absolute_expiration_time>*',str(validation_result))



    def test_002_dns_statistics_view(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        logger.info("DNS Statistics per DNS View")
	
	search_str="search sourcetype=ib:dns:view index=ib_ipam | rex field=_raw \"^(?<timestamp_old>[^,]+),(?<view_old>[^,]+),(?<members_old>[^,]+),(?<zones_forward_old>[^,]+),(?<zones_ipv4_old>[^,]+),(?<zones_ipv6_old>[^,]+),(?<zones_signed_old>[^,]+),(?<rr_a_old>[^,]+),(?<rr_aaaa_old>[^,]+),(?<rr_caa_old>[^,]+),(?<rr_cname_old>[^,]+),(?<rr_dname_old>[^,]+),(?<rr_dnskey_old>[^,]+),(?<rr_ds_old>[^,]+),(?<rr_mx_old>[^,]+),(?<rr_naptr_old>[^,]+),(?<rr_nsec_old>[^,]+),(?<rr_nsec3param_old>[^,]+),(?<rr_nsec3_old>[^,]+),(?<rr_ns_old>[^,]+),(?<rr_ptr_old>[^,]+),(?<rr_rrsig_old>[^,]+),(?<rr_soa_old>[^,]+),(?<rr_srv_old>[^,]+),(?<rr_tlsa_old>[^,]+),(?<rr_txt_old>[^,]+),(?<rr_other_old>[^,]+),(?<rr_total_old>[^,]+),(?<hosts_old>[^,]+),(?<rr_lbdn_old>[^,]+),(?<rr_dhcid_old>[^,]+),(?<rr_alias_old>[^,]+)\" | eval timestamp=coalesce(timestamp,timestamp_old),view=coalesce(view,view_old),members=coalesce(members,members_old),zones_forward=coalesce(zones_forward,zones_forward_old),zones_ipv4=coalesce(zones_ipv4,zones_ipv4_old),zones_ipv6=coalesce(zones_ipv6,zones_ipv6_old),zones_signed=coalesce(zones_signed,zones_signed_old),rr_a=coalesce(rr_a,rr_a_old),rr_aaaa=coalesce(rr_aaaa,rr_aaaa_old),rr_caa=coalesce(rr_caa,rr_caa_old),rr_cname=coalesce(rr_cname,rr_cname_old),rr_dname=coalesce(rr_dname,rr_dname_old),rr_dnskey=coalesce(rr_dnskey,rr_dnskey_old),rr_ds=coalesce(rr_ds,rr_ds_old),rr_mx=coalesce(rr_mx,rr_mx_old),rr_naptr=coalesce(rr_naptr,rr_naptr_old),rr_nsec=coalesce(rr_nsec,rr_nsec_old),rr_nsec3param=coalesce(rr_nsec3param,rr_nsec3param_old),rr_nsec3=coalesce(rr_nsec3,rr_nsec3_old),rr_ns=coalesce(rr_ns,rr_ns_old),rr_ptr=coalesce(rr_ptr,rr_ptr_old),rr_rrsig=coalesce(rr_rrsig,rr_rrsig_old),rr_soa=coalesce(rr_soa,rr_soa_old),rr_srv=coalesce(rr_srv,rr_srv_old),rr_tlsa=coalesce(rr_tlsa,rr_tlsa_old),rr_txt=coalesce(rr_txt,rr_txt_old),rr_other=coalesce(rr_other,rr_other_old),rr_total=coalesce(rr_total,rr_total_old),hosts=coalesce(hosts,hosts_old),rr_lbdn=coalesce(rr_lbdn,rr_lbdn_old),rr_dhcid=coalesce(rr_dhcid,rr_dhcid_old),rr_alias=coalesce(rr_alias,rr_alias_old)   | dedup view | rename view as View, zones_forward as \"Forward Mapping Zones\", zones_ipv4 as \"IPv4 Reverse Mapping Zones\", zones_ipv6 as \"IPv6 Reverse Mapping Zones\", zones_signed as \"Signed Zones\", hosts as \"Hosts\", rr_total as \"Total Records\", rr_a as \"A Records\", rr_aaaa as \"AAAA Records\", rr_alias as \"Alias Records\", rr_caa as \"CAA Records\", rr_cname as \"CNAME Records\", rr_dhcid as \"DHCID Records\", rr_dname as \"DNAME Records\", rr_dnskey as \"DNSKEY Records\", rr_ds as \"DS Records\", rr_mx as \"MX Records\", rr_naptr as \"NAPTR Records\", rr_nsec as \"NSEC Records\", rr_nsec3param as \"NSEC3PARAM Records\", rr_nsec3 as \"NSEC3 Records\", rr_ns as \"NS Records\", rr_ptr as \"PTR Records\", rr_rrsig as \"RRSIG Records\", rr_soa as \"SOA Records\", rr_srv as \"SRV Records\", rr_txt as \"TXT Records\", rr_tlsa as \"TLSA Records\", rr_other as \"Other Records\", rr_lbdn as \"LBDN\" | eval Timestamp = strftime(_time, \"%Y-%m-%d %H:%M:%S %Z\") | fields - *_*, host, linecount, punct, source, sourcetype, index, eventtype, members, EA, HWTYPE, timeendpos, timestamp, timestartpos | table Timestamp, View, \"Forward Mapping Zones\", \"IPv4 Reverse Mapping Zones\", \"IPv6 Reverse Mapping Zones\", \"Signed Zones\", \"Hosts\", \"LBDN\", \"Total Records\", \"A Records\", \"AAAA Records\", \"Alias Records\", \"CAA Records\", \"CNAME Records\", \"DHCID Records\", \"DNAME Records\", \"DNSKEY Records\", \"DS Records\", \"MX Records\", \"NAPTR Records\", \"NSEC Records\", \"NSEC3PARAM Records\", \"NSEC3 Records\", \"NS Records\", \"PTR Records\", \"RRSIG Records\", \"SOA Records\", \"TLSA Records\", \"SRV Records\", \"TXT Records\", \"Other Records\" * | fillnull"

        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        print("##########################",cmd)
        print(os.system(cmd))
        print("*****************%%%%%*********************")

        try:
            retrived_data=open(config.json_file).read()
            print(retrived_data)

        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.statistics_view,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        result = compare_results(self.statistics_view,results_list)
        logger.info("-----------------------------------------------------")
        logger.info(self.statistics_view)
        logger.info(len(self.statistics_view))
        logger.info("--------------------shashhhhhhhh-------------------")
        logger.info(results_list)
        logger.info(len(results_list))
        logger.info("-----------------------------------------------------")
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg
    
    def test_003_dns_statistics_zone(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        logger.info("DNS Statistics per Zone")

	search_str="search sourcetype=ib:dns:zone index=ib_ipam  | rex field=_raw \"^(?<timestamp_old>[^,]+),(?<view_old>[^,]+),(?<zone_name_old>[^,]+),(?<zone_format_old>[^,]+),(?<signed_old>[^,]+),(?<grid_primary_old>[^,]*),(?<ms_primary_old>[^,]*),(?<rr_a_old>[^,]+),(?<rr_aaaa_old>[^,]+),(?<rr_caa_old>[^,]+),(?<rr_cname_old>[^,]+),(?<rr_dname_old>[^,]+),(?<rr_dnskey_old>[^,]+),(?<rr_ds_old>[^,]+),(?<rr_mx_old>[^,]+),(?<rr_naptr_old>[^,]+),(?<rr_nsec_old>[^,]+),(?<rr_nsec3param_old>[^,]+),(?<rr_nsec3_old>[^,]+),(?<rr_ns_old>[^,]+),(?<rr_ptr_old>[^,]+),(?<rr_rrsig_old>[^,]+),(?<rr_soa_old>[^,]+),(?<rr_srv_old>[^,]+),(?<rr_tlsa_old>[^,]+),(?<rr_txt_old>[^,]+),(?<rr_other_old>[^,]+),(?<rr_total_old>[^,]+),(?<hosts_old>[^,]+),(?<rr_lbdn_old>[^,]+),(?<rr_dhcid_old>[^,]+),(?<rr_alias_old>[^,]+)\"  | eval timestamp=coalesce(timestamp,timestamp_old),view=coalesce(view,view_old),zone_name=coalesce(zone_name,zone_name_old),zone_format=coalesce(zone_format,zone_format_old),signed=coalesce(signed,signed_old),grid_primary=coalesce(grid_primary,grid_primary_old),ms_primary=coalesce(ms_primary,ms_primary_old),rr_a=coalesce(rr_a,rr_a_old),rr_aaaa=coalesce(rr_aaaa,rr_aaaa_old),rr_caa=coalesce(rr_caa,rr_caa_old),rr_cname=coalesce(rr_cname,rr_cname_old),rr_dname=coalesce(rr_dname,rr_dname_old),rr_dnskey=coalesce(rr_dnskey,rr_dnskey_old),rr_ds=coalesce(rr_ds,rr_ds_old),rr_mx=coalesce(rr_mx,rr_mx_old),rr_naptr=coalesce(rr_naptr,rr_naptr_old),rr_nsec=coalesce(rr_nsec,rr_nsec_old),rr_nsec3param=coalesce(rr_nsec3param,rr_nsec3param_old),rr_nsec3=coalesce(rr_nsec3,rr_nsec3_old),rr_ns=coalesce(rr_ns,rr_ns_old),rr_ptr=coalesce(rr_ptr,rr_ptr_old),rr_rrsig=coalesce(rr_rrsig,rr_rrsig_old),rr_soa=coalesce(rr_soa,rr_soa_old),rr_srv=coalesce(rr_srv,rr_srv_old),rr_tlsa=coalesce(rr_tlsa,rr_tlsa_old),rr_txt=coalesce(rr_txt,rr_txt_old),rr_other=coalesce(rr_other,rr_other_old),rr_total=coalesce(rr_total,rr_total_old),hosts=coalesce(hosts,hosts_old),rr_lbdn=coalesce(rr_lbdn,rr_lbdn_old),rr_dhcid=coalesce(rr_dhcid,rr_dhcid_old),rr_alias=coalesce(rr_alias,rr_alias_old) | dedup view,zone_name  | noop  | rename view as View, zone_name as Zone, zone_format as Function, signed as Signed, hosts as Hosts, rr_total as \"Total Records\", rr_a as \"A Records\", rr_aaaa as \"AAAA Records\", rr_alias as \"Alias Records\", rr_caa as \"CAA Records\", rr_cname as \"CNAME Records\", rr_dhcid as \"DHCID Records\", rr_dname as \"DNAME Records\", rr_dnskey as \"DNSKEY Records\", rr_ds as \"DS Records\", rr_mx as \"MX Records\", rr_naptr as \"NAPTR Records\", rr_nsec as \"NSEC Records\", rr_nsec3param as \"NSEC3PARAM Records\", rr_nsec3 as \"NSEC3 Records\", rr_ns as \"NS Records\", rr_ptr as \"PTR Records\", rr_rrsig as \"RRSIG Records\", rr_soa as \"SOA Records\", rr_srv as \"SRV Records\", rr_tlsa as \"TLSA Records\", rr_txt as \"TXT Records\", rr_other as \"Other Records\", rr_lbdn as \"LBDN\"  | eval Timestamp = strftime(_time, \"%Y-%m-%d %H:%M:%S %Z\") | fields - *_*, EA, HWTYPE, No, View, eventtype, host, index, linecount, primary, punct, source, sourcetype, timeendpos, timestamp, timestartpos | table Timestamp, Zone, Function, Signed, Hosts, \"LBDN\", \"Total Records\", \"A Records\", \"AAAA Records\", \"Alias Records\", \"CAA Records\", \"CNAME Records\", \"DHCID Records\", \"DNAME Records\", \"DNSKEY Records\", \"DS Records\", \"MX Records\", \"NAPTR Records\", \"NSEC Records\", \"NSEC3PARAM Records\", \"NSEC3 Records\", \"NS Records\", \"PTR Records\", \"RRSIG Records\", \"SOA Records\", \"SRV Records\", \"TLSA Records\", \"TXT Records\", \"Other Records\" * | fillnull"

        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        print("##########################",cmd)
        print(os.system(cmd))
        print("*****************%%%%%*********************")

        try:
            retrived_data=open(config.json_file).read()
            print(retrived_data)

        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.statistics_zone,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        result = compare_results(self.statistics_zone,results_list)
        logger.info("-----------------------------------------------------")
        logger.info(self.statistics_zone)
        logger.info(len(self.statistics_zone))
        logger.info("--------------------shashhhhhhhh-------------------")
        logger.info(results_list)
        logger.info(len(results_list))
        logger.info("-----------------------------------------------------")
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg

    def test_004_dns_object_count_trend(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        logger.info("DNS Object Count Trend for Flex Member")
	
	search_str="search index=ib_ipam sourcetype=\"ib:dns:ibflex_zone_counts\" | bucket span=1d _time | stats sum(rr_total) as MAX_PER_DAY by _time  | streamstats window=5 avg(MAX_PER_DAY) as MAX_COUNT  | eval \"DNS Object Count\"=round(MAX_COUNT, 0) |  sort -_time | rename _time as Time | eval Time=strftime(Time, \"%Y-%m-%d %H:%M:%S %Z\") | table Time,\"DNS Object Count\""

        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        print("##########################",cmd)
        print(os.system(cmd))
        print("*****************%%%%%*********************")

        try:
            retrived_data=open(config.json_file).read()
            print(retrived_data)


        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operaiton failed, Please check Grid Configuraion")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.dns_object_count,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        result = compare_results(self.dns_object_count,results_list)
        logger.info("-----------------------------------------------------")
        logger.info(self.dns_object_count)
        logger.info(len(self.dns_object_count))
        logger.info("--------------------shashhhhhhhh-------------------")
        logger.info(results_list)
        logger.info(len(results_list))
        logger.info("-----------------------------------------------------")
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg

    def test_005_validating_infoblox_log_permission_denied_issue(self):
        logging.info("Validate Infoblox log for permission denied  issues")
        infoblox_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " cat /infoblox/var/infoblox.log"'
        out1 = commands.getoutput(infoblox_log_validation)
        logging.info(out1)
        if re.search(r'ib_hypervisor_vendor_sig().*Error opening /dev/cpu/0/cpuid: Permission denied',out1):
	    assert False
	    print("Observing Permission denied issue, it is a BUG")
	else:
	    assert True
	    print(No issues found")
        logging.info("Test Case 5 Execution Completed")

    def test_006_validating_infoblox_log_syncing_reporting_files(self):
        logging.info("Validate Infoblox log for Syncing reporting files logging continuously")
        infoblox_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " cat /infoblox/var/infoblox.log"'
        out1 = commands.getoutput(infoblox_log_validation)
        logging.info(out1)
        if re.search(r'Syncing reporting files from GM failed with exit code.*11.*',out1):
            assert False
            print("Observing Permission denied issue, it is a BUG")
        else:
            assert True
            print(No issues found")
        logging.info("Test Case 6 Execution Completed")

    def test_007_perform_reboot_on_GM(self):
	
	client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(config.grid_vip, username='root', password = 'infoblox')
        stdin, stdout, stderr = client.exec_command("reboot")
	print("Sleeping for 10 minutes")
	sleep(600)

        while not is_grid_alive():
            if count == 5:
                print("Giving up after 5 tries")
                assert False
            print("Sleeping for 1 more minute...")
            sleep(60)
            count += 1	

    def test_0018_login_reporting_member_validate_disk(self):
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show disk')
        child.expect('Infoblox >')
        string = child.before
        print("#########",string)
        count = 0
        str = string.split(" ")
        print("***SPLIT***\n",str)
        a = "reporting:"
        for i in range(0, len(str)):
            if (a==str[i]):
                count = count+1
        print("*****COUNT*****",count)
        if count > 1:
            assert False
        elif count == 1:
            assert True
        else:
            assert False  

#    @pytest.mark.run(order=4)
#    def test_004_clear_data(self):
#        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=abc.com")
#        logger.info(get_ref)
#        ref1=json.loads(get_ref)[0]['_ref']
#        response = ib_NIOS.wapi_request('DELETE',ref=ref1)
#        print(response)

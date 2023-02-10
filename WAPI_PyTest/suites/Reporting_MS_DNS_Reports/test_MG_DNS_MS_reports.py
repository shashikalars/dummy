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

class DNS_Statistics(unittest.TestCase):
    @classmethod
    def setup_class(cls):

        logger.info("Generating data for MS Server reports")
        print("Generating data for MS Server reports")
        grid_member = ib_NIOS.wapi_request('GET', object_type="member?_return_fields=host_name")
        print("################################################")
        print(grid_member)
        ref = json.loads(grid_member)[0]['host_name']
        print("************************************************")
        print(ref)
        print("***********MS SERVER IP*************",config.ms_server_ip)

	ms_server = {"address": config.ms_server_ip,"grid_member": ref,"read_only": False,"synchronization_min_delay": 2,"login_name": config.ms_name,"login_password": config.ms_password,"dns_server": {"managed": True,"enable_monitoring": True,"synchronization_min_delay": 2,"use_enable_dns_reports_sync": False,"use_enable_monitoring": False,"use_login": False,"use_synchronization_min_delay": False},"dhcp_server": {"managed": True,"enable_monitoring": True,"login_name": config.ms_name,"synchronization_min_delay": 2,"use_enable_monitoring": False,"use_login": False,"use_synchronization_min_delay": False}}

        get_ref = ib_NIOS.wapi_request('POST',object_type="msserver", fields=json.dumps(ms_server))
        print("###############################################################",get_ref)
        if (get_ref[0] == 400):
            print("Another Microsoft server is using the address "+config.ms_server_ip)
            assert True
        else:
            print("MS Server \'10.34.98.56\' has been created")

        print("Performing service restart operation")
        logger.info("Performing service restart operation")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        print(restart)
        logger.info("Waiting 30 sec., for Member Restart")
        sleep(30)

        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:dns")
        get_ref1=json.loads(get_ref)[0]['_ref']
        
        data={"allow_recursive_query":True,"allow_query":[{"_struct": "addressac","address":"Any","permission":"ALLOW"}]}
        put_ref=ib_NIOS.wapi_request('PUT', object_type=get_ref1,fields=json.dumps(data))

        #Restarting
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
    	request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
	restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
    	sleep(60)


        #Validation of Zones

        get_ref = ib_NIOS.wapi_request("GET",object_type="zone_auth?fqdn=abc.com")
        ref_1=json.loads(get_ref)[0]['fqdn']
        print(ref_1)

        if (ref_1 == "abc.com"):
           print("\nPASS")
           assert True
        else:
           print("\nFAIL")
           assert False

	sleep(900)

        fp=os.popen("dig @"+config.grid_ms_ip+" -f /import/qaddi/API_Automation_08_12_20/WAPI_PyTest/suites/Reporting_MS_DNS_Reports/ib_data/DNS_Query/DNS_Top_Requested_Domain_Names/top_requested_domains.txt")
        print("&&&&&&&&&&&&&&&&&",fp)

        fp1=os.popen("dig @"+config.grid_ms_ip+" -f /import/qaddi/API_Automation_08_12_20/WAPI_PyTest/suites/Reporting_MS_DNS_Reports/ib_data/DNS_Query/DNS_Top_Requested_Domain_Names/top_nxdomain.txt")
        print("&&&&&&&&&&&&&&&&&",fp1)

        fp2=os.popen("/import/qaddi/mgovarthanan/dduq/dduq -i "+config.grid_ms_ip+" /import/qaddi/mgovarthanan/queryperf_123.txt")
        logger.info("%s",''.join(fp2.readlines()))
	print("&&&&&&&&&&&&&&&&&",fp2)
        sleep(10)

	fp3=os.popen("/import/qaddi/mgovarthanan/dduq/dduq -i "+config.grid_ms_ip+" /import/qaddi/mgovarthanan/queryperf_123.txt -t 1")
 	logger.info("%s",''.join(fp3.readlines()))
	print("&&&&&&&&&&&&&&&&&",fp3)
        sleep(10)
        fp3=os.popen("/import/qaddi/mgovarthanan/dduq/dduq -i "+config.grid_ms_ip+" /import/qaddi/mgovarthanan/queryperf_123.txt -t 1")
        logger.info("%s",''.join(fp3.readlines()))
        print("&&&&&&&&&&&&&&&&&",fp3)

        cls.statistics_view = [{"AFSDB":"1","MX Records":"1","View":"default"}]
	
	cls.statistics_zone = [{'Zone': 'abc.com', 'AFSDB': '1', 'MX Records': '1', 'AAAA Records': '1', 'A Records': '2'}]

	cls.dns_object_count = [{"DNS Object Count":"7"}]

    def test_001_generate_data(self):

        logger.info("Logging into Grid Master as 'root'")
        child = pexpect.spawn("ssh root@"+config.grid_vip,  maxread=4000)
        print("##############################",config.grid_vip)
	try:
            #child.expect('(yes/no)?',timeout=100)
            #child.sendline("yes")

            child.expect('.0#',timeout=100)
            child.sendline("cd /infoblox/var/reporting")
            child.expect('.0#',timeout=100)
            child.sendline("/infoblox/dns/bin/dns_reporter -z")
            child.expect('.0#',timeout=100)
            print("command executed")
	    print("\n")
	    print("#############################################")
	    #Wait for some time for the reports to be generated
            print("Sleeping for 600 seconds")
            sleep(600)

        except Exception as e:
            print(e)
            child.close()
            assert False


        finally:
            child.close()

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
	print("\n")

        print("######EXPECTED OUTPUT########",self.statistics_view)
        logger.info("-----------------------------------------------------")
        logger.info(self.statistics_view)
	logger.info("-----------------------------------------------------")
        print("#######ACTUAL OUTPUT#########",results_list)
        logger.info("-----------------------------------------------------")
        logger.info(results_list)
        print("#######################",results_list)
        logger.info("-----------------------------------------------------")
        print("#########COMPARISON##########",result)
	logger.info("-----------------------------------------------------")
	logger.info(result)
   	print("###########COMPARED ONE################",result)

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

        print("\n")

        print("######EXPECTED OUTPUT########",self.statistics_zone)
        logger.info("-----------------------------------------------------")
        logger.info(self.statistics_zone)
        print("########################",self.statistics_zone)
        logger.info("-----------------------------------------------------")
        print("#######ACTUAL OUTPUT#########",results_list)
        logger.info("-----------------------------------------------------")
        logger.info(results_list)
        print("#######################",results_list)
        logger.info("-----------------------------------------------------")
        print("#########COMPARISON##########",result)
        logger.info("-----------------------------------------------------")
        logger.info(result)
        print("###########COMPARED ONE",result)

        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg

  
#    @pytest.mark.run(order=4)
#    def test_004_clear_data(self):
#        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=abc.com")
#        logger.info(get_ref)
#        ref1=json.loads(get_ref)[0]['_ref']
#        response = ib_NIOS.wapi_request('DELETE',ref=ref1)
#        print(response)

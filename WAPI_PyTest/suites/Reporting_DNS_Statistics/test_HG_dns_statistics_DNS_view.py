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
      1.  Input/Preparation  : Add an Authoritative zone .
                               Create some records under the zone
      2.  Search     : Performing Search operation with default & custom filter
      3.  Validation : comparing Search results with Reterived "zone and record" data from NIOS Grid using WAPI
"""

class DHCPLeaseHistory(unittest.TestCase):
    @classmethod
    def setup_class(cls):
	
	'''
        logger.info('-'*15+"START:DNS STATISTICS PER DNS VIEW"+'-'*15)
	data = {"fqdn": "abc.com"}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
        print response
        logging.info(response)

        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=abc.com")
        logging.info(get_ref)
        res = json.loads(get_ref)
        ref1 = json.loads(get_ref)[0]['_ref']
        print ref1

        data = {"grid_primary": [{"name": config.grid_fqdn,"stealth":False}]}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data))
        logging.info(response)	

        logging.info("Restart services")
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
	data={"name": "mx.test.com","mail_exchanger": "test.com","preference": 10,"view": "default"}
	response = ib_NIOS.wapi_request('POST', object_type="record:mx",fields=json.dumps(data))
	data={"name": "hinfo.test.com","record_type": "hinfo","subfield_values": [{"field_type": "P","field_value": "\"INTEL\" \"INTEL\"","include_length": "NONE"}],"view": "default"}
	response = ib_NIOS.wapi_request('POST', object_type="record:unknown",fields=json.dumps(data))
	'''

	cls.statistics_view = [{"Total Records":"13","NS Records":"3","PTR Records":"2","SOA Records":"3","AAAA Records":"1","MX Records":"1","A Records":"1","CNAME Records":"1","HINFO":"1"}]
	
	cls.statistics_zone = [{"Zone":"abc.com","Function":"Forward-Mapping","Total Records":"8","A Records":"1","AAAA Records":"1","CNAME Records":"1","MX Records":"1","NS Records":"1","HINFO":"1","SOA Records":"1"}]	
	
    def test_001_dns_statistics_view(self):
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

    def test_002_dns_statistics_zone(self):
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

    @pytest.mark.run(order=3)
    def test_003_clear_data(self):
        get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth?fqdn=abc.com")
        logging.info(get_ref)
        ref1=json.loads(get_ref)[0]['_ref']
        response = ib_NIOS.wapi_request('DELETE',ref=ref1)
        print(response)


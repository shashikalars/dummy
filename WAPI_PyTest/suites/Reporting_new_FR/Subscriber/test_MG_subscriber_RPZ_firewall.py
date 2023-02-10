import config
import json
import os
import pytest
import pexpect
import re
import sys
import subprocess
import time
#from time import sleep
import unittest
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results

class SubscriberRPZ(unittest.TestCase):
    @classmethod
    def setup_class(cls):

        logger.info("Generating data for RPZ and Subscriber reports")
        cw=os.getcwd()
        print(cw)
        #p = os.popen("cd Subscriber")
	#print(p.read())
	os.system("pytest detailed_subscriber_prep.py -vss")
        time.sleep(60)

        logger.info("Performing service restart operation")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        logger.info("Wait for 60 sec., for restart operation")
        time.sleep(600)

	cls.detailed_subscriber = [{"Total Subscriber Hits":"1","Client ID":"10.120.22.146","Malicious Domains":"playboy.com","RPZ Entries":"playboy.com","RPZ Severity":"MAJOR"}]
	cls.rpz_trend_mitigation = [{"Substitute":"1.5","ClientHits":"1.5"}]
	cls.rpz_top_hits = [{"Client ID":"10.120.22.146","Total Client Hits":"1","Domain Name":"playboy.com","RPZ Entry":"playboy.com","Total Rule Hits":"1"}]
	cls.rpz_top_hits_clients = [{"Client ID":"10.120.22.146","Total Client Hits":"1"}]
	cls.top_dns_firewall_hits = [{"RPZ_QNAME":"playboy.com","DOMAIN_NAME":"playboy.com","RPZ_HIT_COUNT":"3","ALL_HIT_COUNT":"3","RPZ_HIT_PCT":"100.00"}]
	cls.firewall_exec_threat = [{"RPZ Rule":"playboy.com","Percentage":"100.00","# Hits":"3"}]
	cls.malicious_client = [{"Client ID":"10.120.22.146","# Hits":"2"}]

    def test_001_detailed_rpz_violation_subscriber(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
	logger.info("Detailed RPZ Violations by Subscriber ID")
	
        search_str="search source=ib:dns:query:top_rpz_hit index=ib_dns | eval SUB_TYPE=if(isnull(SUB_TYPE),\"N/A\",SUB_TYPE) | eval SUB_VAL=if(isnull(SUB_VAL),\"N/A\",SUB_VAL) | eval IPS_VAL=if(isnull(IPS_VAL),\"N/A\",IPS_VAL) | stats count as COUNT by SUB_TYPE, SUB_VAL, IPS_VAL, CLIENT, DOMAIN_NAME, RPZ_QNAME, RPZ_SEVERITY, MITIGATION_ACTION | eventstats sum(COUNT) as TOTAL_DEVICE_HITS by SUB_TYPE, SUB_VAL | sort -TOTAL_DEVICE_HITS | eventstats list(DOMAIN_NAME) as MALICIOUS_DOMAINS, list(RPZ_QNAME) as RPZ_ENTRIES by  SUB_TYPE, SUB_VAL, IPS_VAL, CLIENT, RPZ_SEVERITY, MITIGATION_ACTION | eval MALICIOUS_DOMAINS = mvindex(MALICIOUS_DOMAINS,0,2) | eval RPZ_ENTRIES = mvindex(RPZ_ENTRIES,0,2) | dedup 1 MITIGATION_ACTION, SUB_TYPE, SUB_VAL, IPS_VAL, CLIENT, RPZ_SEVERITY | head 10 | eval MITIGATION_ACTION=case(MITIGATION_ACTION == \"PT\", \"Passthru\", MITIGATION_ACTION == \"NX\", \"Block (No Such Domain)\", MITIGATION_ACTION == \"ND\", \"Block (No Data)\", MITIGATION_ACTION == \"SB\", \"Substitute\", MITIGATION_ACTION == \"A1\", \"Substitute (A)\", MITIGATION_ACTION == \"A4\", \"Substitute (AAAA)\", MITIGATION_ACTION == \"AA\", \"Substitute (A/AAAA)\", MITIGATION_ACTION == \"DN\", \"Substitute (Domain Name)\", MITIGATION_ACTION == \"ER\", \"None\") | eval RPZ_SEVERITY=case(RPZ_SEVERITY == \"4\", \"INFORMATIONAL\", RPZ_SEVERITY == \"6\", \"WARNING\", RPZ_SEVERITY == \"7\", \"MAJOR\", RPZ_SEVERITY == \"8\", \"CRITICAL\", RPZ_SEVERITY == \"\", \"\") | rename SUB_TYPE as \"Subscriber ID Type\", SUB_VAL as \"Subscriber ID Value\", IPS_VAL as \"IP Space Discriminator\", CLIENT as \"Client ID\", TOTAL_DEVICE_HITS as \"Total Subscriber Hits\", MALICIOUS_DOMAINS as \"Malicious Domains\", RPZ_ENTRIES as \"RPZ Entries\", RPZ_SEVERITY as \"RPZ Severity\", MITIGATION_ACTION as \"Mitigation Action\" | table \"Subscriber ID Value\", \"Subscriber ID Type\", \"Client ID\", \"Total Subscriber Hits\", \"Malicious Domains\", \"RPZ Entries\", \"RPZ Severity\", \"Mitigation Action\", \"IP Space Discriminator\""

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
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.detailed_subscriber,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        result = compare_results(self.detailed_subscriber,results_list)
        logger.info("-----------------------------------------------------")
        logger.info(self.detailed_subscriber)
        logger.info(len(self.detailed_subscriber))
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

    def test_002_rpz_trend_mitigation_action(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
	logger.info("DNS RPZ Trend Mitigation Action")

        search_str="search index=ib_dns_summary report=si_dns_rpz_hits| eval MITIGATION_ACTION=case(MITIGATION_ACTION == \"PT\", \"Passthru\", MITIGATION_ACTION == \"NX\" or MITIGATION_ACTION == \"ND\", \"Block\", MITIGATION_ACTION == \"SB\" or MITIGATION_ACTION ==\"A1\" or MITIGATION_ACTION ==\"A4\" or MITIGATION_ACTION ==\"AA\" or MITIGATION_ACTION ==\"DN\", \"Substitute\") | fields _time  MITIGATION_ACTION   TOTAL_COUNT   | timechart bins=1000 avg(TOTAL_COUNT) by MITIGATION_ACTION  useother=f | fillnull | addtotals row=true col=false | rename Total as \"ClientHits\""


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
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.rpz_trend_mitigation,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        result = compare_results(self.rpz_trend_mitigation,results_list)
        logger.info("-----------------------------------------------------")
        logger.info(self.rpz_trend_mitigation)
        logger.info(len(self.rpz_trend_mitigation))
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

    def test_003_dns_rpz_top_hits(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
	logger.info("DNS RPZ Top Hits")	

        search_str="search index=ib_dns_summary  report=si_dns_rpz_hits | lookup dns_viewkey_displayname_lookup VIEW output display_name | eval SUB_VAL=if(isnull(SUB_VAL),\"N/A\",SUB_VAL) | stats sum(COUNT) as QCOUNT by _time, CLIENT, DOMAIN_NAME, orig_host, TOTAL_COUNT, MITIGATION_ACTION, RPZ_SEVERITY, REDIRECTION_RECORD, RPZ_QNAME, SUB_VAL | stats sum(TOTAL_COUNT) as TOTAL_COUNT, sum(QCOUNT) as QCOUNT by _time, CLIENT, DOMAIN_NAME, RPZ_QNAME | eval RPZ_SEVERITY=case(RPZ_SEVERITY == \"4\", \"INFORMATIONAL\", RPZ_SEVERITY == \"6\", \"WARNING\", RPZ_SEVERITY == \"7\", \"MAJOR\", RPZ_SEVERITY == \"8\", \"CRITICAL\", RPZ_SEVERITY == \"\", \"\") | rename CLIENT as \"Client ID\", QCOUNT as \"Total Client Hits\", DOMAIN_NAME as \"Domain Name\", TOTAL_COUNT as \"Total Rule Hits\", RPZ_QNAME as \"RPZ Entry\", RPZ_SEVERITY as \"RPZ Severity\" | sort -\"Total Client Hits\" | head 10 | table \"Client ID\", \"Total Client Hits\", \"Domain Name\", \"RPZ Entry\", \"RPZ Severity\", \"Total Rule Hits\", Time"

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
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.rpz_top_hits,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        result = compare_results(self.rpz_top_hits,results_list)
        logger.info("-----------------------------------------------------")
        logger.info(self.rpz_top_hits)
        logger.info(len(self.rpz_top_hits))
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

    def test_004_dns_rpz_top_hits_clients(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
	logger.info("DNS RPZ Top hits by Clients")

        search_str = "search index=ib_dns_summary report=si_dns_rpz_hits | lookup dns_viewkey_displayname_lookup VIEW output display_name | stats avg(COUNT) as QCOUNT by _time,orig_host,VIEW,CLIENT,SUB_TYPE,SUB_VAL | stats sum(QCOUNT) as QCOUNT by _time, CLIENT | eval QCOUNT=round(QCOUNT) | convert ctime(_time) as Time | rename CLIENT as \"Client ID\", QCOUNT as \"Total Client Hits\" | append [ search index=ib_dns_summary report=si_dns_rpz_hits | stats avg(COUNT) as QCOUNT by _time, VIEW, CLIENT, orig_host | stats sum(QCOUNT) as QCOUNT by _time, CLIENT | eval QCOUNT=round(QCOUNT) | convert ctime(_time) as Time | rename CLIENT as \"Client ID\", QCOUNT as \"Total Client Hits\" ] | sort -\"Total Client Hits\" | head 10 | table \"Client ID\", \"Total Client Hits\", Time"

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
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.rpz_top_hits_clients,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        result = compare_results(self.rpz_top_hits_clients,results_list)
        logger.info("-----------------------------------------------------")
        logger.info(self.rpz_top_hits_clients)
        logger.info(len(self.rpz_top_hits_clients))
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

    def test_005_dns_top_firewall_hits(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
	logger.info("DNS Top Firewall Hits")

        search_str = "search index=ib_dns_summary report=si_dns_rpz_hits | fields RPZ_QNAME TOTAL_COUNT DOMAIN_NAME | stats sum(TOTAL_COUNT) as RPZ_HIT_COUNT by RPZ_QNAME DOMAIN_NAME | sort -RPZ_HIT_COUNT | head 10 | eventstats sum(RPZ_HIT_COUNT) as ALL_HIT_COUNT | eval RPZ_HIT_PCT = round(RPZ_HIT_COUNT * 100 / ALL_HIT_COUNT, 2) | rex  field=RPZ_QNAME \"rpz-ip.(?<RPZ_IP_FEED>[^ ]+)\""

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
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.top_dns_firewall_hits,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        result = compare_results(self.top_dns_firewall_hits,results_list)
        logger.info("-----------------------------------------------------")
        logger.info(self.top_dns_firewall_hits)
        logger.info(len(self.top_dns_firewall_hits))
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

    def test_006_dns_firewall_executive_threat(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
	logger.info("DNS Firewall Executive Threat Report")
	
        search_str = "search index=ib_dns_summary report=si_dns_rpz_hits | fields RPZ_QNAME TOTAL_COUNT DOMAIN_NAME | stats sum(TOTAL_COUNT) as RPZ_HIT_COUNT by RPZ_QNAME, DOMAIN_NAME| where RPZ_HIT_COUNT >=0  | sort -RPZ_HIT_COUNT  | head 10  | eventstats sum(RPZ_HIT_COUNT) as ALL_HIT_COUNT  | eval RPZ_HIT_PCT = round(RPZ_HIT_COUNT * 100 / ALL_HIT_COUNT, 2)  | rex  field=RPZ_QNAME \"rpz-ip.(?<RPZ_IP_FEED>[^ ]+)\" | rename RPZ_QNAME as \"RPZ Rule\", RPZ_HIT_PCT as \"Percentage\", RPZ_HIT_COUNT as \"# Hits\", public_description as \"Description\"  | table \"RPZ Rule\" \"Percentage\" \"# Hits\" \"Description\""

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
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.firewall_exec_threat,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        result = compare_results(self.firewall_exec_threat,results_list)
        logger.info("-----------------------------------------------------")
        logger.info(self.firewall_exec_threat)
        logger.info(len(self.firewall_exec_threat))
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

    def test_007_malicious_activity_client(self):
        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        logger.info("Malicious Activity by Client")
    
        search_str= "search index=ib_dns_summary report=si_dns_rpz_hits | stats avg(COUNT) as COUNT by _time, orig_host, VIEW, CLIENT, DOMAIN_NAME, RPZ_QNAME, RPZ_SEVERITY, TOTAL_COUNT, MITIGATION_ACTION, REDIRECTION_RECORD, SUB_TYPE, SUB_VAL | eval SUBSCRIBER_ID = SUB_TYPE + \": \" + SUB_VAL | stats sum(TOTAL_COUNT) as CLIENT_COUNT_BY_DOMAIN, latest(_time) as LATEST_TIME by CLIENT, SUBSCRIBER_ID, DOMAIN_NAME | eventstats sum(CLIENT_COUNT_BY_DOMAIN) as TOTAL_CLIENT_COUNT, max(LATEST_TIME) as MAX_LATEST_TIME by CLIENT, SUBSCRIBER_ID | append [ search index=ib_dns_summary report=si_dns_rpz_hits | eval RECORD_DATA=if(isnull(RECORD_DATA),\"\",RECORD_DATA) | eval RPZ_QNAME=if(isnull(RPZ_QNAME),\"\",RPZ_QNAME) | eval RPZ_SEVERITY=if(isnull(RPZ_SEVERITY),\"\",RPZ_SEVERITY) | stats avg(COUNT) as COUNT by _time orig_host VIEW CLIENT DOMAIN_NAME RPZ_QNAME RPZ_SEVERITY TOTAL_COUNT MITIGATION_ACTION RECORD_DATA | stats sum(TOTAL_COUNT) as CLIENT_COUNT_BY_DOMAIN latest(_time) as LATEST_TIME by CLIENT DOMAIN_NAME ] | sort -CLIENT_COUNT_BY_DOMAIN| where TOTAL_CLIENT_COUNT >=0| eventstats list(DOMAIN_NAME) as TOP3_DOMAINS by CLIENT, SUBSCRIBER_ID| eval TOP_INDEX = 3 - 1| eval TOP3_DOMAINS=mvindex(TOP3_DOMAINS, 0, TOP_INDEX)| dedup CLIENT, SUBSCRIBER_ID| sort -TOTAL_CLIENT_COUNT| head 10| rename CLIENT as \"Client ID\", TOTAL_CLIENT_COUNT as \"# Hits\", TOP3_DOMAINS as \"Domains\", SUBSCRIBER_ID as \"Subscriber ID\", LAST_ACTIVE as \"Last Active\"| table \"Client ID\" \"# Hits\" \"Domains\" |  fields \"Client ID\" \"# Hits\""   

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
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.firewall_exec_threat,results_list)
        logger.info("dumping search results in '%s' 'dumps' directory",sys._getframe().f_code.co_name+"_search_output.txt")
        logger.info("compare_resutls with 'delta' value as 0")
        result = compare_results(self.malicious_client,results_list)
        logger.info("-----------------------------------------------------")
        logger.info(self.malicious_client)
        logger.info(len(self.malicious_client))
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


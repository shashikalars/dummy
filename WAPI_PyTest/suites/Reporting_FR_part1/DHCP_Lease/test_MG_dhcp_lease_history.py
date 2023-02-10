"""
 Copyright (c) Infoblox Inc., 2016
 ReportName          : DHCP Lease History Reports
 ReportCategory      : DHCP Lease
 Number of Test cases: 1
 Execution time      : 302.61 seconds
 Execution Group     : Hour Group (HG)
 Description         : DHCP Lease History reprots will be updated every 1 min. 

 Author   : Raghavendra MN
 History  : 05/31/2016 (Created)
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
import unittest
import time
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results

"""
TEST Steps:
      1.  Input/Preparation  : Adding Network & Range(with 2 min Lease time) . 
                               Reqest Lease
                               wait for 62 sec., 
                               Renew Lease
                               wait till lease gets expired. (i.e., 122 sec., )
      2.  Search     : Performing Search operaion with default & custom filter
      3.  Validation : comparing Search results with Reterived 'Lease' data from NIOS Grid using WAPI.
"""

class DHCPLeaseHistory(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        logger.info('-'*15+"START:DHCP Lease History"+'-'*15)
        cls.test1=[]
        cls.test2=[]
        cls.test3=[]
        cls.test4=[]
        logger.info("Preparation for DHCP Lease History")
        logger.info("Adding network 10.0.0.0/8")
        net_obj = {"members":[{"_struct": "dhcpmember", "ipv4addr":config.grid_vip ,"name":config.grid_fqdn}], \
                "network": "10.0.0.0/8", "network_view": "default"}
        network1 = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(net_obj))
        logger.info("Adding Range 10.0.0.180 - 10.0.0.181 with lease time 120")
        range_obj = {"start_addr":"10.0.0.180","end_addr":"10.0.0.181","member":{"_struct": "dhcpmember","ipv4addr":config.grid_vip,"name": config.grid_fqdn}, \
                 "options":[{"_struct": "dhcpoption","name":"dhcp-lease-time","num": 51,"use_option": True,"value": "120","vendor_class": "DHCP"}]}
        range = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(range_obj)) 
        logger.info("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref'] 
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        logger.info("Wait for 30 sec.,")
        time.sleep(30) #wait for 30 sec, for Member Restart


        #Preparation for Test1  
        cmd="sudo /import/tools/qa/tools/dras/dras -o outfile.txt -n 2 -i "+config.grid_vip
        logger.info("Request lease using dras command for action=Issued")
        fp=os.popen(cmd)
        logger.info(''.join(fp.readlines()))
        logger.info("Peforming WAPI Request to retrieve Lease History informaion for test#1(i.e., Action eq Issued)")
        response = ib_NIOS.wapi_request("GET", object_type="lease?address=10.0.0.18&_return_fields%2b=starts,ends,hardware,server_host_name,client_hostname,protocol,served_by")
        print(response)
        print("===========================================================")
        val = json.loads(response)
        for i in val:
            temp={}
            temp["Member"]=i["server_host_name"]
            temp["Member IP"]=i["served_by"]
            temp["Protocol"]=i["protocol"]
            temp["Action"]="Issued"
            temp["Lease IP"]=i["address"]
            temp["MAC/DUID"]=i["hardware"]
            temp["Lease Start"]=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(i["starts"]))
            temp["Lease End"]=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(i["ends"]))
            cls.test1.append(temp)
            logger.info ("Input Json for test1 validation")
            logger.info(json.dumps(cls.test1, sort_keys=True, indent=4, separators=(',', ': ')))


        #Preparation for Test2
        logger.info("Wait for 65 sec., for Renew operation")
        time.sleep(65)
        logger.info("Request lease using dras command for action=Renewed")
        cmd="sudo /import/tools/qa/tools/dras/dras -f outfile.txt -n 2 -i "+config.grid_vip+" -w"
        fp=os.popen(cmd)
        logger.info(''.join(fp.readlines()))
        logger.info("Peforming WAPI Request to retrieve Lease History informaion for test#1(i.e., Action eq Issued)")
        response = ib_NIOS.wapi_request("GET", object_type="lease?address~=10.0.0.18&_return_fields%2b=starts,ends,hardware,server_host_name,client_hostname,protocol,served_by")
        val = json.loads(response)
        for i in val:
            temp={}
            temp["Member"]=i["server_host_name"]
            temp["Member IP"]=i["served_by"]
            temp["Protocol"]=i["protocol"]
            temp["Action"]="Renewed"
            temp["Lease IP"]=i["address"]
            temp["MAC/DUID"]=i["hardware"]
            temp["Lease Start"]=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(i["starts"]))
            temp["Lease End"]=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(i["ends"]))
            cls.test2.append(temp)
            logger.info ("Input Json for test2 validation")
            logger.info(json.dumps(cls.test2, sort_keys=True, indent=4, separators=(',', ': ')))



        #Preparation for Test3
        logger.info("Wait till 122 sec., for Release events")
        time.sleep(122)
        response = ib_NIOS.wapi_request("GET", object_type="lease?address~=10.0.0.18&_return_fields%2b=starts,ends,hardware,server_host_name,client_hostname,protocol,served_by")
        val = json.loads(response)
        for i in val:
            temp={}
            temp["Member"]=i["server_host_name"]
            temp["Member IP"]=i["served_by"]
            temp["Protocol"]=i["protocol"]
            temp["Action"]="Freed"
            temp["Lease IP"]=i["address"]
            temp["MAC/DUID"]=i["hardware"]
            temp["Lease Start"]=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(i["starts"]))
            temp["Lease End"]=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(i["ends"]))
            cls.test3.append(temp)
            logger.info ("Input Json for test3 validation")
            logger.info(json.dumps(cls.test3, sort_keys=True, indent=4, separators=(',', ': ')))


        #Test4 & Test5 Preparation combination Issued, Renewed & Freed.
        logger.info ("Input Json for test4 & test5 validation")
        cls.test4=cls.test1+cls.test2+cls.test3
        logger.info(json.dumps(cls.test4, sort_keys=True, indent=4, separators=(',', ': ')))

    def test_1_dhcp_lease_history_Filter_with_Action_eq_Issued(self):
        logger.info("TestCase:%s",sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:dhcp:lease_history index=ib_dhcp_lease_history (host=\"*\") * * ACTION=\"Issued\" * * * dhcpd OR dhcpdv6 r-l-e | eval Protocol=if(PROTO==\"dhcpdv6\",\"IPV6\",\"IPV4\") | noop | eval LEASE_START=strftime(START_EPOCH, \"%Y-%m-%d %H:%M:%S\") | noop | eval LEASE_END=strftime(END_EPOCH, \"%Y-%m-%d %H:%M:%S\") | noop | eval FINGER_PRINT=if(isnull(OS_NUMBER) OR OS_NUMBER==0,FP,SFP) | noop | eval DEVICE_CLASS=if(isnull(DEVICE_CLASS), \"Modified or Deleted\", DEVICE_CLASS) | rename host as \"Member\", ACTION as \"Action\", LEASE_IP as \"Lease IP\", MAC_DUID as \"MAC/DUID\", MEMBER_IP as \"Member IP\", OPTION12HOST as \"Host Name\", LEASE_START as \"Lease Start\", LEASE_END as \"Lease End\", FINGER_PRINT as \"Fingerprint\" | convert ctime(_time) as Time | table Time, Member, \"Member IP\", Protocol, Action, \"Lease IP\", \"MAC/DUID\", \"Host Name\", \"Lease Start\", \"Lease End\", \"Fingerprint\""

        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        print(os.system(cmd))
        print("*****************%%%%%*********************")
        try:
            retrived_data=open(config.json_file).read()
            print(retrived_data)
            
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Looks like reporting service not started please check the GRID")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test1,results_list)
        logger.info("compare_resutls")
        result = compare_results(self.test1,results_list)
        print("------------------------------------------------------------")
        print(self.test1)
        print("-----------------------------------*******************88-------------------------")
        print(results_list)
        print("-----------------------------------*******************88-------------------------")
        print(result)
        #result=(0)
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg


    def test_2_dhcp_lease_history_Filter_with_Action_eq_Renew(self):
        logger.info("TestCase:%s",sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:dhcp:lease_history index=ib_dhcp_lease_history (host=\"*\") * * ACTION=\"Renewed\" * * * dhcpd OR dhcpdv6 r-l-e | eval Protocol=if(PROTO==\"dhcpdv6\",\"IPV6\",\"IPV4\") | noop | eval LEASE_START=strftime(START_EPOCH, \"%Y-%m-%d %H:%M:%S\") | noop | eval LEASE_END=strftime(END_EPOCH, \"%Y-%m-%d %H:%M:%S\") | noop | eval FINGER_PRINT=if(isnull(OS_NUMBER) OR OS_NUMBER==0,FP,SFP) | noop | eval DEVICE_CLASS=if(isnull(DEVICE_CLASS), \"Modified or Deleted\", DEVICE_CLASS) | rename host as \"Member\", ACTION as \"Action\", LEASE_IP as \"Lease IP\", MAC_DUID as \"MAC/DUID\", MEMBER_IP as \"Member IP\", OPTION12HOST as \"Host Name\", LEASE_START as \"Lease Start\", LEASE_END as \"Lease End\", FINGER_PRINT as \"Fingerprint\" | convert ctime(_time) as Time | table Time, Member, \"Member IP\", Protocol, Action, \"Lease IP\", \"MAC/DUID\", \"Host Name\", \"Lease Start\", \"Lease End\", \"Fingerprint\""

        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        os.system(cmd)
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Looks like reporting service not started please check the GRID")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test2,results_list)
        logger.info("compare_resutls")
        result = compare_results(self.test2,results_list)
        print("------------------------------------------------------------")
        print(self.test2)
        print("-----------------------------------*******************-------------------------")
        print(results_list)
        print("-----------------------------------*******************-------------------------")
        #print(result)
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg



    def test_3_dhcp_lease_history_Filter_with_Action_eq_Release(self):
        logger.info("TestCase:%s",sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:dhcp:lease_history index=ib_dhcp_lease_history (host=\"*\") * * ACTION=\"Freed\" * * *  dhcpd OR dhcpdv6 r-l-e | eval Protocol=if(PROTO==\"dhcpdv6\",\"IPV6\",\"IPV4\") | noop | eval LEASE_START=strftime(START_EPOCH, \"%Y-%m-%d %H:%M:%S\") | noop | eval LEASE_END=strftime(END_EPOCH, \"%Y-%m-%d %H:%M:%S\") | noop | eval FINGER_PRINT=if(isnull(OS_NUMBER) OR OS_NUMBER==0,FP,SFP) | noop | eval DEVICE_CLASS=if(isnull(DEVICE_CLASS), \"Modified or Deleted\", DEVICE_CLASS) | rename host as \"Member\", ACTION as \"Action\", LEASE_IP as \"Lease IP\", MAC_DUID as \"MAC/DUID\", MEMBER_IP as \"Member IP\", OPTION12HOST as \"Host Name\", LEASE_START as \"Lease Start\", LEASE_END as \"Lease End\", FINGER_PRINT as \"Fingerprint\" | convert ctime(_time) as Time | table Time, Member, \"Member IP\", Protocol, Action, \"Lease IP\", \"MAC/DUID\", \"Host Name\", \"Lease Start\", \"Lease End\", \"Fingerprint\""

        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        os.system(cmd)
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Looks like reporting service not started please check the GRID")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test3,results_list)
        logger.info("compare_resutls")
        result = compare_results(self.test3,results_list)
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg



    def test_4_dhcp_lease_history_Filter_with_Default(self):
        logger.info("TestCase:%s",sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:dhcp:lease_history index=ib_dhcp_lease_history dhcpd OR dhcpdv6 r-l-e | eval Protocol=if(PROTO==\"dhcpdv6\",\"IPV6\",\"IPV4\") | eval LEASE_START=strftime(START_EPOCH, \"%Y-%m-%d %H:%M:%S\") | eval LEASE_END=strftime(END_EPOCH, \"%Y-%m-%d %H:%M:%S\") | eval FINGER_PRINT=if(isnull(OS_NUMBER) OR OS_NUMBER==0,FP,SFP) | lookup nios_member_ip_lookup host output MEMBER_IP | lookup fingerprint_device_class_lookup FINGER_PRINT output DEVICE_CLASS | eval DEVICE_CLASS=if(isnull(DEVICE_CLASS), \"Modified or Deleted\", DEVICE_CLASS) | rename host as \"Member\", ACTION as \"Action\", LEASE_IP as \"Lease IP\", MAC_DUID as \"MAC/DUID\", MEMBER_IP as \"Member IP\", OPTION12HOST as \"Host Name\", LEASE_START as \"Lease Start\", LEASE_END as \"Lease End\", FINGER_PRINT as \"Fingerprint\" | convert ctime(_time) as Time | table Time, Member, \"Member IP\", Protocol, Action, \"Lease IP\", \"MAC/DUID\", \"Host Name\", \"Lease Start\", \"Lease End\", \"Fingerprint\""

        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        os.system(cmd)
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Looks like reporting service not started please check the GRID")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test4,results_list)
        logger.info("compare_resutls")
        result = compare_results(self.test4,results_list)
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg


    def test_5_dhcp_lease_history_Filter_with_Member_Filter(self):
        logger.info("TestCase:%s",sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:dhcp:lease_history index=ib_dhcp_lease_history (host=\""+config.grid_fqdn+"\") * * * * * *  dhcpd OR dhcpdv6 r-l-e | eval Protocol=if(PROTO==\"dhcpdv6\",\"IPV6\",\"IPV4\") | noop | eval LEASE_START=strftime(START_EPOCH, \"%Y-%m-%d %H:%M:%S\") | noop | eval LEASE_END=strftime(END_EPOCH, \"%Y-%m-%d %H:%M:%S\") | noop | eval FINGER_PRINT=if(isnull(OS_NUMBER) OR OS_NUMBER==0,FP,SFP) | noop | eval DEVICE_CLASS=if(isnull(DEVICE_CLASS), \"Modified or Deleted\", DEVICE_CLASS) | rename host as \"Member\", ACTION as \"Action\", LEASE_IP as \"Lease IP\", MAC_DUID as \"MAC/DUID\", MEMBER_IP as \"Member IP\", OPTION12HOST as \"Host Name\", LEASE_START as \"Lease Start\", LEASE_END as \"Lease End\", FINGER_PRINT as \"Fingerprint\" | convert ctime(_time) as Time | table Time, Member, \"Member IP\", Protocol, Action, \"Lease IP\", \"MAC/DUID\", \"Host Name\", \"Lease Start\", \"Lease End\", \"Fingerprint\""

        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        os.system(cmd)
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Looks like reporting service not started please check the GRID")
        output_data = json.loads(retrived_data)
        results_list = output_data['results']
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",self.test4,results_list)
        logger.info("compare_resutls")
        result = compare_results(self.test4,results_list)
        if result == 0:
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg

    @classmethod
    def teardown_class(cls):
        logger.info("Cleanup, Deleting Added network")
    	delnetwork = ib_NIOS.wapi_request('GET', object_type="network?network~=10.0.0.0/8")
        ref = json.loads(delnetwork)[0]['_ref']
        del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)
        logger.info('-'*15+"END:DHCP Lease History"+'-'*15)

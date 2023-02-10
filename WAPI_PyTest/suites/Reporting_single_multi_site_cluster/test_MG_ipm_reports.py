import config
import json
import os
import pytest
import pexpect
import re
import sys
import subprocess
from time import sleep
import time
import unittest
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results


class IPAM_reports(unittest.TestCase):

    #NEW PERPETUAL LICENSE VALIDATION

    @pytest.mark.run(order=1)
    def test_1_new_perpetual_license_validation_single_site(self):

        logger.info("TestCase:"+sys._getframe().f_code.co_name)
        logger.info("New Perpetual License Validation")

        #cmd="python /import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_single_multi_site_cluster/fetch_search_head_indexer.py search_head "+config.reporting_member1_ip+":"+config.reporting_member2_ip
        #search_head_ip=subprocess.check_output(cmd,shell=True)


        cmd="grep 'host=10.' ~/.splunkrc"
        host=subprocess.check_output(cmd,shell=True)
        print host
        search_head_ip=host.strip("host=\n")
        print("search_head_ip is "+ search_head_ip)
        
        #print("%%%%%%%%%%%%%%%%%",search_head_ip)
        #new_search_head_ip=search_head_ip.split("\n")
        #print("$$$$$$$$$$$$$$$$$",new_search_head_ip)
        #sip = new_search_head_ip[-2]
        #print("search head is "+sip)

        file_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=no  root@'+str(search_head_ip)+' "cat /opt/splunksearchhead/etc/licenses/fixed-sourcetype_E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855/500MB.lic"'
        validation_result = subprocess.check_output(file_validation, shell=True)
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$",validation_result)
        assert re.search(r'.*<creation_time>1644796800</creation_time>*',str(validation_result))
        assert re.search(r'.*<relative_expiration_interval>126230400</relative_expiration_interval>*',str(validation_result))
        assert re.search(r'.*<absolute_expiration_time>1802563200</absolute_expiration_time>*',str(validation_result))

    # IPAMv4 NETWORK USAGE STATISTICS

    @pytest.mark.run(order=2)
    def test_2_IPAMv4_network_usage_statistics(self):
    

        logger.info ("Input Json Data for IPAMv4 Network Usage Statistics report validation")
        logger.info("Test:"+sys._getframe().f_code.co_name)
        
        search_str="search sourcetype=ib:ipam:network index=ib_ipam"
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        logger.info (cmd)
        print(os.system(cmd))
        
        print("-------------%%%----------")
        
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operation failed, Please check Grid Configuration")
        output_data = json.loads(retrived_data)
        results_list = output_data['results'][0]
        print(results_list)

        host=re.findall(config.grid_fqdn,results_list['host'])
        print(host)
        index=re.findall('ib_ipam',results_list['index'])
        print(index)
        source=re.findall('/infoblox/var/reporting/ipam_networks_report.csv',results_list['source'])
        print(source)
        sourcetype=re.findall('ib:ipam:network',results_list['sourcetype'])
        print(sourcetype)


        if host==[config.grid_fqdn] and index==['ib_ipam'] and source==['/infoblox/var/reporting/ipam_networks_report.csv'] and sourcetype==['ib:ipam:network']:
                print("Report successfully generated")
                assert True
        elif host==[] or index==[] or source==[] or sourcetype==[]:
                print("Partial Report is generated!")
                assert False
        else:
                print("Report not found..please check the grid")
                assert False



    # IPAMv4 NETWORK USAGE TREND

    @pytest.mark.run(order=3)
    def test_3_IPAMv4_network_usage(self):
    
        logger.info ("Input Json Data for IPAMv4 Network Usage Trend report validation")
        logger.info("Test:"+sys._getframe().f_code.co_name)

        search_str="search sourcetype=ib:ipam:network index=ib_ipam"
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        logger.info (cmd)
        print(os.system(cmd))
        
        print("-------------%%%----------")
        
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operation failed, Please check Grid Configuration")
        output_data = json.loads(retrived_data)
        results_list = output_data['results'][0]
        print(results_list)

        host=re.findall(config.grid_fqdn,results_list['host'])
        print(host)
        index=re.findall('ib_ipam',results_list['index'])
        print(index)
        source=re.findall('/infoblox/var/reporting/ipam_networks_report.csv',results_list['source'])
        print(source)
        sourcetype=re.findall('ib:ipam:network',results_list['sourcetype'])
        print(sourcetype)


        if host==[config.grid_fqdn] and index==['ib_ipam'] and source==['/infoblox/var/reporting/ipam_networks_report.csv'] and sourcetype==['ib:ipam:network']:
                print("Report successfully generated")
                assert True
        elif host==[] or index==[] or source==[] or sourcetype==[]:
                print("Partial Report is generated!")
                assert False
        else:
                print("Report not found..please check the grid")
                assert False


    # IPAMv4 TOP UTILISED NETWORKS

    @pytest.mark.run(order=4)
    def test_4_IPAMv4_top_utilised_networks(self):
    
        logger.info ("Input Json Data for IPAMv4 Top Utilised Networks report validation")
        logger.info("Test:"+sys._getframe().f_code.co_name)

        search_str="search sourcetype=ib:ipam:network index=ib_ipam"
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        logger.info (cmd)
        print(os.system(cmd))
        
        print("-------------%%%----------")
        
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operation failed, Please check Grid Configuration")
        output_data = json.loads(retrived_data)
        results_list = output_data['results'][0]
        print(results_list)

        host=re.findall(config.grid_fqdn,results_list['host'])
        print(host)
        index=re.findall('ib_ipam',results_list['index'])
        print(index)
        source=re.findall('/infoblox/var/reporting/ipam_networks_report.csv',results_list['source'])
        print(source)
        sourcetype=re.findall('ib:ipam:network',results_list['sourcetype'])
        print(sourcetype)


        if host==[config.grid_fqdn] and index==['ib_ipam'] and source==['/infoblox/var/reporting/ipam_networks_report.csv'] and sourcetype==['ib:ipam:network']:
                print("Report successfully generated")
                assert True
        elif host==[] or index==[] or source==[] or sourcetype==[]:
                print("Partial Report is generated!")
                assert False
        else:
                print("Report not found..please check the grid")
                assert False


    # DHCPv4 TOP UTILISED NETWORKS

    @pytest.mark.run(order=5)
    def test_5_DHCPv4_top_utilised_networks(self):
    
        
        logger.info ("Input Json Data for DHCPv4 Top Utilized networks report validation")
        logger.info("Test:"+sys._getframe().f_code.co_name)

        search_str="search sourcetype=ib:dhcp:network index=ib_dhcp"
        cmd = config.search_py + " '" + search_str + "' --output_mode=json"
        logger.info (cmd)
        print(os.system(cmd))
        
        print("-------------%%%----------")
        
        try:
            retrived_data=open(config.json_file).read()
        except Exception, e:
            logger.error('search operation failed due to %s',e)
            raise Exception("Search operation failed, Please check Grid Configuration")
        output_data = json.loads(retrived_data)
        results_list = output_data['results'][0]
        print(results_list)

        host=re.findall(config.grid_fqdn,results_list['host'])
        print(host)
        index=re.findall('ib_dhcp',results_list['index'])
        print(index)
        source=re.findall('/infoblox/var/reporting/dhcp_networks_report.csv',results_list['source'])
        print(source)
        sourcetype=re.findall('ib:dhcp:network',results_list['sourcetype'])
        print(sourcetype)


        if host==[config.grid_fqdn] and index==['ib_dhcp'] and source==['/infoblox/var/reporting/dhcp_networks_report.csv'] and sourcetype==['ib:dhcp:network']:
                print("Report successfully generated")
                assert True
        elif host==[] or index==[] or source==[] or sourcetype==[]:
                print("Partial Report is generated!")
                assert False
        else:
                print("Report not found..please check the grid")
                assert False

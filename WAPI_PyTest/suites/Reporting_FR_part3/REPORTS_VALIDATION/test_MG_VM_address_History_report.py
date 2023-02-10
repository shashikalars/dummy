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


class VM_address_History(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_1_VM_address_history(self):
    
    # Expected Values

        # VM ADDRESS HISTORY

        test1 = [{"IP Address":"2.2.2.9","Action":"Allocated","Address Type":"Fixed","FQDN":"record.zone.com","VM Name/Instance Name":"567","Network View":"default","Tenant ID":"375","Tenant Name":"375","Is Primary Interface":"No","Management Platform":"vm218ctest"},{"IP Address":"2.0.0.9","Action":"Allocated","Address Type":"Fixed","MAC Address":"15:86:32:12:00:96","VM Name/Instance Name":"361","Network":"2.0.0.0/24","Network View":"default","Tenant ID":"395","Tenant Name":"395","Is Primary Interface":"No","Management Platform":"vm216ctest"}]
        logger.info ("Input Json Data for VM Address history report validation")
        logger.info(json.dumps(test1, sort_keys=True, indent=4, separators=(',', ': ')))
        

        
        logger.info("Test:"+sys._getframe().f_code.co_name)
        search_str="search sourcetype=ib:reserved2 source=ib:cloud:vm_address_history index=ib_cloud | eval IS_PRIMARY_IFC=case(is_primary_ifc==1, \"Yes\", is_primary_ifc==0, \"No\") | eval TYPE=case(address_type==0, \"Floating\", address_type==1, \"Fixed\", address_type==2, \"Private\", address_type==3, \"Public\", address_type==4, \"Elastic\", 1==1, address_type) | convert ctime(_time) as Time  | sort -Time address network_view | rename address as \"IP Address\", TYPE as \"Address Type\", ACTION as \"Action\", IS_PRIMARY_IFC as \"Is Primary Interface\", mac_address as \"MAC Address\", port_id as \"Port ID\", cnames as \"CNAME(s)\", fqdn as \"FQDN\", vm_name as \"VM Name/Instance Name\", network as \"Network\", network_view as \"Network View\", tenant_id as \"Tenant ID\", TENANT_NAME as \"Tenant Name\", location as \"Location\", vlan_id as \"VLAN ID\", application_type as \"Application Type\", private_hostname as \"Private Hostname\", public_hostname as \"Public Hostname\", private_address as \"Private Address\", public_address as \"Public Address\", elastic_address as \"Elastic Address\", interface_name as \"Interface Name\", mgmt_platform as \"Management Platform\", vm_vpc_id as \"VPC ID\", vm_vpc_name as \"VPC Name\", vpc_addr as \"VPC Network\", vm_hostname as \"VM Hostname\" | table Time \"IP Address\" \"Action\" \"Address Type\" \"MAC Address\" \"CNAME(s)\" \"Port ID\" \"FQDN\" \"VM Name/Instance Name\" \"Network\" \"Network View\" \"Tenant ID\" \"Tenant Name\" \"Location\" \"VLAN ID\" \"Application Type\" \"Private Hostname\" \"Public Hostname\" \"Private Address\" \"Public Address\" \"Elastic Address\" \"Interface Name\" \"Is Primary Interface\" \"Management Platform\" \"VPC ID\" \"VPC Name\" \"VPC Network\" \"VM Hostname\""
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
        results_list = output_data['results']
        results_dist= results_list[-240::1]
        search_dump(sys._getframe().f_code.co_name+"_search_output.txt",test1,results_dist)
        logger.info("compare_results with 'delta=1'")
        result = compare_results(test1,results_list,1)
        print(result)
        logger.info("-----------------------------------------------------")
        logger.info(test1)
        logger.info(len(test1))
        logger.info("--------------------**************-------------------")
        logger.info(results_list)
        logger.info(len(results_list))
        logger.info("-----------------------------------------------------")

        if result == 0:
            print("PASSED")
            logger.info("Search validation result: %s (PASS)",result)
        else:
            logger.error("Search validation result: %s (FAIL)",result)
        msg = 'Validation is not matching for object which is retrieved from DB %s', result
        assert result == 0, msg

        

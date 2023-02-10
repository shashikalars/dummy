#!/usr/bin/env python
__author__ = "Shivasai"
__email__  = "sbandaru@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. SA GRID                                                                          #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415)                                      #
########################################################################################

import re
import config
import pytest
import unittest
import logging
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util





def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)
    
    
def restart_services():
    """
    Restart Services
    """
    print("Restart services")
    grid =  ib_NIOS.wapi_request('GET', object_type="grid",grid_vip=config.grid_vip)
    ref = json.loads(grid)[0]['_ref']
    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
    restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices", fields=json.dumps(data),grid_vip=config.grid_vip)
    sleep(30)

class NIOSSPT_8833(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_001_create_network_view(self):
        """
        Create network view 
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 1 Started                |")
        display_msg("------------------------------------------------")
        data={"name": "netview"}
        response=ib_NIOS.wapi_request('POST', object_type="networkview",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            assert False
        else:
            assert True
   
        restart_services()
        print("Testcase 1 completed")
        
        
    @pytest.mark.run(order=2)
    def test_002_create_IPV6_network(self):
        """
        Create network view 
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 2 Started                |")
        display_msg("------------------------------------------------")
        data = {"network_view": "netview", "network": "AB80::/64"}
        response=ib_NIOS.wapi_request('POST', object_type="ipv6network",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            assert False
        else:
            assert True
        print("Testcase 2 completed")
        
        
    @pytest.mark.run(order=3)
    def test_003_create_IPV6_fixedaddress(self):
        """
        Create network view 
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 3 Started                |")
        display_msg("------------------------------------------------")
        
        data = {"network_view": "netview", "ipv6addr": "AB80::1", "duid": "DABA"}
        response=ib_NIOS.wapi_request('POST', object_type="ipv6fixedaddress",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            assert False
        else:
            assert True
        print("Testcase 3 completed")
       

    @pytest.mark.run(order=4)
    def test_004_query_ipv6_address_using_lowercase(self):
        """
        query ipv6 address using lowercase letters (ab80)
        """       
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 4 Started                |")
        display_msg("------------------------------------------------")
        
        addr = ib_NIOS.wapi_request('GET', object_type="ipv6address?network_view=netview&network=ab80::/64&_return_fields=ip_address",grid_vip=config.grid_vip)
        print(addr)
        if "ab80::1" in addr:
            assert True
        else:
            assert False
 
        print("Testcase 4 completed") 
    
        
    @pytest.mark.run(order=5)
    def test_005_query_ipv6_address_using_uppercase(self):
        """
        query ipv6 address using uppercase letters (AB80)
        """       
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 5 Started                |")
        display_msg("------------------------------------------------")
        
        addr = ib_NIOS.wapi_request('GET', object_type="ipv6address?network_view=netview&network=AB80::/64&_return_fields=ip_address",grid_vip=config.grid_vip)
        print(addr)
        if "ab80::1" in addr:
            assert True
        else:
            assert False
 
        print("Testcase 5 completed")
        
        
    @pytest.mark.run(order=6)
    def test_006_query_ipv6_address_using_upper_lowercase(self):
        """
        query ipv6 address using upper and lower case letters (Ab80)
        """       
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 6 Started                |")
        display_msg("------------------------------------------------")
        
        addr = ib_NIOS.wapi_request('GET', object_type="ipv6address?network_view=netview&network=Ab80::/64&_return_fields=ip_address",grid_vip=config.grid_vip)
        print(addr)
        if "ab80::1" in addr:
            assert True
        else:
            assert False
 
        print("Testcase 6 completed")
        
        
  

    @pytest.mark.run(order=7)
    def test_007_query_ipv6_using_complete_ipv6address(self):
        """
        query ipv6 address using upper and lower case letters (Ab80)
        """       
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 7 Started                |")
        display_msg("------------------------------------------------")
        
        addr = ib_NIOS.wapi_request('GET', object_type="ipv6address?network_view=netview&network=Ab80:0:0:0:0:0:0:0/64&_return_fields=ip_address",grid_vip=config.grid_vip)
        print(addr)
        if "ab80::1" in addr:
            assert True
        else:
            assert False
 
        print("Testcase 7 completed")  
        

    @pytest.mark.run(order=8)
    def test_008_query_ipv6network_using_lowercase(self):
        """
        query ipv6 network using lowercase letters (ab80)
        """       
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 8 Started                |")
        display_msg("------------------------------------------------")
        
        addr = ib_NIOS.wapi_request('GET', object_type="ipv6network?network_view=netview&network=ab80::/64",grid_vip=config.grid_vip)
        print(addr)
        if "ab80::/64" in addr:
            assert True
        else:
            assert False
 
        print("Testcase 8 completed") 
    
        
    @pytest.mark.run(order=9)
    def test_009_query_ipv6network_using_uppercase(self):
        """
        query ipv6 network using uppercase letters (AB80)
        """       
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 9 Started                |")
        display_msg("------------------------------------------------")
        
        addr = ib_NIOS.wapi_request('GET', object_type="ipv6network?network_view=netview&network=AB80::/64",grid_vip=config.grid_vip)
        print(addr)
        if "ab80::/64" in addr:
            assert True
        else:
            assert False
 
        print("Testcase 9 completed")
        
        
    @pytest.mark.run(order=10)
    def test_010_query_ipv6network_using_upper_lowercase(self):
        """
        query ipv6 network using upper and lower case letters (Ab80)
        """       
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 10 Started               |")
        display_msg("------------------------------------------------")
        
        addr = ib_NIOS.wapi_request('GET', object_type="ipv6network?network_view=netview&network=Ab80::/64",grid_vip=config.grid_vip)
        print(addr)
        if "ab80::/64" in addr:
            assert True
        else:
            assert False
 
        print("Testcase10 completed")
        
        
  

    @pytest.mark.run(order=11)
    def test_011_query_ipv6network_using_complete_ipv6address(self):
        """
        query ipv6 network using complete ipv6
        """       
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 11 Started               |")
        display_msg("------------------------------------------------")
        
        addr = ib_NIOS.wapi_request('GET', object_type="ipv6network?network_view=netview&network=Ab80:0:0:0:0:0:0:0/64",grid_vip=config.grid_vip)
        print(addr)
        if "ab80::/64" in addr:
            assert True
        else:
            assert False
 
        print("Testcase 11 completed")  
    


    @pytest.mark.run(order=12)
    def test_012_create_IPV6_network_container(self):
        """
        Create network container
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 12 Started               |")
        display_msg("------------------------------------------------")
        data = {"network_view": "netview", "network": "CD00::/64"}
        response=ib_NIOS.wapi_request('POST', object_type="ipv6networkcontainer",fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            assert False
        else:
            assert True
        print("Testcase 12 completed")
        
        
    @pytest.mark.run(order=13)
    def test_013_search_ipv6networkcontainer_using_lowercase(self):
        """
        query ipv6 ipv6networkcontainer using lower case letters (cd00)
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 13 Started               |")
        display_msg("------------------------------------------------")
        
        addr = ib_NIOS.wapi_request('GET', object_type="ipv6networkcontainer?network_view=netview&network=CD00::/64",grid_vip=config.grid_vip)
        print(addr)
        if "cd00::/64" in addr:
            assert True
        else:
            assert False
 
        print("Testcase 13 completed")
        
        
    @pytest.mark.run(order=14)
    def test_014_query_ipv6networkcontainer_using_uppercase(self):
        """
        query ipv6 ipv6networkcontainer using uppercase letters (CD00)
        """       
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 14 Started               |")
        display_msg("------------------------------------------------")
        
        addr = ib_NIOS.wapi_request('GET', object_type="ipv6networkcontainer?network_view=netview&network=CD00::/64",grid_vip=config.grid_vip)
        print(addr)
        if "cd00::/64" in addr:
            assert True
        else:
            assert False
 
        print("Testcase 14 completed")
        
        
  

    @pytest.mark.run(order=15)
    def test_015_query_ipv6networkcontainer_using_upper_lowercase(self):
        """
        query ipv6networkcontainer using upper and lower case letters (Cd00)
        """       
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 15 Started               |")
        display_msg("------------------------------------------------")
        
        addr = ib_NIOS.wapi_request('GET', object_type="ipv6networkcontainer?network_view=netview&network=Cd00::/64",grid_vip=config.grid_vip)
        print(addr)
        if "cd00::/64" in addr:
            assert True
        else:
            assert False
 
        print("Testcase 15 completed")
        
        
  

    @pytest.mark.run(order=16)
    def test_016_query_ipv6network_using_complete_ipv6address(self):
        """
        query ipv6 network using complete ipv6
        """       
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 16 Started               |")
        display_msg("------------------------------------------------")
        
        addr = ib_NIOS.wapi_request('GET', object_type="ipv6networkcontainer?network_view=netview&network=Cd00:0:0:0:0:0:0:0/64",grid_vip=config.grid_vip)
        print(addr)
        if "cd00::/64" in addr:
            assert True
        else:
            assert False
 
        print("Testcase 16 completed")
        
        
    @pytest.mark.run(order=17)
    def test_017_clean_up(self):
        """
        delete all fields
        """   
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case 17 Started               |")
        display_msg("------------------------------------------------")  
        
        ipv6fixedaddress=ib_NIOS.wapi_request('GET', object_type="ipv6fixedaddress?ipv6addr=ab80::1")
        response=json.loads(ipv6fixedaddress)[0]['_ref']
        response=ib_NIOS.wapi_request('DELETE',ref=response)
        
        if type(response) == tuple:
            assert False
        ipv6network=ib_NIOS.wapi_request('GET', object_type="ipv6network?network=ab80::/64")
        response=json.loads(ipv6network)[0]['_ref']
        response=ib_NIOS.wapi_request('DELETE',ref=response)
        if type(response) == tuple:
            assert False

        ipv6networkcontainer=ib_NIOS.wapi_request('GET', object_type="ipv6networkcontainer?network=cd00::/64")
        response=json.loads(ipv6networkcontainer)[0]['_ref']
        response=ib_NIOS.wapi_request('DELETE',ref=response)
        if type(response) == tuple:
            assert False


        
        networkview=ib_NIOS.wapi_request('GET', object_type="networkview?name=netview")
        response=json.loads(networkview)[0]['_ref']
        response=ib_NIOS.wapi_request('DELETE',ref=response)
        if type(response) == tuple:
            assert False

        else:
            assert True
            
        restart_services() 
        print("Testcase 17 completed")
        
        

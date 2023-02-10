import datetime
from ib_utils.common_utilities import generate_token_from_file
import re
import config
import pytest
import pexpect
import unittest
import sys
import logging
import os
import os.path
from os.path import join
import subprocess
import commands
import json
import time
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util
import pdb


class NIOSSPT_12433(unittest.TestCase):


	@pytest.mark.run(order=1)
        def test_001_Add_IPv4_network_container(self):
               logging.info("Add IPv4 network container")
               data={"network": "2.0.0.0/8","network_view": "default"}
               response = ib_NIOS.wapi_request('POST', object_type="networkcontainer",fields=json.dumps(data))
               print(response)
               res=response
               res = json.loads(res)
               print(res)
               if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                                assert False
                        print("Test Casie 1 Execution Completed")

        @pytest.mark.run(order=2)
        def test_002_Validate_addition_of_IPv4_network_container(self):
                logging.info("Validate Addition of IPv4 network container")
                data={'"network"': '"2.0.0.0/8"'}
                get_temp=ib_NIOS.wapi_request('GET', object_type="networkcontainer",params="?_inheritance=True&_return_fields=network")
                print(get_temp)
                get_temp = get_temp.replace("\n","").replace(" ","")
                print('my get_temp is',get_temp)
                for i in data:
                        if i in get_temp:
                                assert True
                        else:
                                assert False
                sleep(10)
                print("Test Case 2 Execution Completed")


	@pytest.mark.run(order=3)
        def test_003_Enable_Threshold_in_above_network_container(self):
                logging.info("Enable_Threshold_in_above_network_container")
                data= {"network": "2.0.0.0/8"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer",fields=json.dumps(data))
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify Host record")
                data = {"enable_dhcp_thresholds":True}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 3 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=4)
        def test_004_Add_2nd_IPv4_network_container(self):
               logging.info("Add 2nd IPv4 network container")
               data={"network": "2.0.0.0/12","network_view": "default"}
               response = ib_NIOS.wapi_request('POST', object_type="networkcontainer",fields=json.dumps(data))
               print(response)
               res=response
               res = json.loads(res)
               print(res)
               if type(response) == tuple:
                        if response[0]==400 or response[0]==401:
                                assert False
                        print("Test Casie 4 Execution Completed")

        @pytest.mark.run(order=5)
        def test_005_Validate_addition_of_2nd_IPv4_network_container(self):
                logging.info("Validate Addition of 2nd IPv4 network container")
                data={'"network"': '"2.0.0.0/12"'}
                get_temp=ib_NIOS.wapi_request('GET', object_type="networkcontainer",params="?_inheritance=True&_return_fields=network")
                print(get_temp)
                get_temp = get_temp.replace("\n","").replace(" ","")
                print('my get_temp is',get_temp)
                for i in data:
                        if i in get_temp:
                                assert True
                        else:
                                assert False
                sleep(10)
                print("Test Case 5 Execution Completed")

	@pytest.mark.run(order=6)
        def test_006_Validate_high_and_low_water_marks_on_2nd_network_container(self):
                logging.info("Validate_high_and_low_water_marks_on_2nd_network_container")
		get_ref = ib_NIOS.wapi_request('GET',object_type="networkcontainer",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="networkcontainer",ref=ref1,params="?_inheritance=True&_return_fields=network,high_water_mark,low_water_mark")
                print(output)
                output=json.loads(output)
                print(output)
                result = {'network':'2.0.0.0/12','high_water_mark': 95, 'low_water_mark': 0}
                HWM=output['high_water_mark']['value']
                LWM=output['low_water_mark']['value']
                NETWORK=output['network']
                output={'network':NETWORK,'high_water_mark':HWM, 'low_water_mark':LWM}

                for i in result:
                    if output[i] == result[i]:
                        assert True
                    else:
                        assert False
                print(result)
                sleep(10)
                print("Test Case 6 Execution Completed")

	@pytest.mark.run(order=7)
        def test_007_Edit_Threshold_in_above_network_container(self):
                logging.info("Edit_Threshold_in_above_network_container")
                data= {"network": "2.0.0.0/8"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="networkcontainer",fields=json.dumps(data))
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify Host record")
                data = {'high_water_mark': 99, 'low_water_mark': 7}
                response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
                print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 7 Execution Completed")
                sleep(5)


	@pytest.mark.run(order=8)
        def test_008_Validate_Updated_high_and_low_water_marks_on_2nd_network_container(self):
                logging.info("Validate_updated_high_and_low_water_marks_on_2nd_network_container")
                get_ref = ib_NIOS.wapi_request('GET',object_type="networkcontainer",grid_vip=config.grid_vip)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[1]['_ref']
                print(ref1)
                output = ib_NIOS.wapi_request('GET',object_type="networkcontainer",ref=ref1,params="?_return_fields=network,high_water_mark,low_water_mark")
                print(output)
                output=json.loads(output)
                print(output)
                result = {'network':'2.0.0.0/12','high_water_mark': 95, 'low_water_mark': 0}
                for i in result:
                    if output[i] == result[i]:
                        assert True
                    else:
                        assert False
                print(result)
                sleep(10)
                print("Test Case 6 Execution Completed")



        @pytest.mark.run(order=9)
        def test_009_Validate_Updated_high_and_low_water_marks_on_2nd_network_container(self):
                logging.info("Validate_updated_high_and_low_water_marks_on_2nd_network_container")
                get_ref = ib_NIOS.wapi_request('GET',object_type="networkcontainer")
                for ref in json.loads(get_ref):
                    if '2.0.0.0/8' in ref["network"]:
                        ib_NIOS.wapi_request('DELETE',object_type=ref['_ref'])
                print("Test Case 6 Execution Completed")

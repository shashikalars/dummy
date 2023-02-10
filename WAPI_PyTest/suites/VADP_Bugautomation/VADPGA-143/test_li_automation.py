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
#import ib_utils.ib_get as ib_get
from time import sleep
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="license.log" ,level=logging.DEBUG,filemode='w')


class NetworkView(unittest.TestCase):

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
    
    @pytest.mark.run(order=1)
    def test_install_tp_software_license(self):
        cmd='/import/qaddi/sramanathan/IBQACI/set_license_name.exp ' +str(config.grid_member1_vip)+ ' "Add Threat Protection \(Software add-on\) license\"'
        os.system(cmd)
        sleep(120)
    
    @pytest.mark.run(order=2)        
    def test_install_tp_license(self):
        cmd1='/import/qaddi/sramanathan/IBQACI/set_license_name.exp ' +str(config.grid_member1_vip)+ ' "Add Threat Protection Update license\"' 
        rc1=os.system(cmd1)
        #logging.info(rc1)
        logging.info("=======================")
        sleep(120)
    
    @pytest.mark.run(order=3)
    def test_get_tp_sub_license(self):
        logging.info("GET TP Subscription License")
        response = ib_NIOS.wapi_request('GET', object_type="member:license?type=TP_SUB")
        logging.info(response)
        logging.info("============================")
	res = json.loads(response)
	for i in res:
	    if i["type"] == "TP_SUB":
		logging.info("found")

    @pytest.mark.run(order=4)
    def test_get_tp_update_license(self):
        logging.info("GET TP Software Add on License")
        response = ib_NIOS.wapi_request('GET', object_type="member:license?type=SW_TP")
        logging.info(response)
        logging.info("============================")
        res = json.loads(response)
        for i in res:
            if i["type"] == "SW_TP":
                logging.info("found")
    
    @pytest.mark.run(order=5)
    def test_get_dns_license(self):
        logging.info("GET DNS License")
        response = ib_NIOS.wapi_request('GET', object_type="member:license?type=DNS")
        logging.info(response)
        logging.info("============================")
        res = json.loads(response)
        for i in res:
            if i["type"] == "DNS":
                logging.info("found")
    
    @pytest.mark.run(order=6)
    def test_get_dhcp_license(self):
        logging.info("GET DNS License")
        response = ib_NIOS.wapi_request('GET', object_type="member:license?type=DHCP")
        logging.info(response)
        logging.info("============================")
        res = json.loads(response)
        for i in res:
            if i["type"] == "DHCP":
                logging.info("found")
 
    @pytest.mark.run(order=7)
    def test_get_grid_license(self):
        logging.info("GET Grid License")
        response = ib_NIOS.wapi_request('GET', object_type="member:license?type=GRID")
        logging.info(response)
        logging.info("============================")
        res = json.loads(response)
        for i in res:
            if i["type"] == "GRID":
                logging.info("found")
   
    @pytest.mark.run(order=8)
    def test_get_vnios_license(self):
        logging.info("GET VNIOS License")
        response = ib_NIOS.wapi_request('GET', object_type="member:license?type=VNIOS")
        logging.info(response)
        logging.info("============================")
        res = json.loads(response)
        for i in res:
            if i["type"] == "GRID":
                logging.info("found")
    
    @pytest.mark.run(order=9)
    def test_delete_license_validation(self):
        logging.info("DELETE Threat Protection Software License")
        sw_lic = ib_NIOS.wapi_request('GET', object_type="member:license?type=SW_TP")
        ref_lic = json.loads(sw_lic)[0]['_ref']
        logging.info(ref_lic)
        del_status = ib_NIOS.wapi_request('DELETE', object_type = ref_lic)
        logging.info(del_status)
        sleep(30)
        logging.info("============================")
        response = ib_NIOS.wapi_request('GET', object_type="member:license")
        logging.info(response)
        res = json.loads(response)
        for i in res:
            if i["type"] != "SW_TP":
                logging.info("TP Software License is not Available")
     
    @pytest.mark.run(order=10)
    def test_install_permananent_license(self):
        logging.info("Generate Permanent License")
        logging.info("Generate Permanent License")
        vm_name=commands.getstatusoutput('identify_lab_unit '+str(config.grid_member1_vip))
        vm_id=vm_name[1].split(" ")[8]
        retrieve_hw_id=commands.getstatusoutput('get_lab_info -H '+str(vm_id)+' |grep HWID|cut -d"=" -f2')
        print retrieve_hw_id
        res= retrieve_hw_id[1]
        print res
        scp_cmd="scp -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null 2>/dev/null /import/qaddi/mavudayappan/generatelic root@"+str(config.grid_member1_vip)+":"
        os.system(scp_cmd)
        generate_license ='sh License/hw_id.sh ' +str(config.grid_member1_vip)+' '+str(res)
        os.system(generate_license)
        sleep(30)    

    @pytest.mark.run(order=11)
    def test_get_tp_software_license(self):
        logging.info("GET TP Software Add on License")
        response = ib_NIOS.wapi_request('GET', object_type="member:license?type=SW_TP")
        logging.info(response)
        logging.info("============================")
        res = json.loads(response)
        for i in res:
            if i["type"] == "SW_TP":
                logging.info("found")
  
    

    @classmethod
    def teardown_class(cls):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """
        logging.info("TEAR DOWN METHOD")   


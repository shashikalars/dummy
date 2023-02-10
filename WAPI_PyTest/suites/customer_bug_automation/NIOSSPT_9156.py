__author__ = "Aditya G"
__email__  = "adityag@infoblox.com"

########################################################################################
#  Grid Set up required:                                                               #
#  1. Grid Master + Member                                                             #
#  2. Licenses : DNS, DHCP, Grid, NIOS (IB-V1415),DTC                                  #
########################################################################################

import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as ib_TOKEN
from time import sleep
import commands
import json, ast
import time
import getpass
import sys
import pexpect


logging.basicConfig(filename='niosspt9156.log', filemode='w', level=logging.DEBUG)


class NIOSSPT_9156(unittest.TestCase):
    @pytest.mark.order(order=1)
    def test001_create_view1_and_add_zone(self):
        logging.info("Creating view1")
        data={"name": "view1"}
        view1_ref=ib_NIOS.wapi_request('POST',object_type='view',fields=json.dumps(data))
        logging.info(view1_ref)
        if bool(re.match("\"view*.",str(view1_ref))):
            logging.info("view1 created succesfully")
            logging.info("Creating zone xyz.com")
            data={"fqdn":"xyz.com","view":"view1","grid_primary":[{"name": config.grid_fqdn,"stealth": False}]}
            zone_ref=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
            logging.info(zone_ref)
            if bool(re.match("\"zone_auth*.",str(zone_ref))):
                logging.info("xyz.com created succesfully")
                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                sleep(5)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(5)
            else:
                raise Exception("xyz.com creation unsuccessful")
        else:
            raise Exception("view1 creation unsuccessful")

    @pytest.mark.order(order=2)
    def test002_create_view2_and_add_zone(self):
        logging.info("Creating view2")
        data={"name": "view2"}
        view2_ref=ib_NIOS.wapi_request('POST',object_type='view',fields=json.dumps(data))
        logging.info(view2_ref)
        if bool(re.match("\"view*.",str(view2_ref))):
            logging.info("view2 created succesfully")
            logging.info("Creating zone xyz.com")
            data={"fqdn":"xyz.com","view":"view2","grid_primary":[{"name": config.grid_fqdn,"stealth": False}]}
            zone_ref=ib_NIOS.wapi_request('POST',object_type='zone_auth',fields=json.dumps(data))
            logging.info(zone_ref)
            if bool(re.match("\"zone_auth*.",str(zone_ref))):
                logging.info("xyz.com created succesfully")
                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                sleep(5)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(5)
            else:
                raise Exception("abc.com creation unsuccessful")

        else:
            raise Exception("view2 creation unsuccessful")

    @pytest.mark.order(order=3)
    def test003_dtc_server1(self):
        logging.info("Creating dtc server1")
        data={"host": config.grid_vip,"name": "server1"}
        server1_ref=ib_NIOS.wapi_request('POST',object_type='dtc:server',fields=json.dumps(data))
        logging.info(server1_ref)
        if bool(re.match("\"dtc:server*.",str(server1_ref))):
            logging.info("dtc server1 created succesfully")
            logging.info("Restart services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            sleep(5)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            sleep(5)

        else:
            raise Exception("dtc server1 creation unsuccessful")

    @pytest.mark.order(order=4)
    def test004_dtc_server2(self):
        logging.info("Creating dtc server2")
        data={"host": config.grid_member1_vip,"name": "server2"}
        server2_ref=ib_NIOS.wapi_request('POST',object_type='dtc:server',fields=json.dumps(data))
        logging.info(server2_ref)
        if bool(re.match("\"dtc:server*.",str(server2_ref))):
            logging.info("dtc server2 created succesfully")
            logging.info("Restart services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            sleep(5)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            sleep(5)

        else:
            raise Exception("dtc server2 creation unsuccessful")

    @pytest.mark.order(order=5)
    def test005_dtc_pool(self):
        logging.info("Creating dtc pool")
        server=ib_NIOS.wapi_request('GET',object_type='dtc:server')
        server1=json.loads(server)[0]['_ref']
        server2=json.loads(server)[1]['_ref']
        data={"name": "pool","lb_preferred_method": "ROUND_ROBIN","servers": [{"ratio": 1,"server": server1},{"ratio": 1,"server": server2}]}
        pool_ref=ib_NIOS.wapi_request('POST',object_type='dtc:pool',fields=json.dumps(data))
        logging.info(pool_ref)
        if bool(re.match("\"dtc:pool*.",str(pool_ref))):
            logging.info("pool created succesfully")
            logging.info("Restart services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            sleep(5)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            sleep(5)

        else:
            raise Exception("pool creation unsuccessful")

    @pytest.mark.order(order=6)
    def test006_dtc_lbdn(self):
        logging.info("Creating lbdn")
        pool=ib_NIOS.wapi_request('GET',object_type='dtc:pool')
        pool_ref=json.loads(pool)[0]['_ref']
        data={"name": "lbdn1","lb_method": "ROUND_ROBIN","pools": [{"pool": pool_ref,"ratio": 1}]}
        lbdn_ref=ib_NIOS.wapi_request('POST',object_type='dtc:lbdn',fields=json.dumps(data))
        logging.info(lbdn_ref)
        if bool(re.match("\"dtc:lbdn*.",str(lbdn_ref))):
            logging.info("lbdn created succesfully")
            logging.info("Restart services")
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            sleep(5)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            sleep(5)

        else:
            raise Exception("lbdn creation unsuccessful")

    '''@pytest.mark.order(order=7)
    def test007_csv_create(self):
        csv=open("csv_to_import_niosspt_9156.csv","w+")
        csv.write("header-dtclbdn,lb_method*,name*,_new_name,auth_zones,comment,disabled,patterns,persistence,pools,priority,topology,ttl,types\r\n")
        csv.write("dtclbdn,ROUND_ROBIN,lbdn,,,,FALSE,,0,pool1/1,1,,,A AAAA CNAME\r\n")
        csv.close()'''

    @pytest.mark.order(order=7)
    def test007_deletelbdn_and_exportcsv(self):
        logging.info("Deleting lbdn")
        lbdn=ib_NIOS.wapi_request('GET',object_type='dtc:lbdn')
        lbdn_ref=json.loads(lbdn)[0]['_ref']
        del_lbdn=ib_NIOS.wapi_request('DELETE',ref=lbdn_ref)
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(5)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(5)

        logging.info("Starting csv import")
        #dir_name="/import/qaddi/API_Automation/WAPI_PyTest/suites/customer_bug_automation/"
        dir_name = os.getcwd()
        base_filename = "niosspt_9156.csv"
        token =ib_TOKEN.generate_token_from_file(dir_name, base_filename)
        data = {"token": token,"action":"START", "doimport":True, "on_error":"CONTINUE","update_method":"OVERRIDE"}
        response = ib_NIOS.wapi_request('POST', object_type="fileop", fields=json.dumps(data),params="?_function=csv_import")
        response=json.loads(response)
        logging.info("logging response")
        logging.info(response)
        sleep(10)
        data={"action":"START","file_name":"niosspt_9156.csv","on_error":"CONTINUE","operation":"CREATE","separator":"COMMA"}
        get_ref=ib_NIOS.wapi_request('GET', object_type="csvimporttask")
        logging.info("get_ref")
        logging.info(get_ref)
        get_ref=json.loads(get_ref)
        for ref in get_ref:
            if response["csv_import_task"]["import_id"]==ref["import_id"]:
                if ref["lines_failed"]==0:
                    logging.info("CSV import successful")
                else:
                    raise Exception("CSV import unsuccessful")
        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(5)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(10)

    @pytest.mark.order(order=7)
    def test007_validate_zone(self):
        """
        Validate imported data
        """
        logging.info("Validating imported data")
        get_ref=ib_NIOS.wapi_request('GET',object_type='dtc:lbdn')
        logging.info(get_ref)
        for ref in json.loads(get_ref):
            assert ref["name"] == "lbdn"

    @pytest.mark.order(order=8)
    def test008_test_cleanup(self):
        logging.info("Deleting lbdn")
        lbdn=ib_NIOS.wapi_request('GET',object_type='dtc:lbdn')
        lbdn_ref=json.loads(lbdn)[0]['_ref']
        del_lbdn=ib_NIOS.wapi_request('DELETE',ref=lbdn_ref)

        pool=ib_NIOS.wapi_request('GET',object_type='dtc:pool')
        pool_ref=json.loads(pool)[0]['_ref']
        del_pool=ib_NIOS.wapi_request('DELETE',ref=pool_ref)

        server=ib_NIOS.wapi_request('GET',object_type='dtc:server')
        server1=json.loads(server)[0]['_ref']
        server2=json.loads(server)[1]['_ref']
        del_server2=ib_NIOS.wapi_request('DELETE',ref=server2)
        del_server1=ib_NIOS.wapi_request('DELETE',ref=server1)


        view=ib_NIOS.wapi_request('GET',object_type='view')
        view1=json.loads(view)[1]['_ref']
        view2=json.loads(view)[2]['_ref']
        del_view1=ib_NIOS.wapi_request('DELETE',ref=view1)
        del_view2=ib_NIOS.wapi_request('DELETE',ref=view2)

        logging.info("Restart services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        sleep(5)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        sleep(5)













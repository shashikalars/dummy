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


class Quering_using_indexer(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_001_setup_for_curl(self):

        # Creating a Admin Group
        group={"name":"superuser"}
        get_ref = ib_NIOS.wapi_request('POST',object_type="admingroup",fields=json.dumps(group),grid_vip=config.grid_member1_vip)
        if (get_ref[0] == 400):
            print("Duplicate object \'superuser\' of type \'admingroup\' already exists in the database")
        else:
            print("Group \'superuser\' has been created")

        # Making the admin group as Superuser
        logger.info("Creating a super User for using curl command")
        get_ref = ib_NIOS.wapi_request('GET',object_type="admingroup",grid_vip=config.grid_member1_vip)
        logger.info(get_ref)
        ref1 = json.loads(get_ref)[4]['_ref']
        print(ref1)

        data={"superuser":True}
        response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data),grid_vip=config.grid_member1_vip)
        print(response)

        # Adding login credentials to the admin group
        user={"name":"vindya","password":"vindyavk","admin_groups":["superuser"]}
        get_ref = ib_NIOS.wapi_request('POST',object_type="adminuser", fields=json.dumps(user))
        if (get_ref[0] == 400):
            print("Duplicate object \'vindya\' of type \'adminuser\' already exists in the database")
        else:
            print("User \'vindya\' has been created")

        # Enabling delete permission for user
        logger.info("Logging into grid master 'admin'")
        try:
            child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect("password:")
            child.sendline("infoblox")

            child.expect("Infoblox >")
            child.sendline('set reporting_user_capabilities enable vindya')

            child.expect(":")
            child.sendline("1")
            child.sendline('\r')

            child.expect("Infoblox >")
            child.sendline("exit")

            assert True

        except Exception as e:
            print(e)
            child.close()
            assert False

        finally:
            child.close()

    @pytest.mark.run(order=2)
    def test_002_curl_using_primary_site_indexer(self):
        # Fetching the indexer_ip from primary site (site 2)

        # cmd="python fetch_search_head_indexer.py indexer "+config.reporting_member1_ip+":"+config.reporting_member2_ip+":"+config.reporting_member3_ip+":"+config.reporting_member4_ip
        cmd="python fetch_search_head_indexer.py indexer3 "+config.reporting_member1_ip+":"+config.reporting_member2_ip+":"+config.reporting_member3_ip+":"+config.reporting_member4_ip
        indexer=subprocess.check_output(cmd,shell=True)
        indexer=indexer.strip("\n")
        print("indexer is "+indexer)

        # Using curl command to validate
        # DHCPv4 top utilised Networks
        # indexer="10.35.110.1"
        try:
            cmd='curl -k -u vindya:vindyavk https://'+indexer+':9185/services/search/jobs/ -d search="search sourcetype=ib:dhcp:network index=ib_dhcp"'
            print(cmd)
            # sleep(200)
            returned_output=subprocess.check_output(cmd,shell=True)
            print(returned_output)
            assert False

        except Exception as e:
            print("Connection Timeout")
            print(e)
            assert True

    @pytest.mark.run(order=3)
    def test_003_curl_using_secondary_site_indexer(self):
        # Fetching the indexer_ip from secondary site (site 1)

        # cmd="python fetch_search_head_indexer.py indexer "+config.reporting_member1_ip+":"+config.reporting_member2_ip+":"+config.reporting_member3_ip+":"+config.reporting_member4_ip
        cmd="python fetch_search_head_indexer.py indexer1 "+config.reporting_member1_ip+":"+config.reporting_member2_ip+":"+config.reporting_member3_ip+":"+config.reporting_member4_ip
        indexer=subprocess.check_output(cmd,shell=True)
        indexer=indexer.strip("\n")
        print("indexer is "+indexer)

        # Using curl command to validate
        # DHCPv4 top utilised Networks
        # indexer="10.35.110.1"
        try:
            cmd='curl -k -u vindya:vindyavk https://'+indexer+':9185/services/search/jobs/ -d search="search sourcetype=ib:dhcp:network index=ib_dhcp"'
            print(cmd)
            # sleep(200)
            returned_output=subprocess.check_output(cmd,shell=True)
            print(returned_output)
            assert False

        except Exception as e:
            print("Connection Timeout")
            print(e)
            assert True



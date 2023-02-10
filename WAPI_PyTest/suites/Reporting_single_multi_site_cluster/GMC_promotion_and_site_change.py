import os
import re
import config
import pytest
import unittest
import logging
import json
import sys
import pexpect
import subprocess
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS


class Reporting_Multisite_Cluster(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_001_convert_member_to_Master_candidate(self):
        print("Make the member as Master candidate")

        get_ref = ib_NIOS.wapi_request('GET', object_type='member?host_name='+config.grid_member1_fqdn)
        get_ref = json.loads(get_ref)[0]['_ref']

        data = {"master_candidate":True}
        response = ib_NIOS.wapi_request('PUT', ref=get_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
        print(response)

        if response[0] == 400 or response[0] == 401:
            print("Failure: Make the member as Master candidate")
            assert False
        else:
            print("Success: Make the member as Master candidate")
            assert True
        sleep(300)


    @pytest.mark.run(order=2)
    def test_002_Promote_GMC(self):
        print("Promoting Grid Master Candidate...")

        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect("password:")
            child.sendline("infoblox")
            child.expect("Infoblox >")

            child.sendline("set promote_master")
            child.expect("Do you want a delay between notification to grid members*")
            child.sendline("n")
            child.expect(":")
            child.sendline("c")
            child.expect("Are you sure you want to do this*")
            child.sendline("n")
            print("Grid Master Candidate NOT promoted!")
            assert True

        except Exception as e:
            print(e)
            child.close()
            print("FAILURE: Something went wrong...")
            assert False

        finally:
            child.close()


    @pytest.mark.run(order=3)
    def test_003_Promote_GMC(self):
        print("Promoting Grid Master Candidate...")

        try:
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_member1_vip)
            child.logfile=sys.stdout
            child.expect("password:")
            child.sendline("infoblox")
            child.expect("Infoblox >")

            child.sendline("set promote_master")
            child.expect("Do you want a delay between notification to grid members*")
            child.sendline("n")
            # prom = child.expect("Infoblox > ")
            # val = child.before
            # print(val)
            child.expect(":")
            child.sendline("2")
            child.expect("Are you sure you want to do this*")
            child.sendline("y")
            child.expect("Are you really sure you want to do this*")
            child.sendline("y")
            print("System restart...")
            sleep(900)
            print("Grid Master Candidate promoted!")
            assert True

        except Exception as e:
            print(e)
            child.close()
            print("FAILURE: Something went wrong...")
            assert False

        finally:
            child.close()


    @pytest.mark.run(order=4)
    def test_004_changing_search_had_in_splunkrc(self):
        print("changing the search head ip in splunkrc file...")

        cmd="grep 'host=10.' ~/.splunkrc"
        host=subprocess.check_output(cmd,shell=True)
        print host
        search_head_ip=host.strip("host=\n")
        print("search_head_ip is "+ search_head_ip)

        cmd="python fetch_search_head_indexer.py search_head "+config.reporting_member1_ip+":"+config.reporting_member2_ip+":"+config.reporting_member3_ip+":"+config.reporting_member4_ip
        new_search_head_ip=subprocess.check_output(cmd,shell=True)
        new_search_head_ip=new_search_head_ip.strip("\n")
        print("new search head is "+new_search_head_ip)

        os.system("sed -i 's/host="+search_head_ip+"/host="+new_search_head_ip+"/g'  ~/.splunkrc")


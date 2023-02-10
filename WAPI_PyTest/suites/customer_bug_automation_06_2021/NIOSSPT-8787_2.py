_author__ = "Siva Krishna"
__email__  = "krishnas@infoblox.com"

####################
#After Upgrade     #   
####################
           
import re
import config
import pytest
import unittest
import logging
import os
import os.path
from os.path import join
import subprocess
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util

@pytest.mark.run(order=1)
def test_001_show_upgrade_history_data():
    logging.info(" show upgrade_history")
    for i in range(10):
        hostname = config.grid_vip
        response = os.system("ping -c 1 " + hostname)
        if response == 0:
            pingstatus = "Network Active"
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
            child.logfile=sys.stdout
            child.expect('password:')
            child.sendline('infoblox')
            child.expect('Infoblox >')
            child.sendline('show version')
            child.expect('Infoblox >')
            child.sendline('show upgrade_history')
            child.expect('Infoblox >')
            upgrade=child.before
            print(upgrade)
            upgrade=upgrade.replace('\n',' ').replace('\r',' ')
            upgrade=re.findall(r'Upgraded to: \d\.\d\.\d-\d{6}',upgrade)
            print(upgrade)
            if (upgrade !=[]):
                    assert True
            else:
                    assert False
            break
        else:
            sleep(300)

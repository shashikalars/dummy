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
from logger import logger




class  midnight_reports_trigger(unittest.TestCase):
    @classmethod
    def setup_class(cls):


        cmd = os.system("scp -pr savedsearches.conf root@"+config.indexer_ip+":/opt/splunk/etc/apps/infoblox/local/")
        print(cmd)

        sleep(10)

        logger.info("Logging into reporting member as 'root'")
        child = pexpect.spawn("ssh root@"+config.indexer_ip,  maxread=4000)
        try:
            child.expect('-bash-5.0#',timeout=100)
            child.sendline("cd /opt/splunk/bin/")

            child.expect('-bash-5.0#',timeout=100)
            child.sendline("./splunk restart")


            child.expect('-bash-5.0#',timeout=100)
            child.sendline("exit")

            # Wait for some time for restart
            sleep(300)

        except Exception as e:
            print(e)
            child.close()
            assert False


        finally:
            child.close()


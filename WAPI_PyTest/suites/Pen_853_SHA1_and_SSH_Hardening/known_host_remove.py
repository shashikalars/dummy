import re
import pprint
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
import commands
import json, ast
import requests
import time
import pexpect
import sys

class Knownhost(unittest.TestCase):

    @pytest.mark.run(order=01)
    def test_01_Delet_the_known_hosts_from_client(self):
        print("delete the known hosts from client")
	whoami = os.popen("whoami").read()
	whoami = whoami.replace('\n','')
	print(" I am "+whoami+" user")
	#dl_knownhost = 'rm /home/'+whoami+'/.ssh/known_hosts'
	dl_knownhost = 'rm /home/'+whoami+'/.ssh/a.txt'
        dl_knownhost = os.system(dl_knownhost)
	print("deleted the known hosts")
        print("Test Case 01 Execution Completed")


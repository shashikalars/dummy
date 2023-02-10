"""
 Copyright (c) Infoblox Inc., 2016

 ReportName          : DNS Scavenge Object Count Trend
 ReportCategory      : DNS Scavenge
 Number of Test cases: 1
 Execution time      : 556.90 seconds
 Execution Group     : Minute Group (MG)
 Description         : 'DNS Scavenge Object Count Trend' report will updated every one min. 

 Authora  : Raghavendra MN
 History  : 06/07/2016 (Created)
 Reviewer : Raghavendra MN
"""
import config
import json
import os
import pytest
import pexpect
import re
import sys
import subprocess
import time
import unittest
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.ib_get as ib_get
import ib_utils.ib_papi as papi
from logger import logger
from ib_utils.ib_system import search_dump as search_dump
from ib_utils.ib_validaiton import compare_results as compare_results

"""
TEST Steps:
      1.  Input/Preparaiton      : Adding zones, RR's in different view through CSV and next performing 'DNS Scavenge' operaiton. 
      2.  Search                 : Performing Search operaion with default/custom filter
      3.  Validation             : validating Search Results against scavenge data.
"""

#class DNSScavengeObjectCountTrend(unittest.TestCase):
#    @classmethod
#    def setup_class(cls):

fin=os.popen("ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null 2>/dev/null root\@"+config.grid_vip+" date +%s")
epoc = fin.readline().rstrip()
print epoc
rc=subprocess.call(['perl','ib_data/Reporting_Properties/reporting_backup.pl',config.grid_vip,epoc,config.client_ip,config.client_user,config.client_passwd,config.backup_path])
print "---sleep 60 seconds--"

print "---Restore Starts--"
rc=subprocess.call(['perl','ib_data/Reporting_Properties/reporting_restore.pl',config.grid_vip,config.client_ip,config.client_user,config.client_passwd,config.backup_path])
print "---sleep 60 seconds--"


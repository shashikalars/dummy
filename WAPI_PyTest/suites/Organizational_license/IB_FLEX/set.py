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
import re
#import ib_utils.ib_get as ib_get
from time import sleep
import sys
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="license.log" ,level=logging.DEBUG,filemode='w')

member_vip=config.grid_member1_vip
print member_vip
#proc=pexpect.spawn("ssh admin@"+member_vip+"")
#print member_vip
'''
try:
    index=proc.expect(["admin.*password:","Are you sure you want to continue connecting.*"],timeout=30)
    if index == 1:
       proc.sendline("yes")
       time.sleep(5)
    proc.sendline("infoblox")
    index1=proc.expect(["Do you want to start wizard? y/n [y]:.*",">"])
    if index1 == 0:
       proc.sendline("n")
'''
    #proc.sendline("set hardware-type IB-FLEX")
    #sleep(60)
    #proc.sendline("exit")

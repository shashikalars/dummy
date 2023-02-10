#!/usr/bin/env python
__author__ = "Chetan Kumar PG"
__email__  = "cpg@infoblox.com"

import os
import re
import config
import pytest
import unittest
import logging
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_xxxx.log" ,level=logging.DEBUG,filemode='w')

# Global variables
a = None
b = None

def display_msg(x=""):
    """ 
    Additional function.
    """
    logging.info(x)
    print(x)

class NIOSSPT_XXXX(unittest.TestCase):
    
    @pytest.mark.run(order=1)
    def test_000_setup(self):
        """
        setup method: Used for configuring pre-required configs.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|           Test Case setup Started            |")
        display_msg("------------------------------------------------")
        # Your setup code here
        pass
    
    @pytest.mark.run(order=2)
    def test_001_template(self):
        """
        Step wise description of the testcase here.
        Use niosspt_XXXX as the name for all the objects created in this script.
        """
        display_msg()
        display_msg("----------------------------------------------------")
        display_msg("|          Test Case 1 Execution Started           |")
        display_msg("----------------------------------------------------")
        # Your testcase code here
        display_msg("-----------Test Case 1 Execution Completed------------")

    @pytest.mark.run(order=-1)
    def test_cleanup(self):
        """
        cleanup method: Delete all the objects created and changes made from this script.
        """
        display_msg()
        display_msg("------------------------------------------------")
        display_msg("|          Test Case cleanup Started           |")
        display_msg("------------------------------------------------")
        display_msg("Reverting back the Grid to its original state")
        
        display_msg("-----------Test Case cleanup Completed------------")
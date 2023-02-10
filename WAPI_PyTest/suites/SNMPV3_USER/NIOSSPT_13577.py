#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
# Grid Set up required:                                                     #
#  1. Grid + Member                                                         #
#  2. Licenses : Grid,NIOS                                                  #
#############################################################################
import os
import re
import config
import pytest
import unittest
import logging
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import shlex
from time import sleep
from subprocess import Popen, PIPE
import pexpect
import paramiko
from  ib_utils.log_capture import log_action as log
from  ib_utils.log_validation import log_validation as logv


class NIOSSPT_13577(unittest.TestCase):
    @pytest.mark.run(order=1)
    def test_000_Add_sysContact_SNMP_System_Information_Grid_level(self):
        print("\nAdding sysContact")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        getref=json.loads(get_ref)[0]['_ref']
        print(getref)
        try:
            data={"snmp_setting":{"syscontact": ["�~C�~M~A�~C�~J~@�~L�~B��~C��~B��~E��~T�移�~L�~V~K�~Y�DNS"]}}
            response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
            print(response)
            
        except Exception as e:
            print(e)
            print("\nInternal Error: Open bug: NIOSSPT-13577")
            assert False
        else:
            assert True
            
    @pytest.mark.run(order=2)
    def test_001_Add_sysdescr_SNMP_System_Information_Grid_level(self):
        print("Adding sysdescr")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        getref=json.loads(get_ref)[0]['_ref']
        print(getref)
        try:
            data={"snmp_setting":{"sysdescr": ["�~C�~M~A�~C�~J~@�~L�~B��~C��~B��~E��~T�移�~L�~V~K�~Y�DNS"]}}
            response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
            print(response)
            
        except Exception as e:
            print(e)
            print("\nInternal Error: Open bug: NIOSSPT-13577")
            assert False
        else:
            assert True
                
    @pytest.mark.run(order=3)
    def test_002_Add_syslocation_SNMP_System_Information_Grid_level(self):
        print("Adding syslocation")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        getref=json.loads(get_ref)[0]['_ref']
        print(getref)
        try:
            data={"snmp_setting":{"syslocation": ["�~C�~M~A�~C�~J~@�~L�~B��~C��~B��~E��~T�移�~L�~V~K�~Y�DNS"]}}
            response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
            print(response)

        except Exception as e:
            print(e)
            print("\nInternal Error: Open bug: NIOSSPT-13577")
            assert False
        else:
            assert True
                
    @pytest.mark.run(order=4)
    def test_003_Add_sysname_SNMP_System_Information_Grid_level(self):
        print("Adding sysname")
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        getref=json.loads(get_ref)[0]['_ref']
        print(getref)
        try:
            data={"snmp_setting":{"sysname": ["�~C�~M~A�~C�~J~@�~L�~B��~C��~B��~E��~T�移�~L�~V~K�~Y�DNS"]}}
            response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
            print(response)

        except Exception as e:
            print(e)
            print("\nInternal Error: Open bug: NIOSSPT-13577")
            assert False
        else:
            assert True
    @pytest.mark.run(order=5)
    def test_004_Add_sysContact_SNMP_System_Information_Master_level(self):
        print("Adding sysContact on Master level\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member')
        getref=json.loads(get_ref)[0]['_ref']
        print(getref)
        try:
            data={"snmp_setting":{"syscontact": ["�~C�~M~A�~C�~J~@�~L�~B��~C��~B��~E��~T�移�~L�~V~K�~Y�DNS"]}}
            response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
            print(response)
            
        except Exception as e:
            print(e)
            print("\nInternal Error: Open bug: NIOSSPT-13577")
            assert False
        else:
            assert True
                
    @pytest.mark.run(order=6)
    def test_005_Add_sysdescr_SNMP_System_Information_Master_level(self):
        print("Adding sysdescr on Master level\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member')
        getref=json.loads(get_ref)[0]['_ref']
        print(getref)
        try:
            data={"snmp_setting":{"sysdescr": ["�~C�~M~A�~C�~J~@�~L�~B��~C��~B��~E��~T�移�~L�~V~K�~Y�DNS"]}}
            response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
            print(response)
            
        except Exception as e:
            print(e)
            print("\nInternal Error: Open bug: NIOSSPT-13577")
            assert False
        else:
            assert True
                
    @pytest.mark.run(order=7)
    def test_006_Add_syslocation_SNMP_System_Information_Master_level(self):
        print("Adding syslocation on Master level")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member')
        getref=json.loads(get_ref)[0]['_ref']
        print(getref)
        try:
            data={"snmp_setting":{"syslocation": ["�~C�~M~A�~C�~J~@�~L�~B��~C��~B��~E��~T�移�~L�~V~K�~Y�DNS"]}}
            response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
            print(response)
            
        except Exception as e:
            print(e)
            print("\nInternal Error: Open bug: NIOSSPT-13577")
            assert False
        else:
            assert True
                
    @pytest.mark.run(order=8)
    def test_007_Add_sysname_SNMP_System_Information_Master_level(self):
        print("Adding sysname on Master level")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member')
        getref=json.loads(get_ref)[0]['_ref']
        print(getref)
        try:
            data={"snmp_setting":{"sysname": ["�~C�~M~A�~C�~J~@�~L�~B��~C��~B��~E��~T�移�~L�~V~K�~Y�DNS"]}}
            response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
            print(response)
            
        except Exception as e:
            print(e)
            print("\nInternal Error: Open bug: NIOSSPT-13577")
            assert False
        else:
            assert True
   
    @pytest.mark.run(order=9)
    def test_008_Add_sysContact_SNMP_System_Information_Member_level(self):
        print("Adding sysContact on Member level\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member')
        getref=json.loads(get_ref)[1]['_ref']
        print(getref)
        try:
            data={"snmp_setting":{"syscontact": ["�~C�~M~A�~C�~J~@�~L�~B��~C��~B��~E��~T�移�~L�~V~K�~Y�DNS"]}}
            response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
            print(response)
            
        except Exception as e:
            print(e)
            print("\nInternal Error: Open bug: NIOSSPT-13577")
            assert False
        else:
            assert True
                
                
    @pytest.mark.run(order=10)
    def test_009_Add_sysdescr_SNMP_System_Information_Member_level(self):
        print("Adding sysdescr on Member level\n")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member')
        getref=json.loads(get_ref)[1]['_ref']
        print(getref)
        try:
            data={"snmp_setting":{"sysdescr": ["�~C�~M~A�~C�~J~@�~L�~B��~C��~B��~E��~T�移�~L�~V~K�~Y�DNS"]}}
            response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
            print(response)
            
        except Exception as e:
            print(e)
            print("\nInternal Error: Open bug: NIOSSPT-13577")
            assert False
        else:
            assert True
                
    @pytest.mark.run(order=11)
    def test_010_Add_syslocation_SNMP_System_Information_Member_level(self):
        print("Adding syslocation on Member level")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member')
        getref=json.loads(get_ref)[1]['_ref']
        print(getref)
        try:
            data={"snmp_setting":{"syslocation": ["�~C�~M~A�~C�~J~@�~L�~B��~C��~B��~E��~T�移�~L�~V~K�~Y�DNS"]}}
            response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
            print(response)
            
        except Exception as e:
            print(e)
            print("\nInternal Error: Open bug: NIOSSPT-13577")
            assert False
        else:
            assert True
                
    @pytest.mark.run(order=12)
    def test_011_Add_sysname_SNMP_System_Information_Member_level(self):
        print("Adding sysname on Member level")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member')
        getref=json.loads(get_ref)[1]['_ref']
        print(getref)
        try:
            data={"snmp_setting":{"sysname": ["�~C�~M~A�~C�~J~@�~L�~B��~C��~B��~E��~T�移�~L�~V~K�~Y�DNS"]}}
            response = ib_NIOS.wapi_request('PUT',ref=getref,fields=json.dumps(data))
            print(response)
            
        except Exception as e:
            print(e)
            print("\nInternal Error: Open bug: NIOSSPT-13577")
            assert False
        else:
            assert True
      
    @pytest.mark.run(order=13)
    def test_012_cleanup(self):
        print("Cleanup all created object")
        get_reff = ib_NIOS.wapi_request('GET', object_type="member")
        for ref in json.loads(get_reff):
            print(ref['_ref'])
            data={"snmp_setting":{"syscontact": [],"sysdescr": [],"syslocation": [],"sysname": []}}
            response=ib_NIOS.wapi_request('PUT',ref=ref['_ref'], fields=json.dumps(data))
            print(response)
            if type(response) == tuple:

                if response[0]==200:
                   
                    assert True
                else:
                    assert False 
                    
        get_ref = ib_NIOS.wapi_request('GET', object_type='grid?_return_fields=snmp_setting')
        get_grid_ref=json.loads(get_ref)[0]['_ref']
        
        data={"snmp_setting":{"syscontact": [],"sysdescr": [],"syslocation": [],"sysname": []}}
        response=ib_NIOS.wapi_request('PUT',ref=get_grid_ref, fields=json.dumps(data))
        print(response)
        if type(response) == tuple:
            if response[0]==200:     
                    assert True
            else:
                assert False
        print("Restart Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(30)


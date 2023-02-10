import re
import config
#import config1
import pytest
import unittest
import logging
import subprocess
import os
import json
from time import sleep
import commands
import json, ast
import requests
import time
import pexpect
import getpass
import sys
import ib_utils.ib_NIOS as ib_NIOS
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="rfe_8203.log" ,level=logging.INFO,filemode='w')


def get_reference_value_grid(self):
          logging.info("To Get reference of grid")
          get_ref = ib_NIOS.wapi_request('GET', object_type="grid")
          logging.info(get_ref)
          res = json.loads(get_ref)
          ref1 = json.loads(get_ref)[0]['_ref']
          return ref1

    
def get_lockout_setting(self):
          ref2 =get_reference_value_grid(self)
          logging.info("Retrieve lockout settings for GRID")
          logging.info ("--------------------------------------------------------", ref2)
          get_ref = ib_NIOS.wapi_request('GET', object_type=ref2 + "?_return_fields=lockout_setting")
          logging.info("\n")
          logging.info(get_ref)
          rec2 = json.loads(get_ref)
          return rec2

def get_lockout_setting_group(self):
          ref2 =get_reference_value_admin_group(self)
          logging.info("Retrieve lockout settings for Group")
          logging.info ("--------------------------------------------------------", ref2)
          get_ref = ib_NIOS.wapi_request('GET', object_type=ref2 + "?_return_fields=lockout_setting")
          logging.info("\n")
          logging.info(get_ref)
          rec2 = json.loads(get_ref)
          return rec2

#Retreving the reference of the given admingroup
def get_reference_value_admin_group(self):
          logging.info("get reference value for GROUP level")
          get_ref = ib_NIOS.wapi_request('GET', object_type="admingroup")
          logging.info(get_ref)
          res = json.loads(get_ref)
          return res
          

#Retreving the reference of the given adminuser
def get_reference_value_admin_user(self):
          logging.info("get reference value for user level")
          get_ref = ib_NIOS.wapi_request('GET', object_type="adminuser")
          logging.info(get_ref)
          res = json.loads(get_ref)
          return res

class Network(unittest.TestCase):
      #logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)
      @pytest.mark.run(order=1)
      def test_a_get_default_setting(self):
          z=[]
          y=[]
          logging.info ("+++++++++++++++++++++ Testcase 1 is executing ++++++++++++++++++++++++++++++++++")
          logging.info ("Checking the values")
          data = {"lockout_setting":{"enable_sequential_failed_login_attempts_lockout":False,"sequential_attempts":5,"failed_lockout_duration":5,"never_unlock_user":False}}
          for i,j in data["lockout_setting"].items():
              z.append(j)
          settings =get_lockout_setting(self)
          logging.info(settings)
          for i,j in settings["lockout_setting"].items():
              y.append(j)
          if  (z==y):
              logging.info ("Test case 1 Passed")
              assert True
          else:
              logging.info ("Test case 1 Failed")
              assert False

      #Checking after disabling the lockout whether fields is editable in grid level
      @pytest.mark.run(order=2)
      def test_b_get_lockout_Disable(self):
          res =get_lockout_setting(self)
          z=[]
          y=[]
          logging.info ("+++++++++++++++++++++Testcase 2 is executing++++++++++++++++++++++++++++++++++")
          logging.info ("Checking the values")
          data1= {"lockout_setting":{"enable_sequential_failed_login_attempts_lockout":False,"sequential_attempts":10,"failed_lockout_duration":20,"never_unlock_user":True}}
          response = ib_NIOS.wapi_request('PUT', ref=res['_ref'],fields=json.dumps(data1), grid_vip=config.grid_vip)
          logging.info (response)
          logging.info(response)
          for i,j in data1["lockout_setting"].items():
              z.append(j)
          settings =get_lockout_setting(self)
          logging.info(settings)
          for i,j in settings["lockout_setting"].items():
              y.append(j)
          if (z==y):
              logging.info ("Test case 2 Passed")
              assert True
          else:
              logging.info ("Test case 2 Failed")
              assert False

      #Check also the edit and get the values for the range 0 for both in grid level.
      @pytest.mark.run(order=3)
      def test_c_null_value(self):
          res =get_lockout_setting(self)
          z = []
          y = []
          logging.info ("+++++++++++++++++++++Testcase 3 is executing++++++++++++++++++++++++++++++++++")
          logging.info ("Editing the values")
          data1 =get_lockout_setting(self)
          data = {"lockout_setting": {'enable_sequential_failed_login_attempts_lockout':True,"sequential_attempts":0,"failed_lockout_duration":0,"never_unlock_user":False}}
          try:
              response = ib_NIOS.wapi_request('PUT',ref=res['_ref'],fields=json.dumps(data), grid_vip=config.grid_vip)
              logging.info(response)
          except Exception as error:
              logging.info ("abcd {}".format(error))
          for i,j in data1["lockout_setting"].items():
              z.append(j)
          settings =get_lockout_setting(self)
          logging.info (settings)
          logging.info(settings)
          for i, j in settings["lockout_setting"].items():
              y.append(j)
          if (z==y):
              logging.info ("Test case 3 Passed")
              assert True
          else:
              logging.info ("Test case 3 Failed")
              assert False


      # Check also the range bw 1-99 and 1-1440 and edit and get the values.(checking for max value for both)

      @pytest.mark.run(order=4)
      def test_d_checking_short_range(self):
          res =get_lockout_setting(self)
          z = []
          y = []
          logging.info ("+++++++++++++++++++++Testcase 4 is executing++++++++++++++++++++++++++++++++++")
          logging.info ("Editing the values")
          data1 =get_lockout_setting(self)
          data = {"security_setting":{"sequential_attempts":100,"failed_lockout_duration":1441,'enable_sequential_failed_login_attempts_lockout':True}}
          try:
              response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data), grid_vip=config.grid_vip)
              logging.info(response)
          except Exception as error:
              logging.info ("abcd {}".format(error))

          settings =get_lockout_setting(self)
          logging.info(settings)
          for i,j in data1["lockout_setting"].items():
              z.append(j)
          settings =get_lockout_setting(self)
          logging.info(settings)
          for i, j in settings["lockout_setting"].items():
              y.append(j)
          if  (z==y):
              logging.info ("Test case 4 Passed")
              assert True
          else:
               logging.info ("Test case 4 Failed")
               assert False

      #Retriving values after changing the values and checking the default values are same as input after lockout_setting is false
      @pytest.mark.run(order=5)
      def test_e_checking_long_range(self):
          res =get_lockout_setting(self)
          z = []
          y = []
          logging.info ("+++++++++++++++++++++Testcase 5 is executing++++++++++++++++++++++++++++++++++")
          logging.info ("Editing the values")
          data2 = {"lockout_setting":{"enable_sequential_failed_login_attempts_lockout": False,"sequential_attempts": 20,"failed_lockout_duration": 20, "never_unlock_user": False}}
          response2 = ib_NIOS.wapi_request('PUT', ref=res['_ref'], fields=json.dumps(data2), grid_vip=config.grid_vip)
          logging.info(response2)
          logging.info("==========================i==")
          settings =get_lockout_setting(self)
          logging.info(settings)
          for i,j in data2["lockout_setting"].items():
              z.append(j)
          for i,j in settings["lockout_setting"].items():
              y.append(j)
          if  (z==y):
               logging.info ("Test case 5 Passed")
               assert True
          else:
               logging.info ("Test case 5 Failed")
               assert False 
      
      #creating user group
      @pytest.mark.run(order=6)
      def test_f_create_user_group(self):
          logging.info("Testcase 6 is executing")
          group={"name":"test1_RFE8203","superuser":True}
          try:
              get_ref_group = ib_NIOS.wapi_request('POST',object_type="admingroup", fields=json.dumps(group))
              res_group = json.loads(get_ref_group)
          except Exception as error:
              logging.info ("abcd {}".format(error))
          try:
              user={"name":"testusr1_RFE8203","password":"infoblox","admin_groups":["test1_RFE8203"]}
              get_ref = ib_NIOS.wapi_request('POST',object_type="adminuser", fields=json.dumps(user))
              logging.info (get_ref)
              logging.info("Creating User Group for testing locking features ")
          except Exception as error:
              logging.info ("abcd {}".format(error))
          try:
              group1={"name":"test2_RFE_8203","superuser":False}
              get_ref_group1 = ib_NIOS.wapi_request('POST',object_type="admingroup", fields=json.dumps(group1))
              logging.info(get_ref_group1)
              res_group1 = json.loads(get_ref_group1)
          except Exception as error:
              logging.info ("abcd {}".format(error)) 
          
          try:     
              user1={"name":"testusr2_RFE8203","password":"infoblox","admin_groups":["test2_RFE_8203"]}
              get_ref1 = ib_NIOS.wapi_request('POST',object_type="adminuser", fields=json.dumps(user1))
              logging.info(get_ref1)
              res1 = json.loads(get_ref1)
              logging.info (res1) 
          except Exception as error:
              logging.info ("abcd {}".format(error))
       
      
      @pytest.mark.run(order=7)      
      #Edit Some values check the status of the user by giving sleep same as duration
      def test_g_get_status_user(self):
          res =get_lockout_setting(self)
          z = []
          y = []
          logging.info ("+++++++++++++++++++++Testcase 7 is executing++++++++++++++++++++++++++++++++++")
          status ="LOCKED"
          logging.info ("Checking the values")
          data = {"lockout_setting": {"enable_sequential_failed_login_attempts_lockout": True, "sequential_attempts": 2,"failed_lockout_duration": 1, "never_unlock_user": False}}
          response = ib_NIOS.wapi_request('PUT', ref=res['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
          duration =60*(data["lockout_setting"]["failed_lockout_duration"])
          logging.info (duration)
          wrong_attempts = (data["lockout_setting"]["sequential_attempts"])
          while (wrong_attempts > 0):
                try:
                    response = ib_NIOS.wapi_request('PUT',user="testusr1_RFE8203",password="infdfs",ref=res['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
                except Exception as error:
                    logging.info ("abcd {}".format(error))
                    wrong_attempts = wrong_attempts-1
                    time.sleep(2)
                logging.info(response)
          list1=get_reference_value_admin_user(self)
          for i in list1:
              if (i['name']=='testusr1_RFE8203'):
                  reference=i['_ref']
          rec2 = ib_NIOS.wapi_request('GET',object_type=reference + "?_return_fields=status")
          ref1 =json.loads(rec2)
          return_status =ref1['status']
          if (status==return_status):
              time.sleep(duration)
              rec2 = ib_NIOS.wapi_request('GET',object_type=reference + "?_return_fields=status")
              ref2 =json.loads(rec2)
              status1 =ref2['status']
              time.sleep(5)
              if (status1=='ACTIVE'):
                  logging.info("Test case 7 Passed")
                  assert True
              else:
                  logging.info("Test case 7 Failed")
        
          else:
               logging.info("Test case 7 Failed")
               assert False

      @pytest.mark.run(order=8)
      #This Checks for super user "never unlock" which must not work
      def test_h_get_status_user(self):
          res =get_lockout_setting(self)
          z = []
          y = []
          logging.info ("++++++++++++++++++++++++Testcase 8 is executing++++++++++++++++++++++++++++++++++")
          status ="LOCKED"
          logging.info ("Checking the values")
          data = {"lockout_setting": {"enable_sequential_failed_login_attempts_lockout": True, "sequential_attempts": 2,"failed_lockout_duration": 1, "never_unlock_user": True}}
          response = ib_NIOS.wapi_request('PUT', ref=res['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
          duration =60*(data["lockout_setting"]["failed_lockout_duration"]+1)
          logging.info (duration)
          wrong_attempts = (data["lockout_setting"]["sequential_attempts"])
          while (wrong_attempts > 0):
                try:
                    response = ib_NIOS.wapi_request('PUT',user="testusr1_RFE8203",password="infdfs",ref=res['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
                except Exception as error:
                    logging.info ("abcd {}".format(error))
                    wrong_attempts = wrong_attempts-1
                    time.sleep(2)
          list1=get_reference_value_admin_user(self)
          for i in list1:
              if (i['name']=='testusr1_RFE8203'):
                  reference=i['_ref']
                  rec2 = ib_NIOS.wapi_request('GET',object_type=reference + "?_return_fields=status")
                  ref1 =json.loads(rec2)
                  return_status =ref1['status']
                  if (status==return_status):
                      time.sleep(duration)
                      rec2 = ib_NIOS.wapi_request('GET',object_type=reference + "?_return_fields=status")
                      ref2 =json.loads(rec2)
                      status1 =ref2['status']
                      time.sleep(5)
                      if (status1=='ACTIVE'):
                          logging.info("Test case 8 Passed")
                          assert True
                      else:
                          logging.info("Test case 8 Failed")
                          assert False      

      @pytest.mark.run(order=9)
      #check attempts>5 and forbidden state
      def test_i_checking_forbidden(self):
          res =get_lockout_setting(self)
          z = []
          y = []
          logging.info ("+++++++++++++++++++++Testcase 9 is executing++++++++++++++++++++++++++++++++++")
          status ="LOCKED"
          logging.info ("Checking the values")
          data = {"lockout_setting": {"enable_sequential_failed_login_attempts_lockout": True, "sequential_attempts": 11,"failed_lockout_duration": 3, "never_unlock_user": False}}
          response = ib_NIOS.wapi_request('PUT', ref=res['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
          duration =60*(data["lockout_setting"]["failed_lockout_duration"]+2)
          logging.info (duration)
          wrong_attempts = (data["lockout_setting"]["sequential_attempts"])
          count=0
          while (wrong_attempts > 0):
                try:
                    response = ib_NIOS.wapi_request('PUT',user="testusr1_RFE8203",password="infdfs",ref=res['_ref'], fields=json.dumps(data),grid_vip=config.grid_vip)
                except Exception as error:
                    logging.info ("abcd {}".format(error))
                    count+=1
                    
                    if (count==5):
                        sleep(120) #Forbidden state sleep standard 2 mins
                        count=0
                    wrong_attempts = wrong_attempts-1
                    logging.info(response)
          list1=get_reference_value_admin_user(self)
          for i in list1:
              if (i['name']=='testusr1_RFE8203'):
                  reference=i['_ref']
                  rec2 = ib_NIOS.wapi_request('GET',object_type=reference + "?_return_fields=status")
                  ref1 =json.loads(rec2)
                  return_status =ref1['status']
                  if (status==return_status):
                      time.sleep(duration)
                      rec2 = ib_NIOS.wapi_request('GET',object_type=reference + "?_return_fields=status")
                      ref2 =json.loads(rec2)
                      status1 =ref2['status']
                      time.sleep(5)
                      if (status1=='ACTIVE'):
                          logging.info("Test case 9 Passed")
                          assert True
                      else:
                          logging.info("Test case 9 Failed")
                  else:
                      logging.info("Test case 9 Failed")
                      assert False


      #Checking non-super user gets never unlock
      @pytest.mark.run(order=10)
      def test_j_get_status_user(self):
          res = get_lockout_setting(self)
          z = []
          y = []
          logging.info ("+++++++++++++++++++++Testcase 10 is executing++++++++++++++++++++++++++++++++++")
          status = "LOCKED"
          logging.info ("Checking the values")
          data = {"lockout_setting": {"enable_sequential_failed_login_attempts_lockout": True, "sequential_attempts": 2,"failed_lockout_duration": 1, "never_unlock_user": True}}
          response = ib_NIOS.wapi_request('PUT', ref=res['_ref'], fields=json.dumps(data), grid_vip=config.grid_vip)
          duration = 60 * (data["lockout_setting"]["failed_lockout_duration"]+1)
          logging.info (duration)
          wrong_attempts = (data["lockout_setting"]["sequential_attempts"])
          while (wrong_attempts > 0):
                try:
                    response = ib_NIOS.wapi_request('PUT', user="testusr2_RFE8203", password="infdfs", ref=res['_ref'],fields=json.dumps(data), grid_vip=config.grid_vip)
                except Exception as error:
                    logging.info ("abcd {}".format(error))
                    wrong_attempts = wrong_attempts - 1
                    time.sleep(2)
                    logging.info(response)
    
          list1 = get_reference_value_admin_user(self)
          for i in list1:
              if (i['name'] == 'testusr2_RFE8203'):
                 reference = i['_ref']
                 rec2 = ib_NIOS.wapi_request('GET', object_type=reference + "?_return_fields=status")
                 ref1 = json.loads(rec2)
                 return_status = ref1['status']
                 if (status == return_status):
                    time.sleep(duration)
                    rec2 = ib_NIOS.wapi_request('GET', object_type=reference + "?_return_fields=status")
                    ref2 = json.loads(rec2)
                    status1 = ref2['status']
                    time.sleep(5)
                    if (status1 =='LOCKED'):
                        logging.info("Test case 10 Passed")
                        assert True
                    else:
                        assert False
                        logging.info("Test case 10 Failed")

###################Grid test is completed###############################################################################

      #checking for default values use_lockout=false
      @pytest.mark.run(order=11)
      def test_k_default_group_values(self):
          list1=get_reference_value_admin_user(self)
          for i in list1:
              if (i['name']=='test1_RFE8203'):
                  reference=i['_ref']
                  rec1 = ib_NIOS.wapi_request('GET',object_type=reference + "?_return_fields=use_lockout_setting")
                  ref1 =json.loads(rec1)
                  status1 =ref1['use_lockout_setting']        
                  if (status1=="false"):
                      logging.info("Testcase 11 is passed")
                      assert True
                  else:
                      logging.info("Testcase 11 is failed")
                      assert False
  
#when group is edited use lockout settings automaticallly becomes true though lockout_settings is false
      @pytest.mark.run(order=12)
      def test_l_check_use_lockout_settings(self):
          z=[]
          y=[]
          list1=get_reference_value_admin_group(self)
          logging.info(list1)
          for i in list1:
              if (i['name']=='test1_RFE8203'):
                  reference=i['_ref']
                  data = {"lockout_setting":{"enable_sequential_failed_login_attempts_lockout":True,"sequential_attempts":50,"failed_lockout_duration":50,"never_unlock_user":False}}
                  response = ib_NIOS.wapi_request('PUT', ref=reference,fields=json.dumps(data), grid_vip=config.grid_vip)
                  logging.info(response)
                  list1=get_reference_value_admin_group(self)
                  for i in list1:
                      if (i['name']=='test1_RFE8203'):
                          reference=i['_ref']
                          updated_data= ib_NIOS.wapi_request('GET',object_type=reference + "?_return_fields=lockout_setting")
                          ref1 =json.loads(updated_data)
                          use_ref=ib_NIOS.wapi_request('GET',object_type=reference + "?_return_fields=use_lockout_setting")
                          ref2 =json.loads(use_ref)
                          status1 =ref2['use_lockout_setting']
                          for i,j in ref1['lockout_setting'].items():
                              z.append(j)
                          for i,j in data['lockout_setting'].items():
                              y.append(j)
                          #import pdb; pdb.set_trace()
                          if (z==y and status1=="True"):
                              logging.info("Test case 12 is Passed")
                              assert True
                          else:
                              logging.info ("Test case 12 is Failed")
                              #assert False


#Enable and set the values for the group and must behave as configured.
      @pytest.mark.run(order=13)
      def test_m_check_lockout_configure(self):
          res =get_lockout_setting(self)
          list1=get_reference_value_admin_group(self)
          for i in list1:
              if (i['name']=='test1_RFE8203'):
                  reference=i['_ref']
                  data = {"lockout_setting":{"enable_sequential_failed_login_attempts_lockout":True,"sequential_attempts":2,"failed_lockout_duration":2,"never_unlock_user":False}}
                  response = ib_NIOS.wapi_request('PUT', ref=reference,fields=json.dumps(data), grid_vip=config.grid_vip)
                  logging.info(response)
                  list1=get_reference_value_admin_group(self)
                  duration =60*(data["lockout_setting"]["failed_lockout_duration"])
                  wrong_attempts =(data["lockout_setting"]["sequential_attempts"])
          while (wrong_attempts > 0):
                try:
                    response = ib_NIOS.wapi_request('PUT', user="testusr1_RFE8203", password="infdfs", ref=res['_ref'],fields=json.dumps(data), grid_vip=config.grid_vip)
                except Exception as error:
                    logging.info ("abcd {}".format(error))
                    wrong_attempts = wrong_attempts - 1
                    time.sleep(2)
          list1=get_reference_value_admin_user(self)
          for i in list1:
               if (i['name']=='testusr1_RFE8203'):
                   reference=i['_ref']
                   status="LOCKED"
                   rec2 = ib_NIOS.wapi_request('GET',object_type=reference + "?_return_fields=status")
                   ref1 = json.loads(rec2)
                   return_status = ref1['status']
                   if (status==return_status):
                       time.sleep(duration)
                       status1 = ib_NIOS.wapi_request('GET',object_type=reference + "?_return_fields=status")
                       ref1 = json.loads(status1)
                       return_status = ref1['status']
                       time.sleep(15)
                       #import pdb; pdb.set_trace()
                       if (return_status=='ACTIVE'):
                           logging.info("Test case 13 Passed")
                           assert True
                       else:
                           logging.info("Test case 13 Failed")
                           #assert False         


#Change the group of a locked user and checking the status.

      @pytest.mark.run(order=14)
      def test_n_change_group(self):
          res =get_lockout_setting(self)
          list1=get_reference_value_admin_group(self)
          for i in list1:
               if (i['name']=='test1_RFE8203'):
                  refer_1=i['_ref']
          for i in list1:
               if (i['name']=='test2_RFE_8203'):
                   refer_2=i['_ref']
          data= {"lockout_setting":{"enable_sequential_failed_login_attempts_lockout":True,"sequential_attempts":2,"failed_lockout_duration":1,"never_unlock_user":False}}
          response = ib_NIOS.wapi_request('PUT', ref=refer_1,fields=json.dumps(data), grid_vip=config.grid_vip)
          logging.info(response)

          data1 = {"lockout_setting":{"enable_sequential_failed_login_attempts_lockout":True,"sequential_attempts":2,"failed_lockout_duration":3,"never_unlock_user":True}}
          response = ib_NIOS.wapi_request('PUT', ref=refer_2,fields=json.dumps(data1), grid_vip=config.grid_vip)
          logging.info(response)
          duration = 60*(data1["lockout_setting"]["failed_lockout_duration"])
          wrong_attempts = (data["lockout_setting"]["sequential_attempts"])
          while (wrong_attempts > 0):
                 try:
                    response = ib_NIOS.wapi_request('PUT', user="testusr1_RFE8203", password="infdfs", ref=res['_ref'],fields=json.dumps(data), grid_vip=config.grid_vip)
                 except Exception as error:
                    logging.info ("abcd {}".format(error))
                    wrong_attempts = wrong_attempts - 1
                    time.sleep(2) 
          list1=get_reference_value_admin_user(self)
          for i in list1:
              if (i['name']=='testusr1_RFE8203'):
                  refer_3=i['_ref']
                  status="LOCKED"
                  rec2 = ib_NIOS.wapi_request('GET',object_type=refer_3 + "?_return_fields=status")
                  ref1 = json.loads(rec2)
                  return_status = ref1['status']
         
                  if (status==return_status):
                      time.sleep(2)
                      logging.info ("testusr1_RFE8203 is locked")
                      logging.info("Changing the group of the locked user")
                      time.sleep(2)
                      data3= {"admin_groups":["test2_RFE_8203"]}
                      response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data3),ref=refer_3,grid_vip=config.grid_vip)
                      list2=get_reference_value_admin_user(self)
                      for i in list2:
                          if (i['name']=='testusr1_RFE8203'):
                              refer_4=i['_ref']
                              rec2 = ib_NIOS.wapi_request('GET',object_type=refer_4 + "?_return_fields=status")
                              ref1 = json.loads(rec2)
                              status2 = ref1['status']
                              if (status2==status):
                                  logging.info("Test case 14 Passed")
                                  assert True
                              else:
                                  logging.info("Test case 14 Failed")
                                  assert False
      #check never unlock for super user group must not be allowed
      @pytest.mark.run(order=15)
      def test_o_check_never_unlock_in_superusergroup(self):
          list1=get_reference_value_admin_group(self)
          for i in list1:
              if (i['name']=='test1_RFE8203'):
                  reference=i['_ref']
                  data1 = {"lockout_setting":{"enable_sequential_failed_login_attempts_lockout":False,"sequential_attempts":1,"failed_lockout_duration":1,"never_unlock_user":True}}
                  response=ib_NIOS.wapi_request('PUT',ref=reference,fields=json.dumps(data1), grid_vip=config.grid_vip)
                  if(response[0]==400):
                     logging.info ("Never unlock not applicable for Super users")
                     assert True



import py
import json
import os
import re
import sys
import getopt
import ib_utils.ib_NIOS as ib_NIOS
#sys.path.append("/home/akulkarni/RFE_8950/WAPI_PyTest/")
#from ib_utils import ib_NIOS as ib_NIOS
from time import sleep
#import ib_data.ib_preparation as prep
import ib_utils.ib_papi as papi
import subprocess
import ib_utils.ib_conf_gen as conf_gen
from logger import logger
os.environ["PYTHONPATH"]=os.getcwd()
"""
   -m : Members separated by ':'  (GridMaster:Member1:Member2:Member3 etc., )
   -v : wapi_version
   -s : clinet_vm:client_ip:client_user:client_user_pw (CLIENT)
"""
args=sys.argv[1:]
optlist, args = getopt.getopt(args,'m:v:s')
for opt, arg in optlist:
    if opt == '-m':
        members=arg
    if opt == '-v':
       wapi_version=arg
      #splunk_version,wapi_version=arg.split(':')
#    if opt == '-s':
#       mgmt_master=arg	      

#client_vm,client_ip,client_user,client_passwd=arg.split(':')

"""
Configuring Master, Member & Reporting Member Variables. 
"""
var_hash={}
L=members.split(':')
master=L[0]
var_hash["GRID_MASTER_VIP"] =master
var_hash["GRID_MASTER_FQDN"]="ib-"+'-'.join(master.split('.'))+".infoblox.com"

#var_hash["GRID_MEMBER1_VIP"] =master
#var_hash["GRID_MEMBER1_FQDN"]="ib-"+'-'.join(master.split('.'))+".infoblox.com"

#var_hash["GRID_MEMBER2_VIP"] =master
#var_hash["GRID_MEMBER2_FQDN"]="ib-"+'-'.join(master.split('.'))+".infoblox.com"

var_hash["GRID_MASTER_VIP6"] =master

#GRID_MEMBER1_VIP

#for i,member in enumerate(L[1:]):
#    var_hash["GRID_MEMBER"+str(i+1)+"_VIP"]=member
#    var_hash["GRID_MEMBER"+str(i+1)+"_FQDN"]="ib-"+'-'.join(member.split('.'))+".infoblox.com"

var_hash["WAPI_VERSION"]=wapi_version





#Generating config.py Conf file
#logger.info("Generating config.py configuraiotn file")
rc=conf_gen.config(**var_hash)

#Addkyes
#logger.info("Adding SSH Keys on Grid Members")
#papi.addkeys(master)
#papi.addkeys(member)
#sleep(300)
    
#logger.info("Triggered execution for Minute Group Reports")  
#args_str = "-k test_validate --tb=long --html=license_report.html --junit-xml=license_results.xml -vv"
#py.test.cmdline.main(args_str.split(" "))

WORKSPACE = os.getenv('WORKSPACE')
BUILD_USER_ID = os.getenv('BUILD_USER_ID')
Build_Path = os.getenv('Build_Path')
Master1_IP = os.getenv('Master1_IP')
REPORT_URL = os.getenv('REPORT_URL')
BUILD_URL = os.getenv('BUILD_URL')
SERVER_IP = os.getenv('SERVER_IP')
PROJECT_NAME = os.getenv('PROJECT_NAME')



#command = "py.test WAPI82_Automation/CAA_Record.py --tb=long --html=WAPI_Test_Reports/HTML/RFE-4537.html --junit-xml=WAPI_Test_Reports/XML/RFE-4537.xml -vv"
#rm = os.system(command)
#sleep(120)




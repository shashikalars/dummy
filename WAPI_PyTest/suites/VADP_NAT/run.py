import py
import json
import os
import re
import sys
import getopt
import ib_utils.ib_NIOS as ib_NIOS
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
optlist, args = getopt.getopt(args,'m:v:z:')
for opt, arg in optlist:
    if opt == '-m':
        members=arg
    if opt == '-v':
       wapi_version=arg
    if opt == '-z':
       grid1_mgmt_vip=arg


"""
Configuring Master, Member & Reporting Member Variables. 
"""
var_hash={}
L=members.split(':')
master=L[0]
var_hash["GRID_MASTER_VIP"] =master
var_hash["GRID_MASTER_FQDN"]="ib-"+'-'.join(master.split('.'))+".infoblox.com"

for i,member in enumerate(L[1:]):
    var_hash["GRID_MEMBER"+str(i+1)+"_VIP"]=member
    var_hash["GRID_MEMBER"+str(i+1)+"_FQDN"]="ib-"+'-'.join(member.split('.'))+".infoblox.com"

#D=vmid.split(':')
#masterid=D[0]
#var_hash["GRID_MASTER_ID"] =masterid

#for i,vmid in enumerate(L[1:]):
#    var_hash["GRID_MEMBER"+str(i+1)+"_ID"]=vmid
    #var_hash["GRID_MEMBER"+str(i+1)+"_ID"]="ib-"+'-'.join(member.split('.'))+".infoblox.com"

var_hash["WAPI_VERSION"]=wapi_version

#var_hash["CLIENT_IP"]=client_ip
var_hash["GRID_MEMBER3_MGMT_VIP"]=grid1_mgmt_vip
#var_hash["GRID2_MASTER_FQDN"]="ib-"+'-'.join(grid2_vip.split('.'))+".infoblox.com"

#var_hash["GRID1_MASTER_V6"]=grid1_v6
#Generating config.py Conf file
rc=conf_gen.config(**var_hash)

#Addkyes
logger.info("Adding SSH Keys on Grid Members")
papi.addkeys(master)
sleep(120)
    

#cmd = "py.test WAPI_Automation/test_adp_nat.py --tb=long --html=adp_nat_report.html --junit-xml=adp_nat_results.xml -vv"
#rm = os.system(cmd)


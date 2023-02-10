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
#import logging
os.environ["PYTHONPATH"]=os.getcwd()
"""
   -m : Members separated by ':'  (GridMaster:Member1:Member2:Member3 etc., )
   -v : wapi_version
   -s : clinet_vm:client_ip:client_user:client_user_pw (CLIENT)
"""
args=sys.argv[1:]
optlist, args = getopt.getopt(args,'m:v:')
for opt, arg in optlist:
    if opt == '-m':
        members=arg
    if opt == '-v':
       wapi_version=arg
      #splunk_version,wapi_version=arg.split(':')
#    if opt == '-s':
#       client_vm,client_ip,client_user,client_passwd=arg.split(':')

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



var_hash["WAPI_VERSION"]=wapi_version



#Generating config.py Conf file
#logger.info("Generating config.py configuraiotn file")
rc=conf_gen.config(**var_hash)

#Addkyes
logger.info("Adding SSH Keys on Grid Members")
#papi.addkeys(master)

#sleep(300)
    

#cmd = "py.test Outbound5/UsernameDB_test.py --tb=long --html=Outbound5/sj.html --junit-xml=Outbound5/sj.xml -vvs"
#cmd = "py.test outbound-6/outbound6_usernameDB_original.py --tb=long --html=sj.html --junit-xml=sj.xml -vvs"
#cmd = "py.test outbound-6/NIOSSPT-8915.py --tb=long --html=sj.html --junit-xml=sj.xml -vvs"
#cmd = "py.test outbound-6/NIOSSPT-9285_copy1.py --tb=long --html=sj.html --junit-xml=sj.xml -vvs"
cmd = "py.test Outbound5/outbound5_dns_zone_delete.py --tb=long --html=vijay.html --junit-xml=vijay.xml -vvs"
#cmd = "py.test outbound-6/outbound5_syslog.py --tb=long --html=sj.html --junit-xml=sj.xml -vvs"
#cmd = "py.test Outbound5/records.py --tb=long --html=Outbound5/rk.html --junit-xml=Outbound5/rk.xml -vvs"
#rm = os.system(cmd)


import json
import os
import re
import sys
import getopt
#import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
#import ib_data.ib_preparation as prep
import ib_utils.ib_papi as papi
import subprocess
import ib_utils.ib_conf_gen as conf_gen
#from logger import logger
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

for i,member in enumerate(L[1:]):
    var_hash["GRID_MEMBER"+str(i+1)+"_VIP"]=member
    var_hash["GRID_MEMBER"+str(i+1)+"_FQDN"]="ib-"+'-'.join(member.split('.'))+".infoblox.com"

var_hash["WAPI_VERSION"]=wapi_version


#CLIENT Configuraiton for reporting backup
if 'client_vm' not in locals():
    client_ip=re.findall('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',os.popen("/usr/sbin/ifconfig | grep 'inet '|grep -v '127.0.0.1'").readline())[0].rstrip()
    client_vm=os.popen("hostname").readline().rstrip()
    client_vm,client_ip,client_user,client_passwd=(client_vm,client_ip,"root","infoblox")
var_hash["CLIENT_HWID"]=client_vm
var_hash["CLIENT_IP"]=client_ip
var_hash["CLIENT_USER"]=client_user
var_hash["CLIENT_PASSWD"]=client_passwd



#Generating config.py Conf file
#logger.info("Generating config.py configuraiotn file")
rc=conf_gen.config(**var_hash)
os.system("sed -i 's/grid_fqdn=\"ib-10-36/grid_fqdn=\"ib-10-35/g'  config.py")
os.system("sed -i 's/grid_member_fqdn=\"ib-10-36/grid_member_fqdn=\"ib-10-35/g'  config.py")
os.system("sed -i 's/dns_resolver=\"10.32.2.228/dns_resolver=\"10.195.3.10/g'  config.py")
os.system('cat config.py')

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




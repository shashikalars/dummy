import py
import json
import os
import re
import sys
import getopt
os.environ["PYTHONPATH"]=os.getcwd()
import ib_utils.ib_papi as papi
import ib_utils.ib_conf_gen as conf_gen
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
from logger import logger
"""
   -t : single_indexer, single_site_cluster, multi_site_cluster, SSC_SystemActivity, MSC_SystemActivity
   -i : Indexers separated by ':', Ex: -i '10.34.221.55' for 'Single Indexer' Similarly -i '10.34.221.55:10.34.221.56' & -i '10.34.221.55:10.34.221.56:10.34.221.57:10.34.221.58' for clusters
   -m : Members separated by ':'  (GridMaster:Member1:Member2:Member3 etc., )
   -d : DCVM_IP 
   -v : splunk_verison:wapi_version
   -p : pool_dir:pool_tag
   -n : network id say (10.34.220.0)
   -s : clinet_vm:client_ip:client_user:client_user_pw (CLIENT)
   -o : cisco_ise_ip:cisco_ise_user:cisco_ise_password:cisco_ise_secret
   -r : olympic ruleset
"""
args=sys.argv[1:]
optlist, args = getopt.getopt(args,'c:i:m:M:d:p:v:t:n:s:o:r:')
for opt, arg in optlist:
    if opt == '-t':
        run_type=arg
    if opt == '-i':
        indexer=arg
    if opt == '-m':
        members=arg
    if opt == '-d':
        dcvm_ip=arg
    if opt == '-v':
        #splunk_version,wapi_version=arg.split(':')
        wapi_version=arg
    if opt == '-p':
        pool_dir,pool_tag=arg.split(':')
    if opt == '-n':
        network_id=arg
    if opt == '-s':
        client_vm,client_ip,client_user,client_passwd=arg.split(':')
    if opt == '-o':
        cisco_ise_ip,cisco_ise_user,cisco_ise_password,cisco_ise_secret=arg.split(':')
    if opt == '-r':
        olympic_ruleset=arg
    if opt == '-M':
        mgmt=arg


"""
Configuring Master, Member & Reporting Member Variables. 
"""
var_hash={}
L=members.split(':')
master=L[0]
var_hash["GRID_MASTER_VIP"] =master
var_hash["GRID_MASTER_FQDN"]="ib-"+'-'.join(master.split('.'))+".infoblox.com"

#var_hash["GRID_MASTER_VIP_MGMT"]=mgmt
#var_hash["GRID_MASTER_FQDN_MGMT"]="ib-"+'-'.join(mgmt.split('.'))+".infoblox.com"

for i,member in enumerate(L[1:]):
    var_hash["GRID_MEMBER"+str(i+1)+"_VIP"]=member
    var_hash["GRID_MEMBER"+str(i+1)+"_FQDN"]="ib-"+'-'.join(member.split('.'))+".infoblox.com"
#L=indexer.split(':')
#for i,member in enumerate(L):
#    var_hash["REPORTING_MEMBER"+str(i+1)+"_VIP"]=member
#    var_hash["REPORTING_MEMBER"+str(i+1)+"_FQDN"]="ib-"+'-'.join(member.split('.'))+".infoblox.com"

#if 'dcvm_ip' in locals():
#     var_hash["DCVM_IP"]=dcvm_ip

var_hash["WAPI_VERSION"]=wapi_version
#var_hash["SPLUNK_VERSION"]=splunk_version
#var_hash["POOL_DIR"]=pool_dir
#var_hash["POOL_TAG"]=pool_tag

####olympic_ruleset
#var_hash["OLYMPIC_RULESET"]=olympic_ruleset

####CLIENT Configuraiton for reporting backup
#if 'client_vm' not in locals():
#    client_ip=re.findall('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',os.popen("/usr/sbin/ifconfig | grep 'inet '|grep -v '127.0.0.1'").readline())[0].rstrip()
#    client_vm=os.popen("hostname").readline().rstrip()
#    client_vm,client_ip,client_user,client_passwd=(client_vm,client_ip,"root","infoblox")
#var_hash["CLIENT_HWID"]=client_vm
#var_hash["CLIENT_IP"]=client_ip
#var_hash["CLIENT_USER"]=client_user
#var_hash["CLIENT_PASSWD"]=client_passwd

####CISCO Configuraiton
#if 'cisco_ise_ip' not in locals():
#    cisco_ise_ip,cisco_ise_user,cisco_ise_password,cisco_ise_secret=("10.36.141.15","qa","Infoblox1492","secret") #default
#var_hash["CISCO_ISE_IP"]=cisco_ise_ip
#var_hash["CISCO_ISE_USER"]=cisco_ise_user
#var_hash["CISCO_ISE_PASSWORD"]=cisco_ise_password
#var_hash["CISCO_ISE_SECRET"]=cisco_ise_secret

####SPLUNK PORT
#if(run_type == 'single_indexer'):
#    var_hash["INDEXER_IP"]=var_hash["REPORTING_MEMBER1_VIP"]
#    var_hash["SPLUNK_PORT"]="8089"
#else:
#    var_hash["INDEXER_IP"]=var_hash["GRID_MASTER_VIP"]
#    var_hash["SPLUNK_PORT"]="7089"


#Generating config.py Conf file
logger.info("Generating config.py configuration file")
rc=conf_gen.config(**var_hash)

import py
import json
import os
import re
import sys
import getopt
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
import ib_data.ib_preparation as prep
import ib_utils.ib_papi as papi
import ib_utils.ib_conf_gen as conf_gen
from logger import logger
#os.environ["PYTHONPATH"]=os.getcwd()
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
optlist, args = getopt.getopt(args,'c:i:m:d:p:v:t:n:s:o:r:')
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
       splunk_version,wapi_version=arg.split(':')
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


"""
Configuring Master, Member & Reporting Member Variables. 
"""
logger.info("START: '%s' Reporting execuiton is started",run_type)
var_hash={}
L=members.split(':')
master=L[0]
var_hash["GRID_MASTER_VIP"] =master
var_hash["GRID_MASTER_FQDN"]="ib-"+'-'.join(master.split('.'))+".infoblox.com"

for i,member in enumerate(L[1:]):
    var_hash["GRID_MEMBER"+str(i+1)+"_VIP"]=member
    var_hash["GRID_MEMBER"+str(i+1)+"_FQDN"]="ib-"+'-'.join(member.split('.'))+".infoblox.com"
L=indexer.split(':')
for i,member in enumerate(L):
    var_hash["REPORTING_MEMBER"+str(i+1)+"_VIP"]=member
    var_hash["REPORTING_MEMBER"+str(i+1)+"_FQDN"]="ib-"+'-'.join(member.split('.'))+".infoblox.com"

if 'dcvm_ip' in locals():
     var_hash["DCVM_IP"]=dcvm_ip

var_hash["WAPI_VERSION"]=wapi_version
var_hash["SPLUNK_VERSION"]=splunk_version
var_hash["POOL_DIR"]=pool_dir
var_hash["POOL_TAG"]=pool_tag

#olympic_ruleset
#var_hash["OLYMPIC_RULESET"]=olympic_ruleset

#CLIENT Configuraiton for reporting backup
if 'client_vm' not in locals():
    client_ip=re.findall('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',os.popen("/usr/sbin/ifconfig | grep 'inet '|grep -v '127.0.0.1'").readline())[0].rstrip()
    client_vm=os.popen("hostname").readline().rstrip()
    client_vm,client_ip,client_user,client_passwd=(client_vm,client_ip,"root","infoblox")
var_hash["CLIENT_HWID"]=client_vm
var_hash["CLIENT_IP"]=client_ip
var_hash["CLIENT_USER"]=client_user
var_hash["CLIENT_PASSWD"]=client_passwd

#CISCO Configuraiton
if 'cisco_ise_ip' not in locals():
    cisco_ise_ip,cisco_ise_user,cisco_ise_password,cisco_ise_secret=("10.36.141.15","qa","Infoblox1492","secret") #default
var_hash["CISCO_ISE_IP"]=cisco_ise_ip
var_hash["CISCO_ISE_USER"]=cisco_ise_user
var_hash["CISCO_ISE_PASSWORD"]=cisco_ise_password
var_hash["CISCO_ISE_SECRET"]=cisco_ise_secret

#SPLUNK PORT
if(run_type == 'single_indexer'):
    var_hash["INDEXER_IP"]=var_hash["REPORTING_MEMBER1_VIP"]
    var_hash["SPLUNK_PORT"]="8089"
else:
    var_hash["INDEXER_IP"]=var_hash["GRID_MASTER_VIP"]
    var_hash["SPLUNK_PORT"]="7089"


print("###############################################")
print("TESTING")

#Generating config.py Conf file
logger.info("Generating config.py configuraiotn file")
rc=conf_gen.config(**var_hash)

os.system('cat config.py')
b = os.system('cp -rf config.py ~/API_Automation/WAPI_PyTest/')
print("COPIED......",b)

#Addkyes
logger.info("Adding SSH Keys on Grid Members")
papi.addkeys(master)

#Download Perl Module
#logger.info("Downloading Perl Module")
#papi.download_pm(master)

#Time Zone Change & Enabling SNMP configuraiton
logger.info("Changing time Zone as UTC")
papi.set_time_zone(master)


#Enabling Reporting 
logger.info("Enabling Reporting by selecting All reporting category")
papi.enable_reporting(master)

logger.info("Wait for 7 min, enabling reporting first Time.")
print("Sleeping for 600 seconds")
sleep(600)

#Generating splunkrc Conf file
logger.info("Generating .splunkrc file")
rc=conf_gen.splunkrc(var_hash["INDEXER_IP"],var_hash["SPLUNK_PORT"],var_hash["SPLUNK_VERSION"])  

if(run_type == 'single_indexer' or  'single_site_cluster' or 'multi_site_cluster'):
    logger.info("Preparation for '%s' execution (Hourly & Minute Reporting Group)",run_type)  

    #Configuring Reporting Mode. 
    if(run_type == 'single_site_cluster'):
        logger.info("Configuring 'Single Site Cluster Mode'")
        papi.configure_single_site(master)
    elif(run_type == 'multi_site_cluster'):
        logger.info("Configuring Reporting-Site extensible attribute")
        papi.configure_reporting_site(master,var_hash["REPORTING_MEMBER1_VIP"],'site1') 
        papi.configure_reporting_site(master,var_hash["REPORTING_MEMBER2_VIP"],'site1') 
        papi.configure_reporting_site(master,var_hash["REPORTING_MEMBER3_VIP"],'site2') 
        papi.configure_reporting_site(master,var_hash["REPORTING_MEMBER4_VIP"],'site2') 
        logger.info("Configuring Reporting-Site extensible attribute")
        logger.info("Configuring 'Multi Site Cluster Mode'")
        papi.configure_multi_site(master,'site1','site2')
    
    # logger.info("Registering DCVM")  
    # #Enabling 'Data Collection'
    # enable = {"enable":True}
    # response = ib_NIOS.wapi_request('POST', object_type="datacollector?_function=registration", fields=json.dumps(enable))
    # rc=papi.register_dcvm(dcvm_ip,master,'auto','auto123') 

    # Preparation for MG & HG
    # logger.info("Preparation for DNS Top Clients Per Domain(Hourly Group Report)")  
    # prep.dns_top_clients_per_domain()   
    
    # logger.info("Preparation for DNS Top Clients(Hourly Group Report)")  
    # prep.dns_top_clients()

    
    # logger.info("Preparation for DNS Top Requested Domain Names(Hourly Group Report)")  
    # prep.dns_top_requested_domain_names()

    # logger.info("Preparation for DNS Top Timed Out Recursive Queries (Hourly Group Report)")  
    # prep.dns_top_timed_out_recursive_queries()

    # logger.info("Preparation for DNS Top NXDOMAIN / NOERROR(Hourly Group Report)")  
    # prep.dns_top_nxdomain_noerror()

    logger.info("Preparation for Threat Protection Reports (Minute Group Report)")
    #prep.threat_protection_reports()

    # logger.info("Preparation for RPZ reports (Hourly Group Reports)")
    # prep.security_rpz_reports()
    
    # logger.info("Preparation for DHCP Fingerprint Category (Hourly Group Reports)")
    # prep.dhcp_fingerprint()
    
    # logger.info("Preparation for DHCP Lease Clients (Hourly Group Reports)")
    # prep.dhcp_top_lease_clients()

    # logger.info("Preparation for DHCPv4 Usage Statistics, DHCP Usage Trend and Range Utilization Trend (Hourly Group Reports)")
    # prep.dhcpv4_usage_statistics()

    # logger.info("Preparation for Discovery report (Hourly Group Report")
    # prep.discovery()
    ''' 
    logger.info("Preparation for servfail report (Hourly Group Report")
    prep.servfail()
    
    logger.info("Preparation for tunneling report (Minute Group Report")
    prep.tunneling()
    
    logger.info("Waiting for 10 min for intial reports to get update")
    sleep(1000)
    '''

    logger.info("Triggered execution for Minute Group Reports")  
    args_str = "-k test_MG --tb=long --html=mg_report.html --junit-xml=mg_results.xml -vss"
    #args_str = "-k test_MG -rF -rP --html=mg_report.html --junit-xml=mg_results.xml -vss"
    m = py.test.cmdline.main(args_str.split(" ")) 
    print(m)
    logger.info("Completed execution of Minute Group Reports")  

    print("Going to sleep for 14400 seconds")
    sleep(14400)
    print("14400 Sleep completed")

    logger.info("Triggered execution for Hourly Group Reports")
    args_str = "-k test_HG --tb=long --html=hg_report.html --junit-xml=hg_results.xml -vss"
    py.test.cmdline.main(args_str.split(" "))
    logger.info("Completed execution of Hourly Group Reports")
    
    print(os.getcwd())
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^") 

    ''''

    logger.info("Triggered execution for Hourly Group Reports")  
    args_str = "-k test_HG --tb=long --html=hg_report.html --junit-xml=hg_results.xml -vv"
    py.test.cmdline.main(args_str.split(" "))
    logger.info("Completed execution of Hourly Group Reports")  
    
    # logger.info("Scipt to Perform Backup/Restore Operation")
    # os.system("python Backup_Restore/Backup_Restore.py")
    # sleep(600)
    
    # logger.info("Triggered execution for Hourly Group Reports After Perform Restore Operation")
    # #args_str = "-k test_BRG --tb=long --html=brg_report.html --junit-xml=brg_results.xml -vv"
    # args_str = "-k test_BRG -vvs"
    # py.test.cmdline.main(args_str.split(" "))
    # logger.info("Completed execution of Hourly Group Reports after perform restore operation")

    '''
    
    '''
    logger.info("Waiting for 12 horus to trigger Half Day Group Reports (Reports which are updated after 6 hours considered as HDG")
    sleep(43200)
    logger.info("Triggered execution for Half Day Group Reports")  
    args_str = "-k test_HDG --tb=long --html=hdg_report.html --junit-xml=hdg_results.xml -vv"
    py.test.cmdline.main(args_str.split(" "))
    logger.info("Completed execution of Half Day Group Reports")  

    logger.info("Waiting for 12 more hours to trigger Day Group Reports")  
    sleep(43200)
    logger.info("Triggered execution for Day Group Reports")  
    args_str = "-k test_DG --tb=long --html=dg_report.html --junit-xml=dg_results.xml -vv"
    py.test.cmdline.main(args_str.split(" "))
    logger.info("Completed execution of Day Group Reports")  

    logger.info("UnRegistering DCVM")  
    rc=papi.unregister_dcvm(dcvm_ip,master,'auto','auto123')
    '''
elif (run_type == 'SSC_SystemActivity'):
    args_str = "-k test_SSC --collect-only"
    py.test.cmdline.main(args_str.split(" "))

elif (run_type == 'MSC_SystemActivity'):
    args_str = "-k test_MSC --collect-only"
    py.test.cmdline.main(args_str.split(" "))

#Report' Generation.

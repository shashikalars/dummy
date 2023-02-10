
"""
Copyright (c) Infoblox Inc., 2016

Description: This is Auto Generated config file.

Author  : Manimaran.A
History : 05/27/2015
"""

#GRID INFORMATION
grid_vip="10.35.189.6"
grid_fqdn="ib-10-35-189-6.infoblox.com"
username="admin"
password="infoblox"
grid2_vip="[GRID2_MASTER_VIP]"
grid2_fqdn="[GRID2_MASTER_FQDN]"
email_id="mgovarthanan@infoblox.com"

#INDEXER_IP WILL BE 'GRID MASTER IP' IF GRID IS CONFIGURED WITH CLUSTERING 
indexer_ip="10.35.188.15"
network_id="[NETWORK_ID]"
grid_master_vip="10.35.189.6"
grid_member_fqdn="ib-10-35-189-6.infoblox.com"
grid_member1_vip="[GRID_MEMBER1_VIP]"
grid_member1_fqdn="[GRID_MEMBER1_FQDN]"
grid_member2_vip="[GRID_MEMBER2_VIP]"
grid_member2_fqdn="[GRID_MEMBER2_FQDN]"
grid_member3_vip="[GRID_MEMBER3_VIP]"
grid_member3_fqdn="[GRID_MEMBER3_FQDN]"
grid_member4_vip="[GRID_MEMBER4_VIP]"
grid_member4_fqdn="[GRID_MEMBER4_FQDN]"
grid_member5_vip="[GRID_MEMBER5_VIP]"
grid_member5_fqdn="[GRID_MEMBER5_FQDN]"
reporting_member1_ip="10.35.188.15"
reporting_member1_fqdn="ib-10-35-188-15.infoblox.com"
reporting_member2_ip="[REPORTING_MEMBER2_VIP]"
reporting_member2_fqdn="[REPORTING_MEMBER2_FQDN]"
reporting_member3_ip="[REPORTING_MEMBER3_VIP]"
reporting_member3_fqdn="[REPORTING_MEMBER3_FQDN]"
reporting_member4_ip="[REPORTING_MEMBER4_VIP]"
reporting_member4_fqdn="[REPORTING_MEMBER4_FQDN]"
resolver_ip="10.120.3.10"
forwarder_ip="10.39.16.160"
client_ip1="10.120.22.146"


#CONFIG POOL INFORMATION
pool_dir="/tmp/MS_Server"
pool_tag="GRID1"
hw_info="/tmp/MS_Server/hws.txt"

#DNS Resolver
dns_resolver="10.32.2.228"  #which is configured for CISCO ISC

#DCVM Configuration
dcvm_ip="[DCVM_IP]"
dcvm_user="auto"
dcvm_password="auto123"

#CISCO ISC Configuraiton
cisco_ise_ip="10.36.141.15"
cisco_ise_user="qa"
cisco_ise_password="Infoblox1492"
cisco_ise_secret="secret"

#WAPI VERSION
wapi_version = "2.12.1"
splunk_port="8089"
splunk_version="7.2.6"

#CLIENT INFORMION
client_vm="vm-01-77"
client_ip="10.36.198.1"
#client_vm="vm-01-77"
#client_ip="10.36.198.1"
client_user="root"
client_passwd="infoblox"
olympic_ruleset="[OLYMPIC_RULESET]"

#BELOW IP'S ARE USED FOR DNS_TOP_CLIENTs
#client_eth1_ip1="10.35.132.6"
client_eth1_ip1="10.35.132.6"
client_eth1_ip2="10.35.195.11"
#client_eth1_ip2="10.34.220.251"
client_eth1_ip3="10.34.220.252"
client_eth1_ip4="10.34.220.253"
client_eth1_ip5="10.34.220.254"
client_netmask="255.255.252.0"

#BELOW IP'S ARE USED FOR DNS_TOP_REQUESTED DOMAIN
client_eth1_ip6="10.34.220.240"
client_eth1_ip7="10.34.220.241"
client_eth1_ip8="10.34.220.242"

#BELOW IP'S ARE USED FOR DNS Query Trend per IP Block Group
client_eth1_ip9 ="10.36.198.8"
client_eth1_ip10="10.36.198.7"
client_eth1_ip11="10.120.22.146"
client_eth1_ip12="10.120.21.51"
client_eth1_ip13="10.120.20.92"


#REPORTING BACKUP & RESTORE DEFAULT PATH
backup_path="/tmp/reporting_bakup"

#PY TEST ENVIRONMNET cONFIGURATION
log_path = "output.log"
search_py="/import/qaddi/API_Automation/splunk-sdk-python/examples/search.py"
json_file="report.json"



#GLOBAL VARIABLE
scal_test1=""
scal_test2=""
scal_test3=""
scal_test4=""
scal_test5=""
list_test1=[]
list_test2=[]
list_test3=[]
list_test4=[]
list_test5=[]
dict_test1={}
dict_test2={}
dict_test3={}
dict_test4={}
dict_test5={}

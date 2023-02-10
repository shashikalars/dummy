import os
import re
import sys
import string
from time import sleep
from logger import logger

"""
 Following 'splunk_conf' variable is used to dynamically generate splunkd config file. 
 NOTE: DONT MODIFY FOLLOWING VARIABLE.
"""

SPLUNK_CONF_VAR="""
#This is Auto Generated Config file
# Splunk host (default: localhost)
# host=<INDEXER_IP>     #For  Single Indexer Configuraiton 
# host=<Grid Master IP> #For Single & Multi Site Clustering Configuration
host=[HOST_IP]
# Splunk admin port (default: 8089)
# port=8089 #For Single Indexer 
# port=7089 #For Single & Multi Site Clustering Configuration
port=[PORT]
# Splunk username
username=admin
# Splunk password
password=[PASSWD]
# Access scheme (default: https)
scheme=https
# Your version of Splunk (default: 5.0)
version=[SPLUNK_VERSION]
"""


"""
Following 'config' variable is used to generate config.py dinamically.
NOTE: DONT MODIFY FOLLOWING VARIABLE.
"""

CONFIG_VAR="""
\"\"\"
Copyright (c) Infoblox Inc., 2016

Description: This is Auto Generated config file.

Author  : Manimaran
History : 12/20/2016
\"\"\"

#GRID INFORMATION
grid_vip="[GRID_MASTER_VIP]"
grid_fqdn="[GRID_MASTER_FQDN]"
username="admin"
password="infoblox"
grid2_vip="[GRID2_MASTER_VIP]"
grid2_fqdn="[GRID2_MASTER_FQDN]"

#INDEXER_IP WILL BE 'GRID MASTER IP' IF GRID IS CONFIGURED WITH CLUSTERING 
indexer_ip="[INDEXER_IP]"
network_id="[NETWORK_ID]"
grid_master_vip="[GRID_MASTER_VIP]"
grid_member_fqdn="[GRID_MASTER_FQDN]"
grid_ipv6_vip="[GRID1_MASTER_V6]"
grid_member1_vip="[GRID_MEMBER1_VIP]"
grid_member1_fqdn="[GRID_MEMBER1_FQDN]"
grid_member2_vip="[GRID_MEMBER2_VIP]"
grid_member2_fqdn="[GRID_MEMBER2_FQDN]"
grid_member3_mgmt_vip="[GRID_MEMBER3_MGMT_VIP]"
grid_member3_mgmt_fqdn="[GRID_MEMBER3_MGMT_FQDN]"
grid_member4_mgmt_vip="[GRID_MEMBER4_VIP]"
grid_member4_mgmt_fqdn="[GRID_MEMBER4_FQDN]"
grid_member5_vip="[GRID_MEMBER5_VIP]"
grid_member5_fqdn="[GRID_MEMBER5_FQDN]"

#CONFIG POOL INFORMATION
pool_dir="[POOL_DIR]"
pool_tag="[POOL_TAG]"
hw_info="[POOL_DIR]/hws.txt"

#DNS Resolver
dns_resolver="10.32.2.228"  #which is configured for CISCO ISC


#WAPI VERSION
wapi_version = "[WAPI_VERSION]"

#CLIENT INFORMION
client_vm="[CLIENT_HWID]"
client_ip="10.36.200.11"
client_eth1="10.34.15.199"
client_eth2="10.34.15.185"
client_user="[CLIENT_USER]"
client_passwd="[CLIENT_PASSWD]"

#PY TEST ENVIRONMNET cONFIGURATION
log_path = "output.log"
search_py="../splunk-sdk-python/examples/search.py"
json_file="report.json"



"""

"""
Search and replace
"""
def  generate_conf(x,k):
    for stext in k.keys():
        x=string.replace(x,"["+stext+"]",k[stext])
    return x


def config(**k):
    conf=generate_conf(CONFIG_VAR,k)
    fout=open('config.py','w')
    fout.write(conf)
    logger.info(conf)
    fout.close

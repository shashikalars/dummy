
"""
Copyright (c) Infoblox Inc., 2016

Description: This is Auto Generated config file.

Author  : Manimaran
History : 12/20/2016
"""

#GRID INFORMATION
grid_vip="10.35.160.14"
grid_fqdn="ib-10-35-160-14.infoblox.com"
username="admin"
password="infoblox"
grid2_vip="[GRID2_MASTER_VIP]"
grid2_fqdn="[GRID2_MASTER_FQDN]"

#INDEXER_IP WILL BE 'GRID MASTER IP' IF GRID IS CONFIGURED WITH CLUSTERING 
indexer_ip="[INDEXER_IP]"
network_id="[NETWORK_ID]"
grid_master_vip="10.35.160.14"
grid_member_fqdn="ib-10-35-160-14.infoblox.com"
grid_ipv6_vip="[GRID1_MASTER_V6]"
grid_member1_vip="10.35.117.14"
grid_member1_fqdn="ib-10-35-117-14.infoblox.com"
grid_member2_vip="[GRID_MEMBER2_VIP]"
grid_member2_fqdn="[GRID_MEMBER2_FQDN]"
grid_member3_mgmt_vip="10.36.117.14"
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
wapi_version = "2.9"

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




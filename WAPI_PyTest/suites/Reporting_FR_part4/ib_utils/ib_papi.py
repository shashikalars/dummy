"""
 Copyright (c) Infoblox Inc., 2016

 Modle Name  : ib_papi
 Description : This module is used to execute PAPI utility

 Author : Raghavendra MN
 History: 05/25/2016(Created)
"""
import subprocess
import config
import os

def import_csv(csv_file,gm_ip=config.grid_vip):
     rc=subprocess.call(['perl','/import/qaddi/API_Automation/WAPI_PyTest/ib_utils/ib_import_CSV.pl',gm_ip,csv_file])
     return rc


"""
This module will add SSH keys into the box.
"""

def addkeys(gm_ip):
    rc=subprocess.call(['addkeys',gm_ip ])
    return rc
'''
This Module is to enable the Recursion, Zone transfer and forwarders.
'''
def enable_forwarders_recursion(gm_ip):
    rc=subprocess.call(['perl', '/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/enable_recursion_and_forwarders.pl',gm_ip])
    return rc
'''
This Module is to disable the Recursion, Zone transfer and forwarders.
'''
def disable_forwarders_recursion(gm_ip):
    rc=subprocess.call(['perl', '/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/disable_forwarder_and_recursion.pl',gm_ip])
    return rc

"""
This Module is to enable the Recursion, Zone transfer and forwarders.
"""
def enable_forwarders_update(gm_ip):
    rc=subprocess.call(['perl', '/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/enable_update_zone_transfer.pl',gm_ip])
    return rc

def disable_forwarders_update(gm_ip):
    rc=subprocess.call(['perl', '/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/disable_update_zone_transfer.pl',gm_ip])
    return rc

"""
Adding RPZ Records in Local Zone.
"""
def add_rpz_records(gm_ip):
    rc=subprocess.call(['python','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/rpz_records.py',gm_ip])
    return rc

"""
Perform Queries for Displaying RPZ Security Reports
"""
def queries_rpz_records(gm_ip):
    rc=subprocess.call(['sh','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/dig.sh',gm_ip])
    return rc

"""
This module will download Perl module from Grid master.

def download_pm(gm_ip):
    rc=subprocess.call(['getPAPI',gm_ip,'/var/tmp/InfobloxPM/'])
    return rc
"""
"""
This module will download Perl module from Grid master.
"""
def download_pm(gm_ip):
    rc=subprocess.call(['getPAPI',gm_ip,'/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4'])
    return rc

"""
This module will change the TIME Zone default will be UTC Format.
"""
def set_time_zone(gm_ip,tz='(UTC) Coordinated Universal Time'):
    rc=subprocess.call(['perl', '/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Grid_properties/enable_Grid_settings.pl',gm_ip,tz])
    return rc


"""
This module will Enable the reproting by selecting all category.
"""
def enable_reporting(gm_ip):
    rc=subprocess.call(['perl', '/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Reporting_Properties/reporting.pl',gm_ip])
    return rc

"""
This module will configure Reporting Site Extensible attribute to Reporting member.
"""
def configure_reporting_site(gm_ip,rm_ip,site):
    rc=subprocess.call(['perl', '/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Reporting_Properties/Configure_ReportingSite.pl',gm_ip,rm_ip,site])
    return rc

"""
This module will enable Multi Site and also change the PrimarySite according to the order.
"""
def configure_multi_site(gm_ip,s1,s2):
    rc=subprocess.call(['perl', '/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Reporting_Properties/configure_primary_site.pl',gm_ip,s1,s2])
    return rc

"""
This module to enalbe Single Site
"""
def configure_single_site(gm_ip):
   rc=subprocess.call(['perl','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Reporting_Properties/configure_single_site.pl',gm_ip])
   return rc

"""
Register & Un-Register DCVM
"""
def register_dcvm(dcvm_ip,gm_ip,scp_user,passwd):
   rc=subprocess.call(['python','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Data_Collector/register_dcvm.py',dcvm_ip,gm_ip,scp_user,passwd])
   return rc

def unregister_dcvm(dcvm_ip,gm_ip,scp_user,passwd):
   rc=subprocess.call(['python','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Data_Collector/unregister_dcvm.py',dcvm_ip,gm_ip,scp_user,passwd])
   return rc


"""
Adding IP Block Group.
"""
def add_ip_block_group(group_name, group_ips,gm_ip=config.grid_vip):
   dname="/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/DNS_Query/DNS_Query_Trend_Per_IP_Block_Group/"
   rc=subprocess.call(['python',dname+"generate_csv.py",dname+"ip_group.csv",group_name,group_ips])
   rc1=subprocess.call(['perl',dname+'import_CSV.pl',gm_ip,dname+"ip_group.csv"])
   return(rc+rc1)

"""
Configuring IP Block
"""
def configure_ip_block_group(group_names,gm_ip=config.grid_vip):
    dname="/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/DNS_Query/DNS_Query_Trend_Per_IP_Block_Group/"
    rc=subprocess.call(['perl',dname+'DNS_Query_Trend_Per_IP_Block_Group.pl',gm_ip,'true',group_names])
    return(rc)

def remove_ip_block_group(group_names,gm_ip=config.grid_vip):
    dname="/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/DNS_Query/DNS_Query_Trend_Per_IP_Block_Group/"
    rc=subprocess.call(['perl',dname+'DNS_Query_Trend_Per_IP_Block_Group.pl',gm_ip,'false',group_names])
    return(rc)


"""
Check Clustering mode.
"""
def check_clustering_mode(gm_ip=config.grid_vip):
    fp=os.popen("perl /import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Reporting_Properties/check_cluster_mode.pl "+gm_ip)
    L=fp.readlines()
    return(L[0].rstrip())


"""
Get search Head.
"""
def get_search_head(gm_ip=config.grid_vip):
    fp=os.popen("perl /import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Reporting_Properties/get_search_head.pl "+gm_ip)
    L=fp.readlines()
    return(L[0].rstrip())



"""
Upload Rulesets
"""
def upload_ruleset(gm_ip,olympic_ruleset):
   rc=subprocess.call(['perl','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/ruleset_upload.pl',gm_ip,olympic_ruleset])
   return rc

"""
Enable MGMT
"""
def enable_mgmt(mgmt_ip,gm_ip=config.grid_vip):
   rc=subprocess.call(['perl','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/enable_mgmt.pl',mgmt_ip,gm_ip])
   return rc

"""
Disable Auto Rules
"""
def disable_auto_rules(tp_ip):
   rc=subprocess.call(['expect','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/disable_auto_rule.exp',tp_ip])
   return rc

"""
Disable TP System Rules
"""
def disable_tp_system_rules(gm_ip):
   rc=subprocess.call(['perl','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/disable_tp_system_rules.pl',gm_ip])
   return rc

"""
Add TCP rules
"""
def add_tcp_rules(gm_ip):
   rc=subprocess.call(['perl','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/add_tcp_rules.pl',gm_ip])
   return rc

"""
Add UDP rules
"""
def add_udp_rules(gm_ip):
   rc=subprocess.call(['perl','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/add_udp_rules.pl',gm_ip])
   return rc

"""
Add Rate limit rules
"""
def add_rate_limit_rules(gm_ip):
   rc=subprocess.call(['perl','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/add_alert_event.pl',gm_ip])
   return rc

"""
Disable Security Category
"""
def disable_security_category(gm_ip):
   rc=subprocess.call(['perl','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/disable_security_cat.pl',gm_ip])
   return rc

"""
Enable Security Category
"""
def enable_security_category(gm_ip):
   rc=subprocess.call(['perl','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/enable_security_cat.pl',gm_ip])
   return rc

"""
Add RPZ zone
"""
def add_rpz_zone(gm_ip,tp_ip):
   rc=subprocess.call(['perl','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/add_rpz_zone.pl',gm_ip,tp_ip])
   return rc

def add_analytics_zone(gm_ip,tp_ip):
   rc=subprocess.call(['perl','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/add_analytics_zone.pl',gm_ip,tp_ip])
   return rc

"""
Add RPZ Data
"""
def add_rpz_data():
   rc=subprocess.call(['python','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/rpz_data.py'])
   return rc

"""
Add Threate Protection Data
"""
def add_threate_protection_data(member_ip):
   rc=subprocess.call(['python','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/tp_data.py',member_ip])
   return rc

"""
Modify Analytics Properties
"""
def modify_analityics_properties(gm_ip):
   rc=subprocess.call(['perl','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/modify_analityics_properties.pl',gm_ip])
   return rc

"""
Start TP Service
"""
def enable_tp_service(gm_ip):
   rc=subprocess.call(['perl','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/enable_threate_protection_service.pl',gm_ip])
   return rc

"""
Start Analytics Service
"""
def enable_analytics_service(gm_ip):
   rc=subprocess.call(['perl','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/enable_analytics_service.pl',gm_ip])
   return rc

"""
Start Discovery Service
"""
def enable_discovery_service(gm_ip,discovery_fqdn):
   rc=subprocess.call(['perl','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Discovery/enable_discovery_service.pl',gm_ip,discovery_fqdn])
   return rc

"""
Enable Forwarder and Recursion
"""
def enable_forwarder_and_recusion(gm_ip):
   rc=subprocess.call(['perl','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/enable_forwarder_and_recursion.pl',gm_ip])
   return rc

"""
Disable Forwarder and Recursion
"""
def disable_forwarder_and_recusion(gm_ip):
   rc=subprocess.call(['perl','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/disable_forwarder_and_recursion.pl',gm_ip])
   return rc

"""
Add Analytics Data
"""
def add_analityics_data(member_ip):
   rc=subprocess.call(['python','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/analityics_data.py',member_ip])
   return rc


"""
Publish Changes
"""
def publish_changes(gm_ip):
   rc=subprocess.call(['perl','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/publish_changes.pl',gm_ip])
   return rc

"""
Enable DNS and DHCP Service
"""
def restart_dns_dhcp_service(gm_ip):
   rc=subprocess.call(['perl','/import/qaddi/API_Automation/WAPI_PyTest/suites/Reporting_FR_part4/ib_data/Security/restart_service.pl',gm_ip])
   return rc


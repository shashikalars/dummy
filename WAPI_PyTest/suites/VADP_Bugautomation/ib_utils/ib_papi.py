"""
 Copyright (c) Infoblox Inc., 2016

 Modle Name  : ib_papi 
 Description : This module is used to execute PAPI utility 

"""
import subprocess
import config
import os

path="/import/qaddi/API_Automation_08_12_20/WAPI_PyTest/ib_utils"
"""
This module will add SSH keys into the box.
"""

def addkeys(gm_ip):
    rc=subprocess.call(['addkeys',gm_ip ])
    return rc


"""
This module will download Perl module from Grid master. 
"""
def download_pm(gm_ip):
    rc=subprocess.call(['getPAPI',gm_ip,'/var/tmp/InfobloxPM/'])
    return rc
"""
Enable MGMT
"""
def enable_mgmt(mgmt_ip,gm_ip=config.grid_vip):
   rc=subprocess.call(['perl',path+'/ib_data/Security/enable_mgmt.pl',mgmt_ip,gm_ip])
   return rc

"""
Upload Rulesets
"""
def upload_ruleset(gm_ip,olympic_ruleset):
   rc=subprocess.call(['perl',path+'/ib_data/Security/ruleset_upload.pl',gm_ip,olympic_ruleset])
   return rc
"""
Publish Changes
"""
def publish_changes(gm_ip):
   rc=subprocess.call(['perl',path+'/ib_data/Security/publish_changes.pl',gm_ip])
   return rc





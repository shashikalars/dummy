import os
import config
import paramiko
import pexpect
import paramiko
from paramiko import client
import subprocess



#reporting_member1_vip="10.35.110.1"
#reporting_member2_vip="10.35.140.15"
##reporting_member3_vip="10.35.110.3"
##reporting_member4_vip="10.35.110.4"

#reporting_members=[reporting_member1_vip, reporting_member2_vip]
reporting_members=[config.reporting_member1_ip, config.reporting_member2_ip]
#print(reporting_members,"\n")


def finding_reporting_search_head():
    for i in reporting_members:
        os.system("scp -pr -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@"+i+":/tmpfs/reporting_conf/ib"+" "+config.runpath)
        os.chdir("ib")
        cmd = "ls"

        returned_output = subprocess.check_output(cmd)
        #print('Looking for search head...\n', returned_output.decode("utf-8"))

        count=0
        list=['reporting_searchhead_role','reporting_indexer_role']
        total_c=len(list)

        for lt in list:
            if lt in returned_output:
                count=count+1

        #print(count)

        if count == 0 or count==1:
            os.chdir(config.runpath)
            os.system("rm -rf ib")
            continue

        elif count == total_c:
            os.chdir(config.runpath)
            os.system("rm -rf ib")
            #print("\nThe search head is "+i)
            return i

    message="Please check the grid configuration...No search head found in the grid"
    return message


def finding_indexer():

    search_head = finding_reporting_search_head()

    if search_head == config.reporting_member1_ip:
        return config.reporting_member2_ip

    elif search_head == config.reporting_member2_ip:
        return config.reporting_member1_ip


indexer = finding_indexer()
print(indexer)

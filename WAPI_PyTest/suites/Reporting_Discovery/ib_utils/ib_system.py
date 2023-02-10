import os
import time
import re
import pexpect
import sys
import pdb 
import json


#Get HW ID's
def get_hwids(pool_dir,pool_tag,hw_info_file):
    os.system("/import/tools/qa/bin/sak.pl -u -P "+pool_dir+" -T "+pool_tag+" -V ALL 'echo $UNIT_1_IPADDR:$UNIT_1_ID' > "+hw_info_file)
    print "Capturing HW informaion in "+hw_info_file+" file"
    os.system("cat "+hw_info_file)
 

#Get HW from IP Address
def get_ip2hwid(node_ip,hw_info_file,node_info):
    hw=os.popen("grep "+node_ip+" < "+hw_info_file+" | cut -d : -f 2")
    hw_id=hw.read()
    fp=open(node_info,"w")
    fp.write(hw_id) 

#moving bulk HW's into Different Network 
def system_vlanset(node_info,sub_net):
    fp = open(node_info,"r")
    hws=fp.readlines()
    fp.close()
    for hw in hws:
        hw_id=hw.rstrip()
        glh=os.popen("/import/tools/lab/bin/get_lab_info -H "+hw_id+" | grep OWNER | cut  -d = -f 2")
        owner=glh.read()
        os.system("/import/tools/lab/bin/netctl_system -H "+hw_id+" -a vlanset -c "+owner+" -S "+sub_net)

#moving single hw into different network
def vlanset(hw_id,sub_net,interface="lan"):
    glh=os.popen("/import/tools/lab/bin/get_lab_info -H "+hw_id+" | grep OWNER | cut  -d = -f 2")
    owner=glh.read()
    if owner and not owner.isspace():
        os.system("/import/tools/lab/bin/netctl_system -H "+hw_id+" -a vlanset -c "+owner+" -S "+sub_net+ " -i "+interface)
    else:
        os.system("/import/tools/lab/bin/netctl_system -H "+hw_id+" -a vlanset -S "+sub_net+ " -i "+interface)


#PowerOFF
def system_poweroff(node_info):
    fp = open(node_info,"r")
    hws=fp.readlines()
    fp.close()
    for hw in hws:
        hw_id=hw.rstrip()
        glh=os.popen("/import/tools/lab/bin/get_lab_info -H "+hw_id+" | grep OWNER | cut  -d = -f 2")
        owner=glh.read()
        os.system("/import/tools/lab/bin/reboot_system -H "+hw_id+" -a poweroff -c "+owner)

#PowerON
def system_poweron(node_info):
    fp = open(node_info,"r")
    hws=fp.readlines()
    fp.close()
    for hw in hws:
        hw_id=hw.rstrip()
        glh=os.popen("/import/tools/lab/bin/get_lab_info -H "+hw_id+" | grep OWNER | cut  -d = -f 2")
        owner=glh.read()
        os.system("/import/tools/lab/bin/reboot_system -H "+hw_id+" -a poweron -c "+owner)

#Reboot
def system_reboot(node_info):
    fp = open(node_info,"r")
    hws=fp.readlines()
    fp.close()
    for hw in hws:
        hw_id=hw.rstrip()
        glh=os.popen("/import/tools/lab/bin/get_lab_info -H "+hw_id+" | grep OWNER | cut  -d = -f 2")
        owner=glh.read()
        os.system("/import/tools/lab/bin/reboot_system -H "+hw_id+" -c "+owner)

#promote Master
def promote_master(gmc):
    #pdb.set_trace()
    clear_ssh_known_hosts()
    proc=pexpect.spawn("ssh admin@"+gmc)
    fout=open("promote_master.log","w")
    proc.logfile_read=fout
    try:
        index=proc.expect(["admin.*password:.*","Are you sure you want to continue connecting.*"],timeout=60)
        if index == 1:
            proc.sendline("yes")
            time.sleep(5)
        proc.sendline("infoblox")
        proc.expect(r"Infoblox >")
        proc.sendline("set promote_master")
        proc.expect(r"Do you want a delay between notification to grid members.*")
        proc.sendline("n")
        index1=proc.expect(["Are you sure you want to do this.*","Please enter.*without changing primary reporting site.*"],timeout=60)
        if index1 == 0:
            time.sleep(2)
            proc.sendline("y")
            time.sleep(4)
        if index1 == 1:
            proc.sendline("c")
            proc.expect(r"Are you sure you want to do this.*")
            proc.sendline("y")
            time.sleep(4)
        proc.expect(r".*Are you really sure you want to do this.*")
        time.sleep(4)
        proc.sendline("y")
        proc.sendline("y")
    except pexpect.TIMEOUT:
        print "Looks like promote master failed"

#HA FO & Reboot 
def node_reboot(node_ip):
    clear_ssh_known_hosts()
    proc=pexpect.spawn("ssh admin@"+node_ip)
    fout=open("node_reboot.log","w")
    proc.logfile_read=fout
    try:
        index=proc.expect(["admin.*password:.*","Are you sure you want to continue connecting.*"],timeout=30)
        if index == 1:
            proc.sendline("yes")
            time.sleep(5)
        proc.sendline("infoblox")
        proc.expect(r"Infoblox >")
        proc.sendline("reboot")
        proc.expect(".*REBOOT THE SYSTEM.*")
        time.sleep(4)
        proc.sendline("y")
    except pexpect.TIMEOUT:
        print "FO or Reboot operation is not completed"

#Product Restart
def node_restart(node_ip):
#    pdb.set_trace()
    clear_ssh_known_hosts()
    proc=pexpect.spawn("ssh root@"+node_ip)
    fout=open("node_product_restart.log","w")
    proc.logfile_read=fout
    try:
        index=proc.expect(["-bash.*","Are you sure you want to continue connecting.*"],timeout=60)
        if index == 1:
            proc.sendline("yes")
            proc.expect(r".*bash.*")
            time.sleep(5)
        if index == 0:
            time.sleep(5)
        proc.sendline("/infoblox/rc restart")
        time.sleep(10)
        proc.sendline("")
        proc.sendline("")
    except pexpect.TIMEOUT:
        print "Product Restart operation is not completed"

#System Restart,stored ips in node_info.ip
def system_restart(node_info):
    fp = open(node_info+".ip","r")
    ips=fp.readlines()
    fp.close()
    for node in ips:
        node_ip=node.rstrip()
        node_restart(node_ip)


#Add Reporting License.
def reporting_license(hw_id,lic_type,capacity,node_ip):
    glh=os.popen("/import/tools/lab/bin/get_lab_info -H "+hw_id+" | grep OWNER | cut  -d = -f 2")
    owner=glh.read().rstrip()
    rl=os.popen("/import/tools/lab/bin/request_license -H "+hw_id+"  -c "+owner+" -p "+lic_type+" -n "+capacity+" | grep LICENSE")
    line=rl.read()
    license=re.sub('LICENSE=','', line.rstrip())
    flag=0
    clear_ssh_known_hosts()
    proc=pexpect.spawn("ssh admin@"+node_ip)
    fout=open("report_license.log","w")
    proc.logfile_read=fout
    try:
        index=proc.expect(["admin.*password:.*","Are you sure you want to continue connecting.*"],timeout=60)
        if index == 1:
            proc.sendline("yes")
            time.sleep(5)
        proc.sendline("infoblox")
        proc.expect(r"Infoblox >")
        proc.sendline("set license")
        proc.expect(r"Enter license string.*")
        proc.sendline(license)
        proc.expect(r"Install license.*")
        proc.sendline("y")
        proc.expect(r"Infoblox >")
    except pexpect.TIMEOUT:
        print "Looks like promote master failed"
    fout.close()
    searchfile = open("report_license.log", "r")
    rc=1
    for line in searchfile:
        if "License is installed" in line:
            print line
            rc=0
        elif "License conflict. License is not installed." in line:
            print line
            rc=1
    searchfile.close()
    return rc

def clear_ssh_known_hosts():
    home_dir=os.environ['HOME']
    os.system("rm -rf "+home_dir+"/.ssh/known_hosts")

def enable_port(node_ip,port):
    fin=os.system("ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null 2>/dev/null root@"+node_ip+" iptables -I INPUT -p tcp --dport "+port+" -j ACCEPT")

MSG="""
Looks like test case got failed. If Yes then Please check the following.
1.Input JSON Content is matching with 'Search Results' except '_time' attribute?
 a.Check the Time zone, Time Zone should be UTC.
 b.Make Sure you have not configured Grid 24 hours before, (i.e. for Minute Group Detail Reports, Initially  time difference between  search events  will be  1min  and after some time it will become 5 min)
2.Trend report?  Then make sure you have not executed reports more than two times.
3.Reports may fail due to some other influence (DHCP events, DNS Query events etc.,)
4.Make sure all Grid Members are online (System reported are validated against all Members )
5.Some reports may fails due to slowness of VM(Example: CPU reports will fail due to slowness of Forwarder)
6.Check Configuration setup(example for DCVM DC HW should be configured in preparation)
7.Make sure PORT is opened for the following. (PORT may be disabled  if  Indexer/Grid Master gets rebooted)
  a. 8089 for Single Indexer in Indexer
  b. 7089 for Clustering  in Grid Master
8.  For Multi-Site Cluster Mode, Please make sure Primary-Site Reporting Members are up and running.

Note:
1.Currently framework is not designed for 'Concurrent/Parallel' execution. So test cases may fail if user manually execute py.test & search.py  when Jenkin Job is under execution.
2.Test cases may fail due data conflict (i.e., make sure newly implemented suites are not causing any issues)
3.'DELTA' in 'compare_results' method is used for compare the values in between range, for example if input_value=10 & delta=5  then search result will be considered as pass when value between 5 and 15. 
"""

def search_dump(file_name,search_input,search_output):
    d='dumps'
    if not os.path.exists(d):
        os.makedirs(d)
    output1=json.dumps(search_input, sort_keys=True, indent=4, separators=(',', ': '))
    output2=json.dumps(search_output, sort_keys=True, indent=4, separators=(',', ': '))  
    fp =open(d+"/"+file_name, "w")
    fp.write(MSG)
    fp.write("\n\n")
    fp.write('-'*25+"Input Data"+'-'*25)
    fp.write(output1)
    fp.write('-'*25+"Search Results"+'-'*25)
    fp.write(output2)
    fp.close()

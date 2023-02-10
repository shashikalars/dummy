import os
import config
import subprocess
import sys
from time import sleep

key =sys.argv[1]

cmd="grep 'host=10.' ~/.splunkrc"

host=subprocess.check_output(cmd,shell=True)
print host


search_head_ip=host.strip("host=\n")
print("search_head_ip is "+ search_head_ip)

# find_search_head="python fetch_search_head_indexer.py search_head "+config.reporting_member1_ip:config.reporting_member2_ip
# search_head_ip=subprocess.check_output(cmd,shell=True)
# search_head_ip=search_head_ip.strip("\n")
# print("search head is "+search_head_ip)

# finding indexer ip
if search_head_ip == config.reporting_member1_ip:
        indexer_ip=config.reporting_member2_ip

elif search_head_ip == config.reporting_member2_ip:
        indexer_ip=config.reporting_member1_ip

print ("indexer is "+indexer_ip)


### identifying vmid of search_head
cmd="identify_lab_unit " + search_head_ip
output=subprocess.check_output(cmd,shell=True)
print(output)
new_output=output.split(" ")
vm_id=new_output[-1].strip(".\n")
print(vm_id)

# powering on search_head
print("Powering on search head...")
os.system("reboot_system -H "+vm_id+" -a poweron")


### identifying vmid of indexer
cmd="identify_lab_unit " + indexer_ip
output=subprocess.check_output(cmd,shell=True)
print(output)
new_output=output.split(" ")
vm_id=new_output[-1].strip(".\n")
print(vm_id)

# powering on indexer
print("Powering on indexer...")
os.system("reboot_system -H "+vm_id+" -a poweron")

sleep(30)


if key=='single':
    cmd="python fetch_search_head_indexer.py search_head "+config.reporting_member1_ip+":"+config.reporting_member2_ip
elif key=='multi':
    cmd="python fetch_search_head_indexer.py search_head "+config.reporting_member1_ip+":"+config.reporting_member2_ip+":"+config.reporting_member3_ip+":"+config.reporting_member4_ip


new_search_head_ip=subprocess.check_output(cmd,shell=True)
new_search_head_ip=new_search_head_ip.strip("\n")
print("new search head is "+new_search_head_ip)

os.system("sed -i 's/host="+search_head_ip+"/host="+new_search_head_ip+"/g'  ~/.splunkrc")


import os
import config
import subprocess
from time import sleep

cmd="grep 'host=10.' ~/.splunkrc"

host=subprocess.check_output(cmd,shell=True)
print host


search_head_ip=host.strip("host=\n")
print("search_head_ip is "+ search_head_ip)

# finding indexer ip

if search_head_ip == config.reporting_member1_ip:
        indexer_ip=config.reporting_member2_ip

elif search_head_ip == config.reporting_member2_ip:
        indexer_ip=config.reporting_member1_ip

print ("indexer is "+indexer_ip)

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


### identifying vmid of search_head

cmd="identify_lab_unit " + search_head_ip
output=subprocess.check_output(cmd,shell=True)
print(output)

new_output=output.split(" ")
vm_id=new_output[-1].strip(".\n")
print(vm_id)

# shutting down search head
print("Shutting down Search head...")
os.system("reboot_system -H "+vm_id+" -a poweroff")
sleep(900)

os.system("sed -i 's/host="+search_head_ip+"/host="+indexer_ip+"/g'  ~/.splunkrc")


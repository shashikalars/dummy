import pexpect
import os
import sys
import time
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS

dc_server=sys.argv[1]
master=sys.argv[2]
dc_user=sys.argv[3] #"auto"
dc_pass=sys.argv[4] # "auto123"

# Enabling registration for DCVM

get_ref = ib_NIOS.wapi_request('GET', object_type="datacollectioncluster", grid_vip=master)
print(get_ref)
res = json.loads(get_ref)
print(res)
print(res[0]['_ref'])

data = {"enable_registration": True}
response = ib_NIOS.wapi_request('PUT', ref=res[0]['_ref'], fields=json.dumps(data), grid_vip=master)
print(response)


# Enabling DNS queries and responses
# Setting up file transfer

get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns", grid_vip=master)
print(get_ref)
res = json.loads(get_ref)
print(res)
print(res[0]['_ref'])

capture_dns = {"enable_capture_dns_queries": True, "enable_capture_dns_responses": True, "capture_dns_queries_on_all_domains": True, "file_transfer_setting":{"directory": "~","host": dc_server,"port": 22,"type": "SCP","username":dc_user,"password":dc_pass}}
response = ib_NIOS.wapi_request('PUT', ref=res[0]['_ref'], fields=json.dumps(capture_dns), grid_vip=master)
print(response)


print("Restart DNS Services")
grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=master)
ref = json.loads(grid)[0]['_ref']
data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=master)
sleep(20)


proc=pexpect.spawn("ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@"+dc_server+" -p 2020")
#fout=open("dumps/dcvm_register.log","w")
fout=open("dcvm_register.log","w")
proc.logfile_read=fout

try:
        #index=proc.expect(["admin.*password:","Are you sure you want to continue connecting.*"],timeout=30)
        #if index == 1:
            #proc.sendline("yes") 
            #time.sleep(5)
    proc.expect(r"admin.*password:")
    proc.sendline("infoblox")
    print("1")
    #index1=proc.expect("Do you want to start wizard? y/n [y]:.*")
    proc.expect("Infoblox Data Connection Virtual Machine.*")
    proc.expect("Do you want to start wizard?.*")
    proc.sendline("n\r")
    print("2")
    #proc.sendline("n")
    proc.expect(r">")    
    proc.sendline("data source scp")
    proc.expect(r"data.source.scp >")
    proc.sendline("user add "+dc_user)
    proc.expect(r"Enter password for user .*:")
    proc.sendline(dc_pass)
    proc.expect(r"Enter again:")
    proc.sendline(dc_pass)
    proc.expect(r"data.source.scp >")
    proc.sendline("exit")
    proc.sendline("data_source_grid")
    proc.expect(r"data.source.grid >")
    proc.sendline("address set "+master)
    proc.expect(r"data.source.grid >")
    proc.sendline("username set admin")
    proc.expect(r"data.source.grid >")
    proc.sendline("password")
    proc.expect(r"Enter the NIOS admin's password:")
    proc.sendline("infoblox")
    proc.expect(r"Enter again:")
    proc.sendline("infoblox")
    proc.expect(r"data.source.grid >")
    proc.sendline("exit")
    proc.sendline("data_destination_reporting_registration")
    proc.expect(r"data.destination.reporting.registration >")  
    proc.sendline("register")
    sleep(60)
    proc.sendline("exit")
    proc.sendline("data destination reporting")
    proc.expect(r"data.destination.reporting >")
    proc.sendline("mode set forward")
    proc.expect(r"data.destination.reporting >")
    proc.sendline("mode")
    proc.expect(r"data.destination.reporting >")
    proc.sendline("exit")
except pexpect.TIMEOUT:
	print "Looks like DC vm is not joined"
fout.close()
        


        


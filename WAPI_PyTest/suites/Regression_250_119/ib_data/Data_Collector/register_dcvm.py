import pexpect
import os
import sys
import time
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import config
import json


dc_server=sys.argv[1]
master=sys.argv[2]
dc_user=sys.argv[3] #"auto"
dc_pass=sys.argv[4] # "auto123"

get_ref = ib_NIOS.wapi_request('GET', object_type="datacollectioncluster", grid_vip=master)
print(get_ref)
res = json.loads(get_ref)
print(res)
print(res[0]['_ref'])

data = {"enable_registration": True}
response = ib_NIOS.wapi_request('PUT', ref=res[0]['_ref'], fields=json.dumps(data), grid_vip=master)
print(response)


	
proc=pexpect.spawn("ssh admin@"+dc_server+" -p 2020")
#fout=open("dumps/dcvm_register.log","w")
fout=open("dcvm_register.log","w")
proc.logfile_read=fout

try:
        index=proc.expect(["admin.*password:","Are you sure you want to continue connecting.*"],timeout=30)
        if index == 1:
	    proc.sendline("yes") 
            time.sleep(5)
#       proc.expect(r"admin.*password:")
	proc.sendline("infoblox")
        index1=proc.expect(["Do you want to start wizard? y/n [y]:.*",">"])
        if index1 == 0:
            proc.sendline("n")
	proc.sendline("data_input_scp")
	proc.expect(r"data.input.scp >")
	proc.sendline("users add "+dc_user)
#       proc.expect(r"Enter password for user" +dc_user+":")
	proc.expect(r"Enter password for user .*:")
	proc.sendline(dc_pass)
	proc.expect(r"Enter again:")
	proc.sendline(dc_pass)
	proc.expect(r"data.input.scp >")
	proc.sendline("exit")
	proc.sendline("data_input_grid")
	proc.expect(r"data.input.grid >")
	proc.sendline("address set "+master)
	proc.expect(r"data.input.grid >")
	proc.sendline("username set admin")
	proc.expect(r"data.input.grid >")
	proc.sendline("password")
	proc.expect(r"Enter the NIOS admin's password:")
	proc.sendline("infoblox")
	proc.expect(r"Enter again:")
	proc.sendline("infoblox")
	proc.expect(r"data.input.grid >")
        proc.sendline("exit")
        proc.sendline("data_output_reporting_registration")
        proc.expect(r"data.output.reporting.registration >")  
	proc.sendline("register")
        sleep(60)
	proc.sendline("exit")
        proc.sendline("data_output_reporting >")  
        proc.expect(r"data.output.reporting >")
        proc.send("mode set forward") 
        proc.send("mode")
        proc.sendline("exit")
except pexpect.TIMEOUT:
	print "Looks like DC vm is not joined"
fout.close()
        


        


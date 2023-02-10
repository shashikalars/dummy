import pexpect
import os
import sys
from time import sleep
dc_server=sys.argv[1]
master=sys.argv[2]
dc_user="auto"
dc_pass="auto123"
	
proc=pexpect.spawn("ssh admin@"+dc_server+" -p 2020")
fout=open("../../dumps/dcvm_unregister.log","w")
proc.logfile_read=fout

try:
        index=proc.expect(["admin.*password:","Are you sure you want to continue connecting.*"],timeout=30)
        if index == 1:
            proc.sendline("yes")
            time.sleep(5)
	proc.sendline("infoblox")
	proc.expect(r">")
        proc.sendline("data_input_scp")
        proc.expect(r"data.input.scp >")
        proc.sendline("users del "+dc_user)
        proc.expect(r"data.input.scp >")
        proc.sendline("exit")
        #proc.expect(r"data.input >")
        #proc.sendline("exit")
        #proc.expect(r"data >")
        #proc.sendline("exit")
        proc.expect(r" > ")
	proc.sendline("data_output_reporting")
	proc.expect(r"data.output.reporting >")
	proc.sendline("mode set disabled")
	proc.expect(r"data.output.reporting >")
	proc.sendline("registration")
	proc.expect(r"data.output.reporting.registration >")
	proc.sendline("unregister")
        sleep(5)  
        proc.sendline("exit")
except pexpect.TIMEOUT:
	print "Looks like DC vm is not unregistered"
fout.close()

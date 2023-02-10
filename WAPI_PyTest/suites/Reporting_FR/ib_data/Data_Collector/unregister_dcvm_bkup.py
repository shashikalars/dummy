import pexpect
import os
import sys
import time
dc_server=sys.argv[1]
master=sys.argv[2]
dc_user="auto"
dc_pass="auto123"
	
proc=pexpect.spawn("ssh admin@"+dc_server+" -p 2020")
fout=open("dumps/dcvm_unregister.log","w")
proc.logfile_read=fout

try:
        index=proc.expect(["admin.*password:","Are you sure you want to continue connecting.*"],timeout=30)
        if index == 1:
            proc.sendline("yes")
            time.sleep(5)
	proc.sendline("infoblox")
	proc.expect(r">")
	proc.sendline("input")
	proc.expect(r"input >")
	proc.sendline("scp")
	proc.expect(r"input.scp >")
	proc.sendline("users del "+dc_user)
	proc.expect(r"input.scp >")
	proc.sendline("exit")
	proc.expect(r"input >")
	proc.sendline("exit")
	proc.expect(r">")
	proc.sendline("grid")
	proc.expect(r"grid >")
	proc.sendline("unregister")
	proc.expect(r"grid >")
        proc.sendline("exit")
        proc.expect(r">")
        proc.sendline("exit")
except pexpect.TIMEOUT:
	print "Looks like DC vm is not unregistered"
fout.close()

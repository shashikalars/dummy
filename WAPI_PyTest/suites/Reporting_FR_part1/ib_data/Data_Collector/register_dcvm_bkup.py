import pexpect
import os
import sys
import time
dc_server=sys.argv[1]
master=sys.argv[2]
dc_user=sys.argv[3] #"auto"
dc_pass=sys.argv[4] # "auto123"
	
proc=pexpect.spawn("ssh admin@"+dc_server+" -p 2020")
#fout=open("dumps/dcvm_register.log","w")
fout=open("dcvm_register.log","w")
proc.logfile_read=fout

try:
        index=proc.expect(["admin.*password:","Are you sure you want to continue connecting.*"],timeout=30)
        if index == 1:
	    proc.sendline("yes") 
            time.sleep(5)
#        proc.expect(r"admin.*password:")
	proc.sendline("infoblox")
        index1=proc.expect(["Please type 'q' to quit, or Enter to continue.*",">"])
        if index1 == 0:
            proc.sendline("q")
#	proc.expect(r">")
	proc.sendline("input")
	proc.expect(r"input >")
	proc.sendline("scp")
	proc.expect(r"input.scp >")
	proc.sendline("users add "+dc_user)
	proc.expect(r"Enter password:")
	proc.sendline(dc_pass)
	proc.expect(r"Enter again:")
	proc.sendline(dc_pass)
	proc.expect(r"input.scp >")
	proc.sendline("exit")
	proc.expect(r"input >")
	proc.sendline("exit")
	proc.expect(r">")
	proc.sendline("grid")
	proc.expect(r"grid >")
	proc.sendline("address set "+master)
	proc.expect(r"grid >")
	proc.sendline("username set admin")
	proc.expect(r"grid >")
	proc.sendline("password")
	proc.expect(r"Enter the NIOS admin's password:")
	proc.sendline("infoblox")
	proc.expect(r"Enter again:")
	proc.sendline("infoblox")
	proc.expect(r"grid >")
	proc.sendline("register")
	proc.expect(r"grid >")
	proc.sendline("exit")
	proc.expect(r">")
	proc.sendline("exit")
except pexpect.TIMEOUT:
	print "Looks like DC vm is not joined"
fout.close()
        


        


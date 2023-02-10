import os
import sys
name=sys.argv[1]
group=sys.argv[2]
ipb=sys.argv[3]
print(name)
fp=open(name,"w")
fp.write("header-ipblockgroup,name*,_new_name,comment\n")
fp.write("header-ipblock,address_string*,_new_address_string,group*,_new_group,comment\n")
fp.write("ipblockgroup,"+group+",,Reporting Automation\n")
L=ipb.split(",")
for ip in L:
    fp.write("ipblock,"+ip+",,"+group+",,Reporting Automation\n")


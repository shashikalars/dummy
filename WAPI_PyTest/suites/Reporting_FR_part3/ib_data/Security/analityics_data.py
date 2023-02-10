import os
import sys
member_ip=sys.argv[1]

for i in range(1,5):
	cmd = "dig +retry=0 +timeout=0 \@" + member_ip
	cmd1 = " 100R02."+ str(i)+ ".down.sshdns.com txt +tcp"
	cmd2 = " 100R02."+ str(i)+ ".abcdefghijklmnopqrstuvwxyz1234.abcdefghijklmnopqrstuvwxyz1234.abcdefghijklmnopqrstuvwxyz1234.abcdefghijklmnopqrstuvwxyz1234 txt +tcp"
   	cmd3 = " 100R02."+ str(i)+ ".abcdefghijklmnopqrstuvwxyz1234abcdefghijklmnopqrstuvwxyz1234.abcdefghijklmnopqrstuvwxyz1234abcdefghijklmnopqrstuvwxyz1234 txt +tcp"
	cmd4 = " 100R02."+ str(i)+ ".abcdefghijklmnopqrstuvwxyz1234abcdefghijklmnopqrstuvwxyz1234123.abcdefghijklmnopqrstuvwxyz1234abcdefghijklmnopqrstuvwxyz1234123 txt +tcp"
	cmd5 = " 100R02."+ str(i)+ ".gu.abcdefghijklmnopqrstuvwxyz1234abcdefghijklmnopqrstuvwxyz1234123.abcdefghijklmnopqrstuvwxyz1234abcdefghijklmnopqrstuvwxyz1234123 txt +tcp"
	cmd6 = " 100R02."+ str(i)+ ".any.knjuqljsfyyc2t.com txt +tcp"
	cmd7 = " 100R02."+ str(i)+ ".ntsc0yljat.com txt +tcp"
	cmd8 = " 100R02."+ str(i)+ ".aaaaaaaaa1234567890123456789012345678.aebabaaaaa txt +tcp"
	cmd9 = " 100R02."+ str(i)+ ".up.sshdns.com txt +tcp"
	cmd10 = " 100R02."+ str(i)+ ".aabbccddeeffgghhiijjkkllmmnnooppqqrrssttuuvvwwxxyy.abc txt +tcp"
	cmd11 = " 100R02."+ str(i)+ ".aaa.=auth.abc txt +tcp"
	cmd12 = " 100R02."+ str(i)+ ".aaa.=connect.abc txt +tcp"
        os.system(cmd + cmd1 +"> /dev/null 2>&1")
	os.system(cmd + cmd2 +"> /dev/null 2>&1")
        os.system(cmd + cmd3 +"> /dev/null 2>&1")
        os.system(cmd + cmd4 +"> /dev/null 2>&1")
        os.system(cmd + cmd5 +"> /dev/null 2>&1")
        os.system(cmd + cmd6 +"> /dev/null 2>&1")
        os.system(cmd + cmd7 +"> /dev/null 2>&1")
        os.system(cmd + cmd8 +"> /dev/null 2>&1")
        os.system(cmd + cmd9 +"> /dev/null 2>&1")
        os.system(cmd + cmd10 +"> /dev/null 2>&1")
        os.system(cmd + cmd11 +"> /dev/null 2>&1")
        os.system(cmd + cmd12 +"> /dev/null 2>&1")

for x in range(0,66):
    os.system("dig @"+member_ip+" passdn.com"+"> /dev/null 2>&1")
for x in range(0,64):
    os.system("dig @"+member_ip+" blocdnnd.com"+"> /dev/null 2>&1")
for x in range(0,62):
    os.system("dig @"+member_ip+" blockdn.com"+"> /dev/null 2>&1")
for x in range(0,60):
    os.system("dig @"+member_ip+" g.com"+"> /dev/null 2>&1")
for x in range(0,58):
    os.system("dig @"+member_ip+" asm"+"> /dev/null 2>&1")
print "Query successfull"

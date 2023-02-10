import os
import sys
member_ip=sys.argv[1]


os.system("dnsq -ns="+member_ip+" -qname=info-udp.com" +"> /dev/null 2>&1")
os.system("dnsq -ns="+member_ip+" -qname=war-udp.com" +"> /dev/null 2>&1")
os.system("dnsq -ns="+member_ip+" -qname=maj-udp.com" +"> /dev/null 2>&1")
os.system("dnsq -ns="+member_ip+" -qname=cri-udp.com" +"> /dev/null 2>&1")

os.system("dnsq -ns="+member_ip+" -qname=info-tcp.com -protocol=tcp" +"> /dev/null 2>&1")
os.system("dnsq -ns="+member_ip+" -qname=war-tcp.com -protocol=tcp" +"> /dev/null 2>&1")
os.system("dnsq -ns="+member_ip+" -qname=maj-tcp.com -protocol=tcp" +"> /dev/null 2>&1")
os.system("dnsq -ns="+member_ip+" -qname=cri-tcp.com -protocol=tcp" +"> /dev/null 2>&1")
os.system("dnsq -ns="+member_ip+" -qname=rudp.com -repeat=3 -wait=0.03" +"> /dev/null 2>&1")

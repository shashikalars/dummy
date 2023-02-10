import sys
ip = sys.argv[1]
ip = ip.replace('0000:0000:0000:000',':')
ip = ip.replace('010A','10A')
ip = ip.lower()
print ip

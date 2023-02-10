import os
fp=open("15k.txt","wb")
for i in range(15000):
    fp.write("frec"+str(i)+".dns_top_clients.com A\n")
fp.close()


import os
import config
import paramiko
import pexpect
import paramiko
from paramiko import client
import subprocess
import sys

key =sys.argv[1]
rep =sys.argv[2]

reporting_members=rep.split(':')


def search_head():
    for i in reporting_members:
        os.system("scp -pr -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@"+i+":/tmpfs/reporting_conf/ib"+" /tmp")
        returned_output = os.listdir("/tmp/ib")
        with open('/tmp/ib/reporting_status.txt') as text:
                status=text.readlines()
        #print(status)
        os.system("rm -rf /tmp/ib")

        if status==['searchhead OK\n']:
                return i
        else:
                continue

    message="No search head found...Please check the grid configuration!"
    print message



def indexer():
    for i in reporting_members:
        os.system("scp -pr -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@"+i+":/tmpfs/reporting_conf/ib"+" /tmp")
        returned_output = os.listdir("/tmp/ib")
        with open('/tmp/ib/reporting_status.txt') as text:
                status=text.readlines()
        #print(status)
        os.system("rm -rf /tmp/ib")

        if status==['searchhead OK\n']:
                reporting_members.remove(i)
                return reporting_members

        else:
                continue

    message="No indexers found...Please check the grid configuration!"
    print message



if key=="search_head":
    search_head=search_head()
    print(search_head)


elif key=="indexer":
    indexers=[]
    indexer=indexer()
    all_indexers=':'.join(indexer)
    print(all_indexers)

elif key=="indexer1":
    indexers=[]
    indexer=indexer()
    #all_indexers=':'.join(indexer)
    print(indexer[0])

elif key=="indexer2":
    indexers=[]
    indexer=indexer()
    #all_indexers=':'.join(indexer)
    print(indexer[1])
    
elif key=="indexer3":
    indexers=[]
    indexer=indexer()
    #all_indexers=':'.join(indexer)
    print(indexer[2])


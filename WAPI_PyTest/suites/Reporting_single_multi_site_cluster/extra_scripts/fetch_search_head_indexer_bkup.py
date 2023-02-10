import os
import subprocess
import sys

key =sys.argv[1]
rep =sys.argv[2]

reporting_members=rep.split(':')
# print key
# print reporting_members[0]    #reporting_member1
# print reporting_members[1]    #reporting_member2


def search_head():
    for i in reporting_members:
        os.system("scp -pr -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@"+i+":/tmpfs/reporting_conf/ib"+" /tmp")
        returned_output = os.listdir("/tmp/ib")
        os.system("rm -rf /tmp/ib")

        if ('reporting_searchhead_role' in returned_output) and ('reporting_indexer_role' in returned_output):
            #print("Search head is"+i)
            return i
        else:
            continue

    message="No search head found...Please check the grid configuration!"
    print message


def indexer():
    for i in reporting_members:
        os.system("scp -pr -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@"+i+":/tmpfs/reporting_conf/ib"+" /tmp")
        returned_output = os.listdir("/tmp/ib")
        os.system("rm -rf /tmp/ib")

        if ('reporting_indexer_role' in returned_output) and ('reporting_searchhead_role' not in returned_output):
            #print("indexer is "+i)
            return i

        else:
            continue

    message="No indexer found...Please check the grid configuration!"
    print message



if key=="search_head":
    search_head=search_head()
    print search_head


elif key=="indexer":
    indexer=indexer()
    print indexer


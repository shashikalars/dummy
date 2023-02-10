import subprocess
import json
import ConfigParser
import ib_NIOS
import os
import re
import time

Main_CONF="/root/Reporting_Test_Cases/Reporting_FR/reporting_conf.ini"
parser = ConfigParser.SafeConfigParser()
parser.read(Main_CONF)

#json_file = 
indexer_ip ="10.35.119.5"
grid_ip ="10.35.119.9"
grid_fqdn ="ib-10-35-119-9.infoblox.com"
data = {"members":[{"_struct": "dhcpmember", "ipv4addr": grid_ip,"name":grid_fqdn}], \
"network": "10.0.0.0/8", "network_view": "default"}
response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data))
data = {"members":[{"_struct": "dhcpmember", "ipv4addr": grid_ip,"name": grid_fqdn}], \
"network": "41.0.0.0/24", "network_view": "default"}
response = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(data))
range_obj = {"start_addr":"41.0.0.1","end_addr":"41.0.0.100","member":{"_struct": "dhcpmember","ipv4addr":grid_ip,"name": grid_fqdn}, \
"options":[{"_struct": "dhcpoption","name":"dhcp-lease-time","num": 51,"use_option": True,"value": "120","vendor_class": "DHCP"}]}
range = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(range_obj))
#range_obj = {"name":"ssn","networks":}
network_ref_list = []
network_10 = ib_NIOS.wapi_request('GET', object_type="network?network~=10.0.0.0/8")
ref10 = json.loads(network_10)[0]['_ref'] 
network_ref_list.append({"_ref":ref10})
network_41 = ib_NIOS.wapi_request('GET', object_type="network?network~=41.0.0.0/24")
ref41 = json.loads(network_41)[0]['_ref']  
network_ref_list.append({"_ref":ref41})
range_obj = {"name":"sharednetworks","networks":network_ref_list}
shared = ib_NIOS.wapi_request('POST', object_type="sharednetwork", fields=json.dumps(range_obj))
time.sleep(65)
cmd="sudo /import/tools/qa/tools/dras_opt55/dras outfile.txt -n 50 -i "+grid_ip+" -w -D -O 55:010304060F"
os.system(cmd)
cmd1="sudo /import/tools/qa/tools/dras_opt55/dras outfile.txt -n 10 -i "+grid_ip+" -w -D -O 55:0103060c0f1c"
os.system(cmd1)
cmd2="sudo /import/tools/qa/tools/dras_opt55/dras outfile.txt -n 5 -i "+grid_ip+" -w -D -O 55:01030f062b4d"
os.system(cmd2)
cmd3="sudo /import/tools/qa/tools/dras_opt55/dras outfile.txt -n 8 -i "+grid_ip+" -w -D -O 55:0103060204070f2a"
os.system(cmd3)
cmd4="sudo /import/tools/qa/tools/dras_opt55/dras outfile.txt -n 5 -i "+grid_ip+" -w -D -O 55:01031c064296"
os.system(cmd4)
cmd5="sudo /import/tools/qa/tools/dras_opt55/dras outfile.txt -n 5 -i "+grid_ip+" -w -D -O 55:0103060f78727d"
os.system(cmd5)
cmd6="sudo /import/tools/qa/tools/dras_opt55/dras outfile.txt -n 5 -i "+grid_ip+" -w -D -O 55:36333a3b0103060f1c" 
os.system(cmd6)
cmd7="sudo /import/tools/qa/tools/dras_opt55/dras outfile.txt -n 5 -i "+grid_ip+" -w -D -O 55:011c42060f0323b0"
os.system(cmd7)
cmd8="sudo /import/tools/qa/tools/dras_opt55/dras outfile.txt -n 4 -i "+grid_ip+" -w -D -O 55:0103062a2b0242"
os.system(cmd8)
cmd9="sudo /import/tools/qa/tools/dras_opt55/dras outfile.txt -n 4 -i "+grid_ip+" -w -D -O 55:0103060c0f2a424378"   
os.system(cmd9)
delshared = ib_NIOS.wapi_request('GET', object_type="sharednetwork?name~=sharednetworks")
ref = json.loads(delshared)[0]['_ref']
del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)
delnetwork = ib_NIOS.wapi_request('GET', object_type="network?network~=10.0.0.0/8")
ref = json.loads(delnetwork)[0]['_ref']
del_status = ib_NIOS.wapi_request('DELETE', object_type = ref)
delnetwork = ib_NIOS.wapi_request('GET', object_type="network?network~=41.0.0.0/24")
ref_40 = json.loads(delnetwork)[0]['_ref']
data = {"disable":True}
del_status = ib_NIOS.wapi_request('PUT',object_type=ref_40,fields=json.dumps(data))    

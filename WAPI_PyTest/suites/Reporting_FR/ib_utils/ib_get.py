#!/usr/bin/python
import os
import time
import re

"""
Method is used to get indexer date
    1. current indexer date by calling "indexer_date(indexer_ip)"  method.
    2. Future date, say 'current time'  + sec.
    3. Past Date, say 'current time' -  sec.
    4. Also user can round off time in minutes (5,10 etc., ) 
       Example : 
           if current time is '2016-06-08T19:04:00.000+00:00' then 
            '2016-06-08T19:04:00.000+00:00'  for  indexer_date(indexer_ip)
	    '2016-06-08T19:14:00.000+00:00'  for  indexer_date(indexer_ip,600)      >>> 10 min ahead time 
	    '2016-06-08T19:54:00.000+00:00'  for  indexer_date(indexer_ip,-600)     >>> 10 min past time
	    '2016-06-08T19:50:00.000+00:00'  for  indexer_date(indexer_ip,-600,10)  >>> 10 min past with roundoff 
"""

def indexer_date(indexer_ip,sec=0,minute_round_off=1):
    fin=os.popen("ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null 2>/dev/null root\@"+indexer_ip+" date +%s")
    epoc = fin.readline().rstrip()
    new_epoc = int(epoc) + int(sec)
    minute=int(time.strftime('%M',time.gmtime(new_epoc)))
    nm = minute - ( minute % minute_round_off)
    new_minute= '0'+str(nm) if nm <=9 else str(nm) #'00' format
    new_time = time.strftime('%Y-%m-%dT%H', time.gmtime(new_epoc))
    time_stamp=new_time+":"+str(new_minute)+":00.000+00:00"
    return(time_stamp)



"""
Need's to remove following module
def indexer_date(indexer_ip):
    fin=os.popen("ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null 2>/dev/null root\@"+indexer_ip+" date +%Y-%m-%dT%H:%M")
    system_date = fin.readline().rstrip()
    system_date = system_date+":00.000+00:00"
    return system_date

def custom_time(member,sec,minute_round_off=1):
    epoc=indexer_epoch_time(member)
    new_epoc = int(epoc) + int(sec) 
    minute=int(time.strftime('%M',time.gmtime(new_epoc)))
    nm = minute - ( minute % minute_round_off)
    new_minute= '0'+str(nm) if nm <=9 else str(nm) #'00' format
    new_time = time.strftime('%Y-%m-%dT%H', time.gmtime(new_epoc))
    time_stamp=new_time+":"+str(new_minute)+":00.000+00:00"
    return(time_stamp)
"""


"""
Method is to get indexer epoc time.
"""
def indexer_epoch_time(indexer_ip):
    fin=os.popen("ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null 2>/dev/null root\@"+indexer_ip+" date +%s")
    system_date = fin.readline().rstrip()
    return system_date



"""
Method is find DNS latency  
"""
def latency(ip):
    fin= os.popen ("ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null 2>/dev/null root\@"+ip+" dig @127.0.0.1 0.0.127.in-addr.arpa in ns | grep time")
    record = fin.readline().rstrip()
    latency = re.findall('\d+',record)
    return latency[0]
"""
Fetch CPU Utilization through SNMP, Assuming community string 'public' is added.
"""
def member_cpu_utilization(member_ip):
    fin= os.popen ("snmpget -v2c -c public -m all "+member_ip+" .1.3.6.1.4.1.7779.3.1.1.2.1.10.1.3.43")
    record = fin.readline().rstrip()
    cpu_usage = re.findall('CPU Usage: (\d+)%',record)
    return cpu_usage[0]


"""
Fetch Memory Utilization through SNMP, Assuming community string 'public' is added.
"""
def member_memory_utilization(member_ip):
    fin= os.popen ("snmpget -v2c -c public -m all "+member_ip+" .1.3.6.1.4.1.7779.3.1.1.2.1.10.1.3.16")
    record = fin.readline().rstrip()
    memory_usage = re.findall('STRING: "(\d+)', record)
    return memory_usage[0]

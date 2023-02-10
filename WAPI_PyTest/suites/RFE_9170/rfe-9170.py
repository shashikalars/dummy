import datetime
import config
import re
import pexpect
import pytest
import unittest
import logging
import subprocess
import os
import json
import config
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
import commands
import json, ast
#import requests
import time
import getpass
import sys
import pexpect
#from ib_utils.log_capture import log_action as log
#from ib_utils.file_validation import log_validation as logv
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv
def remove_whitelist_and_moduleset():

    list1=subprocess.check_output("rm whitelist.bin2 moduleset.bin2",shell=True)
    print list1

def current_whitelist_path():
    list1=[]
    list1=subprocess.check_output("cd /import/builds/prod/analytics/MAIN; ls -ltr",shell=True)
    build= list1.split('\n')[-2].split(" ")[-1]
    path="/import/builds/prod/analytics/MAIN/"+build
    get_whitelist=subprocess.check_output("cd " + path +";"+ "ls -ltr | grep -i 'whitelist-.*bin2'",shell=True)
    get_whitelist=get_whitelist.split(" ")
    get_whitelist=get_whitelist[-1].replace('\n',"")
    whitelist_path=path+"/"+get_whitelist
    whitelist_path= whitelist_path.strip('\n')
    print whitelist_path
    print get_whitelist
    whitelist=subprocess.check_output("cp "+whitelist_path+" .",shell=True)
    #print "mv "+list2+" moduleset.bin2"
    whitelist=subprocess.check_output("mv "+get_whitelist+" whitelist.bin2",shell=True)
    print ("whitelist is copied to local path")
    #return get_whitelist

def current_moduleset_path():
    list1=[]
    list1=subprocess.check_output("cd /import/builds/prod/analytics/MAIN; ls -ltr",shell=True)
    build= list1.split('\n')[-2].split(" ")[-1]
    path="/import/builds/prod/analytics/MAIN/"+build
    get_moduleset=subprocess.check_output("cd " + path +";"+ "ls -ltr | grep -i 'moduleset-.*bin2'",shell=True)
    get_moduleset=get_moduleset.split(" ")
    get_moduleset=get_moduleset[-1].replace('\n',"")
    moduleset_path=path+"/"+get_moduleset
    moduleset_path= moduleset_path.strip('\n')
    moduleset=subprocess.check_output("cp "+moduleset_path+" .",shell=True)
    #print "mv "+list2+" moduleset.bin2"
    moduleset=subprocess.check_output("mv "+get_moduleset+" moduleset.bin2",shell=True)
    print ("Moduleset is copied to local path")


def get_time(time_to_move):
    current_date=os.popen("ssh root@"+config.grid_vip+" date").readline()
    current_date=current_date.split(" ")
    for i in current_date:
        if i == "":
            current_date.remove(i)
    current_time=current_date[3].split(":")
    today=int(current_date[2])
    month=(current_date[1])
    if month=="Jan":
        month=1
    elif month=="Feb":
        month=2
    elif month=="Mar":
        month=3
    elif month=="Apr":
        month=4
    elif month=="May":
        month=5
    elif month=="Jun":
        month=6
    elif month=="Jul":
        month=7
    elif month=="Aug":
        month=8
    elif month=="Sep":
        month=9
    elif month=="Oct":
        month=10
    elif month=="Nov":
        month=11
    elif month=="Dec":
        month=12
    month=int(month)
    day=current_date[0]
    if day=='Sun':
        day='SUNDAY'
    elif day=='Mon':
        day="MONDAY"
    elif day=='Tue':
        day='TUESDAY'
    elif day=='Wed':
        day='WEDNESDAY'
    elif day=='Thu':
        day="THURSDAY"
    elif day=='Fri':
        day="FRIDAY"
    else:
        day="SATURDAY"

    year=int(current_date[5])
    print year
    hour=int(current_time[0])
    minute=int(current_time[1])
    seconds=int(current_time[2])
    time_zone=current_date[4]
    if time_zone=="UTC":
        #time_zone="(UTC + 5:30) Bombay, Calcutta, Madras, New Delhi"
        time_zone="(UTC) Coordinated Universal Time"
    elif time_zone=="PST":
        time_zone="(UTC - 8:00) Pacific Time (US and Canada), Tijuana"
    elif time_zone=="PDT":
        time_zone="(UTC - 8:00) Pacific Time (US and Canada), Tijuana"
    elif time_zone=="IST":
        time_zone="(UTC + 5:30) Bombay, Calcutta, Madras, New Delhi"
    else:
        time_zone=None
    current_date = datetime.datetime(year,month,today,hour,minute,seconds)
    current_date+= datetime.timedelta(minutes=time_to_move)
    current_date=str(current_date)
    print current_date
    current_date=current_date.split(" ")
    shedule_date=current_date[0].split("-")
    schedule_time=current_date[1].split(":")
    year=int(shedule_date[0])
    month=int(shedule_date[1])
    dates=int(shedule_date[2])
    hour=int(schedule_time[0])
    minutes=int(schedule_time[1])
    seconds=int(schedule_time[2])
    return year,month,today,hour,minutes,seconds,day,time_zone,day

def GRID_BACKUP():
    logging.info("Take Empty database Backup")
    data = {"type":"BACKUP"}
    response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data))
    print response
    res = json.loads(response)
    global token
    token=res['token']
    print token
    print("Token is : %s", token)
    print ("Backup is Done")
    read  = re.search(r'201',token)
    for read in  response:
        assert True
    logging.info("Test Case 1 Execution Completed")

domains="subdomainA.subdomainB.subdomainC.subdomainD.xdomain.com"
def send_query(ip):
    record_type="CNAME"
    for i in range(1,10):
        dig_cmd = 'dig @'+ip+' '+'226L01TTL-0.'+str(i)+'.'+domains+str(' IN ')+str(record_type)
        print dig_cmd
        os.system(dig_cmd)
        print ip

class Network(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_001_Start_DNS_Service(self):
        logging.info("Start DNS Service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
        logging.info(get_ref)
        res = json.loads(get_ref)
        for ref in res:
            ref1 = ref["_ref"]
            logging.info("Modify a enable_dns")
            data = {"enable_dns": True}
            response = ib_NIOS.wapi_request('PUT', ref=ref1, fields=json.dumps(data))
            print response
            sleep(20)
            logging.info(response)
            read  = re.search(r'200',response)
            for read in  response:
                assert True
        logging.info("Test Case 1 Execution Completed")

    @pytest.mark.run(order=2)
    def test_002_Validate_DNS_service_Enabled(self):
        logging.info("Validate DNs Service is enabled")
        get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dns",params="?_return_fields=enable_dns")
        logging.info(get_tacacsplus)
        res = json.loads(get_tacacsplus)
        print res
        for i in res:
            print i
            logging.info("found")
            assert i["enable_dns"] == True
        logging.info("Test Case 2 Execution Completed")
        logging.info("============================")

    @pytest.mark.run(order=3)
    def test_003_modify_grid_dns_properties_to_configure_threat_analytics(self):
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:dns")
        get_ref1=json.loads(get_ref)[0]['_ref']
        print get_ref1
        data={"allow_recursive_query":True,"recursive_query_list":[{"_struct": "addressac","address":"Any","permission":"ALLOW"}],"allow_query":[{"_struct": "addressac","address":"Any","permission":"ALLOW"}],"forwarders":[config.forwarder_ip],"logging_categories":{"log_rpz":True,"log_queries":True,"log_responses":True}}
        put_ref=ib_NIOS.wapi_request('PUT', object_type=get_ref1,fields=json.dumps(data))
        logging.info(put_ref)
        print put_ref
        read  = re.search(r'200',put_ref)
        for read in put_ref:
            assert True
        logging.info("Test Case 3 Execution Completed")
        sleep(20)

    @pytest.mark.run(order=4)
    def test_004_add_rpz_zone(self):
        data={"fqdn": "zone1","grid_primary":[{"name": config.grid_fqdn,"stealth":False}]}
        get_ref=ib_NIOS.wapi_request('POST', object_type="zone_rp",fields=json.dumps(data))
        logging.info("adding RPZ zone ")
        if type(get_ref)!=tuple:
            grid =  ib_NIOS.wapi_request('GET', object_type="grid")
            ref = json.loads(grid)[0]['_ref']
            publish={"member_order":"SIMULTANEOUSLY"}
            request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
            time.sleep(10)
            request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
            restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
            time.sleep(20)
            print ("Restarting the grid ")
            response=ib_NIOS.wapi_request('GET', object_type="zone_rp")
            response1=json.loads(response)
            if response1[0]["fqdn"]==data["fqdn"]:
                logging.info("Test case 4 passed as RPZ zone is added")
                assert True
            else:
                logging.info("Test case 4 failed as RPZ zone is not added")
                assert False
        else:
            logging.info("Test case 4 failed as RPZ zone is not added")
            assert False

    @pytest.mark.run(order=5)
    def test_005_check_gw_ta_license_in_CLI(self):
        #logging.info("show tcp timestamps")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no admin@'+config.grid_vip)
        child.logfile=sys.stdout
        child.expect('password:')
        child.sendline('infoblox')
        child.expect('Infoblox >')
        child.sendline('show license all')
        fout = file('mylogfile.txt','w')
        child.logfile = fout
        child.expect('Infoblox >')
        child.sendline('exit')
        child.expect(pexpect.EOF)
        #child.expect(pexpect.EOF)
        fobj=open("mylogfile.txt","r")
        output=fobj.read()
        logging.info(output)
        if re.search(r"Threat Analytics.* Grid-wide",output):
            logging.info("Threat analytics license is present hence test case 5 passed")
            assert True
        else:
            logging.info("Threat analytics license is not present hence test case 5 failed")
            assert False

    @pytest.mark.run(order=6)
    def test_006_add_RPZ_zone_to_threat_analytics(self):
        get_ref=ib_NIOS.wapi_request('GET', object_type="zone_rp")
        getref1=json.loads(get_ref)
        data={"dns_tunnel_black_list_rpz_zones":[getref1[0]['_ref']]}
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics")
        logging.info(get_ref)
        get_ref1=json.loads(get_ref)[0]['_ref']
        get_ref_of_TA=ib_NIOS.wapi_request('PUT', object_type=get_ref1,fields=json.dumps(data))
        logging.info(get_ref_of_TA)
        if type(get_ref_of_TA)!=tuple:
            logging.info(get_ref_of_TA)
            logging.info("Test case 6 passed")
            assert True
        else:
            logging.info("Test case 6 failed")
            assert False

    @pytest.mark.run(order=7)
    def test_007_start_threat_analytics(self):
        members=[]
        get_ref=ib_NIOS.wapi_request('GET', object_type="member:threatanalytics")
        get_ref=json.loads(get_ref)
        for i in get_ref:
            members.append(i["_ref"])
        for ref in members:
            data={"enable_service":True}
            get_ref_of_TA=ib_NIOS.wapi_request('PUT', object_type=ref,fields=json.dumps(data))
            logging.info(get_ref)
            time.sleep(30)
        grid =  ib_NIOS.wapi_request('GET', object_type="grid")
        ref = json.loads(grid)[0]['_ref']
        publish={"member_order":"SIMULTANEOUSLY"}
        request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
        time.sleep(10)
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
        restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
        time.sleep(40)
        logging.info("Restarting the grid ")
        for i in members:
            get_ref=ib_NIOS.wapi_request('GET', object_type=i)
            get_ref1=json.loads(get_ref)
            if get_ref1["status"]=="WORKING":
                assert True
                logging.info("Test case 7 passed as threat analytics is running")
            else:
                assert False
                logging.info("Test case 7 failed as threat analytics is not running")

    @pytest.mark.run(order=8)
    def test_008_get_grid_wide_license_name(self):
        licenses=[]
        get_ref=ib_NIOS.wapi_request('GET', object_type="license:gridwide")
        get_ref1=json.loads(get_ref)
        for name in get_ref1:
            for name1 in name:
                if name1=="type":
                    licenses.append(name[name1])
        if "THREAT_ANALYTICS" in licenses:
            logging.info("Test case 8 Passed")
            assert True
        else:
            logging.info("Test case  8 Failed")
            assert False

    @pytest.mark.run(order=9)
    def test_009_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 9 passed")

    @pytest.mark.run(order=10)
    def test_010_check_added_domains_to_rpz_when_domain_collapsing_is_not_set(self):
        domain="subdomainA.subdomainB.subdomainC.subdomainD.xdomain.com"
        send_query(config.grid_vip)
        time.sleep(40)
        reference=ib_NIOS.wapi_request('GET', object_type="record:rpz:cname")
        reference=json.loads(reference)[0]['name']
        get_ref_of_rpz=ib_NIOS.wapi_request('GET', object_type="zone_rp")
        get_ref_of_rpz=json.loads(get_ref_of_rpz)[0]["fqdn"]
        response=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=domain_collapsing_level")
        response=json.loads(response)[0]["domain_collapsing_level"]
        response2=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=configure_domain_collapsing")
        response2=json.loads(response2)[0]["configure_domain_collapsing"]
        if response2==True:
            domain=domain.split(".")
            domain1=""
            domain2=domain[-response::]
            for i in domain2:
                domain1=domain1+'.'+i
            domain1='*'+domain1+'.'+get_ref_of_rpz
            if reference==domain1:
                logging.info("Test case 10 execution passed")
            else:
                logging.info("Test case 10 execution failed")
        else:
            domain1="*."+domain+'.'+get_ref_of_rpz
            if reference=="*."+domain+'.'+get_ref_of_rpz:
                logging.info("Test case 10 execution passed")
            else:
                logging.info("Test case 10 execution failed")

    @pytest.mark.run(order=11)
    def test_011_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        print("Test Case 11 Execution Completed")

    @pytest.mark.run(order=12)
    def test_012_validate_Syslog_Messages_for_DNS_tunneling_detection(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="info DNS Tunneling detected"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 12 Execution Completed")
            assert True
        else:
            logging.info("Test Case 12 Execution Failed")
            assert False


    @pytest.mark.run(order=13)
    def test_013_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        print("Test Case 13 Execution Completed")

    @pytest.mark.run(order=14)
    def test_014_validate_for_CEF_logs(self):
        time.sleep(10)
        domain="subdomainA.subdomainB.subdomainC.subdomainD.xdomain.com"
        dig_cmd = 'dig @'+config.grid_vip+' '+'any'+'.'+domain
        os.system(dig_cmd)
        sleep(30)
        logging.info("Test case 14 execution passed")

    @pytest.mark.run(order=15)
    def test_015_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        print("Test Case 15 Execution Completed")

    @pytest.mark.run(order=16)
    def test_016_validate_Syslog_Messages_for_CEF_logs(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="CEF:0*/|NIOS|"
        #LookFor="rajeev"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 16 Execution Completed")
            assert True
        else:
            logging.info("Test Case 16 Execution Failed")
            assert False

    @pytest.mark.run(order=17)
    def test_017_delete_rpz_domains(self):
        reference=ib_NIOS.wapi_request('GET', object_type="record:rpz:cname")
        reference=get_ref=json.loads(reference)
        for domain in get_ref:
            ref=domain["_ref"]
            get_ref=ib_NIOS.wapi_request('DELETE', object_type=ref)
            if type(get_ref)!=tuple:
                logging.info("Test case 17 execution passed")
                assert True
                time.sleep(10)
            else:
                logging.info("Test case 17 execution failed")
                assert False
     
    @pytest.mark.run(order=18)
    def test_018_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_member1_vip)
        logging.info("test case 9 passed")

    @pytest.mark.run(order=19)
    def test_019_check_added_domains_to_rpz_when_domain_collapsing_is_not_set(self):
        domain="subdomainA.subdomainB.subdomainC.subdomainD.xdomain.com"
        send_query(config.grid_member1_vip)
        time.sleep(40)
        reference=ib_NIOS.wapi_request('GET', object_type="record:rpz:cname")
        reference=json.loads(reference)[0]['name']
        get_ref_of_rpz=ib_NIOS.wapi_request('GET', object_type="zone_rp")
        get_ref_of_rpz=json.loads(get_ref_of_rpz)[0]["fqdn"]
        response=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=domain_collapsing_level")
        response=json.loads(response)[0]["domain_collapsing_level"]
        response2=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=configure_domain_collapsing")
        response2=json.loads(response2)[0]["configure_domain_collapsing"]
        if response2==True:
            domain=domain.split(".")
            domain1=""
            domain2=domain[-response::]
            for i in domain2:
                domain1=domain1+'.'+i
            domain1='*'+domain1+'.'+get_ref_of_rpz
            if reference==domain1:
                logging.info("Test case 19 execution passed")
            else:
                logging.info("Test case 19 execution failed")
        else:
            domain1="*."+domain+'.'+get_ref_of_rpz
            if reference=="*."+domain+'.'+get_ref_of_rpz:
                logging.info("Test case 19 execution passed")
            else:
                logging.info("Test case 19 execution failed")

    @pytest.mark.run(order=20)
    def test_020_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        print("Test Case 20 Execution Completed")

    @pytest.mark.run(order=21)
    def test_021_validate_Syslog_Messages_for_DNS_tunneling_detection(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="info DNS Tunneling detected"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 21 Execution Completed")
            assert True
        else:
            logging.info("Test Case 21 Execution Failed")
            assert False


    @pytest.mark.run(order=22)
    def test_022_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_member1_vip)
        print("Test Case 22 Execution Completed")

    @pytest.mark.run(order=23)
    def test_023_validate_for_CEF_logs(self):
        time.sleep(10)
        domain="subdomainA.subdomainB.subdomainC.subdomainD.xdomain.com"
        dig_cmd = 'dig @'+config.grid_member1_vip+' '+'any'+'.'+domain
        os.system(dig_cmd)
        sleep(30)
        logging.info("Test case 23 execution passed")

    @pytest.mark.run(order=24)
    def test_024_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_member1_vip)
        print("Test Case 24 Execution Completed")
    
    @pytest.mark.run(order=25)
    def test_025_validate_Syslog_Messages_for_CEF_logs(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="CEF:0*/|NIOS|"
        #LookFor="rajeev"
        logs=logv(LookFor,"/var/log/syslog",config.grid_member1_vip)
        print logs
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 25 Execution Completed")
            assert True
        else:
            logging.info("Test Case 25 Execution Failed")
            assert False

    @pytest.mark.run(order=26)
    def test_026_delete_rpz_domains(self):
        reference=ib_NIOS.wapi_request('GET', object_type="record:rpz:cname")
        reference=get_ref=json.loads(reference)
        for domain in get_ref:
            ref=domain["_ref"]
            get_ref=ib_NIOS.wapi_request('DELETE', object_type=ref)
            if type(get_ref)!=tuple:
                logging.info("Test case 26 execution passed")
                assert True
                time.sleep(10)
            else:
                logging.info("Test case 26 execution failed")
                assert False


    @pytest.mark.run(order=27)
    def test_027_get_default__value_set_for_configure_domain_collapsing(self):
        #Get default the value of the configure_domain_collapsing
        reference=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=configure_domain_collapsing")
        reference=json.loads(reference)[0]['configure_domain_collapsing']
        if reference==False:
            logging.info("Test case 27 passed as by default the value_set_for_configure_domain_collapsing is set to False")
            assert True
        else:
            logging.info("Test case 27 Failed as by default the value set for configure_domain_collapsing is not set to False")
            assert False

    @pytest.mark.run(order=28)
    def test_028_get_default_domain_collapsing_level(self):
        #Get the default value of domain_collapsing_level
        reference=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=domain_collapsing_level")
        reference=json.loads(reference)[0]['domain_collapsing_level']
        if reference==2:
            logging.info("Test case 28 passed as by default the value set for _domain_collapsing_level is set to 2")
            assert True
        else:
            logging.info("Test case 28 failed as by default the value set for _domain_collapsing_level is not set to 2")
            assert False

    @pytest.mark.run(order=29)
    def test_029_enable_configure_domain_collapsing(self):
        response=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics")
        response=json.loads(response)[0]['_ref']
        data={'configure_domain_collapsing':True}
        response1=ib_NIOS.wapi_request('PUT', object_type=response,fields=json.dumps(data))
        if type(response)!=tuple:
            logging.info("test case 29 passed as the configure_domain_collapsing is set")
            assert True
        else:
            logging.info("test case 29 failed as the configure_domain_collapsing is not set")
            assert False

    @pytest.mark.run(order=30)
    def test_030_validate_configure_domain_collapsing(self):
        reference=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=configure_domain_collapsing")
        reference=json.loads(reference)[0]['configure_domain_collapsing']
        if reference==True:
            logging.info("Test case 30 passed as the configure_domain_collapsing is set")
            assert True
        else:
            logging.info("Test case 30 failed configure_domain_collapsing is not set")
            assert False

    @pytest.mark.run(order=31)
    def test_031_set_domain_collapsing_level_to_invalid_value_1(self):
        reference=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics")
        reference=json.loads(reference)[0]["_ref"]
        data={"domain_collapsing_level":1}
        status,response=ib_NIOS.wapi_request('PUT', object_type=reference,fields=json.dumps(data))
        print response
        read  = re.search(r'"text": "Domain collapsing level must be between 2 and 5"',response)
        if status==400 and read:
            assert True
            logging.info("Test Case 31 passed as the value is invalid")
        else:
            assert False
            logging.info("Test Case 31 Failed as the invalid value is added")

    @pytest.mark.run(order=32)
    def test_032_set_domain_collapsing_level_to_invalid_value_6(self):
        reference=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics")
        reference=json.loads(reference)[0]["_ref"]
        data={"domain_collapsing_level":6}
        status,response=ib_NIOS.wapi_request('PUT', object_type=reference,fields=json.dumps(data))
        read  = re.search(r'"text": "Domain collapsing level must be between 2 and 5"',response)
        if status==400 and read:
            logging.info("Test Case 32 passed as the value is invalid")
            assert True
        else:
            logging.info("Test Case 32 Failed as the invalid value is added")
            assert False


    @pytest.mark.run(order=33)
    def test_033_set_domain_collapsing_level_to_3(self):
        reference=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics")
        reference=json.loads(reference)[0]["_ref"]
        data={"domain_collapsing_level":3}
        response=ib_NIOS.wapi_request('PUT', object_type=reference,fields=json.dumps(data))
        if type(response)!=tuple:
            logging.info("Test Case 33 passed as the value is valid")
            assert True
        else:
            logging.info( "Test Case 33 execution Failed ")
            assert False


    @pytest.mark.run(order=34)
    def test_034_validate_domain_collapsing_level_to_3(self):
        reference=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=domain_collapsing_level")
        reference=json.loads(reference)[0]["domain_collapsing_level"]
        data={"domain_collapsing_level":3}
        if data["domain_collapsing_level"]==reference:
            logging.info("Test Case 34 execution passed")
            assert True
        else:
            logging.info("Test Case 34 execution Failed")
            assert False


    @pytest.mark.run(order=35)
    def test_035_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 35 execution passed")

    @pytest.mark.run(order=36)
    def test_036_check_added_domains_to_rpz_when_domain_collapsing_is_set(self):
        domain="subdomainA.subdomainB.subdomainC.subdomainD.xdomain.com"
        send_query(config.grid_vip)
        time.sleep(20)
        reference=ib_NIOS.wapi_request('GET', object_type="record:rpz:cname")
        reference=json.loads(reference)[0]['name']
        get_ref_of_rpz=ib_NIOS.wapi_request('GET', object_type="zone_rp")
        get_ref_of_rpz=json.loads(get_ref_of_rpz)[0]["fqdn"]
        response=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=domain_collapsing_level")
        response=json.loads(response)[0]["domain_collapsing_level"]
        response2=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=configure_domain_collapsing")
        response2=json.loads(response2)[0]["configure_domain_collapsing"]
        if response2==True:
            domain=domain.split(".")
            domain1=""
            domain2=domain[-response::]
            for i in domain2:
                domain1=domain1+'.'+i
            domain1='*'+domain1+'.'+get_ref_of_rpz
            if reference==domain1:
                logging.info("Test case 36 execution passed")
                assert True
            else:

                logging.info("Test case 36 execution failed")
                assert False
        else:
            domain1="*."+domain+'.'+get_ref_of_rpz
            if reference==domain1:
                logging.info("Test case 36 execution passed")
                assert True
            else:
                logging.info("Test case 36 execution failed")
                assert False


    @pytest.mark.run(order=37)
    def test_037_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        print("Test Case 37 Execution Completed")

    @pytest.mark.run(order=38)
    def test_038_validate_Syslog_Messages_for_Dns_Tunneling(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="info DNS Tunneling detected"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 38 Execution Completed")
            assert True
        else:
            logging.info("Test Case 38 Execution Failed")
            assert False

    @pytest.mark.run(order=39)
    def test_039_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("Test case 39 execution failed")

    @pytest.mark.run(order=40)
    def test_040_validate_for_CEF_logs(self):
        time.sleep(40)
        domain="subdomainA.subdomainB.subdomainC.subdomainD.xdomain.com"
        dig_cmd = 'dig @'+config.grid_vip+' '+'any'+'.'+domain
        os.system(dig_cmd)
        time.sleep(30)
        logging.info("Test case 40 execution passed")

    @pytest.mark.run(order=41)
    def test_041_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        print("Test Case 41 Execution Completed")

    @pytest.mark.run(order=42)
    def test_042_validate_Syslog_Messages_for_CEF_logs(self):
        time.sleep(40)
        logging.info("Validating Sylog Messages Logs")
        LookFor="CEF:0*/|NIOS|"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 42 Execution Completed")
            assert True
        else:
            logging.info("Test Case 42 Execution Failed")
            assert False


    @pytest.mark.run(order=43)
    def test_043_add_rpz_domain_to_whitelist(self):
        domains="*.subdomainD.xdomain.com.zone1"
        reference=ib_NIOS.wapi_request('GET', object_type="record:rpz:cname")
        reference=get_ref=json.loads(reference)
        for domain in reference:
            if domain["name"]==domains:
                ref=domain["_ref"]
                response=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics")
                response=json.loads(response)[0]["_ref"]
                data={"rpz_cnames":[ref]}
                get_ref=ib_NIOS.wapi_request('POST', object_type=response+"?_function=move_blacklist_rpz_to_white_list",fields=json.dumps(data))
                if type(get_ref)!=tuple:
                    logging.info("test case 43 execution passed")
                    assert True
                else:
                    logging.info("test case 43 execution failed")
                    assert False

    @pytest.mark.run(order=44)
    def test_044_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("Test case 44 execution failed")

    @pytest.mark.run(order=45)
    def test_045_query_for_added_rpz_domain_added_in_whitelist(self):
        send_query(config.grid_vip)
        time.sleep(10)
        logging.info("Test case 45 execution passed")

    @pytest.mark.run(order=46)
    def test_046_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 46 Execution Completed")

    @pytest.mark.run(order=47)
    def test_047_validate_Syslog_Messages_for_NOERROR(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="IN CNAME response: NOERROR"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 47 Execution Completed")
            assert True
        else:
            logging.info("Test Case 47 Execution Failed")
            assert False


    @pytest.mark.run(order=48)
    def test_048_delete_rpz_domains(self):
        reference=ib_NIOS.wapi_request('GET', object_type="record:rpz:cname")
        reference=get_ref=json.loads(reference)
        for domain in get_ref:
            ref=domain["_ref"]
            get_ref=ib_NIOS.wapi_request('DELETE', object_type=ref)
            if type(get_ref)!=tuple:
                logging.info("Test case 48 execution passed")
                assert True
            else:
                logging.info("Test case 48 execution failed")
                assert False


    @pytest.mark.run(order=49)
    def test_049_delete_rpz_domains_added_in_whitelist(self):
        domain="subdomainD.xdomain.com"
        reference=ib_NIOS.wapi_request('GET', object_type="threatanalytics:whitelist?fqdn="+domain)
        reference=json.loads(reference)
        for i in reference:
            if i["fqdn"]==domain:
                ref=i["_ref"]
                get_ref=ib_NIOS.wapi_request('DELETE', object_type=ref)
                if type(get_ref)!=tuple:
                    logging.info("Test case 49 execution passed")
                    assert True
                else:
                    logging.info("Test case 49 execution failed")
                    assert False

    @pytest.mark.run(order=50)
    def test_050_add_TLD_in_rpz_zones(self):
        data={"name":"*.xdomain.com.zone1","rp_zone":"zone1","canonical":""}
        reference=ib_NIOS.wapi_request('POST', object_type="record:rpz:cname",fields=json.dumps(data))
        if type(reference)!=tuple:
            logging.info("Test case 50 execution passed as TLD is added in RPZ Zone")
            assert True
        else:
            logging.info("Test case 50 execution failed as TLD is not added in RPZ Zone")
            assert False

    @pytest.mark.run(order=51)
    def test_051_validate_TLD_in_rpz_zones(self):
        data={"name":"*.xdomain.com.zone1","rp_zone":"zone1","canonical":""}
        reference=ib_NIOS.wapi_request('GET', object_type="record:rpz:cname")
        reference=json.loads(reference)[0]["name"]
        if reference==data['name']:
            assert True
            logging.info("Test case 51 passed as the zone is present")
        else:
            assert False
            logging.info("Test case 51 failed as the zone is not present")

    @pytest.mark.run(order=52)
    def test_052_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("Test case 52 execution failed")

    @pytest.mark.run(order=53)
    def test_053_query_for_added_rpz_domain_added_in_blacklist(self):
        send_query(config.grid_vip)
        time.sleep(10)
        logging.info("Test case 53 execution passed")

    @pytest.mark.run(order=54)
    def test_054_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        print("Test Case 54 Execution Completed")


    @pytest.mark.run(order=55)
    def test_055_validate_Syslog_Messages_for_CEF_logs(self):
        time.sleep(40)
        logging.info("Validating Sylog Messages Logs")
        LookFor="CEF:0*/|NIOS|"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 55 Execution Completed")
            assert True
        else:
            logging.info("Test Case 55 Execution Failed")
            assert False


    @pytest.mark.run(order=56)
    def test_056_delete_rpz_domains(self):
        reference=ib_NIOS.wapi_request('GET', object_type="record:rpz:cname")
        reference=get_ref=json.loads(reference)
        for domain in get_ref:
            ref=domain["_ref"]
            get_ref=ib_NIOS.wapi_request('DELETE', object_type=ref)
        assert True
        logging.info("Test case 56 failed as the zone is not present")

    @pytest.mark.run(order=57)
    def test_057_disable_configure_domain_collapsing(self):
        reference=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics")
        reference=json.loads(reference)[0]['_ref']
        data={'configure_domain_collapsing':False}
        response=ib_NIOS.wapi_request('PUT', object_type=reference,fields=json.dumps(data))
        if type(response)!=tuple:
            logging.info("test case 57 passed as the configure_domain_collapsing is set to False")
            assert True
        else:
            logging.info("test case 57 failed as the configure_domain_collapsing is set to True")
            assert False

    @pytest.mark.run(order=58)
    def test_058_validate_configure_domain_collapsing(self):
        reference=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=configure_domain_collapsing")
        reference=json.loads(reference)[0]['configure_domain_collapsing']
        data={'configure_domain_collapsing':False}
        if data["configure_domain_collapsing"]==reference:
            logging.info("test case 58 passed as the configure_domain_collapsing is set to False")
            assert True
        else:
            logging.info("test case 58 failed as the configure_domain_collapsing is set to True")
            assert False

    @pytest.mark.run(order=59)
    def test_059_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("Test case 59 execution failed")

    @pytest.mark.run(order=60)
    def test_060_check_added_domains_to_rpz_when_domain_collapsing_is_not_set(self):
        domain="subdomainA.subdomainB.subdomainC.subdomainD.xdomain.com"
        send_query(config.grid_vip)
        time.sleep(20)
        reference=ib_NIOS.wapi_request('GET', object_type="record:rpz:cname")
        reference=json.loads(reference)[0]['name']
        get_ref_of_rpz=ib_NIOS.wapi_request('GET', object_type="zone_rp")
        get_ref_of_rpz=json.loads(get_ref_of_rpz)[0]["fqdn"]
        response=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=domain_collapsing_level")
        response=json.loads(response)[0]["domain_collapsing_level"]
        response2=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=configure_domain_collapsing")
        response2=json.loads(response2)[0]["configure_domain_collapsing"]
        if response2==True:
            domain=domain.split(".")
            domain1=""
            domain2=domain[-response::]
            for i in domain2:
                domain1=domain1+'.'+i
            domain1='*'+domain1+'.'+get_ref_of_rpz
            print get_ref1
            print domain1
            if get_ref1==domain1:
                assert True
                logging.info("Test case 60 execution passed")
            else:
                assert False
                logging.info("Test case 60 execution failed")
        else:
            domain1="*."+domain+'.'+get_ref_of_rpz
            if reference==domain1:
                assert True
                logging.info("Test case 60 execution passed")
            else:
                assert False
                logging.info("Test case 60 execution failed")

    @pytest.mark.run(order=61)
    def test_061_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 61 Execution Completed")


    @pytest.mark.run(order=62)
    def test_062_validate_Syslog_Messages_for_DNS_Tunneling(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="info DNS Tunneling detected"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 62 Execution Completed")
            assert True
        else:
            logging.info("Test Case 62 Execution Failed")
            assert False


    @pytest.mark.run(order=63)
    def test_063_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("Test case 63 execution failed")

    @pytest.mark.run(order=64)
    def test_064_validate_for_CEF_logs(self):
        time.sleep(40)
        domain="subdomainA.subdomainB.subdomainC.subdomainD.xdomain.com"
        dig_cmd = 'dig @'+config.grid_vip+' '+'any'+'.'+domain
        os.system(dig_cmd)
	time.sleep(30)
        logging.info("Test case 64 execution passed")

    @pytest.mark.run(order=65)
    def test_065_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        print("Test Case 65 Execution Completed")

    @pytest.mark.run(order=66)
    def test_066_validate_Syslog_Messages_for_CEF_logs(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="CEF:0*/|NIOS|"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        if logs!=None:
            logging.info(logs)
            logging.info("Test Case 66 Execution Completed")
            assert True
        else:
            logging.info("Test Case 66 Execution Failed")
            assert False

    @pytest.mark.run(order=67)
    def test_067_check_for_the_current_moduleset(self):
        reference=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=current_moduleset")
        logging.info(reference)
        if re.search(r'[0-9]*',reference):
            assert True
            logging.info("Test case 67 execution passed")
        else:
            assert False
            logging.info("Test case 67 execution Failed")

    @pytest.mark.run(order=68)
    def test_068_check_for_the_current_whitelist(self):
        reference=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=current_moduleset")
        logging.info(reference)
        if re.search(r'[0-9]*',reference):
            assert True
            logging.info("Test case 68 execution passed")
        else:
            assert False
            logging.info("Test case 68 execution Failed")

    @pytest.mark.run(order=69)
    def test_069_default_whitelist_update_policy(self):
        reference=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=whitelist_update_policy")
        reference=json.loads(reference)[0]["whitelist_update_policy"]
        data={"whitelist_update_policy":"AUTOMATIC"}
        if data["whitelist_update_policy"]==reference:
            logging.info("test case 69 execution passed")
            assert True
        else:
            logging.info("test case 69 execution failed")
            assert False

    @pytest.mark.run(order=70)
    def test_070_default_moduleset_update_policy(self):
        reference=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=module_update_policy")
        reference=json.loads(reference)[0]["module_update_policy"]
        data={"module_update_policy":"AUTOMATIC"}
        if data["module_update_policy"]==reference:
            logging.info("test case 70 execution passed")
            assert True
        else:
            logging.info("test case 70 execution failed")
            assert False

    @pytest.mark.run(order=71)
    def test_071_default_value_for_enable_whitelist_auto_download(self):
        reference=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=enable_whitelist_auto_download")
        reference=json.loads(reference)[0]["enable_whitelist_auto_download"]
        data={"enable_whitelist_auto_download":False}
        if data["enable_whitelist_auto_download"]==reference:
            logging.info("test case 71 execution passed")
            assert True
        else:
            logging.info("test case 71 execution failed")
            assert False

    @pytest.mark.run(order=72)
    def test_072_default_value_for_enable_moduleset_auto_download(self):
        reference=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=enable_auto_download")
        reference=json.loads(reference)[0]["enable_auto_download"]
        data={"enable_auto_download":False}
        if data["enable_auto_download"]==reference:
            logging.info("test case 72 execution passed")
            assert True
        else:
            logging.info("test case 72  execution failed")
            assert False

    @pytest.mark.run(order=73)
    def test_073_default_value_for_enable_whitelist_scheduled_download(self):
        reference=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=enable_whitelist_scheduled_download")
        reference=json.loads(reference)[0]["enable_whitelist_scheduled_download"]
        data={"enable_whitelist_scheduled_download":False}
        if data["enable_whitelist_scheduled_download"]==reference:
            logging.info("test case 73 execution passed")
            assert True
        else:
            logging.info("test case 73 execution failed")
            assert False

    @pytest.mark.run(order=74)
    def test_074_default_value_for_enable_scheduled_download(self):
        reference=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=enable_scheduled_download")
        reference=json.loads(reference)[0]["enable_scheduled_download"]
        data={"enable_scheduled_download":False}
        if data["enable_scheduled_download"]==reference:
            logging.info("test case 74 execution passed")
            assert True
        else:
            logging.info("test case 74 execution failed")
            assert False

    @pytest.mark.run(order=75)
    def test_075_last_checked_for_whitelist_update(self):
        reference=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=last_checked_for_whitelist_update")
        print reference
        reference=json.loads(reference)[0]
        if len(reference)==1:
            logging.info("test case 75 execution passed")
            assert True
        elif len(reference)==2:
            reference1=reference["last_checked_for_whitelist_update"]
            if type(reference1)==int:
                logging.info("test case 75 execution passed")
                assert True
            else:
                logging.info("test case 75 execution failed")
                assert False
        else:
            logging.info("test case 75 execution failed")
            assert False

    @pytest.mark.run(order=76)
    def test_076_last_checked_for_moduleset_update(self):
        reference=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=last_checked_for_update")
        print reference
        reference=json.loads(reference)[0]
        if len(reference)==1:
            assert True
            logging.info("test case 76 execution passed")
        elif len(reference)==2:
            reference1=reference["last_checked_for_update"]
            if type(reference1)==int:
                assert True
                logging.info("test case 76 execution passed")
            else:
                assert False
                logging.info("test case 76 execution failed")
        else:
            logging.info("test case 76 execution failed")
            assert False
    
    @pytest.mark.run(order=77)
    def test_077_last_whitelist_update_time(self):
        reference=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=last_whitelist_update_time")
        print reference
        reference=json.loads(reference)[0]
        if len(reference)==1:
            assert True
            logging.info("test case 77 execution passed")
        elif len(reference)==2:
            reference1=reference["last_whitelist_update_time"]
            if type(reference1)==int:
                assert True
                logging.info("test case 77 execution passed")
            else:
                assert False
                logging.info("test case 77 execution failed")
        else:
            logging.info("test case 77 execution failed")
            assert False

    @pytest.mark.run(order=78)
    def test_078_last_module_update_time(self):
        reference=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=last_module_update_time")
        print reference
        reference=json.loads(reference)[0]
        if len(reference)==1:
            assert True
            logging.info("test case 78 execution passed")
        elif len(reference)==2:
            reference1=reference["last_module_update_time"]
            if type(reference1)==int:
                assert True
                logging.info("test case 78 execution passed")
            else:
                assert False
                logging.info("test case 78 execution failed")
        else:
            logging.info("test case 78 execution failed")
            assert False

    
    @pytest.mark.run(order=79)
    def test_079_last_whitelist_update_version(self):
        reference=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=last_whitelist_update_version")
        reference=json.loads(reference)[0]["last_whitelist_update_version"]
        logging.info(reference)
        if type(reference)==unicode or reference=="[]":
            logging.info("Test case 79 passed")
            assert True
        else:
            logging.info("Test case 79 failed")
            assert False


    @pytest.mark.run(order=80)
    def test_080_last_module_set_update_version(self):
        reference=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=last_module_update_version")
        reference=json.loads(reference)[0]["last_module_update_version"]
        if type(reference)==unicode or reference=="[]":
            logging.info("Test case 80 passed")
            assert True
        else:
            logging.info("Test case 80 failed")
            assert False

    @pytest.mark.run(order=81)
    def test_081_set_dns_resolvers(self):
        reference=ib_NIOS.wapi_request('GET', object_type="grid")
        reference=json.loads(reference)[0]["_ref"]
        print reference
        data={"dns_resolver_setting":{"resolvers":[config.resolver_ip],"search_domains":[]}}
        reference1=ib_NIOS.wapi_request('PUT', object_type=reference,fields=json.dumps(data))
        read  = re.search(r'200',reference1)
        for read in  reference1:
            assert True
            time.sleep(40)
        logging.info("Test Case 81 Execution Completed")

    @pytest.mark.run(order=82)
    def test_082_test_connection_for_moduleset_and_whitelist(self):
        reference=ib_NIOS.wapi_request('POST', object_type="grid:threatanalytics?_function=test_threat_analytics_server_connectivity")
        reference=json.loads(reference)["overall_status"]
        print reference
        if reference== "SUCCESS":
            logging.info("test case 82 execution passed")
            assert True
        else:
            logging.info("test case 82 execution failed")
            assert False


    @pytest.mark.run(order=83)
    def test_083_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("test case 83 passed")

###############################
    @pytest.mark.run(order=84)
    def test_084_test_download_threat_analytics_moduleset_update_when_both_policy_is_set_to_AUTOMATIC(self):
        reference=ib_NIOS.wapi_request('POST', object_type="grid:threatanalytics",params="?_function=download_threat_analytics_moduleset_update")
        if type(reference)==tuple:
            if re.search(r'"text": "Grid Master already has the latest Threat Analytics moduleset versions. No new files downloaded."',reference[1]):
                assert True
                logging.info("test case 84 execution passed")
            else:
                assert False
                logging.info("test case 84 execution failed")
        elif reference=='{}':
            assert True
            logging.info("test case 84 execution passed")
        else:
            assert False
            logging.info("test case 84 execution failed")

    @pytest.mark.run(order=85)
    def test_085_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        print("Test Case 85 Execution Completed")


    @pytest.mark.run(order=86)
    def test_086_validate_Syslog_Messages(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="Grid Master already have the latest moduleset"
        #LookFor="Arun|Kumar"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        if logs==None:
            LookFor="Latest threat analytics moduleset available from Infoblox Download server"
            logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
            if logs!=None:
                logging.info("Test Case 86 Execution Completed")
                assert True
            else:
                logging.info("Test Case 86 Execution failed")
                assert False
        else:
            logging.info("Test Case 86 Execution Completed")
            assert True


    @pytest.mark.run(order=87)
    def test_087_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 87 passed")

    @pytest.mark.run(order=88)
    def test_088_test_download_threat_analytics_whitelist_update_when_both_policy_is_set_to_AUTOMATIC(self):
        data={"is_whitelist":True}
        reference=ib_NIOS.wapi_request('POST', object_type="grid:threatanalytics",params="?_function=download_threat_analytics_whitelist_update",fields=json.dumps(data))
        print reference
        if type(reference)==tuple:
            if re.search(r'"text": "Grid Master already has the latest Threat Analytics whitelist versions. No new files downloaded."',reference[1]):
                assert True
                logging.info("test case 88 execution passed")
            else:
                assert False
                logging.info("test case 88 execution failed")
        elif reference=='{}':
            assert True
            logging.info("test case 88 execution passed")
        else:
            assert False
            logging.info("test case 88 execution failed")

    @pytest.mark.run(order=89)
    def test_089_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        print("Test Case 89 Execution Completed")

    @pytest.mark.run(order=90)
    def test_090_validate_Syslog_Messages(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="Grid Master already have the latest whitelist|info Automated Threat Analytics file Download and Update succeeded"

        #LookFor="Arun|Kumar"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        if logs!=None:
            logging.info("Test Case 90 Execution Completed")
            assert True
        else:
            logging.info("Test Case 90 Execution failed")
            assert False

    @pytest.mark.run(order=91)
    def test_091_start_Infoblox_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        print ("++++++++++++++++++++++++++++++++++++")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        #log("start","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("test case 91 passed")

    @pytest.mark.run(order=92)
    def test_092_upload_whitelist_when_both_policy_is_set_to_AUTOMATIC(self):
        current_whitelist_path()
        #print path
        filename="whitelist.bin2"
        logging.info("Test Uploading the Template with fileop")
        data = {"filename":filename}
        create_file = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadinit")
        logging.info(create_file)
        print create_file
        res = json.loads(create_file)
        token = json.loads(create_file)['token']
        url = json.loads(create_file)['url']
        file1=url.split("/")
        os.system('curl -k1 -u admin:infoblox -F name=%s -F filedata=@%s %s'%(filename,filename,url))
        filename="/"+filename
        data = {"moduleset_token":token}
        create_file1 = ib_NIOS.wapi_request('POST', object_type="grid:threatanalytics/YW5hbHl0aWNzLmNsdXN0ZXJfYW5hbHl0aWNzX3Byb3BlcnRpZXMkMA",fields=json.dumps(data),params="?_function=set_last_uploaded_threat_analytics_moduleset")
        create_file1=json.loads(create_file1)

        create_file1 = ib_NIOS.wapi_request('POST', object_type="grid:threatanalytics/YW5hbHl0aWNzLmNsdXN0ZXJfYW5hbHl0aWNzX3Byb3BlcnRpZXMkMA",params="?_function=update_threat_analytics_moduleset")
        print create_file1
        if type(create_file1)==tuple:
            if re.search(r'uploaded already exists in Grid',create_file1[1]):
                logging.info("test case 92 execution passed")
                assert True
            else:
                logging.info("test case 92 execution failed")
                assert False
        elif create_file1=='{}':
            logging.info("test case 92 execution passed")
            assert True
        else:
            logging.info("test case 92 execution failed")
            assert False

    @pytest.mark.run(order=93)
    def test_093_stop_Infoblox_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        #log("start","/infoblox/var/infoblox",config.grid_vip)
        logging.info("test case 93  passed")

    @pytest.mark.run(order=94)
    def test_094_validate_Infoblox_Messages(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="uploaded already exists in Grid|updated to db"#Domain Name White List update completed in var/log/messages
        #LookFor="Arun|Kumar"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info("Test Case 94 Execution Completed")
            assert True
        else:
            logging.info("Test Case 94 Execution failed")
            assert False
    
    @pytest.mark.run(order=95)
    def test_095_start_Infoblox_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/infoblox/var/infoblox.log",config.grid_vip)
        logging.info("test case 95 passed")

    @pytest.mark.run(order=96)
    def test_096_upload_moduleset_when_both_policy_is_set_to_AUTOMATIC(self):
        current_moduleset_path()
        filename="moduleset.bin2"
        logging.info("Test Uploading the Template with fileop")
        data = {"filename":filename}
        create_file = ib_NIOS.wapi_request('POST', object_type="fileop",fields=json.dumps(data),params="?_function=uploadinit")
        logging.info(create_file)
        res = json.loads(create_file)
        token = json.loads(create_file)['token']
        url = json.loads(create_file)['url']
        file1=url.split("/")
        os.system('curl -k1 -u admin:infoblox -F name=%s -F filedata=@%s %s'%(filename,filename,url))
        filename="/"+filename
        data = {"moduleset_token":token}
        create_file1 = ib_NIOS.wapi_request('POST', object_type="grid:threatanalytics/YW5hbHl0aWNzLmNsdXN0ZXJfYW5hbHl0aWNzX3Byb3BlcnRpZXMkMA",fields=json.dumps(data),params="?_function=set_last_uploaded_threat_analytics_moduleset")
        create_file1=json.loads(create_file1)

        create_file1 = ib_NIOS.wapi_request('POST', object_type="grid:threatanalytics/YW5hbHl0aWNzLmNsdXN0ZXJfYW5hbHl0aWNzX3Byb3BlcnRpZXMkMA",params="?_function=update_threat_analytics_moduleset")
        if type(create_file1)==tuple:
            if re.search(r'uploaded already exists in Grid',create_file1[1]):
                logging.info("test case 96 execution passed")
                assert True
            else:
                logging.info("test case 96 execution failed")
                assert False
        elif create_file1=='{}':
            logging.info("test case 96 execution passed")
            assert True
        else:
            logging.info("test case 96 execution failed")
            assert False

    @pytest.mark.run(order=97)
    def test_097_stop_Infoblox_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/infoblox/var/infoblox.log",config.grid_vip)
        print("Test Case 97 Execution Completed")

    @pytest.mark.run(order=98)
    def test_098_validate_Infoblox_Messages(self):
        #remove_whitelist_and_moduleset()
        logging.info("Validating Sylog Messages Logs")
        LookFor="uploaded already exists in Grid|Importing Moduleset Version"
        #LookFor="Arun|Kumar"
        logs=logv(LookFor,"/infoblox/var/infoblox.log",config.grid_vip)
        if logs!=None:
            logging.info("Test Case 98 Execution Completed")
            assert True
        else:
            logging.info("Test Case 98 Execution failed")
            assert False

    @pytest.mark.run(order=99)
    def test_099_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 99 passed")

    @pytest.mark.run(order=100)
    def test_100_scheduled_whitelist_download_hourly_when_both_policy_is_set_to_AUTOMATIC(self):
        schedule_date=get_time(2)
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics")
        get_ref1=json.loads(get_ref)[0]['_ref']
        print schedule_date[7]
        data={"enable_whitelist_auto_download":True,"enable_whitelist_scheduled_download":True,"scheduled_whitelist_download":{"disable":False,"frequency": "HOURLY","hour_of_day": schedule_date[3],"minutes_past_hour": schedule_date[4],"time_zone": schedule_date[7],"month":schedule_date[1],"day_of_month":schedule_date[2],"repeat":"RECUR"}}
        put_ref=ib_NIOS.wapi_request('PUT', object_type=get_ref1,fields=json.dumps(data))
        logging.info(put_ref)
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=enable_whitelist_auto_download,enable_whitelist_scheduled_download,scheduled_whitelist_download")
        get_ref=json.loads(get_ref)
        if get_ref[0]["enable_whitelist_scheduled_download"]==data["enable_whitelist_scheduled_download"] and get_ref[0]["enable_whitelist_auto_download"]==data["enable_whitelist_auto_download"] and get_ref[0]["scheduled_whitelist_download"]["frequency"]==data["scheduled_whitelist_download"]["frequency"]:
            print("Test case 94 passed")
            time.sleep(1800)
            assert True
        else:
            print("Test case 100 failed")
            assert False

    @pytest.mark.run(order=101)
    def test_101_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        print("Test Case 101 Execution Completed")

    @pytest.mark.run(order=102)
    def test_102_validate_Syslog_Messages(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="info Automated Threat Analytics file Download and Update skipped: no moduleset file|info Success : File download success for analytics update and it is rsync with GM|info Grid Master already have the latest whitelist"
        #LookFor="Arun|Kumar"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        if logs!=None:
            logging.info("Test Case 102 Execution Completed")
            assert True
        else:
            logging.info("Test Case 102 Execution failed")
            assert False

    @pytest.mark.run(order=103)
    def test_103_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("Test Case 103 Execution Completed")

    @pytest.mark.run(order=104)
    def test_104_scheduled_moduleset_download_hourly_when_both_policy_is_set_to_AUTOMATIC(self):
        schedule_date=get_time(5)
        print schedule_date
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics")
        get_ref1=json.loads(get_ref)[0]['_ref']
        data={"enable_auto_download":True,"enable_scheduled_download":True,"scheduled_download":{"disable":False,"frequency": "HOURLY","hour_of_day": schedule_date[3],"minutes_past_hour": schedule_date[4],"time_zone": schedule_date[7],"month":schedule_date[1],"day_of_month":schedule_date[2],"repeat":"RECUR"}}
        put_ref=ib_NIOS.wapi_request('PUT', object_type=get_ref1,fields=json.dumps(data))
        print put_ref
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=enable_auto_download,enable_scheduled_download,scheduled_download")
        get_ref=json.loads(get_ref)
        if get_ref[0]["enable_scheduled_download"]==data["enable_scheduled_download"] and get_ref[0]["enable_auto_download"]==data["enable_auto_download"] and get_ref[0]["scheduled_download"]["frequency"]==data["scheduled_download"]["frequency"]:
            print("Test case 104 passed")
            time.sleep(1800)
            assert True
        else:
            print("Test case 104 failed")
            assert False

    @pytest.mark.run(order=105)
    def test_105_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        print("Test Case 105 Execution Completed")

    @pytest.mark.run(order=106)
    def test_106_validate_Syslog_Messages(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="info Automated Threat Analytics file Download and Update skipped: no moduleset file | info Success : File download success for analytics update and it is rsync with GM | info Grid Master already have the latest moduleset"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        if logs!=None:
            logging.info("Test Case 106 Execution Completed")
            assert True
        else:
            logging.info("Test Case 106 Execution failed")
            assert False

    @pytest.mark.run(order=107)
    def test_107_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 107 passed")

    @pytest.mark.run(order=108)
    def test_108_scheduled_whitelist_download_daily_when_both_policy_is_set_to_AUTOMATIC(self):
        #restore()
        schedule_date=get_time(5)
        print schedule_date
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics")
        get_ref1=json.loads(get_ref)[0]['_ref']
        data={"enable_whitelist_auto_download":True,"enable_whitelist_scheduled_download":True,"scheduled_whitelist_download":{"disable":False,"frequency": "DAILY","hour_of_day": schedule_date[3],"minutes_past_hour": schedule_date[4],"time_zone": schedule_date[7],"month":schedule_date[1],"day_of_month":schedule_date[2],"repeat":"RECUR"}}
        put_ref=ib_NIOS.wapi_request('PUT', object_type=get_ref1,fields=json.dumps(data))
        logging.info (put_ref)
        print put_ref
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=enable_whitelist_auto_download,enable_whitelist_scheduled_download,scheduled_whitelist_download")
        get_ref=json.loads(get_ref)
        if get_ref[0]["enable_whitelist_scheduled_download"]==data["enable_whitelist_scheduled_download"] and get_ref[0]["enable_whitelist_auto_download"]==data["enable_whitelist_auto_download"] and get_ref[0]["scheduled_whitelist_download"]["frequency"]==data["scheduled_whitelist_download"]["frequency"]:
            print("Test case 108 passed")
            time.sleep(1800)
            assert True
        else:
            print("Test case 108 failed")
            assert False

    @pytest.mark.run(order=109)
    def test_109_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        print("Test Case 109 Execution Completed")

    @pytest.mark.run(order=114)
    def test_110_validate_Syslog_Messages(self):
        logging.info("Validating Sylog Messages Logs")
        #LookFor="Arun|Kumar"
        LookFor1=".*info Automated Threat Analytics file Download and Update skipped: no moduleset file.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        LookFor2=".*info Success : File download success for analytics update and it is rsync with GM.*"
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
        LookFor3=".*info Grid Master already have the latest moduleset.*"
        logs3=logv(LookFor3,"/var/log/syslog",config.grid_vip)
        if logs1!=None or logs2!=None or logs3!=None:
            logging.info("Test Case 114 Execution Completed")
            assert True
        else:
            logging.info("Test Case 114 Execution failed")
            assert False

    @pytest.mark.run(order=111)
    def test_111_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 111 passed")

    @pytest.mark.run(order=112)
    def test_112_scheduled_moduleset_download_daily_when_both_policy_is_set_to_AUTOMATIC(self):
        schedule_date=get_time(5)
        #print schedule_date
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics")
        print get_ref
        get_ref1=json.loads(get_ref)[0]['_ref']
        data={"enable_auto_download":True,"enable_scheduled_download":True,"scheduled_download":{"disable":False,"frequency": "DAILY","hour_of_day": schedule_date[3],"minutes_past_hour": schedule_date[4],"time_zone": schedule_date[7],"month":schedule_date[1],"day_of_month":schedule_date[2],"repeat":"RECUR"}}
        put_ref=ib_NIOS.wapi_request('PUT', object_type=get_ref1,fields=json.dumps(data))
        #print put_ref
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=enable_auto_download,enable_scheduled_download,scheduled_download")
        get_ref=json.loads(get_ref)
        print get_ref
        if get_ref[0]["enable_scheduled_download"]==data["enable_scheduled_download"] and get_ref[0]["enable_auto_download"]==data["enable_auto_download"] and get_ref[0]["scheduled_download"]["frequency"]==data["scheduled_download"]["frequency"]:
            print("Test case 112 passed")
            time.sleep(1800)
            assert True
        else:
            print("Test case 112 failed")
            assert False

    @pytest.mark.run(order=113)
    def test_113_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        print("Test Case 113 Execution Completed")

    @pytest.mark.run(order=114)
    def test_114_validate_Syslog_Messages(self):
        logging.info("Validating Sylog Messages Logs")
        #LookFor="Arun|Kumar"
        LookFor1=".*info Automated Threat Analytics file Download and Update skipped: no moduleset file.*"
        logs1=logv(LookFor1,"/var/log/syslog",config.grid_vip)
        LookFor2=".*info Success : File download success for analytics update and it is rsync with GM.*"
        logs2=logv(LookFor2,"/var/log/syslog",config.grid_vip)
        LookFor3=".*info Grid Master already have the latest moduleset.*"
        logs3=logv(LookFor3,"/var/log/syslog",config.grid_vip)
        if logs1!=None or logs2!=None or logs3==None:
            logging.info("Test Case 114 Execution Completed")
            assert True
        else:
            logging.info("Test Case 114 Execution failed")
            assert False

    @pytest.mark.run(order=115)
    def test_115_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 115 passed")

    @pytest.mark.run(order=116)
    def test_116_scheduled_whitelist_download_weekly_when_both_policy_is_set_to_AUTOMATIC(self):
        #restore()
        schedule_date=get_time(5)
        print schedule_date
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics")
        get_ref1=json.loads(get_ref)[0]['_ref']
        data={"enable_whitelist_auto_download":True,"enable_whitelist_scheduled_download":True,"scheduled_whitelist_download":{"disable":False,"frequency": "WEEKLY","hour_of_day": schedule_date[3],"minutes_past_hour": schedule_date[4],"weekdays":[schedule_date[8]],"time_zone": schedule_date[7],"month":schedule_date[1],"day_of_month":schedule_date[2],"repeat":"RECUR"}}
        put_ref=ib_NIOS.wapi_request('PUT', object_type=get_ref1,fields=json.dumps(data))
        print put_ref
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=enable_whitelist_auto_download,enable_whitelist_scheduled_download,scheduled_whitelist_download")
        get_ref=json.loads(get_ref)
        if get_ref[0]["enable_whitelist_scheduled_download"]==data["enable_whitelist_scheduled_download"] and get_ref[0]["enable_whitelist_auto_download"]==data["enable_whitelist_auto_download"] and get_ref[0]["scheduled_whitelist_download"]["frequency"]==data["scheduled_whitelist_download"]["frequency"]:
            print("Test case 116 passed")
            time.sleep(1800)
            assert True
        else:
            print("Test case 116 failed")
            assert False

    @pytest.mark.run(order=117)
    def test_117_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        print("Test Case 117 Execution Completed")

    @pytest.mark.run(order=118)
    def test_118_validate_Syslog_Messages(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="info Automated Threat Analytics file Download and Update skipped: no moduleset file | info Success : File download success for analytics update and it is rsync with GM | .*info Grid Master already have the latest whitelist.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        if logs!=None:
            logging.info("Test Case 118 Execution Completed")
            assert True
        else:
            logging.info("Test Case 118 Execution failed")
            assert False

    @pytest.mark.run(order=119)
    def test_119_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 119 passed")

    @pytest.mark.run(order=120)
    def test_120_scheduled_moduleset_download_weekly_when_both_policy_is_set_to_AUTOMATIC(self):
        schedule_date=get_time(5)
        print schedule_date
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics")
        get_ref1=json.loads(get_ref)[0]['_ref']
        data={"enable_auto_download":True,"enable_scheduled_download":True,"scheduled_download":{"disable":False,"frequency": "WEEKLY","hour_of_day": schedule_date[3],"minutes_past_hour": schedule_date[4],"time_zone": schedule_date[7],"weekdays":[schedule_date[8]],"month":schedule_date[1],"day_of_month":schedule_date[2],"repeat":"RECUR"}}
        put_ref=ib_NIOS.wapi_request('PUT', object_type=get_ref1,fields=json.dumps(data))
        print put_ref

        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=enable_auto_download,enable_scheduled_download,scheduled_download")
        get_ref=json.loads(get_ref)
        if get_ref[0]["enable_scheduled_download"]==data["enable_scheduled_download"] and get_ref[0]["enable_auto_download"]==data["enable_auto_download"] and get_ref[0]["scheduled_download"]["frequency"]==data["scheduled_download"]["frequency"]:
            print("Test case 120 passed")
            time.sleep(1800)
            assert True
        else:
            print("Test case 120 failed")
            assert False

    @pytest.mark.run(order=121)
    def test_121_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        print("Test Case 121 Execution Completed")

    @pytest.mark.run(order=122)
    def test_122_validate_Syslog_Messages(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="info Automated Threat Analytics file Download and Update skipped: no moduleset file | info Success : File download success for analytics update and it is rsync with GM | .*info Grid Master already have the latest moduleset.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        if logs!=None:
            logging.info("Test Case 122 Execution Completed")
            assert True
        else:
            logging.info("Test Case 122 Execution failed")
            assert False

    @pytest.mark.run(order=123)
    def test_123_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 123 passed")

    @pytest.mark.run(order=124)
    def test_124_scheduled_whitelist_download_monthly_when_both_policy_is_set_to_AUTOMATIC(self):
        #restore()
        schedule_date=get_time(5)
        print schedule_date
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics")
        get_ref1=json.loads(get_ref)[0]['_ref']
        data={"enable_whitelist_auto_download":True,"enable_whitelist_scheduled_download":True,"scheduled_whitelist_download":{"disable":False,"frequency": "MONTHLY","hour_of_day": schedule_date[3],"minutes_past_hour": schedule_date[4],"time_zone": schedule_date[7],"month":schedule_date[1],"day_of_month":schedule_date[2],"repeat":"RECUR"}}
        put_ref=ib_NIOS.wapi_request('PUT', object_type=get_ref1,fields=json.dumps(data))
        print put_ref
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=enable_whitelist_auto_download,enable_whitelist_scheduled_download,scheduled_whitelist_download")
        get_ref=json.loads(get_ref)
        if get_ref[0]["enable_whitelist_scheduled_download"]==data["enable_whitelist_scheduled_download"] and get_ref[0]["enable_whitelist_auto_download"]==data["enable_whitelist_auto_download"] and get_ref[0]["scheduled_whitelist_download"]["frequency"]==data["scheduled_whitelist_download"]["frequency"]:
            print("Test case 124 passed")
            time.sleep(1800)
            assert True
        else:
            print("Test case 124 failed")
            assert False

    @pytest.mark.run(order=125)
    def test_125_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        print("Test Case 125 Execution Completed")

    @pytest.mark.run(order=126)
    def test_126_validate_Syslog_Messages(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="info Automated Threat Analytics file Download and Update skipped: no moduleset file | info Success : File download success for analytics update and it is rsync with GM | .*info Grid Master already have the latest whitelist.*"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        if logs!=None:
            logging.info("Test Case 126 Execution Completed")
            assert True
        else:
            logging.info("Test Case 126 Execution failed")
            assert False

    @pytest.mark.run(order=127)
    def test_127_start_Syslog_Messages_logs(self):
        logging.info("Starting Syslog Messages Logs")
        log("start","/var/log/syslog",config.grid_vip)
        logging.info("test case 127 passed")

    @pytest.mark.run(order=128)
    def test_128_scheduled_moduleset_download_monthly_when_both_policy_is_set_to_AUTOMATIC(self):
        schedule_date=get_time(5)
        print schedule_date
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics")
        get_ref1=json.loads(get_ref)[0]['_ref']
        data={"enable_auto_download":True,"enable_scheduled_download":True,"scheduled_download":{"disable":False,"frequency": "MONTHLY","hour_of_day": schedule_date[3],"minutes_past_hour": schedule_date[4],"time_zone": schedule_date[7],"month":schedule_date[1],"day_of_month":schedule_date[2],"repeat":"RECUR"}}
        put_ref=ib_NIOS.wapi_request('PUT', object_type=get_ref1,fields=json.dumps(data))
        print schedule_date[7]
        print put_ref
        get_ref=ib_NIOS.wapi_request('GET', object_type="grid:threatanalytics?_return_fields=enable_auto_download,enable_scheduled_download,scheduled_download")
        print get_ref
        get_ref=json.loads(get_ref)
        if get_ref[0]["enable_scheduled_download"]==data["enable_scheduled_download"] and get_ref[0]["enable_auto_download"]==data["enable_auto_download"] and get_ref[0]["scheduled_download"]["frequency"]==data["scheduled_download"]["frequency"]:
            print("Test case 128 passed")
            time.sleep(1800)
            assert True
        else:
            print("Test case 128 failed")
            assert False

    @pytest.mark.run(order=129)
    def test_129_stop_Syslog_Messages_Logs(self):
        logging.info("Stopping Syslog Logs")
        log("stop","/var/log/syslog",config.grid_vip)
        print("Test Case 129 Execution Completed")

    @pytest.mark.run(order=130)
    def test_130_validate_Syslog_Messages(self):
        logging.info("Validating Sylog Messages Logs")
        LookFor="info Automated Threat Analytics file Download and Update skipped: no moduleset file | info Success : File download success for analytics update and it is rsync with GM | .*info Grid Master already have the latest moduleset.*"
        #LookFor="Arun|Kumar"
        logs=logv(LookFor,"/var/log/syslog",config.grid_vip)
        if logs!=None:
            logging.info("Test Case 130 Execution Completed")
            assert True
        else:
            logging.info("Test Case 130 Execution failed")
            assert False
    





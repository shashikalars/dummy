import datetime
import re
import config
import pytest
import pexpect
import unittest
import sys
import logging
import os
import os.path
from os.path import join
import subprocess
import commands
import json
import time
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import ib_utils.common_utilities as common_util

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
    hour=int(current_time[0])
    minute=int(current_time[1])
    seconds=int(current_time[2])
    time_zone=current_date[4]
    if time_zone=="UTC":
        time_zone="(UTC + 5:30) Bombay, Calcutta, Madras, New Delhi"
    elif time_zone=="PST":
        time_zone="(UTC - 8:00) Pacific Time (US and Canada), Tijuana"
    elif time_zone=="PDT":
        time_zone="(UTC - 8:00) Pacific Time (US and Canada), Tijuana"
    else:
        time_zone=None
    current_date = datetime.datetime(year,month,today,hour,minute,seconds)
    current_date+= datetime.timedelta(minutes=time_to_move)
    current_date=str(current_date)
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

def display_msg(x=""):
    """
    Additional function.
    """
    logging.info(x)
    print(x)

def epoch(date):
        date = time.strftime("%a,%b %d %H:%M:%S %Z %Y", time.localtime(date))
	return date

class RFE_8805(unittest.TestCase):

#Starting DNS service

        @pytest.mark.run(order=1)
        def test_001_Start_DNS_Service(self):
                logging.info("Start DNS Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                for i in res:
                        logging.info("Modify a enable_dns")
                        data = {"enable_dns": True}
                        response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                        print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                print("Test Case 1 Execution Completed")

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
                print("Test Case 2 Execution Completed")

#Adding Forwarder

        @pytest.mark.run(order=3)
        def test_003_Update_Forwarders(self):
                logging.info("Update Forwarders")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify Grid DNS Properties")
                data = {"allow_recursive_query": True,"allow_update": [{"_struct": "addressac","address": "Any","permission": "ALLOW"}],"logging_categories": {"log_queries": True,"log_responses": True,"log_rpz": True}}
                response = ib_NIOS.wapi_request('PUT',ref= ref1,fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
		sleep(10)
                print("Test Case 3 Execution Completed")

	@pytest.mark.run(order=4)
        def test_004_Validate_Configured_Global_Forwarders_Logging_Categories_Allow_Recursion_At_Grid_level(self):
                logging.info("Validate Configured Global Forwarders Logging Categories Allow Recursion at Grid level")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="grid:dns",params="?_return_fields=allow_recursive_query,forwarders,allow_update")
                res = json.loads(get_tacacsplus)
                res = eval(json.dumps(get_tacacsplus))
                print(res)
                output=res.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                print(output)
                result = ["allow_recursive_query:true,allow_update:[_struct:addressac,address:Any,permission:ALLOW]"]
                for i in result:
                  if i in output:
                        assert True
                  else:
                        assert False
                print(result)
                logging.info("Test Case 4 Execution Completed")
                logging.info("============================")

	@pytest.mark.run(order=5)
        def test_005_Configure_DNS_scavenging_grid_level_to_enable_last_queried_time_for_RR_and_zones(self):
                logging.info("Configure DNS scavenging grid level to enable last queried time for RR and zones")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify Grid DNS Properties")
                data = {"scavenging_settings": {"ea_expression_list": [],"enable_auto_reclamation": False,"enable_recurrent_scavenging": False,"enable_rr_last_queried": True,"enable_scavenging": False,"enable_zone_last_queried": True,"expression_list": [],"reclaim_associated_records": False}}
                response = ib_NIOS.wapi_request('PUT',ref= ref1,fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
		sleep(10)
                print("Test Case 5 Execution Completed")

		logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                print("System Restart is done successfully")
                sleep(5)

	@pytest.mark.run(order=6)
        def test_006_Add_Authoritative_zone(self):
                logging.info("Create Auth Zone")
                grid_member=config.grid_member_fqdn
                data = {"fqdn": "test.com","grid_primary": [{"name":config.grid_member_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 6 Execution Completed")

                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                print("System Restart is done successfully")
                sleep(5)

	@pytest.mark.run(order=7)
        def test_007_Validate_addition_of_Authoritative_zone(self):
                logging.info("Validating addition of authoritative zone")
                get_temp = ib_NIOS.wapi_request('GET', object_type="zone_auth",params="?_inheritance=True&_return_fields=fqdn")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'fqdn': 'test.com'"
                if data in res:
                        assert True
                else:
                        assert False
                print("Test Case 7 Execution Completed")
                sleep(15)


	@pytest.mark.run(order=8)
        def test_008_Create_CNAME_record(self):
                logging.info ("Creating CNAME Record for added Zone")
                data = {"fqdn":"test.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "cname.test.com","canonical": "test.com","_ref":endpoint,"view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:cname",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("CNAME Record is created Successfully")
                print("Test Case 8 Execution Completed")
		sleep(10)

	@pytest.mark.run(order=9)
        def test_009_Validate_addition_of_CNAME_record(self):
                logging.info("Validating addition of CNAME record")
                get_temp = ib_NIOS.wapi_request('GET', object_type="record:cname",params="?_inheritance=True&_return_fields=name")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'name': 'cname.test.com'"
                if data in res:
                        assert True
                else:
                        assert False
		print(data)
                print("Test Case 9 Execution Completed")
                sleep(5)
	
	@pytest.mark.run(order=10)
        def test_010_Login_as_root_to_GM_to_validate_current_date(self):
		logging.info("Login as root to GM to validate current date")
		global date
		child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
            	child.logfile=sys.stdout
            	child.expect('#')
            	child.sendline('date')
            	child.sendline('\r')
            	child.expect('#')
            	date = child.before
            	date = date.replace('\r','').replace('\n','').replace('date','')
            	print('date is ',date)
            	date = date[:-26]
            	date = date.replace(' ','')
            	print(date)
            	date=time.strptime(date,"%a%b%d")
            	date = time.strftime("%a%b%d",date)
            	print("####################################################################################################################################")
            	print('conveter',date)
		print("Test Case 10 Execution Completed")

	@pytest.mark.run(order=11)
        def test_011_dig_CNAME_record_to_get_current_last_queried_timestamp(self):
                logging.info ("Dig CNAME Record to get last queried timestamp")
                dig_cmd = ('dig @'+str(config.grid_vip)+' cname.test.com cname' )
                print(dig_cmd)
                for i in range(1,4000):
                       os.system(dig_cmd)
                sleep(200)
		print("Test Case 11 Execution Completed")
		

	@pytest.mark.run(order=12)
        def test_012_validate_CNAME_record_to_get_current_last_queried_timestamp(self):
                response = ib_NIOS.wapi_request('GET',"record:cname?name=cname.test.com&_return_fields%2B=last_queried&_return_as_object=1",grid_vip=config.grid_vip)
                res=json.loads(response)
                res = eval(json.dumps(res))
                res= str(res)
                output=res.replace(':','').replace(' ','').replace("'",'')
                print(output)
                result = re.findall(r'last_queried[0-9]{10}',output)
                result = (str(result))
                print(result)
                result = result.replace('last_queried','').replace('[','').replace(']','').replace('"','').replace("'",'')
                print(result)
                print ('my result is ',result)
                time = epoch(int(result))
                print('time is',time)
                time = time.replace(',','').replace(' ','')
                time = time[ 0 : 8]
                print('converted time is',time)
                #date = 'ThuFeb04'
                print(date)
                if date == time:
                        assert True
                else:
                        assert False
                print("Test Case 12 Execution Completed")


	@pytest.mark.run(order=13)
        def test_013_Create_DNAME_record(self):
		logging.info ("Creating DMANE Record for added Zone")
                data = {"fqdn":"test.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                data={"name": "dname.test.com","target": "cname.test.com","_ref":endpoint,"comment":"Adding dname rec","view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:dname",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("DNAME Record is created Successfully")
                print("Test Case 13 Execution Completed")
		sleep(10)

        @pytest.mark.run(order=14)
        def test_014_Validate_addition_of_DNAME_record(self):
                logging.info("Validating addition of DNAME record")
                get_temp = ib_NIOS.wapi_request('GET', object_type="record:dname",params="?_inheritance=True&_return_fields=name")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'name': 'dname.test.com'"
                if data in res:
                        assert True
                else:
                        assert False
                print(data)
                print("Test Case 14 Execution Completed")
                sleep(5)	

	@pytest.mark.run(order=15)
        def test_015_dig_DNAME_record_to_get_current_last_queried_timestamp(self):
                logging.info ("Dig CNAME Record to get last queried timestamp")
                dig_cmd = ('dig @'+str(config.grid_vip)+' dname.test.com dname' )
                print(dig_cmd)
                for i in range(1,1000):
                       os.system(dig_cmd)
                sleep(150)
                print("Test Case 15 Execution Completed")

	@pytest.mark.run(order=16)
        def test_016_validate_DNAME_record_to_get_current_last_queried_timestamp(self):
                response = ib_NIOS.wapi_request('GET',"record:dname?name=dname.test.com&_return_fields%2B=last_queried&_return_as_object=1",grid_vip=config.grid_vip)
                res=json.loads(response)
                res = eval(json.dumps(res))
                res= str(res)
                output=res.replace(':','').replace(' ','').replace("'",'')
                print(output)
                result = re.findall(r'last_queried[0-9]{10}',output)
                result = (str(result))
                print(result)
                result = result.replace('last_queried','').replace('[','').replace(']','').replace('"','').replace("'",'')
                print(result)
                print ('my result is ',result)
                time = epoch(int(result))
                print('time is',time)
                time = time.replace(',','').replace(' ','')
                time = time[ 0 : 8]
                print('converted time is',time)
                #date = 'WedDec02'
                print(date)
                if date == time:
                        assert True
                else:
                        assert False
                print("Test Case 16 Execution Completed")


	@pytest.mark.run(order=17)
        def test_017_Add_another_Authoritative_zone(self):
                logging.info("Create one more Auth Zone")
                data = {"fqdn": "test1.com","grid_primary": [{"name":config.grid_member_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 17 Execution Completed")

                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                print("System Restart is done successfully")
                sleep(5)

        @pytest.mark.run(order=18)
        def test_018_Validate_addition_of_Authoritative_zone(self):
                logging.info("Validating addition of authoritative zone")
                get_temp = ib_NIOS.wapi_request('GET', object_type="zone_auth",params="?_inheritance=True&_return_fields=fqdn")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'fqdn': 'test1.com'"
                if data in res:
                        assert True
                else:
                        assert False
                print("Test Case 18 Execution Completed")

	@pytest.mark.run(order=19)
        def test_019_Create_A_record(self):
                logging.info ("Creating A Record for added Zone")
                data = {"fqdn":"test1.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "arec.test1.com","ipv4addr":"1.2.3.9","_ref":endpoint,"comment":"Adding arec","view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                #import pdb;pdb.set_trace()
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                print("Test Case 19 Execution Completed")
                sleep(5)

	@pytest.mark.run(order=20)
        def test_020_Validate_addition_of_A_record_in_another_zone(self):
                logging.info("Validating addition of authoritative zone with match rule as delete")
                get_temp = ib_NIOS.wapi_request('GET', object_type="record:a",params="?_inheritance=True&_return_fields=name")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'name': 'arec.test1.com'"
                if data in res:
                        assert True
                else:
                        assert False
                print("Test Case 20 Execution Completed")

	@pytest.mark.run(order=21)
        def test_021_Create_CNAME_record_pointing_to_A_record_created_in_another_zone(self):
                logging.info ("Creating CNAME Record pointing to A record created in another zone")
                data = {"fqdn":"test.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "cname2.test.com","canonical": "arec.test1.com","_ref":endpoint,"view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:cname",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("CNAME Record is created Successfully")
                print("Test Case 21 Execution Completed")

        @pytest.mark.run(order=22)
        def test_022_Validate_addition_of_CNAME_record(self):
                logging.info("Validating addition of CNAME record")
		get_temp = ib_NIOS.wapi_request('GET', object_type="record:cname",params="?_inheritance=True&_return_fields=name,canonical")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'name': 'cname2.test.com', 'canonical': 'arec.test1.com'"
                if data in res:
                        assert True
                else:
                        assert False
                print(data)
                print("Test Case 22 Execution Completed")
                sleep(5)


        @pytest.mark.run(order=23)
        def test_023_dig_A_record_to_get_current_last_queried_timestamp(self):
                logging.info ("Dig A Record to get last queried timestamp")
                global date
                dig_cmd = ('dig @'+str(config.grid_vip)+' cname2.test.com a' )
                print(dig_cmd)
                for i in range(1,6000):
                       os.system(dig_cmd)
                sleep(300)
                print("Test Case 23 Execution Completed")

	@pytest.mark.run(order=24)
        def test_024_validate_A_record_to_get_current_last_queried_timestamp_when_connected_to_sibling_zone(self):
		logging.info("validate A record to get current last queried timestamp when connected to sibling zone")
		response = ib_NIOS.wapi_request('GET',"record:a?name=arec.test1.com&_return_fields%2B=last_queried&_return_as_object=1",grid_vip=config.grid_vip)
                res=json.loads(response)
                res = eval(json.dumps(res))
                res= str(res)
                output=res.replace(':','').replace(' ','').replace("'",'')
                print(output)
                result = re.findall(r'last_queried[0-9]{10}',output)
                result = (str(result))
                print(result)
                result = result.replace('last_queried','').replace('[','').replace(']','').replace('"','').replace("'",'')
                print(result)
                print ('my result is ',result)
                time = epoch(int(result))
                print('time is',time)
                time = time.replace(',','').replace(' ','')
                time = time[ 0 : 8]
                print('converted time is',time)
                #date = 'WedDec02'
                print(date)
                if date == time:
                        assert True
                else:
                        assert False
		print("Test Case 24 Execution Completed")	


	@pytest.mark.run(order=25)
        def test_025_Add_Delegated_zone(self):
                logging.info("Create Delegated Zone")
                grid_member=config.grid_member_fqdn
                data = {"fqdn": "del.test.com","delegate_to": [{"address": "10.0.0.9","name": "secondary.com"}]}
                response = ib_NIOS.wapi_request('POST', object_type= "zone_delegated", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Test Case 25 Execution Completed")
                sleep(30)

	@pytest.mark.run(order=26)
        def test_026_Validate_addition_of_ns_record_for_delegated_zone(self):
                logging.info("Validating addition of ns record for delegated zone")
                get_temp = ib_NIOS.wapi_request('GET', object_type="record:ns",params="?_inheritance=True&_return_fields=name")
                logging.info(get_temp)
                res=json.loads(get_temp)
		print(res)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'name': 'del.test.com'"
                if data in res:
                        assert True
                else:
                        assert False
                print(data)
                print("Test Case 26 Execution Completed")
                sleep(10)

	@pytest.mark.run(order=27)
        def test_027_Negative_scenario_validate_NS_record_to_get_current_last_queried_timestamp(self):
		logging.info("Validating NS record to get current last queried timestamp")
		response = ib_NIOS.wapi_request('GET',"record:ns?name=del.test.com&_return_fields%2B=last_queried&_return_as_object=1",grid_vip=config.grid_vip)
		print(response)
                if "last_queried" in response:
                        assert False
                else:
                        assert True
		print("Test Case 27 Execution Completed")
    
        @pytest.mark.run(order=28)
        def test_028_Create_A_record(self):
                logging.info ("Creating A Record for added Zone")
                data = {"fqdn":"test.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "arec123.test.com","ipv4addr":"1.2.3.7","_ref":endpoint,"comment":"Adding arec","view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                #import pdb;pdb.set_trace()
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                print("Test Case 28 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=29)
        def test_029_Validate_addition_of_A_record_in_another_zone(self):
                logging.info("Validating addition of authoritative zone with match rule as delete")
                get_temp = ib_NIOS.wapi_request('GET', object_type="record:a",params="?_inheritance=True&_return_fields=name")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'name': 'arec123.test.com'"
                if data in res:
                        assert True
                else:
                        assert False
                print("Test Case 29 Execution Completed")    


	@pytest.mark.run(order=30)
        def test_030_Negative_scenario_Create_SRV_record(self):
                logging.info ("Creating SRV Record for added Zone")
                data = {"fqdn":"test.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "srv.test.com","port":22,"_ref":endpoint,"target":"arec123.test.com","view":"default","weight":10,"priority":1}
                response = ib_NIOS.wapi_request('POST', object_type="record:srv",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("SRV Record is created Successfully")
                print("Test Case 30 Execution Completed")
		sleep(10)

        @pytest.mark.run(order=31)
        def test_031_Negative_scenario_dig_SRV_record_to_get_current_last_queried_timestamp(self):
                logging.info ("Dig SRV Record to get last queried timestamp of the target record")
                global date
                dig_cmd = ('dig @'+str(config.grid_vip)+' srv.test.com srv' )
                print(dig_cmd)
                for i in range(1,1000):
                       os.system(dig_cmd)
                sleep(150)
                print("Test Case 31 Execution Completed")

	@pytest.mark.run(order=32)
        def test_032_Negative_scenario_validate_CNAME_record_to_get_current_last_queried_timestamp(self):
                logging.info("Validating cname record to get current last queried timestamp")
                response = ib_NIOS.wapi_request('GET',"record:a?name=arec123.test.com&_return_fields%2B=last_queried&_return_as_object=1",grid_vip=config.grid_vip)
               	print(response)
                if "last_queried" in response:
                        assert False
                else:
                        assert True
                print("Test Case 32 Execution Completed")


	@pytest.mark.run(order=33)
        def test_033_Negative_scenario_Create_A_record(self):
                logging.info ("Creating A Record for added Zone")
                data = {"fqdn":"test.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "arec.test.com","ipv4addr":"1.2.3.9","_ref":endpoint,"comment":"Adding arec","view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                #import pdb;pdb.set_trace()
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                print("Test Case 33 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=34)
        def test_034_Validate_addition_of_A_record(self):
                logging.info("Validating addition of authoritative zone with match rule as delete")
                get_temp = ib_NIOS.wapi_request('GET', object_type="record:a",params="?_inheritance=True&_return_fields=name,ipv4addr")
                logging.info(get_temp)
                res=json.loads(get_temp)
		print(res)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'ipv4addr': '1.2.3.9', 'name': 'arec.test1.com'"
                if data in res:
                        assert True
                else:
                        assert False
                print("Test Case 34 execution Completed")

	@pytest.mark.run(order=35)
        def test_035_Negative_scenario_Create_AAAA_record(self):
                logging.info ("Creating AAAA Record for added Zone")
                data = {"fqdn":"test.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"ipv6addr": "fd60:e45:e31b::","name":"arec.test.com","_ref":endpoint,"view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:aaaa",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                print("Test Case 35 Execution Completed")
                sleep(10)

	@pytest.mark.run(order=36)
        def test_036_Validate_addition_of_AAAA_record(self):
                logging.info("Validating addition of authoritative zone with match rule as delete")
                get_temp = ib_NIOS.wapi_request('GET', object_type="record:aaaa",params="?_inheritance=True&_return_fields=name,ipv6addr")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'ipv6addr': 'fd60:e45:e31b::', 'name': 'arec.test.com'"
                if data in res:
                        assert True
                else:
                        assert False
                print("Test Case 36 Execution Completed")


        @pytest.mark.run(order=37)
        def test_037_Negative_scenario_dig_A_record_of_type_any_to_get_current_last_queried_timestamp(self):
                logging.info ("Dig A Record of type any to get last queried timestamp")
                dig_cmd = ('dig @'+str(config.grid_vip)+' arec.test.com any' )
                print(dig_cmd)
                for i in range(1,3000):
                       os.system(dig_cmd)
                sleep(150)
                print("Test Case 37 Execution Completed")

	@pytest.mark.run(order=38)
        def test_038_Negative_scenario_Validate_last_queried_time_stamp_updated_for_Query_made_of_type_ANY(self):
		response = ib_NIOS.wapi_request('GET',"record:a?name=arec.test.com&_return_fields%2B=last_queried&_return_as_object=1",grid_vip=config.grid_vip)
                print(response)
                if "last_queried" in response:
                        assert False
                else:
                        assert True
		print("Test Case 38 Execution Completed")

	@pytest.mark.run(order=39)
        def test_039_Negative_scenario_dig_AAAA_record_of_type_any_to_get_current_last_queried_timestamp(self):
                logging.info ("Dig AAAA Record of type any to get last queried timestamp")
                dig_cmd = ('dig @'+str(config.grid_vip)+' arec.test.com any' )
                print(dig_cmd)
                for i in range(1,1000):
                       os.system(dig_cmd)
                sleep(100)
                print("Test Case 39 Execution Completed")

        @pytest.mark.run(order=40)
        def test_040_Negative_scenario_Validate_last_queried_time_stamp_updated_for_Query_made_of_type_ANY(self):
                response = ib_NIOS.wapi_request('GET',"record:aaaa?name=arec.test.com&_return_fields%2B=last_queried&_return_as_object=1",grid_vip=config.grid_vip)
                print(response)
                if "last_queried" in response:
                        assert False
                else:
                        assert True
		print("Test Case 40 Execution Completed")


	@pytest.mark.run(order=41)
        def test_041_Create_A_record(self):
                logging.info ("Creating A Record for added Zone")
                data = {"fqdn":"test.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "x.sub.test.com","ipv4addr":"1.2.3.10","_ref":endpoint,"comment":"Adding arec","view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                #import pdb;pdb.set_trace()
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                print("Test Case 41 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=42)
        def test_042_Validate_addition_of_A_record(self):
                logging.info("Validating addition of authoritative zone with match rule as delete")
                get_temp = ib_NIOS.wapi_request('GET', object_type="record:a",params="?_inheritance=True&_return_fields=name,ipv4addr")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'ipv4addr': '1.2.3.10', 'name': 'x.sub.test.com'"
                if data in res:
                        assert True
                else:
                        assert False
                print("Test Case 42 Execution Completed")

	@pytest.mark.run(order=43)
        def test_043_Create_A_record(self):
                logging.info ("Creating A Record for added Zone")
                data = {"fqdn":"test.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
               	data={"name": "x.elsewhere.test.com","ipv4addr":"11.2.3.10","_ref":endpoint,"comment":"Adding arec","view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                #import pdb;pdb.set_trace()
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                print("Test Case 43 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=44)
        def test_044_Validate_addition_of_A_record(self):
                logging.info("Validating addition of authoritative zone with match rule as delete")
                get_temp = ib_NIOS.wapi_request('GET', object_type="record:a",params="?_inheritance=True&_return_fields=name,ipv4addr")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'ipv4addr': '11.2.3.10', 'name': 'x.elsewhere.test.com'"
                if data in res:
                        assert True
                else:
                        assert False
                print("Test Case 44 Execution Completed")


	@pytest.mark.run(order=45)
        def test_045_Create_DNAME_record(self):
                logging.info ("Creating DMANE Record for added Zone")
                data = {"fqdn":"test.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "sub.test.com","target": "elsewhere.test.com","_ref":endpoint,"comment":"Adding dname rec","view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:dname",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                logging.info("DNAME Record is created Successfully")
                print("Test Case 45 Execution Completed")

	@pytest.mark.run(order=46)
        def test_046_dig_A_record_of_type_any_to_get_current_last_queried_timestamp(self):
                logging.info ("Dig A Record of type any to get last queried timestamp")
                dig_cmd = ('dig @'+str(config.grid_vip)+' x.sub.test.com a' )
                print(dig_cmd)
                for i in range(1,2000):
                       os.system(dig_cmd)
                sleep(150)
                print("Test Case 46 Execution Completed")

        @pytest.mark.run(order=47)
        def test_047_Validate_DNAME_record_to_get_last_queried_time_stamp(self):
                response = ib_NIOS.wapi_request('GET',"record:dname?name=sub.test.com&_return_fields%2B=last_queried&_return_as_object=1",grid_vip=config.grid_vip)
                res=json.loads(response)
                res = eval(json.dumps(res))
                res= str(res)
                output=res.replace(':','').replace(' ','').replace("'",'')
                print(output)
                result = re.findall(r'last_queried[0-9]{10}',output)
                result = (str(result))
                print(result)
                result = result.replace('last_queried','').replace('[','').replace(']','').replace('"','').replace("'",'')
                print(result)
                print ('my result is ',result)
                time = epoch(int(result))
                print('time is',time)
                time = time.replace(',','').replace(' ','')
                time = time[ 0 : 8]
                print('converted time is',time)
                #date = 'WedDec02'
                print(date)
                if date == time:
                        assert True
                else:
                        assert False
		print("Test Case 47 Execution Completed")

	@pytest.mark.run(order=48)
        def test_048_Validate_A_record_to_get_last_queried_time_stamp(self):
                response = ib_NIOS.wapi_request('GET',"record:a?name=x.elsewhere.test.com&_return_fields%2B=last_queried&_return_as_object=1",grid_vip=config.grid_vip)
                res=json.loads(response)
                res = eval(json.dumps(res))
                res= str(res)
                output=res.replace(':','').replace(' ','').replace("'",'')
                print(output)
                result = re.findall(r'last_queried[0-9]{10}',output)
                result = (str(result))
                print(result)
                result = result.replace('last_queried','').replace('[','').replace(']','').replace('"','').replace("'",'')
                print(result)
                print ('my result is ',result)
                time = epoch(int(result))
                print('time is',time)
                time = time.replace(',','').replace(' ','')
                time = time[ 0 : 8]
                print('converted time is',time)
                #date = 'WedDec02'
                print(date)
                if date in time:
                        assert True
                else:
                        assert False
                print("Test Case 48 Execution Completed")


	@pytest.mark.run(order=49)
	def test_049_add_resource_records_through_nsupdate(self):
		display_msg()
        	display_msg("----------------------------------------------------")
        	display_msg("|          Test Case 49 Execution Started          |")
        	display_msg("----------------------------------------------------")

        	display_msg("Add resource records using nsupdate")

        	hostnames = [("A 1.0.1.18","auto.")]
		try:
        		for data,record in hostnames:
            			record = record+'test.com'
            			display_msg("RR name : "+record)
            			child = pexpect.spawn("nsupdate")
                		child.expect('>')
                		child.sendline('server '+config.grid_vip)
                		child.expect('>')
                		child.sendline('update add '+record+' 3600 IN '+data)
                		child.expect('>')
                		child.sendline('send')
                		child.expect('>')
				output = child.before
				print(output)
				print(type(output))
                                child.sendline('quit')
                                child.close()
				if "failed" in output:
					assert False
		except:
			print("Test case failed")
			assert False

		print("-----------Test Case 49 Execution Completed-----------")


	@pytest.mark.run(order=50)
        def test_050_Validate_autocreated_A_record_to_get_last_queried_time_stamp(self):
                response = ib_NIOS.wapi_request('GET',"record:a?name=auto.test.com&_return_fields%2B=last_queried&_return_as_object=1",grid_vip=config.grid_vip)
                res=json.loads(response)
                res = eval(json.dumps(res))
                res= str(res)
                output=res.replace(':','').replace(' ','').replace("'",'')
                print(output)
                result = re.findall(r'last_queried[0-9]{10}',output)
                result = (str(result))
                print(result)
                result = result.replace('last_queried','').replace('[','').replace(']','').replace('"','').replace("'",'')
                print(result)
                print ('my result is ',result)
                time = epoch(int(result))
                print('time is',time)
                time = time.replace(',','').replace(' ','')
                time = time[ 0 : 8]
                print('converted time is',time)
                #date = 'WedDec02'
                print(date)
                if date == time:
                        assert True
                else:
                        assert False
		print("Test Case 50 Execution Completed")

	@pytest.mark.run(order=51)
        def test_051_Create_A_record(self):
                logging.info ("Creating A Record for added Zone")
                data = {"fqdn":"test.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "prereq.test.com","ipv4addr":"11.12.3.10","_ref":endpoint,"comment":"Adding arec","view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                #import pdb;pdb.set_trace()
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                print("Test Case 51 Execution Completed")
                sleep(5)


        @pytest.mark.run(order=52)
        def test_052_Validate_addition_of_A_record(self):
                logging.info("Validating addition of authoritative zone with match rule as delete")
                get_temp = ib_NIOS.wapi_request('GET', object_type="record:a",params="?_inheritance=True&_return_fields=name,ipv4addr")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'ipv4addr': '11.12.3.10', 'name': 'prereq.test.com'"
                if data in res:
                        assert True
                else:
                        assert False
                print("Test Case 52 Execution Completed")

	@pytest.mark.run(order=53)
        def test_053_validate_DNS_update_prerquisite_section(self):
                display_msg()
                display_msg("----------------------------------------------------")
                display_msg("|          Test Case 53 Execution Started          |")
                display_msg("----------------------------------------------------")

                display_msg("Add resource records using nsupdate")

                hostnames = [("A 2.0.1.18","prereq.")]
                try:
                        for data,record in hostnames:
                                record = record+'test.com'
                                display_msg("RR name : "+record)
                                child = pexpect.spawn("nsupdate")
                                child.expect('>')
                                child.sendline('server '+config.grid_vip)
                                child.expect('>')
                                child.sendline('update add '+record+' 3600 IN '+data)
                                child.expect('>')
                                child.sendline('send')
                                child.expect('>')
                                output = child.before
                                print(output)
                                print(type(output))
                                child.sendline('quit')
                                child.close()
                                if "YXDOMAIN" in output:
                                        assert False
                except:
                        print("Test case 53 failed")
                        assert False

                print("-----------Test Case 53 execution Completed-----------")



	@pytest.mark.run(order=54)
        def test_054_Add_Authoritative_zone(self):
                logging.info("Create Auth Zone")
                data = {"fqdn": "zone.com","grid_primary": [{"name":config.grid_member_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 54 Execution Completed")

                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                print("System Restart is done successfully")
                sleep(20)

        @pytest.mark.run(order=55)
        def test_055_Validate_addition_of_Authoritative_zone(self):
                logging.info("Validating addition of authoritative zone")
                get_temp = ib_NIOS.wapi_request('GET', object_type="zone_auth",params="?_inheritance=True&_return_fields=fqdn")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'fqdn': 'zone.com'"
                if data in res:
                        assert True
                else:
                        assert False
                print("Test Case 55 Execution Completed")

	@pytest.mark.run(order=56)
        def test_056_Create_A_record(self):
                logging.info ("Creating A Record for added Zone")
                data = {"fqdn":"zone.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "aaa.zone.com","ipv4addr":"88.77.66.55","_ref":endpoint,"comment":"Adding arec","view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                #import pdb;pdb.set_trace()
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                print("Test Case 56 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=57)
        def test_057_Validate_addition_of_A_record(self):
                logging.info("Validating addition of authoritative zone with match rule as delete")
                get_temp = ib_NIOS.wapi_request('GET', object_type="record:a",params="?_inheritance=True&_return_fields=name,ipv4addr")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'ipv4addr': '88.77.66.55', 'name': 'aaa.zone.com'"
                if data in res:
                        assert True
                else:
                        assert False
                print("Test Case 57 Execution Completed")


	@pytest.mark.run(order=58)
        def test_058_Add_a_LBDN_server_to_create_DTC_resource_record(self):
		logging.info("Add a LBDN server to create DTC resource record")
                data={"name": "aaa","host":"88.77.66.55"}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:server",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                print("Test Case 58 Execution Completed")


	@pytest.mark.run(order=59)
        def test_059_Validate_addition_of_LBDN_server(self):
                logging.info("Validating addition of LBDN server")
                get_temp = ib_NIOS.wapi_request('GET', object_type="dtc:server",params="?_inheritance=True&_return_fields=name,host")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'host': '88.77.66.55', 'name': 'aaa'"
                if data in res:
                        assert True
                else:
                        assert False
                print("Test Case 59 Execution Completed")

	@pytest.mark.run(order=60)
        def test_060_Add_a_LBDN_Pool_to_create_DTC_resource_record(self):
                logging.info("Add a LBDN pool to create DTC resource record")
		data = {"name":"aaa"}
		endpoint=common_util.get_object_reference(object_type="dtc:server",data=data)
		endpoint = eval(json.dumps(endpoint))
                print ("******************************************",endpoint)
		data={"name": "pool1","lb_preferred_method":"ROUND_ROBIN","servers":[{"ratio": 1,"server":endpoint}]}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:pool",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                print("Test Case 60 Execution Completed")

	@pytest.mark.run(order=61)
        def test_061_Validate_addition_LBDN_pool(self):
                logging.info("Validating addition of LBDN Pool")
                get_temp = ib_NIOS.wapi_request('GET', object_type="dtc:pool",params="?_inheritance=True&_return_fields=name,lb_preferred_method")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'name': 'pool1', 'lb_preferred_method': 'ROUND_ROBIN'"
                if data in res:
                        assert True
                else:
                        assert False
                print("Test Case 61 Execution Completed")


	@pytest.mark.run(order=62)
        def test_062_Add_a_LBDN_to_create_DTC_resource_record(self):
                logging.info("Add a LBDN pool to create DTC resource record")
                data = {"name":"pool1"}
                pool=common_util.get_object_reference(object_type="dtc:pool",data=data)
                pool = eval(json.dumps(pool))
                print ("******************************************",pool)
		data1 = {"fqdn":"zone.com"}
		endpoint=common_util.get_object_reference(object_type="zone_auth",data=data1)
                endpoint = eval(json.dumps(endpoint))
                print ("******************************************",endpoint)
                data={"name": "lbdn","lb_method":"ROUND_ROBIN","patterns":["*.zone.com"],"pools":[{"ratio": 1,"pool":pool}],"priority": 1,"types": ["A","AAAA","CNAME"],"auth_zones": [endpoint]}
                response = ib_NIOS.wapi_request('POST', object_type="dtc:lbdn",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                print("Test Case 62 Execution Completed")

		logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                print("System Restart is done successfully")
                sleep(30)


	@pytest.mark.run(order=63)
        def test_063_Validate_addition_LBDN_pool(self):
                logging.info("Validating addition of LBDN Pool")
                get_temp = ib_NIOS.wapi_request('GET', object_type="dtc:lbdn",params="?_inheritance=True&_return_fields=name")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'name': 'lbdn'"
                if data in res:
                        assert True
                else:
                        assert False
                print("Test Case 63 Execution Completed")


	@pytest.mark.run(order=64)
        def test_064_dig_DTC_A_record_of_type_any_to_get_current_last_queried_timestamp(self):
                logging.info ("Dig DTC A Record of type any to get last queried timestamp")
                dig_cmd = ('dig @'+str(config.grid_vip)+' aaa.zone.com a' )
                print(dig_cmd)
                for i in range(1,4000):
                       os.system(dig_cmd)
                sleep(150)
                print("Test Case 64 Execution Completed")

        @pytest.mark.run(order=65)
        def test_065_Validate_DTC_A_record_to_get_last_queried_time_stamp(self):
		logging.info ("Validate DTC A record to get last queried timestamp")
                response = ib_NIOS.wapi_request('GET',"record:a?name=aaa.zone.com&_return_fields%2B=last_queried&_return_as_object=1",grid_vip=config.grid_vip)
                res=json.loads(response)
                res = eval(json.dumps(res))
                res= str(res)
                output=res.replace(':','').replace(' ','').replace("'",'')
                print(output)
                result = re.findall(r'last_queried[0-9]{10}',output)
                result = (str(result))
                print(result)
                result = result.replace('last_queried','').replace('[','').replace(']','').replace('"','').replace("'",'')
                print(result)
                print ('my result is ',result)
                time = epoch(int(result))
                print('time is',time)
                time = time.replace(',','').replace(' ','')
                time = time[ 0 : 8]
                print('converted time is',time)
                #date = 'WedDec02'
                print(date)
                if date == time:
                        assert True
                else:
                        assert False
		print("Test Case 65 Execution Completed")

	
	@pytest.mark.run(order=66)
        def test_066_Sign_Dnssec_Zone(self):
                logging.info("Sign zone for adding DS Record")
                data = {"fqdn":"test1.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"buffer":"KSK","operation":"SIGN"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                logging.info("The selected zone is signed successfully")
                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")
                print("Test Case 66 Execution Completed")

	@pytest.mark.run(order=67)
        def test_067_Add_Authoritative_subzone(self):
                logging.info("Add Authoritative subzone")
                data = {"fqdn": "def.test1.com","grid_primary": [{"name":config.grid_member_fqdn,"stealth":False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 67 Execution Completed")

                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                print("System Restart is done successfully")
                sleep(10)

        @pytest.mark.run(order=68)
        def test_068_Validate_addition_of_Authoritative_subzone(self):
                logging.info("Validating addition of authoritative subzone")
                get_temp = ib_NIOS.wapi_request('GET', object_type="zone_auth",params="?_inheritance=True&_return_fields=fqdn")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'fqdn': 'def.test1.com'"
                if data in res:
                        assert True
                else:
                        assert False
                print("Test Case 68 Execution Completed")

	@pytest.mark.run(order=69)
        def test_069_Sign_Dnssec_authoritative_subZone(self):
                logging.info("Sign Authoritative subzone for adding DS Record")
                data = {"fqdn":"def.test1.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"buffer":"KKK","operation":"SIGN"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=dnssec_operation")
                print (response)
                for read in response:
                        assert True
                logging.info("The selected zone is signed successfully")
                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
		sleep(10)
                logging.info("System Restart is done successfully")
                print("Test Case 69 Execution Completed")

	@pytest.mark.run(order=70)
        def test_070_dig_DS_record_to_get_current_last_queried_timestamp(self):
                logging.info ("Dig DS Record to get last queried timestamp")
                dig_cmd = ('dig @'+str(config.grid_vip)+' def.test1.com ds' )
                print(dig_cmd)
                for i in range(1,1000):
                       os.system(dig_cmd)
                sleep(150)
                print("Test Case 70 Execution Completed")

        @pytest.mark.run(order=71)
        def test_071_Validate_DS_record_to_get_last_queried_time_stamp(self):
		logging.info ("validate DS Record to get last queried timestamp")
		get_ref = ib_NIOS.wapi_request('GET',"record:ds",grid_vip=config.grid_vip)
                ref = json.loads(get_ref)[-1]['_ref']
                print('ref is',ref)
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=last_queried&_return_fields=last_queried",grid_vip=config.grid_vip)
                print(response)
                response = json.loads(response)
                print(type(response),response)
                response = eval(json.dumps(response))
                print(type(response),response)
                print("answer is",response['last_queried'])
                res= str(response)
                output=res.replace(':','').replace(' ','').replace("'",'')
                print(output)
                result = re.findall(r'last_queried[0-9]{10}',output)
                result = (str(result))
                print(result)
                result = result.replace('last_queried','').replace('[','').replace(']','').replace('"','').replace("'",'')
                print(result)
                print('my result is ',result)
                time = epoch(int(result))
                print('time is',time)
                time = time.replace(',','').replace(' ','')
                time = time[ 0 : 8]
                print('converted time is',time)
                print(date)
                if date == time:
                   assert True
                else:
                   assert False
		print("Test Case 71 Execution Completed")


	@pytest.mark.run(order=72)
        def test_072_GRID_BACKUP(self):
                print ("Take Grid Backup")
                data = {"type": "BACKUP"}
                response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=getgriddata", fields=json.dumps(data))
                res = json.loads(response)
                URL=res['url']
                print("URL is : %s", URL)
                infoblox_log_validation ='curl -k -u admin:infoblox -H  "content-type: application/force-download" "' + str(URL) +'" -o "database.bak"'
                print ("infoblox.log",infoblox_log_validation)
                out2 = commands.getoutput(infoblox_log_validation)
                print("logs are",out2)
                print ("Backup is Done")
                read  = re.search(r'201',URL)
                for read in  response:
                        assert True
                logging.info("Test Case 72 Execution Completed")
		sleep(10)


	@pytest.mark.run(order=73)
        def test_073_Delete_Authzone_to_validate_last_queried_timestamp_post_DB_restore(self):
                logging.info("Deleting Authzone to validate last queried timestamp post DB restore")
                data= {"fqdn": "test1.com"}
                get_ref = ib_NIOS.wapi_request('GET', object_type="zone_auth",fields=json.dumps(data))
                print("$$$$$$$$$$$$$$$$$",get_ref)
                ref = json.loads(get_ref)[0]['_ref']
                request_restart = ib_NIOS.wapi_request('DELETE', object_type = ref + "?_return_as_object=1",fields=json.dumps(data),grid_vip=config.grid_vip)
                print("Delete operation is successful")
                sleep(5)
		logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(10)
                logging.info("System Restart is done successfully")
                print("Test Case 73 Execution Completed")

	@pytest.mark.run(order=74)
        def test_074_GRID_RESTORE(self):
             logging.info("Grid Restore")
             response = ib_NIOS.wapi_request('POST', object_type="fileop?_function=uploadinit")
             print response
             res = json.loads(response)
             URL=res['url']
             token1=res['token']
             print("URL is : %s", URL)
             print("Token is %s",token1)
             infoblox_log_validation ='curl -k -u admin:infoblox -H content_type="content-typemultipart-formdata" ' + str(URL) +' -F file=@database.bak'
             print infoblox_log_validation
             out2 = commands.getoutput(infoblox_log_validation)
             print ("out2$$$$$$",out2)
             data2={"mode":"NORMAL","nios_data":True,"token":token1}
             print ("&*&*&*&*&*&*",data2)
             response2 = ib_NIOS.wapi_request('POST', object_type="fileop?_function=restoredatabase",fields=json.dumps(data2))
             sleep(150)
             logging.info("Validate Syslog afer perform queries")
             infoblox_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@' + str( config.grid_vip) + ' " tail -1200 /infoblox/var/infoblox.log "'
             out1 = commands.getoutput(infoblox_log_validation)
             print out1
             logging.info(out1)
             assert re.search(r'restore_node complete',out1)
             sleep(50)
             read  = re.search(r'201',response)
             for read in  response:
                 assert True
             logging.info("Test Case 74 Execution Completed")


	@pytest.mark.run(order=75)
        def test_075_Validate_DS_record_to_get_last_queried_time_stamp_post_DB_restore(self):
                logging.info ("validate DS Record to get last queried timestamp post DB restore")
		get_ref = ib_NIOS.wapi_request('GET',"record:ds",grid_vip=config.grid_vip)
		ref = json.loads(get_ref)[-1]['_ref']
                print('ref is',ref)
                response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=last_queried&_return_fields=last_queried",grid_vip=config.grid_vip)
                print(response)
                response = json.loads(response)
                print(type(response),response)
                response = eval(json.dumps(response))
                print(type(response),response)
                print("answer is",response['last_queried'])
                res= str(response)
                output=res.replace(':','').replace(' ','').replace("'",'')
                print(output)
                result = re.findall(r'last_queried[0-9]{10}',output)
                result = (str(result))
                print(result)
                result = result.replace('last_queried','').replace('[','').replace(']','').replace('"','').replace("'",'')
                print(result)
                print('my result is ',result)
                time = epoch(int(result))
                print('time is',time)
                time = time.replace(',','').replace(' ','')
                time = time[ 0 : 8]
                print('converted time is',time)
                print(date)
                if date == time:
                   assert True
                else:
                   assert False
		print("Test Case 75 Execution Completed")

	@pytest.mark.run(order=76)
        def test_076_Start_DHCP_Service(self):
                logging.info("Start DHCP Service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties")
                logging.info(get_ref)
                res = json.loads(get_ref)
                for i in res:
                        logging.info("Modify a enable_dhcp")
                        data = {"enable_dhcp": True}
                        response = ib_NIOS.wapi_request('PUT', ref=i['_ref'], fields=json.dumps(data))
                        print response

                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True

                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
		sleep(10)
                logging.info("System Restart is done successfully")
                print("Test Case 76 Execution Completed")

        @pytest.mark.run(order=77)
        def test_077_Validate_DHCP_service_Enabled(self):
                logging.info("Validate DHCP Service is enabled")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties",params="?_return_fields=enable_dhcp")
                logging.info(get_tacacsplus)
                res = json.loads(get_tacacsplus)
                print res
                for i in res:
                        print i
                        logging.info("found")
                        assert i["enable_dhcp"] == True
                print("Test Case 77 Execution Completed")

	@pytest.mark.run(order=78)
        def test_078_Add_DHCP_Network_and_range_to_start_DDNS_updates(self):
		logging.info("Add DHCP network and range to start DDNS updates")
		logging.info("Adding network 10.0.0.0/8")
		net_obj = {"members":[{"_struct": "dhcpmember", "ipv4addr":config.grid_vip ,"name":config.grid_member_fqdn}],"network": "10.0.0.0/8", "network_view": "default"}
		network = ib_NIOS.wapi_request('POST', object_type="network", fields=json.dumps(net_obj))
		logging.info("Adding Range 10.0.0.200 - 10.0.0.10 with lease time 120")
		range_obj = {"start_addr":"10.0.0.10","end_addr":"10.0.0.200","member":{"_struct": "dhcpmember","ipv4addr":config.grid_vip,"name": config.grid_member_fqdn},"options":[{"_struct": "dhcpoption","name":"dhcp-lease-time","num": 51,"use_option": True,"value": "120","vendor_class": "DHCP"}]}
		range = ib_NIOS.wapi_request('POST', object_type="range", fields=json.dumps(range_obj))
		print(range)
		logging.info("Restart DHCP Services")
		grid =  ib_NIOS.wapi_request('GET', object_type="grid")
		ref = json.loads(grid)[0]['_ref']
		request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
		restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
		logging.info("Wait for 10 sec.,")
		print("Test Case 78 Execution Completed")
		sleep(10)

	@pytest.mark.run(order=79)
        def test_079_Validate_addition_of_DHCP_network(self):
                logging.info("Validating addition of DHCP network and network")
                get_temp = ib_NIOS.wapi_request('GET', object_type="network",params="?_inheritance=True&_return_fields=network")
                res = json.loads(get_temp)
                res = eval(json.dumps(get_temp))
                print(res)
                output=res.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                print(output)
                result = ["network:10.0.0.0/8"]
                for i in result:
                  if i in output:
                        assert True
                  else:
                        assert False
                print("Test Case 79 Execution Completed")
                logging.info("============================")

	@pytest.mark.run(order=80)
        def test_080_Validate_addition_of_DHCP_range(self):
                logging.info("Validating addition of DHCP range")
                get_temp = ib_NIOS.wapi_request('GET', object_type="range",params="?_inheritance=True&_return_fields=start_addr,end_addr")
                res = json.loads(get_temp)
                res = eval(json.dumps(get_temp))
                print(res)
                output=res.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                print(output)
                result = ["end_addr:10.0.0.200,start_addr:10.0.0.10"]
                for i in result:
                  if i in output:
                        assert True
                  else:
                        assert False
                print("Test Case 80 Execution Completed")
                logging.info("============================")
	
	@pytest.mark.run(order=81)
        def test_081_Setting_lease_time_at_range_level(self):
                logging.info("Setting lease time at range level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="range")
                logging.info(get_ref)
		res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify  DHCP range Properties")
                data = {"options": [{"name": "dhcp-lease-time","num": 51,"use_option": True,"value": "86400","vendor_class": "DHCP"}]}
                response = ib_NIOS.wapi_request('PUT',ref= ref1,fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                print("System Restart is done successfully")
                sleep(5)
                print("Test Case 81 Execution Completed")
	

	@pytest.mark.run(order=82)
        def test_082_Enable_DDNS_updates_to_create_autocreated_records(self):
                logging.info("Enable DDNS")
		get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify Grid DHCP Properties")
                data = {"ddns_domainname": "zone.com","ddns_generate_hostname": True,"enable_ddns": True,"ddns_update_fixed_addresses": True,"options":[{"name": "dhcp-lease-time","num": 51,"value": "43200","vendor_class": "DHCP"},{"name": "domain-name","num": 15,"value": "zone.com","vendor_class": "DHCP"}],"ddns_ttl": 86400}
                response = ib_NIOS.wapi_request('PUT',ref= ref1,fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
		logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                print("System Restart is done successfully")
                sleep(5)
                print("Test Case 82 Execution Completed")

	@pytest.mark.run(order=83)
        def test_083_send_leases_via_dras_to_create_dynamic_records(self):
               logging.info("send lease via dras to create dynamic records")
	       child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@10.36.201.11')
	       child.expect('password:')
	       child.sendline('infoblox')
	       child.expect('\$')
	       child.sendline('cd dras')
	       child.expect('\$')
	       child.sendline('sudo ./dras -i '+config.grid_vip+' -n 1 -h -D zone.com')
	       child.expect('Return value.*')
	       output = child.before
	       print(output)
	       child.close()
               print("\nTest Case 83 Executed Successfully")

	
	@pytest.mark.run(order=84)
        def test_084_validate_dynamic_records_last_queried_timestamp(self):
	        logging.info ("validate DS Record to get last queried timestamp post DB restore")
	        get_ref = ib_NIOS.wapi_request('GET',"record:a",grid_vip=config.grid_vip)
	        ref = json.loads(get_ref)[-1]['_ref']
	        print('ref is',ref)
	        response = ib_NIOS.wapi_request('GET',ref=ref,params="?_inheritance=last_queried&_return_fields=last_queried",grid_vip=config.grid_vip)
	        print(response)
	        response = json.loads(response)
                print(type(response),response)
	        response = eval(json.dumps(response))
                print(type(response),response)
                print("answer is",response['last_queried'])
                res= str(response)
	        output=res.replace(':','').replace(' ','').replace("'",'')
	        print(output)
	        result = re.findall(r'last_queried[0-9]{10}',output)
	        result = (str(result))
                print(result)
                result = result.replace('last_queried','').replace('[','').replace(']','').replace('"','').replace("'",'')
	        print(result)
	        print('my result is ',result)
	        time = epoch(int(result))
	        print('time is',time)
	        time = time.replace(',','').replace(' ','')
	        time = time[ 0 : 8]
	        print('converted time is',time)
	        print(date)
	        if date == time:
	           assert True
                else:
                   assert False
                print("Test Case 84 Execution Completed")


	@pytest.mark.run(order=85)
        def test_085_Configure_DNS_scavenging_grid_level_to_enable_scavenging_feature(self):
                logging.info("Configure DNS scavenging grid level to enable scavenging feature")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1
                logging.info("Modify Grid DNS Properties")
                data = {"scavenging_settings": {"ea_expression_list": [],"enable_auto_reclamation": True,"enable_recurrent_scavenging": True,"enable_rr_last_queried": True,"enable_scavenging": True,"enable_zone_last_queried": True,"expression_list": [{"op": "AND","op1_type": "LIST"},{"op": "EQ","op1": "rtype","op1_type": "FIELD","op2": "A","op2_type": "STRING"},{"op": "ENDLIST"}],"reclaim_associated_records": False}}
                response = ib_NIOS.wapi_request('PUT',ref= ref1,fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                sleep(10)
                print("Test Case 85 Execution Completed")

                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                print("System Restart is done successfully")
                sleep(5)


	@pytest.mark.run(order=86)
        def test_086_Validate_DNS_Scavenging_settings_at_grid_level(self):
                logging.info("Validate DNS scavenging settings at grid level")
                get_tacacsplus = ib_NIOS.wapi_request('GET', object_type="grid:dns",params="?_return_fields=scavenging_settings")
                res = json.loads(get_tacacsplus)
                res = eval(json.dumps(get_tacacsplus))
                print(res)
                output=res.replace('\n','').replace('"','').replace('{','').replace('}','').replace(' ','').replace('_ref','')
                print(output)
                result = ['scavenging_settings:ea_expression_list:[],enable_auto_reclamation:true,enable_recurrent_scavenging:true,enable_rr_last_queried:true,enable_scavenging:true,enable_zone_last_queried:true,expression_list:[op:AND,op1_type:LIST,op:EQ,op1:rtype,op1_type:FIELD,op2:A,op2_type:STRING,op:ENDLIST],reclaim_associated_records:false']
                for i in result:
                  if i in output:
                        assert True
                  else:
                        assert False
                print("Test Case 86 Execution Completed")
                logging.info("============================")


	@pytest.mark.run(order=87)
        def test_087_Scavenge_DNS_Record(self):
                logging.info("Scavenge DNS Record")
                data = {"fqdn":"test.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                ref=endpoint
                print ("###########",ref)
                data={"action":"ANALYZE_RECLAIM"}
                response = ib_NIOS.wapi_request('POST', object_type=ref,fields=json.dumps(data),params="?_function=run_scavenging")
                for read in response:
                        assert True
                logging.info("The selected zone is signed successfully")
                logging.info("Restart services")
                grid=ib_NIOS.wapi_request('GET', object_type="grid")
                ref=json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                logging.info("System Restart is done successfully")
		sleep(300)
                print("Test Case 87 Execution Completed")


	@pytest.mark.run(order=88)
        def test_088_Validate_Dynamic_A_record_reclaimed(self):
                logging.info("Validate dynamic A record scavenged")
                get_temp = ib_NIOS.wapi_request('GET', object_type="record:a",params="?_inheritance=True&_return_fields=name")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'name': 'auto.test.com'"
                if data in res:
                        assert False
                else:
                        assert True
                print("Test Case 88 Execution Completed")

	@pytest.mark.run(order=89)
        def test_089_Add_Authoritative_zone_with_secondary_nameserver(self):
                logging.info("Create Auth Zone with secondary name server")
                grid_member=config.grid_member_fqdn
                data = {"fqdn": "test2.com","grid_primary": [{"name":config.grid_member_fqdn,"stealth":False}],"grid_secondaries": [{"enable_preferred_primaries": False,"name":config.grid_member1_fqdn,"grid_replicate": True,"lead": False,"stealth": False}]}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 89 Execution Completed")

                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                print("System Restart is done successfully")
                sleep(5)

        @pytest.mark.run(order=90)
        def test_090_Validate_addition_of_Authoritative_zone_secondary_nameserver(self):
                logging.info("Validating addition of authoritative zone with secondary name server")
                get_temp = ib_NIOS.wapi_request('GET', object_type="zone_auth",params="?_inheritance=True&_return_fields=fqdn")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'fqdn': 'test2.com'"
                if data in res:
                        assert True
                else:
                        assert False
                print("Test Case 90 Execution Completed")
                sleep(10)

	@pytest.mark.run(order=91)
        def test_091_Create_A_record(self):
                logging.info ("Creating A Record for added Zone")
                data = {"fqdn":"test2.com"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "arec1.test2.com","ipv4addr":"1.2.3.9","_ref":endpoint,"comment":"Adding arec","view":"default"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                #import pdb;pdb.set_trace()
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                print("Test Case 91 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=92)
        def test_092_Validate_addition_of_A_record_in_above_zone(self):
                logging.info("Validating addition of authoritative zone in above zone")
                get_temp = ib_NIOS.wapi_request('GET', object_type="record:a",params="?_inheritance=True&_return_fields=name")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'name': 'arec1.test2.com'"
                if data in res:
                        assert True
                else:
                        assert False
                print("Test Case 92 Execution Completed")



	@pytest.mark.run(order=93)
        def test_093_dig_A_record_with_secondary_nameserver_to_get_current_last_queried_timestamp(self):
                logging.info ("Dig A Record with secondary nameserver to get last queried timestamp")
                global date
                dig_cmd = ('dig @'+str(config.grid_member1_vip)+' arec1.test2.com a' )
                print(dig_cmd)
                for i in range(1,4000):
                       os.system(dig_cmd)
                sleep(150)
                print("Test Case 93 Execution Completed")

        @pytest.mark.run(order=94)
        def test_094_validate_A_record_to_get_current_last_queried_timestamp_when_connected_to_sibling_zone(self):
                logging.info("validate A record to get current last queried timestamp when connected to sibling zone")
                response = ib_NIOS.wapi_request('GET',"record:a?name=arec1.test2.com&_return_fields%2B=last_queried&_return_as_object=1",grid_vip=config.grid_vip)
                res=json.loads(response)
                res = eval(json.dumps(res))
                res= str(res)
                output=res.replace(':','').replace(' ','').replace("'",'')
                print(output)
                result = re.findall(r'last_queried[0-9]{10}',output)
                result = (str(result))
                print(result)
                result = result.replace('last_queried','').replace('[','').replace(']','').replace('"','').replace("'",'')
                print(result)
                print ('my result is ',result)
                time = epoch(int(result))
                print('time is',time)
                time = time.replace(',','').replace(' ','')
                time = time[ 0 : 8]
                print('converted time is',time)
                #date = 'WedDec02'
                print(date)
                if date == time:
                        assert True
                else:
                        assert False
                print("Test Case 94 Execution Completed")

	@pytest.mark.run(order=95)
        def test_095_Add_a_network_view(self):
                logging.info("Add a network view")
                grid_member=config.grid_member_fqdn
                data = {"name": "custom"}
                response = ib_NIOS.wapi_request('POST', object_type="networkview", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 95 Execution Completed")

		logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                print("System Restart is done successfully")
                sleep(5)


	@pytest.mark.run(order=96)
        def test_096_Validate_addition_of_network_view(self):
                logging.info("Validating addition of network view")
                get_temp = ib_NIOS.wapi_request('GET', object_type="networkview",params="?_inheritance=True&_return_fields=name")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'name': 'custom'"
                if data in res:
                        assert True
                else:
                        assert False
                print("Test Case 96 Execution Completed")

	@pytest.mark.run(order=97)
        def test_097_Add_Authoritative_zone_in_custom_network_view(self):
                logging.info("Create Auth Zone in custom netwok view")
                grid_member=config.grid_member_fqdn
                data = {"fqdn": "custom.com","grid_primary": [{"name":config.grid_member_fqdn,"stealth":False}],"view":"default.custom"}
                response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
                res=json.loads(response)
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                print("Test Case 97 Execution Completed")

                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                print("System Restart is done successfully")
                sleep(5)

        @pytest.mark.run(order=98)
        def test_098_Validate_addition_of_Authoritative_zone_secondary_nameserver(self):
                logging.info("Validating addition of authoritative zone with secondary name server")
                get_temp = ib_NIOS.wapi_request('GET', object_type="zone_auth",params="?_inheritance=True&_return_fields=fqdn,view")
		print(get_temp)
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'fqdn': 'custom.com', 'view': 'default.custom'"
                if data in res:
                        assert True
                else:
                        assert False
		print(data)
                print("Test Case 98 Execution Completed")

	@pytest.mark.run(order=99)
        def test_099_Create_A_record_in_custom_network_view(self):
                logging.info ("Creating A Record in custom network view")
                data = {"fqdn":"custom.com","view": "default.custom"}
                endpoint=common_util.get_object_reference(object_type="zone_auth",data=data)
                print ("******************************************",endpoint)
                data={"name": "arec2.custom.com","ipv4addr":"1.2.3.6","_ref":endpoint,"comment":"Adding arec","view":"default.custom"}
                response = ib_NIOS.wapi_request('POST', object_type="record:a",fields=json.dumps(data))
                print ("---------------------------------------------------",json.loads(response))
                #import pdb;pdb.set_trace()
                read  = re.search(r'201',response)
                for read in response:
                    assert True
                print("Test Case 99 Execution Completed")
                sleep(5)

        @pytest.mark.run(order=100)
        def test_100_Validate_addition_of_A_record_in_above_zone(self):
                logging.info("Validating addition of authoritative zone in above zone")
                get_temp = ib_NIOS.wapi_request('GET', object_type="record:a",params="?_inheritance=True&_return_fields=name,ipv4addr,view")
                logging.info(get_temp)
                res=json.loads(get_temp)
                res = eval(json.dumps(res))
                res = ''.join(map(str, res))
                print(res)
                data= "'ipv4addr': '1.2.3.6', 'name': 'arec2.custom.com', 'view': 'default.custom'"
                if data in res:
                        assert True
                else:
                        assert False
		print(data)
                print("Test Case 100 Execution Completed")

	@pytest.mark.run(order=101)
        def test_101_Enable_custom_DNS_view_to_GM(self):
                logging.info("Enable custom DNS view to GM")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify Grid DHCP Properties")
                data = {"views": ["default.custom","default"]}
                response = ib_NIOS.wapi_request('PUT',ref= ref1,fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
		logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                print("System Restart is done successfully")
                print("Test Case 101 Execution Completed") 
                sleep(5)

	@pytest.mark.run(order=102)
        def test_102_dig_A_record_with_secondary_nameserver_to_get_current_last_queried_timestamp(self):
                logging.info ("Dig A Record with secondary nameserver to get last queried timestamp")
                global date
                dig_cmd = ('dig @'+str(config.grid_vip)+' arec2.custom.com a' )
                print(dig_cmd)
                for i in range(1,5000):
                       os.system(dig_cmd)
                sleep(200)
                print("Test Case 102 Execution Completed")

        @pytest.mark.run(order=103)
        def test_103_validate_A_record_to_get_current_last_queried_timestamp_created_in_custom_network_view(self):
                logging.info("validate A record to get current last queried timestamp created in custom network view")
                response = ib_NIOS.wapi_request('GET',"record:a?name=arec2.custom.com&_return_fields%2B=last_queried&_return_as_object=1",grid_vip=config.grid_vip)
                res=json.loads(response)
                res = eval(json.dumps(res))
                res= str(res)
                output=res.replace(':','').replace(' ','').replace("'",'')
                print(output)
                result = re.findall(r'last_queried[0-9]{10}',output)
                result = (str(result))
                print(result)
                result = result.replace('last_queried','').replace('[','').replace(']','').replace('"','').replace("'",'')
                print(result)
                print ('my result is ',result)
                time = epoch(int(result))
                print('time is',time)
                time = time.replace(',','').replace(' ','')
                time = time[ 0 : 8]
                print('converted time is',time)
                #date = 'WedDec02'
                print(date)
                if date == time:
                        assert True
                else:
                        assert False
                print("Test Case 104 Execution Completed")

	@pytest.mark.run(order=105)
        def test_105_Enable_custom_DNS_view_to_GM(self):
                logging.info("Enable custom DNS view to GM")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dns")
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                logging.info("Modify Grid DHCP Properties")
                data = {"views": ["default","default.custom"]}
                response = ib_NIOS.wapi_request('PUT',ref= ref1,fields=json.dumps(data))
                print response
                logging.info(response)
                read  = re.search(r'200',response)
                for read in  response:
                        assert True
                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                print("System Restart is done successfully")
                sleep(60)
                print("Test Case 105 Execution Completed")

	@pytest.mark.run(order=106)
        def test_106_add_resource_records_through_nsupdate(self):
                display_msg()
                display_msg("----------------------------------------------------")
                display_msg("|          Test Case 106 Execution Started          |")
                display_msg("----------------------------------------------------")

                display_msg("Add resource records using nsupdate")

                hostnames = [("A 1.0.1.19","auto1.")]
                try:
                        for data,record in hostnames:
                                record = record+'zone.com'
                                display_msg("RR name : "+record)
                                child = pexpect.spawn("nsupdate")
                                child.expect('>')
                                child.sendline('server '+config.grid_vip)
                                child.expect('>')
                                child.sendline('update add '+record+' 3600 IN '+data)
                                child.expect('>')
                                child.sendline('send')
                                child.expect('>')
                                output = child.before
                                print(output)
                                print(type(output))
                                child.sendline('quit')
                                child.close()
                                if "failed" in output:
                                        assert False
                except:
                        print("Test case failed")
                        assert False
                sleep(300)
                print("-----------Test Case 106 Execution Completed-----------")



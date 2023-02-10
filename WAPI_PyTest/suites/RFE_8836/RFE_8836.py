import re
import config
import pytest
import unittest
import logging
import subprocess
import os
import json
import ib_utils.ib_NIOS as ib_NIOS
from time import sleep
import commands
import json, ast
import requests
import time
import pexpect




def validate_prefixbit_and_duid(Macaddress,bit):
    #a="lease?ipv6_duid~=.*:" + Macaddress + "\\&_return_fields=ipv6_prefix_bits"
    #print a
    get_ref = ib_NIOS.wapi_request('GET', object_type="lease?ipv6_duid~=.*:" + Macaddress + "&_return_fields=ipv6_prefix_bits")
    res = json.loads(get_ref)
    logging.info(res)
    print res
    if  res[0]["ipv6_prefix_bits"]==bit:
        return True
    else:
        return False
    	

class Network(unittest.TestCase):

        @pytest.mark.run(order=1)
        def test_001_start_IPv4_service(self):
                logging.info("start the ipv4 service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"enable_dhcp": True}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("============================")
                print response


	@pytest.mark.run(order=2)
        def test_002_start_IPv6_service(self):
                logging.info("start the ipv6 service")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"enable_dhcpv6_service": True}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("============================")
                print response

	@pytest.mark.run(order=3)
        def test_003_create_IPv6_network(self):
		logging.info("Creatiing an ipv6 network with members assignment")
                global ipv6_network
                ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
                print(ipv6_network)
                ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
                print(ipv6_network)
                data = {"network": ipv6_network+"::/64","network_view": "default","members": [{"ipv4addr":config.grid_vip,"name":config.grid_fqdn}]}
                print(data)
                response = ib_NIOS.wapi_request('POST', object_type="ipv6network", fields=json.dumps(data), grid_vip=config.grid_vip)
                print(response)
                sleep(02)
                print("Test Case 1 Execution Completed")


	@pytest.mark.run(order=4)
        def test_004_create_IPv6_Prefix_delegation_Range_1(self):
                logging.info("Create an ipv6 range in  default network view")
		global ipv6_network
                ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
                print(ipv6_network)
                ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
                print(ipv6_network)

                data ={"address_type":"PREFIX","network":ipv6_network+"::/64","ipv6_start_prefix":ipv6_network+":10::","ipv6_end_prefix":ipv6_network+":20::","ipv6_prefix_bits":80,"network_view": "default","member":{"_struct":"dhcpmember","ipv4addr":config.grid_vip,"name":config.grid_fqdn}}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6range", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Created the ipv6 prefix range with bits 80  in default view")


	@pytest.mark.run(order=5)
        def test_005_create_IPv6_Prefix_delegation_Range_2(self):
		logging.info("Create an ipv6 range in  default network view")
                global ipv6_network
                ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
                print(ipv6_network)
                ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
                print(ipv6_network)

                data ={"address_type":"PREFIX","network":ipv6_network+"::/64","ipv6_start_prefix":ipv6_network+":21::","ipv6_end_prefix":ipv6_network+":30::","ipv6_prefix_bits":90,"network_view": "default","member":{"_struct":"dhcpmember","ipv4addr":config.grid_vip,"name":config.grid_fqdn}}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6range", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Created the ipv6 prefix range with bits 90  in default view")


	
	@pytest.mark.run(order=6)
        def test_006_create_IPv6_Prefix_delegation_Range_3(self):
                logging.info("Create an ipv6 range in  default network view")
                global ipv6_network
                ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
                print(ipv6_network)
                ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
                print(ipv6_network)

                data ={"address_type":"PREFIX","network":ipv6_network+"::/64","ipv6_start_prefix":ipv6_network+":31::","ipv6_end_prefix":ipv6_network+":40::","ipv6_prefix_bits":100,"network_view": "default","member":{"_struct":"dhcpmember","ipv4addr":config.grid_vip,"name":config.grid_fqdn}}
                response = ib_NIOS.wapi_request('POST', object_type="ipv6range", fields=json.dumps(data), grid_vip=config.grid_vip)
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Created the ipv6 prefix range with bits 80  in default view")


		logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                sleep(10)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(20)
                logging.info("Test Case 6 Execution Completed")


       	@pytest.mark.run(order=7)
        def test_007_requesting_ipv6_lease_with_Exact_prefix_lenght(self):
                logging.info("Perform dras command")
		global ipv6_network
                ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
                print(ipv6_network)
                ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
                print(ipv6_network)

                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i'+str(config.grid_vip6)+' '+' -n 1 -c '+str(ipv6_network)+'"::" -a 2a:2a:aa:aa:aa:ae -A -b  '+str(ipv6_network)+'"::/80" '
                dras_cmd1 = os.system(dras_cmd)
                sleep(10)
                logging.info("Validate Syslog afer perform lease operation")
                if validate_prefixbit_and_duid("2a:2a:aa:aa:aa:ae",80)== True:
                        assert True
                else:
                        assert False


	@pytest.mark.run(order=8)
        def test_008_requesting_ipv6_lease_with_Exact_prefix_lenght_2(self):
                logging.info("Perform dras command")
		global ipv6_network
                ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
                print(ipv6_network)
                ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
                print(ipv6_network)

                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i'+str(config.grid_vip6)+' '+'-n 1 -c '+str(ipv6_network)+'"::" -a 11:22:aa:aa:aa:aa -A -b '+str(ipv6_network)+'"::/85"  '
                dras_cmd1 = os.system(dras_cmd)
                sleep(10)
                logging.info("Validate Syslog afer perform lease operation")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -300 /var/log/syslog | grep  \'no prefixes available\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'no prefixes available',out1)
                logging.info("Test Case 8 Execution Completed")



	@pytest.mark.run(order=9)
        def test_009_changin_prefix_from_Exact_to_Ignore(self):
                logging.info("change from exact to Ignore")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties?_return_fields=prefix_length_mode", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"prefix_length_mode":"IGNORE"}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("============================")
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                sleep(10)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(20)
                logging.info("Test Case 9 execution Completed")

	
	@pytest.mark.run(order=10)
        def test_010_audit_Log_after_changing_to_ignore_at_grid_level(self):
                logging.info("Validate Audit Log validation afer changing the PLM to ignore at grid level")
                Audit_Log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -25 /infoblox/var/audit.log | grep  \'Changed prefix_length_mode.*EXACT.*IGNORE.*\'"'
                out1 = commands.getoutput(Audit_Log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'Changed prefix_length_mode.*EXACT.*IGNORE.*',out1)
                logging.info("Test Case 10 Execution Completed")

	@pytest.mark.run(order=11)
        def test_011_dhcpconf_file_after_changing_to_Ignore(self):
                logging.info("Validate dhcp conf file validation afer changing the PLM to ignore")
                conf_file__validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -30 /infoblox/var/dhcpdv6_conf/dhcpdv6.conf | grep  \'prefix-length-mode ignore\'"'
                out1 = commands.getoutput(conf_file__validation)
                print out1
                logging.info(out1)
                assert re.search(r'prefix-length-mode ignore',out1)
                logging.info("Test Case 11 Execution Completed")


	@pytest.mark.run(order=12)
        def test_012_requesting_ipv6_lease_with_Ignore_prefix_length(self):
                logging.info("Perform dras command")
		global ipv6_network
                ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
                print(ipv6_network)
                ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
                print(ipv6_network)

                dras_cmd ='sudo /import/tools/qa/tools/dras6/dras6 -i'+str(config.grid_vip6)+' '+'-n 1 -c '+str(ipv6_network)+'"::" -a bb:bb:bb:bb:bb:bb -A -b  '+str(ipv6_network)+'"::/90" '
                dras_cmd1 = os.system(dras_cmd)
                sleep(5)
                logging.info("Validate Syslog afer perform lease operation")
                if validate_prefixbit_and_duid("bb:bb:bb:bb:bb:bb",80)== True:
                        assert True
                else:
                        assert False
                logging.info("Test Case 12 Execution Completed")

 	@pytest.mark.run(order=13)
        def test_013_changin_prefix_from_Ignore_to_Maximum(self):
                logging.info("change from Ignore to Maximum")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties?_return_fields=prefix_length_mode", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"prefix_length_mode":"MAXIMUM"}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("============================")
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                sleep(10)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(20)
                logging.info("Test Case 13 execution Completed")


	@pytest.mark.run(order=14)
        def test_014_audit_Log_after_changing_to_maximum_at_grid_level(self):
                logging.info("Validate Audit Log validation afer changing the PLM to maximum at grid level")
                Audit_Log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -25 /infoblox/var/audit.log | grep  \'Changed prefix_length_mode.*IGNORE.*MAXIMUM.*\'"'
                out1 = commands.getoutput(Audit_Log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'Changed prefix_length_mode.*IGNORE.*MAXIMUM.*',out1)
                logging.info("Test Case 14 Execution Completed")


	@pytest.mark.run(order=15)
        def test_015_dhcpconf_file_after_changing_to_Maximum(self):
                logging.info("Validate dhcp conf file validation afer changing the PLM to maximum")
                conf_file__validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -30 /infoblox/var/dhcpdv6_conf/dhcpdv6.conf | grep  \'prefix-length-mode maximum\'"'
                out1 = commands.getoutput(conf_file__validation)
                print out1
                logging.info(out1)
                assert re.search(r'prefix-length-mode maximum',out1)
                logging.info("Test Case 15 Execution Completed")




	@pytest.mark.run(order=16)
        def test_016_requesting_ipv6_lease_with_Maximum_prefix_lenght(self):
                logging.info("Perform dras command")
		global ipv6_network
                ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
                print(ipv6_network)
                ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
                print(ipv6_network)

                dras_cmd ='sudo /import/tools/qa/tools/dras6/dras6 -i'+str(config.grid_vip6)+' '+'-n 1 -c '+str(ipv6_network)+'"::" -a cc:cc:cc:cc:cc:cc -A -b  '+str(ipv6_network)+'"::/95" '
                dras_cmd1 = os.system(dras_cmd)
                sleep(5)
                logging.info("Validate Syslog afer perform lease operation")
                if validate_prefixbit_and_duid("cc:cc:cc:cc:cc:cc",80)== True:
                        assert True
                else:
                        assert False
                logging.info("Test Case 13 Execution Completed")



	@pytest.mark.run(order=17)
        def test_017_changin_prefix_from_Maximum_to_Minimum(self):
                logging.info("change from Maximum to Minimum")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties?_return_fields=prefix_length_mode", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"prefix_length_mode":"MINIMUM"}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("============================")
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                sleep(10)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(20)
                logging.info("Test Case 17 execution Completed")
	

	@pytest.mark.run(order=18)
        def test_018_audit_Log_after_changing_to_minimum_at_grid_level(self):
                logging.info("Validate Audit Log validation afer changing the PLM to minimum at grid level")
                Audit_Log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -25 /infoblox/var/audit.log | grep  \'Changed prefix_length_mode.*MAXIMUM.*MINIMUM.*\'"'
                out1 = commands.getoutput(Audit_Log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'Changed prefix_length_mode.*MAXIMUM.*MINIMUM.*',out1)
                logging.info("Test Case 18 Execution Completed")


	@pytest.mark.run(order=19)
        def test_019_dhcpconf_file_after_changing_to_Minimum(self):
                logging.info("Validate dhcp conf file validation afer changing the PLM to minimum")
                conf_file__validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -40 /infoblox/var/dhcpdv6_conf/dhcpdv6.conf | grep  \'prefix-length-mode minimum\'"'
                out1 = commands.getoutput(conf_file__validation)
                print out1
                logging.info(out1)
                assert re.search(r'prefix-length-mode minimum',out1)
                logging.info("Test Case 19 Execution Completed")




	@pytest.mark.run(order=20)
        def test_020_requesting_ipv6_lease_with_Minimum_prefix_lenght(self):
                logging.info("Perform dras command")
		global ipv6_network
                ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
                print(ipv6_network)
                ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
                print(ipv6_network)
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i'+str(config.grid_vip6)+' '+'-n 1 -c '+str(ipv6_network)+'"::" -a dd:dd:dd:dd:dd:dd -A -b  '+str(ipv6_network)+'"::/95" '
                dras_cmd1 = os.system(dras_cmd)
                sleep(5)
                if validate_prefixbit_and_duid("dd:dd:dd:dd:dd:dd",100)== True:
                        assert True
                else:
                        assert False
                logging.info("Test Case 20 Execution Completed")




	@pytest.mark.run(order=21)
        def test_021_changin_prefix_from_Minimum_to_Prefer(self):
                logging.info("change from Minimum to Prefer")
                get_ref = ib_NIOS.wapi_request('GET', object_type="grid:dhcpproperties?_return_fields=prefix_length_mode", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"prefix_length_mode":"PREFER"}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("============================")
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                sleep(10)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(20)
                logging.info("Test Case 21 execution Completed")

	
	@pytest.mark.run(order=22)
        def test_022_audit_Log_after_changing_to_prefer_at_grid_level(self):
                logging.info("Validate Audit Log validation after changing the PLM to prefer at grid level")
                Audit_Log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -25 /infoblox/var/audit.log | grep  \'Changed prefix_length_mode.*MINIMUM.*PREFER.*\'"'
                out1 = commands.getoutput(Audit_Log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'Changed prefix_length_mode.*MINIMUM.*PREFER.*',out1)
                logging.info("Test Case 22 Execution Completed")

	@pytest.mark.run(order=23)
        def test_023_dhcpconf_file_after_changing_to_Prefer(self):
                logging.info("Validate dhcp conf file validation afer changing the PLM to prefer")
                conf_file__validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -30 /infoblox/var/dhcpdv6_conf/dhcpdv6.conf | grep  \'prefix-length-mode prefer\'"'
                out1 = commands.getoutput(conf_file__validation)
                print out1
                logging.info(out1)
                assert re.search(r'prefix-length-mode prefer',out1)
                logging.info("Test Case 23 Execution Completed")




	@pytest.mark.run(order=24)
        def test_024_requesting_ipv6_lease_with_Prefer_prefix_length_1(self):
                logging.info("Perform dras command")
		global ipv6_network
                ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
                print(ipv6_network)
                ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
                print(ipv6_network)

                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i'+str(config.grid_vip6)+' '+'-n 1 -c '+str(ipv6_network)+'"::" -a ee:8d:8d:9d:dd:dd -A -b  '+str(ipv6_network)+'"::/90" '
                dras_cmd1 = os.system(dras_cmd)
                sleep(5)
                if validate_prefixbit_and_duid("ee:8d:8d:9d:dd:dd",90)== True:
                        assert True
                else:
                        assert False
                logging.info("Test Case 24 Execution Completed")



	@pytest.mark.run(order=25)
        def test_025_requesting_ipv6_lease_with_Prefer_prefix_length_2(self):
                logging.info("Perform dras command")
		global ipv6_network
                ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
                print(ipv6_network)
                ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
                print(ipv6_network)
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i'+str(config.grid_vip6)+' '+'-n 1 -c '+str(ipv6_network)+'"::" -a ee:ee:5d:7d:dd:dd -A -b  '+str(ipv6_network)+'"::/95" '
                dras_cmd1 = os.system(dras_cmd)
                sleep(5)
                if validate_prefixbit_and_duid("ee:ee:5d:7d:dd:dd",80)== True:
                        assert True
                else:
                        assert False
                logging.info("Test Case 25 Execution Completed")






	@pytest.mark.run(order=26)
        def test_026_changin_prefix_to_Exact_at_Member_level(self):
                logging.info("change to exact at member level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties?_return_fields=prefix_length_mode", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"prefix_length_mode":"EXACT"}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("============================")
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                sleep(10)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(20)
                logging.info("Test Case 26 execution Completed")

	@pytest.mark.run(order=27)
        def test_027_dhcpconf_file_after_changing_to_exact_at_member_level(self):
                logging.info("Validate dhcp conf file validation afer changing the PLM to exact at member level")
                conf_file__validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -30 /infoblox/var/dhcpdv6_conf/dhcpdv6.conf | grep  \'prefix-length-mode exact\'"'
                out1 = commands.getoutput(conf_file__validation)
                print out1
                logging.info(out1)
                assert re.search(r'prefix-length-mode exact',out1)
                logging.info("Test Case 27 Execution Completed")



	@pytest.mark.run(order=28)
        def test_028_audit_Log_after_changing_to_exact_at_member_level(self):
                logging.info("Validate Audit Log validation afer changing the PLM to exact at member level")
                Audit_Log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -20 /infoblox/var/audit.log | grep  \'Changed use_prefix_length_mode:False->True\'"'
                out1 = commands.getoutput(Audit_Log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'Changed use_prefix_length_mode:False->True',out1)
                logging.info("Test Case 28 Execution Completed")


	@pytest.mark.run(order=29)
        def test_029_requesting_ipv6_lease_with_Exact_prefix_lenght_at_member_level(self):
                logging.info("Perform dras command")
		global ipv6_network
                ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
                print(ipv6_network)
                ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
                print(ipv6_network)
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i'+str(config.grid_vip6)+' '+'-n 1 -c '+str(ipv6_network)+'"::" -a 11:11:11:11:11:11 -A -b  '+str(ipv6_network)+'"::/80" '
                dras_cmd1 = os.system(dras_cmd)
                sleep(5)
                if validate_prefixbit_and_duid("11:11:11:11:11:11",80)== True:
                        assert True
                else:
                        assert False
                logging.info("Test Case 29 Execution Completed")


        @pytest.mark.run(order=30)
        def test_030_requesting_ipv6_lease_with_Exact_prefix_lenght_at_member_level_2(self):
                logging.info("Perform dras command")
		global ipv6_network
                ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
                print(ipv6_network)
                ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
                print(ipv6_network)
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i'+str(config.grid_vip6)+' '+'-n 1 -c '+str(ipv6_network)+'"::" -a 22:22:22:22:22:22 -A -b  '+str(ipv6_network)+'"::/85" '
                dras_cmd1 = os.system(dras_cmd)
                sleep(5)
                logging.info("Validate Syslog afer perform lease operation")
                sys_log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -200 /var/log/syslog | grep  \'no prefixes available\'"'
                out1 = commands.getoutput(sys_log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'no prefixes available',out1)
                logging.info("Test Case 30 Execution Completed")

	@pytest.mark.run(order=31)
        def test_031_changin_prefix_from_Exact_to_Ignore_at_member_level(self):
                logging.info("change from exact to Ignore")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties?_return_fields=prefix_length_mode", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"prefix_length_mode":"IGNORE"}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("============================")
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                sleep(10)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(20)
                logging.info("Test Case 31 execution Completed")



	@pytest.mark.run(order=32)
        def test_032_dhcpconf_file_after_changing_to_Ignore_at_member_level(self):
                logging.info("Validate dhcp conf file validation after changing the PLM to ignore at member level")
                conf_file__validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -30 /infoblox/var/dhcpdv6_conf/dhcpdv6.conf | grep  \'prefix-length-mode ignore\'"'
                out1 = commands.getoutput(conf_file__validation)
                print out1
                logging.info(out1)
                assert re.search(r'prefix-length-mode ignore',out1)
                logging.info("Test Case 32 Execution Completed")

				
	@pytest.mark.run(order=33)
        def test_033_audit_Log_after_changing_to_Ignore_at_member_level(self):
                logging.info("Validate Audit Log validation afer changing the PLM to ignore at member level")
                Audit_Log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -25 /infoblox/var/audit.log | grep  \'Changed prefix_length_mode.*EXACT.*IGNORE.*\'"'
                out1 = commands.getoutput(Audit_Log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'Changed prefix_length_mode.*EXACT.*IGNORE.*',out1)
                logging.info("Test Case 33 Execution Completed")


	@pytest.mark.run(order=34)
        def test_034_requesting_ipv6_lease_with_Ignore_prefix_length_at_member_level(self):
                logging.info("Perform dras command")
		global ipv6_network
                ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
                print(ipv6_network)
                ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
                print(ipv6_network)
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i'+str(config.grid_vip6)+' '+'-n 1 -c '+str(ipv6_network)+'"::" -a 44:44:bb:bb:bb:bb -A -b  '+str(ipv6_network)+'"::/90" '
                dras_cmd1 = os.system(dras_cmd)
                sleep(5)
                if validate_prefixbit_and_duid("44:44:bb:bb:bb:bb",80)== True:
                        assert True
                else:
                        assert False
                logging.info("Test Case 34 Execution Completed")


	@pytest.mark.run(order=35)
        def test_035_changin_prefix_from_Ignore_to_Maximum_at_member_level(self):
                logging.info("change from Ignore to Maximum at member level")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties?_return_fields=prefix_length_mode", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"prefix_length_mode":"MAXIMUM"}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("============================")
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                sleep(10)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(20)
                logging.info("Test Case 35 execution Completed")



	@pytest.mark.run(order=36)
        def test_036_dhcpconf_file_after_changing_to_Maximum_at_member_level(self):
                logging.info("Validate dhcp conf file validation after changing the PLM to Maximum at member level")
                conf_file__validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -30 /infoblox/var/dhcpdv6_conf/dhcpdv6.conf | grep  \'prefix-length-mode maximum\'"'
                out1 = commands.getoutput(conf_file__validation)
                print out1
                logging.info(out1)
                assert re.search(r'prefix-length-mode maximum',out1)
                logging.info("Test Case 36 Execution Completed")


        @pytest.mark.run(order=37)
        def test_037_audit_Log_after_changing_to_Maximum_at_member_level(self):
                logging.info("Validate Audit Log validation afer changing the PLM to Maximum at member level")
                Audit_Log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -25 /infoblox/var/audit.log | grep  \'Changed prefix_length_mode.*IGNORE.*MAXIMUM.*\'"'
                out1 = commands.getoutput(Audit_Log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'Changed prefix_length_mode.*IGNORE.*MAXIMUM.*',out1)
                logging.info("Test Case 37 Execution Completed")



	@pytest.mark.run(order=38)
        def test_038_requesting_ipv6_lease_with_Maximum_prefix_lenght_at_Member_Level(self):
                logging.info("Perform dras command")
		global ipv6_network
                ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
                print(ipv6_network)
                ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
                print(ipv6_network)
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i'+str(config.grid_vip6)+' '+'-n 1 -c '+str(ipv6_network)+'"::" -a 44:cc:cc:44:cc:44 -A -b  '+str(ipv6_network)+'"::/95" '
                dras_cmd1 = os.system(dras_cmd)
                sleep(5)
                if validate_prefixbit_and_duid("44:cc:cc:44:cc:44",80)== True:
                        assert True
                else:
                        assert False
                logging.info("Test Case 38 Execution Completed")


	@pytest.mark.run(order=39)
        def test_039_changin_prefix_from_Maximum_to_Minimum_at_Member_Level(self):
                logging.info("change from Maximum to Minimum")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties?_return_fields=prefix_length_mode", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"prefix_length_mode":"MINIMUM"}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("============================")
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                sleep(10)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(20)
                logging.info("Test Case 39 execution Completed")

				
 	@pytest.mark.run(order=40)
        def test_040_dhcpconf_file_after_changing_to_Minimum_at_member_level(self):
                logging.info("Validate dhcp conf file validation after changing the PLM to Minimum at member level")
                conf_file__validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -30 /infoblox/var/dhcpdv6_conf/dhcpdv6.conf | grep  \'prefix-length-mode minimum\'"'
                out1 = commands.getoutput(conf_file__validation)
                print out1
                logging.info(out1)
                assert re.search(r'prefix-length-mode minimum',out1)
                logging.info("Test Case 40 Execution Completed")


        @pytest.mark.run(order=41)
        def test_041_audit_Log_after_changing_to_Minimum_at_member_level(self):
                logging.info("Validate Audit Log validation afer changing the PLM to minimum at member level")
                Audit_Log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -25 /infoblox/var/audit.log | grep  \'Changed prefix_length_mode.*MAXIMUM.*MINIMUM.*\'"'
                out1 = commands.getoutput(Audit_Log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'Changed prefix_length_mode.*MAXIMUM.*MINIMUM.*',out1)
                logging.info("Test Case 41 Execution Completed")



	@pytest.mark.run(order=42)
        def test_042_requesting_ipv6_lease_with_Minimum_prefix_lenght_at_Member_Level(self):
                logging.info("Perform dras command")
		global ipv6_network
                ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
                print(ipv6_network)
                ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
                print(ipv6_network)

                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i'+str(config.grid_vip6)+' '+'-n 1 -c '+str(ipv6_network)+'"::" -a a5:bd:c9:dd:88:9d -A -b  '+str(ipv6_network)+'"::/95" '
                dras_cmd1 = os.system(dras_cmd)
                sleep(5)
                if validate_prefixbit_and_duid("a5:bd:c9:dd:88:9d",100)== True:
                        assert True
                else:
                        assert False
                logging.info("Test Case 42 Execution Completed")




	@pytest.mark.run(order=43)
        def test_043_changin_prefix_from_Minimum_to_Prefer_at_member_Level(self):
                logging.info("change from Minimum to Prefer")
                get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties?_return_fields=prefix_length_mode", grid_vip=config.grid_vip)
                logging.info(get_ref)
                res = json.loads(get_ref)
                ref1 = json.loads(get_ref)[0]['_ref']
                print ref1

                data = {"prefix_length_mode":"PREFER"}
                response = ib_NIOS.wapi_request('PUT',ref=ref1,fields=json.dumps(data), grid_vip=config.grid_vip)
                logging.info(response)
                logging.info("============================")
                print response
                logging.info(response)
                read  = re.search(r'201',response)
                for read in  response:
                        assert True
                logging.info("Restart services")
                grid =  ib_NIOS.wapi_request('GET', object_type="grid")
                ref = json.loads(grid)[0]['_ref']
                publish={"member_order":"SIMULTANEOUSLY"}
                request_publish = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=publish_changes",fields=json.dumps(publish))
                sleep(10)
                request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=requestrestartservicestatus")
                restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices")
                sleep(20)
                logging.info("Test Case 43 execution Completed")
				
				
	@pytest.mark.run(order=44)
        def test_044_dhcpconf_file_after_changing_to_prefer_at_member_level(self):
                logging.info("Validate dhcp conf file validation afer changing the PLM to prefer at member level")
                conf_file__validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -30 /infoblox/var/dhcpdv6_conf/dhcpdv6.conf | grep  \'prefix-length-mode prefer\'"'
                out1 = commands.getoutput(conf_file__validation)
                print out1
                logging.info(out1)
                assert re.search(r'prefix-length-mode prefer',out1)
                logging.info("Test Case 44 Execution Completed")



        @pytest.mark.run(order=45)
        def test_045_audit_Log_after_changing_to_prefer_at_member_level(self):
                logging.info("Validate Audit Log validation afer changing the PLM to prefer at member level")
                Audit_Log_validation = 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o UserKnownHostsFile=/dev/null root@'+str(config.grid_vip)+' " tail -25 /infoblox/var/audit.log | grep  \'Changed prefix_length_mode.*MINIMUM.*PREFER.*\'"'
                out1 = commands.getoutput(Audit_Log_validation)
                print out1
                logging.info(out1)
                assert re.search(r'Changed prefix_length_mode.*MINIMUM.*PREFER.*',out1)
                logging.info("Test Case 45 Execution Completed")

				
	@pytest.mark.run(order=46)
        def test_046_requesting_ipv6_lease_with_Prefer_prefix_length_at_member_level(self):
                logging.info("Perform dras command")
		global ipv6_network
                ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
                print(ipv6_network)
                ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
                print(ipv6_network)
                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i'+str(config.grid_vip6)+' '+'-n 1 -c '+str(ipv6_network)+'"::" -a ee:8d:99:99:99:99 -A -b  '+str(ipv6_network)+'"::/90" '
                dras_cmd1 = os.system(dras_cmd)
                sleep(2)
                if validate_prefixbit_and_duid("ee:8d:99:99:99:99",90)== True:
                        assert True
                else:
                        assert False
                logging.info("Test Case 46 Execution Completed")



        @pytest.mark.run(order=47)
        def test_047_requesting_ipv6_lease_with_Prefer_prefix_length_at_member_level_2(self):
                logging.info("Perform dras command")
		global ipv6_network
                ipv6_network=os.popen("echo IPv6_prefix=$(hostname -I|awk -F ' ' {print'$2'}|sed s/::.*//g)").read()
                print(ipv6_network)
                ipv6_network = ipv6_network.replace('IPv6_prefix=','').replace('\n','')
                print(ipv6_network)

                dras_cmd = 'sudo /import/tools/qa/tools/dras6/dras6 -i'+str(config.grid_vip6)+' '+'-n 1 -c '+str(ipv6_network)+'"::" -a 99:99:5d:7d:ab:87 -A -b  '+str(ipv6_network)+'"::/95" '
                dras_cmd1 = os.system(dras_cmd)
                sleep(5)
                if validate_prefixbit_and_duid("99:99:5d:7d:ab:87",80)== True:
                        assert True
                else:
                        assert False
                logging.info("Test Case 47 Execution Completed")






        

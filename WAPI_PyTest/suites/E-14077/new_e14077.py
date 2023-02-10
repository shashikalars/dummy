import dns.message
import base64
import config                                    
import pytest                                    
import unittest                                  
import logging
import os
import pexpect
import re
import sys
import json
import commands
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
from ib_utils.start_stop_logs import log_action as log
from ib_utils.file_content_validation import log_validation as logv

#  -----------------------------------------------------------

# Grid Configuration :-

# Grid Master (IB-FLEX small) with MGMT enabled having 8 CPU and 32 GB Memory
# Author - Chanchal Sutradhar
# Email - csutradhar@infoblox.com

# The reponse size of  *.1santhosh.com A ~ 3744 B
# The reponse size of  *.1santhosh.com TXT ~ 29016 B
# The reponse size of  *.flex.com A ~ 1200 B
#  

#-------------------------------------------------------------

# Making DoH Query
def doh_query(ip,domain='a.flex.com',rr='A',edns=True):
    endpoint = "https://"+ip+"/dns-query"
    message = dns.message.make_query(domain, rr, use_edns=edns)
    dns_req = base64.urlsafe_b64encode(message.to_wire()).decode("UTF8").rstrip('=')
    query = "curl -H 'content-type: application/dns-message' "+endpoint+"?dns="+dns_req+" -o - -s -k1 --http2 > doh_http2.txt"
    try:
        op = os.popen(query)
        h = op.read()
        fi = open("doh_http2.txt", "rb").read()
        response = dns.message.from_wire(fi)
        response = response.to_text().encode("utf-8")
        os.remove("doh_http2.txt")
    except:
        print("\nThere is some problem with the DOH server...!!")
        response = "NIL"
    return response
   
#Getting the Grid DNS Reference sting

def grid_dns_ref_string():
    response = ib_NIOS.wapi_request('GET', object_type="grid:dns")
    logging.info(response)
    print(response)
    if type(response)!=tuple:
        ref1 = json.loads(response)
        for key in ref1:
            grid_ref = key.get('_ref')
    else:
        print("Failed to get grid DNS ref string")
        grid_ref = "NIL"
    return grid_ref


#Getting the member DNS Reference sting

def mem_dns_ref_string(hostname):
    response = ib_NIOS.wapi_request('GET', object_type="member:dns")
    logging.info(response)
    print(response)
    if type(response)!=tuple:
        ref1 = json.loads(response)
        for key in ref1:
            if key.get('host_name') == hostname:
                mem_ref = key.get('_ref')
                break
    else:
        print("Failed to get member DNS ref string")
        mem_ref = "NIL"
    
    return mem_ref

#Getting the member Reference sting

def mem_ref(hostname):
    response = ib_NIOS.wapi_request('GET', object_type="member")
    logging.info(response)
    print(response)
    if type(response)!=tuple:
        ref1 = json.loads(response)
        for key in ref1:
            if key.get('host_name') == hostname:
                mem_ref = key.get('_ref')
                break
    else:
        print("Failed to get member DNS ref string")
        mem_ref = "NIL"
    
    return mem_ref


#Perform DNS Restart

def dns_restart(hostname):
    ref = mem_ref(hostname)
    data= {"restart_option":"FORCE_RESTART","service_option": "DNS"}
    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data))
    sleep(60)
    print("DNS Restart Successfull")

# Perform product reboot

def prod_reboot(ip):
    child = pexpect.spawn('ssh admin@'+ip)
    child.logfile=sys.stdout
    child.expect('password:')
    child.sendline('infoblox')
    child.expect('Infoblox >')
    child.sendline('reboot')
    child.expect('REBOOT THE SYSTEM?')
    child.sendline('y')
    child.expect(pexpect.EOF)
    for i in range(1,20):
        sleep(60)
        status = os.system("ping -c1 -w2 "+ip)
        print(status)
        if status == 0:
            print("System is up")
            break
        else:
            print("System is still down..!!")
    sleep(10)
    print("Product Reboot successfull ..!!!")
                    

class RFE_9826(unittest.TestCase):

        # Changing the hostname of the master

        @pytest.mark.run(order=1)
        def test_001_changing_hostname_of_the_master(self):
            logging.info("Changing the hostname of the master")
            mgmt_fqdn = "ib-"+config.grid_vip.replace('.','-')+".infoblox.com"
            lan_fqdn = "ib-"+config.grid_master_ip.replace('.','-')+".infoblox.com"
            data = {"host_name": mgmt_fqdn}
            mem_ref_str = mem_ref(lan_fqdn)
            if mem_ref_str != "NILL":
                response = ib_NIOS.wapi_request('PUT', object_type=mem_ref_str, fields=json.dumps(data),grid_vip=config.grid_vip)
                sleep(60)
                if type(response)!=tuple:
                    print("Hostname changed successfully")
                    logging.info("Hostname Changed successfully")
                    assert True
                else:
                    print("Failed to change the hostname")
                    logging.info("Failed to change the hostname")
                    assert False
            else:
                print("Failed to get the member reference string")
                logging.info("Failed to get the member reference string")
                assert False
        
        # Configuring the Forwarder, recursion, query and response logs on Grid level

        @pytest.mark.run(order=2)
        def test_002_configuring_forwarder_recursion_query_response_logging_grid_wide(self):
            logging.info("Configuring forwarder,recursion, query and response logging on the grid wide")
            data = {"forward_only":True, "forwarders": [config.forwarder],"allow_recursive_query":True, "logging_categories": {"log_queries": True, "log_responses": True}}
            grid_dns_ref = grid_dns_ref_string()
            if grid_dns_ref != "NILL":
                response = ib_NIOS.wapi_request('PUT', object_type=grid_dns_ref, fields=json.dumps(data))
                print(response)
                if type(response)!=tuple:
                    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                    ref = json.loads(grid)[0]['_ref']
                    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "DNS"}
                    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data))
                    sleep(120)
                    print("Forwarder, Recursion, query and response log enabled")
                    logging.info("Forwarder, recursion, query and response log enabled")
                    assert True
                else:
                    print("Failed to enable forwarder, recursion, query and response logging")
                    logging.info("Failed to enable forwarder, recursion, query and response logging")
                    assert False
            else:
                print("Failed to get the Grid DNS reference string")
                logging.info("Failed to enable forwarder and recursion")
                assert False

        # Validating recursiona and forwarder setting on the master

        @pytest.mark.run(order=3)
        def test_003_validating_forwarder_and_recursion(self):
                logging.info("Validating forwarder and recursion")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('.*bash.*')
                child.sendline('cat /infoblox/var/named_conf/named.conf')
                try:
                    child.expect('recursion yes')
                    forward = "forwarders { "+config.forwarder+"; };"
                    child.expect(forward)
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    child.close()
                    sleep(20)
                    print("Validation complete for forwarder and recursion")
                    logging.info("Validation complete for forwarder and recursion")
                    assert True
                except:
                    child.expect('.*bash.*')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    child.close()
                    sleep(20)
                    print("Validation failed for forwarder and recursion")
                    logging.info("Validation failed for forwarder and recursion")
                    assert False
                

        # Enable DNS on Lan1 and MGMT (v4 and v6) both

        @pytest.mark.run(order=4)
        def test_004_enable_dns_lisen_on_interface_on_lan_mgmt_v4_and_v6(self):
            logging.info("Enable DNS listen on interface on lan1 and mgmt - v4 and v6 both")
            data = {"use_mgmt_port":True, "use_mgmt_ipv6_port":True,"use_lan_port":True, "use_lan_ipv6_port":True}
            mem_dns_ref = mem_dns_ref_string(config.grid_member_fqdn)
            if mem_dns_ref != "NILL":
                response = ib_NIOS.wapi_request('PUT', object_type=mem_dns_ref, fields=json.dumps(data))
                if type(response)!=tuple:
                    grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                    ref = json.loads(grid)[0]['_ref']
                    data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "DNS"}
                    request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data))
                    sleep(120)
                    print("Enabled DNS listen on interface on lan1 and mgmt - v4 and v6")
                    logging.info("Enabled DNS listen on interface on lan1 and mgmt - v4 and v6")
                    assert True
                else:
                    print("Failed to enabled DNS listen on interface on lan1 and mgmt - v4 and v6")
                    logging.info("Failed to enabled DNS listen on interface on lan1 and mgmt - v4 and v6")
                    assert False
            else:
                print("Failed to get the Grid DNS reference string")
                logging.info("Failed to enable forwarder and recursion")
                assert False

        # Configuring DoH and DoT on the standalone Grid having MGMT and fastpath configured

        @pytest.mark.run(order=5)
        def test_005_configure_DoH_and_dot_on_master(self):
                logging.info("Configure DoH/DoT on the master")
                data = {"doh_service": True, "doh_https_session_duration": 40, "dns_over_tls_service": True, "tls_session_duration": 40}
                mem_dns_ref = mem_dns_ref_string(config.grid_member_fqdn)
                if mem_dns_ref != "NILL":
                    response = ib_NIOS.wapi_request('PUT', object_type=mem_dns_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
                    sleep(60)
                    print(response)
                    if type(response)!=tuple:
                        sleep(20)
                        print("DoH/DoT has been configured on the master")
                        logging.info("DoH/DoT has been configured on the master")
                        assert True
                    else:
                        print("Failed to configured DoH/DoT on the member Level")
                        logging.info("Failed to configured DoH/DoT on the member Level")
                        assert False
                else:
                    print("Failed to get the member DNS reference string")
                    logging.info("Failed to get the member DNS reference string")
                    assert False
        
          
        # Enable DCA on the standalone Grid (Master)

        @pytest.mark.run(order=6)
        def test_006_enable_DCA_on_standalone_member(self):
                logging.info("Enable DCA on the master of the Grid")
                data = {"enable_dns": True, "enable_dns_cache_acceleration": True}
                mem_dns_ref = mem_dns_ref_string(config.grid_member_fqdn)
                if mem_dns_ref != "NILL":
                    response = ib_NIOS.wapi_request('PUT', object_type=mem_dns_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
                    print(response)
                    for i in range(1,20):
                        sleep(60)
                        status = os.system("ping -c1 -w2 "+config.grid_vip)
                        print(status)
                        if status == 0:
                            print("System is up")
                            break
                        else:
                            print("System is still down..!!")
                    sleep(10)
                    print("Product Reboot successfull ..!!!")
                    sleep(200)
                    if type(response)!=tuple:
                        print("DCA Enabled successfully")
                        logging.info("DCA Enabled successfully")
                        assert True
                    else:
                        print("Failed to enable DCA on the standalone Grid")
                        logging.info("Failed to enable DCA")
                        assert False
                else:
                        print("Failed to get member reference string")
                        logging.info("Failed to get member reference string")
                        assert False
            
        # Debug log verification for the above test case:

        @pytest.mark.run(order=7)
        def test_007_validate_debug(self):
                logging.info("Validate_DCA_service_running")
                child = pexpect.spawn('ssh admin@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show dns-accel')
                try:
                    child.expect('DNS query stats:')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    child.close()
                    sleep(120)
                    print("Test case Successfull")
                    logging.info("DCA log varification successfull")
                    assert True
                except:
                    child.expect('Infoblox >')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    child.close()
                    sleep(120)
                    print("Test case Failed")
                    logging.info("DCA log varification successfull")
                    assert False

              
        # Verification for the DoH/DoT:

        @pytest.mark.run(order=8)
        def test_008_validate_if_doh_and_dot_enabled(self):
                logging.info("Validating if DOH and DOT enabled")
                child = pexpect.spawn('ssh admin@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show doh-status')
                try:
                    child.expect('DoH is enabled')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    child.close()
                    sleep(120)
                    print("Test case Successfull")
                    logging.info("DoT/DoH log varification successfull")
                    assert True
                except:
                    child.expect('Infoblox >')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    child.close()
                    sleep(120)
                    print("Test case Failed")
                    logging.info("DoT/DoH log varification successfull")
                    assert False

        # Verifying response-padding and infoblox-process-edns0-destination-address from named config when we have doh/dot enabled

        @pytest.mark.run(order=9)
        def test_009_validating_response_padding_and_infoblox_process_edns0_destination_address_from_named_config_with_doh_dot_enabled(self):
                logging.info("Validating response-padding and infoblox-process-edns0-destination-address from named config when we have doh/dot enabled ")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('.*bash.*')
                child.sendline('cat /infoblox/var/named_conf/named.conf')
                try:
                    response_padding = "response-padding { any; } block-size 468;"
                    edns0_listenon = "infoblox-process-edns0-destination-address { 169.254.252.10; fc00::1; };"
                    child.expect(response_padding)
                    child.expect(edns0_listenon)
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    child.close()
                    sleep(20)
                    print("Validation complete and we could find response-padding and infoblox-process-edns0-destination-address in named config")
                    logging.info("Validation complete and we could find the response-padding and infoblox-process-edns0-destination-address in named config")
                    assert True
                except:
                    child.expect('.*bash.*')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    child.close()
                    sleep(20)
                    print("Validation failed for response-padding and infoblox-process-edns0-destination-address")
                    logging.info("Validation failed for esponse-padding and infoblox-process-edns0-destination-address")
                    assert False
                


        # Perfrom a EDNS DoH query on v4 of master whose response size is less than default UDP buffer size (1220B)
        
        @pytest.mark.run(order=10)
        def test_010_check_response_details_of_DoH_query_on_v4_with_edns_having_response_size_less_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoH response details by making a query on v4 with EDNS whose response is less than default UDP buffer size, default - 1220B")
            response = doh_query(config.grid_master_ip)
            if response == "NIL":
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False
            else:
                if "rcode NOERROR" in response:
                    print("The response of the query is" + response)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is less than default UDP buffer size 1220B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed to executed the test case and validate the response is less than default UDP buffer size 1220B !!")
                    assert False

        # Perfrom a EDNS DoH query on v6 member1 whose response size is less than default UDP buffer size (1220B)
        
        @pytest.mark.run(order=11)
        def test_011_check_response_details_of_DoH_query_on_v6_with_edns_having_response_size_less_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoH response details by making a query on v6 with EDNS whose response is less than default UDP buffer size, default - 1220B")
            os.system("ping6 -c2 "+config.lan_v6)
            response = doh_query("["+config.lan_v6+"]")
            if response == "NIL":
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False
            else:
                if "rcode NOERROR" in response:
                    print("The response of the query is" + response)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is less than default UDP buffer size 1220B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed to executed the test case and validate the response is less than default UDP buffer size 1220B !!")
                    assert False

        # Perfrom a EDNS DoH query on v4 of member1 whose response size is bigger than UDP buffer size (1220B)
        
        @pytest.mark.run(order=12)
        def test_012_check_response_details_of_DoH_query_on_v4_with_edns_having_response_size_greater_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoH response details by making a query on v4 with EDNS whose response would be greater than default UDP buffer size, default - 1220B")
            response = doh_query(config.grid_master_ip,'a.1santhosh.com','A',True)
            if response == "NIL":
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False
            else:
                if "rcode NOERROR" in response:
                    print("The response of the query is" + response)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is greater than default UDP buffer size 1220B !!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed to executed the test case and validate the response is greater than default UDP buffer size 1220B !!")
                    assert False

        # Perfrom a EDNS DoH query on v6 of member1 whose response size is bigger than default UDP buffer size (1220B)
        
        @pytest.mark.run(order=13)
        def test_013_check_response_details_of_DoH_query_on_v6_with_edns_having_response_size_greater_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoH response details by making a query on v6 with EDNS whose response would be greater than default UDP buffer size, default - 1220B")
            os.system("ping6 -c2 "+config.lan_v6)
            response = doh_query("["+config.lan_v6+"]",'a.1santhosh.com','A',True)
            if response == "NIL":
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False
            else:
                if "rcode NOERROR" in response:
                    print("The response of the query is" + response)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is greater than default UDP buffer size 1220B !!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed to executed the test case and validate the response is greater than default UDP buffer size 1220B !!")
                    assert False
        
        # Perfrom a DoT queries on v4 with EDNS header whose response size is less then default UDP/EDNS buffer size (1220B)
        
        @pytest.mark.run(order=14)
        def test_014_check_response_details_of_dot_query_on_v4_with_edns_having_response_size_less_than_default_UDP_buffer_size_1220B(self):
            logging.info("Check DoT response details by making a DoT queries on v4 whose response would be less then the default UDP/EDNS buffer size, default - 1220B")
            query = "kdig @"+config.grid_master_ip+" a.flex.com +tls +edns +nopadding"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is less than default UDP buffer size 1220B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Perfrom a DoT queries on v6 with EDNS header whose response size is less then default UDP/EDNS buffer size (1220B)
        
        @pytest.mark.run(order=15)
        def test_015_check_response_details_of_dot_query_on_v6_with_edns_having_response_size_less_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoT response details by making a DoT query on v6 whose response would be less than the default UDP/EDNS buffer size, default - 1220B")
            query = "kdig @"+config.lan_v6+" a.flex.com +tls +edns +nopadding"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is less than default UDP buffer size 1220B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Perfrom a DoT queries on v4 with EDNS whose response size is greater then UDP/EDNS buffer size (1220B)
        
        @pytest.mark.run(order=16)
        def test_016_check_response_details_of_dot_query_on_v4_with_edns_having_response_size_bigger_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoT response details by making a DoT queries on v4 whose response would be greate then the default UDP/EDNS buffer size, default -1220B")
            query = "kdig @"+config.grid_master_ip+" a.1santhosh.com +tls +edns +nopadding"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is greater than default UDP buffer size 1220B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Perfrom a DoT queries on v6 with EDNS whose response size is greater then default UDP/EDNS buffer size (1220B)
        
        @pytest.mark.run(order=17)
        def test_017_check_response_details_of_dot_query_on_v6_with_edns_having_response_size_bigger_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoT response details by making a DoT query on v6 whose response would be greate then the default UDP/EDNS buffer size, default -1220B")
            query = "kdig @"+config.lan_v6+" a.1santhosh.com +tls +edns +nopadding"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is greater than default UDP buffer size 1220B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Perfrom a DoT queries on v4 with padding option set whose response is less than default UDP buffer size (1220B)
        
        @pytest.mark.run(order=18)
        def test_018_check_response_details_of_dot_query_on_v4_with_padding_having_response_size_less_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoT response details by making a DoT queries on v4 with padding whose response is less than default UDP buffer size, default -1220B")
            query = "kdig @"+config.grid_master_ip+" a.flex.com +tls +padding=10"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is less than default UDP buffer size 1220B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Perfrom a DoT queries on v6 with padding option set whose response is less than default UDP buffer size (1220B)
        
        @pytest.mark.run(order=19)
        def test_019_check_response_details_of_dot_query_on_v6_with_padding_having_response_size_less_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoT response details by making a DoT query on v6 with padding whose response is less than default UDP buffer size, default -1220B")
            query = "kdig @"+config.lan_v6+" a.flex.com +tls +padding=10"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is less than default UDP buffer size 1220B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Perfrom a DoT queries on v4 with padding option set whose response is bigger than default UDP buffer size (1220B)
        
        @pytest.mark.run(order=20)
        def test_020_check_response_details_of_dot_query_on_v4_with_padding_having_response_size_bigger_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoT response details by making a DoT queries on v4 with padding whose response is bigger than default UDP buffer size, default 1220B")
            query = "kdig @"+config.grid_master_ip+" a.1santhosh.com +tls +padding=10"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is greater than default UDP buffer size 1220B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Perfrom a DoT queries on v6 with padding option set whose response is bigger than default UDP buffer size (1220B)
        
        @pytest.mark.run(order=21)
        def test_021_check_response_details_of_dot_query_on_v6_with_padding_having_response_bigger_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoT response details by making a DoT query on v6 with padding whose response is bigger than default UDP buffer size, default 1220B")
            query = "kdig @"+config.lan_v6+" a.1santhosh.com +tls +padding=10"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is bigger than default UDP buffer size 1220B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Perfrom normal queries on v4 without padding option set 
        
        @pytest.mark.run(order=22)
        def test_022_check_response_details_of_normal_dns_query_on_v4_without_padding_having_response_size_less_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DNS response details by making a DNS query on v4 without padding")
            query = "kdig @"+config.grid_master_ip+" a.flex.com +nopadding +noedns"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Perfrom normal queries on v6 without padding option set 
        
        @pytest.mark.run(order=23)
        def test_023_check_response_details_of_normal_dns_query_on_v6_without_padding_having_response_size_less_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DNS response details by making a DNS query on v6 without padding")
            query = "kdig @"+config.lan_v6+" a.flex.com +nopadding +noedns"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Perfrom normal dig queries on v4 with padding option set 
        
        @pytest.mark.run(order=24)
        def test_024_check_response_details_of_normal_dns_query_on_v4_with_padding_having_response_size_less_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DNS response details by making a DNS query on v4 with padding")
            query = "kdig @"+config.grid_master_ip+" a.flex.com +padding=10 +edns"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: REFUSED" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the responses are REFUSED when DoH/DoT enabled!!")
                    assert True
                else:
                    print("Failed to executed the test case !!")
                    logging.info("Failed to executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to executed the test case !!")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Perfrom normal dig queries on v6 with padding option set 
        
        @pytest.mark.run(order=25)
        def test_025_check_response_details_of_normal_dns_query_on_v6_with_padding_having_response_size_less_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DNS response details by making a DNS query on v6 with padding")
            query = "kdig @"+config.lan_v6+" a.flex.com +padding=10 +edns"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: REFUSED" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the responses are REFUSED when DoH/DoT Enabled!!")
                    assert True
                else:
                    print("Failed to executed the test case !!")
                    logging.info("Failed to executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to executed the test case !!")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False
    
        # Enable ADP on the master

        @pytest.mark.run(order=26)
        def test_026_enable_ADP_on_master(self):
                logging.info("Enable ADP on the master")
                data = {"enable_service": True}
                response = ib_NIOS.wapi_request('GET', object_type="member:threatprotection",grid_vip=config.grid_vip)
                logging.info(response)
                print(response)
                if type(response)!=tuple:
                    ref1 = json.loads(response)
                    for key in ref1:
                        if config.grid_member_fqdn in key.get('_ref'):
                            mem_ref = key.get('_ref')
                            print(mem_ref)
                            break
                response = ib_NIOS.wapi_request('PUT', object_type=mem_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
                print(response)
                for i in range(1,20):
                    sleep(60)
                    status = os.system("ping -c1 -w2 "+config.grid_vip)
                    print(status)
                    if status == 0:
                        print("System is up")
                        break
                    else:
                        print("System is still down..!!")
                sleep(10)
                print("Product Reboot successfull ..!!!")
                sleep(200)
                if type(response)!=tuple:
                    print("ADP Enabled successfully")
                    logging.info("ADP Enabled successfully")
                    assert True
                else:
                    print("Failed to enable ADP on the Master")
                    logging.info("Failed to enable ADP on the Master")
                    assert False
        
        # Debug log verification for the above test case:

        @pytest.mark.run(order=27)
        def test_027_validate_debug_for_adp_configuration(self):
                logging.info("Validating debug logs for ADP configuration")
                child = pexpect.spawn('ssh admin@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show adp')
                try:
                    child.expect('Threat Protection:               Enabled')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    child.close()
                    sleep(120)
                    print("Test case Successfull")
                    logging.info("DCA log varification successfull")
                    assert True
                except:
                    child.expect('Infoblox >')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    child.close()
                    sleep(120)
                    print("Test case Failed")
                    logging.info("DCA log varification successfull")
                    assert False

        
        # Perfrom a EDNS DoH query on v4 of master whose response size is less than default UDP buffer size (1220B)
        
        @pytest.mark.run(order=28)
        def test_028_check_response_details_of_DoH_query_on_v4_with_edns_having_response_size_less_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoH response details by making a query on v4 with EDNS whose response is less than default UDP buffer size, default - 1220B")
            response = doh_query(config.grid_master_ip)
            if response == "NIL":
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False
            else:
                if "rcode NOERROR" in response:
                    print("The response of the query is" + response)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is less than default UDP buffer size 1220B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed to executed the test case and validate the response is less than default UDP buffer size 1220B !!")
                    assert False

        # Perfrom a EDNS DoH query on v6 member1 whose response size is less than default UDP buffer size (1220B)
        
        @pytest.mark.run(order=30)
        def test_030_check_response_details_of_DoH_query_on_v6_with_edns_having_response_size_less_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoH response details by making a query on v6 with EDNS whose response is less than default UDP buffer size, default - 1220B")
            os.system("ping6 -c2 "+config.lan_v6)
            response = doh_query("["+config.lan_v6+"]")
            if response == "NIL":
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False
            else:
                if "rcode NOERROR" in response:
                    print("The response of the query is" + response)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is less than default UDP buffer size 1220B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed to executed the test case and validate the response is less than default UDP buffer size 1220B !!")
                    assert False

        # Perfrom a EDNS DoH query on v4 of member1 whose response size is bigger than UDP buffer size (1220B)
        
        @pytest.mark.run(order=31)
        def test_031_check_response_details_of_DoH_query_on_v4_with_edns_having_response_size_greater_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoH response details by making a query on v4 with EDNS whose response would be greater than default UDP buffer size, default - 1220B")
            response = doh_query(config.grid_master_ip,'a.1santhosh.com','A',True)
            if response == "NIL":
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False
            else:
                if "rcode NOERROR" in response:
                    print("The response of the query is" + response)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is greater than default UDP buffer size 1220B !!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed to executed the test case and validate the response is greater than default UDP buffer size 1220B !!")
                    assert False

        # Perfrom a EDNS DoH query on v6 of member1 whose response size is bigger than default UDP buffer size (1220B)
        
        @pytest.mark.run(order=32)
        def test_032_check_response_details_of_DoH_query_on_v6_with_edns_having_response_size_greater_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoH response details by making a query on v6 with EDNS whose response would be greater than default UDP buffer size, default - 1220B")
            os.system("ping6 -c2 "+config.lan_v6)
            response = doh_query("["+config.lan_v6+"]",'a.1santhosh.com','A',True)
            if response == "NIL":
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False
            else:
                if "rcode NOERROR" in response:
                    print("The response of the query is" + response)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is greater than default UDP buffer size 1220B !!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed to executed the test case and validate the response is greater than default UDP buffer size 1220B !!")
                    assert False
        
        # Perfrom a DoT queries on v4 with EDNS header whose response size is less then default UDP/EDNS buffer size (1220B)
        
        @pytest.mark.run(order=33)
        def test_033_check_response_details_of_dot_query_on_v4_with_edns_having_response_size_less_than_default_UDP_buffer_size_1220B(self):
            logging.info("Check DoT response details by making a DoT queries on v4 whose response would be less then the default UDP/EDNS buffer size, default - 1220B")
            query = "kdig @"+config.grid_master_ip+" a.flex.com +tls +edns +nopadding"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is less than default UDP buffer size 1220B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Perfrom a DoT queries on v6 with EDNS header whose response size is less then default UDP/EDNS buffer size (1220B)
        
        @pytest.mark.run(order=34)
        def test_034_check_response_details_of_dot_query_on_v6_with_edns_having_response_size_less_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoT response details by making a DoT query on v6 whose response would be less than the default UDP/EDNS buffer size, default - 1220B")
            query = "kdig @"+config.lan_v6+" a.flex.com +tls +edns +nopadding"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is less than default UDP buffer size 1220B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Perfrom a DoT queries on v4 with EDNS whose response size is greater then UDP/EDNS buffer size (1220B)
        
        @pytest.mark.run(order=35)
        def test_035_check_response_details_of_dot_query_on_v4_with_edns_having_response_size_bigger_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoT response details by making a DoT queries on v4 whose response would be greate then the default UDP/EDNS buffer size, default -1220B")
            query = "kdig @"+config.grid_master_ip+" a.1santhosh.com +tls +edns +nopadding"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is greater than default UDP buffer size 1220B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Perfrom a DoT queries on v6 with EDNS whose response size is greater then default UDP/EDNS buffer size (1220B)
        
        @pytest.mark.run(order=36)
        def test_036_check_response_details_of_dot_query_on_v6_with_edns_having_response_size_bigger_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoT response details by making a DoT query on v6 whose response would be greate then the default UDP/EDNS buffer size, default -1220B")
            query = "kdig @"+config.lan_v6+" a.1santhosh.com +tls +edns +nopadding"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is greater than default UDP buffer size 1220B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Perfrom a DoT queries on v4 with padding option set whose response is less than default UDP buffer size (1220B)
        
        @pytest.mark.run(order=37)
        def test_037_check_response_details_of_dot_query_on_v4_with_padding_having_response_size_less_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoT response details by making a DoT queries on v4 with padding whose response is less than default UDP buffer size, default -1220B")
            query = "kdig @"+config.grid_master_ip+" a.flex.com +tls +padding=10"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is less than default UDP buffer size 1220B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Perfrom a DoT queries on v6 with padding option set whose response is less than default UDP buffer size (1220B)
        
        @pytest.mark.run(order=38)
        def test_038_check_response_details_of_dot_query_on_v6_with_padding_having_response_size_less_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoT response details by making a DoT query on v6 with padding whose response is less than default UDP buffer size, default -1220B")
            query = "kdig @"+config.lan_v6+" a.flex.com +tls +padding=10"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is less than default UDP buffer size 1220B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Perfrom a DoT queries on v4 with padding option set whose response is bigger than default UDP buffer size (1220B)
        
        @pytest.mark.run(order=39)
        def test_039_check_response_details_of_dot_query_on_v4_with_padding_having_response_size_bigger_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoT response details by making a DoT queries on v4 with padding whose response is bigger than default UDP buffer size, default 1220B")
            query = "kdig @"+config.grid_master_ip+" a.1santhosh.com +tls +padding=10"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is greater than default UDP buffer size 1220B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Perfrom a DoT queries on v6 with padding option set whose response is bigger than default UDP buffer size (1220B)
        
        @pytest.mark.run(order=40)
        def test_040_check_response_details_of_dot_query_on_v6_with_padding_having_response_bigger_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoT response details by making a DoT query on v6 with padding whose response is bigger than default UDP buffer size, default 1220B")
            query = "kdig @"+config.lan_v6+" a.1santhosh.com +tls +padding=10"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is bigger than default UDP buffer size 1220B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Perfrom normal queries on v4 without padding option set 
        
        @pytest.mark.run(order=41)
        def test_041_check_response_details_of_normal_dns_query_on_v4_without_padding_having_response_size_less_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DNS response details by making a DNS query on v4 without padding")
            query = "kdig @"+config.grid_master_ip+" a.flex.com +nopadding +noedns"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Perfrom normal queries on v6 without padding option set 
        
        @pytest.mark.run(order=42)
        def test_042_check_response_details_of_normal_dns_query_on_v6_without_padding_having_response_size_less_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DNS response details by making a DNS query on v6 without padding")
            query = "kdig @"+config.lan_v6+" a.flex.com +nopadding +noedns"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Perfrom normal dig queries on v4 with padding option set 
        
        @pytest.mark.run(order=43)
        def test_043_check_response_details_of_normal_dns_query_on_v4_with_padding_having_response_size_less_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DNS response details by making a DNS query on v4 with padding")
            query = "kdig @"+config.grid_master_ip+" a.flex.com +padding=10 +edns"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: REFUSED" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the responses are REFUSED when DoH/DoT enabled!!")
                    assert True
                else:
                    print("Failed to executed the test case !!")
                    logging.info("Failed to executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to executed the test case !!")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Perfrom normal dig queries on v6 with padding option set 
        
        @pytest.mark.run(order=44)
        def test_044_check_response_details_of_normal_dns_query_on_v6_with_padding_having_response_size_less_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DNS response details by making a DNS query on v6 with padding")
            query = "kdig @"+config.lan_v6+" a.flex.com +padding=10 +edns"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: REFUSED" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the responses are REFUSED when DoH/DoT Enabled!!")
                    assert True
                else:
                    print("Failed to executed the test case !!")
                    logging.info("Failed to executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to executed the test case !!")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Add custom views  
        
        @pytest.mark.run(order=45)
        def test_045_add_custom_views(self):
            logging.info("Add custom views")
            data = {"name": "custom"}
            response = ib_NIOS.wapi_request('POST', object_type="view", fields=json.dumps(data))
            if type(response)!=tuple:
                sleep(60)
                print("View Created")
                dns_restart(config.grid_member_fqdn)
                print("DNS Restart Successfull")
                logging.info("Successfully added custom view")
                assert True
            else:
                print("Failed to add custom view")
                logging.info("Failed to add custom view")
                assert False
        
        #Verify custom view
        @pytest.mark.run(order=46)
        def test_046_verify_custom_views(self):
            logging.info("Verify custom views")
            response = ib_NIOS.wapi_request('GET', object_type="view")
            logging.info(response)
            print(response)
            if type(response)!=tuple:
                ref1 = json.loads(response)
                for key in ref1:
                    if key.get('name') == "custom":
                        a = True
                if a == True:
                    print("Successfully verify the custom view")
                    logging.info("Successfully verify the custom view")
                    assert True
                else:
                    print("Failed to verify custom view")
                    logging.info("Failed to verify custom view")
                    assert False
            else:
                print("Failed to get view information")
                logging.info("Failed to get view information")
                assert False

        #ADD match-destination ACL to custom and default view. LAN1 IP in custom view and mgmt IP in default view.
        @pytest.mark.run(order=47)
        def test_047_add_match_destination_acl_on_custom_and_default_view(self):
            logging.info("ADD match-destination ACL to custom and default view")
            response = ib_NIOS.wapi_request('GET', object_type="view")
            logging.info(response)
            print(response)
            if type(response)!=tuple:
                ref1 = json.loads(response)
                for key in ref1:
                    if key.get('name') == "custom":
                        grid_ref = key.get('_ref')
                    if key.get('name') == "default":
                        grid_default_ref = key.get('_ref')
            else:
                print("Failed to get view information")
                logging.info("Failed to get view information")
                assert False
            data_custom = {"match_destinations":[{"address":""+config.grid_master_ip+"","permission":"ALLOW","_struct": "addressac"},{"address":""+config.lan_v6+"","permission":"ALLOW","_struct": "addressac"}]}
            response_custom = ib_NIOS.wapi_request('PUT', object_type=grid_ref, fields=json.dumps(data_custom))

            data_default = {"match_destinations":[{"address":""+config.grid_vip+"","permission":"ALLOW","_struct": "addressac"},{"address":""+config.mgmt_v6+"","permission":"ALLOW","_struct": "addressac"}]}
            response_default = ib_NIOS.wapi_request('PUT', object_type=grid_default_ref, fields=json.dumps(data_default))
            dns_restart(config.grid_member_fqdn)
            if type(response_custom)!=tuple and type(response_default)!=tuple:
                logging.info("Match Destination ACL Added successfully")
                assert True
            else:
                logging.info("Failed to add match-destination ACL")
                assert False

        #Verify ACL on Default view.
        @pytest.mark.run(order=48)
        def test_048_verify_match_destination_acl_on_default_view(self):
            logging.info("Verify match-destination ACL on default view")
            response = ib_NIOS.wapi_request('GET', object_type="view")
            logging.info(response)
            print(response)
            if type(response)!=tuple:
                ref1 = json.loads(response)
                for key in ref1:
                    if key.get('name') == "default":
                        grid_default_ref = key.get('_ref')
            else:
                logging.info("Failed to GET Grid info")
                assert False
            response = ib_NIOS.wapi_request('GET', object_type=grid_default_ref + "?_return_fields=match_destinations")
            logging.info(response)
            if type(response)!=tuple:
                ref1 = json.loads(response)
                if ref1["match_destinations"][0].get("address") == config.grid_vip:
                    logging.info("ACL verified successfully on default view")
                    assert True
                else:
                    logging.info("Failed to verify ACL on default view")
                    assert False
            else:
                logging.info("Failed to GET match-destination details")
                assert False
        
        #Verify ACL on Custom view.
        @pytest.mark.run(order=49)
        def test_049_verify_match_destination_acl_on_custom_view(self):
            logging.info("Verify match-destination ACL on custom view")
            response = ib_NIOS.wapi_request('GET', object_type="view")
            logging.info(response)
            print(response)
            if type(response)!=tuple:
                ref1 = json.loads(response)
                for key in ref1:
                    if key.get('name') == "custom":
                        grid_default_ref = key.get('_ref')
            else:
                logging.info("Failed to GET Grid info")
                assert False
            response = ib_NIOS.wapi_request('GET', object_type=grid_default_ref + "?_return_fields=match_destinations")
            logging.info(response)
            if type(response)!=tuple:
                ref1 = json.loads(response)
                if ref1["match_destinations"][0].get("address") == config.grid_master_ip:
                    logging.info("ACL verified successfully on custom view")
                    assert True
                else:
                    logging.info("Failed to verify ACL on custom view")
                    assert False
            else:
                logging.info("Failed to GET match-destination details")
                assert False

        # Perfrom a DoT query on v4 with padding option set whose response is bigger than default UDP buffer size (Default - 1220B) and check if we are getting a response and truncated query is not listenling to BIND internal IP.
        
        @pytest.mark.run(order=50)
        def test_050_check_response_details_of_DoT_query_on_v4_with_padding_having_response_having_bigger_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoT response details by making a DoT query on v4 with padding having bigger response than default UDP buffer 1220B")
            query = "kdig @"+config.grid_master_ip+" aaa.1santhosh.com +tls +padding=10"
            try:
                log("start","/var/log/syslog",config.grid_vip)
                op = os.popen(query)
                h = op.read()
                sleep(20)
                log("stop","/var/log/syslog",config.grid_vip)
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is bigger than default udp buffer size 1220B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Verify if we are getting DoT response on v4 from custom view

        @pytest.mark.run(order=51)
        def test_051_validate_syslog_and_verify_if_DoT_response_from_v4_is_coming_from_custom_view(self):
                logging.info("Validating syslog to verify if DoT response from v4 is coming from custom")
                LookForSys="View 1: TCP: query: aaa.1santhosh.com IN A response: NOERROR"
                logsys = logv(LookForSys,"/var/log/syslog",config.grid_vip)
                if logsys!=None:
                    logging.info("Successfully validate that the DoT responses are coming from custom view")
                    assert True
                else:
                    print("Could not find the expeted logs in the syslog and failed to validate that the DoT responses are coming from custom view")
                    logging.info("Could not find the expeted logs in the syslog and failed to validate that the DoT responses are coming from custom view")
                    assert False        
                

        # Perfrom a DoT query on v6 with padding option set whose response is bigger than default UDP buffer size (Default - 1220B) and check if we are getting a response and truncated query is not listenling to BIND internal IP.
        
        @pytest.mark.run(order=52)
        def test_052_check_response_details_of_DoT_query_on_v6_with_padding_having_response_size_bigger_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoT response details by making a DoT query on v6 with padding having bigger response, default UDP buffer 1220B")
            query = "kdig @"+config.lan_v6+" bbb.1santhosh.com +tls +padding=10"
            try:
                log("start","/var/log/syslog",config.grid_vip)
                op = os.popen(query)
                sleep(120)
                h = op.read()
                print(h,"output of query")
                log("stop","/var/log/syslog",config.grid_vip)
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is bigger than default udp buffer size 1220B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False
            sleep(60)


        # Verify if we are getting DoT response on v6 from custom view

        @pytest.mark.run(order=53)
        def test_053_validate_syslog_and_verify_if_DoT_response_from_v6_is_coming_from_custom_view(self):
                logging.info("Validating syslog to verify if DoT response from v6 is coming from custom view")
                LookForSys="View 1: TCP: query: bbb.1santhosh.com IN A response: NOERROR"
                logsys = logv(LookForSys,"/var/log/syslog",config.grid_vip)
                print(logsys,"output from logsssssss")
                if logsys!=None:
                    logging.info("Successfully validate that the DoT responses are coming from custom view")
                    assert True
                else:
                    print("Could not find the expeted logs in the syslog and failed to validate that the DoT responses are coming from custom view")
                    logging.info("Could not find the expeted logs in the syslog and failed to validate that the DoT responses are coming from custom view")
                    assert False

        # Perfrom a EDNS DoH query on v6 with padding option set whose response is bigger than default UDP buffer size (default 1220B) and check if we are getting a response and truncated query is not listenling to BIND internal IP.
        
        @pytest.mark.run(order=54)
        def test_054_check_response_details_of_DoH_query_on_v6_with_edns_having_response_size_greater_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoH response details by making a query on v6 with EDNS whose response would be greater than default UDP buffer size, default - 1220B")
            os.system("ping6 -c2 "+config.lan_v6)
            log("start","/var/log/syslog",config.grid_vip)
            response = doh_query("["+config.lan_v6+"]",'ccc.1santhosh.com','A',True)
            sleep(10)
            log("stop","/var/log/syslog",config.grid_vip)
            if response == "NIL":
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False
            else:
                if "rcode NOERROR" in response:
                    print("The response of the query is" + response)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is greater than default udp buffer size 1220B !!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed to executed the test case and validate the response is greater than default udp buffer size 1220B !!")
                    assert False

        # Verify if we are getting DoH response on v6 from custom view

        @pytest.mark.run(order=55)
        def test_055_validate_syslog_and_verify_if_DoH_response_from_v6_is_coming_from_custom_view(self):
                logging.info("Validating syslog to verify if DoH response from v6 is coming from custom view")
                LookForSys="View 1: TCP: query: ccc.1santhosh.com IN A response: NOERROR"
                logsys = logv(LookForSys,"/var/log/syslog",config.grid_vip)
                if logsys!=None:
                    logging.info("Successfully validate that the DoH responses are coming from custom view")
                    assert True
                else:
                    print("Could not find the expeted logs in the syslog and failed to validate that the DoH responses are coming from custom view")
                    logging.info("Could not find the expeted logs in the syslog and failed to validate that the DoH responses are coming from custom view")
                    assert False

        # Perfrom a EDNS DoH query on v4 with padding option set whose response is bigger than default UDP buffer size (default 1220B) and check if we are getting a response and truncated query is not listenling to BIND internal IP.
        
        @pytest.mark.run(order=56)
        def test_056_check_response_details_of_DoH_query_on_v4_with_edns_having_response_size_greater_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoH response details by making a query on v4 with EDNS whose response would be greater than default UDP buffer size, default - 1220B")
            log("start","/var/log/syslog",config.grid_vip)
            response = doh_query(config.grid_master_ip,'ddd.1santhosh.com','A',True)
            sleep(10)
            log("stop","/var/log/syslog",config.grid_vip)
            if response == "NIL":
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False
            else:
                if "rcode NOERROR" in response:
                    print("The response of the query is" + response)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is bigger than default udp buffer size 1220B !!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed to executed the test case and validate the response is bigger than default udp buffer size 1220B !!")
                    assert False

        # Verify if we are getting DoH response on v4 from custom view

        @pytest.mark.run(order=57)
        def test_057_validate_syslog_and_verify_if_DoH_response_from_v4_is_coming_from_custom(self):
                logging.info("Validating syslog to verify if DoH response from v4 is coming from custom view")
                LookForSys="View 1: TCP: query: ddd.1santhosh.com IN A response: NOERROR"
                logsys = logv(LookForSys,"/var/log/syslog",config.grid_vip)
                if logsys!=None:
                    logging.info("Successfully validate that the DoH responses are coming from custom view")
                    assert True
                else:
                    print("Could not find the expeted logs in the syslog and failed to validate that the DoH responses are coming from custom view")
                    logging.info("Could not find the expeted logs in the syslog and failed to validate that the DoH responses are coming from custom view")
                    assert False

        
        # Enable Trace on DoT

        @pytest.mark.run(order=58)
        def test_058_enable_tarce_on_DoT_server(self):
                logging.info("Enable Trace on DOT server")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('.*bash.*')
                child.sendline('fp-cli fp ib_dca set dot_trace 1')
                try:
                    response_dot = "DOT trace is set to on"
                    child.expect(response_dot)
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    child.close()
                    sleep(120)
                    print("Enabled trace on DOT Server")
                    logging.info("Enabled trace on DoT server")
                    assert True
                except:
                    child.expect('.*bash.*')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    child.close()
                    sleep(120)
                    print("Failed to enabled trace on DOT Server")
                    logging.info("Failed to enabled trace on DoT server")
                    assert False

        # Validate Trace on DoT

        @pytest.mark.run(order=59)
        def test_059_validate_trace_on_dot_server(self):
                logging.info("Validating trace on DOT server")
                child = pexpect.spawn('ssh admin@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show dns-over-tls-status')
                try:
                    child.expect('DoT trace is on')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    child.close()
                    sleep(120)
                    print("Successfully Validate DoT trace enabled")
                    logging.info("Successfully Validate DoT trace enabled")
                    assert True
                except:
                    child.expect('DoT trace is off')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    child.close()
                    sleep(120)
                    print("Failed to Validate DoT trace enabled")
                    logging.info("Failed to Validate DoT trace enabled")
                    assert False

        # Enable Trace on DoH

        @pytest.mark.run(order=60)
        def test_060_enable_tarce_on_DoH_server(self):
                logging.info("Enable Trace on DOH server")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('.*bash.*')
                child.sendline('fp-cli fp ib_dca set doh_trace 1')
                try:
                    response_dot = "DOH trace is set to on"
                    child.expect(response_dot)
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    child.close()
                    sleep(20)
                    print("Enabled trace on DOH Server")
                    logging.info("Enabled trace on DoH server")
                    assert True
                except:
                    child.expect('.*bash.*')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    child.close()
                    sleep(20)
                    print("Failed to enabled trace on DOH Server")
                    logging.info("Failed to enabled trace on DoH server")
                    assert False

        # Validate Trace on DoH

        @pytest.mark.run(order=61)
        def test_061_validate_trace_on_doh_server(self):
                logging.info("Validating trace on DOH server")
                child = pexpect.spawn('ssh admin@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show doh-status')
                try:
                    child.expect('DoH trace is on')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    child.close()
                    sleep(120)
                    print("Successfully Validate DoH trace enabled")
                    logging.info("Successfully Validate DoH trace enabled")
                    assert True
                except:
                    child.expect('DoH trace is off')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    child.close()
                    sleep(120)
                    print("Failed to Validate DoH trace enabled")
                    logging.info("Failed to Validate DoH trace enabled")
                    assert False

        # Perform truncated DoT query on the v6 address of the server whose response is greater than default UDP buffer size 1220B

        @pytest.mark.run(order=62)
        def test_062_check_response_details_of_DoT_query_on_v6_with_padding_having_response_size_bigger_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoT response details by making a DoT query on v6 with padding having bigger response, default UDP buffer 1220B")
            query = "kdig @"+config.lan_v6+" bbb.1santhosh.com +tls +padding=10"
            try:
                log("start","/var/log/syslog",config.grid_vip)
                op = os.popen(query)
                h = op.read()
                sleep(5)
                log("stop","/var/log/syslog",config.grid_vip)
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is bigger than default udp buffer size 1220B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Validate the response of the above DoT query on v6 address and check if we have used FC00:01 address for fastpath to Bind communication for truncated query. 

        @pytest.mark.run(order=63)
        def test_063_validate_syslog_and_verify_if_truncated_queries_are_communicating_with_fc00_01_between_fastpath_and_bind(self):
                logging.info("Validating syslog to verify if truncated DOT queries are communicating with FC00:01 between fastpath and bind")
                LookForSys="TCP Connection attempt to ip:fc00::1 port:8853"
                logsys = logv(LookForSys,"/var/log/syslog",config.grid_vip)
                if logsys!=None:
                    logging.info("Successfully validate that the DoT truncated response use FC00:01 IP to communicate with BIND")
                    assert True
                else:
                    print("Could not find the expeted logs in the syslog and failed to validate that the DoT responses")
                    logging.info("Could not find the expeted logs in the syslog and failed to validate that the DoT responses")
                    assert False

        # Perform truncated DoT query on the v4 address of the server whose response is greater than default UDP buffer size 1220B

        @pytest.mark.run(order=64)
        def test_064_check_response_details_of_DoT_query_on_v4_with_padding_having_response_size_bigger_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoT response details by making a DoT query on v4 with padding having bigger response, default UDP buffer 1220B")
            query = "kdig @"+config.grid_master_ip+" bbb.1santhosh.com +tls +padding=10"
            try:
                log("start","/var/log/syslog",config.grid_vip)
                op = os.popen(query)
                h = op.read()
                sleep(5)
                log("stop","/var/log/syslog",config.grid_vip)
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is bigger than default udp buffer size 1220B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Validate the response of the above DoT query on v4 address and check if we have used 169.254.252.10 address for fastpath to Bind communication for truncated query. 

        @pytest.mark.run(order=65)
        def test_065_validate_syslog_and_verify_if_truncated_queries_are_communicating_with_169_254_252_10_between_fastpath_and_bind(self):
                logging.info("Validating syslog to verify if truncated DOT queries are communicating with 169.254.252.10 between fastpath and bind")
                LookForSys="TCP Connection attempt to ip:169.254.252.10 port:8853"
                logsys = logv(LookForSys,"/var/log/syslog",config.grid_vip)
                if logsys!=None:
                    logging.info("Successfully validate that the DoT truncated response use 169.254.252.10 IP to communicate with BIND")
                    assert True
                else:
                    print("Could not find the expeted logs in the syslog and failed to validate that the DoT responses")
                    logging.info("Could not find the expeted logs in the syslog and failed to validate that the DoT responses")
                    assert False 

        # Perform truncated DoH query on the v4 address of the server whose response is greater than default UDP buffer size 1220B

        @pytest.mark.run(order=66)
        def test_066_check_response_details_of_DoH_query_on_v4_with_edns_having_response_size_greater_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoH response details by making a query on v4 with EDNS whose response would be greater than default UDP buffer size, default - 1220B")
            log("start","/var/log/syslog",config.grid_vip)
            response = doh_query(config.grid_master_ip,'ddd.1santhosh.com','A',True)
            sleep(10)
            log("stop","/var/log/syslog",config.grid_vip)
            if response == "NIL":
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False
            else:
                if "rcode NOERROR" in response:
                    print("The response of the query is" + response)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is bigger than default udp buffer size 1220B !!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed to executed the test case and validate the response is bigger than default udp buffer size 1220B !!")
                    assert False

        # Validate the response of the above query and check if we have used 169.254.252.10 address for fastpath to Bind communication for truncated query. 

        @pytest.mark.run(order=67)
        def test_067_validate_syslog_and_verify_if_truncated_queries_are_communicating_with_169_254_252_10_between_fastpath_and_bind(self):
                logging.info("Validating syslog to verify if truncated DOH queries are communicating with 169.254.252.10 between fastpath and bind")
                LookForSys="TCP Connection attempt to ip:169.254.252.10 port:8443"
                logsys = logv(LookForSys,"/var/log/syslog",config.grid_vip)
                if logsys!=None:
                    logging.info("Successfully validate that the DoH truncated response use 169.254.252.10 IP to communicate with BIND")
                    assert True
                else:
                    print("Could not find the expeted logs in the syslog and failed to validate that the DoH responses")
                    logging.info("Could not find the expeted logs in the syslog and failed to validate that the DoH responses")
                    assert False 

        # Perform truncated DoH query on the v6 address of the server whose response is greater than default UDP buffer size 1220B

        @pytest.mark.run(order=68)
        def test_068_check_response_details_of_DoH_query_on_v6_with_edns_having_response_size_greater_than_default_udp_buffer_size_1220B(self):
            logging.info("Check DoH response details by making a query on v6 with EDNS whose response would be greater than default UDP buffer size, default - 1220B")
            os.system("ping6 -c2 "+config.lan_v6)
            log("start","/var/log/syslog",config.grid_vip)
            response = doh_query("["+config.lan_v6+"]",'ccc.1santhosh.com','A',True)
            sleep(10)
            log("stop","/var/log/syslog",config.grid_vip)
            if response == "NIL":
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False
            else:
                if "rcode NOERROR" in response:
                    print("The response of the query is" + response)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is bigger than default udp buffer size 1220B !!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed to executed the test case and validate the response is bigger than default udp buffer size 1220B !!")
                    assert False

        # Validate the response of the above query on v6 and check if we have used FC00::01 address for fastpath to Bind communication for truncated query. 

        @pytest.mark.run(order=69)
        def test_069_validate_syslog_and_verify_if_truncated_queries_are_communicating_with_FC00_01_between_fastpath_and_bind(self):
                logging.info("Validating syslog to verify if truncated DOH queries are communicating with FC00::01 between fastpath and bind")
                LookForSys="TCP Connection attempt to ip:FC00::1 port:8443"
                logsys = logv(LookForSys,"/var/log/syslog",config.grid_vip)
                if logsys!=None:
                    logging.info("Successfully validate that the DoH truncated response use FC00::01 IP to communicate with BIND")
                    assert True
                else:
                    print("Could not find the expeted logs in the syslog and failed to validate that the DoH responses")
                    logging.info("Could not find the expeted logs in the syslog and failed to validate that the DoH responses")
                    assert False

        # Change the buffer size from 1220B to 4096B.

        @pytest.mark.run(order=70)
        def test_070_change_the_buffer_size_from_1220B_to_4096B(self):
                logging.info("Change the buffer size from 1220B to 4096B")
                data = {"edns_udp_size": 4096, "max_udp_size": 4096}
                mem_dns_ref = mem_dns_ref_string(config.grid_member_fqdn)
                if mem_dns_ref != "NILL":
                    response = ib_NIOS.wapi_request('PUT', object_type=mem_dns_ref, fields=json.dumps(data))
                    print(response)
                    if type(response)!=tuple:
                        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
                        ref = json.loads(grid)[0]['_ref']
                        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "DNS"}
                        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data))
                        sleep(120)
                        print("Changed the EDNS0 UDP buffer size from 1220B to 4096B")
                        logging.info("Changed the EDNS0 UDP buffer size from 1220B to 4096B")
                        assert True
                    else:
                        print("Failed to Changed the EDNS0 UDP buffer size from 1220B to 4096B")
                        logging.info("Failed to Changed the EDNS0 UDP buffer size from 1220B to 4096B")
                        assert False
                else:
                    print("Failed to get the Member DNS reference string")
                    logging.info("Failed to get the Member DNS reference string")
                    assert False
        
        # Perfrom a EDNS DoH query on v6 with padding option set whose response is less than default UDP buffer size (4096B) and verify the response.        
        @pytest.mark.run(order=71)
        def test_071_check_response_details_of_DoH_query_on_v6_with_edns_whose_response_size_is_less_than_default_udp_buffer_size_4096B(self):
            logging.info("Check DoH response details by making a query on v6 with EDNS whose response would be less than default UDP buffer size, default - 4096B")
            os.system("ping6 -c2 "+config.lan_v6)
            response = doh_query("["+config.lan_v6+"]",'a.flex.com','A',True)
            if response == "NIL":
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False
            else:
                if "rcode NOERROR" in response:
                    print("The response of the query is" + response)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is less than default UDP buffer size 4096B !!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed to executed the test case and validate the response is less than default UDP buffer size 4096B !!")
                    assert False
        sleep(60)
        # Perfrom a EDNS DoT query on v6 with padding option set whose response is bigger than default UDP buffer size (4096B) and verify the response.
        
        @pytest.mark.run(order=72)
        def test_072_check_response_details_of_DoT_query_on_v6_with_padding_whose_response_is_bigger_than_default_udp_buffer_size_4096B(self):
            logging.info("Check response details of a DoT query on v6 with padding whose response is bigger than default UDP buffer size 4096B")
            query = "kdig @"+config.lan_v6+" a.1santhosh.com TXT +tls +padding=10"
            try:
                op = os.popen(query)
                sleep(120)
                h = op.read()
                print(h)
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is bigger than 4096B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

        # Perfrom a EDNS DoT query on v4 with padding option set whose response is lesser than default UDP buffer size (4096B) and verify the response.
        
        @pytest.mark.run(order=73)
        def test_073_check_response_details_of_DoT_query_on_v6_with_padding_whose_response_is_lesser_than_default_udp_buffer_size_4096B(self):
            logging.info("Check response details of a DoT query on v6 with padding whose response is lesser than default UDP buffer size 4096B")
            query = "kdig @"+config.grid_master_vip+" a.flex.com +tls +padding=10"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response is lesser than default UDP buffer size 4096B!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False


        # Disable DoH and DoT on the standalone Grid having MGMT and fastpath configured

        @pytest.mark.run(order=74)
        def test_074_disable_DoH_and_dot_on_master(self):
                logging.info("Disable DoH/DoT on the master")
                data = {"doh_service": False, "doh_https_session_duration": 40, "dns_over_tls_service": False, "tls_session_duration": 40}
                mem_dns_ref = mem_dns_ref_string(config.grid_member_fqdn)
                if mem_dns_ref != "NILL":
                    response = ib_NIOS.wapi_request('PUT', object_type=mem_dns_ref, fields=json.dumps(data),grid_vip=config.grid_vip)
                    sleep(60)
                    print(response)
                    if type(response)!=tuple:
                        prod_reboot(config.grid_vip)
                        sleep(120)
                        print("DoH/DoT has been disabled on the master")
                        logging.info("DoH/DoT has been disabled on the master")
                        assert True
                    else:
                        print("Failed to disable DoH/DoT on the member Level")
                        logging.info("Failed to disable DoH/DoT on the member Level")
                        assert False
                else:
                    print("Failed to get the member DNS reference string")
                    logging.info("Failed to get the member DNS reference string")
                    assert False

        # Debug log verification for the above test case:

        @pytest.mark.run(order=75)
        def test_075_validate_debug_logs_for_disabling_doh_dot_feature(self):
                logging.info("Validating debug logs for disabling DoH/DoT feature")
                child = pexpect.spawn('ssh admin@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('password:')
                child.sendline('infoblox')
                child.expect('Infoblox >')
                child.sendline('show doh-status')
                try:
                    child.expect('DoH is enabled')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    child.close()
                    sleep(120)
                    print("Test case Successfull")
                    logging.info("DoT/DoH log varification successfull")
                    assert False
                except:
                    child.expect('Infoblox >')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    child.close()
                    sleep(120)
                    print("Test case Failed")
                    logging.info("DoT/DoH log varification successfull")
                    assert True



        # Verifying response-padding and infoblox-process-edns0-destination-address from named config when we have doh/dot disabled

        @pytest.mark.run(order=76)
        def test_076_validating_response_padding_and_infoblox_process_edns0_destination_address_from_named_config_with_doh_dot_disable(self):
                logging.info("Validating response-padding and infoblox-process-edns0-destination-address from named config when we have doh/dot disable ")
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no root@'+config.grid_vip)
                child.logfile=sys.stdout
                child.expect('.*bash.*')
                child.sendline('cat /infoblox/var/named_conf/named.conf')
                try:
                    response_padding = "response-padding { any; } block-size 468;"
                    edns0_listenon = "infoblox-process-edns0-destination-address { 169.254.252.10; };"
                    child.expect(response_padding)
                    child.expect(edns0_listenon)
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    child.close()
                    sleep(20)
                    print("Validation failed and we could find the response-padding and infoblox-process-edns0-destination-address")
                    logging.info("Validation failed and we could find the response-padding and infoblox-process-edns0-destination-address")
                    assert False
                except:
                    child.expect('.*bash.*')
                    child.sendline('exit')
                    child.expect(pexpect.EOF)
                    child.close()
                    sleep(20)
                    print("Validation successfull and we cound not find the response-padding and infoblox-process-edns0-destination-address in named config")
                    logging.info("Validation successfull and we could not find the response-padding and infoblox-process-edns0-destination-address in named config")
                    assert True
                

        # Perfrom normal queries with padding option set when doh and dot is not enabled 
        
        @pytest.mark.run(order=77)
        def test_077_check_response_details_of_normal_dns_query_with_padding_when_doh_dot_is_disabled(self):
            logging.info("Check DNS response details by making a DNS query with padding when DoH/DoT is not enabled")
            query = "kdig @"+config.grid_master_ip+" a.flex.com +padding=10 +edns"
            try:
                op = os.popen(query)
                h = op.read()
                if "status: NOERROR" in h:
                    print(h)
                    print("Successfully executed the test case !!")
                    logging.info("Successfully executed the test case and validated the response!!")
                    assert True
                else:
                    print("Failed to execute the test case")
                    logging.info("Failed executed the test case and validated the response!!")
                    assert False    
            except:
                print("Failed to execute the test case")
                logging.info("Failed to executed the test case and validated the response!!")
                assert False

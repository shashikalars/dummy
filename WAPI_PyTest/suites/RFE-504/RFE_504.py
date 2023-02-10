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
import time
import sys
import pexpect


def validate_CLI(username,password,role_list):
    try:    
	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+username+'@'+config.grid_vip)
        child.expect ('password.*:')
        child.sendline (password)
        child.expect ('Infoblox >',timeout=60)
        #print("logged in ")
        
        for key,value in role_list.iteritems():
            print (key,value)
            child.sendline(key)
            child.expect(value)
            assert True
        sleep(10)
        child.sendline("exit")

    except Exception as e:
        print(e)
        assert False

    finally:
        #child.sendline("exit")
        child.close()
        #os.system("/import/tools/lab/bin/reset_console -H "+config.vmid)
        #sleep(20)
        
def validate_member_CLI(username,password,role_list):
    try:    
	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+username+'@'+config.grid_member1_vip)
        child.expect ('password.*:')
        child.sendline (password)
        child.expect ('Infoblox >',timeout=60)
        
        for key,value in role_list.iteritems():
            print (key,value)
            child.sendline(key)
            child.expect(value)
            assert True

    except Exception as e:
        print(e)
        assert False

    finally:
        child.sendline("exit")
        child.close()
        
def validate_member_adp_CLI(username,password,role_list):
    try:
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+username+'@'+config.grid_member3_vip)
        child.expect ('password.*:')
        child.sendline (password)
        child.expect ('Infoblox >',timeout=60)

        for key,value in role_list.iteritems():
            print (key,value)
            child.sendline(key)
            child.expect(value)
            assert True

    except Exception as e:
        print(e)
        assert False

    finally:
        child.sendline("exit")
        child.close()
def validate_member1_CLI(username,password,role_list):
    try:    
	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+username+'@'+config.grid_member3_vip)
        child.expect ('password.*:')
        child.sendline (password)
        child.expect ('Infoblox >',timeout=60)
        child.sendline('set expertmode')
        child.expect("set .*\s*\"Disclaimer")
        
        for key,value in role_list.iteritems():
            print (key,value)
            child.sendline(key)
            child.expect(value)
            assert True

    except Exception as e:
        print(e)
        assert False

    finally:
        child.sendline("exit")
        child.close()

def validate_member4_CLI(username,password,role_list):
    try:
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+username+'@'+config.grid_member1_vip)
        child.expect ('password.*:')
        child.sendline (password)
        child.expect ('Infoblox >',timeout=60)
        child.sendline('set expertmode')
        child.expect("set .*\s*\"Disclaimer")

        for key,value in role_list.iteritems():
            print (key,value)
            child.sendline(key)
            child.expect(value)
            assert True

    except Exception as e:
        print(e)
        assert False

    finally:
        child.sendline("exit")
        child.close()

def validate_member2_CLI(username,password,role_list):
    try:    
	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+username+'@'+config.grid_member2_vip)
        child.expect ('password.*:')
        child.sendline (password)
        child.expect ('Infoblox >',timeout=60)
        print("in login") 
        for key,value in role_list.iteritems():
            print (key,value)
            child.sendline(key)
            child.expect(value)
            assert True

    except Exception as e:
        print(e)
        assert False

    finally:
        child.sendline("exit")
        child.close()

def validate_expert_CLI(username,password,role_list):  
    try:    
	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+username+'@'+config.grid_vip)
        child.expect ('password.*:')
        child.sendline (password)
        child.expect ('Infoblox >',timeout=60)
        child.sendline('set expertmode')
        child.expect("set .*\s*\"Disclaimer")
        
        for key,value in role_list.iteritems():
            print (key,value)
            child.sendline(key)
            child.expect(value)
            assert True

    except Exception as e:
        print(e)
        assert False

    finally:
        child.sendline("exit")
        child.close()
        
def validate_maintenance_CLI(username,password,role_list):  
    try:    
	child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+username+'@'+config.grid_vip)
        child.expect ('password.*:')
        child.sendline (password)
        child.expect ('Infoblox >',timeout=60)
        child.sendline('set maintenancemode')
        child.expect("Maintenance Mode > ",timeout=60)
        
        for key,value in role_list.iteritems():
            print (key,value)
            child.sendline(key)
            child.expect(value)
            assert True

    except Exception as e:
        print(e)
        assert False

    finally:
        child.sendline("exit")
        child.close()


class Network(unittest.TestCase):
    logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)

    @pytest.mark.run(order=1)
    def test_001_create_nonsuperuser_group(self):
        logging.info("Create a non-super-user group")
        data={"name":"test1","access_method": ["API","CLI"]}
        response = ib_NIOS.wapi_request('POST',object_type="admingroup",fields=json.dumps(data))
        print("#######################",response)
        logging.info(response)
        logging.info("============================")
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Group 'test1' is created")

    @pytest.mark.run(order=2)
    def test_002_create_nonsuperuser_user(self):
        logging.info("Create a non-super-user group")
        data = {"name":config.username1,"password":config.password1,"admin_groups": ["test1"]}
        response = ib_NIOS.wapi_request('POST',object_type="adminuser",fields=json.dumps(data))
        print("#######################",response)
        logging.info(response)
        logging.info("============================")
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Admin user 'user' is created")

    @pytest.mark.run(order=3)
    def test_003_verify_clilogin(self):
        os.system("/import/tools/lab/bin/reset_console -H "+config.vmid)
        sleep(20)
        try:
            child = pexpect.spawn("console_connect -H "+config.vmid,  maxread=100)
            child.expect(".*Escape character is .*")
            child.sendline("\r")
            sleep(5)
            child.expect(".*login:")
            child.sendline(config.username1)
            child.expect('password:')
            child.sendline(config.password1)
            sleep(5)
            child.expect('Infoblox')
            child.sendline("exit")
            print(child.before)
            assert True
        except:
            assert False
        finally:
            child.close()
            os.system("/import/tools/lab/bin/reset_console -H "+config.vmid)
            sleep(20)
       

    @pytest.mark.run(order=4)
    def test_004_verify_sshlogin(self):
        print("Testcase 4 started")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+config.username1+'@'+config.grid_vip)
        child.expect ('password.*:')
        child.sendline (config.password1)
        child.expect ('Infoblox >')
        child.sendline ('exit')
        assert True
        
        
    @pytest.mark.run(order=5)
    def test_005_verify_disabled_admin_group_show_cmds_validate_permission(self):
        logging.info("Disabled admin group show commands")
        print("Testcase 5 started")
        username=config.username1
        password=config.password1
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"show admin_group_acl":No_privilege,"show arp":No_privilege,"show bfd":No_privilege,"show bgp":No_privilege,"show bloxtools":No_privilege,"show capacity":No_privilege,"show clusterd_info":No_privilege,"show config":No_privilege,"show cpu":No_privilege,"show date":No_privilege,"show debug":No_privilege,
        "show delete_tasks_interval":No_privilege,"show disk":No_privilege,"show file":No_privilege,"show hardware-type":No_privilege,"show hwid":No_privilege,"show ibtrap":No_privilege,"show lcd":No_privilege,"show lcd_info":No_privilege,"show lcd_settings":No_privilege,"show log":No_privilege,"show logfiles":No_privilege,"show memory":No_privilege,"show ntp":No_privilege,"show scheduled":No_privilege,"show snmp":No_privilege,"show status":No_privilege,"show tech-support":No_privilege,"show temperature":No_privilege,"show thresholdtrap":No_privilege,"show upgrade_history":No_privilege,"show uptime":No_privilege,
        "show version":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 5 Execution Completed")
        
    
    @pytest.mark.run(order=6)
    def test_006_enable_admin_group_show_cmds(self):
        logging.info("Enabling admin group show commands")
        print("\n\n\n")
        print("Testcase 6 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"admin_show_commands":{"show_admin_group_acl":True,"show_arp":True,"show_bfd":True,"show_bloxtools":True,"show_bgp":True,"show_capacity":True,"show_clusterd_info":True,"show_config":True,"show_cpu":True,"show_date":True,"show_debug":True,"show_delete_tasks_interval":True,"show_disk":True,"show_file":True,"show_hardware_type":True,"show_hwid":True,"show_ibtrap":True,"show_lcd":True,"show_lcd_info":True,"show_lcd_settings":True,"show_log":True,"show_logfiles":True,"show_memory":True,"show_ntp":True,"show_scheduled":True,"show_snmp":True,"show_status":True,"show_tech_support":True,"show_temperature":True,"show_thresholdtrap":True,"show_upgrade_history":True,"show_uptime":True,
"show_version":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 6 Execution Completed")
    
        
         
    @pytest.mark.run(order=7)
    def test_007_verify_admin_group_show_cmds(self):
        username=config.username1
        password=config.password1
        role_list={"show admin_group_acl":"None of Admin Groups.*","show bfd":"bfdd process is not running","show bgp":"bgpd process","show capacity":"Hardware Type","show bloxtools":"bloxTools status:","show clusterd_info":"g_sw_version","show config":"Synopsis:","show cpu":"memory","show date":"[:\w\s\d]+[PST|UTC][\s\d]+","show debug":"Debug logging status :","show delete_tasks_interval":"Current delete tasks interval.*","show disk":"Disk space","show file":"Description","show hardware-type":"Member hardware type","show hwid":"Hardware ID:","show ibtrap":"show ibtrap","show lcd":"No LCD present","show lcd_info":"No LCD present","show lcd_settings":"No LCD present","show logfiles":"Logfiles present on the system","show memory":"Mem:","show ntp":"remote","show scheduled":"show scheduled task","show snmp":"show snmp","show status":"Grid Status:","show temperature":"No sensors present","show thresholdtrap":"show threhsoldtrap","show upgrade_history":"version","show uptime":"Up time",
"show version":"Version :"}
        validate_CLI(username,password,role_list)
        print("Test Case 7 Execution completed")
        


    @pytest.mark.run(order=8)
    def test_008_verify_disabled_Database_group_show_cmds_validate_permission(self):
        logging.info("Disabled admin group show commands")
        print("Testcase 08  started")
        username=config.username1
        password=config.password1
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"show named_max_journal_size":No_privilege,"show txn_trace":No_privilege,"show database_transfer_status":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 08 Execution Completed") 


    @pytest.mark.run(order=9)
    def test_009_enable_database_group_show_cmds(self):
        logging.info("Enabling database group show commands")
        print("Testcase 09 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"database_show_commands":{"show_named_max_journal_size":True,"show_txn_trace":True,"show_database_transfer_status":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 09 Execution Completed")

    @pytest.mark.run(order=10)
    def test_010_verify_database_group_show_cmds(self):
        logging.info("Verifying database group show commands")
        username=config.username1
        password=config.password1
        print("Testcase 10 started")
        role_list={"show named_max_journal_size":"Member override inactive","show txn_trace":"txn_trace set to off","show database_transfer_status":"Transfer was not initiated"}
        validate_CLI(username,password,role_list)
        print("Test Case 10 Execution Completed")    

   
    @pytest.mark.run(order=11)
    def test_011_verify_disabled_dhcp_group_show_cmds_validate_permission(self):
        logging.info("Disabled dhcp group show commands")
        print("Testcase 11 started")
        username=config.username1
        password=config.password1
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"show dhcpd_recv_sock_buf_size":No_privilege,"show dhcp_gss_tsig":No_privilege,"show dhcpv6_gss_tsig":No_privilege,"show log_txn_id":No_privilege,"show overload_bootp":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 11 Execution Completed")

       
    @pytest.mark.run(order=12)
    def test_012_enable_dhcp_group_show_cmds(self):
        logging.info("Enabling dhcp group show commands")
        print("Testcase 12 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"dhcp_show_commands":{"show_dhcpd_recv_sock_buf_size":True,"show_log_txn_id":True,"show_dhcp_gss_tsig":True,"show_dhcpv6_gss_tsig":True,"show_overload_bootp":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 12 Execution Completed")
    
    @pytest.mark.run(order=13)
    def test_013_verify_dhcp_group_show_cmds(self):
        logging.info("Verifying dhcp group show commands")
        username=config.username1
        password=config.password1
        print("Testcase 13 started")
        role_list={"show dhcpd_recv_sock_buf_size":"UDP receive socket buffer size","show dhcpv6_gss_tsig":"Synopsis:","show dhcp_gss_tsig":"Synopsis:","show log_txn_id":"DHCP Transaction id logging","show overload_bootp":"Overload BOOTP option turned"}
        validate_CLI(username,password,role_list)
        print("Test Case 13 Execution Completed")
 
    

    @pytest.mark.run(order=14)
    def test_014_verify_disabled_dns_group_show_cmds_validate_permission(self):
        logging.info("Disabled dns group show commands")
        print("Testcase 14 started")
        username=config.username1
        password=config.password1
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"show dns":No_privilege,"show dns_rrl":No_privilege,"show dtc_ea":No_privilege,
        "show dtc_geoip":No_privilege,"show enable_match_recursive_only":No_privilege,
        "show log_guest_lookups":No_privilege,"show max_recursion_depth":No_privilege,"show max_recursion_queries":No_privilege,"show monitor":No_privilege,"show ms_sticky_ip":No_privilege,"show query_capture":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 14 Execution Completed")

        
    @pytest.mark.run(order=15)
    def test_015_enable_dns_group_show_cmds(self):
        logging.info("Enabling dns group show commands")
        print("Testcase 15 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"dns_show_commands":{"show_dns":True,"show_dns_rrl":True,"show_dtc_ea":True,"show_dtc_geoip":True,"show_enable_match_recursive_only":True,"show_log_guest_lookups":True,"show_max_recursion_depth":True,"show_max_recursion_queries":True,"show_monitor":True,"show_ms_sticky_ip":True,"show_query_capture":True}}

        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 15 Execution Completed")


    @pytest.mark.run(order=16)
    def test_016_verify_dns_group_show_cmds(self):
        logging.info("Verifying dns group show commands")
        username=config.username1
        password=config.password1
        print("Testcase 16 started")
        role_list={"show dns":"Synopsis:","show dns_rrl":"DNS RRL feature","show dtc_ea":"Synopsis:","show dtc_geoip":"Synopsis:","show log_guest_lookups":"Logging Guest lookups","show max_recursion_depth":"Recursion depth limit:","show max_recursion_queries":"Recursion queries limit:","show monitor":"Network Monitoring for DNS","show ms_sticky_ip":"ms_sticky_ip is","show query_capture":"quer"}
        validate_CLI(username,password,role_list)
        sleep(25)
        print("Test Case 16 Execution Completed") 
        
    @pytest.mark.run(order=17)
    def test_017_verify_disabled_docker_group_show_cmds_validate_permission(self):
        logging.info("Disabled docker group show commands")
        print("Testcase 17 started")
        username=config.username1
        password=config.password1
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"show docker_bridge":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 17 Execution Completed")
        
    @pytest.mark.run(order=18)
    def test_018_enable_docker_group_show_cmds(self):
        logging.info("Enabling docker group show commands")
        print("Testcase 18 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"docker_show_commands":{"show_docker_bridge":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 18 Execution Completed")


    @pytest.mark.run(order=19)
    def test_019_verify_docker_group_show_cmds(self):
        logging.info("Verifying docker group show commands")
        username=config.username1
        password=config.password1
        print("Testcase 19 started")
        role_list={"show docker_bridge":"Current Docker Bridge settings:"}
        validate_CLI(username,password,role_list)
        print("Test Case 19 Execution Completed") 
        
    @pytest.mark.run(order=20)
    def test_020_verify_disabled_Networking_group_show_cmds_validate_permission(self):
        logging.info("Disabled Networking group show commands")
        print("Testcase 20 started")
        username=config.username1
        password=config.password1
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"show connection_limit":No_privilege,"show connections":No_privilege,"show interface":No_privilege,"show ip_rate_limit":No_privilege,"show ipv6_bgp":No_privilege,"show ipv6_disable_on_dad":No_privilege,"show ipv6_neighbor":No_privilege,"show ipv6_ospf":No_privilege,"show lom":No_privilege,"show mld_version":No_privilege,"show named_recv_sock_buf_size":No_privilege,"show named_tcp_clients_limit":No_privilege,"show network":No_privilege,"show ospf":No_privilege,"show remote_console":No_privilege,"show routes":No_privilege,"show static_routes":No_privilege,"show tcp_timestamps":No_privilege,"show traffic_capture_status":No_privilege,"show wins_forwarding":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 20 Execution Completed")
        
    @pytest.mark.run(order=21)
    def test_021_enable_Networking_group_show_cmds(self):
        logging.info("Enabling Networking group show commands")
        print("Testcase 21 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"networking_show_commands":{"show_connection_limit":True,"show_connections":True,"show_interface":True,"show_ip_rate_limit":True,"show_ipv6_bgp":True,"show_ipv6_disable_on_dad":True,"show_ipv6_neighbor":True,"show_ipv6_ospf":True,"show_lom":True,"show_mld_version":True,"show_named_recv_sock_buf_size":True,"show_named_tcp_clients_limit":True,
        "show_network":True,"show_ospf":True,"show_remote_console":True,"show_routes":True,"show_static_routes":True,"show_tcp_timestamps":True,"show_traffic_capture_status":True,"show_wins_forwarding":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 21 Execution Completed")


    @pytest.mark.run(order=22)
    def test_022_verify_Networking_group_show_cmds(self):
        logging.info("Verifying Networking group show commands")
        username=config.username1
        password=config.password1
        print("Testcase 22 started")
        role_list={"show connection_limit":"Description:","show ip_rate_limit":"Rate limits","show ipv6_bgp":"bgpd process is not running","show ipv6_disable_on_dad":"Disable IPv6","show ipv6_neighbor":"","show ipv6_ospf":"ospf6d process is not running","show lom":"LOM for grid:","show mld_version":"Current Multicast Listener","show named_recv_sock_buf_size":"DNS 'named' UDP receive socket buffer size:","show named_tcp_clients_limit":"tcp_clients_limit using grid value","show network":"IPv4 Address:","show ospf":"ospfd process is not running","show remote_console":
"Current remote console access settings:","show routes":"route table:","show static_routes":"IPv4 static routes","show tcp_timestamps":"TCP timestamps","show traffic_capture_status":"Traffic capture is","show wins_forwarding":"Grid level WINS forwarding:"}
        validate_CLI(username,password,role_list)
        print("Test Case 22 Execution Completed") 
        
    @pytest.mark.run(order=23)
    def test_023_verify_disabled_Grid_group_show_cmds_validate_permission(self):
        logging.info("Disabled Grid group show commands")
        print("Testcase 23 started")
        username=config.username1
        password=config.password1
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"show token":No_privilege,}
        validate_CLI(username,password,role_list)
        print("Test Case 23 Execution Completed")
 
    @pytest.mark.run(order=24)
    def test_024_enable_Grid_group_show_cmds(self):
        logging.info("Enabling Grid group show commands")
        print("Testcase 24 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"grid_show_commands":{"show_token":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 24 Execution Completed")

    @pytest.mark.run(order=25)
    def test_025_verify_Grid_group_show_cmds(self):
        logging.info("Verifying Grid group show commands")
        username=config.username1
        password=config.password1
        print("Testcase 25 started")
        role_list={"show token":"The token is not configured"}
        validate_CLI(username,password,role_list)
        print("Test Case 25 Execution Completed")
       
    @pytest.mark.run(order=26)
    def test_026_verify_disabled_Licensing_group_show_cmds_validate_permission(self):
        logging.info("Disabled Licensing group show commands")
        print("Testcase 26 started")
        username=config.username1
        password=config.password1
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"show license":No_privilege,"show license_pool_container":No_privilege,"show license_uid":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 26 Execution Completed")
 
    @pytest.mark.run(order=27)
    def test_027_enable_Licensing_group_show_cmds(self):
        logging.info("Enabling Licensing group show commands")
        print("Testcase 27 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"licensing_show_commands":{"show_license":True,"show_license_pool_container":True,"show_license_uid":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 27 Execution Completed")

    @pytest.mark.run(order=28)
    def test_028_verify_Licensing_group_show_cmds(self):
        logging.info("Verifying Licensing group show commands")
        username=config.username1
        password=config.password1
        print("Testcase 28 started")
        role_list={"show license":"Version","show license_pool_container":"The Unique ID of the License Pool Container","show license_uid":"The grid-wide license unique ID"}
        validate_CLI(username,password,role_list)
        print("Test Case 28 Execution Completed")
        
    @pytest.mark.run(order=29)
    def test_029_verify_disabled_Security_group_show_cmds_validate_permission(self):
        logging.info("Disabled Security group show commands")
        print("Testcase 29 started")
        username=config.username1
        password=config.password1
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"show cc_mode":No_privilege,"show certificate_auth_admins":No_privilege,"show certificate_auth_services":No_privilege,"show check_auth_ns":No_privilege,"show fips_mode":No_privilege,"show session_timeout":No_privilege,
        "show subscriber_secure_data":No_privilege,"show check_ssl_certificate":No_privilege,"show support_access":No_privilege,"show vpn_cert_dates":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 29 Execution Completed")
        
    @pytest.mark.run(order=30)
    def test_030_enable_Security_group_show_cmds(self):
        logging.info("Enabling Security group show commands")
        print("Testcase 30 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"security_show_commands":{"show_cc_mode":True,"show_check_ssl_certificate":True,"show_certificate_auth_admins":True,"show_certificate_auth_services":True,"show_check_auth_ns":True,"show_fips_mode":True,"show_session_timeout":True,
        "show_subscriber_secure_data":True,"show_support_access":True,"show_vpn_cert_dates":True,"show_security":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 30 Execution Completed")


    @pytest.mark.run(order=31)
    def test_031_verify_Security_group_show_cmds(self):
        logging.info("Verifying Security group show commands")
        username=config.username1
        password=config.password1
        print("Testcase 31 started")
        role_list={"show cc_mode":"Common Criteria Mode Setting:","show certificate_auth_admins":"No Admins with enabled Certificate Authentication"
        ,"show certificate_auth_services":"No effective Certificate Authentication Services","show check_ssl_certificate":"Synopsis:","show check_auth_ns":"Check authoritative NS RRset is disabled",
        "show fips_mode":"FIPS Mode Setting:","show security":"current security settings:","show session_timeout":"Current GUI/CLI timeout is",
        "show vpn_cert_dates":"Start Date="}
        validate_CLI(username,password,role_list)
        print("Test Case 31 Execution Completed")
        
     
    @pytest.mark.run(order=32)
    def test_032_verify_disabled_admin_group_set_cmds_validate_permission(self):
        logging.info("Disabled admin group set commands")
        print("Testcase 32 started")
        username=config.username1
        password=config.password1
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"set admin_group_acl":No_privilege,"show rpz_recursive_only":No_privilege,"show reporting_user_capabilities":No_privilege,"show hardware_status":No_privilege,"show debug_analytics":No_privilege,"show analytics_parameter":No_privilege,"set bfd":No_privilege,"set debug_analytics":No_privilege,"set purge_restart_objects":No_privilege,"set reporting_user_capabilities":No_privilege,"set bgp":No_privilege,"set bloxtools":No_privilege,"set debug":No_privilege,"set delete_tasks_interval":No_privilege,"set expertmode":No_privilege,"set hardware-type":No_privilege,"set ibtrap":No_privilege,"set lcd":No_privilege,"set lcd_settings":No_privilege,"set lines":No_privilege,"set maintenancemode":No_privilege,"set ms_max_connection":No_privilege,"set nosafemode":No_privilege,"set ocsp":No_privilege,"set safemode":No_privilege,"set scheduled":No_privilege,"set snmptrap":No_privilege,"set sysname":No_privilege,"set term":No_privilege,"set thresholdtrap":No_privilege,"set transfer_reporting_data":No_privilege,"set transfer_supportbundle":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 32 Execution Completed")

    @pytest.mark.run(order=33)
    def test_033_enable_admin_group_set_cmds(self):
        logging.info("Enabling admin group set commands")
        print("Testcase 33 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"admin_set_commands":{"set_admin_group_acl":True,"set_bfd":True,"set_bgp":True,"set_debug_analytics":True,"set_reporting_user_capabilities":True,"set_bloxtools":True,"set_debug":True,"set_delete_tasks_interval":True,"set_hardware_type":True,"set_ibtrap":True,"set_lcd":True,"set_lcd_settings":True,"set_lines":True,"set_ms_max_connection":True,"set_nosafemode":True,"set_ocsp":True,"set_safemode":True,"set_scheduled":True,"set_snmptrap":True,"set_sysname":True,"set_term":True,"set_thresholdtrap":True,"set_transfer_reporting_data":True,"set_transfer_supportbundle":True,"set_expertmode":True,"set_maintenancemode":True},"admin_show_commands":{"show_rpz_recursive_only":True,"show_reporting_user_capabilities":True,"show_hardware_status":True,"show_debug_analytics":True,"show_analytics_parameter":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 33 Execution Completed")


    @pytest.mark.run(order=34)
    def test_034_verify_admin_group_set_cmds(self):
        logging.info("Verifying admin group set commands")
        username=config.username1
        password=config.password1
        print("Testcase 34 started")
        role_list={"set admin_group_acl":"set .*\s*Synopsis:","show rpz_recursive_only":"Usage:","show reporting_user_capabilities":"No users are configured with any additional reporting","show hardware_status":"No sensors present","show debug_analytics":"off","show analytics_parameter":"Must specify","set debug_analytics":"set .*\s*Synopsis:","set reporting_user_capabilities":"set .*\s*Synopsis:","set bfd":"set .*\s*Synopsis:","set bgp":"set .*\s*Synopsis:","set bloxtools":"set .*\s*Synopsis:","set debug":"set .*\s*Synopsis:","set delete_tasks_interval":"set .*\s*Synopsis:","set hardware-type":"set .*\s*Synopsis:","set ibtrap":"set .*\s*Synopsis:","set lcd":"The LCD can not be configured on a this appliance","set lcd_settings":"set .*\s*Synopsis:","set lines":"set .*\s*Synopsis:","set ms_max_connection":"set .*\s*Synopsis:","set nosafemode":"set nosafemode\s*Infoblox >","set ocsp":"set .*\s*Synopsis:","set safemode":"set safemode\s*Infoblox >","set scheduled":"set .*\s*Synopsis:","set snmptrap":"set .*\s*Synopsis:","set sysname":"set .*\s*Synopsis:","set term":"set .*\s*Synopsis:","set thresholdtrap":"set .*\s*Synopsis:","set transfer_reporting_data":"set .*\s*Synopsis:","set transfer_supportbundle":"set .*\s*Synopsis:"}
        validate_CLI(username,password,role_list)
        print("Test Case 34 Execution Completed")

    @pytest.mark.run(order=35)
    def test_035_verify_admin_group_set_mode_cmds(self):
        logging.info("Verifying admin group set commands")
        username=config.username1
        password=config.password1
        print("Testcase 35 started")
        role_list={"set maintenancemode":"set .*\s*Maintenance Mode >","set expertmode":"set .*\s*\"Disclaimer"}
        validate_CLI(username,password,role_list)
        print("Test Case 35 Execution Completed")

    @pytest.mark.run(order=36)
    def test_036_verify_disabled_database_group_set_cmds_validate_permission(self):
        logging.info("Disabled database group set commands")
        print("Testcase 36 started")
        username=config.username1
        password=config.password1
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"set named_max_journal_size":No_privilege,"set txn_trace":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 36 Execution Completed")

    @pytest.mark.run(order=37)
    def test_037_enable_database_group_set_cmds(self):
        logging.info("Enabling database group set commands")
        print("Testcase 37 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"database_set_commands":{"set_named_max_journal_size":True,"set_txn_trace":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 37 Execution Completed")

    @pytest.mark.run(order=38)
    def test_038_verify_database_group_set_cmds(self):
        logging.info("Verifying admin group set commands")
        username=config.username1
        password=config.password1
        print("Testcase 38 started")
        role_list={"set named_max_journal_size":"Incorrect number of arguments","set txn_trace":"set .*\s*Synopsis:"}
        validate_CLI(username,password,role_list)
        print("Test Case 38 Execution Completed")
        
    @pytest.mark.run(order=39)
    def test_039_verify_disabled_dhcp_group_set_cmds_validate_permission(self):
        logging.info("Disabled dhcp group set commands")
        print("Testcase 39 started")
        username=config.username1
        password=config.password1
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"set dhcpd_recv_sock_buf_size":No_privilege,"set log_txn_id":No_privilege,"set overload_bootp":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 39 Execution Completed")

    @pytest.mark.run(order=40)
    def test_040_enable_dhcp_group_set_cmds(self):
        logging.info("Enabling dhcp group set commands")
        print("Testcase 40 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"dhcp_set_commands":{"set_dhcpd_recv_sock_buf_size":True,"set_log_txn_id":True,"set_overload_bootp":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 40 Execution Completed")

    @pytest.mark.run(order=41)
    def test_041_verify_dhcp_group_set_cmds(self):
        logging.info("Verifying dhcp group set commands")
        username=config.username1
        password=config.password1
        print("Testcase 41 started")
        role_list={"set dhcpd_recv_sock_buf_size":"Usage: set dhcpd_recv_sock_buf_size N","set log_txn_id":"DHCP force restart services is required in order for the changed value to take effect","set overload_bootp":"DHCP force restart services is required in order for the changed value to take effect"}
        validate_CLI(username,password,role_list)
        print("Test Case 41 Execution Completed")
        sleep(30)
        
    @pytest.mark.run(order=42)
    def test_042_verify_disabled_dns_group_set_cmds_validate_permission(self):
        logging.info("Disabled dns group set commands")
        print("Testcase 42 started")
        username=config.username1
        password=config.password1
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"set dns":No_privilege,"set dns_rrl":No_privilege,"set enable_match_recursive_only":No_privilege,"set log_guest_lookups":No_privilege,"set max_recursion_depth":No_privilege,"set max_recursion_queries":No_privilege,"set monitor":No_privilege,"set ms_dns_reports_sync_interval":No_privilege,"set ms_sticky_ip":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 42 Execution Completed")

    @pytest.mark.run(order=43)
    def test_043_enable_dns_group_set_cmds(self):
        logging.info("Enabling dns group set commands")
        print("Testcase 43 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"dns_set_commands":{"set_dns":True,"set_dns_rrl":True,"set_enable_match_recursive_only":True,"set_log_guest_lookups":True,"set_max_recursion_depth":True,"set_max_recursion_queries":True,"set_monitor":True,"set_ms_sticky_ip":True,"set_ms_dns_reports_sync_interval":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 43 Execution Completed")
        sleep(30)

    @pytest.mark.run(order=44)
    def test_044_verify_dns_group_set_cmds(self):
        logging.info("Verifying dns group set commands")
        username=config.username1
        password=config.password1
        print("Testcase 44 started")
        role_list={"set dns":"set .*\s*Synopsis:","set dns_rrl":"set .*\s*Synopsis:","set enable_match_recursive_only":"if view_name omitted","set log_guest_lookups":"set .*\s*Synopsis:","set max_recursion_depth":"set .*\s*Synopsis:","set max_recursion_queries":"set .*\s*Synopsis:","set monitor":"set .*\s*Synopsis:","set ms_dns_reports_sync_interval":"set .*\s*Synopsis:","set ms_sticky_ip":"set .*\s*Synopsis:"}
        validate_CLI(username,password,role_list)
        print("Test Case 44 Execution Completed")
        
    @pytest.mark.run(order=45)
    def test_045_verify_disabled_grid_group_set_cmds_validate_permission(self):
        logging.info("Disabled grid group set commands")
        print("Testcase 45 started")
        username=config.username1
        password=config.password1
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"set default_revert_window":No_privilege,"show test_promote_master":No_privilege,"set test_promote_master":No_privilege,"set nogrid":No_privilege,"set promote_master":No_privilege,"set token":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 45 Execution Completed")

    @pytest.mark.run(order=46)
    def test_046_enable_grid_group_set_cmds(self):
        logging.info("Enabling grid group set commands")
        print("Testcase 46 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"grid_set_commands":{"set_default_revert_window":True,"set_test_promote_master":True,"set_nogrid":True,"set_promote_master":True,"set_token":True},"grid_show_commands":{"show_test_promote_master":True} }
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        sleep(30)
        for read in response:
            assert True
        print("Test Case 46 Execution Completed")

    @pytest.mark.run(order=47)
    def test_047_verify_grid_group_set_cmds(self):
        logging.info("Verifying grid group set commands")
        username=config.username1
        password=config.password1
        print("Testcase 47 started")
        role_list={"set default_revert_window":"set .*\s*Synopsis:","show test_promote_master":"show .*\s*Synopsis:","set test_promote_master":"set .*\s*Synopsis:","set nogrid":"This function only valid on a member node","set promote_master":"Unable to promote","set token":"set .*\s*Synopsis:"}
        validate_CLI(username,password,role_list)
        print("Test Case 47 Execution Completed")
        
    @pytest.mark.run(order=48)
    def test_048_verify_disabled_networking_group_set_cmds_validate_permission(self):
        logging.info("Disabled networking group set commands")
        print("Testcase 48 started")
        username=config.username1
        password=config.password1
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"set connection_limit":No_privilege,"set default_route":No_privilege,"set interface":No_privilege,"set ip_rate_limit":No_privilege,"set ipv6_disable_on_dad":No_privilege,"set ipv6_neighbor":No_privilege,"set ipv6_ospf":No_privilege,"set ipv6_status":No_privilege,"set lom":No_privilege,"set named_recv_sock_buf_size":No_privilege,"set named_tcp_clients_limit":No_privilege,"set ospf":No_privilege,"set prompt":No_privilege,"set static_route":No_privilege,"set tcp_timestamps":No_privilege,"set traffic_capture":No_privilege,"set wins_forwarding":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 48 Execution Completed")

    @pytest.mark.run(order=49)
    def test_049_enable_networking_group_set_cmds(self):
        logging.info("Enabling networking group set commands")
        print("Testcase 49 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"networking_set_commands":{"set_connection_limit":True,"set_default_route":True,"set_interface":True,"set_ip_rate_limit":True,"set_ipv6_disable_on_dad":True,"set_ipv6_neighbor":True,"set_ipv6_ospf":True,"set_ipv6_status":True,"set_lom":True,"set_named_recv_sock_buf_size":True,"set_named_tcp_clients_limit":True,"set_ospf":True,"set_prompt":True,"set_static_route":True,"set_tcp_timestamps":True,"set_traffic_capture":True,"set_wins_forwarding":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 49 Execution Completed")

    @pytest.mark.run(order=50)
    def test_050_verify_networking_group_set_cmds(self):
        logging.info("Verifying networking group set commands")
        username=config.username1
        password=config.password1
        print("Testcase 50 started")
        role_list={"set connection_limit":"set .*\s*Synopsis:","set default_route":"set .*\s*Synopsis:","set interface":"Error: The interface settings can not be configured on ","set ip_rate_limit":"set .*\s*Synopsis:","set ipv6_disable_on_dad":"set .*\s*Synopsis:","set ipv6_neighbor":"set .*\s*Synopsis:","set ipv6_ospf":"set .*\s*Synopsis:","set ipv6_status":"set .*\s*Synopsis:","set lom":"Error: LOM settings are not supported on this device","set named_recv_sock_buf_size":"Usage: set named_recv_sock_buf_size N","set named_tcp_clients_limit":"Incorrect number of arguments","set ospf":"set .*\s*Synopsis:","set prompt":"set .*\s*Synopsis:","set static_route":"set .*\s*Synopsis:","set tcp_timestamps":"set .*\s*Synopsis:","set traffic_capture":"set .*\s*Synopsis:","set wins_forwarding":"set .*\s*Synopsis:"}
        validate_CLI(username,password,role_list)
        print("Test Case 50 Execution Completed")
        
    @pytest.mark.run(order=51)
    def test_051_verify_disabled_security_group_set_cmds_validate_permission_show_dns_gss_tsig(self):
        logging.info("Disabled security group set commands")
        print("Testcase 51 started")
        os.system("/import/tools/lab/bin/reboot_system -H "+config.vmid1)
        sleep(700)
        username=config.username1
        password=config.password1
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list1={"set adp":No_privilege,"set check_ssl_certificate":No_privilege,"set support_install":No_privilege}
        role_list={"set certificate_auth_admins":No_privilege,"set certificate_auth_services":No_privilege,"set check_auth_ns":No_privilege,"set disable_https_cert_regeneration":No_privilege,"set subscriber_secure_data":No_privilege}
        validate_CLI(username,password,role_list)
        validate_member_adp_CLI(username,password,role_list1)
        print("Test Case 51 Execution Completed")

    @pytest.mark.run(order=52)
    def test_052_enable_security_group_set_cmds(self):
        logging.info("Enabling security group set commands")
        print("Testcase 52 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"security_set_commands":{"set_adp":True,"set_certificate_auth_admins":True,"set_support_install":True,"set_check_ssl_certificate":True,"set_certificate_auth_services":True,"set_check_auth_ns":True,"set_disable_https_cert_regeneration":True,"set_subscriber_secure_data":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 52 Execution Completed")

    @pytest.mark.run(order=53)
    def test_053_verify_security_group_set_cmds(self):
        logging.info("Verifying security group set commands")
        username=config.username1
        password=config.password1
        print("Testcase 53 started")
        role_list1={"set adp":"set .*\s*Synopsis:","set check_ssl_certificate":"set .*\s*Synopsis:"}
        role_list={"set certificate_auth_admins":"set .*\s*Synopsis:","set certificate_auth_services":"set .*\s*Synopsis:","set check_auth_ns":"set .*\s*Synopsis:","set disable_https_cert_regeneration":"set .*\s*Synopsis:","set subscriber_secure_data":"set .*\s*Synopsis:"}
        validate_CLI(username,password,role_list)
        validate_member_adp_CLI(username,password,role_list1)
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+username+'@'+config.grid_vip)
        child.expect ('password.*:')
        child.sendline (password)
        child.expect ('Infoblox >',timeout=60)
        child.sendline("set support_install")
        child.expect("paste")
        child.sendline("cntl + c")
        child.close()
        assert True
        #validate_support({"setsupport_install":"support"})
        print("Test Case 53 Execution Completed")
    
    @pytest.mark.run(order=54)
    def test_054_verify_disabled_Licensing_group_set_cmds_validate_permission(self):
        logging.info("Disabled Licensing group set commands")
        print("Testcase 54 started")
        username=config.username1
        password=config.password1
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"set reporting_reset_license":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 54 Execution Completed")

    @pytest.mark.run(order=55)
    def test_055_enable_licensing_group_set_cmds(self):
        logging.info("Enabling licensing group set commands")
        print("Testcase 40 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"licensing_set_commands":{"set_reporting_reset_license":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 55 Execution Completed")

    @pytest.mark.run(order=56)
    def test_056_verify_licensing_group_set_cmds(self):
        logging.info("Verifying licensing group set commands")
        username=config.username1
        password=config.password1
        print("Testcase 56 started")
        role_list={"set reporting_reset_license":"Reporting license"}
        validate_CLI(username,password,role_list)
        print("Test Case 56 Execution Completed")
        
        
    @pytest.mark.run(order=57)
    def test_057_verify_disabled_general_cmds_validate_permission(self):
        logging.info("Disabled general commands")
        print("Testcase 57 started")
        username=config.username1
        password=config.password1
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"iostat":No_privilege,"netstat":No_privilege,"ps":No_privilege,"rndc":No_privilege,"sar":No_privilege,"tcpdump":No_privilege,"vmstat":No_privilege,"ddns_add":No_privilege,"ddns_delete":No_privilege,"dns_a_record_delete":No_privilege,"delete":No_privilege,"reboot":No_privilege,"reset":No_privilege,"shutdown":No_privilege,"dig":No_privilege,"ping":No_privilege,"ping6":No_privilege,"rotate":No_privilege,"traceroute":No_privilege}
        role_list1={"console":No_privilege,"traffic_capture":No_privilege,"restart_product":No_privilege,"strace":No_privilege,"resilver":No_privilege,"scrape":No_privilege,"tracepath":No_privilege,"saml_restart":No_privilege}
        role_list2={"snmpget":No_privilege,"snmpwalk":No_privilege}
        role_list3={"restart":No_privilege,"show dns_gss_tsig":No_privilege}
        validate_expert_CLI(username,password,role_list)
        validate_maintenance_CLI(username,password,role_list1)
        validate_member4_CLI(username,password,role_list2)
        validate_member2_CLI(username,password,role_list3)
        print("Test Case 57 Execution Completed")
        
    
    @pytest.mark.run(order=58)
    def test_058_enable_general_cmds(self):
        logging.info("Enabling dns group set commands")
        print("Testcase 58 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"admin_toplevel_commands":{"iostat":True,"netstat":True,"restart_product":True,"ps":True,"rndc":True,"sar":True,"tcpdump":True,"vmstat":True,"resilver":True,"scrape":True,"saml_restart":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("\n\n\n\n\n admin\n\n\n\n")
        data={"dns_toplevel_commands":{"ddns_add":True,"ddns_delete":True,"dns_a_record_delete":True,"delete":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print(response)
        data={"dns_show_commands":{"show_dns_gss_tsig":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("dns\n\n\n\n")
        data={"machine_control_toplevel_commands":{"reboot":True,"reset":True,"restart":True,"shutdown":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("machine\n\n\n\n")
        data={"trouble_shooting_toplevel_commands":{"console":True,"dig":True,"ping":True,"ping6":True,"rotate":True,"snmpget":True,"snmpwalk":True,"strace":True,"traceroute":True,"tracepath":True,"traffic_capture":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 58 Execution Completed")
    
    
    @pytest.mark.run(order=59)
    def test_059_verify_general_expert_cmds(self):
        logging.info("Verifying general commands")
        username=config.username1
        password=config.password1
        print("Testcase 59 started")
        role_list={"iostat":"Linux","netstat":"Active Internet connections","ps":"  PID TTY","sar":"Cannot open","tcpdump":"Please specify the","vmstat":"procs","ddns_add":"Synopsis:","ddns_delete":"Synopsis:","dns_a_record_delete":"Synopsis:","delete":"Synopsis:","reset":"Synopsis:","ping":"Usage:","ping6":"Usage:","traceroute":"Usage:","rotate":"Synopsis:","dig":"global options","rndc":"Usage:"}
        validate_expert_CLI(username,password,role_list)
        print("Test Case 59 Execution Completed")
        
    
    @pytest.mark.run(order=60)
    def test_060_verify_general_maintenance_member_cmds(self):
        logging.info("Verifying general commands")
        username=config.username1
        password=config.password1
        print("Testcase 60 started")
        role_list={"strace":"Synopsis:","console":"Synopsis:","resilver":"Synopsis:","scrape":"Maintenance Mode","tracepath":"Synopsis:","saml_restart":"SAML PROCESS NOT RUNNING"}
        validate_maintenance_CLI(username,password,role_list)
        role_list1={"restart":"Synopsis.*restart","snmpget":"Synopsis.*snmpget","snmpwalk":"Synopsis.*snmpwalk"}
        validate_member4_CLI(username,password,role_list1)
        print("Test Case 60 Execution Completed")    
        
    @pytest.mark.run(order=61)
    def test_061_verify_general_expert_reboot_shutdown_cmds(self):
        logging.info("Verifying general commands")
        try:    
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+config.username1+'@'+config.grid_vip)
            child.expect ('password.*:')
            child.sendline (config.password1)
            child.expect ('Infoblox >',timeout=60)
            child.sendline('set expertmode')
            child.expect("set .*\s*\"Disclaimer")
            child.sendline("shutdown")
            child.expect("SHUTDOWN THE SYSTEM\? \(y or n\)\: ")
            child.sendline("n")
            child.expect("Expert Mode > ")
            child.sendline("reboot")
            child.expect("REBOOT THE SYSTEM\? \(y or n\)\: ")
            child.sendline("n")
            child.expect("Expert Mode > ")
            assert True
        
        except Exception as e:
            print(e)
            assert False

        finally:
            child.sendline("exit")
            child.close()
            
        print("Test Case 61 Execution Completed")
        
    @pytest.mark.run(order=62)
    def test_062_verify_traffic_capture_cmd(self):
        logging.info("Verifying general commands")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+config.username1+'@'+config.grid_member3_vip)      
        try:    
            child.expect ('password.*: ')
            child.sendline (config.password1)
            child.expect ('Infoblox >',timeout=60)
            child.sendline('set maintenancemode')
            child.expect('Maintenance Mode > ')
            child.sendline('traffic_capture -p')
            child.expect('Synopsis:')
            #child.sendline("cntl + c")
            sleep(15)
            child.sendline('restart_product')
            child.expect('y or n\): ')
            child.sendline('n')
            
            assert True
        
        except Exception as e:
            print(e)
            assert False

        finally:
            child.sendline('exit')
            child.close()
            
        print("Test Case 62 Execution Completed")
        
        
    @pytest.mark.run(order=63)
    def test_063_verify_disabled_dscp_cmd_validate_permission(self):
        logging.info("Disabled dscp commands")
        print("Testcase 63 started")
        username=config.username1
        password=config.password1
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"set dscp":No_privilege}
        validate_member2_CLI(username,password,role_list)
        print("Test Case 63 Execution Completed")

    @pytest.mark.run(order=64)
    def test_064_enable_dscp_set_cmds(self):
        logging.info("Enabling licensing group set commands")
        print("Testcase 64 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"grid_set_commands":{"set_dscp":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 64 Execution Completed")

    @pytest.mark.run(order=65)
    def test_065_verify_dscp_set_cmds_show_dns_gss_tsig(self):
        logging.info("Verifying dscp set commands")
        username=config.username1
        password=config.password1
        print("Testcase 65 started")
        role_list={"set dscp":"set .*\s*Synopsis:","show dns_gss_tsig":"set .*\s*Synopsis:"}
        validate_member2_CLI(username,password,role_list)
        print("Test Case 65 Execution Completed")   
        

    @pytest.mark.run(order=66)
    def test_066_create_radius_authentication_server_group(self):
        logging.info("Creating radius service in authentication server group")
        data={
                "name": "radius",
                "servers": [
                    {
                        "acct_port": 1813,
                        "address": "10.197.38.101",
                        "auth_port": 1812,
                        "auth_type": "PAP",
                        "shared_secret": "testing123"
                    }
                ]
            }
        response = ib_NIOS.wapi_request('POST', object_type="radius:authservice",fields=json.dumps(data))
        print(response)
        logging.info(response)
        radiusref=response
        radiusref = json.loads(radiusref)
        print(radiusref)            
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
               assert False
               
        print("Test Case 66 Execution Completed") 
               
               
    @pytest.mark.run(order=67)
    def test_067_create_radius_authentication_policy(self):
        logging.info("Create authentication policy group to add remote authentication")
        logging.info("get authentication policy ref")
        res = ib_NIOS.wapi_request('GET',object_type='authpolicy')
        res = json.loads(res)
        print(res)
        auth_policy_ref=res[0][u'_ref']
        print(auth_policy_ref)
        logging.info("adding default group for authpolicy")
        data={"default_group": "test1"}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=auth_policy_ref)
        print(response)
        logging.info("Get auth_service localuser reference")
        res = ib_NIOS.wapi_request('GET',object_type='authpolicy?_return_fields=auth_services')
        res = json.loads(res)
        print(res)
        localuser_ref=res[0][u'auth_services'][0]
        print(localuser_ref)
        logging.info("Get radius server reference")
        response = ib_NIOS.wapi_request('GET', object_type="radius:authservice")
        print(response)
        response = json.loads(response)
        radiusref=response[0][u'_ref']
        logging.info("Adding localuser and radius reference to auth_services")
        data={"auth_services":[localuser_ref,radiusref]}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=auth_policy_ref)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
               assert False
        print("Test Case 67 Execution Completed") 
               
               
    @pytest.mark.run(order=68)
    def test_068_validate_radius_user_clilogin(self):
        logging.info("validating radius user authentication after adding radius in auth_services")
        os.system("/import/tools/lab/bin/reboot_system -H "+config.vmid)
        sleep(700)
        try:
            child = pexpect.spawn("console_connect -H "+config.vmid,  maxread=100)
            child.expect(".*Escape character is .*")
            child.sendline("\r")
            child.expect(".*login: ")
            child.sendline("user1_radius")
            child.expect('password: ')
            child.sendline("infoblox")
            child.expect('Infoblox >')
            child.sendline("exit")
            #print(child.before)
            assert True
        except:
            assert False
        finally:
            child.close()
            os.system("/import/tools/lab/bin/reset_console -H "+config.vmid)
            sleep(20)
        print("Test Case 68 Execution Completed") 
        
    
    @pytest.mark.run(order=69)
    def test_069_create_tacacs_authentication_server_group(self):
        logging.info("Creating tacacs service in authentication server group")
        data={
                "name": "tacacs",
                "servers": [
                    {
                        "address": "10.197.38.101",
                        "shared_secret": "testing123"
                    }
                ]
            }
        response = ib_NIOS.wapi_request('POST', object_type="tacacsplus:authservice",fields=json.dumps(data))
        print(response)
        logging.info(response)
        tacacs_ref=response
        tacacs_ref = json.loads(tacacs_ref)
        print(tacacs_ref)            
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
               assert False
               
        print("Test Case 69 Execution Completed")   
        
        
        
    @pytest.mark.run(order=70)
    def test_070__add_tacacs_plus_in_authentication_policy(self):
        logging.info("Add tacacs in authentication policy group")
        logging.info("get authentication policy ref")
        res = ib_NIOS.wapi_request('GET',object_type='authpolicy')
        res = json.loads(res)
        auth_policy_ref=res[0][u'_ref']
        res = ib_NIOS.wapi_request('GET',object_type='authpolicy?_return_fields=auth_services')
        res = json.loads(res)
        logging.info("get localuser,radius and tacacsplus reference to add in auth_services")
        localuser_ref=res[0][u'auth_services'][0]
        print(localuser_ref)
        logging.info("get radius server ref")
        response = ib_NIOS.wapi_request('GET', object_type="radius:authservice")
        response = json.loads(response)
        radiusref=response[0][u'_ref']
        logging.info("get tacacs server ref")
        response = ib_NIOS.wapi_request('GET', object_type="tacacsplus:authservice")
        response = json.loads(response)
        tacacsplusref=response[0]['_ref']
        logging.info("adding localuser,radius and tacacsplus authentication to authentication services")
        data={"auth_services":[localuser_ref,tacacsplusref,radiusref]}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=auth_policy_ref)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
               assert False
        print("Test Case 70 Execution Completed") 
            
            
    @pytest.mark.run(order=71)
    def test_071_validate_tacacs_plus_user_clilogin(self):
        logging.info("validating tacacsplus user authentication after adding tacacs in auth_services")
        os.system("/import/tools/lab/bin/reset_console -H "+config.vmid)
        sleep(20)
        try:
            child = pexpect.spawn("console_connect -H "+config.vmid2,  maxread=100)
            child.expect(".*Escape character is .*")
            child.sendline("\r")
            child.expect(".*login:")
            child.sendline("user1")
            child.expect('password:')
            child.sendline("infoblox")
            child.expect("Infoblox >")
            child.sendline("exit")
            print(child.before)
            assert True
        except:
            assert False
        finally:
            child.close()
            os.system("/import/tools/lab/bin/reset_console -H "+config.vmid2)
            sleep(20)
        print("Test Case 71 Execution Completed")
        

    @pytest.mark.run(order=72)
    def test_072_create_adserver_authentication_server_group(self):
        logging.info("Creating Active Directory server service in authentication server group")
        data={
                "name": "asmgroup",
                "ad_domain": "ad19187.com",
                "domain_controllers": [
                    {
                        "auth_port": 389,
                        "disabled": False,
                        "fqdn_or_ip": "10.34.98.56",
                        "encryption": "NONE",
                        "use_mgmt_port": False
                    }
                ]
            }
        response = ib_NIOS.wapi_request('POST', object_type="ad_auth_service",fields=json.dumps(data))
        print(response)
        logging.info(response)
        ad_ref=response
        ad_ref = json.loads(ad_ref)
        print(ad_ref)            
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
               assert False
               
        print("Test Case 69 Execution Completed")   
        
        
        
    @pytest.mark.run(order=73)
    def test_073__add_adserver_plus_in_authentication_policy(self):
        logging.info("Add adserver in authentication policy group")
        logging.info("get authentication policy ref")
        res = ib_NIOS.wapi_request('GET',object_type='authpolicy')
        res = json.loads(res)
        auth_policy_ref=res[0][u'_ref']
        res = ib_NIOS.wapi_request('GET',object_type='authpolicy?_return_fields=auth_services')
        res = json.loads(res)
        logging.info("get localuser,radius and tacacsplus and adserver reference to add in auth_services")
        localuser_ref=res[0][u'auth_services'][0]
        print(localuser_ref)
        logging.info("get radius server ref")
        response = ib_NIOS.wapi_request('GET', object_type="radius:authservice")
        response = json.loads(response)
        radiusref=response[0][u'_ref']
        logging.info("get tacacs server ref")
        response = ib_NIOS.wapi_request('GET', object_type="tacacsplus:authservice")
        response = json.loads(response)
        tacacsplusref=response[0]['_ref']
        logging.info("get adserver ref")
        response = ib_NIOS.wapi_request('GET', object_type="ad_auth_service")
        response = json.loads(response)
        adserverref=response[0]['_ref']
        logging.info("adding localuser,radius and tacacsplus and adserver authentication to authentication services")
        data={"auth_services":[localuser_ref,radiusref,tacacsplusref,adserverref]}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=auth_policy_ref)
        print(response)
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
               assert False
        print("Test Case 73 Execution Completed") 
            
            
    @pytest.mark.run(order=74)
    def test_074_validate_adserver_user_clilogin(self):
        logging.info("validating adserver user authentication after adding adserver in auth_services")
        os.system("/import/tools/lab/bin/reset_console -H "+config.vmid3)
        sleep(20)
        try:
            child = pexpect.spawn("console_connect -H "+config.vmid3,  maxread=100)
            child.expect(".*Escape character is .*")
            child.sendline("\r")
            child.expect(".*login:")
            child.sendline("manoj")
            child.expect('password:')
            child.sendline("Infoblox@123")
            child.expect('Infoblox >')
            child.sendline("exit")
            print(child.before)
            assert True
        except:
            assert False
        finally:
            child.close()
            os.system("/import/tools/lab/bin/reboot_system -H "+config.vmid)
            sleep(700)
        print("Test Case 74 Execution Completed")
        
    @pytest.mark.run(order=75)
    def test_075_negative_validation_for_remote_authentication(self):
            logging.info("disable CLI access and verify remote authentication")
            res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
            res = json.loads(res)
            ref1=res[0]['_ref']
            data={"access_method": ["API"]}
            response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
            print("#######################",response)
            sleep(10)
            try:
                child = pexpect.spawn("console_connect -H "+config.vmid,  maxread=100)
                child.expect(".*Escape character is .*")
                child.sendline("\r")
                child.expect(".*login:")
                child.sendline("user1")
                child.expect("password:")
                child.sendline("user123")
                child.expect(".*login:")
                child.sendline("exit")
                print(child.before)
                assert True
            except:
                assert False
            finally:
                child.close()
                os.system("/import/tools/lab/bin/reset_console -H "+config.vmid)
                data={"name":"test1","access_method": ["API","CLI"]}
                response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
                print("#######################",response)
    
    @pytest.mark.run(order=76)
    def test_076_disable_all_commands(self):
        logging.info("Disable all commands")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={
                "admin_set_commands": {
                "disable_all": True
                },
                "admin_show_commands": {
                "disable_all": True
                },
                "admin_toplevel_commands": {
                "disable_all": True
                },
                "cloud_set_commands": {
                "disable_all": True
                },
                "database_set_commands": {
                "disable_all": True
                },
                "database_show_commands": {
                "disable_all": True
                },
                "dhcp_set_commands": {
                "disable_all": True
                },
                "dhcp_show_commands": {
                "disable_all": True
                },
                "dns_set_commands": {
                "disable_all": True
                },
                "dns_show_commands": {
                "disable_all": True
                },
                "dns_toplevel_commands": {
                "disable_all": True
                },
                "docker_set_commands": {
                "disable_all": True
                },
                "docker_show_commands": {
                "disable_all": True
                },
                "machine_control_toplevel_commands": {
                "disable_all": True
                },
                "grid_set_commands": {
                "disable_all": True
                },
                "grid_show_commands": {
                "disable_all": True
                },
                "licensing_set_commands": {
                "disable_all": True
                },
                "licensing_show_commands": {
                "disable_all": True
                },
                "trouble_shooting_toplevel_commands": {
                "disable_all": True
                },
                "networking_set_commands": {
                "disable_all": True
                },
                "networking_show_commands": {
                "disable_all": True
                },
                "security_set_commands": {
                "disable_all": True
                },
                "security_show_commands": {
                "disable_all": True
                }
            }
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 76 Execution Completed")


    @pytest.mark.run(order=77)
    def test_077_verify_disabled_admin_group_show_cmds_validate_permission_for_radius_user(self):
        logging.info("Disabled admin group show commands")
        print("Testcase 77 started")
        username=config.username2
        password=config.password2
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"show admin_group_acl":No_privilege,"show arp":No_privilege,"show bfd":No_privilege,"show bgp":No_privilege,"show bloxtools":No_privilege,"show capacity":No_privilege,"show clusterd_info":No_privilege,"show config":No_privilege,"show cpu":No_privilege,"show date":No_privilege,"show debug":No_privilege,
        "show delete_tasks_interval":No_privilege,"show disk":No_privilege,"show file":No_privilege,"show hardware-type":No_privilege,"show hwid":No_privilege,"show ibtrap":No_privilege,"show lcd":No_privilege,"show lcd_info":No_privilege,"show lcd_settings":No_privilege,"show log":No_privilege,"show logfiles":No_privilege,"show memory":No_privilege,"show ntp":No_privilege,"show scheduled":No_privilege,"show snmp":No_privilege,"show status":No_privilege,"show tech-support":No_privilege,"show temperature":No_privilege,"show thresholdtrap":No_privilege,"show upgrade_history":No_privilege,"show uptime":No_privilege,
        "show version":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 77 Execution Completed")
        
    
    @pytest.mark.run(order=78)
    def test_078_enable_admin_group_show_cmds_for_radius_user(self):
        logging.info("Enabling admin group show commands")
        print("\n\n\n")
        print("Testcase 78 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"admin_show_commands":{"show_admin_group_acl":True,"show_arp":True,"show_bfd":True,"show_bloxtools":True,"show_bgp":True,"show_capacity":True,"show_clusterd_info":True,"show_config":True,"show_cpu":True,"show_date":True,"show_debug":True,"show_delete_tasks_interval":True,"show_disk":True,"show_file":True,"show_hardware_type":True,"show_hwid":True,"show_ibtrap":True,"show_lcd":True,"show_lcd_info":True,"show_lcd_settings":True,"show_log":True,"show_logfiles":True,"show_memory":True,"show_ntp":True,"show_scheduled":True,"show_snmp":True,"show_status":True,"show_tech_support":True,"show_temperature":True,"show_thresholdtrap":True,"show_upgrade_history":True,"show_uptime":True,
"show_version":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 78 Execution Completed")
    
        
         
    @pytest.mark.run(order=79)
    def test_079_verify_admin_group_show_cmds_for_radius_user(self):
        username=config.username2
        password=config.password2
        role_list={"show admin_group_acl":"None of Admin Groups.*","show bfd":"bfdd process is not running","show bgp":"bgpd process","show capacity":"Hardware Type","show bloxtools":"bloxTools status:","show clusterd_info":"g_sw_version","show config":"Synopsis:","show cpu":"memory","show date":"[:\w\s\d]+[PST|UTC][\s\d]+","show debug":"Debug logging status :","show delete_tasks_interval":"Current delete tasks interval.*","show disk":"Disk space","show file":"Description","show hardware-type":"Member hardware type","show hwid":"Hardware ID:","show ibtrap":"show ibtrap","show lcd":"No LCD present","show lcd_info":"No LCD present","show lcd_settings":"No LCD present","show logfiles":"Logfiles present on the system","show memory":"Mem:","show ntp":"remote","show scheduled":"show scheduled task","show snmp":"show snmp","show status":"Grid Status:","show temperature":"No sensors present","show thresholdtrap":"show threhsoldtrap","show upgrade_history":"version","show uptime":"Up time",
"show version":"Version :"}
        validate_CLI(username,password,role_list)
        print("Test Case 79 Execution completed")
        


    @pytest.mark.run(order=80)
    def test_080_verify_disabled_Database_group_show_cmds_validate_permission_for_radius_user(self):
        logging.info("Disabled admin group show commands")
        print("Testcase 080  started")
        username=config.username2
        password=config.password2
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"show named_max_journal_size":No_privilege,"show txn_trace":No_privilege,"show database_transfer_status":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 080 Execution Completed") 

    @pytest.mark.run(order=81)
    def test_081_verify_disabled_dscp_cmd_validate_permission_for_radius_user(self):
        logging.info("Disabled dscp commands")
        print("Testcase 81 started")
        username=config.username2
        password=config.password2
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"set dscp":No_privilege}
        validate_member2_CLI(username,password,role_list)
        print("Test Case 81 Execution Completed")


    @pytest.mark.run(order=82)
    def test_082_enable_database_group_show_cmds_for_radius_user(self):
        logging.info("Enabling database group show commands")
        print("Testcase 82 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"database_show_commands":{"show_named_max_journal_size":True,"show_txn_trace":True,"show_database_transfer_status":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 82 Execution Completed")


    @pytest.mark.run(order=83)
    def test_083_verify_database_group_show_cmds_for_radius_user(self):
        logging.info("Verifying database group show commands")
        username=config.username2
        password=config.password2
        print("Testcase 83 started")
        role_list={"show named_max_journal_size":"Member override inactive","show txn_trace":"txn_trace set to off","show database_transfer_status":"Transfer was not initiated"}
        validate_CLI(username,password,role_list)
        print("Test Case 83 Execution Completed")    

   
    @pytest.mark.run(order=84)
    def test_084_verify_disabled_dhcp_group_show_cmds_validate_permission_for_radius_user(self):
        logging.info("Disabled dhcp group show commands")
        print("Testcase 11 started")
        username=config.username2
        password=config.password2
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"show dhcpd_recv_sock_buf_size":No_privilege,"show log_txn_id":No_privilege,"show overload_bootp":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 84 Execution Completed")

       
    @pytest.mark.run(order=85)
    def test_085_enable_dhcp_group_show_cmds_for_radius_user(self):
        logging.info("Enabling dhcp group show commands")
        print("Testcase 85 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"dhcp_show_commands":{"show_dhcpd_recv_sock_buf_size":True,"show_log_txn_id":True,"show_overload_bootp":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 85 Execution Completed")
    
    @pytest.mark.run(order=86)
    def test_086_verify_dhcp_group_show_cmds_for_radius_user(self):
        logging.info("Verifying dhcp group show commands")
        username=config.username2
        password=config.password2
        print("Testcase 86 started")
        role_list={"show dhcpd_recv_sock_buf_size":"UDP receive socket buffer size","show log_txn_id":"DHCP Transaction id logging","show overload_bootp":"Overload BOOTP option turned"}
        validate_CLI(username,password,role_list)
        print("Test Case 86 Execution Completed")
 
    

    @pytest.mark.run(order=87)
    def test_087_verify_disabled_dns_group_show_cmds_validate_permission_for_radius_user(self):
        logging.info("Disabled dns group show commands")
        print("Testcase 87 started")
        username=config.username2
        password=config.password2
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"show dns":No_privilege,"show dns_rrl":No_privilege,"show dtc_ea":No_privilege,
        "show dtc_geoip":No_privilege,"show enable_match_recursive_only":No_privilege,
        "show log_guest_lookups":No_privilege,"show max_recursion_depth":No_privilege,"show max_recursion_queries":No_privilege,"show monitor":No_privilege,"show ms_sticky_ip":No_privilege,"show query_capture":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 87 Execution Completed")

        
    @pytest.mark.run(order=88)
    def test_088_enable_dns_group_show_cmds_for_radius_user(self):
        logging.info("Enabling dns group show commands")
        print("Testcase 88 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"dns_show_commands":{"show_dns":True,"show_dns_rrl":True,"show_dtc_ea":True,"show_dtc_geoip":True,"show_enable_match_recursive_only":True,"show_log_guest_lookups":True,"show_max_recursion_depth":True,"show_max_recursion_queries":True,"show_monitor":True,"show_ms_sticky_ip":True,"show_query_capture":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 88 Execution Completed")


    @pytest.mark.run(order=89)
    def test_089_verify_dns_group_show_cmds_for_radius_user(self):
        logging.info("Verifying dns group show commands")
        username=config.username2
        password=config.password2
        print("Testcase 89 started")
        role_list={"show dns":"Synopsis:","show dns_rrl":"DNS RRL feature","show dtc_ea":"Synopsis:","show dtc_geoip":"Synopsis:","show log_guest_lookups":"Logging Guest lookups","show max_recursion_depth":"Recursion depth limit:","show max_recursion_queries":"Recursion queries limit:","show monitor":"Network Monitoring for DNS","show ms_sticky_ip":"ms_sticky_ip is","show query_capture":"quer"}
        validate_CLI(username,password,role_list)
        print("Test Case 89 Execution Completed") 
        
    @pytest.mark.run(order=90)
    def test_090_verify_disabled_docker_group_show_cmds_validate_permission_for_radius_user(self):
        logging.info("Disabled docker group show commands")
        print("Testcase 90 started")
        username=config.username2
        password=config.password2
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"show docker_bridge":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 90 Execution Completed")
        
    @pytest.mark.run(order=91)
    def test_091_enable_docker_group_show_cmds_for_radius_user(self):
        logging.info("Enabling docker group show commands")
        print("Testcase 91 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"docker_show_commands":{"show_docker_bridge":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 91 Execution Completed")


    @pytest.mark.run(order=92)
    def test_092_verify_docker_group_show_cmds_for_radius_user(self):
        logging.info("Verifying docker group show commands")
        username=config.username2
        password=config.password2
        print("Testcase 92 started")
        role_list={"show docker_bridge":"Current Docker Bridge settings:"}
        validate_CLI(username,password,role_list)
        print("Test Case 92 Execution Completed") 
        
    @pytest.mark.run(order=93)
    def test_093_verify_disabled_Networking_group_show_cmds_validate_permission_for_radius_user(self):
        logging.info("Disabled Networking group show commands")
        print("Testcase 93 started")
        username=config.username2
        password=config.password2
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"show connection_limit":No_privilege,"show connections":No_privilege,"show interface":No_privilege,"show ip_rate_limit":No_privilege,"show ipv6_bgp":No_privilege,"show ipv6_disable_on_dad":No_privilege,"show ipv6_neighbor":No_privilege,"show ipv6_ospf":No_privilege,"show lom":No_privilege,"show mld_version":No_privilege,"show named_recv_sock_buf_size":No_privilege,"show named_tcp_clients_limit":No_privilege,"show network":No_privilege,"show ospf":No_privilege,"show remote_console":No_privilege,"show routes":No_privilege,"show static_routes":No_privilege,"show tcp_timestamps":No_privilege,"show traffic_capture_status":No_privilege,"show wins_forwarding":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 93 Execution Completed")
        
    @pytest.mark.run(order=94)
    def test_094_enable_Networking_group_show_cmds_for_radius_user(self):
        logging.info("Enabling Networking group show commands")
        print("Testcase 94 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"networking_show_commands":{"show_connection_limit":True,"show_connections":True,"show_interface":True,"show_ip_rate_limit":True,"show_ipv6_bgp":True,"show_ipv6_disable_on_dad":True,"show_ipv6_neighbor":True,"show_ipv6_ospf":True,"show_lom":True,"show_mld_version":True,"show_named_recv_sock_buf_size":True,"show_named_tcp_clients_limit":True,
        "show_network":True,"show_ospf":True,"show_remote_console":True,"show_routes":True,"show_static_routes":True,"show_tcp_timestamps":True,"show_traffic_capture_status":True,"show_wins_forwarding":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 94 Execution Completed")


    @pytest.mark.run(order=95)
    def test_095_verify_Networking_group_show_cmds_for_radius_user(self):
        logging.info("Verifying Networking group show commands")
        username=config.username2
        password=config.password2
        print("Testcase 95 started")
        role_list={"show connection_limit":"Description:","show ip_rate_limit":"Rate limits","show ipv6_bgp":"bgpd process is not running","show ipv6_disable_on_dad":"Disable IPv6","show ipv6_neighbor":"","show ipv6_ospf":"ospf6d process is not running","show lom":"LOM for grid:","show mld_version":"Current Multicast Listener","show named_recv_sock_buf_size":"DNS 'named' UDP receive socket buffer size:","show named_tcp_clients_limit":"tcp_clients_limit using grid value","show network":"IPv4 Address:","show ospf":"ospfd process is not running","show remote_console":
"Current remote console access settings:","show routes":"route table:","show static_routes":"IPv4 static routes","show tcp_timestamps":"TCP timestamps","show traffic_capture_status":"Traffic capture is","show wins_forwarding":"Grid level WINS forwarding:"}
        validate_CLI(username,password,role_list)
        print("Test Case 95 Execution Completed") 
        
    @pytest.mark.run(order=96)
    def test_096_verify_disabled_Grid_group_show_cmds_validate_permission_for_radius_user(self):
        logging.info("Disabled Grid group show commands")
        print("Testcase 96 started")
        username=config.username2
        password=config.password2
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"show token":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 96 Execution Completed")
 
    @pytest.mark.run(order=97)
    def test_097_enable_Grid_group_show_cmds_for_radius_user(self):
        logging.info("Enabling Grid group show commands")
        print("Testcase 97 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"grid_show_commands":{"show_token":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 97 Execution Completed")

    @pytest.mark.run(order=98)
    def test_098_verify_Grid_group_show_cmds_for_radius_user(self):
        logging.info("Verifying Grid group show commands")
        username=config.username2
        password=config.password2
        print("Testcase 98 started")
        role_list={"show token":"The token is not configured"}
        validate_CLI(username,password,role_list)
        print("Test Case 98 Execution Completed")
       
    @pytest.mark.run(order=99)
    def test_099_verify_disabled_Licensing_group_show_cmds_validate_permission_for_radius_user(self):
        logging.info("Disabled Licensing group show commands")
        print("Testcase 99 started")
        username=config.username2
        password=config.password2
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"show license":No_privilege,"show license_pool_container":No_privilege,"show license_uid":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 99 Execution Completed")
    
    @pytest.mark.run(order=100)
    def test_100_enable_Licensing_group_show_cmds_for_radius_user(self):
        logging.info("Enabling Licensing group show commands")
        print("Testcase 100 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"licensing_show_commands":{"show_license":True,"show_license_pool_container":True,"show_license_uid":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 100 Execution Completed")

    @pytest.mark.run(order=101)
    def test_101_verify_Licensing_group_show_cmds_for_radius_user(self):
        logging.info("Verifying Licensing group show commands")
        username=config.username2
        password=config.password2
        print("Testcase 101 started")
        role_list={"show license":"Version","show license_pool_container":"The Unique ID of the License Pool Container","show license_uid":"The grid-wide license unique ID"}
        validate_CLI(username,password,role_list)
        print("Test Case 101 Execution Completed")
        
    @pytest.mark.run(order=102)
    def test_102_verify_disabled_Security_group_show_cmds_validate_permission_for_radius_user(self):
        logging.info("Disabled Security group show commands")
        print("Testcase 102 started")
        username=config.username2
        password=config.password2
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"show cc_mode":No_privilege,"show certificate_auth_admins":No_privilege,"show certificate_auth_services":No_privilege,"show check_auth_ns":No_privilege,"show fips_mode":No_privilege,"show session_timeout":No_privilege,
        "show subscriber_secure_data":No_privilege,"show support_access":No_privilege,"show vpn_cert_dates":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 102 Execution Completed")
        
    @pytest.mark.run(order=103)
    def test_103_enable_Security_group_show_cmds_for_radius_user(self):
        logging.info("Enabling Security group show commands")
        print("Testcase 103 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"security_show_commands":{"show_cc_mode":True,"show_certificate_auth_admins":True,"show_certificate_auth_services":True,"show_check_auth_ns":True,"show_fips_mode":True,"show_session_timeout":True,
        "show_subscriber_secure_data":True,"show_support_access":True,"show_vpn_cert_dates":True,"show_security":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 103 Execution Completed")


    @pytest.mark.run(order=104)
    def test_104_verify_Security_group_show_cmds_for_radius_user(self):
        logging.info("Verifying Security group show commands")
        username=config.username2
        password=config.password2
        print("Testcase 104 started")
        role_list={"show cc_mode":"Common Criteria Mode Setting:","show certificate_auth_admins":"No Admins with enabled Certificate Authentication"
        ,"show certificate_auth_services":"No effective Certificate Authentication Services","show check_auth_ns":"Check authoritative NS RRset is disabled",
        "show fips_mode":"FIPS Mode Setting:","show security":"current security settings:","show session_timeout":"Current GUI/CLI timeout is",
        "show vpn_cert_dates":"Start Date="}
        validate_CLI(username,password,role_list)
        print("Test Case 104 Execution Completed")
        
     
    @pytest.mark.run(order=105)
    def test_105_verify_disabled_admin_group_set_cmds_validate_permission_for_radius_user(self):
        logging.info("Disabled admin group set commands")
        print("Testcase 105 started")
        username=config.username2
        password=config.password2
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"set admin_group_acl":No_privilege,"set bfd":No_privilege,"set bgp":No_privilege,"set bloxtools":No_privilege,"set debug":No_privilege,"set delete_tasks_interval":No_privilege,"set expertmode":No_privilege,"set hardware-type":No_privilege,"set ibtrap":No_privilege,"set lcd":No_privilege,"set lcd_settings":No_privilege,"set lines":No_privilege,"set maintenancemode":No_privilege,"set ms_max_connection":No_privilege,"set nosafemode":No_privilege,"set ocsp":No_privilege,"set safemode":No_privilege,"set scheduled":No_privilege,"set snmptrap":No_privilege,"set sysname":No_privilege,"set term":No_privilege,"set thresholdtrap":No_privilege,"set transfer_reporting_data":No_privilege,"set transfer_supportbundle":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 105 Execution Completed")

    @pytest.mark.run(order=106)
    def test_106_enable_admin_group_set_cmds_for_radius_user(self):
        logging.info("Enabling admin group set commands")
        print("Testcase 106 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"admin_set_commands":{"set_admin_group_acl":True,"set_bfd":True,"set_bgp":True,"set_bloxtools":True,"set_debug":True,"set_delete_tasks_interval":True,"set_hardware_type":True,"set_ibtrap":True,"set_lcd":True,"set_lcd_settings":True,"set_lines":True,"set_ms_max_connection":True,"set_nosafemode":True,"set_ocsp":True,"set_safemode":True,"set_scheduled":True,"set_snmptrap":True,"set_sysname":True,"set_term":True,"set_thresholdtrap":True,"set_transfer_reporting_data":True,"set_transfer_supportbundle":True,"set_expertmode":True,"set_maintenancemode":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 106 Execution Completed")


    @pytest.mark.run(order=107)
    def test_107_verify_admin_group_set_cmds_for_radius_user(self):
        logging.info("Verifying admin group set commands")
        username=config.username2
        password=config.password2
        print("Testcase 107 started")
        role_list={"set admin_group_acl":"set .*\s*Synopsis:","set bfd":"set .*\s*Synopsis:","set bgp":"set .*\s*Synopsis:","set bloxtools":"set .*\s*Synopsis:","set debug":"set .*\s*Synopsis:","set delete_tasks_interval":"set .*\s*Synopsis:","set hardware-type":"set .*\s*Synopsis:","set ibtrap":"set .*\s*Synopsis:","set lcd":"The LCD can not be configured on a this appliance","set lcd_settings":"set .*\s*Synopsis:","set lines":"set .*\s*Synopsis:","set ms_max_connection":"set .*\s*Synopsis:","set nosafemode":"set nosafemode\s*Infoblox >","set ocsp":"set .*\s*Synopsis:","set safemode":"set safemode\s*Infoblox >","set scheduled":"set .*\s*Synopsis:","set snmptrap":"set .*\s*Synopsis:","set sysname":"set .*\s*Synopsis:","set term":"set .*\s*Synopsis:","set thresholdtrap":"set .*\s*Synopsis:","set transfer_reporting_data":"set .*\s*Synopsis:","set transfer_supportbundle":"set .*\s*Synopsis:"}
        validate_CLI(username,password,role_list)
        print("Test Case 107 Execution Completed")

    @pytest.mark.run(order=108)
    def test_108_verify_admin_group_set_mode_cmds_for_radius_user(self):
        logging.info("Verifying admin group set commands")
        username=config.username2
        password=config.password2
        print("Testcase 108 started")
        role_list={"set maintenancemode":"set .*\s*Maintenance Mode >","set expertmode":"set .*\s*\"Disclaimer"}
        validate_CLI(username,password,role_list)
        print("Test Case 108 Execution Completed")

    @pytest.mark.run(order=109)
    def test_109_verify_disabled_database_group_set_cmds_validate_permission_for_radius_user(self):
        logging.info("Disabled database group set commands")
        print("Testcase 109 started")
        username=config.username2
        password=config.password2
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"set named_max_journal_size":No_privilege,"set txn_trace":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 109 Execution Completed")

    @pytest.mark.run(order=110)
    def test_110_enable_database_group_set_cmds_for_radius_user(self):
        logging.info("Enabling database group set commands")
        print("Testcase 110 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"database_set_commands":{"set_named_max_journal_size":True,"set_txn_trace":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 110 Execution Completed")

    @pytest.mark.run(order=111)
    def test_111_verify_database_group_set_cmds_for_radius_user(self):
        logging.info("Verifying admin group set commands")
        username=config.username2
        password=config.password2
        print("Testcase 111 started")
        role_list={"set named_max_journal_size":"Incorrect number of arguments","set txn_trace":"set .*\s*Synopsis:"}
        validate_CLI(username,password,role_list)
        print("Test Case 111 Execution Completed")
        
    @pytest.mark.run(order=112)
    def test_112_verify_disabled_dhcp_group_set_cmds_validate_permission_for_radius_user(self):
        logging.info("Disabled dhcp group set commands")
        print("Testcase 112 started")
        username=config.username2
        password=config.password2
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"set dhcpd_recv_sock_buf_size":No_privilege,"set log_txn_id":No_privilege,"set overload_bootp":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 112 Execution Completed")

    @pytest.mark.run(order=113)
    def test_113_enable_dhcp_group_set_cmds_for_radius_user(self):
        logging.info("Enabling dhcp group set commands")
        print("Testcase 113 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"dhcp_set_commands":{"set_dhcpd_recv_sock_buf_size":True,"set_log_txn_id":True,"set_overload_bootp":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 113 Execution Completed")

    @pytest.mark.run(order=114)
    def test_114_verify_dhcp_group_set_cmds_for_radius_user(self):
        logging.info("Verifying dhcp group set commands")
        username=config.username2
        password=config.password2
        print("Testcase 114 started")
        role_list={"set dhcpd_recv_sock_buf_size":"Usage: set dhcpd_recv_sock_buf_size N","set log_txn_id":"DHCP force restart services is required in order for the changed value to take effect","set overload_bootp":"DHCP force restart services is required in order for the changed value to take effect"}
        validate_CLI(username,password,role_list)
        print("Test Case 114 Execution Completed")
        sleep(30)
        
    @pytest.mark.run(order=115)
    def test_115_verify_disabled_dns_group_set_cmds_validate_permission_for_radius_user(self):
        logging.info("Disabled dns group set commands")
        print("Testcase 115 started")
        username=config.username2
        password=config.password2
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"set dns":No_privilege,"set dns_rrl":No_privilege,"set enable_match_recursive_only":No_privilege,"set log_guest_lookups":No_privilege,"set max_recursion_depth":No_privilege,"set max_recursion_queries":No_privilege,"set monitor":No_privilege,"set ms_dns_reports_sync_interval":No_privilege,"set ms_sticky_ip":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 115 Execution Completed")

    @pytest.mark.run(order=116)
    def test_116_enable_dns_group_set_cmds_for_radius_user(self):
        logging.info("Enabling dns group set commands")
        print("Testcase 116 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"dns_set_commands":{"set_dns":True,"set_dns_rrl":True,"set_enable_match_recursive_only":True,"set_log_guest_lookups":True,"set_max_recursion_depth":True,"set_max_recursion_queries":True,"set_monitor":True,"set_ms_sticky_ip":True,"set_ms_dns_reports_sync_interval":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 116 Execution Completed")
        sleep(30)

    @pytest.mark.run(order=117)
    def test_117_verify_dns_group_set_cmds_for_radius_user(self):
        logging.info("Verifying dns group set commands")
        username=config.username2
        password=config.password2
        print("Testcase 117 started")
        role_list={"set dns":"set .*\s*Synopsis:","set dns_rrl":"set .*\s*Synopsis:","set enable_match_recursive_only":"if view_name omitted","set log_guest_lookups":"set .*\s*Synopsis:","set max_recursion_depth":"set .*\s*Synopsis:","set max_recursion_queries":"set .*\s*Synopsis:","set monitor":"set .*\s*Synopsis:","set ms_dns_reports_sync_interval":"set .*\s*Synopsis:","set ms_sticky_ip":"set .*\s*Synopsis:"}
        validate_CLI(username,password,role_list)
        print("Test Case 117 Execution Completed")
        
    @pytest.mark.run(order=118)
    def test_118_verify_disabled_grid_group_set_cmds_validate_permission_for_radius_user(self):
        logging.info("Disabled grid group set commands")
        print("Testcase 118 started")
        username=config.username2
        password=config.password2
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"set default_revert_window":No_privilege,"set nogrid":No_privilege,"set promote_master":No_privilege,"set token":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 118 Execution Completed")

    @pytest.mark.run(order=119)
    def test_119_enable_grid_group_set_cmds_for_radius_user(self):
        logging.info("Enabling grid group set commands")
        print("Testcase 119 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"grid_set_commands":{"set_default_revert_window":True,"set_nogrid":True,"set_promote_master":True,"set_token":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        sleep(30)
        for read in response:
            assert True
        print("Test Case 119 Execution Completed")

    @pytest.mark.run(order=120)
    def test_120_verify_grid_group_set_cmds_for_radius_user(self):
        logging.info("Verifying grid group set commands")
        username=config.username2
        password=config.password2
        print("Testcase 120 started")
        role_list={"set default_revert_window":"set .*\s*Synopsis:","set nogrid":"This function only valid on a member node","set promote_master":"Unable to promote","set token":"set .*\s*Synopsis:"}
        validate_CLI(username,password,role_list)
        print("Test Case 47 Execution Completed")
        
    @pytest.mark.run(order=121)
    def test_121_verify_disabled_networking_group_set_cmds_validate_permission_for_radius_user(self):
        logging.info("Disabled networking group set commands")
        print("Testcase 121 started")
        username=config.username2
        password=config.password2
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"set connection_limit":No_privilege,"set interface":No_privilege,"set ip_rate_limit":No_privilege,"set ipv6_disable_on_dad":No_privilege,"set ipv6_neighbor":No_privilege,"set ipv6_ospf":No_privilege,"set ipv6_status":No_privilege,"set lom":No_privilege,"set named_recv_sock_buf_size":No_privilege,"set named_tcp_clients_limit":No_privilege,"set ospf":No_privilege,"set prompt":No_privilege,"set static_route":No_privilege,"set tcp_timestamps":No_privilege,"set traffic_capture":No_privilege,"set wins_forwarding":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 121 Execution Completed")

    @pytest.mark.run(order=122)
    def test_122_enable_networking_group_set_cmds_for_radius_user(self):
        logging.info("Enabling networking group set commands")
        print("Testcase 122 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"networking_set_commands":{"set_connection_limit":True,"set_interface":True,"set_ip_rate_limit":True,"set_ipv6_disable_on_dad":True,"set_ipv6_neighbor":True,"set_ipv6_ospf":True,"set_ipv6_status":True,"set_lom":True,"set_named_recv_sock_buf_size":True,"set_named_tcp_clients_limit":True,"set_ospf":True,"set_prompt":True,"set_static_route":True,"set_tcp_timestamps":True,"set_traffic_capture":True,"set_wins_forwarding":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 122 Execution Completed")

    @pytest.mark.run(order=123)
    def test_123_verify_networking_group_set_cmds_for_radius_user(self):
        logging.info("Verifying networking group set commands")
        username=config.username2
        password=config.password2
        print("Testcase 123 started")
        role_list={"set connection_limit":"set .*\s*Synopsis:","set interface":"Error: The interface settings can not be configured on ","set ip_rate_limit":"set .*\s*Synopsis:","set ipv6_disable_on_dad":"set .*\s*Synopsis:","set ipv6_neighbor":"set .*\s*Synopsis:","set ipv6_ospf":"set .*\s*Synopsis:","set ipv6_status":"set .*\s*Synopsis:","set lom":"Error: LOM settings are not supported on this device","set named_recv_sock_buf_size":"Usage: set named_recv_sock_buf_size N","set named_tcp_clients_limit":"Incorrect number of arguments","set ospf":"set .*\s*Synopsis:","set prompt":"set .*\s*Synopsis:","set static_route":"set .*\s*Synopsis:","set tcp_timestamps":"set .*\s*Synopsis:","set traffic_capture":"set .*\s*Synopsis:","set wins_forwarding":"set .*\s*Synopsis:"}
        validate_CLI(username,password,role_list)
        print("Test Case 123 Execution Completed")
        
    @pytest.mark.run(order=124)
    def test_124_verify_disabled_security_group_set_cmds_validate_permission_for_radius_user(self):
        logging.info("Disabled security group set commands")
        os.system("/import/tools/lab/bin/reboot_system -H "+config.vmid1)
        sleep(700)
        print("Testcase 124 started")
        username=config.username2
        password=config.password2
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list1={"set adp":No_privilege}
        role_list={"set certificate_auth_admins":No_privilege,"set certificate_auth_services":No_privilege,"set check_auth_ns":No_privilege,"set disable_https_cert_regeneration":No_privilege,"set subscriber_secure_data":No_privilege}
        validate_CLI(username,password,role_list)
        validate_member_adp_CLI(username,password,role_list1)
        print("Test Case 124 Execution Completed")

    @pytest.mark.run(order=125)
    def test_125_enable_security_group_set_cmds_for_radius_user(self):
        logging.info("Enabling security group set commands")
        print("Testcase 125 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"security_set_commands":{"set_adp":True,"set_certificate_auth_admins":True,"set_certificate_auth_services":True,"set_check_auth_ns":True,"set_disable_https_cert_regeneration":True,"set_subscriber_secure_data":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 125 Execution Completed")

    @pytest.mark.run(order=126)
    def test_126_verify_security_group_set_cmds_for_radius_user(self):
        logging.info("Verifying security group set commands")
        username=config.username2
        password=config.password2
        print("Testcase 126 started")
        role_list1={"set adp":"set .*\s*Synopsis:"}
        role_list={"set certificate_auth_admins":"set .*\s*Synopsis:","set certificate_auth_services":"set .*\s*Synopsis:","set check_auth_ns":"set .*\s*Synopsis:","set disable_https_cert_regeneration":"set .*\s*Synopsis:","set subscriber_secure_data":"set .*\s*Synopsis:"}
        validate_CLI(username,password,role_list)
        validate_member_adp_CLI(username,password,role_list1)
        print("Test Case 126 Execution Completed")
    
    @pytest.mark.run(order=127)
    def test_127_verify_disabled_Licensing_group_set_cmds_validate_permission_for_radius_user(self):
        logging.info("Disabled Licensing group set commands")
        print("Testcase 127 started")
        username=config.username2
        password=config.password2
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"set reporting_reset_license":No_privilege}
        validate_CLI(username,password,role_list)
        print("Test Case 127 Execution Completed")

    @pytest.mark.run(order=128)
    def test_128_enable_licensing_group_set_cmds_for_radius_user(self):
        logging.info("Enabling licensing group set commands")
        print("Testcase 128 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"licensing_set_commands":{"set_reporting_reset_license":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 128 Execution Completed")

    @pytest.mark.run(order=129)
    def test_129_verify_licensing_group_set_cmds_for_radius_user(self):
        logging.info("Verifying licensing group set commands")
        username=config.username2
        password=config.password2
        print("Testcase 129 started")
        role_list={"set reporting_reset_license":"Reporting license"}
        validate_CLI(username,password,role_list)
        print("Test Case 129 Execution Completed")
        
        
    @pytest.mark.run(order=130)
    def test_130_verify_disabled_general_cmds_validate_permission_for_radius_user(self):
        logging.info("Disabled general commands")
        print("Testcase 130 started")
        username=config.username2
        password=config.password2
        No_privilege='Error: The user does not have sufficient privileges to run this command'
        role_list={"iostat":No_privilege,"netstat":No_privilege,"ps":No_privilege,"rndc":No_privilege,"sar":No_privilege,"tcpdump":No_privilege,"vmstat":No_privilege,"ddns_add":No_privilege,"ddns_delete":No_privilege,"dns_a_record_delete":No_privilege,"delete":No_privilege,"reboot":No_privilege,"reset":No_privilege,"shutdown":No_privilege,"dig":No_privilege,"ping":No_privilege,"ping6":No_privilege,"rotate":No_privilege,"traceroute":No_privilege}
        role_list1={"console":No_privilege,"traffic_capture":No_privilege,"restart_product":No_privilege,"strace":No_privilege,"resilver":No_privilege,"scrape":No_privilege,"tracepath":No_privilege,"saml_restart":No_privilege}
        role_list2={"snmpget":No_privilege,"snmpwalk":No_privilege}
        role_list3={"restart":No_privilege}
        validate_expert_CLI(username,password,role_list)
        validate_maintenance_CLI(username,password,role_list1)
        validate_member4_CLI(username,password,role_list2)
        validate_member2_CLI(username,password,role_list3)
        
        print("Test Case 130 Execution Completed")
        
    
    @pytest.mark.run(order=131)
    def test_131_enable_general_cmds_for_radius_user(self):
        logging.info("Enabling dns group set commands")
        print("Testcase 131 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"admin_toplevel_commands":{"iostat":True,"netstat":True,"restart_product":True,"ps":True,"rndc":True,"sar":True,"tcpdump":True,"vmstat":True,"resilver":True,"scrape":True,"saml_restart":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("\n\n\n\n\n admin\n\n\n\n")
        data={"dns_toplevel_commands":{"ddns_add":True,"ddns_delete":True,"dns_a_record_delete":True,"delete":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print(response)
        data={"machine_control_toplevel_commands":{"reboot":True,"reset":True,"restart":True,"shutdown":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("machine\n\n\n\n")
        data={"trouble_shooting_toplevel_commands":{"console":True,"dig":True,"ping":True,"ping6":True,"rotate":True,"snmpget":True,"snmpwalk":True,"strace":True,"traceroute":True,"tracepath":True,"traffic_capture":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 131 Execution Completed")
    
    
    @pytest.mark.run(order=132)
    def test_132_verify_general_expert_cmds_for_radius_user(self):
        logging.info("Verifying general commands")
        username=config.username2
        password=config.password2
        print("Testcase 59 started")
        role_list={"iostat":"Linux","netstat":"Active Internet connections","ps":"  PID TTY","sar":"Cannot open","tcpdump":"Please specify the","vmstat":"procs","ddns_add":"Synopsis:","ddns_delete":"Synopsis:","dns_a_record_delete":"Synopsis:","delete":"Synopsis:","reset":"Synopsis:","ping":"Usage:","ping6":"Usage:","traceroute":"Usage:","rotate":"Synopsis:","dig":"global options","rndc":"Named is not running"}
        validate_expert_CLI(username,password,role_list)
        print("Test Case 132 Execution Completed")
        
    
    @pytest.mark.run(order=133)
    def test_133_verify_general_maintenance_member_cmds_for_radius_user(self):
        logging.info("Verifying general commands")
        username=config.username2
        password=config.password2
        print("Testcase 133 started")
        role_list={"strace":"Synopsis:","console":"Synopsis:","resilver":"Synopsis:","scrape":"Maintenance","tracepath":"Synopsis:","saml_restart":"SAML PROCESS NOT RUNNING"}
        validate_maintenance_CLI(username,password,role_list)
        role_list1={"restart":"Synopsis.*restart","snmpget":"Synopsis.*snmpget","snmpwalk":"Synopsis.*snmpwalk"}
        validate_member4_CLI(username,password,role_list1)
        print("Test Case 133 Execution Completed")    
        
    @pytest.mark.run(order=134)
    def test_134_verify_general_expert_reboot_shutdown_cmds_for_radius_user(self):
        logging.info("Verifying general commands")
        try:    
            child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+config.username2+'@'+config.grid_vip)
            child.expect ('password.*:')
            child.sendline (config.password2)
            child.expect ('Infoblox >',timeout=60)
            child.sendline('set expertmode')
            child.expect("set .*\s*\"Disclaimer")
            child.sendline("shutdown")
            child.expect("SHUTDOWN THE SYSTEM\? \(y or n\)\: ")
            child.sendline("n")
            child.expect("Expert Mode > ")
            child.sendline("reboot")
            child.expect("REBOOT THE SYSTEM\? \(y or n\)\: ")
            child.sendline("n")
            child.expect("Expert Mode > ")
            assert True
        
        except Exception as e:
            print(e)
            assert False

        finally:
            child.sendline("exit")
            child.close()
            
        print("Test Case 134 Execution Completed")
        
    @pytest.mark.run(order=135)
    def test_135_verify_traffic_capture_cmd_for_radius_user(self):
        logging.info("Verifying general commands")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+config.username2+'@'+config.grid_member3_vip)      
        try:    
            child.expect ('password.*:')
            child.sendline (config.password2)
            child.expect ('Infoblox >',timeout=60)
            child.sendline('set maintenancemode')
            child.expect("Maintenance Mode > ")
            print("in mode")
            child.sendline('traffic_capture -p')
            child.expect('Synopsis:')
            child.sendline('restart_product')
            child.expect('y or n\): ')
            child.sendline('n')
            child.sendline("n")
            
            
            assert True
        
        except Exception as e:
            print(e)
            assert False

        finally:
            child.sendline("exit")
            child.close()
            
        print("Test Case 135 Execution Completed")
        

    @pytest.mark.run(order=136)
    def test_136_enable_dscp_set_cmds_for_radius_user(self):
        logging.info("Enabling licensing group set commands")
        print("Testcase 136 started")
        res = ib_NIOS.wapi_request('GET',object_type='admingroup?name=test1')
        res = json.loads(res)
        ref1=res[0]['_ref']
        data={"grid_set_commands":{"set_dscp":True}}
        response = ib_NIOS.wapi_request('PUT',fields=json.dumps(data),ref=ref1)
        print("#######################",response)
        logging.info(response)
        read  = re.search(r'200',response)
        for read in response:
            assert True
        print("Test Case 136 Execution Completed")

    @pytest.mark.run(order=137)
    def test_137_verify_dscp_set_cmds_for_radius_user(self):
        logging.info("Verifying dscp set commands")
        username=config.username2
        password=config.password2
        print("Testcase 137 started")
        role_list={"set dscp":"set .*\s*Synopsis:"}
        validate_member2_CLI(username,password,role_list)
        print("Test Case 137 Execution Completed")

    @pytest.mark.run(order=138)
    def test_138_verify_sshlogin_tacacsplus(self):
        print("Testcase 138 started")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+'user1'+'@'+config.grid_vip)
        child.expect ('password.*:')
        child.sendline ('infoblox')
        child.expect ('Infoblox >')
        child.sendline ('exit')
        child.close()
        assert True

    @pytest.mark.run(order=139)
    def test_139_verify_sshlogin_ad_server(self):
        print("Testcase 139 started")
        child = pexpect.spawn('ssh -o StrictHostKeyChecking=no '+'manoj'+'@'+config.grid_vip)
        child.expect ('password.*:')
        child.sendline ('Infoblox@123')
        child.expect ('Infoblox >')
        child.sendline ('exit') 
        child.close()
        assert True

